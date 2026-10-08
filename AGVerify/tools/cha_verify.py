import os
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cha_verify: CHA 形式化验证统一入口（DESIGN.md §5）

封装三步:
  1. 生成 src/test/scala/cha/TileTest.scala（预给定 *Prop 类骨架
     + 插入 SignalName 别名 / chaAssume / 单条 chaAssert + verify 行）
  2. 编译检查: sbt "testOnly mini.TileSignal" —— 不合法信号/编译错误
     在此暴露 (ERROR verdict, 不进求解器)
  3. 验证: sbt "testOnly mini.TileFlatPropSpec" —— 解析四种输出:
     BMC/IC3 PASS、BMC FAIL(带 VCD 反例)、IC3 FAIL(无反例)、ERROR

用法 (库):
  from cha_verify import cha_verify
  r = cha_verify(
      module="ICache",                 # 目标模块
      signals=[("req", "io.cpu.req.valid", 20), ...],  # (别名, 路径, 编号)
      assumes=[("F nastiReadReqReady", [("nastiReadReqReady","io.nasti.ar.ready",1)])],
      assert_formula="F response",
      mode="bmc",                      # "bmc" | "ic3"
      bound=20,                        # bmc: BoundedCheck 深度; ic3: 迭代次数
  )
  # r = {"verdict": "PASS"|"FAIL"|"ERROR",
  #      "detail": str, "vcd": path|None, "log": path}
