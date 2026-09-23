"""Video-grouped 5-fold CV splits + selection/confirmation video sets for the L2 DaughterNet stage.

Reads every local GT .geff with the same reader as tools/score_geffs.py (tracksdata IndexedRXGraph.from_geff, the
official package's io path), counts GT divisions per video (nodes with >= 2 outgoing GT edges; cross-checked against
tracksdata's dividing_nodes(), which is what the official division metric iterates), and writes

    experiments/l2_daughternet/splits.json
    {
      "folds":               {"<stem>": 0..4},        # one fold per video; leak groups share one fold
      "selection":           [stems],                  # 6bba videos with ODD index in sorted 6bba order
      "confirmation":        [stems],                  # 6bba EVEN index + all 44b6 videos
      "divisions_per_video": {"<stem>": int},
      "summary":             {...},                    # counts per fold / embryo / split + shared_annotation
      "meta":                {...}                     # seed, method, data dir, reader, leak_groups, links
    }

LEAKAGE: the train videos are overlapping space-time crops of one recording per embryo. In 44b6, 62 video pairs share
4..164 IDENTICAL GT nodes (same global node id = absolute_frame * 1e9 + cell, one (dt,dz,dy,dx) offset; 2 shared
divisions; 64 of the 71 44b6 videos fall into 11 groups, the largest has 24 videos), so a plain split by video puts
identical labelled samples on both sides of a fold. find_shared_annotation_links() detects these pairs from the GT
alone; their connected components (leak_groups) are kept in one fold, and verify() fails if any link crosses a fold.
6bba shows no shared annotation (its ids are local per-video counters; image checks found a few one-frame boundary
overlaps between consecutive crops, annotated independently, which this detector does not link).

Fold assignment (deterministic, no RNG state - order keys are sha256(seed:...), stable across Python versions):
  1. units = leak groups (one unit each) + every other video as its own unit;
  2. greedy: groups largest first, then videos stratum by stratum ((embryo, min(n_div, 3)), bin high->low), each into
     the fold that lowers the objective most - weighted squared deviation from the per-fold mean of videos and
     divisions overall, per (embryo, fold), and video counts per stratum;
  3. local search: best-improving move of one unit or swap of two units until nothing improves.

Usage:
    python tools/make_splits.py                       # build + verify + print summary
    python tools/make_splits.py --verify-only         # re-read GT and check an existing splits.json
    python tools/make_splits.py --seed 7 --out other.json
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "official" / "src"))
warnings.filterwarnings("ignore")

DEFAULT_DATA = Path(os.environ.get("BIOHUB_DATA_DIR", PROJECT_ROOT / "biohub-cell-tracking-during-development" / "train"))
DEFAULT_OUT = PROJECT_ROOT / "experiments" / "l2_daughternet" / "splits.json"
EMBRYOS = ("44b6", "6bba")
N_FOLDS = 5
SEED = 20260923
DIV_BINS = (0, 1, 2, 3)  # bin = min(n_div, 3): 0, 1, 2, 3+
EXPECTED_DIVISIONS = 151
EXPECTED_VIDEOS = 199
MIN_SHARED_NODES = 8  # exact shared GT nodes that link two videos into one fold group (null max on 6bba = 7)
MIN_SHARED_IDS = 4  # or: shared node ids agreeing on one offset (+-1 voxel) (null max on 6bba = 3)
W_OVERALL, W_EMBRYO, W_STRATUM = 2.0, 1.0, 1.0  # fold-balance objective weights


def embryo_of(stem: str) -> str:
    prefix = stem.split("_", 1)[0]
    if prefix not in EMBRYOS:
        raise ValueError(f"unexpected embryo prefix in stem {stem!r}")
    return prefix


def count_gt_divisions(geff_path: Path) -> dict:
    """GT division count of one video: nodes with >= 2 outgoing GT edges (== tracksdata dividing_nodes()).
    Also returns the node table (ids, t/z/y/x voxel coords) and edges for the shared-annotation (leakage) check."""
    import numpy as np
    import tracksdata as td

    loaded = td.graph.IndexedRXGraph.from_geff(geff_path)
    graph = loaded[0] if isinstance(loaded, tuple) else loaded
    edge_list = [(int(src), int(dst)) for src, dst in graph.edge_list()]
    out_deg = collections.Counter(src for src, _dst in edge_list)
    n_div = sum(1 for d in out_deg.values() if d >= 2)
    n_deg3 = sum(1 for d in out_deg.values() if d >= 3)
    n_dividing_nodes = len(list(graph.dividing_nodes()))
    if n_dividing_nodes != n_div:
        raise RuntimeError(f"{geff_path.name}: out-degree>=2 count {n_div} != dividing_nodes() {n_dividing_nodes}")
    attrs = graph.node_attrs()
    ids = np.asarray(attrs["node_id"].to_numpy(), dtype=np.int64)
    pos = np.stack([np.asarray(attrs[k].to_numpy(), dtype=np.int64) for k in ("t", "z", "y", "x")], axis=1)
    return {"divisions": n_div, "out_degree_ge3": n_deg3, "nodes": int(graph.num_nodes()), "edges": int(graph.num_edges()),
            "ids": ids, "pos": pos, "edge_list": edge_list, "dividing": sorted(k for k, d in out_deg.items() if d >= 2)}


def read_all_divisions(data_dir: Path) -> tuple[dict[str, int], dict, dict[str, dict]]:
    geffs = sorted(p for p in data_dir.glob("*.geff") if p.is_dir())
    if not geffs:
        raise FileNotFoundError(f"no .geff stores in {data_dir}")
    divs, tables = {}, {}
    info = {"out_degree_ge3": 0, "gt_nodes": 0, "gt_edges": 0, "missing_zarr": []}
    for i, g in enumerate(geffs):
        r = count_gt_divisions(g)
        divs[g.stem] = r["divisions"]
        tables[g.stem] = {k: r[k] for k in ("ids", "pos", "edge_list", "dividing")}
        info["out_degree_ge3"] += r["out_degree_ge3"]
        info["gt_nodes"] += r["nodes"]
        info["gt_edges"] += r["edges"]
        if not (data_dir / f"{g.stem}.zarr").exists():
            info["missing_zarr"].append(g.stem)
        if (i + 1) % 40 == 0:
            print(f"  read {i + 1}/{len(geffs)} GT graphs", flush=True)
    return divs, info, tables


def _pos_key(pos):
    """Injective int64 key of (t, z, y, x) rows (components |v| < 2048); linear, so key(p + o) = key(p) + key(o)."""
    b = 4096
    return ((pos[..., 0] * b + pos[..., 1]) * b + pos[..., 2]) * b + pos[..., 3]


def find_shared_annotation_links(tables: dict[str, dict], min_shared: int = None, min_shared_ids: int = None) -> list[dict]:
    """Video pairs of one embryo whose GT annotations overlap: the same annotated nodes at one exact (dt, dz, dy, dx)
    offset. The train videos are overlapping space-time crops of one recording per embryo (44b6 node ids are even
    global: id // 1e9 = absolute frame), so a video-grouped split leaks identical labelled samples across folds.
    Candidate offsets come from (a) node ids shared by both videos and (b) identical 3-node track segments (two
    consecutive displacement vectors, translation invariant). Evidence = max of the exact coordinate matches at the
    best candidate offset (link at >= MIN_SHARED_NODES) and the shared node ids that agree on one offset within +-1
    voxel (link at >= MIN_SHARED_IDS). Null on 6bba (local ids, no shared crops): 7 coordinate matches, 3 agreeing
    ids; 44b6 real overlaps share up to 164 nodes."""
    import numpy as np

    min_shared = MIN_SHARED_NODES if min_shared is None else int(min_shared)
    min_shared_ids = min(MIN_SHARED_IDS, min_shared) if min_shared_ids is None else int(min_shared_ids)
    stems = sorted(tables)
    cand: dict[tuple[str, str], collections.Counter] = collections.defaultdict(collections.Counter)
    shared_ids: dict[tuple[str, str], dict] = {}
    for emb in EMBRYOS:
        segs = collections.defaultdict(list)  # signature -> [(stem, anchor (t,z,y,x))]
        ids_of = {}
        for s in stems:
            if embryo_of(s) != emb:
                continue
            tb = tables[s]
            row = {int(i): k for k, i in enumerate(tb["ids"].tolist())}
            pos = tb["pos"].tolist()
            ids_of[s] = dict(zip(tb["ids"].tolist(), pos))
            children = collections.defaultdict(list)
            for a, b in tb["edge_list"]:
                children[row[a]].append(row[b])
            for n0, c1 in children.items():
                for n1 in c1:
                    for n2 in children.get(n1, ()):
                        p0, p1, p2 = pos[n0], pos[n1], pos[n2]
                        sig = tuple(p1[k] - p0[k] for k in range(4)) + tuple(p2[k] - p1[k] for k in range(4))
                        segs[sig].append((s, tuple(p0)))
        for lst in segs.values():
            for i in range(len(lst)):
                a, pa = lst[i]
                for j in range(i + 1, len(lst)):
                    b, pb = lst[j]
                    if a == b:
                        continue
                    if a < b:
                        cand[(a, b)][tuple(x - y for x, y in zip(pa, pb))] += 1
                    else:
                        cand[(b, a)][tuple(y - x for x, y in zip(pa, pb))] += 1
        es = sorted(ids_of)
        for i, a in enumerate(es):
            for b in es[i + 1:]:
                common = ids_of[a].keys() & ids_of[b].keys()
                if common:
                    shared_ids[(a, b)] = {nid: tuple(x - y for x, y in zip(ids_of[a][nid], ids_of[b][nid])) for nid in common}
                    for d in shared_ids[(a, b)].values():
                        cand[(a, b)][d] += 1
    # GT centres of nuclei cut by the crop border are clamped to the border (e.g. z = 63 in one crop, z = 64 after the
    # shift into the other), so shifted points up to CLAMP voxels outside the annotated range are clamped too.
    allpos = np.concatenate([tables[s]["pos"] for s in stems])
    lo, hi, clamp = allpos[:, 1:].min(0), allpos[:, 1:].max(0), 2
    keys = {s: np.sort(_pos_key(tables[s]["pos"])) for s in stems}
    is_div = {s: np.isin(tables[s]["ids"], tables[s]["dividing"]) for s in stems}
    div_keys = {s: _pos_key(tables[s]["pos"][is_div[s]]) for s in stems}
    dividing = {s: set(int(v) for v in tables[s]["dividing"]) for s in stems}

    def shifted(b, off):
        q = tables[b]["pos"] + np.asarray(off, dtype=np.int64)
        ok = np.all((q[:, 1:] >= lo - clamp) & (q[:, 1:] <= hi + clamp), axis=1)
        q[:, 1:] = np.clip(q[:, 1:], lo, hi)
        return _pos_key(q), ok

    def hits(a, q, ok):
        idx = np.minimum(np.searchsorted(keys[a], q), len(keys[a]) - 1)
        return ok & (keys[a][idx] == q)

    links = []
    for (a, b), offs in sorted(cand.items()):
        # (a) coordinates: exact matches (after border clamping) at the best candidate offset
        best = (0, None)
        for off, _support in offs.most_common(5):
            n = int(hits(a, *shifted(b, off)).sum())
            if n > best[0]:
                best = (n, off)
        n_xyz, n_div_xyz = best[0], 0
        if best[1] is not None:
            q, ok = shifted(b, best[1])
            n_div_xyz = int((hits(a, q, ok) & is_div[b] & np.isin(q, div_keys[a])).sum())
        # (b) ids (44b6 ids are global): shared ids whose position differences agree with their modal offset within
        # +-1 voxel per spatial axis (border centres of a cut nucleus move by 1 voxel between crops); random id
        # collisions (6bba ids are local counters) have unrelated positions and never agree
        n_id, n_div_id, mode = 0, 0, None
        if (a, b) in shared_ids:
            diffs = shared_ids[(a, b)]
            mode = collections.Counter(diffs.values()).most_common(1)[0][0]
            agree = [nid for nid, d in diffs.items()
                     if d[0] == mode[0] and all(abs(d[k] - mode[k]) <= 1 for k in (1, 2, 3))]
            n_id = len(agree)
            n_div_id = sum(1 for nid in agree if nid in dividing[a] and nid in dividing[b])
        n = max(n_xyz, n_id)
        if n_xyz >= min_shared or n_id >= min_shared_ids:
            off = best[1] if n_xyz >= n_id else mode
            links.append({"a": a, "b": b, "shared_nodes": n, "shared_divisions": max(n_div_xyz, n_div_id),
                          "offset_tzyx_a_minus_b": [int(v) for v in off]})
    return links


def leak_groups(stems, links: list[dict]) -> list[list[str]]:
    """Connected components (size >= 2) of the shared-annotation graph; each must sit in ONE fold."""
    parent = {s: s for s in stems}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for link in links:
        ra, rb = find(link["a"]), find(link["b"])
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    comps = collections.defaultdict(list)
    for s in sorted(stems):
        comps[find(s)].append(s)
    return sorted((c for c in comps.values() if len(c) > 1), key=lambda c: (-len(c), c[0]))


def _portable_path(p: Path) -> str:
    """Repo-relative POSIX path when under the project (no local user name in the JSON that ships to Kaggle)."""
    try:
        return Path(p).resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return Path(p).as_posix()


def _key(seed: int, *parts) -> str:
    return hashlib.sha256(":".join([str(seed), *map(str, parts)]).encode()).hexdigest()


def _bin(n_div: int) -> int:
    return min(int(n_div), DIV_BINS[-1])


def _unit_vector(unit: list[str], divs: dict[str, int]) -> dict:
    """Additive count features of a fold unit (one video, or one shared-annotation group)."""
    v = collections.Counter()
    for s in unit:
        e = embryo_of(s)
        v["V"] += 1
        v["D"] += divs[s]
        v[("V", e)] += 1
        v[("D", e)] += divs[s]
        v[("S", e, _bin(divs[s]))] += 1
    return v


def _weight(feature) -> float:
    if feature in ("V", "D"):
        return W_OVERALL
    return W_EMBRYO if feature[0] in ("V", "D") else W_STRATUM


def assign_folds(divs: dict[str, int], n_folds: int = N_FOLDS, seed: int = SEED,
                 groups: list[list[str]] | None = None) -> dict[str, int]:
    """Leakage-safe, balanced folds. Every shared-annotation group is ONE unit (all its videos in one fold); other
    videos are single units. Objective = weighted squared deviation from the per-fold mean of: videos and divisions
    overall (W_OVERALL), per embryo (W_EMBRYO) and video counts per (embryo, division-count bin) stratum (W_STRATUM).
    Greedy placement (groups largest first, then videos stratum by stratum, bin high->low, sha256 order) into the fold
    that lowers the objective most (ties -> seeded label order), then best-improving unit moves / swaps until none
    improves. Deterministic: no RNG, only sha256(seed:...) keys."""
    labels = sorted(range(n_folds), key=lambda f: _key(seed, "fold", f))
    grouped = {s for g in (groups or []) for s in g}
    if len(grouped) != sum(len(g) for g in (groups or [])):
        raise ValueError("a video appears in two leak groups")
    units = [sorted(g) for g in (groups or [])]
    units.sort(key=lambda g: (-len(g), -sum(divs[s] for s in g), _key(seed, "group", g[0])))
    singles = [s for s in divs if s not in grouped]
    singles.sort(key=lambda s: (EMBRYOS.index(embryo_of(s)), -_bin(divs[s]), -divs[s], _key(seed, s)))
    units += [[s] for s in singles]
    vecs = [_unit_vector(u, divs) for u in units]
    total = collections.Counter()
    for v in vecs:
        total.update(v)
    target = {k: total[k] / n_folds for k in total}
    load = [collections.Counter() for _ in range(n_folds)]

    def delta_add(f, v, sign=1) -> float:
        return sum(_weight(k) * ((load[f][k] + sign * n - target[k]) ** 2 - (load[f][k] - target[k]) ** 2)
                   for k, n in v.items())

    def delta_swap(fi, vi, fj, vj) -> float:
        diff = {k: vj.get(k, 0) - vi.get(k, 0) for k in set(vi) | set(vj)}
        d = 0.0
        for k, n in diff.items():
            if n:
                w, t = _weight(k), target[k]
                d += w * ((load[fi][k] + n - t) ** 2 - (load[fi][k] - t) ** 2)
                d += w * ((load[fj][k] - n - t) ** 2 - (load[fj][k] - t) ** 2)
        return d

    where = [0] * len(units)
    for i, v in enumerate(vecs):
        f = min(labels, key=lambda f: (round(delta_add(f, v), 9), labels.index(f)))
        where[i] = f
        load[f].update(v)
    # Local search: best-improving move of one unit, or swap of two units, until nothing improves.
    while True:
        best = (-1e-9, None)
        for i, vi in enumerate(vecs):
            fi = where[i]
            out_i = delta_add(fi, vi, -1)
            for g in labels:
                if g != fi:
                    d = out_i + delta_add(g, vi)
                    if d < best[0] - 1e-9:
                        best = (d, ("move", i, g))
            for j in range(i + 1, len(vecs)):
                fj = where[j]
                if fj == fi or vecs[j] == vi:
                    continue
                d = delta_swap(fi, vi, fj, vecs[j])
                if d < best[0] - 1e-9:
                    best = (d, ("swap", i, j))
        if best[1] is None:
            break
        kind, i, x = best[1]
        if kind == "move":
            load[where[i]].subtract(vecs[i]); load[x].update(vecs[i]); where[i] = x
        else:
            fi, fj = where[i], where[x]
            load[fi].subtract(vecs[i]); load[fi].update(vecs[x])
            load[fj].subtract(vecs[x]); load[fj].update(vecs[i])
            where[i], where[x] = fj, fi
    folds = {s: where[i] for i, u in enumerate(units) for s in u}
    return dict(sorted(folds.items()))


def selection_confirmation(stems) -> tuple[list[str], list[str]]:
    s6 = sorted(s for s in stems if embryo_of(s) == "6bba")
    s4 = sorted(s for s in stems if embryo_of(s) == "44b6")
    selection = [s for i, s in enumerate(s6) if i % 2 == 1]
    confirmation = sorted([s for i, s in enumerate(s6) if i % 2 == 0] + s4)
    return selection, confirmation


def _counts(stems, divs, by_embryo: bool = True) -> dict:
    stems = list(stems)
    out = {
        "videos": len(stems),
        "divisions": int(sum(divs[s] for s in stems)),
        "videos_with_divisions": sum(1 for s in stems if divs[s] > 0),
    }
    for e in EMBRYOS if by_embryo else ():
        es = [s for s in stems if embryo_of(s) == e]
        out[e] = {
            "videos": len(es),
            "divisions": int(sum(divs[s] for s in es)),
            "videos_with_divisions": sum(1 for s in es if divs[s] > 0),
        }
    return out


def _leak_summary(folds, selection, links, groups) -> dict:
    sel_set = set(selection)
    return {
        "min_shared_nodes": MIN_SHARED_NODES,
        "min_shared_ids": MIN_SHARED_IDS,
        "links": len(links),
        "links_per_embryo": {e: sum(1 for l in links if embryo_of(l["a"]) == e) for e in EMBRYOS},
        "shared_gt_nodes": int(sum(l["shared_nodes"] for l in links)),
        "shared_gt_divisions": int(sum(l["shared_divisions"] for l in links)),
        "groups": len(groups),
        "grouped_videos": sum(len(g) for g in groups),
        "group_sizes": [len(g) for g in groups],
        "cross_fold_links": sum(1 for l in links if folds[l["a"]] != folds[l["b"]]),
        "selection_confirmation_links": sum(1 for l in links if (l["a"] in sel_set) != (l["b"] in sel_set)),
    }


def build_summary(folds, selection, confirmation, divs, n_folds, links=(), groups=()) -> dict:
    stems = sorted(divs)
    sel_set, conf_set = set(selection), set(confirmation)
    per_fold = {}
    for f in range(n_folds):
        fs = [s for s in stems if folds[s] == f]
        c = _counts(fs, divs)
        c["selection_videos"] = sum(1 for s in fs if s in sel_set)
        c["confirmation_videos"] = sum(1 for s in fs if s in conf_set)
        c["division_count_histogram"] = {
            str(k): v for k, v in sorted(collections.Counter(divs[s] for s in fs).items())
        }
        per_fold[str(f)] = c
    return {
        "total": _counts(stems, divs),
        "per_embryo": {e: _counts([s for s in stems if embryo_of(s) == e], divs, by_embryo=False) for e in EMBRYOS},
        "per_fold": per_fold,
        "per_split": {"selection": _counts(selection, divs), "confirmation": _counts(confirmation, divs)},
        "division_count_histogram": {
            e: {str(k): v for k, v in sorted(collections.Counter(divs[s] for s in stems if embryo_of(s) == e).items())}
            for e in EMBRYOS
        },
        "shared_annotation": _leak_summary(folds, selection, list(links), list(groups)),
    }


def verify(splits: dict, divs: dict[str, int], n_folds: int = N_FOLDS, links: list[dict] | None = None) -> list[str]:
    """Return a list of failures (empty = all checks passed). Division total mismatch is reported, not failed.
    `links` = shared-annotation links recomputed from the GT: any link whose two videos sit in different folds is a
    label leak and fails the check."""
    errors = []
    links = list(links or [])
    stems = set(divs)
    folds = splits["folds"]
    if set(folds) != stems:
        errors.append(f"folds keys != GT stems: missing {sorted(stems - set(folds))[:5]} extra {sorted(set(folds) - stems)[:5]}")
    if len(folds) != len(stems):
        errors.append(f"folds has {len(folds)} entries, expected {len(stems)}")
    bad = {s: f for s, f in folds.items() if isinstance(f, bool) or not (isinstance(f, int) and 0 <= f < n_folds)}
    if bad:
        errors.append(f"fold ids outside 0..{n_folds - 1}: {list(bad.items())[:5]}")
    for f in range(n_folds):
        if not any(v == f for v in folds.values()):
            errors.append(f"fold {f} is empty")
    sel, conf = splits["selection"], splits["confirmation"]
    if len(sel) != len(set(sel)) or len(conf) != len(set(conf)):
        errors.append("duplicate stems inside selection or confirmation")
    if set(sel) & set(conf):
        errors.append(f"selection and confirmation overlap: {sorted(set(sel) & set(conf))[:5]}")
    if set(sel) | set(conf) != stems:
        errors.append("selection U confirmation != all stems")
    exp_sel, exp_conf = selection_confirmation(stems)
    if sorted(sel) != sorted(exp_sel) or sorted(conf) != sorted(exp_conf):
        errors.append("selection/confirmation do not follow the odd/even 6bba rule")
    if any(embryo_of(s) != "6bba" for s in sel):
        errors.append("selection contains non-6bba videos")
    if splits.get("divisions_per_video") != divs:
        errors.append("divisions_per_video differs from the GT re-count")
    if not errors:
        leaks = [(l["a"], l["b"], l["shared_nodes"]) for l in links if folds[l["a"]] != folds[l["b"]]]
        if leaks:
            errors.append(f"{len(leaks)} shared-annotation links cross folds (label leakage), e.g. {leaks[:3]}")
        groups = leak_groups(stems, links)
        if splits.get("meta", {}).get("leak_groups") not in (None, groups):
            errors.append("meta.leak_groups differs from the groups recomputed from the GT")
        summary = build_summary(folds, sel, conf, divs, n_folds, links, groups)
        if splits.get("summary") != json.loads(json.dumps(summary)):
            errors.append("stored summary is stale: it does not match a summary recomputed from folds/selection/"
                          "confirmation and the GT shared-annotation links")
    return errors


def print_summary(summary: dict, n_folds: int) -> None:
    t = summary["total"]
    print(f"TOTAL videos={t['videos']} divisions={t['divisions']} videos_with_divisions={t['videos_with_divisions']}")
    for e in EMBRYOS:
        c = summary["per_embryo"][e]
        print(f"  {e}: videos={c['videos']} divisions={c['divisions']} videos_with_div={c['videos_with_divisions']} "
              f"hist(n_div:videos)={summary['division_count_histogram'][e]}")
    print(f"{'fold':>4} {'vid':>4} {'div':>4} {'vwd':>4} | {'44b6 v/d/vwd':>13} | {'6bba v/d/vwd':>13} | {'sel':>4} {'conf':>4}")
    for f in range(n_folds):
        c = summary["per_fold"][str(f)]
        a, b = c["44b6"], c["6bba"]
        print(f"{f:>4} {c['videos']:>4} {c['divisions']:>4} {c['videos_with_divisions']:>4} | "
              f"{a['videos']:>4}/{a['divisions']:>3}/{a['videos_with_divisions']:>3} | "
              f"{b['videos']:>4}/{b['divisions']:>3}/{b['videos_with_divisions']:>3} | "
              f"{c['selection_videos']:>4} {c['confirmation_videos']:>4}")
    for name in ("selection", "confirmation"):
        c = summary["per_split"][name]
        print(f"  {name:12s} videos={c['videos']:3d} divisions={c['divisions']:3d} "
              f"(44b6 {c['44b6']['videos']} vid/{c['44b6']['divisions']} div, 6bba {c['6bba']['videos']} vid/{c['6bba']['divisions']} div)")
    if "shared_annotation" in summary:
        print(f"  shared annotation: {summary['shared_annotation']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--n-folds", type=int, default=N_FOLDS)
    ap.add_argument("--verify-only", action="store_true", help="re-read GT and verify an existing --out file")
    a = ap.parse_args()

    print(f"reading GT graphs from {a.data_dir}", flush=True)
    divs, info, tables = read_all_divisions(a.data_dir)
    total = sum(divs.values())
    print(f"videos={len(divs)} GT divisions={total} (out-degree>=3 nodes: {info['out_degree_ge3']}, "
          f"GT nodes={info['gt_nodes']}, GT edges={info['gt_edges']}, stems without .zarr: {info['missing_zarr']})")
    if len(divs) != EXPECTED_VIDEOS:
        print(f"WARNING: expected {EXPECTED_VIDEOS} videos, found {len(divs)}")
    if total != EXPECTED_DIVISIONS:
        print(f"WARNING: expected {EXPECTED_DIVISIONS} GT divisions, found {total}")
    links = find_shared_annotation_links(tables)
    groups = leak_groups(divs, links)
    print(f"shared-annotation links (>= {MIN_SHARED_NODES} identical GT nodes or >= {MIN_SHARED_IDS} shared node ids at one "
          f"(dt,dz,dy,dx) offset): {len(links)} "
          f"({ {e: sum(1 for l in links if embryo_of(l['a']) == e) for e in EMBRYOS} }), "
          f"{sum(l['shared_nodes'] for l in links)} shared nodes, {sum(l['shared_divisions'] for l in links)} shared "
          f"divisions -> {len(groups)} fold groups, sizes {[len(g) for g in groups]}")

    if a.verify_only:
        splits = json.loads(a.out.read_text())
        a.n_folds = int(splits.get("meta", {}).get("n_folds", a.n_folds))  # verify against the file's own fold count
    else:
        folds = assign_folds(divs, a.n_folds, a.seed, groups)
        selection, confirmation = selection_confirmation(divs)
        splits = {
            "folds": folds,
            "selection": selection,
            "confirmation": confirmation,
            "divisions_per_video": dict(sorted(divs.items())),
            "summary": build_summary(folds, selection, confirmation, divs, a.n_folds, links, groups),
            "meta": {
                "generator": "tools/make_splits.py",
                "seed": a.seed,
                "n_folds": a.n_folds,
                "division_definition": "GT node with >= 2 outgoing GT edges (== tracksdata dividing_nodes())",
                "reader": "tracksdata IndexedRXGraph.from_geff (same as tools/score_geffs.py)",
                "fold_method": "videos that share GT annotations (overlapping space-time crops: >= "
                               f"{MIN_SHARED_NODES} identical GT nodes or >= {MIN_SHARED_IDS} shared node ids at one "
                               "(dt,dz,dy,dx) offset) are merged into "
                               "one unit (leak_groups) that sits in one fold; units placed greedily then improved by "
                               "best moves/swaps on a weighted squared deviation of videos + divisions per fold "
                               f"(w={W_OVERALL}), per (embryo, fold) (w={W_EMBRYO}) and video counts per (embryo, "
                               f"min(n_div,3)) stratum (w={W_STRATUM}); sha256(seed:...) ordering, no RNG",
                "selection_rule": "6bba stems with odd index (0-based) in sorted 6bba order",
                "confirmation_rule": "6bba even-index stems + all 44b6 stems",
                "leak_groups": groups,
                "shared_annotation_links": links,
                "data_dir": _portable_path(a.data_dir),
            },
        }
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(splits, indent=1) + "\n")
        print(f"wrote {a.out}")

    print_summary(splits["summary"], a.n_folds)
    errors = verify(splits, divs, a.n_folds, links)
    if errors:
        print("VERIFY FAILED:")
        for e in errors:
            print("  -", e)
        return 1
    print(f"VERIFY OK: {len(splits['folds'])} stems each in exactly one of {a.n_folds} folds; selection "
          f"({len(splits['selection'])}) and confirmation ({len(splits['confirmation'])}) partition the set; "
          f"total GT divisions = {total}" + ("" if total == EXPECTED_DIVISIONS else f" (expected {EXPECTED_DIVISIONS})")
          + f"; 0 of {len(links)} shared-annotation links cross folds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
