"""UP test for a W1 read. python uptest.py save <tag>  |  python uptest.py compare <tagS0> <tagS1>
save: downloads the public LB (read-only CLI) into _lb/<tag>/ and prints our row (rank, score, SubmissionCount).
compare: TeamIds above us in S0 that are below us in S1 (public bests never fall, so any such team = our best rose)."""
import csv
import glob
import io
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(r"C:\Users\vital\Documents\kAGGLE\Biohub - Cell Tracking During Development")
OUT = REPO / "experiments" / "lb_poll" / "_lb"
TEAM = "16810638"


def load(tag):
    d = OUT / tag
    z = sorted(glob.glob(str(d / "*.zip")))
    if z:
        with zipfile.ZipFile(z[-1]) as zf:
            name = [n for n in zf.namelist() if n.endswith(".csv")][0]
            text = zf.read(name).decode("utf-8-sig")
    else:
        text = Path(sorted(glob.glob(str(d / "*.csv")))[-1]).read_text(encoding="utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text)))
    ranks = {r["TeamId"]: int(r["Rank"]) for r in rows}
    ours = next(r for r in rows if r["TeamId"] == TEAM)
    return rows, ranks, ours


def save(tag):
    d = OUT / tag
    d.mkdir(parents=True, exist_ok=True)
    p = subprocess.run([sys.executable, "-m", "kaggle", "competitions", "leaderboard",
                        "biohub-cell-tracking-during-development", "-d", "-p", str(d)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(p.stdout.strip()[-200:], p.stderr.strip()[-200:])
    rows, ranks, ours = load(tag)
    better = sum(1 for r in rows if float(r["Score"]) > float(ours["Score"]))
    same = [r for r in rows if r["Score"] == ours["Score"]]
    pos = [r["TeamId"] for r in same].index(TEAM) + 1
    print(f"{tag}: rank {ours['Rank']} score {ours['Score']} SubmissionCount {ours['SubmissionCount']} last {ours['LastSubmissionDate']}"
          f" | strictly better {better} | position {pos} of {len(same)} in the {ours['Score']} block | teams {len(rows)}")


def compare(t0, t1):
    rows0, ranks0, o0 = load(t0)
    rows1, ranks1, o1 = load(t1)
    r0, r1 = int(o0["Rank"]), int(o1["Rank"])
    above0 = [t for t, r in ranks0.items() if r < r0]
    passed = [t for t in above0 if ranks1.get(t, 0) > r1]
    print(f"S0 {t0}: rank {r0} score {o0['Score']} count {o0['SubmissionCount']} | S1 {t1}: rank {r1} score {o1['Score']} "
          f"count {o1['SubmissionCount']} | TeamIds passed {len(passed)} -> {'UP' if passed else 'no UP'}")


if __name__ == "__main__":
    {"save": lambda: save(sys.argv[2]), "compare": lambda: compare(sys.argv[2], sys.argv[3])}[sys.argv[1]]()
