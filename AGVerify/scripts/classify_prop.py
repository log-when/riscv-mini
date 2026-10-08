#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""classify_prop: 性质分类脚本（DESIGN.md §2）

职责:
  1. atomic/composite 判定（纯脚本，零 LLM）
  2. scope 声明与计算值的一致性门（拒绝即报错）
  3. atomic 时将 signals 重映射为归属模块边界视角，写入 derived 字段

判定算法:
  |S| == 1                -> atomic, 归属该模块
  |S| > 1: 信号合一 —— 连接两侧端口字段指同一物理信号
    (Datapath.imem.req.valid ≡ ICache.io.req.valid, 同一根连线)
    合一后若全部信号落在同一模块 -> atomic, 以该模块为准
  否则                     -> composite

注意: "存在共同父模块但信号分属不同子模块"不构成 atomic —— 验证在
子模块内进行, 父级共观察不足以支持子模块级验证。

用法:
  python classify_prop.py spec/hierarchy.json spec/properties.json
  （输出带 derived 字段的 property JSON 到 stdout；校验失败 exit 1）

设计读取: 通过 DesignReader 接口获取模块端口方向（Input/Output），
当前提供基于正则的 Chisel IO 解析器 ChiselFileReader；后续可替换为
read_design 工具实现。
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------

class ClassifyError(Exception):
    """分类失败（含拒绝原因），调用方应中止流程"""


@dataclass
class ModuleInfo:
    name: str
    src: str = ""
    inst: Optional[str] = None
    parent: Optional[str] = None
    cls: Optional[str] = None      # 源码类名（缺省 = name）


@dataclass
class Connection:
    frm: str   # "Datapath.imem"
    to: str    # "ICache.io"


@dataclass
class Hierarchy:
    modules: Dict[str, ModuleInfo] = field(default_factory=dict)
    connections: List[Connection] = field(default_factory=list)

    @classmethod
    def load(cls, path: str) -> "Hierarchy":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        h = cls()
        for m in data.get("modules", []):
            h.modules[m["name"]] = ModuleInfo(
                name=m["name"], src=m.get("src", ""),
                inst=m.get("inst"), parent=m.get("parent"),
                cls=m.get("cls") or m["name"])
        for c in data.get("connections", []):
            h.connections.append(Connection(frm=c["from"], to=c["to"]))
        return h

    def children_of(self, module: str) -> List[str]:
        """直接子模块名列表"""
        return [m.name for m in self.modules.values() if m.parent == module]

    def ancestors_of(self, module: str) -> List[str]:
        """自父向上的祖先链"""
        chain, cur = [], self.modules.get(module)
        while cur and cur.parent:
            chain.append(cur.parent)
            cur = self.modules.get(cur.parent)
        return chain

    def find_connection(self, mod_a: str, mod_b: str) -> Optional[Connection]:
        """查找 a、b 之间的连接（任一方向），返回时保证 frm 一方为 a"""
        for c in self.connections:
            a, _ = c.frm.split(".", 1)
            b, _ = c.to.split(".", 1)
            if {a, b} == {mod_a, mod_b}:
                return c if a == mod_a else Connection(frm=c.to, to=c.frm)
        return None


# ---------------------------------------------------------------------------
# 设计读取（端口方向），后续由 read_design 工具替换
# ---------------------------------------------------------------------------

class DesignReader:
    def port_direction(self, module: str, port: str) -> Optional[str]:
        """返回 "Input" / "Output" / None（未知）"""
        raise NotImplementedError


