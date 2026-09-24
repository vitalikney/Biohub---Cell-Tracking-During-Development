"""Status + download of the capture kernels' outputs into experiments/coordhead_retrain/captures/<name>/.

    python experiments/coordhead_retrain/fetch_captures.py pilot s0of4 s1of4 s2of4 s3of4 [--wait]

For each name: kernel vitaliineibauer/biohub-chcap-<name>; if COMPLETE and not yet downloaded, downloads the capture
files (npz, manifests, summary) and the log, then prints the capture summary line. --wait polls every 2 min until all
named kernels are COMPLETE or ERROR.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def status(kid: str) -> str:
    r = subprocess.run([sys.executable, "-m", "kaggle", "kernels", "status", kid], capture_output=True, text=True,
                       timeout=120)
    out = (r.stdout + r.stderr).strip().splitlines()
    return out[-1] if out else "?"


def fetch(name: str) -> bool:
    kid = f"vitaliineibauer/biohub-chcap-{name}"
    st = status(kid)
    dest = HERE / "captures" / name
    done_flag = dest / ".downloaded"
    if done_flag.exists():
        print(f"{name}: already downloaded ({dest})")
        return True
    print(f"{name}: {st}")
    if "COMPLETE" not in st:
        return "ERROR" in st or "CANCEL" in st
    dest.mkdir(parents=True, exist_ok=True)
    for attempt in range(4):
        # the kernel deletes its repo / weights copies at the end, so the whole output is the capture + small logs
        r = subprocess.run([sys.executable, "-m", "kaggle", "kernels", "output", kid, "-p", str(dest), "-o", "-q"],
                           capture_output=True, text=True, timeout=1800)
        if r.returncode == 0:
            break
        print(f"  download retry {attempt + 1}: {(r.stdout + r.stderr)[-300:]}")
        time.sleep(30)
    summaries = sorted(dest.rglob("capture_summary_*.json"))
    npz = sorted(dest.rglob("*.npz"))
    if not summaries:
        print(f"  no capture summary in {dest} (files: {len(list(dest.rglob('*')))})")
        return False
    s = json.loads(summaries[0].read_text())
    print(f"  {len(npz)} npz, {sum(p.stat().st_size for p in npz) / 1e6:.1f} MB; video_seconds_mean "
          f"{s['video_seconds_mean']} s, predict wall {s['predict_wall_seconds']} s, setup {s.get('setup_seconds_before_predict')} s,"
          f" missing {s['missing']}")
    done_flag.write_text(json.dumps({"kernel": kid, "status": st, "npz": len(npz)}))
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="+")
    ap.add_argument("--wait", action="store_true")
    a = ap.parse_args()
    pending = list(a.names)
    while pending:
        pending = [n for n in pending if not fetch(n)]
        if not a.wait or not pending:
            break
        time.sleep(120)


if __name__ == "__main__":
    main()
