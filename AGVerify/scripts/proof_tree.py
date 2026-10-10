#!/usr/bin/env python3
"""层次化证明恢复工具 (2026-10-10).

用法:
  python3 proof_tree.py <run_dir>                   # 被动分析 + 消融 + 证明树
  python3 proof_tree.py <run_dir> --no-ablate       # 仅被动分析(快速, 不跑 sbt)

功能:
  1. 解析 run 的 KB 标签 / Scala 备份 → 每条验证烘入了哪些 KB 条目(全集)
  2. 消融: 逐条移除 KB 前提 + BMC 重跑 → 最小必要集
  3. 递归构建依赖 DAG → 渲染证明树 + 性质明细表
"""
import json, sys, re, collections
from pathlib import Path


# ══════════════════════════════════════════════════════════════════
# 被动分析: 从账本 + Scala 备份提取依赖全集
# ══════════════════════════════════════════════════════════════════

def extract_deps(run_dir):
    """从 run 目录提取每条验证的 KB 依赖.

    返回 {node_id: {
        'formula': str,
        'module': str,
        'phase': str,          # module_ic3 / assume_validity
        'kb_used': [kid],      # 烘入的 KB 条目(全集)
        'priors': [formula],   # 烘入的先验公式
        'own_assumes': [formula],  # 自身假设
    }}
    """
    deps = {}
    kb_by_formula = {}  # 归一化公式 → kid

    s = json.load(open(Path(run_dir) / 'final_proof_state.json'))
    for e in s.get('kb', []):
        norm = re.sub(r'\s+', '', e.get('formula', ''))
        kb_by_formula[norm] = e['kid']

    nodes = s.get('nodes', {})
    node_info = {}
    if isinstance(nodes, dict):
        node_info = nodes

    for line in open(Path(run_dir) / 'outcomes.jsonl'):
        d = json.loads(line)
        if d.get('verdict') != 'PASS':
            continue
        phase = d.get('phase', '')
        if phase not in ('module_ic3',):
            continue
        node_id = d.get('node', '?')
        detail = str(d.get('detail', ''))

        # 新格式: [KB:T5,T7,...]
        kb_kids = []
        m = re.search(r'\[KB:([T0-9,]+)\]', detail)
        if m:
            kb_kids = m.group(1).split(',')
        else:
            # 旧格式: 从 Scala 备份解析
            kb_kids = _parse_scala_deps(run_dir, d, kb_by_formula)

        n = node_info.get(node_id, {})
        deps[node_id] = {
            'formula': d.get('formula', ''),
            'module': d.get('module', '?'),
            'phase': phase,
            'kb_used': kb_kids,
            'ts': d.get('ts', ''),
        }
    return deps, kb_by_formula


def _parse_scala_deps(run_dir, outcome, kb_by_formula):
    """从 Scala 备份解析 chaAssume 公式, 匹配 KB 条目."""
    ts = outcome.get('ts', '')
    # 找最近的备份 (时间戳相近)
    best = None
    for f in Path(run_dir, 'sbt').glob('backup_*.scala'):
        file_ts = f.stem.split('_')[-1]
        try:
            ft = int(file_ts)
            ot = int(ts.replace(':', ''))  # HH:MM:SS → HHMMSS
            # 不精确, 用日志的 DIAG 时间更准
        except ValueError:
            continue
        best = f
        break

    if not best or not best.exists():
        return []

    content = best.read_text(errors='ignore')
    kids = []
    for m in re.finditer(r'chaAssume\(this,\s*"([^"]+)"\)', content):
        formula = m.group(1)
        norm = re.sub(r'\s+', '', formula)
        if norm in kb_by_formula:
            kids.append(kb_by_formula[norm])
    return list(set(kids))


# ══════════════════════════════════════════════════════════════════
# 消融: 逐条移除 KB 前提, BMC 重跑
# ══════════════════════════════════════════════════════════════════

def ablate(run_dir, deps, do_ablate=True):
    """对每条验证做消融, 更新 kb_used 为最小必要集.

    消融顺序: T 编号降序(先移除晚期条目, 保留基础条目).
    返回更新后的 deps + 消融日志.
    """
    if not do_ablate:
        return deps, []

    s = json.load(open(Path(run_dir) / 'final_proof_state.json'))
    kb_entries = {e['kid']: e for e in s.get('kb', [])}
    log = []

    for node_id in sorted(deps, key=lambda x: deps[x].get('ts', '')):
        info = deps[node_id]
        kids = info['kb_used']
        if len(kids) <= 1:
            continue  # 只有一条或零条, 无需消融

        remaining = list(kids)
        # 降序: 先尝试移除编号大的(晚期, 复杂的)
        for kid in sorted(kids, reverse=True):
            trial = [k for k in remaining if k != kid]
            if not trial:
                continue  # 不能全删
            result = _bmc_without(run_dir, node_id, info, trial, kb_entries)
            if result == 'PASS':
                remaining = trial
                log.append(f"  {node_id}: {kid} 冗余(移除后 PASS)")
            else:
                log.append(f"  {node_id}: {kid} 必要({result})")

        deps[node_id]['kb_minimal'] = remaining
        removed = set(kids) - set(remaining)
        if removed:
            log.append(f"  {node_id}: 最小集 {remaining} (移除 {sorted(removed)})")

    return deps, log