class ChiselFileReader(DesignReader):
    """基于正则的简易 Chisel IO 解析。

    识别 class X ... IO(...) / IO(new Bundle { val p = Input(UInt(..)) })
    中的 val <name> = Input/Output(...)。扁平字段（io.cpu.req.valid）按
    Bundle 嵌套展开不可靠，这里只取顶层字段方向；嵌套 bundle 的方向
    由顶层字段名和连接语义在重映射时保守处理（见 _remap）。
    """

    def __init__(self, hierarchy: Hierarchy, src_root: str = "."):
        self.h = hierarchy
        self.src_root = Path(src_root)
        self._cache: Dict[str, Dict[str, str]] = {}

    def ports(self, module: str) -> Dict[str, str]:
        """模块顶层端口组 -> 方向。识别 Input/Output 原语与
        IO(new Bundle)/Flipped(new Bundle) 形态。"""
        if module in self._cache:
            return self._cache[module]
        info = self.h.modules.get(module)
        result: Dict[str, str] = {}
        if info and info.src:
            body = self._scan_class(info.cls or module)
            if body is not None:
                for m in re.finditer(
                        r"val\s+(\w+)\s*=\s*(Input|Output)\s*\[", body):
                    result[m.group(1)] = m.group(2)
                # Bundle 字段其它形态: IO(new X) / Flipped(new X) / new X
                for m in re.finditer(
                        r"val\s+(\w+)\s*=\s*(?:IO\()?(?:Flipped\()?"
                        r"\s*new\s+(\w+)\s*\(", body):
                    result.setdefault(m.group(1), "Bundle")
        self._cache[module] = result
        return result

    def _scan_class(self, cls_name: str) -> Optional[str]:
        for m in (self.h.modules.values() if self.h else []):
            pass
        # 搜索所有已知 src 文件
        seen = set()
        for info in self.h.modules.values():
            if not info.src or info.src in seen:
                continue
            seen.add(info.src)
            p = self.src_root / info.src
            if not p.exists():
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            cls = re.search(
                r"(?:class|case class)\s+" + re.escape(cls_name) +
                r"\b[^{]*\{", text)
            if cls:
                start = cls.end()
                depth, i = 1, start
                while i < len(text) and depth > 0:
                    if text[i] == "{":
                        depth += 1
                    elif text[i] == "}":
                        depth -= 1
                    i += 1
                return text[start:i - 1]
        return None

    def port_path_exists(self, module: str, port: str) -> bool:
        """端口路径逐段校验。识别 Input/Output 原语、IO(new Bundle)、
        Flipped/Valid/Decoupled wrapper（wrapper 字段 valid/bits/ready
        直接收，bits 下钻到 new 的类）。无法解析的层保守放行。"""
        segs = port.split(".")
        ports = self.ports(module)
        if not ports:
            return True                 # 端口表不可得（无源码/不可解析）→ 放行
        if segs[0] not in ports:
            return False
        if len(segs) == 1:
            return True
        info = self.h.modules.get(module)
        if not info or not info.src:
            return True
        cls = info.cls or module
        WRAP_FIELDS = {"Valid": {"valid", "bits"},
                       "Decoupled": {"valid", "ready", "bits"}}
        # 初始下钻: 端口组(io) → 其 Bundle 类
        mbody = self._scan_class(cls)
        if mbody is None:
            return True
        m0 = re.search(r"val\s+" + re.escape(segs[0]) +
                       r"\s*=\s*[^\n]*?\bnew\s+(\w+)\s*\(", mbody)
        if not m0:
            return len(segs) == 1
        cls = m0.group(1)
        pending_wrap = None        # 当前层的 wrapper 类型名
        for seg in segs[1:]:
            cbody = self._scan_class(cls)
            if cbody is None:
                return True                     # 类不可解析 → 放行余下段
            if pending_wrap is not None:
                if seg not in WRAP_FIELDS[pending_wrap]:
                    return False
                if seg != "bits":
                    pending_wrap = None         # valid/ready 为叶
                    continue
                pending_wrap = None             # bits → 下钻, 本段不查字段
                continue
            m = re.search(r"val\s+" + re.escape(seg) +
                          r"\s*=\s*([^\n]*)", cbody)
            if not m:
                return False                    # 字段不存在
            rhs = m.group(1)
            wm = re.search(r"\b(Valid|Decoupled)\s*\(", rhs)
            nm = re.search(r"\bnew\s+(\w+)\s*\(", rhs)
            if wm and (nm is None or rhs.index(wm.group(0)) < rhs.index(nm.group(0))):
                pending_wrap = wm.group(1)      # wrapper 层
                cls = nm.group(1) if nm else cls
            elif nm:
                cls = nm.group(1)
            else:
                if seg != segs[-1]:
                    return False                # 标量字段还有下段 → 路径非法
        return True

    def port_direction(self, module: str, port: str) -> Optional[str]:
        top = port.split(".", 1)[0]
        return self.ports(module).get(top)


# ---------------------------------------------------------------------------
# 分类核心
# ---------------------------------------------------------------------------

