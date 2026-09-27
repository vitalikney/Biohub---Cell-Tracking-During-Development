#!/usr/bin/env bash
cd "/c/Users/vital/Documents/kAGGLE/Biohub - Cell Tracking During Development" || exit 1
until /c/Users/vital/AppData/Local/Programs/Python/Python312/python experiments/lb_poll/ladder_watch.py --s0 experiments/e10_watch/20260927T0147Z.txt --hard-cap 2026-09-27T11:30Z >> experiments/lb_poll/ladder_watch.stdout.log 2>&1; do
  echo "=== restart $(date -u +%Y-%m-%dT%H:%M:%SZ) rc=$?" >> experiments/lb_poll/ladder_watch.stdout.log
  sleep 120
done
