"""OVERLAP-CONSENSUS registration (tools/overlap_reg.py): synthetic crops of one noise 'recording' with known offsets.

    python -m pytest tests/test_overlap_reg.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import overlap_reg as R  # noqa: E402

REC = np.random.default_rng(7).integers(50, 4000, size=(14, 20, 70, 70), dtype=np.uint16)


def crop(t0, z0, y0, x0, T, Z, Y, X, rec=REC):
    return np.ascontiguousarray(rec[t0:t0 + T, z0:z0 + Z, y0:y0 + Y, x0:x0 + X])


def video(arr):
    return (lambda t, _a=arr: _a[int(t)]), tuple(arr.shape)


def run(vids: dict, **kw):
    anchors = {n: R.video_anchors(video(a)[0], a.shape[0], backend="sparse") for n, a in vids.items()}
    readers = {n: video(a)[0] for n, a in vids.items()}
    shapes = {n: a.shape for n, a in vids.items()}
    return R.register(anchors, readers, shapes, **kw)


def test_threshold_matches_numpy_percentile():
    rng = np.random.default_rng(1)
    for shape in ((3, 5, 7), (4, 33, 17), (1, 1, 1), (2, 64, 64)):
        a = rng.integers(0, 3000, size=shape, dtype=np.uint16)
        for pct in (99.5, 50.0, 0.0, 100.0, 12.3):
            assert R.frame_threshold(a, pct) == pytest.approx(float(np.percentile(a, pct)), abs=1e-9)


def test_backends_give_identical_anchors():
    f = REC[0]
    h1, z1 = R.frame_anchors(f, backend="sparse")
    h2, z2 = R.frame_anchors(f, backend="scipy")
    assert len(h1) > 20
    assert np.array_equal(z1, z2) and np.array_equal(h1, h2)
    pytest.importorskip("torch")
    h3, z3 = R.frame_anchors(f, backend="torch")
    assert np.array_equal(z1, z3) and np.array_equal(h1, h3)


def test_anchor_rules_and_hash():
    f = np.full((5, 12, 12), 100, dtype=np.uint16)
    f[2, 6, 6] = 900          # interior max -> anchor
    f[0, 6, 2] = 950          # z border and y/x border -> never an anchor
    f[2, 2, 6] = 800          # y too close to the border (< 3)
    h, zyx = R.frame_anchors(f, pct=99.0, backend="sparse")
    assert zyx.tolist() == [[2, 6, 6]]
    patch = np.ascontiguousarray(f[1:4, 4:9, 4:9], dtype="<u2").tobytes()
    import hashlib
    assert int(h[0]) == int.from_bytes(hashlib.blake2b(patch, digest_size=8).digest(), "little")


def test_geometry_and_check_frames():
    g = R.overlap_geometry((10, 16, 48, 48), (9, 16, 50, 52), (3, 2, 10, 12))
    assert g["lo_a"] == [3, 2, 10, 12] and g["hi_a"] == [10, 16, 48, 48] and g["n_frames"] == 7
    assert g["spatial_vox"] == 14 * 38 * 36
    assert g["spatial_frac"] == pytest.approx(14 * 38 * 36 / (16 * 48 * 48))
    assert R.check_frames(7) == [2, 3, 5] or len(R.check_frames(7)) == 3
    assert R.check_frames(2) == [0, 1]
    assert R.check_frames(0) == []


def test_registration_finds_known_offset_and_orientation():
    a = crop(0, 0, 0, 0, 10, 16, 48, 48)
    b = crop(3, 2, 10, 12, 9, 16, 50, 52)
    other = np.random.default_rng(99).integers(50, 4000, size=(10, 16, 48, 48), dtype=np.uint16)
    res = run({"e1_a": a, "e1_b": b, "e1_c": other})
    assert len(res["pairs"]) == 1
    p = res["pairs"][0]
    # voxel at recording g: coord_a = g, coord_b = g - (3,2,10,12) -> offset = coord_a - coord_b
    assert (p["a"], p["b"], p["offset"]) == ("e1_a", "e1_b", [3, 2, 10, 12])
    assert p["votes"] >= 30 and p["equal_fracs"] == [1.0, 1.0, 1.0] and p["n_frames"] == 7
    assert res["stats"]["accepted_cross_prefix"] == 0
    # swapped names -> negated offset
    res2 = run({"e1_z": a, "e1_b": b})
    assert res2["pairs"][0]["a"] == "e1_b" and res2["pairs"][0]["offset"] == [-3, -2, -10, -12]


def test_near_miss_contents_rejected():
    a = crop(0, 0, 0, 0, 10, 16, 48, 48)
    b = crop(3, 2, 10, 12, 9, 16, 50, 52).copy()
    rng = np.random.default_rng(3)
    m = rng.random(b.shape) < 0.01  # 1% of the voxels differ by one grey level
    b[m] += 1
    res = run({"e1_a": a, "e1_b": b})
    assert res["pairs"] == []
    rej = [r for r in res["rejected"] if r["offset"] == [3, 2, 10, 12]]
    assert rej and rej[0]["reason"] == "voxels" and rej[0]["votes"] >= 30
    assert 0.98 < min(rej[0]["equal_fracs"]) < 0.999


def test_too_few_frames_and_small_overlap_rejected():
    a = crop(0, 0, 0, 0, 10, 16, 48, 48)
    b = crop(7, 0, 0, 0, 7, 16, 48, 48)   # 3 shared frames (like a 6bba boundary overlap)
    res = run({"e1_a": a, "e1_b": b})
    assert res["pairs"] == [] and res["stats"]["rejected_frames"] == 1
    c = crop(0, 0, 0, 0, 10, 16, 48, 48)
    d = crop(0, 0, 42, 42, 10, 16, 28, 28)  # 6x6 of the smaller 28x28 -> 4.6% < 5%
    r = R.verify_offset(video(c)[0], video(d)[0], c.shape, d.shape, (0, 0, 42, 42))
    assert not r["ok"] and r["reason"] == "spatial" and r["equal_fracs"] == []
    r = R.verify_offset(video(c)[0], video(d)[0], c.shape, d.shape, (0, 0, 42, 42), min_spatial=0.04)
    assert r["ok"] and r["equal_fracs"] == [1.0, 1.0, 1.0]


def test_prefix_flag_and_cross_prefix_report():
    a = crop(0, 0, 0, 0, 10, 16, 48, 48)
    b = crop(2, 0, 5, 5, 10, 16, 48, 48)
    res = run({"p1_a": a, "p2_b": b}, same_prefix=True)
    assert res["pairs"] == [] and res["rejected"][0]["reason"] == "prefix"
    assert res["stats"]["cross_prefix_candidates"] == 1
    res = run({"p1_a": a, "p2_b": b})
    assert res["pairs"][0]["offset"] == [2, 0, 5, 5] and res["stats"]["accepted_cross_prefix"] == 1


def test_frozen_frame_secondary_votes_do_not_win():
    rec = REC.copy()
    rec[6] = rec[5]  # frozen frame in the recording -> both crops carry it -> extra votes at dt +- 1
    a = crop(0, 0, 0, 0, 10, 16, 48, 48, rec)
    b = crop(3, 2, 10, 12, 9, 16, 50, 52, rec)
    votes, _ = R.vote_offsets({n: R.video_anchors(video(v)[0], v.shape[0], backend="sparse")
                               for n, v in (("e1_a", a), ("e1_b", b))})
    offs = [o for o, _ in votes[("e1_a", "e1_b")]]
    assert offs[0] == (3, 2, 10, 12) and {(2, 2, 10, 12), (4, 2, 10, 12)} <= set(offs)
    res = run({"e1_a": a, "e1_b": b})
    assert len(res["pairs"]) == 1 and res["pairs"][0]["offset"] == [3, 2, 10, 12]


def test_saturated_buckets_skipped():
    flat = np.full((6, 8, 20, 20), 100, dtype=np.uint16)
    flat[:, 4, 10, 10] = 500  # same patch in every frame of every video
    anchors = {f"e_{i}": R.video_anchors(video(flat)[0], 6, backend="sparse") for i in range(3)}
    votes, st = R.vote_offsets(anchors, max_bucket=10)
    assert st["buckets_skipped_large"] == 1 and votes == {}


def test_estimate_and_timing_fields():
    a = crop(0, 0, 0, 0, 3, 16, 48, 48)
    res = R.video_anchors(video(a)[0], 3, backend="sparse")
    assert res["timing"]["frames"] == 3 and res["timing"]["per_frame_s"] > 0
    assert R.estimate_seconds(130, 100, 0.12, workers=4) == pytest.approx(390.0)


def test_register_videos_one_call():
    a = crop(0, 0, 0, 0, 10, 16, 48, 48)
    b = crop(3, 2, 10, 12, 9, 16, 50, 52)
    readers = {"e1_a": video(a)[0], "e1_b": video(b)[0]}
    shapes = {"e1_a": a.shape, "e1_b": b.shape}
    lines = []
    out = R.register_videos(readers, shapes, backend="sparse", log=lines.append)
    assert out["pairs"][0]["offset"] == [3, 2, 10, 12] and len(lines) == 2
    assert out["stats"]["mean_per_frame_s"] > 0


def test_check_against_splits(tmp_path):
    splits = {"meta": {"shared_annotation_links": [
        {"a": "44b6_b", "b": "44b6_a", "offset_tzyx_a_minus_b": [-3, -2, -10, -12]},
        {"a": "44b6_a", "b": "44b6_c", "offset_tzyx_a_minus_b": [1, 1, 1, 1]}]}}
    f = tmp_path / "splits.json"
    f.write_text(json.dumps(splits))
    pairs = [{"a": "44b6_a", "b": "44b6_b", "offset": [3, 2, 11, 12]},
             {"a": "44b6_a", "b": "44b6_d", "offset": [0, 0, 5, 5]},
             {"a": "44b6_a", "b": "6bba_x", "offset": [0, 0, 5, 5]}]
    c = R.check_against_splits(pairs, f)
    assert c["found_at_gt_offset"] == 1 and len(c["missing"]) == 1
    assert c["accepted_by_embryo"] == {"44b6": 2, "cross": 1} and c["extra_44b6_pairs"] == ["44b6_a|44b6_d"]