def classify(prop: dict, h: Hierarchy, reader: DesignReader) -> dict:
    """对单条 property 分类，返回带 derived 的 property 副本。

    抛 ClassifyError 当: 引用不存在的模块 / 一致性门拒绝。
    """
    signals = prop.get("signals", {})
    if not signals:
        raise ClassifyError(f"[{prop.get('id')}] 缺少 signals 映射")
    for _k, _s in signals.items():
        if not _s.get("port"):
            _s["port"] = "expr:" + _s.get("expr", "?")   # expr 占位路径

    mods = {s["module"] for s in signals.values()}
    for m in mods:
        if m not in h.modules:
            raise ClassifyError(f"[{prop.get('id')}] 引用未定义模块 {m}")

    # --- 一致性门 & 归属确定 ---
    declared = prop.get("scope")
    declared_module = prop.get("module")

    if len(mods) == 1:
        scope = "atomic"
        module = mods.pop()
        # 声明了归属且与唯一宿主矛盾 -> 拒绝
        if declared == "atomic" and declared_module and declared_module != module:
            raise ClassifyError(
                f"[{prop.get('id')}] scope 一致性门拒绝: 声明归属 "
                f"{declared_module} 但信号唯一宿主是 {module}")
    else:
        # |S| > 1: 信号合一。声明 atomic 时归属以声明的 module 为准,
        # 校验所有信号都能以该模块视角表达; 未声明 module 则视为 composite
        if declared == "atomic":
            if not declared_module:
                raise ClassifyError(
                    f"[{prop.get('id')}] scope=atomic 且信号分属多个模块"
                    f"({sorted(mods)})时, 必须指明归属 module 字段")
            if declared_module not in h.modules:
                raise ClassifyError(
                    f"[{prop.get('id')}] 归属模块 {declared_module} 未在"
                    f" hierarchy 中定义")
            module = declared_module
            if not _all_viewable_in(signals, module, h):
                raise ClassifyError(
                    f"[{prop.get('id')}] scope 一致性门拒绝: 声明归属 "
                    f"{module} 但存在无法以该模块视角表达的信号"
                    f"（未与 {module} 直接相连或不在连接子树内）")
            scope = "atomic"
        else:
            module = _unify_module(signals, h)
            scope = "atomic" if module else "composite"

    mismatch = (declared == "composite" and scope == "atomic")

    out = dict(prop)
    derived: Dict = {"scope": scope}
    if scope == "atomic":
        derived["module"] = module
        derived["signals"] = _remap(signals, module, h, reader)
    out["derived"] = derived
    out["_scope_mismatch_note"] = (
        "声明 composite 但计算为 atomic, 按 atomic 处理" if mismatch else None)
    if not mismatch:
        out.pop("_scope_mismatch_note", None)
    return out


def _port_on_side(side: str, port: str) -> Optional[str]:
    """信号 port 是否落在连接侧 side 所指的子树内。

    匹配规则（前缀匹配, 而非全等）:
      side == port            -> 命中, 后缀 ""
      port 以 side + "." 开头  -> 命中, 后缀为余下字段
      port 是 side 的前缀      -> 不命中（信号比连接更宽, 连接只钉住子树,
                                 不能证明整个 port 是同一根连线）
    """
    if side == port:
        return ""
    if port.startswith(side + "."):
        return port[len(side):]
    return None


def _all_viewable_in(signals: dict, module: str, h: Hierarchy) -> bool:
    """所有信号是否都能以 module 视角表达（合一校验）"""
    return all(_viewable_in(s, module, h) for s in signals.values())


def _viewable_in(s: dict, module: str, h: Hierarchy) -> bool:
    mod, port = s["module"], s["port"]
    if mod == module:
        return True
    for c in h.connections:
        frm_mod, frm_port = c.frm.split(".", 1)
        to_mod, to_port = c.to.split(".", 1)
        if frm_mod == mod and to_mod == module:
            if _port_on_side(frm_port, port) is not None:
                return True
        if to_mod == mod and frm_mod == module:
            if _port_on_side(to_port, port) is not None:
                return True
    return False


def _unify_module(signals: dict, h: Hierarchy) -> Optional[str]:
    """|S|>1 时的信号合一: 找单一模块 M, 使每个信号都能以 M 视角表达。

    信号 s 可以 M 视角表达当且仅当:
      - s 的宿主就是 M; 或
      - 存在连接 mod.sidesub ↔ M.otherside, 且 s 的端口路径落在
        sidesub 子树内（含相等; 不允许宽于连接侧）。
        此时 M 视角路径 = otherside + 字段后缀。
    字段级对应需端口结构比对, v1 假定连接两侧子树结构一致。
    候选 M 有多个时取 signals 中首个信号的首选视角（宿主优先）。
    """
    def views(s: dict) -> List[str]:
        """信号 s 可表达的模块视角列表（宿主在前）"""
        mod, port = s["module"], s["port"]
        result = [mod]
        for c in h.connections:
            frm_mod, frm_port = c.frm.split(".", 1)
            to_mod, to_port = c.to.split(".", 1)
            if frm_mod == mod and to_mod != mod:
                suffix = _port_on_side(frm_port, port)
                if suffix is not None:
                    result.append(to_mod)
            elif to_mod == mod and frm_mod != mod:
                suffix = _port_on_side(to_port, port)
                if suffix is not None:
                    result.append(frm_mod)
        return result

    all_views = [views(s) for s in signals.values()]
    # 候选 = 首个信号的视角中, 能表达所有其余信号者
    for cand in all_views[0]:
        if all(cand in vs for vs in all_views[1:]):
            return cand
    return None


