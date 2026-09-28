#!/usr/bin/env bash
# READ-ONLY discussion + public-notebook-score feed (tools/kaggle_feed.py) every 30 min until 29 Sep 23:59 UTC.
# Each run writes experiments/discussions/digest_<UTC>.md; a run with new topics/comments or an E10 flag appends one
# 'FEED SIGNAL' line to experiments/discussions/feed_loop.log (waiters grep for it).
# Start detached (PowerShell): Start-Process -FilePath 'C:\Program Files\Git\bin\bash.exe' -ArgumentList 'experiments/lb_poll/run_feed_loop.sh' -WorkingDirectory <repo> -WindowStyle Hidden
cd "/c/Users/vital/Documents/kAGGLE/Biohub - Cell Tracking During Development" || exit 1
PY=/c/Users/vital/AppData/Local/Programs/Python/Python312/python
LOG=experiments/discussions/feed_loop.log
while [ "$(date -u +%Y%m%d%H%M)" -lt 202609292359 ]; do
  out=$(PYTHONIOENCODING=utf-8 $PY tools/kaggle_feed.py 2>>"$LOG"); rc=$?
  line=$(printf '%s\n' "$out" | grep -m1 '^topics checked')
  flag=$(printf '%s\n' "$out" | grep -m1 '^E10 FLAG:')
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) rc=$rc | $line | $flag" >> "$LOG"
  if printf '%s\n' "$line" | grep -qvE 'new topics 0, new comments 0' || ! printf '%s\n' "$flag" | grep -q 'none'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FEED SIGNAL: $line | $flag | digest $(ls -t experiments/discussions/digest_*.md | head -1)" >> "$LOG"
  fi
  sleep 1800
done
