#!/bin/sh
URL="https://download1.dcloud.net.cn/download/HBuilderX.5.15.2026070915.linux_x64.full.tar.gz"
OUT="HBuilderX.5.15.2026070915.linux_x64.full.tar.gz"
TARGET=1559925221

while true; do
  SIZE=$(stat -c%s "$OUT" 2>/dev/null || echo 0)
  echo "$(date) size=$SIZE target=$TARGET" >> download-loop.log
  if [ "$SIZE" -ge "$TARGET" ]; then
    echo "download complete" >> download-loop.log
    break
  fi
  curl -L -C - --retry 5 --retry-delay 2 -o "$OUT" "$URL" >> download-loop.log 2>&1
  sleep 2
done
