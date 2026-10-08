#!/usr/bin/env python3
"""run 耗时报告: 从 outcomes.jsonl + llm_calls 重建每阶段耗时。

用法: python3 timing_report.py <run_dir>

方法:
  - 阶段耗时 = 相邻账本条目 ts 差(归属后一条的 phase), >30min 截断
  - LLM 窗口 = llm_calls 文件夹时间戳 ~ +meta.elapsed_sec, 从 gap 中扣除
    重叠得"工具纯耗时"
  - module_bmc 二次划分: 同节点紧随 module_ic3 条目 → "pre_ic3"(两段式
    第一段, BMC 过后续跑 IC3); 否则 → "bmc_only"(BMC 失败即止)
"""
import json, os, re, sys, collections, datetime


def parse_time(t, day_hint=None):
    return datetime.datetime.strptime(
        f"2026-{day_hint or day_of(t)} {t}", "%Y-%m-%d %H:%M:%S").timestamp()


def day_of(t):
    return "09"  # 按需扩展; 跨日 gap 由 +86400 兜底


def main(run_dir):
    rows = [json.loads(l) for l in open(os.path.join(run_dir, "outcomes.jsonl"))]
    if not rows:
        print("空账本"); return
    day = re.match(r"run_(\d{8})_\d{6}", os.path.basename(run_dir))
    day_hint = f"{day.group(1)[4:6]}-{day.group(1)[6:8]}" if day else None

    def T(t):
        return datetime.datetime.strptime(
            f"2026-{day_hint} {t}" if day_hint else t,
            ("%Y-%m-%d %H:%M:%S" if day_hint else "%H:%M:%S")).timestamp()

    # LLM 窗口
    llm = []
    lc = os.path.join(run_dir, "llm_calls")
    if os.path.isdir(lc):
        for d in os.listdir(lc):
            m = re.match(r"\d{8}_(\d{6})", d)
            if not m:
                continue
            try:
                meta = json.load(open(os.path.join(lc, d, "meta.json")))
            except OSError:
                continue
            hh, mm, ss = (int(m.group(1)[i:i+2]) for i in (0, 2, 4))
            base = datetime.datetime.strptime(
                f"2026-{day_hint or '09-29'} 00:00:00", "%Y-%m-%d %H:%M:%S")
            start = base.timestamp() + hh*3600 + mm*60 + ss
            llm.append((start, float(meta.get("elapsed_sec", 0))))
    llm.sort()

    def llm_overlap(a, b):
        s = 0.0
        for st, dur in llm:
            s += max(0.0, min(b, st + dur) - max(a, st))
        return s

    # module_bmc 二次划分: 同节点下一条同源验证条目是否为 module_ic3
    idx_by_node = collections.defaultdict(list)
    for i, d in enumerate(rows):
        if d.get("node"):
            idx_by_node[d["node"]].append(i)

    def bmc_kind(i):
        d = rows[i]
        for j in idx_by_node.get(d["node"], []):
            if j > i and rows[j].get("phase") == "module_ic3":
                # 中间不得隔 decision(隔了就不是同一次两段式)
                between = [rows[k].get("kind") for k in range(i+1, j)
                           if rows[k].get("node") == d["node"]]
                if not any(b == "decision" for b in between):
                    return "module_bmc(续IC3)"
        return "module_bmc(败即止)"

    agg = collections.defaultdict(lambda: [0.0, 0.0, 0])
    prev = None
    for i, d in enumerate(rows):
        t = T(d["ts"])
        ph = d.get("phase") or f"decision:{d.get('strategy', '?')}"
        if ph == "module_bmc":
            ph = bmc_kind(i)
        if prev is not None:
            gap = t - prev[0]
            if gap < 0:
                gap += 86400
            gap = min(gap, 1800)
            ov = llm_overlap(prev[0], t)
            agg[ph][0] += gap
            agg[ph][1] += max(0.0, gap - ov)
            agg[ph][2] += 1
        prev = (t, ph)

    llm_tot = sum(d for _, d in llm)
    print(f"== {os.path.basename(run_dir)} 耗时报告 ==")
    print(f"LLM: {len(llm)} 次纯调用 {llm_tot/3600:.1f}h "
          f"(均值 {llm_tot/max(1, len(llm)):.0f}s)")
    print(f"{'阶段':<28s}{'总耗时':>9s}{'工具纯':>9s}{'次数':>5s}{'均值':>8s}")
    for ph, (g, tl, n) in sorted(agg.items(), key=lambda kv: -kv[1][0]):
        print(f"{ph:<28s}{g/60:8.1f}m{tl/60:8.1f}m{n:5d}{g/max(1,n):7.1f}s")


if __name__ == "__main__":
    main(sys.argv[1])
