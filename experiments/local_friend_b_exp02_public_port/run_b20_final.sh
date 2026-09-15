#!/usr/bin/env bash
# B20 verdict on all 199 videos, run after stream_bundles.py has finished (CONTEXT_FRIEND_B.md §38.10).
# Trains the ranker (add and steal), then re-runs the division stage from the pass-1 checkpoints with the shipped
# ranking (control) and with out-of-fold GBM scores at several thresholds, and scores everything officially.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; PY="${BIOHUB_PYTHON:-$HOME/anaconda3/envs/biohub/bin/python}"
HERE="$ROOT/experiments/local_friend_b_exp02_public_port"; R="$HERE/results"; cd "$ROOT"
N=$(ls .public_local_cache/exp29pp/ckpt | wc -l); echo "=== B20 final on $N videos with checkpoints ($(date '+%H:%M'))"
for mode in add steal; do
  echo "=== train $mode"; "$PY" "$HERE/b20_train_ranker.py" --mode $mode > "$R/b20_train_${mode}_199.log" 2>&1; tail -20 "$R/b20_train_${mode}_199.log"
done
echo "=== pass 2: control"; "$PY" "$HERE/pass2_rank_divisions.py" --tag exp29pp --ranker public --mode add --label p2_public_add_199 > "$R/p2_public_add_199.log" 2>&1; grep '^== ' "$R/p2_public_add_199.log"
for mode in add steal; do for key in oof_embryo oof_video; do for thr in 0.5 0.7 0.8 0.9; do
  lab="p2_gbm_${mode}_${key}_t${thr}"; echo "=== pass 2: $lab"
  "$PY" "$HERE/pass2_rank_divisions.py" --tag exp29pp --ranker gbm --mode $mode --scores-file "$R/b20_oof_${mode}.npz" --scores-key $key --min-score $thr --label "$lab" > "$R/$lab.log" 2>&1
  grep '^== ' "$R/$lab.log" || tail -3 "$R/$lab.log"
done; done; done
echo "=== table"; "$PY" - <<'PYEOF'
import json, sys
from pathlib import Path
sys.path.insert(0, 'tools/official/src'); from tracking_cellmot.metrics import summarise
C = Path('.public_local_cache/exp29pp/pp')
def load(l): return json.load(open(C / f'{l}.json'))
labs = ['p2_public_add_199'] + [f'p2_gbm_{m}_{k}_t{t}' for m in ('add', 'steal') for k in ('oof_embryo', 'oof_video') for t in ('0.5', '0.7', '0.8', '0.9')]
base = load('p2_public_add_199')
for name, keep in [('ALL', lambda d: True), ('44b6', lambda d: d.startswith('44b6')), ('6bba', lambda d: d.startswith('6bba'))]:
    print(f"\n### {name}"); print(f"{'variant':32s} {'score':>8s} {'delta':>8s} {'adj_edge':>9s} {'div_J':>7s} {'TP/FP/FN':>12s}")
    b = summarise([r for r in base['metric_rows'] if keep(r['dataset'])])
    for l in labs:
        try: s = summarise([r for r in load(l)['metric_rows'] if keep(r['dataset'])])
        except Exception: continue
        print(f"{l:32s} {s['score']:8.4f} {s['score']-b['score']:+8.4f} {s['adj_edge_jaccard']:9.4f} {s['division_jaccard']:7.4f} {int(s['division_tp']):4d}/{int(s['division_fp']):4d}/{int(s['division_fn']):3d}")
PYEOF
"$PY" "$HERE/collect_results.py" > /dev/null; echo "=== B20 FINAL DONE ($(date '+%H:%M')) - commit and push results/"
