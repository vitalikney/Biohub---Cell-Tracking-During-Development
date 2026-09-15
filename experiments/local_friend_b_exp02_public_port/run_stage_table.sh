#!/usr/bin/env bash
# The stage table the Friend B start kit asked for: raw ILP / +relink / +gap / +divisions / +veto /
# +short-track filter, scored with the official metric.
#
# Built as a CUMULATIVE ablation driven only by the notebook's own BIOHUB_* switches, so every row runs the
# same post-processing code with one more stage enabled. It reuses the cached raw graphs, so the whole table
# is CPU-only and costs no GPU time.
#
# Usage: run_stage_table.sh [tag]        (default tag: exp29)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${BIOHUB_PYTHON:-$HOME/anaconda3/envs/biohub/bin/python}"
TAG="${1:-exp29}"
CACHE="$ROOT/.public_local_cache/$TAG"

# Everything off. Later rows switch pieces back on one at a time, in the order filter_output_graph runs them.
OFF=(
  BIOHUB_OUTPUT_MOTION_RELINK=0
  BIOHUB_OUTPUT_GAP_CLOSE=0
  BIOHUB_OUTPUT_GAP2_RECOVERY=0
  BIOHUB_OUTPUT_SAFE_DIVISIONS=0
  BIOHUB_USE_DEEPCENTER_VETO=0
  BIOHUB_REQUIRE_DEEPCENTER_VETO=0
  BIOHUB_OUTPUT_FILTER_SHORT_TRACKS=0
  BIOHUB_OUTPUT_LINEFIT_SMOOTH=0
)

stage() {                 # stage <label> <env overrides...>
  local label="$1"; shift
  echo "######## $label"
  "$PY" "$ROOT/tools/public_local.py" --tag "$TAG" --label "$label" --stage pp \
      --stems $(ls "$CACHE/raw" | sed 's/\.geff$//' | tr '\n' ' ') --env "$@"
}

echo "######## raw (ILP graphs straight from inference, no post-processing at all)"
"$PY" "$ROOT/tools/score_geffs.py" "$CACHE/raw" | tail -1

stage edgefilter   "${OFF[@]}"
stage relink       "${OFF[@]}" BIOHUB_OUTPUT_MOTION_RELINK=1
stage gap          "${OFF[@]}" BIOHUB_OUTPUT_MOTION_RELINK=1 BIOHUB_OUTPUT_GAP_CLOSE=1 BIOHUB_OUTPUT_GAP2_RECOVERY=1
stage divisions    "${OFF[@]}" BIOHUB_OUTPUT_MOTION_RELINK=1 BIOHUB_OUTPUT_GAP_CLOSE=1 BIOHUB_OUTPUT_GAP2_RECOVERY=1 \
                               BIOHUB_OUTPUT_SAFE_DIVISIONS=1
stage veto         "${OFF[@]}" BIOHUB_OUTPUT_MOTION_RELINK=1 BIOHUB_OUTPUT_GAP_CLOSE=1 BIOHUB_OUTPUT_GAP2_RECOVERY=1 \
                               BIOHUB_OUTPUT_SAFE_DIVISIONS=1 BIOHUB_USE_DEEPCENTER_VETO=1 BIOHUB_REQUIRE_DEEPCENTER_VETO=1
stage shorttrack   "${OFF[@]}" BIOHUB_OUTPUT_MOTION_RELINK=1 BIOHUB_OUTPUT_GAP_CLOSE=1 BIOHUB_OUTPUT_GAP2_RECOVERY=1 \
                               BIOHUB_OUTPUT_SAFE_DIVISIONS=1 BIOHUB_USE_DEEPCENTER_VETO=1 BIOHUB_REQUIRE_DEEPCENTER_VETO=1 \
                               BIOHUB_OUTPUT_FILTER_SHORT_TRACKS=1
echo "######## full (= the shipped configuration, linefit smoothing on)"
echo "   see the 'base' run of this tag"

echo "######## stage table"
"$PY" - "$CACHE" <<'EOF'
import json, sys
from pathlib import Path
cache = Path(sys.argv[1])
order = [("edgefilter", "edge filter only (t->t+1, <=14um)"),
         ("relink", "+ motion relink"),
         ("gap", "+ gap closing (1 frame + gap2)"),
         ("divisions", "+ safe divisions"),
         ("veto", "+ DeepCenter veto"),
         ("shorttrack", "+ short-track filter"),
         ("base", "+ linefit smoothing (= shipped)")]
print(f"{'stage':40s} {'score':>8s} {'delta':>8s} {'edge':>8s} {'nodes':>9s} {'div TP/FP/FN':>13s}")
prev = None
for label, name in order:
    p = cache / "pp" / f"{label}.json"
    if not p.is_file():
        continue
    d = json.loads(p.read_text())
    s = d["summary"]
    nodes = sum(v["nodes"] for v in d["per_video"])
    delta = "" if prev is None else f"{s['score'] - prev:+8.4f}"
    print(f"{name:40s} {s['score']:8.4f} {delta:>8s} {s['edge_jaccard']:8.4f} {nodes:9d} "
          f"{int(s['division_tp']):3d}/{int(s['division_fp']):3d}/{int(s['division_fn']):3d}")
    prev = s["score"]
EOF
