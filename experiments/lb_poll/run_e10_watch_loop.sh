#!/usr/bin/env bash
# Restart wrapper for the READ-ONLY hourly E10 v3 watch loop (exits 0 at 29 Sep 12:00 UTC, which ends the wrapper).
# Start it in the background from any shell:  bash experiments/lb_poll/run_e10_watch_loop.sh &
# Watch for signals:  grep "E10 SIGNAL:" experiments/e10_watch/watch_loop.log
cd "/c/Users/vital/Documents/kAGGLE/Biohub - Cell Tracking During Development" || exit 1
until /c/Users/vital/AppData/Local/Programs/Python/Python312/python experiments/lb_poll/e10_watch_loop.py >> experiments/e10_watch/watch_loop.stdout.log 2>&1; do
  echo "=== restart $(date -u +%Y-%m-%dT%H:%M:%SZ) rc=$?" >> experiments/e10_watch/watch_loop.stdout.log
  sleep 120
done
