#!/usr/bin/env python3
"""层次化证明恢复工具 (standalone, 2026-10-10).

用法:
  python3 proof_tree_tool.py <run_dir> [--ablate]

数据源: run 目录的全部输出 (outcomes.jsonl, final_proof_state.json, sbt logs).
不依赖 Dispatcher 内存状态.
"""
import json, sys, re, os, subprocess, collections
from pathlib import Path

AGV_ROOT = Path(__file__).resolve().parents[1]
REPO = AGV_ROOT.parent
sys.path.insert(0, str(AGV_ROOT / 'scripts'))
sys.path.insert(0, str(AGV_ROOT / 'agents'))
sys.path.insert(0, str(AGV / 'tools')) if False else None
sys.path.insert(0, str(AGV_ROOT / 'tools'))


class RunData:
    """解析 run 目录的全部输出."""

    def __init__(self, run_dir):
        self.dir = Path(run_dir)
        self.outcomes = [json.loads(l) for l in
                         open(self.dir / 'outcomes.jsonl')]
        self.state = json.load(open(self.dir / 'final_proof_state.json'))
        self.kb = {e['kid']: e for e in self.state.get('kb', [])}
        self.nodes = self.state.get('nodes', {})
        self.root = self.state.get('root', '')

        # 时间线: node_id → module_ic3 PASS 的 ts
        self.verify_ts = {}
        for d in self.outcomes:
            if (d.get('phase') == 'module_ic3'
                    and d.get('verdict') == 'PASS'):
                self.verify_ts[d['node']] = d['ts']

        # KB 入库时间 (来源节点的验证时间)
        self.kb_ts = {}
        for kid, e in self.kb.items():
            origin = e.get('node_origin', '')
            if origin in self.verify_ts:
                self.kb_ts[kid] = self.verify_ts[origin]

    def kb_deps(self, node_id, ts=None):
        """获取节点验证时可用的 KB 条目(时序过滤)."""
        node_ts = ts or self.verify_ts.get(node_id, '99:99')
        # 尝试 [KB:T1,...] 标签
        for d in reversed(self.outcomes):
            if (d.get('node') == node_id
                    and d.get('phase') == 'module_ic3'
                    and d.get('verdict') == 'PASS'):
                detail = str(d.get('detail', ''))
                m = re.search(r'\[KB:([T0-9,]+)\]', detail)
                if m:
                    return m.group(1).split(',')
                break
        # fallback: 所有早于此节点入 KB 的条目
        return [kid for kid, t in self.kb_ts.items() if t < node_ts]

    def node_formula(self, node_id):
        n = self.nodes.get(node_id, {})
        return n.get('formula', '?')

    def node_module(self, node_id):
        n = self.nodes.get(node_id, {})
        return (n.get('derived', {}).get('module')
                or self._first_signal_module(n))

    def _first_signal_module(self, node):
        sigs = node.get('signals', {})
        if sigs:
            return next(iter(sigs.values())).get('module', '?')
        return '?'

    def node_kind(self, node_id):
        return self.nodes.get(node_id, {}).get('kind', '?')

    def children(self, node_id):
        return self.nodes.get(node_id, {}).get('children', [])

    def assumes(self, node_id):
        return self.nodes.get(node_id, {}).get('assumes', [])

    def assume_discharge(self, assume_id):
        a = self.nodes.get(assume_id, {})
        return a.get('discharged_by')

    def assume_formula(self, assume_id):
        return self.nodes.get(assume_id, {}).get('formula', '?')


