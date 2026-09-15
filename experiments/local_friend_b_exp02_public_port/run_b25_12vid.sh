#!/usr/bin/env bash
# B25 on all 12 LOEO-44b6 videos. Waits for the 12-video calibration driver to finish (so the GPU is free and
# the raw cache is complete), then: exp29 inference with peak_prob stored, LOO pruner, pruned sets at several
# fractions, official post-processing on each, table (ALL / CLEAN / LEAKY do not matter here - this is a
# within-model comparison - but recall after post-processing does).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${BIOHUB_PYTHON:-$HOME/anaconda3/envs/biohub/bin/python}"
HERE="$ROOT/experiments/local_friend_b_exp02_public_port"
DRIVER_PID_FILE="${1:-/tmp/claude-1000/full12.pid}"
cd "$ROOT"
SPLIT=(--split "$ROOT/experiments/_lib/loeo_train6bba_val44b6.json" --key holdout)
FRACS="0.05 0.08 0.10 0.12 0.13"

echo "=== waiting for the calibration driver ($(date '+%H:%M'))"
if [ -f "$DRIVER_PID_FILE" ]; then pid="$(cat "$DRIVER_PID_FILE")"; while kill -0 "$pid" 2>/dev/null; do sleep 60; done; fi

echo "=== exp29 inference with peak_prob on 12 videos ($(date '+%H:%M'))"
"$PY" tools/public_local.py --tag exp29pp --label base "${SPLIT[@]}" --keep-peak-prob

echo "=== LOO pruner ($(date '+%H:%M'))"
"$PY" "$HERE/b25_prune.py" --tag exp29pp --fractions $FRACS

for f in $FRACS; do
  X=$(printf '%02d' "$(python3 -c "print(round($f*100))")")
  echo "=== post-processing prune$X ($(date '+%H:%M'))"
  "$PY" tools/public_local.py --tag "exp29pp_prune$X" --label base --stage pp "${SPLIT[@]}"
done

echo "=== B25 table on 12 videos"
"$PY" - "$FRACS" <<'PYEOF'
import json, sys
from pathlib import Path
C = Path('.public_local_cache')
LEAKY = {"44b6_12dfb391","44b6_2a2eff9f","44b6_a21120c2","44b6_c50204e0","44b6_d2f34f90","44b6_d5e7d891"}
sys.path.insert(0, 'tools/official/src')
from tracking_cellmot.metrics import summarise
def load(t): return json.load(open(C/t/'pp'/'base.json'))
def sub(d, keep): return summarise([r for r in d['metric_rows'] if keep(r['dataset'])])
base = load('exp29pp')
pr = {p['tag']: p for p in json.load(open(C/'exp29pp'/'b25_prune_summary.json'))['pruning']}
tags = ['exp29pp'] + [f"exp29pp_prune{int(round(float(f)*100)):02d}" for f in sys.argv[1].split()]
for name, keep in [('ALL 12', lambda d: True), ('CLEAN 6', lambda d: d not in LEAKY)]:
    print(f"\n### {name}")
    print(f"{'set':18s} {'score':>8s} {'delta':>8s} {'edge':>8s} {'recall':>8s} {'annot.recall@cut':>16s}")
    b = sub(base, keep)
    for t in tags:
        try:
            s = sub(load(t), keep)
        except Exception as e:
            print(t, 'MISSING', e); continue
        cut = pr.get(t, {}).get('annotated_recall_after_prune', float('nan'))
        print(f"{t.replace('exp29pp','base'):18s} {s['score']:8.4f} {s['score']-b['score']:+8.4f} {s['edge_jaccard']:8.4f} {s['node_recall']:8.4f} {cut:16.4f}")
PYEOF
"$PY" "$HERE/collect_results.py" > /dev/null
echo "=== B25 12-video results collected - commit and push ($(date '+%H:%M'))"
