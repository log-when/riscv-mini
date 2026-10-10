#!/usr/bin/env python3
"""对已完成的 run 重放证明树构建 (2026-10-10).

用法: python3 replay_proof_tree.py <run_dir> [--no-ablate]

从 final_proof_state.json + outcomes.jsonl 恢复状态,
调用 Dispatcher._build_proof_tree 输出证明树.
"""
import json, sys, re
from pathlib import Path

# 设置路径
AGV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGV / 'scripts'))
sys.path.insert(0, str(AGV / 'agents'))
sys.path.insert(0, str(AGV / 'tools'))


def replay(run_dir, do_ablate=True):
    run_dir = Path(run_dir)

    # 1. 加载 spec 路径 (从 run 的同级找)
    spec_dir = run_dir.parents[1] / 'spec'
    hier = spec_dir / 'hierarchy.json'
    props = spec_dir / 'properties.json'

    # 2. 创建 Dispatcher (只为了 verifier 和 _materialize)
    import dispatcher as dp
    
    import proof_state

    # 3. 创建 Dispatcher 实例
    disp = dp.Dispatcher(
        str(hier), str(props),
        priors_path=str(spec_dir / 'priors.json'))

    # 4. 替换 ProofState 为保存的状态
    saved = json.load(open(run_dir / 'final_proof_state.json'))
    # 恢复 KB: 直接创建 KBEntry
    from proof_state import KBEntry
    disp.st.kb.entries = []
    for e in saved.get('kb', []):
        entry = KBEntry(
            kid=e.get('kid', ''),
            formula=e.get('formula', ''),
            nl=e.get('nl', ''),
            formula_raw=e.get('formula_raw', ''),
            wire_ids=e.get('wire_ids', []),
            node_origin=e.get('node_origin', ''),
            signals=e.get('signals', {}),
            proven_at=e.get('proven_at'),
        )
        disp.st.kb.entries.append(entry)

    # 5. 恢复 outcome records
    disp._outcome_records = []
    for line in open(run_dir / 'outcomes.jsonl'):
        d = json.loads(line)
        disp._outcome_records.append({
            "node": d.get("node"),
            "phase": d.get("phase"),
            "module": d.get("module"),
            "verdict": d.get("verdict"),
            "detail": d.get("detail", ""),
            "_ts": d.get("ts", ""),
        })

    # 6. 恢复节点状态
    nodes = saved.get('nodes', {})
    for nid, ndata in nodes.items():
        # 创建 Node 对象
        from proof_state import Node
        n = Node(
            id=nid,
            kind=ndata.get('kind', 'assert'),
            formula=ndata.get('formula', ''),
            nl=ndata.get('nl', ''),
            signals=ndata.get('signals', {}),
            derived=ndata.get('derived', {}),
            strategy=ndata.get('strategy'),
            children=ndata.get('children', []),
            assumes=ndata.get('assumes', []),
            depth=ndata.get('depth', 0),
            status=ndata.get('status', 'PENDING'),
        )
        n.discharged_by = ndata.get('discharged_by')
        n.parent = ndata.get('parent')
        disp.st.nodes[nid] = n

    disp.st.root = saved.get('root', '')

    # 7. 设置消融开关
    import proof_state as ps
    ps.CONFIG['proof_tree_ablate'] = do_ablate

    # 8. 调用 _build_proof_tree
    tree = disp._build_proof_tree()
    if tree:
        print(tree)
        # 追加到 SUMMARY
        summary_path = run_dir / 'SUMMARY.md'
        if summary_path.exists():
            existing = summary_path.read_text()
            existing = re.sub(r'\n## 7\. 层次化证明树.*$', '',
                              existing, flags=re.DOTALL)
            summary_path.write_text(existing + '\n' + tree + '\n')
            print(f"\n已追加到 {summary_path}")
    else:
        print("未生成证明树(可能无依赖或状态不完整)")


if __name__ == '__main__':
    run_dir = sys.argv[1] if len(sys.argv) > 1 else None
    do_ablate = '--no-ablate' not in sys.argv
    if not run_dir:
        print("用法: python3 replay_proof_tree.py <run_dir> [--no-ablate]")
        sys.exit(1)
    replay(run_dir, do_ablate)
