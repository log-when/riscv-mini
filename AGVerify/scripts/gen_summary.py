#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SUMMARY 批量生成器: 对指定 run 目录生成 SUMMARY.md(直读账本)。
用法: python3 gen_summary.py <run_dir> [<run_dir> ...]"""
import json, sys, collections, re
from pathlib import Path

norm = lambda s: re.sub(r'\s+', '', s)

def enc(phases):
    g = m = i = '—'; alt = []; n_modfail = 0
    for p, v, mod, det in phases:
        if p == 'global_bmc':
            g = '✓' if v == 'PASS' else ('✗' if v == 'FAIL' else '编译✗')
        elif p == 'module_bmc':
            if v == 'PASS': m = '✓'
            elif v == 'FAIL':
                n_modfail += 1
                cyc = det.split('第')[1].split('拍')[0].strip() if '第' in det else '?'
                m = f'✗@{cyc}'
            else: m = '编译✗'
        elif p == 'module_ic3':
            i = '★' if v == 'PASS' else ('✗' if v == 'FAIL' else '编译✗')
        elif p.startswith('alt_bmc@') or p.startswith('alt_ic3@'):
            if v == 'PASS': alt.append(p.split('@')[1] + '★')
        elif p.startswith('alt_rewrite@'):
            alt.append('改写✗@' + p.split('@')[1])
    s = f'G{g}/M{m}/I{i}'
    if alt: s += ' (' + ', '.join(dict.fromkeys(alt)) + ')'
    if n_modfail > 1: s += f' [模块重验×{n_modfail}]'
    if g == m == i == '—': s = '复用/截留'
    return s

def _retro_conditional(run_dir: Path) -> dict:
    """回溯判定 module_ic3 PASS 是否条件证毕(旧账本无 conditional 字段):
    扫描 sbt 日志的 DIAG 头(ctx=模块|公式前缀|阶段)与 chaAssume 行数,
    假设数 > 该模块先验数 → 条件证毕。返回 {(模块, 公式前缀): True/False}"""
    import re, time as _t
    # 先验假设数(按模块)
    prior_n = {}
    pj = run_dir.parent.parent / 'spec' / 'priors.json'
    try:
        for x in json.loads(pj.read_text(encoding='utf-8')):
            prior_n[x['module']] = prior_n.get(x['module'], 0) + 1
    except Exception:
        pass
    out = {}
    for lg in (run_dir / 'sbt').glob('*.log'):
        try:
            head = open(lg, errors='ignore').read(4000)
        except Exception:
            continue
        m = re.search(r'\[DIAG\] ctx=(\w+)\|(.+?)\|ic3\|module', head)
        if not m:
            continue
        mod, fpre = m.group(1), m.group(2)
        n = head.count('chaAssumeStmt')
        if n > prior_n.get(mod, 0):
            out[(mod, fpre)] = True
        else:
            out.setdefault((mod, fpre), False)
    return out


def gen(run_dir: Path):
    R = str(run_dir)
    items_by_round = []; ph = collections.defaultdict(list)
    for line in open(run_dir / 'outcomes.jsonl'):
        d = json.loads(line)
        if d.get('kind') == 'decision':
            items_by_round.append((d['node'], d.get('goal'), d.get('goal_nl'),
                                   d.get('strategy'), d.get('items', []),
                                   d.get('ts', '')))
        elif d.get('phase'):
            ph[norm(d['formula'])].append(
                (d['phase'], d.get('verdict'), d.get('module'), d.get('detail', '')))
    rep = {}
    if (run_dir / 'report.json').exists():
        rep = json.load(open(run_dir / 'report.json'))
    concl = rep.get('conclusion', '运行中')
    kb = rep.get('kb', [])
    npass = sum(1 for v in ph.values() for x in v
                if x[1] == 'PASS')
    nic3 = sum(1 for v in ph.values() for x in v
               if x[0] == 'module_ic3' and x[1] == 'PASS')
    ics = [x for v in ph.values() for x in v
           if x[0] == 'module_ic3' and x[1] == 'PASS']
    nic3 = len(ics)
    # 全局 PASS 计数(账本口径)
    ngpass = sum(1 for v in ph.values() for x in v
                 if x[0] == 'global_bmc' and x[1] == 'PASS')

    L = []
    L.append(f'# SUMMARY — {run_dir.name}（{concl}）\n')
    L.append('## 1. 运行信息\n')
    L.append(f'- **结局**: {concl} | 轮次 {rep.get("rounds", len(items_by_round))} | '
             f'调用 {rep.get("agent_calls", "?")} | done {rep.get("done")} | '
             f'KB {len(kb)} 条')
    L.append(f'- **账本**: {len(items_by_round)} 轮 decision | '
             f'全局BMC PASS {ngpass} | 模块IC3证毕 {nic3}')
    try:
        _p = json.loads((run_dir.parent.parent / 'spec' /
                         'properties.json').read_text(encoding='utf-8'))
        _t = f"`{_p['formula']}`@{_p.get('module', '?')}"
    except Exception:
        _t = '(读取失败)'
    L.append(f'- 目标性质: {_t}\n')

    L.append('## 2. 目标演化轨迹\n')
    seen_goal = {}
    for rn, (node, goal, _, strat, items, _ts) in enumerate(items_by_round, 1):
        seen_goal.setdefault(goal, []).append(rn)
    for goal, rounds in seen_goal.items():
        tag = f'(×{len(rounds)})' if len(rounds) > 1 else ''
        L.append(f'- 轮 {rounds[0]}: `{goal}` {tag}')
    L.append('')

    L.append('## 3. 逐轮摘要表\n')
    L.append('| 轮 | node | 目标(缩写) | 策略 | 性质数 |')
    L.append('|---|---|---|---|---|')
    for rn, (node, goal, _, strat, items, _ts) in enumerate(items_by_round, 1):
        g = goal if len(goal) <= 44 else goal[:42] + '…'
        L.append(f'| {rn} | {node} | {g} | {strat} | {len(items)} |')
    L.append('')

    L.append('## 4. 逐条性质明细表（每轮全量, 含重复）\n')
    L.append('图例: G=全局BMC M=模块BMC I=模块IC3; ✓通过 ✗@N第N拍反例 —未达 '
             '★完备证毕; (…)内多落点; 复用/截留=KB复用或未上BMC。')
    L.append('每轮先列任务目标, 再列全部生成性质(不去重, 重复标 ×N); '
             '信号每行一条(别名 = 模块.定义); 轮末标有效性检查结果。\n')
    seen = set()
    seen_count = {}
    # 预收集每轮的有效性检查结果(按时间窗口匹配)
    # 收集各轮的失败记录(assume/property 被拒的原因)
    _round_failures = {}
    for line2 in open(run_dir / 'outcomes.jsonl'):
        d2 = json.loads(line2)
        if d2.get('kind') == 'decision':
            pass  # 轮号从 items_by_round 获取
    # 失败记录在 final_proof_state 里, 按 node+round 匹配
    try:
        fps = json.load(open(run_dir / 'final_proof_state.json'))
        for f2 in fps.get('failures', []):
            rn2 = f2.get('round', 0)
            _round_failures.setdefault(rn2, []).append(f2)
    except Exception:
        pass
    _raw_valids = [(d.get('ts',''), d.get('phase',''), d.get('verdict',''),
                    str(d.get('detail',''))[:60])
                   for d in map(json.loads, open(run_dir / 'outcomes.jsonl'))
                   if d.get('phase') and ('validity' in d.get('phase','')
                                          or d.get('phase') == 'implication')]
    valid_events = _raw_valids
    for rn, (node, goal, goal_nl, strat, items, rts) in enumerate(items_by_round, 1):
        L.append(f'**轮{rn} · node={node} · 策略={strat}**\n')
        L.append(f'> 任务目标: `{goal}`')
        L.append(f'> （{goal_nl}）\n')
        for it in items:
            if 'candidate_actions' in it: continue
            f = it['formula']; k = norm(f)
            seen_count[k] = seen_count.get(k, 0) + 1
            dup_tag = f' ×{seen_count[k]}' if k in seen else ''
            seen.add(k)
            sigs = it.get('signals') or {}
            mod = next(iter(sigs.values()))['module'] if sigs else '?'
            ab = {'ICache': 'IC', 'MemArbiter': 'MA', 'Datapath': 'DP',
                  'DCache': 'DC', 'Tile': 'T'}.get(mod, mod)
            L.append(f'- [{ab}] `{f}`{dup_tag}')
            for a, s in sigs.items():
                port = s.get('port')
                loc = port if port else 'expr:' + (s.get('expr') or '?')
                L.append(f'  - {a} = {s["module"]}.{loc}')
            L.append(f'  - 结果: {enc(ph.get(k, []))}')
        # 本轮被拒性质(从失败记录提取, 标注原因)
        round_fails = _round_failures.get(rn, [])
        if round_fails:
            for f2 in round_fails:
                cause2 = f2.get('cause', '?')
                ev2 = str(f2.get('evidence', ''))[:70]
                L.append(f'')
                L.append(f'  **被拒: ⚠ {cause2}** {ev2}')
            L.append(f'  (因上述被拒, 本轮回滚, 未做有效性检查)')

        # 本轮有效性检查结果(时间窗口: 本轮 ts 到下一轮 ts)
        # 轮内按 phase 去重(BMC+IC3 两段只报最终结果), 保留最后一条
        next_ts = items_by_round[rn][5] if rn < len(items_by_round) else '99:99'
        round_valids = [(ts2, ph2, v2, det2) for ts2, ph2, v2, det2 in valid_events
                        if rts <= ts2 < next_ts]
        if round_valids:
            by_phase = {}
            for ev in round_valids:
                by_phase[ev[1]] = ev  # 后者覆盖前者(最终结果)
            for ph2, (ts2, _, v2, det2) in sorted(by_phase.items()):
                # ASSUME 轮只显示 assume_validity; implication 属于兑现节点
                # (CONJUNCT) 的轮末检查, 混入父 ASSUME 窗口会误导
                if strat == 'ASSUME' and ph2 == 'implication':
                    continue
                icon = {'PASS': '✓', 'FAIL': '✗', 'ERROR': '⚠'}.get(v2, '?')
                L.append(f'')
                L.append(f'  **检查: {icon} {v2}** ({ph2}) {det2}')
        L.append('')

    L.append('## 5. 已证毕性质清单（模块 IC3, 按子模块）\n')
    L.append('图例: 无标记=无条件证毕(已入KB); ☆=条件证毕(依赖未兑现'
             '假设, 节点未终态, 不可当定理复用)\n')
    bymod = collections.defaultdict(list)
    for p, v, mod, det in ics:
        bymod[mod].append(det is None)
    retro = _retro_conditional(run_dir)
    prov = {}
    for line in open(run_dir / 'outcomes.jsonl'):
        d = json.loads(line)
        if d.get('phase') == 'module_ic3' and d.get('verdict') == 'PASS':
            cond = d.get('conditional')
            if cond is None:      # 旧账本: 回溯判定
                cond = retro.get((d.get('module'),
                                  d['formula'][:len(
                                      next((p for (m2, p) in retro
                                            if m2 == d.get('module')
                                            and d['formula'].startswith(p)),
                                           d['formula'][:40]))]), False)
                # 宽松回退: 任一同模块前缀匹配
                if cond is False:
                    cond = any(v and m2 == d.get('module')
                               and d['formula'].startswith(p)
                               for (m2, p), v in retro.items())
            tag = '☆' if cond else ''
            prov.setdefault(d['module'], []).append(tag + d['formula'])
    for mod in sorted(prov, key=lambda m: -len(prov[m])):
        L.append(f'### {mod}（{len(prov[mod])} 条）')
        for f in prov[mod]:
            L.append(f'- `{f}`')
        L.append('')

    L.append('## 6. 结论\n')
    L.append(f'- {"KB 定理 " + str(len(kb)) + " 条沉淀" if kb else "KB 无沉淀"}; '
             f'根目标 {"已证毕" if rep.get("done") else "未定案"}')
    L.append('- 义务链覆盖度与其他 run 的对比见跨轮总览')
    (run_dir / 'SUMMARY.md').write_text('\n'.join(L), encoding='utf-8')
    return len(seen), nic3, len(kb)

if __name__ == '__main__':
    for rd in sys.argv[1:]:
        n, ic3, kb = gen(Path(rd))
        print(f'{Path(rd).name}: 性质{n} IC3×{ic3} KB{kb} → SUMMARY.md')