def _remap(signals: dict, module: str, h: Hierarchy,
           reader: DesignReader) -> dict:
    """将 signals 统一为归属模块 module 的视角。

    宿主 == module 的信号原样保留; 宿主 != module 的信号沿连接换
    module 侧前缀 + 字段后缀（前缀匹配, 见 _port_on_side）,
    via 记录原始引用。
    """
    remapped = {}
    for local, s in signals.items():
        mod, port = s["module"], s["port"]
        if mod == module:
            remapped[local] = ({"module": module, "port": port}
                           if not port.startswith("expr:")
                           else {"module": module, "port": port,
                                 "expr": port[len("expr:"):]})
            continue
        peer_path = None
        for c in h.connections:
            frm_mod, frm_port = c.frm.split(".", 1)
            to_mod, to_port = c.to.split(".", 1)
            if frm_mod == mod and to_mod == module:
                suffix = _port_on_side(frm_port, port)
                if suffix is not None:
                    peer_path = to_port + suffix
                    break
            if to_mod == mod and frm_mod == module:
                suffix = _port_on_side(to_port, port)
                if suffix is not None:
                    peer_path = frm_port + suffix
                    break
        if peer_path is None:
            raise ClassifyError(
                f"信号 {local}({mod}.{port}) 无法以 {module} 视角表达"
                f"（无匹配连接）, 内部一致性错误")
        remapped[local] = {"module": module,
                           "port": peer_path,
                           "via": f"{mod}.{port}"}
    return remapped


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    hierarchy_path, prop_path = argv[1], argv[2]
    h = Hierarchy.load(hierarchy_path)
    reader = ChiselFileReader(h, src_root=str(Path(hierarchy_path).parent.parent))
    prop = json.loads(Path(prop_path).read_text(encoding="utf-8"))
    try:
        result = classify(prop, h, reader)
    except ClassifyError as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))


def rewrite_path(path: str, from_mod: str, to_mod: str, h) -> Optional[str]:
    """路径前缀改写: from_mod 视角 → to_mod 视角。
    依据 connections 字段级前缀; 无法改写返回 None。"""
    if from_mod == to_mod:
        return path
    for conn in h.connections:
        frm_mod, frm_port = conn.frm.split(".", 1)
        to_mod_, to_port = conn.to.split(".", 1)
        if frm_mod == from_mod and to_mod_ == to_mod:
            suffix = _port_on_side(frm_port, path)
            if suffix is not None:
                return to_port + suffix
        if to_mod_ == from_mod and frm_mod == to_mod:
            suffix = _port_on_side(to_port, path)
            if suffix is not None:
                return frm_port + suffix
    return None


PATH_TOKEN = re.compile(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*")

REDUCE_METHODS = {"orR", "andR", "or", "and", "not", "toBool", "toUInt"}

def _split_methods(tok: str, from_mod: str, reader):
    """剥离尾部归约方法段(.orR 等): 返回 (基路径, 方法段) 或 None。
    基路径须在 from_mod 是真实路径。"""
    segs = tok.split(".")
    methods = []
    while len(segs) > 1:
        if segs[-1] in REDUCE_METHODS and reader \
                and hasattr(reader, "port_path_exists") \
                and reader.port_path_exists(from_mod, ".".join(segs[:-1])):
            methods.insert(0, segs.pop())
        else:
            break
    base = ".".join(segs)
    if reader and hasattr(reader, "port_path_exists"):
        return (base, ".".join(methods)) if methods and \
            reader.port_path_exists(from_mod, base) else \
            (base, "") if not methods and \
            reader.port_path_exists(from_mod, base) else None
    return (base, ".".join(methods)) if methods else (base, "")


def rewrite_expr(expr: str, from_mod: str, to_mod: str, h,
                 reader) -> Optional[str]:
    """expr 内路径样 token 的安全前缀改写。
    token 先剥离尾部归约方法(.orR 等), 基路径须在【from_mod】为真实
    路径才尝试改写; 其余(0.U/枚举名等)不动。
    是真实路径但改不动 → 整体返回 None(保守放弃)。"""
    changed = []
    for m in PATH_TOKEN.finditer(expr):
        tok = m.group(0)
        sm = _split_methods(tok, from_mod, reader)
        if sm is None:
            continue            # 非真实路径(常量/枚举) → 不动
        base, methods = sm
        new_base = rewrite_path(base, from_mod, to_mod, h)
        if new_base is None:
            return None         # 真实路径改不动 → 放弃该候选
        changed.append((tok, new_base + ("." + methods if methods else "")))
    out = expr
    for old, new in changed:
        out = out.replace(old, new)
    return out


if __name__ == "__main__":
    sys.exit(main(sys.argv))


EXPR_PREFIX = "expr:"


def strip_expr(port: str) -> str:
    """剥 expr: 前缀, 返回原始表达式; 非 expr 信号原样返回。"""
    return port[len(EXPR_PREFIX):] if port.startswith(EXPR_PREFIX) else port


def pack_expr(expr: str) -> str:
    """打包表达式为 port 字段形式。"""
    return EXPR_PREFIX + expr
