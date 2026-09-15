#!/usr/bin/env bash
# Wait for the 12 LOEO 44b6 videos to finish downloading, verify they are complete, then run the full
# calibration and print the verdict. Written as one script so the work proceeds unattended while Kaggle's
# rate limit expires.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${BIOHUB_PYTHON:-$HOME/anaconda3/envs/biohub/bin/python}"
HERE="$ROOT/experiments/local_friend_b_exp02_public_port"
FETCH_PID_FILE="${1:-/tmp/claude-1000/fetch.pid}"

cd "$ROOT"

echo "=== waiting for the download to finish ($(date '+%H:%M'))"
if [ -f "$FETCH_PID_FILE" ]; then
  pid="$(cat "$FETCH_PID_FILE")"
  while kill -0 "$pid" 2>/dev/null; do sleep 60; done
fi

echo "=== verifying the 12 videos are complete ($(date '+%H:%M'))"
if ! "$PY" - <<'EOF'
import json, sys
from pathlib import Path
root = Path('biohub-cell-tracking-during-development')
idx = {f['name']: f['size'] for f in json.loads((root / '_file_index.json').read_text())}
stems = json.loads(Path('experiments/_lib/loeo_train6bba_val44b6.json').read_text())['holdout']
bad = []
for s in stems:
    want = [n for n in idx if n.startswith(f'train/{s}.')]
    ok = sum(1 for n in want if (root / n).is_file() and (root / n).stat().st_size == idx[n])
    print(f'{s} {ok:3d}/{len(want)}')
    if ok != len(want):
        bad.append(s)
if bad:
    print('INCOMPLETE:', bad)
    sys.exit(1)
print('all 12 videos complete')
EOF
then
  echo "=== data incomplete; re-running the fetcher once more"
  "$PY" tools/kaggle_fetch_videos.py --split experiments/_lib/loeo_train6bba_val44b6.json --key holdout --workers 4 || true
fi

echo "=== calibration on all 12 videos ($(date '+%H:%M'))"
bash "$HERE/run_calibration.sh"

echo "=== verdict ($(date '+%H:%M'))"
mkdir -p "$HERE/results"
"$PY" "$HERE/rescore.py"
"$PY" "$HERE/summarise.py" | tee "$HERE/results/calibration_12videos.txt"
echo "=== finished ($(date '+%H:%M'))"
