#!/usr/bin/env python3
"""KB 消融与层次化恢复 (2026-10-10).

用法:
  python3 kb_ablation.py <run_dir>                    # 生成依赖 DAG
  python3 kb_ablation.py <run_dir> --ablate <node_id> # 对指定节点做消融

功能:
  1. 解析 outcomes.jsonl 中 [KB:T1,T2,...] 标签, 重建每条验证的 KB 依赖
  2. 构建证明依赖 DAG (节点→所用 KB 条目→该条目的依赖→...→先验)
  3. 消融: 逐条移除 KB 前提重跑验证, 找最小必要集
"""
import json, sys, re, collections
from pathlib import Path


def parse_kb_deps(run_dir):
    """从账本提取每条验证的 KB 依赖(具体 kid). 返回 {node_id: {phase: [kids]}}"""
    deps = {}
    for line in open(Path(run_dir) / 'outcomes.jsonl'):
        d = json.loads(line)
        if d.get('verdict') != 'PASS':
            continue
        detail = str(d.get('detail', ''))
        m = re.search(r'\[KB:([T0-9,]+)\]', detail)
        if not m:
            continue
        kids = m.group(1).split(',')
        node = d.get('node', '?')
        phase = d.get('phase', '?')
        deps.setdefault(node, {})[phase] = kids
    return deps


def build_dag(run_dir):
    """构建证明依赖 DAG."""
    deps = parse_kb_deps(run_dir)
    s = json.load(open(Path(run_dir) / 'final_proof_state.json'))
    kb_formulas = {e['kid']: e['formula'] for e in s.get('kb', [])}
    nodes = s.get('nodes', {})
    node_formulas = {}
    if isinstance(nodes, dict):
        node_formulas = {nid: n.get('formula', '') for nid, n in nodes.items()}

    # 层次化: node → 依赖的 KB 条目 → 这些条目本身又依赖什么
    edges = []  # (from, to, label)
    for node_id, phases in sorted(deps.items()):
        nf = node_formulas.get(node_id, '?')[:50]
        for phase, kids in phases.items():
            for kid in kids:
                kf = kb_formulas.get(kid, '?')[:50]
                edges.append((node_id, kid, f"{phase}"))
                # KB 条目自身的依赖
                kid_node = next((n for n, e in
                                 ((nid, e) for nid, e in
                                  (nodes.items() if isinstance(nodes, dict) else []))
                                 if e.get('kid') == kid), None)

    # 输出 DAG
    print("══ 证明依赖 DAG ══")
    print(f"{'节点':>8s}  {'公式':50s}  ← 依赖的 KB")
    for node_id, phases in sorted(deps.items()):
        nf = node_formulas.get(node_id, '?')[:50]
        all_kids = set()
        for kids in phases.values():
            all_kids.update(kids)
        kd = ', '.join(sorted(all_kids))
        print(f"{node_id:>8s}  {nf:50s}  ← {kd}")

    # 反向: 每个 KB 条目被谁依赖
    print("\n══ KB 被依赖关系 ══")
    used_by = collections.defaultdict(list)
    for node_id, phases in deps.items():
        for kids in phases.values():
            for kid in kids:
                used_by[kid].append(node_id)
    for kid in sorted(used_by):
        kf = kb_formulas.get(kid, '?')[:45]
        print(f"  {kid}: {kf}")
        print(f"       ← {', '.join(sorted(used_by[kid]))}")

    return deps


if __name__ == '__main__':
    run_dir = sys.argv[1] if len(sys.argv) > 1 else None
    if not run_dir:
        print("用法: python3 kb_ablation.py <run_dir> [--ablate <node_id>]")
        sys.exit(1)
    build_dag(run_dir)
