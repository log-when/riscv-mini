#!/bin/bash
# 自动修复守护 v2:
# 1) dispatcher 死亡: traceback→停等修复; 否则重启
# 2) 活性判据: 最新 run 的 outcomes.jsonl 30分钟无更新 且 进程活着
#    → 判定挂死(LLM挂死连接等), 杀掉重启
cd "$(dirname "$0")"
LOG=../run_detached.log
while true; do
  sleep 120
  D=$(pgrep -f "python3 dispatcher.py" | head -1)
  NEWEST=$(ls -t ../results/run_*/outcomes.jsonl 2>/dev/null | head -1)
  STALE=$( [ -n "$NEWEST" ] && find "$NEWEST" -mmin +30 | head -1 )
  if [ -n "$D" ] && [ -n "$STALE" ]; then
    echo "[autorestart] 账本30min无更新, 判定挂死, kill $D $(date +%H:%M:%S)" >> "$LOG"
    kill "$D"; sleep 5
  fi
  if ! pgrep -f "python3 dispatcher.py" > /dev/null; then
    if tail -50 "$LOG" 2>/dev/null | grep -q "Traceback"; then
      echo "[autorestart] 检测到代码崩溃(traceback), 暂不重启, 等待修复 $(date)" >> "$LOG"
      exit 1
    fi
    LC_ALL=C.UTF-8 python3 dispatcher.py ../spec/hierarchy.json ../spec/properties.json >> "$LOG" 2>&1 &
    echo "[autorestart] relaunched $(date +%H:%M:%S)" >> "$LOG"
  fi
done
