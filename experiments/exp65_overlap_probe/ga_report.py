"""G-A readout (CONTEXT.md 2026-09-26 08:58 UTC) from a full tools/overlap_reg.py run on the 199 train videos.

    nice -n 19 python tools/overlap_reg.py --data-dir <train> --workers 4 --cache <c> --out <ga_full.json> \
        --check-splits experiments/l2_daughternet/splits.json
    nice -n 19 python experiments/exp65_overlap_probe/ga_report.py <ga_full.json> <train> [run.log]

Adds to the tool's own check: (1) every missed GT-linked pair diagnosed at its GT offset (overlap frames, spatial
fraction vs the pre-registered >= 5 frames / >= 5% floors, raw-voxel equality there, whether the pair had any candidate);
(2) extra 44b6 pairs checked against the GT geff (B's annotated nodes shifted by the found offset that land on A's
annotated nodes, +-1 voxel); (3) 6bba / cross-embryo candidates and rejections; (4) timing. Writes ga_report.json next
to this file.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import overlap_reg as R  # noqa: E402


def gt_nodes(train: Path, stem: str) -> np.ndarray:
    import zarr
    g = zarr.open(str(train / f"{stem}.geff" / "nodes" / "props"), mode="r")
    return np.stack([np.asarray(g[k]["values"][:]).astype(np.int64) for k in ("t", "z", "y", "x")], axis=1)


def gt_match(train, a, b, off, shape_a, tol=1) -> dict:
    """B's GT nodes shifted into A (coord_a = coord_b + off) inside A's crop, and those within tol voxels of an A node."""
    pa, pb = gt_nodes(train, a), gt_nodes(train, b)
    q = pb + np.asarray(off, dtype=np.int64)
    inside = np.all((q >= 0) & (q < np.asarray(shape_a)), axis=1)
    q = q[inside]
    hit = 0
    by_t = {}
    for p in pa:
        by_t.setdefault(int(p[0]), []).append(p[1:])
    for p in q:
        cand = by_t.get(int(p[0]))
        if cand and np.min(np.max(np.abs(np.asarray(cand) - p[1:]), axis=1)) <= tol:
            hit += 1
    return {"b_nodes_in_a_crop": int(len(q)), "matched_a_nodes": int(hit)}


def main():
    full = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    train = Path(sys.argv[2])
    log = Path(sys.argv[3]).read_text(encoding="utf-8", errors="replace") if len(sys.argv) > 3 else ""
    st, chk = full["stats"], full["check"]
    shapes, readers = {}, {}

    def vid(s):
        if s not in readers:
            readers[s], shapes[s] = R.zarr_video(train / f"{s}.zarr")
        return readers[s], shapes[s]

    rej_by_pair = {}
    for r in full["rejected"]:
        rej_by_pair.setdefault((r["a"], r["b"]), []).append(r)
    missing = []
    for m in chk["missing"]:
        a, b, off = m["a"], m["b"], m["gt"]
        ra, sa = vid(a)
        rb, sb = vid(b)
        g = R.overlap_geometry(sa, sb, off)
        v = R.verify_offset(ra, rb, sa, sb, off, min_frames=1, min_spatial=0.0)
        rj = rej_by_pair.get((a, b), [])
        missing.append({"a": a, "b": b, "gt_offset": off, "n_frames": g["n_frames"],
                        "spatial_frac": round(g["spatial_frac"], 5),
                        "below_floor": [k for k, bad in (("frames", g["n_frames"] < R.MIN_FRAMES),
                                                         ("spatial", g["spatial_frac"] < R.MIN_SPATIAL_FRAC)) if bad],
                        "raw_equal_at_gt": v["equal_fracs"],
                        "candidate": [{"offset": r["offset"], "votes": r["votes"], "reason": r.get("reason")}
                                      for r in rj]})
    extra = []
    acc = {(p["a"], p["b"]): p for p in full["pairs"]}
    for key in chk["extra_44b6_pairs"]:
        a, b = key.split("|")
        p = acc[(a, b)]
        extra.append({"a": a, "b": b, "offset": p["offset"], "votes": p["votes"], "n_frames": p["n_frames"],
                      "spatial_frac": p["spatial_frac"], "equal_fracs": p["equal_fracs"],
                      **gt_match(train, a, b, p["offset"], vid(a)[1])})
    found_gt = []
    for p in full["pairs"]:
        if f"{p['a']}|{p['b']}" in chk["extra_44b6_pairs"]:
            continue
        found_gt.append(p)
    reachable = [m for m in missing if not m["below_floor"]]
    n_links = chk["gt_links"]
    cand_6bba = [r for r in full["rejected"] if R.prefix_of(r["a"]) == R.prefix_of(r["b"]) == "6bba"]
    acc_6bba = [p for p in full["pairs"] if R.prefix_of(p["a"]) == "6bba" or R.prefix_of(p["b"]) == "6bba"]
    cross_acc = [p for p in full["pairs"] if R.prefix_of(p["a"]) != R.prefix_of(p["b"])]
    frames_total = 0
    for s in {p.name[:-5] for p in train.glob("*.zarr")}:
        frames_total += vid(s)[1][0]
    rep = {
        "gate": "G-A (CONTEXT.md 2026-09-26 08:58 UTC): >= 60 of the 65 GT-linked 44b6 pairs at the exact GT offset "
                "(+-1 voxel); 0 accepted 6bba pairs; 0 cross-embryo pairs",
        "videos": st["videos"],
        "gt_links_in_splits_json": n_links,
        "gt_links_note": "experiments/l2_daughternet/splits.json meta.shared_annotation_links holds 62 links, not 65",
        "found_at_gt_offset": chk["found_at_gt_offset"],
        "wrong_offset": len(chk["wrong_offset"]),
        "missing": len(missing),
        "missing_below_preregistered_floor": len(missing) - len(reachable),
        "missing_reachable": len(reachable),
        "found_of_reachable": f"{chk['found_at_gt_offset']}/{chk['found_at_gt_offset'] + len(reachable)}",
        "accepted_total": st["accepted"],
        "accepted_by_embryo": chk["accepted_by_embryo"],
        "accepted_6bba_pairs": len(acc_6bba),
        "accepted_cross_embryo_pairs": len(cross_acc),
        "cross_prefix_candidates": st["cross_prefix_candidates"],
        "rejected_6bba_candidates": [{"a": r["a"], "b": r["b"], "offset": r["offset"], "votes": r["votes"],
                                      "n_frames": r.get("n_frames"), "spatial_frac": r.get("spatial_frac"),
                                      "reason": r.get("reason")} for r in cand_6bba],
        "rejected_by_reason": {k: st[k] for k in st if k.startswith("rejected_")},
        "extra_44b6_pairs_without_shared_gt": extra,
        "missing_detail": missing,
        "gate_verdict": {
            "found_ge_60": chk["found_at_gt_offset"] >= 60,
            "zero_6bba": len(acc_6bba) == 0,
            "zero_cross": len(cross_acc) == 0,
        },
        "timing": {"anchor_wall_s_4_workers": st["anchor_wall_s"], "verify_s": st["verify_s"],
                   "mean_per_frame_s_per_worker": st["mean_per_frame_s"], "frames_total": frames_total,
                   "wall_per_frame_s_4_workers": round(st["anchor_wall_s"] / max(1, frames_total), 4)},
        "log_tail": log.strip().splitlines()[-3:] if log else [],
    }
    rep["gate_verdict"]["G_A_pass"] = all(rep["gate_verdict"].values())
    out = HERE / "ga_report.json"
    out.write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: rep[k] for k in ("found_at_gt_offset", "gt_links_in_splits_json", "missing",
                                          "missing_below_preregistered_floor", "found_of_reachable",
                                          "accepted_by_embryo", "accepted_6bba_pairs", "accepted_cross_embryo_pairs",
                                          "gate_verdict", "timing")}, indent=1))
    for m in missing:
        print("MISSING", m["a"], m["b"], m["n_frames"], m["spatial_frac"], m["below_floor"], m["raw_equal_at_gt"],
              m["candidate"])
    for e in extra:
        print("EXTRA", e)


if __name__ == "__main__":
    main()