"""

import json
import re
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[2]   # riscv-mini/
AGV = Path(__file__).resolve().parents[1]
TEMPLATE = AGV / "templates" / "TileTest.scala.tpl"
TEST_FILE = REPO / "src/test/scala/cha/TileTest.scala"
LOG_DIR = AGV / "results"


def set_log_dir(path):
    """由 dispatcher 设置本次运行的 sbt 日志子目录"""
    global LOG_DIR
    LOG_DIR = Path(path)

# 外部可调参数（AGVerify/config.json）
_cfg = {"bmc_bound": 15, "bmc_timeout_sec": 600,
        "ic3_iters": 20, "ic3_timeout_sec": 1800,
        "compile_check": True, "sbt_xmx": "8G"}
_cfg_file = AGV / "config.json"
if _cfg_file.exists():
    _cfg.update(json.loads(_cfg_file.read_text(encoding="utf-8")))

MODULES = ["Datapath", "Control", "DCache", "ICache", "MemArbiter", "Tile",
           "Implication"]
VERIFY_LINES = {
    "Datapath":    '  verify(new AGDatapathProp(config.core), Seq({ANN}))',
    "Control":     '  verify(new AGControlProp(), Seq({ANN}))',
    "DCache":      '  verify(new AGDCacheProp(config.cache, config.nasti, config.core.xlen), Seq({ANN}))',
    "ICache":      '  verify(new AGICacheProp(config.cache, config.nasti, config.core.xlen), Seq({ANN}))',
    "MemArbiter":  '  verify(new AGMemArbiterProp(config.nasti), Seq({ANN}))',
    "Tile":        '  verify(new AGTileFlatProp(config.core, config.nasti, config.cache), Seq({ANN}))',
    "Implication": '  verify(new AGImplicationProp(), Seq({ANN}))',
}


# ---------------------------------------------------------------------------
# 1. 测试文件生成
# ---------------------------------------------------------------------------

def _render_body(lines: List[str]) -> str:
    return "\n".join("  " + l for l in lines) if lines else ""


def gen_signal_lines(signals: List[Tuple[str, str, int]]) -> List[str]:
    """[(别名, 信号路径, 编号)] -> val + SignalName 行
    汇点防御 (2026-10-07): path 带 expr: 前缀时剥离——上游任何生产者
    (KB前提/多落点改写/物化) 泄漏的前缀在此统一兜底, 杜绝整类编译错"""
    out = []
    for alias, path, num in signals:
        if isinstance(path, str) and path.startswith("expr:"):
            path = path[5:]
        out.append(f'val {alias} = {path}')
        out.append(f'SignalName({alias},{num})')
    return out



def _backup_old(new_content: str):
    """辅助定位④: 写入前把旧版 TileTest.scala 备份到 LOG_DIR
    (文件名含新版指纹+时间戳; 失败不阻塞主流程)"""
    try:
        import hashlib as _hl
        _old = TEST_FILE.read_bytes() if TEST_FILE.exists() else b""
        _dig = _hl.md5(new_content.encode()).hexdigest()[:10]
        LOG_DIR.mkdir(exist_ok=True)
        (LOG_DIR / f"backup_{_dig}_{int(time.time())}.scala").write_bytes(_old)
    except Exception:
        pass

def build_test_file(module: str,
                    signals: List[Tuple[str, str, int]],
                    assumes: List[str],
                    assert_formula: str,
                    mode: str = "bmc",
                    bound: int = 20,
                    priors_by_module: Optional[Dict[str, Dict]] = None,
                    run_at: str = "module") -> None:
    """全量覆盖生成 TileTest.scala。

    - module = 目标性质归属模块: 其 *Prop 类 body 承载
      信号行 + assume 行 + 单条 assert 行（模块视角路径, 无论全局
      还是模块级运行, assert 都住在归属模块的 Prop 类里）
    - run_at = 实际运行的 verify 目标: "module"(默认, 单模块验证)
      或 "Tile"(全局验证——实例化全部 *Prop 子类, 真实环境+先验常驻)
    - priors_by_module: {模块: {"signals": [...], "assumes": [...]}}
      —— 各模块先验以 chaAssume 常驻对应 *Prop 类
    """
    if module not in MODULES:
        raise ValueError(f"未知模块 {module}, 可选 {MODULES}")
    if mode not in ("bmc", "ic3"):
        raise ValueError("mode 必须是 bmc 或 ic3")
    priors_by_module = priors_by_module or {}

    if module == "Implication":
        # 空设计: signals 的 path 即 io 输入名(如 io.s3)
        ann = (f"BoundedCheck({bound}), PonoEngineAnnotation" if mode == "bmc"
               else f"Ic3Check({bound}), RIC3EngineAnnotation")
        io_lines = []
        for alias, path, num in signals:
            iname = path.split(".")[-1]
            if f"val {iname} = Input" not in "\n".join(io_lines):
                io_lines.append(f"    val {iname} = Input(Bool())")
        body = ([f"  val {a} = io.{p.split('.')[-1]}"
                 for a, p, n in signals]
                + [f"  SignalName({a},{n})" for a, p, n in signals]
                + [f'chaAssume(this, "{a}")' for a in assumes]
                + [f'chaAssert(this, "{assert_formula}")'])
        vlines = []
        for m in MODULES:
            line = "  " + VERIFY_LINES[m].format(ANN=ann)
            prefix = "" if m == "Implication" else "// "
            vlines.append(f'{prefix}behavior of "{m}"')
            vlines.append(f'{prefix}it should "pass" in {{')
            vlines.append(f"{prefix}{line}")
            vlines.append(f"{prefix}}}")
        tpl = TEMPLATE.read_text(encoding="utf-8")
        content = tpl.replace("@IMPL_IO@", "\n".join(io_lines)) \
                     .replace("@IMPL_BODY@", "\n".join("  " + l for l in body)) \
                     .replace("@VERIFY_LINES@", "\n".join(vlines))
        for key in ["DATAPATH_BODY", "CONTROL_BODY", "DCACHE_BODY",
                    "ICACHE_BODY", "MEMARBITER_BODY", "TILE_BODY"]:
            content = content.replace("@%s@" % key, "")
        _backup_old(content)
        TEST_FILE.write_text(content, encoding="utf-8")
        return

    def prior_lines(m):
        p = priors_by_module.get(m) or {}
        return (gen_signal_lines(p.get("signals", []))
                + [f'chaAssume(this, "{a}")' for a in p.get("assumes", [])])

    # 别名冲突处理: 先验已占用的别名(同模块烘焙), 性质信号同名时
    # 【改别名并同步改写公式引用】——绝不静默丢弃声明(否则公式会
    # 绑到先验的端口, 同名不同网 → 语义改写, 不可靠)
    import re as _re
    seen = set()
    _p = (priors_by_module or {}).get(module) or {}
    for a, _pth, _n in _p.get("signals", []):
        seen.add(a)
    deduped = []
    renames = {}                        # 旧别名 → 新别名
    for alias, path, num in signals:
        a2 = alias
        if a2 in seen:
            while True:
                a2 = "{}_{}".format(alias, num)
                if a2 not in seen:
                    break
            renames[alias] = a2
        seen.add(a2)
        deduped.append((a2, path, num))
    if renames:
        def _sub(formula):
            out = formula
            for old_a, new_a in renames.items():
                out = _re.sub(r'\b{}\b'.format(_re.escape(old_a)),
                              new_a, out)
            return out
        assumes = [_sub(x) for x in assumes]
        assert_formula = _sub(assert_formula)
    # 注意: 各模块槽位已拼接 prior_lines(m), body 不再重复带先验
    body = (gen_signal_lines(deduped)
            + [f'chaAssume(this, "{a}")' for a in assumes]
            + [f'chaAssert(this, "{assert_formula}")'])

    ann = (f"BoundedCheck({bound}), PonoEngineAnnotation" if mode == "bmc"
           else f"Ic3Check({bound}), RIC3EngineAnnotation")

    active = "Tile" if run_at == "Tile" else module
    vlines = []
    for m in MODULES:
        line = "  " + VERIFY_LINES[m].format(ANN=ann)
        prefix = "" if m == active else "// "
        vlines.append(f'{prefix}behavior of "{m}"')
        vlines.append(f'{prefix}it should "pass" in {{')
        vlines.append(f"{prefix}{line}")
        vlines.append(f"{prefix}}}")

    tpl = TEMPLATE.read_text(encoding="utf-8")
    content = tpl.replace("@IMPL_IO@", "").replace("@IMPL_BODY@", "")
    for key, val in [
        ("DATAPATH_BODY", _render_body(
            prior_lines("Datapath") + (body if module == "Datapath" else []))),
        ("CONTROL_BODY", _render_body(
            prior_lines("Control") + (body if module == "Control" else []))),
        ("DCACHE_BODY", _render_body(
            prior_lines("DCache") + (body if module == "DCache" else []))),
        ("ICACHE_BODY", _render_body(
            prior_lines("ICache") + (body if module == "ICache" else []))),
        ("MEMARBITER_BODY", _render_body(
            prior_lines("MemArbiter") + (body if module == "MemArbiter" else []))),
        ("TILE_BODY", _render_body(
            prior_lines("Tile") + (body if module == "Tile" else []))),
        ("VERIFY_LINES", "\n".join(vlines)),
    ]:
        content = content.replace("@%s@" % key, val)
    TEST_FILE.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# 2/3. sbt 运行与日志解析
# ---------------------------------------------------------------------------

def run_sbt(test_class: str, timeout: int = 1800,
            ctx_tag: str = "") -> Tuple[int, str]:
    """sbt -J-Xmx4G -J-XX:+UseG1GC "testOnly mini.<class>" → (exit_code, log)
    ctx_tag: 调用方上下文标识(node/公式), 写入日志头辅助定位 verdict 错位"""
    cmd = ["sbt", f"-J-Xmx{_cfg['sbt_xmx']}", "-J-XX:+UseG1GC",
           f"testOnly mini.{test_class}"]
    env = {**os.environ, "LC_ALL": "C.UTF-8", "LANG": "C.UTF-8"}
    t0 = time.time()
    # 辅助定位①: 生成文件的指纹(调用前), 用于检测 sbt 运行期间文件被并发覆盖
    file_md5 = ""
    try:
        import hashlib
        file_md5 = hashlib.md5(TEST_FILE.read_bytes()).hexdigest()[:10]
    except Exception:
        pass
    try:
        proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True,
                              timeout=timeout, env=env)
    except subprocess.TimeoutExpired as e:
        # 超时 → ERROR(工具超时), 不裸崩; dispatcher 按 TIMEOUT 降级
        log = (e.stdout or "") + (e.stderr or "") if isinstance(
            e.stdout, str) else ""
        LOG_DIR.mkdir(exist_ok=True)
        log_path = LOG_DIR / f"{test_class}_{int(time.time())}.log"
        log_path.write_text(log + "\n[TIMEOUT] sbt 超时被终止\n",
                            encoding="utf-8")
        return -1, str(log_path)
    log = proc.stdout + proc.stderr
    LOG_DIR.mkdir(exist_ok=True)
    log_path = LOG_DIR / f"{test_class}_{int(time.time())}.log"
    # 辅助定位②: 运行后文件是否被改(并发覆盖证据) + 耗时 + 上下文标签
    file_md5_after = ""
    try:
        import hashlib
        file_md5_after = hashlib.md5(
            TEST_FILE.read_bytes()).hexdigest()[:10]
    except Exception:
        pass
    stamp = (f"[DIAG] ctx={ctx_tag} dur={time.time()-t0:.0f}s "
             f"file={file_md5}->{file_md5_after}"
             f"{' ⚠️OVERWRITTEN' if file_md5 != file_md5_after else ''}\n")
    log_path.write_text(stamp + log, encoding="utf-8")
    return proc.returncode, str(log_path)


def parse_verify_log(log_text: str) -> Dict:
    """解析 AGTileFlatPropSpec 输出 → 四种 verdict。

    FAIL 仅当有明确的违反证据（FailedBoundedCheckException / rIC3 判定
    违反）; 其它异常一律 ERROR——其中公式语法错误标注 subtype=SYNTAX,
    供 dispatcher 反馈 decomposer 修改公式而非误判为性质不成立。
    """
    if "All properties can be proven" in log_text or (
            "All tests passed" in log_text):
        # 辅助定位③: PASS 可信性校验 — 日志必须含本次断言打印且无失败残留
        # (防"跑了空/旧类"的伪 PASS: 并发覆盖或编译竞争)
        has_assert = "chaAssertStmt" in log_text
        if not has_assert:
            return {"verdict": "ERROR",
                    "detail": "⚠️伪PASS拦截: 日志无 chaAssertStmt 打印 — "
                              "可能运行了空/旧测试类(并发覆盖?)",
                    "subtype": "NO_ASSERT_SEEN"}
        return {"verdict": "PASS", "detail": "CHA 证明通过"}
    m = re.search(r"FailedBoundedCheckException: \[(\w+)\] found an assertion"
                  r" violation (\d+) steps after reset", log_text)
    if m:
        return {"verdict": "FAIL",
                "detail": f"BMC 反例: {m.group(1)} 复位后第 {m.group(2)} 拍违反断言"}
    if "does not generate valid counter-examples" in log_text:
        return {"verdict": "FAIL",
                "detail": "rIC3 判定违反但不产生反例, 建议换 BMC 定位"}
    if "error" in log_text.lower() or "Exception" in log_text:
        # 提取首个 error/exception 行
        err = next((l.strip() for l in log_text.splitlines()
                    if l.strip().startswith(("[error]", "[info]   "))
                    and ("error" in l.lower() or "Exception" in l)),
                   "unknown error")
        # 方法发射缺陷: 公式→Scala 方法的生成失败(运行期反射
        # NoSuchMethodException), 按编译类错误归类(修公式而非算失败)
        if "NoSuchMethod" in log_text:
            m2 = re.search(r"(\w*\(\))", err) or re.search(
                r"NoSuchMethodException: [\w.]*\.(\w+)", log_text)
            return {"verdict": "ERROR", "subtype": "COMPILE",
                    "detail": ("公式→方法生成失败(NoSuchMethod): "
                               f"{m2.group(1) if m2 else err[:200]} — "
                               "该公式形态不被模板方法发射支持, "
                               "请改写公式(如展开 X 算子)")}
        # 公式语法错误识别: 性质串解析失败通常发生在 chaAssertStmt 打印
        # 阶段或 verify 入口, 报错含 parse/syntax/formula/chaAssert 等
        if re.search(r"parse|syntax|formula|chaAssert|chaAssume|LTL",
                     log_text, re.I):
            return {"verdict": "ERROR", "subtype": "SYNTAX",
                    "detail": f"性质公式疑似语法错误: {err[:300]}"}
        return {"verdict": "ERROR", "detail": err[:300]}
    return {"verdict": "ERROR", "detail": "无法解析的输出"}


def find_vcd(module: str) -> Optional[str]:
    """定位 BMC 反例波形 test_run_dir/<X>_should_pass/AG<X>Prop.bmc.vcd"""
    d = REPO / "test_run_dir" / f"{module}_should_pass"
    vcd = d / f"AG{module}Prop.bmc.vcd"
    return str(vcd) if vcd.exists() else None


def find_impl_vcd() -> Optional[str]:
    """空设计蕴含检查的反例波形"""
    return find_vcd("Implication")


# ---------------------------------------------------------------------------
# 对外主入口
# ---------------------------------------------------------------------------

def cha_verify(module: str,
               signals: List[Tuple[str, str, int]],
               assert_formula: str,
               assumes: Optional[List[str]] = None,
               mode: str = "bmc",
               bound: Optional[int] = None,
               skip_compile_check: Optional[bool] = None,
               timeout: Optional[int] = None,
               priors_by_module: Optional[Dict[str, Dict]] = None,
               run_at: str = "module") -> Dict:
    assumes = assumes or []
    if bound is None:
        bound = _cfg["bmc_bound"] if mode == "bmc" else _cfg["ic3_iters"]
    if timeout is None:
        timeout = (_cfg["bmc_timeout_sec"] if mode == "bmc"
                   else _cfg["ic3_timeout_sec"])
    if skip_compile_check is None:
        skip_compile_check = not _cfg["compile_check"]

    # 1. 生成测试文件
    build_test_file(module, signals, assumes, assert_formula, mode, bound,
                    priors_by_module, run_at=run_at)
    _tag = f"{module}|{assert_formula[:40]}|{mode}|{run_at}"

    # 2. 编译检查（不合法信号在此暴露, 不浪费求解器时间）
    if not skip_compile_check:
        code, log_path = run_sbt("AGTileSignal", timeout=timeout,
                                 ctx_tag=_tag)
        log = Path(log_path).read_text(encoding="utf-8")
        if code != 0 or "*** FAILED ***" in log or "[error]" in log:
            errs = []
            for l in log.splitlines():
                l = l.strip()
                if l.startswith("[error]") and "compileIncremental" not in l \
                        and "Tests unsuccessful" not in l and "one error found" not in l:
                    if l not in errs:
                        errs.append(l)
            detail = "编译失败: " + (" | ".join(errs[:6]) if errs
                                      else "unknown compile error")
            return {"verdict": "ERROR", "subtype": "COMPILE",
                    "detail": detail[:800], "vcd": None, "log": log_path}

    # 3. 验证
    code, log_path = run_sbt("AGTileFlatPropSpec", timeout=timeout,
                             ctx_tag=_tag)
    log = Path(log_path).read_text(encoding="utf-8")
    result = parse_verify_log(log)
    result["log"] = log_path
    result["vcd"] = find_vcd(module) if result["verdict"] == "FAIL" else None
    if result["vcd"]:
        # 反例时序摘要(critic 可读): 别名按生成时的 signals 匹配
        try:
            from parse_cex import cex_timeline, cex_full_timeline
            tl = cex_timeline(result["vcd"], signals)
            if tl:
                result["cex_timeline"] = tl
            # 完整波形: 全部信号(不限性质相关), 供深挖反例根因。
            # 抽象: 用同目录 .sys 数据流图做【种子间通路敏感集】过滤,
            # 只保留命名敏感信号(剔除 _T/_GEN/MPORT 中间线)——
            # 防止数千信号的全波形撑爆 LLM 输入。
            full = cex_full_timeline(result["vcd"])
            if full:
                vcd_p = Path(result["vcd"])
                # vcd 可能带双后缀(x.bmc.vcd) —— 剥到主名再配 .sys
                stem = vcd_p.name
                for suf in ('.vcd', '.bmc', '.ic3'):
                    if stem.endswith(suf):
                        stem = stem[:-len(suf)]
                sys_cands = [vcd_p.with_suffix('.sys'),
                             vcd_p.parent / (stem + '.sys')]
                sys_p = next((p for p in sys_cands if p.exists()), None)
                if sys_p:
                    try:
                        from parse_cex import sensitive_set
                        seeds = [p.replace(".", "_")
                                 for _a, p, _n in signals]
                        keep = set(sensitive_set(str(sys_p), seeds))
                        # 波形信号白名单: 只保留 sys input/state 的本体名;
                        # 影子副本(__后缀)与相等指示位(eq_前缀)均删除
                        def _hit(n):
                            if n.startswith("eq_") or n.endswith("__"):
                                return False
                            return n in keep
                        full = {t: {n: v for n, v in row.items()
                                    if _hit(n)}
                                for t, row in full.items()}
                    except Exception:
                        pass
                # 体积硬上限: 敏感集过滤失效(缺 sys/解析异常)时防全波形
                # 撑爆 LLM 输入 —— 超限直接丢弃(保留小体积 cex_timeline)
                try:
                    import json as _j
                    if len(_j.dumps(full)) > 40000:
                        full = None
                except Exception:
                    full = None
                if full:
                    result["cex_full_timeline"] = full
        except Exception:
            pass                       # 解析失败不阻塞验证结果
    return result


if __name__ == "__main__":
    import json
    import sys
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    print(json.dumps(cha_verify(**args), ensure_ascii=False, indent=2))
