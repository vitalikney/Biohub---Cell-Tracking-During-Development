#!/usr/bin/env bash
# STEP 4 calibration: reproduce the four LB-probed configurations of 2026-09-10 locally and compare the
# local ranking with the known leaderboard ranking (exp29 0.947 > exp30 0.944 > exp31 0.941 > exp32 0.937).
#
# Measured beforehand (see CONTEXT_FRIEND_B.md §4.2): the post-processing cell is byte-identical in all four
# notebooks and the patch cell differs only for exp31, so this is four GPU runs plus CPU-only re-runs of the
# post-processing. The MOTION_RELINK_TIGHT_UM grid is there because exp29 was SUBMITTED with the in-kernel
# sweep's pick (5.5) while exp30/31/32 ran with the sweep off (6.0) - reporting both removes that confound.
#
# Usage: run_calibration.sh [--stems "a b c"] [--tag-suffix _4vid]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${BIOHUB_PYTHON:-$HOME/anaconda3/envs/biohub/bin/python}"
NB29="$ROOT/experiments/exp29_sjlee947_verbatim/exp29-sjlee947-verbatim.ipynb"
NB31="$ROOT/experiments/exp31_sjlee947_ft03B_zflip/exp31-sjlee947-ft03B-zflip.ipynb"

STEMS=""
SUFFIX=""
while [ $# -gt 0 ]; do
  case "$1" in
    --stems) STEMS="$2"; shift 2 ;;
    --tag-suffix) SUFFIX="$2"; shift 2 ;;
    *) echo "unknown arg $1" >&2; exit 2 ;;
  esac
done

if [ -n "$STEMS" ]; then
  # shellcheck disable=SC2206
  SEL=(--stems $STEMS)
else
  SEL=(--split "$ROOT/experiments/_lib/loeo_train6bba_val44b6.json" --key holdout)
fi

run() {           # run <tag> <with-tight55: yes|no> <notebook> [extra weight-override args...]
  local tag="$1$SUFFIX"; shift
  local tight="$1"; shift
  local nb="$1"; shift
  echo "################ $tag (GPU + post-processing at the base tight 6.0)"
  "$PY" "$ROOT/tools/public_local.py" --notebook "$nb" --tag "$tag" --label base "${SEL[@]}" "$@"
  if [ "$tight" = "yes" ]; then
    echo "################ $tag (post-processing only, tight 5.5 = the setting exp29 was submitted with)"
    "$PY" "$ROOT/tools/public_local.py" --notebook "$nb" --tag "$tag" --label tight55 --stage pp "${SEL[@]}" "$@" \
        --env BIOHUB_MOTION_RELINK_TIGHT_UM=5.5
  fi
}

# Only exp29 needs the tight-5.5 re-run: it is the one that was SUBMITTED with the in-kernel sweep's pick,
# so it is the only one where "as submitted" differs from "base". Measured on the 4-video set, 5.5 and 6.0
# score identically to four decimals, so re-running it for the other three would buy nothing.
run exp29 yes "$NB29"
run exp30 no  "$NB29" --primary exp03B
run exp31 no  "$NB31" --primary exp03B
run exp32 no  "$NB29" --primary exp03B --secondary exp23

echo "################ summary"
"$PY" "$ROOT/experiments/local_friend_b_exp02_public_port/summarise.py" --suffix "$SUFFIX"