def build_tree(data, do_ablate=False):
    """构建证明树(传递闭包 + 可选消融 + 渲染)."""
    # ── 传递闭包 ──
    chain = {}

    def collect(node_id, depth=0):
        if node_id in chain or depth > 20:
            return
        if node_id not in data.nodes:
            return
        status = data.nodes[node_id].get('status')
        if status != 'IC3_PROVEN':
            return
        deps = data.kb_deps(node_id)
        chain[node_id] = {
            'formula': data.node_formula(node_id),
            'module': data.node_module(node_id),
            'kb_used': deps,
            'kind': data.node_kind(node_id),
        }
        for kid in deps:
            collect(kid, depth + 1)
        for c in data.children(node_id):
            collect(c, depth + 1)
        for a in data.assumes(node_id):
            did = data.assume_discharge(a)
            if did:
                collect(did, depth + 1)

    collect(data.root)
    if not chain:
        return None

    # ── 消融 ──
    minimal = {nid: list(info['kb_used']) for nid, info in chain.items()}
    ablation_status = {}  # nid → "精确" | "近似"
    if do_ablate:
        for nid in sorted(chain,
                          key=lambda x: (0, x) if x.startswith('T')
                          else (1, x)):
            info = chain[nid]
            if len(info['kb_used']) <= 1:
                ablation_status[nid] = "精确"
                continue
            remaining = list(info['kb_used'])
            all_skip = True
            for kid in sorted(info['kb_used'], reverse=True):
                trial = [k for k in remaining if k != kid]
                if not trial:
                    continue
                result = ablate_bmc(data, nid, trial)
                if result.startswith('SKIP'):
                    continue  # 备份缺失或匹配失败
                all_skip = False
                if result == 'PASS':
                    remaining = trial
                    print(f"  消融: {nid} <- {kid} 冗余")
                else:
                    print(f"  消融: {nid} <- {kid} 必要({result})")
            minimal[nid] = remaining
            ablation_status[nid] = "近似" if all_skip else "精确"
    else:
        for nid in chain:
            ablation_status[nid] = "未消融"

    # ── 渲染 ──
    L = ["\n## 7. 层次化证明树\n"]

    def render(node_id, indent, visited):
        if node_id in visited:
            L.append("  " * indent + f"(ref) {node_id}")
            return
        visited.add(node_id)
        pad = "  " * indent

        if node_id in data.kb:
            e = data.kb[node_id]
            deps = minimal.get(node_id, [])
            proven = e.get('proven_at', '?')
            L.append(pad + f"[{e['kid']}] `{e['formula'][:55]}` @{proven}")
            for kd in sorted(deps):
                render(kd, indent + 1, visited)
        elif node_id in chain:
            info = chain[node_id]
            deps = minimal.get(node_id, [])
            L.append(pad + f"{node_id}: `{info['formula'][:50]}`"
                     + f" @{info['module']}")
            for kd in sorted(deps):
                render(kd, indent + 1, visited)
            for c in data.children(node_id):
                render(c, indent + 1, visited)
            for a in data.assumes(node_id):
                af = data.assume_formula(a)
                L.append("  " * (indent + 1) + f"ASSUME: `{af[:45]}`")
                did = data.assume_discharge(a)
                if did:
                    render(did, indent + 2, visited)

    render(data.root, 0, set())

    # 明细表
    L.append("\n### 性质明细\n")
    L.append("| 标签 | 性质 | 验证模块 | 最小依赖 | 消融精度 |")
    L.append("|---|---|---|---|---|")
    for nid in sorted(chain):
        info = chain[nid]
        deps = minimal.get(nid, [])
        if nid in data.kb:
            e = data.kb[nid]
            # 跨模块
            used_at = set()
            for oid, oinfo in chain.items():
                if nid in oinfo.get('kb_used', []):
                    om = oinfo.get('module', '?')
                    if om != e.get('proven_at', '?'):
                        used_at.add(om)
            cross = f" → 使用@{','.join(used_at)}" if used_at else ""
            L.append(f"| {e['kid']} | `{e['formula'][:40]}`"
                     + f" | {e.get('proven_at','?')}{cross}"
                     + f" | {', '.join(deps) or '(先验)'}"
                     + f" | {ablation_status.get(nid, '?')} |")
        else:
            L.append(f"| {nid} | `{info['formula'][:40]}`"
                     + f" | {info['module']}"
                     + f" | {', '.join(deps) or '(先验)'}"
                     + f" | {ablation_status.get(nid, '?')} |")

    return "\n".join(L)