def _bmc_without(run_dir, node_id, info, kb_kids, kb_entries):
    """构造去掉指定 KB 前提的验证并跑 BMC.

    这里需要调用 cha_verify. 为简化, 先返回模拟结果.
    实际实现需要:
    1. 从 final_proof_state 取节点信号
    2. 构造 chaVerify 参数(排除 kb_kids 之外的条目)
    3. 调用 self.verifier(mode="bmc", ...)
    """
    # TODO: 实际 BMC 调用
    # 目前返回模拟结果用于测试
    return "SKIP"  # 占位


# ══════════════════════════════════════════════════════════════════
# 证明树渲染
# ══════════════════════════════════════════════════════════════════

def render_tree(run_dir, deps, kb_info):
    """渲染层次化证明树 + 性质明细表."""
    s = json.load(open(Path(run_dir) / 'final_proof_state.json'))
    nodes = s.get('nodes', {})
    kb_entries = {e['kid']: e for e in s.get('kb', [])}
    root_id = s.get('root', '')

    L = []
    L.append('\n## 7. 层次化证明树\n')

    # 递归渲染
    def render(node_id, indent, visited):
        if node_id in visited:
            L.append(f"{'  ' * indent}↻ {node_id} (已展示)")
            return
        visited.add(node_id)

        if node_id in kb_entries:
            e = kb_entries[node_id]
            # KB 条目
            dep_key = 'kb_minimal' if 'kb_minimal' in deps.get(node_id, {}) else 'kb_used'
            kb_deps = deps.get(node_id, {}).get(dep_key, [])
            L.append(f"{'  ' * indent}[{e['kid']}] {e['formula'][:55]} @{e.get('proven_at', '?')}")
            for kd in sorted(kb_deps):
                if kd != node_id:  # 避免自引用
                    render(kd, indent + 1, visited)
        elif node_id in nodes:
            n = nodes[node_id]
            # 证明节点
            info = deps.get(node_id, {})
            dep_key = 'kb_minimal' if 'kb_minimal' in info else 'kb_used'
            kb_deps = info.get(dep_key, [])
            L.append(f"{'  ' * indent}{node_id}: {n.get('formula', '')[:55]} @{info.get('module', n.get('derived', {}).get('module', '?'))}")
            # 递归渲染 KB 依赖
            for kd in sorted(kb_deps):
                render(kd, indent + 1, visited)
            # 递归渲染子节点/假设
            for c in (n.get('children') or []):
                render(c, indent + 1, visited)
            for a in (n.get('assumes') or []):
                an = nodes.get(a, {})
                L.append(f"{'  ' * (indent+1)}ASSUME: {an.get('formula', '')[:50}")
                did = an.get('discharged_by')
                if did:
                    render(did, indent + 2, visited)

    if root_id:
        render(root_id, 0, set())

    # 性质明细表
    L.append('\n### 性质明细\n')
    L.append('| 标签 | 性质 | 验证模块 | 使用模块 | 信号 |')
    L.append('|---|---|---|---|---|')
    shown = set()
    for node_id in sorted(deps):
        info = deps[node_id]
        dep_key = 'kb_minimal' if 'kb_minimal' in info else 'kb_used'
        for kid in info.get(dep_key, []):
            if kid in shown:
                continue
            shown.add(kid)
            e = kb_entries.get(kid, {})
            sigs = e.get('signals', {})
            sig_str = ', '.join(f"{a}={v.get('port', '?')}" for a, v in sigs.items())
            verified_at = e.get('proven_at', '?')
            used_at = info.get('module', '?')
            cross = f" → {used_at}" if used_at != verified_at else ""
            L.append(f"| {kid} | `{e.get('formula', '?')[:45]}` | {verified_at}{cross} | {used_at} | `{sig_str[:50]}` |")

    # 节点自身
    for node_id in sorted(deps):
        info = deps[node_id]
        if node_id in shown:
            continue
        shown.add(node_id)
        n = nodes.get(node_id, {})
        sigs = n.get('signals', {})
        sig_str = ', '.join(f"{a}={v.get('port', '?')}" for a, v in sigs.items())
        L.append(f"| {node_id} | `{info.get('formula', '?')[:45]}` | {info.get('module', '?')} | — | `{sig_str[:50]}` |")

    return '\n'.join(L)


# ══════════════════════════════════════════════════════════════════
# 主入口
# ══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    run_dir = sys.argv[1] if len(sys.argv) > 1 else None
    do_ablate = '--no-ablate' not in sys.argv
    if not run_dir:
        print("用法: python3 proof_tree.py <run_dir> [--no-ablate]")
        sys.exit(1)

    deps, kb_by_formula = extract_deps(run_dir)
    print(f"提取到 {len(deps)} 条验证的 KB 依赖")

    if do_ablate:
        deps, log = ablate(run_dir, deps, do_ablate)
        for l in log:
            print(l)

    tree = render_tree(run_dir, deps, kb_by_formula)
    print(tree)

    # 追加到 SUMMARY
    summary_path = Path(run_dir) / 'SUMMARY.md'
    if summary_path.exists():
        existing = summary_path.read_text()
        # 去掉旧的证明树(如果有)
        existing = re.sub(r'\n## 7\. 层次化证明树.*$', '', existing, flags=re.DOTALL)
        summary_path.write_text(existing + '\n' + tree + '\n')
        print(f"\n已追加到 {summary_path}")
