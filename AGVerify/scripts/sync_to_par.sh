#!/bin/bash
# 代码同步: 主侧 → 并行侧 (riscv-mini-par)。
# 运行中的 B 进程不受影响 (python 已加载), 重启时生效 — "不终止, 保同步"。
# 用法: 在主侧 AGVerify/scripts/ 下执行 ./sync_to_par.sh
SRC="$(cd "$(dirname "$0")/.." && pwd)"
DST="$SRC/../../riscv-mini-par/AGVerify"
if [ ! -d "$DST" ]; then
  echo "并行侧不存在: $DST"; exit 1
fi
rsync -a --delete \
  --exclude='__pycache__' --exclude='.dispatcher.pid' --exclude='run_par.log' \
  --exclude='results' --exclude='out' --exclude='run_detached*.log' \
  "$SRC/scripts/" "$DST/scripts/"
rsync -a --delete --exclude='__pycache__' "$SRC/tools/" "$DST/tools/"
rsync -a --delete --exclude='__pycache__' --exclude='.env' "$SRC/agents/" "$DST/agents/"
rsync -a "$SRC/spec/" "$DST/spec/"
cp "$SRC/config.json" "$DST/config.json"
echo "同步完成 → $DST ($(date '+%H:%M:%S'))"
echo "注意: B 侧运行中进程不受影响, 其 dispatcher 死亡后由看护器以新代码重启"
