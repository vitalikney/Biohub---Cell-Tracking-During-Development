"""Swap anatomy of the FINAL exp39 (+ edge filter) graph: local re-assignment moves, their prediction-side evidence and
their exact effect on the official edge counts.

WHY
    fn_anatomy.py: after the edge filter 1528 FN are swaps (p_u linked to y, p_v linked from x, the GT link p_u -> p_v
    never proposed by the linker; median length 9.3 um, i.e. fast-moving cells linked to a closer neighbour) and ~1150
    are single diversions (u_diverted / v_taken). This script enumerates the local moves that would fix them, without
    GT, and labels each move under the fixed official matching (moves never add or remove nodes, so the matching and
    the edge TP / FP / FN deltas are exact; the division term is not).

MOVES (between frames t and t+1, only "simple" edges: source out-degree 1, target in-degree 1)
    swap      edges a->b and c->d (a, c within --src-um of each other) become a->d and c->b
    repoint   edge a->b becomes a->d where d is a track START at t+1 (b becomes a start), or edge c->d becomes a->d
              where a is a track END at t (c becomes an end)
FEATURES (float coordinates after linefit, um)
    len_*       edge lengths; p_* current edge probabilities (0 = unscored relink pair, >0 = the linker's own edge,
                nan = gap / safe-division edge)
    acc_cur / acc_new   sum of second differences |x_{t+1} - 2 x_t + x_{t-1}| at every node whose neighbourhood the move
                changes (only terms computable before AND after the move; n_acc = how many)
    dist_cur / dist_new sum of edge lengths before / after
LABELS
    d_tp, d_fp  change of official edge TP / FP of the move (removed edges: the metric's own labels; added edges:
                anatomy._label_pair under the same matching)

USAGE
    python experiments/l2_daughternet/edge_anatomy/swap_anatomy.py --split selection --workers 2 --ef alt=3,relink=1,prune=1
    python experiments/l2_daughternet/edge_anatomy/swap_anatomy.py --eval --split all --workers 2 --ef ...  (kernel fn)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import anatomy as A  # noqa: E402
import fn_anatomy as F  # noqa: E402

R = A.R
DEFAULT_OUT = F.DEFAULT_OUT
SWAP_RULES: dict[str, dict] = {}  # --eval: pass a JSON {name: sw params} with --rules


def _graph(stem: str, settings: dict):
    A.init_worker(settings["anatomy"])
    cache, tail_dir = Path(settings["cache"]), Path(settings["tail_dir"])
    ns = A._W["ns"]
    nodes, edges, _ = R.load_tail(tail_dir / f"{stem}.npz")
    ilp_probs = R.load_ilp_probs(cache, stem)
    if settings["ef"]:
        nodes, edges = ns["edgefilter_final_graph"](nodes, [dict(e) for e in edges], {}, dict(settings["ef"]),
                                                    dict(ilp_probs))
        match_out = Path(settings["out"])
    else:
        match_out = Path(settings["anatomy"]["out"])
    mt = A.official_match(stem, nodes, edges, match_out, settings["match_key"])
    match = {int(i): int(m) for i, m in zip(mt["n_id"].tolist(), mt["n_match"].tolist())}
    gt_edges = set(zip(mt["gt_src"].tolist(), mt["gt_dst"].tolist()))
    gt_out: dict[int, int] = {}
    gt_in: dict[int, int] = {}
    for a, b in gt_edges:
        gt_out[a] = gt_out.get(a, 0) + 1
        gt_in[b] = gt_in.get(b, 0) + 1
    lab = {(int(s), int(d)): (1 if tp else (2 if v else 0)) for s, d, tp, v in
           zip(mt["e_src"].tolist(), mt["e_dst"].tolist(), mt["e_tp"].tolist(), mt["e_valid"].tolist())}

    def label(s: int, d: int, existing: bool) -> int:
        if existing:
            return lab.get((s, d), 0)
        return A._label_pair(s, d, match, gt_edges, gt_out, gt_in)

    return nodes, edges, ilp_probs, json.loads(str(mt["row"])), label


def moves_video(stem: str, settings: dict) -> dict:
    started = time.time()
    nodes, edges, _ilp, row, label = _graph(stem, settings)
    scale = np.asarray([1.625, 0.40625, 0.40625])
    pos = {i: np.asarray([n["z"], n["y"], n["x"]], dtype=np.float64) * scale for i, n in nodes.items()}
    tt = {i: int(n["t"]) for i, n in nodes.items()}
    succ: dict[int, list[int]] = {}
    pred: dict[int, list[int]] = {}
    prob: dict[tuple[int, int], float] = {}
    for e in edges:
        s, d = int(e["source_id"]), int(e["target_id"])
        succ.setdefault(s, []).append(d)
        pred.setdefault(d, []).append(s)
        prob[(s, d)] = np.nan if e.get("edge_prob") is None else float(e["edge_prob"])
    t_max = max(tt.values())

    def only(lst):
        return lst[0] if lst and len(lst) == 1 else None

    def acc(p0, p1, p2) -> float:
        return float(np.linalg.norm(pos[p2] - 2 * pos[p1] + pos[p0]))

    simple = [(a, b) for a, bs in succ.items() if len(bs) == 1 for b in bs
              if len(pred.get(b, [])) == 1 and tt[b] == tt[a] + 1]
    by_t: dict[int, list[tuple[int, int]]] = {}
    for a, b in simple:
        by_t.setdefault(tt[a], []).append((a, b))
    from scipy.spatial import cKDTree

    rows = []
    src_um, max_len = float(settings["src_um"]), float(settings["max_len_um"])
    ends_by_t: dict[int, list[int]] = {}
    starts_by_t: dict[int, list[int]] = {}
    for i in nodes:
        if not succ.get(i) and tt[i] < t_max:
            ends_by_t.setdefault(tt[i], []).append(i)
        if not pred.get(i) and tt[i] > 0:
            starts_by_t.setdefault(tt[i], []).append(i)

    for t, es in by_t.items():
        if len(es) < 1:
            continue
        srcs = np.stack([pos[a] for a, _ in es])
        tree = cKDTree(srcs)
        # ---- 2x2 swaps
        for i, j in tree.query_pairs(src_um):
            (a, b), (c, d) = es[i], es[j]
            l_ad = float(np.linalg.norm(pos[d] - pos[a]))
            l_cb = float(np.linalg.norm(pos[b] - pos[c]))
            if l_ad > max_len or l_cb > max_len:
                continue
            pa, pc = only(pred.get(a, [])), only(pred.get(c, []))
            sb, sd = only(succ.get(b, [])), only(succ.get(d, []))
            # comparable acceleration terms: only those computable both before and after
            cur, new = [], []
            if pa is not None:
                cur.append(acc(pa, a, b)); new.append(acc(pa, a, d))
            if pc is not None:
                cur.append(acc(pc, c, d)); new.append(acc(pc, c, b))
            if sb is not None:
                cur.append(acc(a, b, sb)); new.append(acc(c, b, sb))
            if sd is not None:
                cur.append(acc(c, d, sd)); new.append(acc(a, d, sd))
            l_ab = float(np.linalg.norm(pos[b] - pos[a]))
            l_cd = float(np.linalg.norm(pos[d] - pos[c]))
            acc_cur, acc_new = float(sum(cur)), float(sum(new))
            if acc_new >= acc_cur:  # keep only moves the motion model prefers (design table stays small)
                continue
            rem = [label(a, b, True), label(c, d, True)]
            add = [label(a, d, False), label(c, b, False)]
            rows.append({"stem": stem, "kind": "swap", "t": t, "a": a, "b": b, "c": c, "d": d,
                         "p1": prob[(a, b)], "p2": prob[(c, d)], "len1": l_ab, "len2": l_cd, "len_new1": l_ad,
                         "len_new2": l_cb, "acc_cur": acc_cur, "acc_new": acc_new, "n_acc": len(cur),
                         "dist_cur": l_ab + l_cd, "dist_new": l_ad + l_cb,
                         "d_tp": add.count(1) - rem.count(1), "d_fp": add.count(2) - rem.count(2),
                         "rem_tp": rem.count(1), "rem_fp": rem.count(2), "add_tp": add.count(1),
                         "add_fp": add.count(2)})
        # ---- repoints to a free start (a->b => a->d) / from a free end (c->d => a->d)
        if settings["repoint"]:
            st = starts_by_t.get(t + 1, [])
            if st:
                stree = cKDTree(np.stack([pos[d] for d in st]))
                for (a, b) in es:
                    pa, sb = only(pred.get(a, [])), only(succ.get(b, []))
                    if pa is None:
                        continue
                    for k in stree.query_ball_point(pos[a], max_len):
                        d = st[k]
                        sd = only(succ.get(d, []))
                        if sd is None:
                            continue
                        cur = acc(pa, a, b) + (acc(a, b, sb) if sb is not None else 0.0)
                        new = acc(pa, a, d) + acc(a, d, sd)
                        n_terms = 1 + (sb is not None)
                        if n_terms == 2 and new >= cur:
                            continue
                        rem, add = label(a, b, True), label(a, d, False)
                        rows.append({"stem": stem, "kind": "repoint_fwd", "t": t, "a": a, "b": b, "c": -1, "d": d,
                                     "p1": prob[(a, b)], "p2": np.nan,
                                     "len1": float(np.linalg.norm(pos[b] - pos[a])), "len2": np.nan,
                                     "len_new1": float(np.linalg.norm(pos[d] - pos[a])), "len_new2": np.nan,
                                     "acc_cur": cur, "acc_new": new, "n_acc": n_terms,
                                     "dist_cur": np.nan, "dist_new": np.nan,
                                     "d_tp": int(add == 1) - int(rem == 1), "d_fp": int(add == 2) - int(rem == 2),
                                     "rem_tp": int(rem == 1), "rem_fp": int(rem == 2), "add_tp": int(add == 1),
                                     "add_fp": int(add == 2)})
    return {"stem": stem, "rows": rows, "row": row, "seconds": round(time.time() - started, 2)}


def _task(stem: str, settings: dict) -> dict:
    for attempt in range(4):
        try:
            if settings.get("eval"):
                return eval_video(stem, settings)
            return moves_video(stem, settings)
        except PermissionError:
            if attempt == 3:
                raise
            time.sleep(2.0 * (attempt + 1))


def eval_video(stem: str, settings: dict) -> dict:
    """Run the kernel function (bpk.SWAPFIX_FN via the replay namespace) with every rule; exact edge deltas."""
    nodes, edges, ilp, row, label = _graph(stem, settings)
    ns = A._W["ns"]
    old = {(int(e["source_id"]), int(e["target_id"])) for e in edges}
    out = {}
    for name, params in settings["rules"].items():
        st: dict = {}
        _n, new_edges = ns["swapfix_final_graph"](nodes, [dict(e) for e in edges], st, dict(params), dict(ilp))
        new = {(int(e["source_id"]), int(e["target_id"])) for e in new_edges}
        removed, added = old - new, new - old
        rl = [label(s, d, True) for s, d in removed]
        al = [label(s, d, False) for s, d in added]
        out[name] = {"tp_add": al.count(1), "fp_add": al.count(2), "tp_drop": rl.count(1), "fp_drop": rl.count(2),
                     "moves": int(st.get("swapfix_swaps", 0)) + int(st.get("swapfix_repoints", 0))}
    return {"stem": stem, "eval": out, "row": row}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache", default=str(A.DEFAULT_CACHE))
    ap.add_argument("--replay-out", default=str(A.DEFAULT_REPLAY_OUT))
    ap.add_argument("--anatomy-out", default=str(A.DEFAULT_OUT))
    ap.add_argument("--config", default="exp39")
    ap.add_argument("--ef", default="")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--split", default="selection", choices=["selection", "confirmation", "all"])
    ap.add_argument("--splits", default=str(R.DEFAULT_SPLITS))
    ap.add_argument("--data-dir", default=str(R.pl.DEFAULT_DATA))
    ap.add_argument("--src-um", type=float, default=10.0)
    ap.add_argument("--max-len-um", type=float, default=14.0)
    ap.add_argument("--repoint", type=int, default=1)
    ap.add_argument("--eval", action="store_true", help="evaluate the kernel function with the rules in --rules")
    ap.add_argument("--rules", default="", help="JSON file {name: params} for --eval")
    ap.add_argument("--tag", default="")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    if a.workers > 2:
        raise SystemExit("at most 2 workers (the laptop is in use)")
    import pandas as pd

    cache, out, replay_out = Path(a.cache).resolve(), Path(a.out).resolve(), Path(a.replay_out).resolve()
    tail_dir, _cfg = A.tail_dir_for(a.config, replay_out)
    ef, match_key = {}, tail_dir.name
    if a.ef:
        raw = {k.strip(): R._parse_value(v) for k, _, v in (item.partition("=") for item in a.ef.split(","))}
        ef = R.edgefilter_params("swap_anatomy", raw)
        match_key = f"{tail_dir.name}__ef_{R._fingerprint({'ef': ef, 'sha': R._edgefilter_sha()})[:10]}"
    splits = json.loads(Path(a.splits).read_text(encoding="utf-8"))
    all_stems = sorted(p.stem for p in (cache / "ckpt").glob("*.npz"))
    stems = all_stems if a.split == "all" else sorted(splits[a.split])
    anatomy_settings = {"cache": str(cache), "out": str(Path(a.anatomy_out).resolve()), "tail_dir": str(tail_dir),
                        "data_dir": str(Path(a.data_dir)), "ns_out": str(Path(a.anatomy_out).resolve() / "ns")}
    rules = json.loads(Path(a.rules).read_text(encoding="utf-8")) if a.rules else SWAP_RULES
    settings = {"cache": str(cache), "out": str(out), "tail_dir": str(tail_dir), "ef": ef, "match_key": match_key,
                "anatomy": anatomy_settings, "src_um": a.src_um, "max_len_um": a.max_len_um, "repoint": a.repoint,
                "eval": a.eval, "rules": rules}
    tag = a.tag or (("exp39_ef" if ef else "exp39") + f"_{a.split}")
    print(f"{len(stems)} videos ({a.split}), ef {ef or 'off'}, {'eval' if a.eval else 'moves'}", flush=True)
    results: dict[str, dict] = {}
    started = time.time()
    with ProcessPoolExecutor(max_workers=max(1, a.workers)) as pool:
        pending = list(reversed(stems))
        running = set()
        while pending or running:
            while pending and len(running) < 2 * a.workers:
                running.add(pool.submit(_task, pending.pop(), settings))
            done, running = wait(running, return_when=FIRST_COMPLETED)
            for fut in done:
                r = fut.result()
                results[r["stem"]] = r
                if len(results) % 20 == 0 or len(results) == len(stems):
                    print(f"  {len(results)}/{len(stems)} {(time.time() - started) / 60:.1f} min", flush=True)
    base_rows = {s: {"dataset": s, **results[s]["row"]} for s in stems}
    if not a.eval:
        df = pd.DataFrame([r for s in stems for r in results[s]["rows"]])
        df["embryo"] = df["stem"].str.split("_").str[0]
        path = out / f"moves_{tag}.parquet"
        df.to_parquet(path, index=False)
        print(f"wrote {path} ({len(df)} moves); base score {A.summarise(list(base_rows.values())):.6f}", flush=True)
        return
    table = []
    for name in rules:
        counts = {s: results[s]["eval"][name] for s in stems}
        e = {"rule": name, "params": rules[name],
             **{k: int(sum(c[k] for c in counts.values())) for k in ("moves", "tp_add", "fp_add", "tp_drop", "fp_drop")}}
        for emb in ("all", "44b6", "6bba"):
            se = [s for s in stems if emb == "all" or s.startswith(emb)]
            if not se:
                continue
            b = {s: base_rows[s] for s in se}
            new = {r["dataset"]: r for r in A.video_score_rows(counts, b)}
            e[f"d_{emb}"] = A.summarise(list(new.values())) - A.summarise(list(b.values()))
            e[f"win_{emb}"] = sum(R._video_score(new[s]) > R._video_score(b[s]) + 1e-12 for s in se) / len(se)
            e[f"loss_{emb}"] = sum(R._video_score(new[s]) < R._video_score(b[s]) - 1e-12 for s in se) / len(se)
        table.append(e)
        print(json.dumps({k: (round(v, 6) if isinstance(v, float) else v) for k, v in e.items()}), flush=True)
    R._atomic_text(out / f"swap_eval_{tag}.json", R._dumps(table, indent=1))


if __name__ == "__main__":
    main()
