#!/usr/bin/env bash
# Can the "TTA over memorised views" explanation be falsified?
#
# Claim (CONTEXT_FRIEND_B.md §13): averaging predictions over the training augmentation group pays off on
# videos the model was trained on, because it averages over views the model has memorised, and that gain does
# not exist on unseen embryos - which is why exp31 (Z-flip TTA) gains +0.059 locally and loses 0.003 on the LB.
#
# Test: repeat the same TTA comparison with a primary that has genuinely never seen a 44b6 video.
# friend_a_exp02_loeo20 was trained from scratch on the 126 6bba videos only.
#
#   pilkwang primary  : delta(Z-flip)  = exp31 - exp30      <- both saw every 44b6 video in pretraining
#   scratch primary   : delta(Z-flip)  = scratchZ - scratch <- primary has never seen these videos
#
# A much smaller (or negative) delta on the scratch primary supports the explanation; an equal delta refutes
# it and sends the local-vs-LB discrepancy back to plain embryo difference.
#
# LIMITATION, stated so the result is not over-read: the Z-flip patch touches BOTH TTA loops, and the
# secondary stays pilkwang seed314159, which saw all 199 videos. Isolation is therefore partial and the
# expectation is a halved delta, not a zero one. The scratch model is also much weaker in absolute terms
# (raw 0.68 vs 0.88), so only the delta within each pair is comparable, never the absolute scores.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${BIOHUB_PYTHON:-$HOME/anaconda3/envs/biohub/bin/python}"
NB29="$ROOT/experiments/exp29_sjlee947_verbatim/exp29-sjlee947-verbatim.ipynb"
NB31="$ROOT/experiments/exp31_sjlee947_ft03B_zflip/exp31-sjlee947-ft03B-zflip.ipynb"
SPLIT=(--split "$ROOT/experiments/_lib/loeo_train6bba_val44b6.json" --key holdout)
SCRATCH=friend_a_exp02_loeo20

echo "################ scratch primary, public TTA"
"$PY" "$ROOT/tools/public_local.py" --notebook "$NB29" --tag scratch_publicTTA --label base \
    "${SPLIT[@]}" --primary "$SCRATCH"

echo "################ scratch primary, + Z-flip TTA"
"$PY" "$ROOT/tools/public_local.py" --notebook "$NB31" --tag scratch_zflipTTA --label base \
    "${SPLIT[@]}" --primary "$SCRATCH"

echo "################ deltas"
"$PY" - <<'EOF'
import json
from pathlib import Path
cache = Path(__file__).resolve().parent if False else Path("/home/georgii/Documents/Biohub---Cell-Tracking-During-Development/.public_local_cache")


def score(tag):
    p = cache / tag / "pp" / "base.json"
    return json.loads(p.read_text())["summary"]["score"] if p.is_file() else None


pairs = [("pilkwang primary (saw every 44b6 video)", "exp30", "exp31"),
         ("scratch primary (never saw a 44b6 video)", "scratch_publicTTA", "scratch_zflipTTA")]
print(f"{'primary':42s} {'public TTA':>11s} {'+Z-flip':>9s} {'delta':>9s}")
for name, a, b in pairs:
    sa, sb = score(a), score(b)
    if sa is None or sb is None:
        print(f"{name:42s} {'-':>11s} {'-':>9s} {'(missing)':>9s}")
        continue
    print(f"{name:42s} {sa:11.4f} {sb:9.4f} {sb - sa:+9.4f}")
print("\nLeaderboard delta for the same change (probe 12 vs 11): -0.003")
EOF
