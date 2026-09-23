"""Place every Kaggle 44b6 train clip inside the public Ultrack "dorado" zebrafish movie (tools/dorado_crops.py).

Finding (2026-09-24, L3 verification): the 44b6 videos are space-time crops of the SAME recording as the public dorado
movie (same voxel scale, same orientation, no flips). Example: 44b6_12dfb391 = dorado frames 106..205 at a fixed shift;
with that one (time offset, translation) 84% of its 777 GT nodes on all frames have a dorado track point within 2.5 um
(no search), wrong time offsets give 5-11%. 6bba clips stay at chance (a different embryo). Consequence: a DaughterNet
trained on dorado crops has seen the 44b6 evaluation images (and Ultrack pseudo-labels of the same cells) unless the
dorado samples inside the 44b6 clips are dropped (tools/train_dorado.py --exclude-kaggle, which reads this file).

Method (no image data, GT node positions and dorado track points only):
  roots   one clip per splits.json leak group (+ every singleton): for each time offset o, the clip's GT nodes on up to
          `frames` frames vote for translations against the dorado track points at frame t + o (6.5 um bins); the top
          bins are refined (nearest dorado point, mean shift) and scored by the number of DISTINCT GT nodes with a dorado
          point within 2.5 um. Accepted when, with the best (o, v) fixed, a no-search check over ALL GT nodes of the clip
          matches >= 25% of them, >= 10 nodes and >= 3x the best control (same v, time offset +-20 / +-40; a wrong
          translation matches about as many nodes at every time offset). A failed root is
          retried with a larger node budget, then with the next group member.
  others  placed through splits.json shared_annotation_links (offset_tzyx_a_minus_b from shared global GT node ids) and
          checked the same way.
Output JSON (default data_external/dorado/kaggle44b6_in_dorado.json): per 44b6 stem: reliable, o (dorado t = clip t + o),
shift_vox (dorado voxel = clip voxel + shift_vox), matched / n_gt, controls, how. Clip footprint in dorado space:
frames [o, o + 99], voxels [shift_vox, shift_vox + (64, 256, 256)).

    python tools/register_44b6_dorado.py [--workers 5] [--out data_external/dorado/kaggle44b6_in_dorado.json]
Resumable: reliable roots already in --out are reused.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import deque
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
for _p in (str(ROOT), str(ROOT / "experiments" / "l2_daughternet" / "kdn_train")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

N_T = 522                                   # dorado frames
SCALE = np.array([1.625, 0.40625, 0.40625])  # um per voxel (z, y, x), Kaggle == dorado
CLIP_VOX = (64, 256, 256)
CLIP_T = 100
R_UM, BIN_UM, TOP_K = 2.5, 6.5, 100
MIN_FRAC, MIN_CTRL_RATIO, MIN_MATCHED = 0.25, 3.0, 10
DATA = ROOT / "biohub-cell-tracking-during-development" / "train"
TRACKS = ROOT / "data_external" / "dorado" / "tracks" / "tracks.npz"
SPLITS = ROOT / "experiments" / "l2_daughternet" / "splits.json"
DEFAULT_OUT = ROOT / "data_external" / "dorado" / "kaggle44b6_in_dorado.json"

_UM = _PTR = None
_TREES: dict = {}


def log(*a) -> None:
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def _init(tracks: str = str(TRACKS)) -> None:
    global _UM, _PTR
    d = np.load(tracks)
    t = d["pt_t"].astype(np.int32)
    order = np.argsort(t, kind="stable")
    _UM = d["pt_zyx"][order].astype(np.float32) * 0.40625          # bundle units are isotropic 0.40625 um
    _PTR = np.searchsorted(t[order], np.arange(N_T + 1))


def _frame(t: int) -> np.ndarray:
    return _UM[_PTR[t]:_PTR[t + 1]]


def _tree(t: int):
    from scipy.spatial import cKDTree
    if t not in _TREES:
        if len(_TREES) > 160:
            _TREES.pop(next(iter(_TREES)))
        _TREES[t] = cKDTree(_frame(t))
    return _TREES[t]


def _gt(stem: str, data_dir: Path = DATA) -> tuple[np.ndarray, np.ndarray]:
    import kdn_core
    g = kdn_core.read_gt_geff(Path(data_dir) / f"{stem}.geff")
    return g["t"].astype(np.int64), np.stack([g["z"], g["y"], g["x"]], 1) * SCALE


def matched(T: np.ndarray, P: np.ndarray, o: int, v: np.ndarray) -> int | None:
    """Distinct GT nodes (t, p um) with a dorado track point within R_UM at frame t + o after translation v."""
    n = 0
    for t in np.unique(T):
        if not 0 <= t + o < N_T:
            return None
        m = T == t
        d, _ = _tree(int(t + o)).query(P[m] + v, distance_upper_bound=R_UM)
        n += int(np.isfinite(d).sum())
    return n


def check(T, P, o, v) -> dict:
    m = matched(T, P, o, v)
    ctrl = [matched(T, P, o + d, v) for d in (-40, -20, 20, 40)]
    ctrl_max = max([c for c in ctrl if c is not None], default=0)
    ok = m is not None and m >= max(MIN_MATCHED, MIN_FRAC * len(T), MIN_CTRL_RATIO * ctrl_max)
    return {"matched": m, "n_gt": int(len(T)), "frac": None if m is None else round(m / len(T), 3),
            "controls": ctrl, "reliable": bool(ok)}


def search(job: tuple[str, int, int, str]) -> dict:
    stem, max_nodes, max_frames, data_dir = job
    if _UM is None:
        _init()
    t0 = time.time()
    T, P = _gt(stem, Path(data_dir))
    ts, cnt = np.unique(T, return_counts=True)
    chosen: list[int] = []
    for i in np.argsort(-cnt, kind="stable"):                   # GT-rich frames, >= 5 frames apart
        if all(abs(int(ts[i]) - c) >= 5 for c in chosen):
            chosen.append(int(ts[i]))
        if int(cnt[np.isin(ts, chosen)].sum()) >= max_nodes or len(chosen) >= max_frames:
            break
    sel = np.isin(T, chosen)
    Ts, Ps = T[sel], P[sel]
    best = (-1, 0, np.zeros(3))
    for o in range(-int(T.min()), N_T - int(T.max())):
        v = np.concatenate([(_frame(t + o)[None, :, :] - Ps[Ts == t][:, None, :]).reshape(-1, 3) for t in chosen])
        k = np.floor(v / BIN_UM).astype(np.int64)
        k -= k.min(0)
        key = (k[:, 0] * 100000 + k[:, 1]) * 100000 + k[:, 2]
        u, inv, c = np.unique(key, return_inverse=True, return_counts=True)
        top = np.argsort(-c)[:TOP_K]
        sums = np.zeros((len(u), 3))
        np.add.at(sums, inv, v)
        for vv in sums[top] / c[top, None]:
            for _ in range(3):
                res = []
                for t in chosen:
                    q = Ps[Ts == t] + vv
                    d, j = _tree(t + o).query(q, distance_upper_bound=4.0)
                    ok = np.isfinite(d)
                    res.append(_frame(t + o)[j[ok]] - q[ok])
                res = np.concatenate(res)
                if not len(res):
                    break
                vv = vv + res.mean(0)
            s = matched(Ts, Ps, o, vv)
            if s is not None and s > best[0]:
                best = (s, o, vv)
    s, o, v = best
    out = {"stem": stem, "o": int(o), "shift_um": [float(x) for x in v], "search_score": int(s),
           "search_nodes": int(sel.sum()), "search_frames": chosen, "budget": [max_nodes, max_frames],
           "secs": round(time.time() - t0, 1)}
    out.update(check(T, P, o, v))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--data-dir", default=str(DATA))
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--recheck-only", action="store_true", help="no search: re-check the roots in --out, propagate")
    ap.add_argument("--budgets", default="30x8,80x24", help="search node budgets per attempt: <nodes>x<frames>,...")
    a = ap.parse_args(argv)
    out_path = Path(a.out)
    sp = json.loads(SPLITS.read_text())
    stems = sorted(s for s in sp["folds"] if s.startswith("44b6"))
    groups = [list(g) for g in sp["meta"]["leak_groups"]]
    in_group = {s for g in groups for s in g}
    groups += [[s] for s in stems if s not in in_group]
    _init()

    def richness(s):
        return int(np.unique(_gt(s, a.data_dir)[0], return_counts=True)[1].max())

    for g in groups:
        g.sort(key=lambda s: (-richness(s), s))
    prev = json.loads(out_path.read_text()).get("roots", {}) if out_path.is_file() else {}
    roots = {}
    for s, r in prev.items():                                    # reuse earlier roots only if they still check out
        if s in stems and "o" in r and "shift_um" in r:
            r = {**r, **check(*_gt(s, a.data_dir), int(r["o"]), np.array(r["shift_um"]))}
            if r["reliable"]:
                roots[s] = r
    budgets = [tuple(int(v) for v in b.split("x")) for b in a.budgets.split(",")]
    log(f"{len(stems)} 44b6 clips in {len(groups)} units (leak groups + singletons); reused roots {len(roots)}")
    tried: dict[tuple, dict] = {}
    failed: list[dict] = []
    with Pool(a.workers, initializer=_init) as pool:
        for attempt in range(0 if a.recheck_only else max(len(g) for g in groups) * len(budgets)):
            todo = []
            for g in groups:
                if any(s in roots for s in g):
                    continue
                for s in g:                                      # next untried (stem, budget) of this unit
                    b = next((b for b in budgets if (s, b) not in tried), None)
                    if b is not None:
                        todo.append((s, b[0], b[1], a.data_dir))
                        break
            if not todo:
                break
            log(f"round {attempt + 1}: {len(todo)} searches")
            for r in pool.imap_unordered(search, todo):
                tried[(r["stem"], tuple(r["budget"]))] = r
                log(f"  {r['stem']}: o={r['o']} search {r['search_score']}/{r['search_nodes']} | all frames "
                    f"{r['matched']}/{r['n_gt']} controls {r['controls']} -> {'OK' if r['reliable'] else 'fail'} "
                    f"({r['secs']}s)")
                if r["reliable"]:
                    roots[r["stem"]] = r
                else:
                    failed.append(r)
    # propagate through the shared-annotation links (pos_b = pos_a + d_ab with d_ab = b - a)
    adj: dict[str, list] = {}
    for L in sp["meta"]["shared_annotation_links"]:
        d = np.array(L["offset_tzyx_a_minus_b"], float)
        adj.setdefault(L["a"], []).append((L["b"], -d))
        adj.setdefault(L["b"], []).append((L["a"], d))
    place = {s: (r["o"], np.array(r["shift_um"]), "search") for s, r in roots.items()}
    q = deque(place)
    while q:
        s_a = q.popleft()
        o_a, v_a, _ = place[s_a]
        for s_b, d_ab in adj.get(s_a, []):
            if s_b not in place:          # same physical node: t_b = t_a + dt -> o_b = o_a - dt; v_b = v_a - dp
                place[s_b] = (o_a - int(round(d_ab[0])), v_a - d_ab[1:] * SCALE, f"via {s_a}")
                q.append(s_b)
    clips = {}
    for s in stems:
        if s not in place:
            clips[s] = {"placed": False, "reliable": False}
            log(f"{s}: NOT placed")
            continue
        o, v, how = place[s]
        T, P = _gt(s, a.data_dir)
        c = {"placed": True, "how": how, "o": int(o), "shift_um": [round(float(x), 3) for x in v],
             "shift_vox": [round(float(x), 3) for x in v / SCALE],
             "clip_frames_dorado": [int(o), int(o) + CLIP_T - 1]}
        c.update(check(T, P, o, v))
        clips[s] = c
        log(f"{s}: {how:22s} o={o:4d} shift_vox {np.round(v / SCALE, 1).tolist()} matched {c['matched']}/{c['n_gt']} "
            f"controls {c['controls']} {'OK' if c['reliable'] else 'UNRELIABLE'}")
    n_ok = sum(c["reliable"] for c in clips.values())
    payload = {"generator": "tools/register_44b6_dorado.py", "built": time.strftime("%Y-%m-%d %H:%M:%S"),
               "clip_vox": list(CLIP_VOX), "clip_frames": CLIP_T, "voxel_um": SCALE.tolist(), "r_um": R_UM,
               "min_frac": MIN_FRAC, "min_ctrl_ratio": MIN_CTRL_RATIO, "min_matched": MIN_MATCHED, "n_clips": len(stems), "n_reliable": n_ok,
               "unreliable": sorted(s for s, c in clips.items() if not c["reliable"]), "roots": roots,
               "failed_searches": failed, "clips": clips}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=1))
    log(f"{n_ok}/{len(stems)} 44b6 clips placed reliably -> {out_path}")
    return 0 if n_ok == len(stems) else 1


if __name__ == "__main__":
    sys.exit(main())
