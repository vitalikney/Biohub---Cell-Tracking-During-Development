"""Push kernel folders one after another, retrying while Kaggle refuses with the 2-GPU-session limit.

    python experiments/coordhead_retrain/push_queue.py DIR [DIR ...] [--wait 120] [--max-hours 14]

Each DIR holds a kernel-metadata.json. A push that fails with "Maximum batch GPU session count" is retried every
--wait seconds; any other error stops the queue. A pushed kernel is recorded in push_queue.log (UTC time, id) next to
this script. Chaining 4 capture shards = one call with the 4 folders: the first two start at once (if sessions are
free), the others start as soon as a session frees up.
"""
import argparse
import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "push_queue.log"


def log(msg: str) -> None:
    line = f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M:%S} UTC  {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--wait", type=int, default=120)
    ap.add_argument("--max-hours", type=float, default=14.0)
    ap.add_argument("--force", action="store_true", help="push even if the kernel already has a run")
    a = ap.parse_args()
    deadline = time.time() + a.max_hours * 3600
    for d in a.dirs:
        kid = json.loads((Path(d) / "kernel-metadata.json").read_text())["id"]
        if not a.force:
            st = subprocess.run([sys.executable, "-m", "kaggle", "kernels", "status", kid], capture_output=True,
                                text=True, timeout=120)
            if any(s in (st.stdout + st.stderr) for s in ("RUNNING", "QUEUED", "COMPLETE")):
                # a second queue (e.g. after a session restart) must not push a new version: Kaggle keeps the old
                # version running, the GPU hour is spent twice (happened once for chcap-6bba-s2of4)
                log(f"SKIP {kid}: already pushed ({(st.stdout + st.stderr).strip().splitlines()[-1]}); --force to re-push")
                continue
        while True:
            r = subprocess.run([sys.executable, "-m", "kaggle", "kernels", "push", "-p", d],
                               capture_output=True, text=True, timeout=600)
            out = (r.stdout + r.stderr).strip()
            if "Maximum batch GPU session count" in out:
                if time.time() > deadline:
                    log(f"GIVE UP {kid}: session limit until --max-hours")
                    sys.exit(2)
                time.sleep(a.wait)
                continue
            if r.returncode == 0 and "successfully pushed" in out.lower():
                log(f"PUSHED {kid}: {out.splitlines()[-1]}")
                break
            log(f"ERROR {kid}: rc={r.returncode} {out[-500:]}")
            sys.exit(1)
        time.sleep(20)  # let the session register before the next push


if __name__ == "__main__":
    main()
