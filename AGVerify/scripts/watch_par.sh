#!/bin/bash
# 并行双跑看护器 (每侧一份, 按 PID 文件区分, 不误匹配对侧):
#   - 本侧 dispatcher 死亡 → 用当前代码重启 (持续运行直到成功)
#   - 任一侧 SUCCESS (标志文件 /tmp/agverify_par_success) → 双侧退出
#   - 只认看护器启动之后产生的新 run 的 report (忽略历史 SUCCESS)
cd "$(dirname "$0")"
PIDFILE=../.dispatcher.pid
LOG=../run_par.log
FLAG=/tmp/agverify_par_success
# 基准: 启动时已存在的最新 run 目录 (之后的才算数)
BASE_REF=$(ls -td ../results/run_*/report.json 2>/dev/null | head -1)
echo "[watch] start $(date '+%m-%d %H:%M:%S') base_ref=${BASE_REF:-none}" >> "$LOG"
while true; do
  [ -f "$FLAG" ] && { echo "[watch] 双侧任务已成功, 退出" >> "$LOG"; exit 0; }
  # 新 run 的 SUCCESS 检查
  L=$(ls -td ../results/run_*/report.json 2>/dev/null | head -1)
  if [ -n "$L" ] && [ "$L" != "$BASE_REF" ]; then
    CONCL=$(python3 -c "import json;print(json.load(open('$L')).get('conclusion',''))" 2>/dev/null)
    if [ "$CONCL" = "SUCCESS" ]; then
      touch "$FLAG"
      echo "[watch] 本侧 SUCCESS ($L), 已置全局成功标志" >> "$LOG"
      exit 0
    fi
  fi
  # 本侧进程存活检查 (PID 文件, 不看对侧)
  if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    sleep 60; continue
  fi
  LC_ALL=C.UTF-8 python3 dispatcher.py ../spec/hierarchy.json ../spec/properties.json >> "$LOG" 2>&1 &
  echo $! > "$PIDFILE"
  echo "[watch] launched $(date '+%m-%d %H:%M:%S') pid=$(cat "$PIDFILE")" >> "$LOG"
  sleep 60
done
