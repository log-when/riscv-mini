#!/bin/bash
# 永久链式看护: 当前 dispatcher 退出后立即启动下一个, 无限循环
cd "$(dirname "$0")"
while true; do
  D=$(pgrep -f "python3 dispatcher.py" | head -1)
  if [ -z "$D" ]; then
    LC_ALL=C.UTF-8 python3 dispatcher.py ../spec/hierarchy.json ../spec/properties.json >> ../run_detached.log 2>&1 &
    echo "[chain] launched $(date +%H:%M:%S)" >> ../run_detached.log
  fi
  sleep 60
done