def ablate_bmc(data, node_id, exclude_kids):
    """消融 BMC: 找到节点的 Scala 备份, 删除指定 KB 条目对应的
    chaAssume 行, 重跑 sbt BMC.

    data: RunData 实例
    node_id: 要消融的节点
    exclude_kids: 要排除的 KB kid 列表(即测试"没有这些条目还能过吗")

    返回 PASS/FAIL/SKIP.
    """
    node_ts = data.verify_ts.get(node_id)
    if not node_ts:
        return "SKIP:no_ts"

    # 1. 找到节点验证时刻的 Scala 备份
    # 备份保存的是被覆盖前的内容, 所以要找验证时刻之后最近的备份
    # (那个备份的内容就是验证后下一次写入时被保存的)
    best_backup = None
    best_diff = None
    for f in data.dir.glob('sbt/backup_*.scala'):
        ts_match = re.search(r'_(\d+)\.scala$', f.name)
        if not ts_match:
            continue
        file_epoch = int(ts_match.group(1))
        # 将 node_ts (HH:MM:SS) 转为当天 epoch 的近似
        try:
            h, m, sec = node_ts.split(':')
            ts_sec = int(h) * 3600 + int(m) * 60 + int(sec)
            # 备份文件的 epoch 是完整的, 只比较时间部分
            import datetime
            file_dt = datetime.datetime.fromtimestamp(file_epoch)
            file_sec = file_dt.hour * 3600 + file_dt.minute * 60 + file_dt.second
            diff = abs(file_sec - ts_sec)
            if best_diff is None or diff < best_diff:
                best_diff = diff
                best_backup = f
        except (ValueError, IndexError):
            continue

    if not best_backup or not best_backup.exists():
        # 备份缺失: 从 final_proof_state 重建验证参数
        return _ablate_reconstruct(data, node_id, exclude_kids)

    # 2. 解析备份, 提取全部 chaAssume 公式
    content = best_backup.read_text(errors='ignore')
    assume_lines = []  # (行号, 公式)
    all_lines = content.split('\n')
    for i, line in enumerate(all_lines):
        m = re.search(r'chaAssume\(this,\s*"([^"]+)"\)', line)
        if m:
            assume_lines.append((i, m.group(1)))

    if not assume_lines:
        return "SKIP:no_assumes"

    # 3. 识别先验公式(不删除) — 从 priors.json
    prior_formulas = set()
    priors_path = data.dir.parents[1] / 'spec' / 'priors.json'
    if priors_path.exists():
        try:
            for x in json.load(open(priors_path)):
                prior_formulas.add(
                    re.sub(r'\s+', '', x.get('formula', '')))
        except Exception:
            pass

    # 4. 可删除的行 = 非先验的 chaAssume
    removable = [(i, f) for i, f in assume_lines
                 if re.sub(r'\s+', '', f) not in prior_formulas]
    if not removable:
        return "SKIP:all_priors"

    # 5. 逐行删除测试(简化: 一次删一行)
    # 对于"exclude_kids"中的条目, 我们尝试删除它们对应的行
    # 匹配策略: 归一化公式 + 信号声明推断
    # (这里用启发式: 如果公式长度相近且信号子串有交集, 视为可能匹配)
    to_remove = set()
    for kid in exclude_kids:
        e = data.kb.get(kid)
        if not e:
            continue
        kb_norm = re.sub(r'\s+', '', e.get('formula', ''))
        # 尝试精确匹配
        for i, f in removable:
            f_norm = re.sub(r'\s+', '', f)
            if f_norm == kb_norm:
                to_remove.add(i)
                continue
        # 启发式: 替换常见别名前缀
        kb_alt = kb_norm.replace('dcacheNastiReq', 'nastiReq')
        kb_alt2 = kb_norm.replace('nastiReq', 'dcacheNastiReq')
        for i, f in removable:
            f_norm = re.sub(r'\s+', '', f)
            if f_norm in (kb_alt, kb_alt2):
                to_remove.add(i)

    # 如果精确匹配失败, 退化为删除全部非先验行(测试"没有KB还能过吗")
    if not to_remove:
        to_remove = {i for i, _ in removable}

    # 6. 构造过滤后的内容
    filtered = [line for i, line in enumerate(all_lines)
                if i not in to_remove]

    # 4. 写入修改后的 Scala 文件
    test_file = REPO / 'src/test/scala/cha/TileTest.scala'
    # 备份当前文件
    if test_file.exists():
        import shutil
        backup_current = data.dir / 'sbt' / f'pre_ablation_{node_id}.scala.bak'
        shutil.copy2(test_file, backup_current)
    test_file.write_text('\n'.join(filtered))

    # 5. 运行 sbt BMC
    from cha_verify import run_sbt
    try:
        code, log = run_sbt("AGTileFlatPropSpec", timeout=120)
        # 解析结果
        if "All properties can be proven" in log or \
           "succeeded 1" in log:
            result = "PASS"
        elif "violation" in log or "failed 1" in log:
            result = "FAIL"
        else:
            result = f"UNKNOWN:{code}"
    except Exception as e:
        result = f"ERROR:{str(e)[:30]}"

    # 6. 恢复原文件
    if 'backup_current' in dir() and backup_current.exists():
        import shutil
        shutil.copy2(backup_current, test_file)

    return result


