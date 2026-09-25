"""Dummy gates of the pre-registered plan v3 (research/wf_ideas_v3/FINAL_REPORT.md §e "Ворота дамми", with the K2
correction recorded in CONTEXT.md on 25 Sep 14:29 UTC). Reads downloaded kernel outputs (submission.csv, run_stats.csv,
*.log) and prints PASS/FAIL per gate.

    python tools/dummy_gates.py --ref56 _dl/biohub-exp56-x138-verbatim --ref57b _dl/biohub-exp57b-x138-divins-only \
        --k2 _dl/<K2> --k1 _dl/<K1> [--fd _dl/<FD>] [--ff _dl/<FF>] [--insertion 1]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def log_lines(d: Path) -> list[str]:
    logs = sorted(d.glob("*.log"))
    if not logs:
        return []
    out = []
    for r in json.loads(logs[0].read_text(encoding="utf-8")):
        out.extend(r.get("data", "").splitlines())
    return out


def stats(d: Path) -> dict[str, dict]:
    return {r["dataset"]: r for r in csv.DictReader((d / "run_stats.csv").open(encoding="utf-8"))}


def validate_csv(p: Path) -> tuple[bool, str, dict]:
    nodes, edges = {}, []
    for r in csv.DictReader(p.open(encoding="utf-8")):
        if r["row_type"] == "node":
            nodes[(r["dataset"], int(r["node_id"]))] = int(r["t"])
        else:
            edges.append((r["dataset"], int(r["source_id"]), int(r["target_id"])))
    indeg, outdeg = Counter(), Counter()
    for ds, s, t in edges:
        if (ds, s) not in nodes or (ds, t) not in nodes:
            return False, f"dangling edge {ds} {s}->{t}", {}
        if nodes[(ds, t)] - nodes[(ds, s)] != 1:
            return False, f"edge dt != 1 {ds} {s}->{t}", {}
        outdeg[(ds, s)] += 1
        indeg[(ds, t)] += 1
    if indeg and max(indeg.values()) > 1:
        return False, "in-degree > 1", {}
    if outdeg and max(outdeg.values()) > 2:
        return False, "out-degree > 2", {}
    per = Counter(ds for ds, _ in nodes)
    forks = Counter(ds for (ds, _), k in outdeg.items() if k == 2)
    return True, "ok", {"nodes": dict(per), "edges": len(edges), "forks": dict(forks)}


def has(lines: list[str], pat: str) -> list[str]:
    return [l for l in lines if pat in l]


def gate(name: str, ok: bool, detail: str, results: list) -> None:
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref56", required=True)
    ap.add_argument("--ref57b", required=True)
    ap.add_argument("--k2")
    ap.add_argument("--k1")
    ap.add_argument("--fd")
    ap.add_argument("--ff")
    ap.add_argument("--insertion", type=int, default=1, help="1 = branch with the DaughterNet insertion")
    a = ap.parse_args()
    ref56, ref57b = Path(a.ref56), Path(a.ref57b)
    R: list = []
    lowdet56 = {m.group(1): int(m.group(2)) for l in log_lines(ref56)
                for m in [re.search(r"LOWDET (\S+): (\d+) peaks", l)] if m}
    st56 = stats(ref56)

    if a.k1:
        k1 = Path(a.k1)
        ref = ref57b if a.insertion else ref56
        gate("K1 sha256 == " + ref.name, sha(k1 / "submission.csv") == sha(ref / "submission.csv"),
             sha(k1 / "submission.csv")[:16], R)
        L = log_lines(k1)
        bad = [p for p in ("DEADLINE:", "DIVINS FAILED", "REPAIR FAILED") if has(L, p)]
        gate("K1 log clean", not bad, f"found {bad}" if bad else "no DEADLINE / DIVINS FAILED / REPAIR FAILED", R)

    if a.k2:
        k2 = Path(a.k2)
        L = log_lines(k2)
        ok, why, info = validate_csv(k2 / "submission.csv")
        gate("K2 CSV valid", ok, f"{why} {info.get('edges', '')} edges", R)
        gate("K2 'Low-detection dump applied'", bool(has(L, "Low-detection dump applied")), "", R)
        lowdet = {m.group(1): int(m.group(2)) for l in L for m in [re.search(r"LOWDET (\S+): (\d+) peaks", l)] if m}
        gate("K2 LOWDET N == exp56", lowdet == lowdet56, f"{lowdet} vs {lowdet56}", R)
        lr = {m.group(1): (int(m.group(2)), int(m.group(3)), int(m.group(4))) for l in L
              for m in [re.search(r"LOWREFINE (\S+): refined (\d+) of (\d+) .*failed frames (\d+)", l)] if m}
        lr_ok = bool(lr) and all(n == lowdet.get(c) and r > 0 and f == 0 for c, (r, n, f) in lr.items())
        gate("K2 LOWREFINE refined R of N, N == LOWDET, R > 0, 0 failed", lr_ok, str(lr), R)
        hard = [p for p in ("LOW-DETECTION DUMP SKIPPED", "gap filler idle", "invalid V1284 displacement",
                            "REPAIR FAILED", "LOWREFINE FAILED", "DIVINS FAILED", "DEADLINE:") if has(L, p)]
        gate("K2 no hard-fail lines", not hard, f"found {hard}" if hard else "none", R)
        st = stats(k2)
        raw = sum(int(v["raw_nodes"]) for v in st.values())
        gate("K2 raw nodes == 121,777", raw == 121777, str(raw), R)
        for col in ("readmitted_nodes", "gapfill_added_nodes"):
            v2 = sum(int(v.get(col) or 0) for v in st.values())
            v6 = sum(int(v.get(col) or 0) for v in st56.values())
            gate(f"K2 {col} within +-10% of exp56", v6 > 0 and abs(v2 - v6) <= 0.10 * v6, f"{v2} vs {v6}", R)
        if a.k1:
            s1 = stats(Path(a.k1))
            dev = {ds: (int(st[ds]["nodes"]) - int(s1[ds]["nodes"])) / int(s1[ds]["nodes"]) for ds in st}
            gate("K2 final nodes within +-0.3% of K1 per clip", all(abs(x) <= 0.003 for x in dev.values()),
                 {k: f"{v:+.4%}" for k, v in dev.items()}.__repr__(), R)

    if a.fd:
        fd = Path(a.fd)
        L = log_lines(fd)
        ok, why, _ = validate_csv(fd / "submission.csv")
        gate("FD CSV valid", ok, why, R)
        gate("FD 'DEADLINE:' present", bool(has(L, "DEADLINE:")), has(L, "DEADLINE:")[:1].__repr__(), R)
        if a.insertion:
            skipped = has(L, "DIVINS SKIPPED (deadline)")
            gate("FD insertion skipped by deadline", bool(skipped), f"{len(skipped)} lines", R)
        st = stats(fd)
        sd = sum(int(v.get("safe_divisions_added") or 0) for v in st.values())
        lf = sum(int(v.get("linefit_smoothed_nodes") or 0) for v in st.values())
        gate("FD safe divisions and linefit kept (counters > 0)", sd > 0 and lf > 0, f"safe_div={sd} linefit={lf}", R)
        gate("FD no REPAIR FAILED", not has(L, "REPAIR FAILED"), "", R)

    if a.ff:
        ff = Path(a.ff)
        L = log_lines(ff)
        n_fail = len(has(L, "DIVINS FAILED"))
        gate("FF 'DIVINS FAILED' on every clip", n_fail >= len(lowdet56), f"{n_fail} lines", R)
        gate("FF sha256 == exp56", sha(ff / "submission.csv") == sha(ref56 / "submission.csv"),
             sha(ff / "submission.csv")[:16], R)

    n_fail = sum(1 for _, ok, _ in R if not ok)
    print(f"\n{len(R) - n_fail}/{len(R)} gates PASS" + ("" if not n_fail else f"; {n_fail} FAIL"))


if __name__ == "__main__":
    main()