def _ablate_reconstruct(data, node_id, exclude_kids):
    """备份缺失时的消融: 从 final_proof_state 重建验证参数调 cha_verify."""
    try:
        from cha_verify import cha_verify

        node = data.nodes.get(node_id, {})
        formula = node.get('formula', '')
        signals = node.get('signals', {})
        module = data.node_module(node_id)
        if not formula or not module:
            return "SKIP:reconstruct_fail"

        # 构造 assume 集: 先验在 cha_verify 内烘焙, 只需 KB 子集
        assumes = []
        decls = []
        num = 100  # 避免与先验编号冲突

        # 节点自身信号
        for alias, sdef in signals.items():
            port = sdef.get('port', '')
            expr = sdef.get('expr', '')
            path = expr if expr else port
            if path.startswith('expr:'):
                path = path[5:]
            num += 1
            decls.append((alias, path, num))

        # 保留的 KB 条目
        for kid in data.kb:
            if kid in exclude_kids:
                continue
            e = data.kb[kid]
            # 只包含早于此节点的
            if data.kb_ts.get(kid, '99:99') >= data.verify_ts.get(node_id, '00:00'):
                continue
            e_formula = e.get('formula_raw') or e.get('formula', '')
            e_signals = e.get('signals', {})
            # 信号需要映射到目标模块的端口视图
            for alias, sdef in e_signals.items():
                port = sdef.get('port', '')
                if not port:
                    continue
                # 如果信号模块 == 目标模块, 直接用
                if sdef.get('module') == module:
                    num += 1
                    # 避免别名冲突
                    a = alias if alias not in dict(decls) else f"{alias}_r"
                    decls.append((a, port, num))
                    e_formula = e_formula.replace(alias, a)
            assumes.append(e_formula)

        # 先验
        priors_by_module = {}
        priors_path = data.dir.parents[1] / 'spec' / 'priors.json'
        if priors_path.exists():
            for x in json.load(open(priors_path)):
                m = x.get('module', '?')
                priors_by_module.setdefault(m, []).append(x)

        result = cha_verify(
            module=module,
            signals=decls,
            assert_formula=formula,
            assumes=assumes,
            mode="bmc",
            priors_by_module=priors_by_module,
        )
        return result.get("verdict", "?")
    except Exception as e:
        return f"ERROR:{str(e)[:40]}"


if __name__ == '__main__':
    run_dir = sys.argv[1] if len(sys.argv) > 1 else None
    do_ablate = '--ablate' in sys.argv
    if not run_dir:
        print("用法: python3 proof_tree_tool.py <run_dir> [--ablate]")
        sys.exit(1)

    data = RunData(run_dir)
    print(f"KB {len(data.kb)} 条, 节点 {len(data.nodes)}, 根 {data.root}")

    tree = build_tree(data, do_ablate)
    if tree:
        print(tree)
        summary = Path(run_dir) / 'SUMMARY.md'
        if summary.exists():
            existing = summary.read_text()
            existing = re.sub(r'\n## 7\. 层次化证明树.*$', '',
                              existing, flags=re.DOTALL)
            summary.write_text(existing + '\n' + tree + '\n')
            print(f"\n已追加到 {summary}")
    else:
        print("未生成证明树")
