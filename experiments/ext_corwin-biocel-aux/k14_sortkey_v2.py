# ---------------------------------------------------------------------------
# GENERE PAR scripts/frontier/cells/_build_shard_variant.py -- NE PAS EDITER.
# Variante SHARDEE de cell_06.py (RUNTIME-TIR / ITEM 0 d ARTILLERIE).
# BIOHUB_POSTPROC_SHARD non defini => comportement HISTORIQUE au caractere pres
# (aucune des 5 substitutions ne change alors le flux de controle).
# ---------------------------------------------------------------------------
import os as _sh_os


def _sh_slice():
    """(k, n) depuis BIOHUB_POSTPROC_SHARD="k::n", ou (0, 1) si non defini."""
    raw = _sh_os.environ.get("BIOHUB_POSTPROC_SHARD", "").strip()
    if not raw:
        return 0, 1
    k, _, n = raw.partition("::")
    k, n = int(k), int(n)
    if not (n >= 1 and 0 <= k < n):
        raise ValueError(f"BIOHUB_POSTPROC_SHARD invalide: {raw!r}")
    return k, n


_SH_K, _SH_N = _sh_slice()
_SH_SUFFIX = "" if _SH_N == 1 else f"_shard{_SH_K}"


def _sh_path(p):
    """Suffixe le nom de fichier, sans toucher le repertoire ni l extension."""
    if not _SH_SUFFIX:
        return p
    return p.with_name(p.stem + _SH_SUFFIX + p.suffix)


import tracksdata as td
import numpy as np
import blosc2
from scipy.optimize import linear_sum_assignment


def _ilp2_ilp_assign(cost, big, unlink):
    """The FULLTIGHT formulation: a linear assignment with abstention, solved
    exactly. Variables exist only for ADMISSIBLE pairs (cost < big); an
    unmatched SOURCE pays `unlink`, an unclaimed target is free.

    Minimising `sum (cost_ij - unlink) x_ij` over a matching is the same
    optimum, because total = sum(chosen) + unlink*(ns - |M|) and the constant
    unlink*ns drops.
    """
    import time as _time
    import numpy as _np
    from scipy.optimize import milp as _milp
    from scipy.optimize import LinearConstraint as _LC
    from scipy.sparse import coo_matrix as _coo
    _t_enter = _time.perf_counter()

    c = _np.asarray(cost, dtype=_np.float64)
    if not _np.isfinite(big):
        raise ValueError("ILP2: big is not finite (%r)" % (big,))
    # THE FINITENESS REFUSAL, ON THE WHOLE MATRIX, BEFORE THE RANGE TEST.
    # `NaN < big` is FALSE, so a NaN never reaches the admissible set: testing
    # only admissible cells would DROP a poisoned score instead of catching it.
    if not _np.all(_np.isfinite(c)):
        raise ValueError("ILP2: %d cost cells are NaN or inf; refused before "
                         "any range test" % int((~_np.isfinite(c)).sum()))
    if not _np.isfinite(unlink):
        raise ValueError("ILP2: the abstention price is not finite (%r)" % (unlink,))

    ns, nt = c.shape
    adm = _np.argwhere(c < big)
    info = {"n_vars": 0, "status": "empty", "objective": 0.0,
            "solve_s": 0.0, "build_s": 0.0}
    if adm.shape[0] == 0:
        return set(), info
    vals = c[adm[:, 0], adm[:, 1]]
    base = float(unlink)
    nx = int(adm.shape[0])
    obj = vals - base

    rows, cols, data, lb, ub = [], [], [], [], []
    nc = 0
    by_row, by_col = {}, {}
    for k in range(nx):
        by_row.setdefault(int(adm[k, 0]), []).append(k)
        by_col.setdefault(int(adm[k, 1]), []).append(k)
    for _i, ks in by_row.items():
        for k in ks:
            rows.append(nc); cols.append(k); data.append(1.0)
        lb.append(-_np.inf); ub.append(1.0); nc += 1
    for _j, ks in by_col.items():
        for k in ks:
            rows.append(nc); cols.append(k); data.append(1.0)
        lb.append(-_np.inf); ub.append(1.0); nc += 1

    A = _coo((data, (rows, cols)), shape=(nc, nx)).tocsr()
    _t_solve = _time.perf_counter()
    res = _milp(c=obj, constraints=_LC(A, _np.asarray(lb), _np.asarray(ub)),
                integrality=_np.ones(nx),
                bounds=(_np.zeros(nx), _np.ones(nx)))
    info["solve_s"] = float(_time.perf_counter() - _t_solve)
    info["build_s"] = float(_t_solve - _t_enter)
    info["status"] = str(getattr(res, "message", ""))[:80]
    if not getattr(res, "success", False) or res.x is None:
        raise RuntimeError("ILP2: milp did not solve (%s)" % info["status"])
    take = _np.asarray(res.x) > 0.5
    edges = set()
    for k in range(nx):
        if take[k]:
            edges.add((int(adm[k, 0]), int(adm[k, 1])))
    info["n_vars"] = nx
    info["objective"] = float(obj[take].sum())
    return edges, info



def _coll_node_translation(ids_by_t, position_um, t,
                           radius_um=10.0, min_vectors=8):
    """COLL-NODE: the frame's collective translation from the NODE SET.

    For every node at t, its nearest node at t+1 within radius_um; the MEDIAN
    of those offsets is the frame's translation. Returns None -- DISARMED, not
    zero -- on the last frame or under min_vectors vectors.
    """
    src = ids_by_t.get(t)
    tgt = ids_by_t.get(t + 1)
    if not src or not tgt:
        return None
    P = np.asarray([position_um[n] for n in tgt], dtype=np.float64)
    if P.size == 0:
        return None
    off = []
    for n in src:
        p = position_um[n]
        v = P - p
        r = np.sqrt((v * v).sum(axis=1))
        k = int(np.argmin(r))
        if float(r[k]) <= radius_um:
            off.append(v[k])
    if len(off) < min_vectors:
        return None
    T = np.median(np.asarray(off, dtype=np.float64), axis=0)
    if not np.all(np.isfinite(T)):
        return None
    return T

from scipy.spatial import cKDTree

SUBMISSION_COLUMNS = ["dataset", "row_type", "node_id", "t", "z", "y", "x", "source_id", "target_id"]
CSV_COLUMNS = ["id", *SUBMISSION_COLUMNS]
VOXEL_SCALE_UM = (1.625, 0.40625, 0.40625)


def graph_from_geff(path: Path):
    graph = td.graph.IndexedRXGraph.from_geff(path)
    return graph[0] if isinstance(graph, tuple) else graph


def edge_distance_um(source: dict[str, object], target: dict[str, object]) -> float:
    dz = (float(source["z"]) - float(target["z"])) * VOXEL_SCALE_UM[0]
    dy = (float(source["y"]) - float(target["y"])) * VOXEL_SCALE_UM[1]
    dx = (float(source["x"]) - float(target["x"])) * VOXEL_SCALE_UM[2]
    return math.sqrt(dz * dz + dy * dy + dx * dx)


def point_distance_um(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    dz = (a[0] - b[0]) * VOXEL_SCALE_UM[0]
    dy = (a[1] - b[1]) * VOXEL_SCALE_UM[1]
    dx = (a[2] - b[2]) * VOXEL_SCALE_UM[2]
    return math.sqrt(dz * dz + dy * dy + dx * dx)


def node_point(node: dict[str, object]) -> tuple[float, float, float]:
    return (float(node["z"]), float(node["y"]), float(node["x"]))


def edge_sort_key(edge: dict[str, object]) -> tuple[float, float]:
    prob = edge.get("edge_prob")
    prob_value = float(prob) if prob is not None else 0.0
    return prob_value, -float(edge["distance_um"])


def _next_node_id(nodes_by_id: dict[int, dict[str, object]]) -> int:
    return max(nodes_by_id) + 1 if nodes_by_id else 1



def read_test_frame(dataset: str, t: int, frame_cache: dict[int, np.ndarray]) -> np.ndarray:
    if t in frame_cache:
        return frame_cache[t]
    zarr_path = TEST_DIR / f"{dataset}.zarr"
    meta = json.loads((zarr_path / "0" / "zarr.json").read_text())
    shape = tuple(int(v) for v in meta["shape"])
    dtype = np.dtype(meta["data_type"])
    frame_shape = shape[1:]
    chunk_path = zarr_path / "0" / "c" / str(t) / "0" / "0" / "0"
    try:
        raw = chunk_path.read_bytes()
        arr = np.frombuffer(blosc2.decompress(raw), dtype=dtype)
        if arr.size == int(np.prod(frame_shape)):
            frame = arr.reshape(frame_shape).copy()
            frame_cache[t] = frame
            return frame
    except Exception:
        pass
    import zarr
    frame = np.asarray(zarr.open(zarr_path / "0", mode="r")[t])
    frame_cache[t] = frame
    return frame


def refine_synthetic_midpoint(
    dataset: str | None,
    t: int,
    midpoint: tuple[float, float, float],
    frame_cache: dict[int, np.ndarray],
    stats: dict[str, int],
) -> tuple[float, float, float]:
    if not GAP_REFINE_SYNTHETIC or dataset is None:
        return midpoint
    try:
        frame = read_test_frame(dataset, t, frame_cache)
        z, y, x = [int(round(v)) for v in midpoint]
        z0 = max(0, z - GAP_REFINE_WIN_Z)
        z1 = min(frame.shape[0], z + GAP_REFINE_WIN_Z + 1)
        y0 = max(0, y - GAP_REFINE_WIN_YX)
        y1 = min(frame.shape[1], y + GAP_REFINE_WIN_YX + 1)
        x0 = max(0, x - GAP_REFINE_WIN_YX)
        x1 = min(frame.shape[2], x + GAP_REFINE_WIN_YX + 1)
        patch = frame[z0:z1, y0:y1, x0:x1].astype(np.float64)
        if patch.size == 0:
            stats["gap_refine_failed"] += 1
            return midpoint
        baseline = float(np.percentile(patch, 20.0))
        weights = np.maximum(patch - baseline, 0.0)
        total = float(weights.sum())
        if total <= 0:
            stats["gap_refine_failed"] += 1
            return midpoint
        zz = np.arange(z0, z1, dtype=np.float64)[:, None, None]
        yy = np.arange(y0, y1, dtype=np.float64)[None, :, None]
        xx = np.arange(x0, x1, dtype=np.float64)[None, None, :]
        refined = (
            float((weights * zz).sum() / total),
            float((weights * yy).sum() / total),
            float((weights * xx).sum() / total),
        )
        if point_distance_um(refined, midpoint) > GAP_REFINE_MAX_SHIFT_UM:
            stats["gap_refine_rejected_shift"] += 1
            return midpoint
        stats["gap_refined_synthetic"] += 1
        return refined
    except Exception:
        stats["gap_refine_failed"] += 1
        return midpoint



def _dc_pool_frame_xy(volume: np.ndarray, factor: int) -> np.ndarray:
    if factor <= 1:
        return volume.astype(np.float32, copy=False)
    z, y, x = volume.shape
    y2 = (y // factor) * factor
    x2 = (x // factor) * factor
    cropped = volume[:, :y2, :x2].astype(np.float32, copy=False)
    return cropped.reshape(z, y2 // factor, factor, x2 // factor, factor).mean(axis=(2, 4))


def _dc_normalize_dynamic_range(volume: np.ndarray, cfg: object) -> np.ndarray:
    vol = np.asarray(volume, dtype=np.float32)
    lo = float(np.percentile(vol, float(getattr(cfg, "norm_lo_pct", 50.0))))
    hi = float(np.percentile(vol, float(getattr(cfg, "norm_hi_pct", 99.5))))
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        return np.zeros_like(vol, dtype=np.float32)
    ratio = (vol - lo) / (hi - lo)
    return np.clip(
        ratio,
        float(getattr(cfg, "norm_clip_lo", -0.5)),
        float(getattr(cfg, "norm_clip_hi", 6.0)),
    ).astype(np.float32)


def _dc_manifest_weight_paths(manifest_path: Path) -> list[Path]:
    if not manifest_path.exists():
        return []
    try:
        manifest = json.loads(manifest_path.read_text())
    except Exception as exc:
        print("Could not read DeepCenter manifest:", manifest_path, type(exc).__name__, exc)
        return []
    root = manifest_path.parent
    sections: list[dict[str, object]] = []
    for section in [
        manifest.get("model", {}),
        manifest.get("models", {}).get("full_frame_center", {}) if isinstance(manifest.get("models", {}), dict) else {},
        manifest.get("full_frame_center", {}),
    ]:
        if isinstance(section, dict):
            sections.append(section)
    candidates: list[Path] = []
    for section in sections:
        for key in ("weight_path", "path"):
            rel = section.get(key)
            if isinstance(rel, str) and rel:
                candidates.append(root / rel)
        for key in ("last_checkpoint", "best_checkpoint"):
            item = section.get(key)
            if isinstance(item, dict):
                rel = item.get("path")
                if isinstance(rel, str) and rel:
                    candidates.append(root / rel)
    for name in ("checkpoint_last.pt", "best.pt", "last.pt"):
        candidates.append(root / "weights" / "full_frame_center" / name)
        candidates.append(root / name)
    candidates.append(root / DEEPCENTER_RELATIVE)
    return candidates


def _dc_checkpoint_candidates() -> list[Path]:
    candidates: list[Path] = []
    explicit = os.environ.get("BIOHUB_DEEPCENTER_CHECKPOINT", DEEPCENTER_CHECKPOINT_DEFAULT).strip()
    if explicit:
        candidates.append(Path(explicit))
    manifest_explicit = os.environ.get("BIOHUB_DEEPCENTER_MANIFEST", DEEPCENTER_MANIFEST_DEFAULT).strip()
    if manifest_explicit:
        candidates.extend(_dc_manifest_weight_paths(Path(manifest_explicit)))

    input_root = Path("/kaggle/input")
    preferred_dirs = [
        Path("/kaggle/input/biohub-deepcenter-unet3d-center-prior-v1"),
        Path("/kaggle/input/datasets/pilkwang/biohub-deepcenter-unet3d-center-prior-v1"),
    ]
    for directory in preferred_dirs:
        candidates.extend(_dc_manifest_weight_paths(directory / "ARTIFACT_MANIFEST.json"))
        for name in ("checkpoint_last.pt", "best.pt", "last.pt"):
            candidates.append(directory / "weights" / "full_frame_center" / name)
            candidates.append(directory / name)
    if input_root.exists():
        for name in ("checkpoint_last.pt", "best.pt", "last.pt"):
            candidates.extend(sorted(input_root.glob(f"**/full_frame_center/**/{name}")))

    seen: set[Path] = set()
    out: list[Path] = []
    for path in candidates:
        path = path.expanduser()
        try:
            key = path.resolve() if path.exists() else path
        except Exception:
            key = path
        if key in seen:
            continue
        seen.add(key)
        out.append(path)
    return out


try:
    import torch
except Exception as _dc_torch_error:
    torch = None


if torch is not None:
    class _DCConvBlock3d(torch.nn.Module):
        def __init__(self, in_channels: int, out_channels: int) -> None:
            super().__init__()
            groups = min(8, out_channels)
            self.block = torch.nn.Sequential(
                torch.nn.Conv3d(in_channels, out_channels, 3, padding=1, bias=False),
                torch.nn.GroupNorm(groups, out_channels),
                torch.nn.SiLU(inplace=True),
                torch.nn.Conv3d(out_channels, out_channels, 3, padding=1, bias=False),
                torch.nn.GroupNorm(groups, out_channels),
                torch.nn.SiLU(inplace=True),
            )

        def forward(self, x):
            return self.block(x)


    class _DCDeepCenterUNet3D(torch.nn.Module):
        def __init__(self, in_channels: int = 1, base_channels: int = 24) -> None:
            super().__init__()
            c = int(base_channels)
            self.enc1 = _DCConvBlock3d(in_channels, c)
            self.down1 = torch.nn.MaxPool3d(2, 2)
            self.enc2 = _DCConvBlock3d(c, c * 2)
            self.down2 = torch.nn.MaxPool3d(2, 2)
            self.enc3 = _DCConvBlock3d(c * 2, c * 4)
            self.down3 = torch.nn.MaxPool3d(2, 2)
            self.bottleneck = _DCConvBlock3d(c * 4, c * 8)
            self.up3 = torch.nn.ConvTranspose3d(c * 8, c * 4, 2, 2)
            self.dec3 = _DCConvBlock3d(c * 8, c * 4)
            self.up2 = torch.nn.ConvTranspose3d(c * 4, c * 2, 2, 2)
            self.dec2 = _DCConvBlock3d(c * 4, c * 2)
            self.up1 = torch.nn.ConvTranspose3d(c * 2, c, 2, 2)
            self.dec1 = _DCConvBlock3d(c * 2, c)
            self.head = torch.nn.Conv3d(c, 1, 1)

        def forward(self, x):
            e1 = self.enc1(x)
            e2 = self.enc2(self.down1(e1))
            e3 = self.enc3(self.down2(e2))
            b = self.bottleneck(self.down3(e3))
            d3 = self.dec3(torch.cat([self.up3(b), e3], dim=1))
            d2 = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
            d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))
            return self.head(d1)
else:
    _DCConvBlock3d = None
    _DCDeepCenterUNet3D = None

def load_deepcenter_veto_detector() -> dict[str, object] | None:
    if not USE_DEEPCENTER_VETO:
        print("DeepCenter add-only repair gate disabled by configuration.")
        return None
    if torch is None:
        if REQUIRE_DEEPCENTER_VETO:
            raise ImportError("torch is required for DeepCenter add-only repair gate")
        print("DeepCenter add-only repair gate skipped because torch is unavailable.")
        return None
    from types import SimpleNamespace

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    load_errors: list[str] = []
    for checkpoint_path in _dc_checkpoint_candidates():
        if not checkpoint_path.exists():
            continue
        try:
            print("Trying DeepCenter add-only gate checkpoint:", checkpoint_path)
            checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
            if not isinstance(checkpoint, dict) or "model_state" not in checkpoint:
                raise ValueError("checkpoint has no model_state")
            checkpoint_epoch = int(checkpoint.get("epoch", -1))
            if DEEPCENTER_EXPECTED_EPOCH > 0 and checkpoint_epoch != DEEPCENTER_EXPECTED_EPOCH:
                raise ValueError(
                    f"expected DeepCenter epoch {DEEPCENTER_EXPECTED_EPOCH}, got {checkpoint_epoch}"
                )
            cfg = SimpleNamespace(**checkpoint.get("config", {}))
            model = _DCDeepCenterUNet3D(base_channels=int(getattr(cfg, "base_channels", 24)))
            model.load_state_dict(checkpoint["model_state"])
            model.to(device)
            model.eval()
            print("Loaded DeepCenter add-only gate checkpoint:", checkpoint_path)
            print("DeepCenter checkpoint epoch:", checkpoint.get("epoch"), "best_score:", checkpoint.get("best_score"))
            return {
                "model": model,
                "cfg": cfg,
                "device": device,
                "path": checkpoint_path,
                "torch": torch,
            }
        except Exception as exc:
            load_errors.append(f"{checkpoint_path}: {type(exc).__name__}: {exc}")
            print("Skipping incompatible DeepCenter checkpoint:", checkpoint_path, "|", type(exc).__name__, exc)
    message = "No usable DeepCenter checkpoint found for add-only repair gate."
    if REQUIRE_DEEPCENTER_VETO:
        checked = "\n".join(str(p) for p in _dc_checkpoint_candidates()[:80])
        errors = "\n".join(load_errors[-20:])
        raise FileNotFoundError(message + "\nChecked:\n" + checked + ("\nLoad errors:\n" + errors if errors else ""))
    print(message)
    return None


def _dc_cache_trim(cache: dict[tuple[str, int], np.ndarray]) -> None:
    limit = max(1, int(DEEPCENTER_SCORE_CACHE_MAX_FRAMES))
    while len(cache) > limit:
        cache.pop(next(iter(cache)))


def deepcenter_heatmap_for_frame(
    dataset: str,
    t: int,
    detector_bundle: dict[str, object] | None,
    frame_cache: dict[int, np.ndarray],
    heatmap_cache: dict[tuple[str, int], np.ndarray],
) -> np.ndarray | None:
    if detector_bundle is None:
        return None
    key = (dataset, int(t))
    cached = heatmap_cache.get(key)
    if cached is not None:
        return cached
    model = detector_bundle["model"]
    cfg = detector_bundle["cfg"]
    device = detector_bundle["device"]
    torch_mod = detector_bundle["torch"]
    pool_factor = int(getattr(cfg, "pool_factor", 4))
    volume = read_test_frame(dataset, int(t), frame_cache)
    pooled = _dc_pool_frame_xy(volume, pool_factor)
    image = _dc_normalize_dynamic_range(pooled, cfg)
    with torch_mod.no_grad():
        tensor = torch_mod.from_numpy(image[None, None, ...]).to(device=device, dtype=torch_mod.float32)
        heatmap = torch_mod.sigmoid(model(tensor))[0, 0].detach().cpu().numpy().astype(np.float32, copy=False)
    heatmap_cache[key] = heatmap
    _dc_cache_trim(heatmap_cache)
    return heatmap


def deepcenter_score_point(
    dataset: str | None,
    t: int,
    point: tuple[float, float, float],
    detector_bundle: dict[str, object] | None,
    frame_cache: dict[int, np.ndarray],
    heatmap_cache: dict[tuple[str, int], np.ndarray],
) -> float | None:
    if not USE_DEEPCENTER_VETO or detector_bundle is None or dataset is None:
        return None
    heatmap = deepcenter_heatmap_for_frame(dataset, int(t), detector_bundle, frame_cache, heatmap_cache)
    if heatmap is None or heatmap.size == 0:
        return None
    cfg = detector_bundle["cfg"]
    pool_factor = int(getattr(cfg, "pool_factor", 4))
    z = int(round(float(point[0])))
    y = int(round(float(point[1]) / max(pool_factor, 1)))
    x = int(round(float(point[2]) / max(pool_factor, 1)))
    z0, z1 = max(0, z - DEEPCENTER_SCORE_WIN_Z), min(heatmap.shape[0], z + DEEPCENTER_SCORE_WIN_Z + 1)
    y0, y1 = max(0, y - DEEPCENTER_SCORE_WIN_YX), min(heatmap.shape[1], y + DEEPCENTER_SCORE_WIN_YX + 1)
    x0, x1 = max(0, x - DEEPCENTER_SCORE_WIN_YX), min(heatmap.shape[2], x + DEEPCENTER_SCORE_WIN_YX + 1)
    patch = heatmap[z0:z1, y0:y1, x0:x1]
    if patch.size == 0:
        return None
    score = float(np.max(patch))
    return score if np.isfinite(score) else None


def deepcenter_accept_repair_point(
    dataset: str | None,
    t: int,
    point: tuple[float, float, float],
    detector_bundle: dict[str, object] | None,
    frame_cache: dict[int, np.ndarray],
    heatmap_cache: dict[tuple[str, int], np.ndarray],
    stats: dict[str, int],
    prefix: str,
    threshold: float,
) -> bool:
    if not USE_DEEPCENTER_VETO:
        return True
    if detector_bundle is None or dataset is None:
        stats[f"deepcenter_{prefix}_missing"] += 1
        return True
    stats[f"deepcenter_{prefix}_checked"] += 1
    score = deepcenter_score_point(dataset, int(t), point, detector_bundle, frame_cache, heatmap_cache)
    if score is None:
        stats[f"deepcenter_{prefix}_missing"] += 1
        return True
    if score < float(threshold):
        stats[f"deepcenter_{prefix}_rejected"] += 1
        return False
    stats[f"deepcenter_{prefix}_accepted"] += 1
    return True

def _position_um(node: dict[str, object]) -> np.ndarray:
    return np.array(
        [float(node["z"]) * VOXEL_SCALE_UM[0], float(node["y"]) * VOXEL_SCALE_UM[1], float(node["x"]) * VOXEL_SCALE_UM[2]],
        dtype=np.float64,
    )


def motion_relink_edges(
    nodes_by_id: dict[int, dict[str, object]],
    stats: dict[str, int],
    learned_edge_probs: dict[tuple[int, int], float] | None = None,
) -> list[dict[str, object]]:
    if not OUTPUT_MOTION_RELINK or not nodes_by_id:
        return []

    learned_edge_probs = learned_edge_probs or {}

    def learned_prob(source_id: int, target_id: int) -> float:
        value = learned_edge_probs.get((source_id, target_id), 0.0)
        try:
            value = float(value)
        except (TypeError, ValueError):
            return 0.0
        if not np.isfinite(value):
            return 0.0
        if value < 0.0 or value > 1.0:
            value = 1.0 / (1.0 + math.exp(-max(-20.0, min(20.0, value))))
        return float(np.clip(value, 0.0, 1.0))

    ids_by_t: dict[int, list[int]] = {}
    for node_id, node in nodes_by_id.items():
        ids_by_t.setdefault(int(node["t"]), []).append(node_id)
    for ids in ids_by_t.values():
        ids.sort()

    frame_sizes = [len(ids) for ids in ids_by_t.values()]
    if frame_sizes and max(frame_sizes) > MOTION_RELINK_MAX_FRAME_NODES:
        stats["motion_relink_skipped_large_frame"] = 1
        return []

    position_um = {node_id: _position_um(node) for node_id, node in nodes_by_id.items()}
    predecessor_position_um: dict[int, np.ndarray] = {}
    selected_edges: list[dict[str, object]] = []

    def assign_pass(
        source_ids: list[int],
        target_ids: list[int],
        gate_um: float,
    ) -> list[tuple[int, int, float, float, float]]:
        if not source_ids or not target_ids:
            return []
        big = gate_um * 1000.0 + 1.0
        cost = np.full((len(source_ids), len(target_ids)), big, dtype=np.float64)
        raw_dist = np.full_like(cost, np.inf)
        motion_dist = np.full_like(cost, np.inf)
        prob_matrix = np.zeros_like(cost)
        for i, source_id in enumerate(source_ids):
            source_pos = position_um[source_id]
            prev_pos = predecessor_position_um.get(source_id)
            if prev_pos is None:
                predicted = source_pos
            else:
                predicted = source_pos + MOTION_RELINK_VELOCITY_WEIGHT * (source_pos - prev_pos)
            for j, target_id in enumerate(target_ids):
                target_pos = position_um[target_id]
                raw = float(np.linalg.norm(target_pos - source_pos))
                if raw > gate_um:
                    continue
                motion = float(np.linalg.norm(target_pos - predicted))
                prob = learned_prob(source_id, target_id)
                raw_dist[i, j] = raw
                motion_dist[i, j] = motion
                prob_matrix[i, j] = prob
                cost[i, j] = motion + 0.05 * raw - MOTION_RELINK_LEARNED_BONUS * prob
        # --- ENG/DIVGATE : ILP-2 (v5-SLIM) AT THE ASSIGNMENT ANCHOR --------
        # BIOCEL_ILP2 unset -> this block does nothing and the function below is
        # the deployed code line for line. Armed with FULLTIGHT it re-decides
        # the TIGHT pass on the cost matrix as it stands.
        #
        # ATOMIC FALLBACK: the matrices are restored from copies taken at entry
        # if anything raises, so a late exception leaves the world
        # byte-identical; every measurement counter accumulates in a LOCAL dict
        # merged only on the success path, so a failed frame publishes no
        # number. Only the error itself is published.
        _i2_mode = os.environ.get("BIOCEL_ILP2", "").strip().upper()
        if _i2_mode == "FULLTIGHT" and cost.size:
            _i2_cost0 = cost.copy()
            _i2_motion0 = motion_dist.copy()
            _i2_out = {}
            try:
                _i2_coll = os.environ.get("BIOCEL_ILP2_COLL", "").strip() == "1"
                _i2_unl = float(os.environ.get("BIOCEL_ILP2_UNLINK", "nan"))
                _i2_tight = abs(float(gate_um) - float(MOTION_RELINK_TIGHT_UM)) < 1e-9
                _i2_in0 = cost < big
                _i2_ns, _i2_nt = cost.shape

                # ---- COLL-NODE: the frame's collective translation ----------
                # Computed over EVERY node at t at a FIXED 10 um radius, because
                # the frame has ONE translation and a pass-local one would give
                # the tight and relaxed passes two different answers. Disarmed
                # (None) on the last frame or under 8 vectors -- and disarmed is
                # NOT zero, so the deployed cost is left alone.
                # COMPUTE APART, VALIDATE WHOLE, INSTALL ONCE.
                if _i2_coll:
                    _i2_t = int(nodes_by_id[source_ids[0]]["t"])
                    _i2_T = _coll_node_translation(ids_by_t, position_um, _i2_t)
                    if _i2_T is None:
                        _i2_out["ilp2_coll_disarmed_frames"] = (
                            stats.get("ilp2_coll_disarmed_frames", 0) + 1)
                    else:
                        _i2_cost_n = cost.copy()
                        _i2_motion_n = motion_dist.copy()
                        for _i2_i in range(_i2_ns):
                            _i2_p = position_um[source_ids[_i2_i]] + _i2_T
                            for _i2_j in np.nonzero(_i2_in0[_i2_i])[0]:
                                _i2_j = int(_i2_j)
                                _i2_m = float(np.linalg.norm(
                                    position_um[target_ids[_i2_j]] - _i2_p))
                                _i2_motion_n[_i2_i, _i2_j] = _i2_m
                                _i2_cost_n[_i2_i, _i2_j] = (
                                    _i2_m + 0.05 * raw_dist[_i2_i, _i2_j]
                                    - MOTION_RELINK_LEARNED_BONUS
                                    * prob_matrix[_i2_i, _i2_j])
                        if not np.all(np.isfinite(_i2_cost_n)):
                            raise ValueError(
                                "ILP2: COLL produced %d non-finite cost cells; "
                                "refused before any range test"
                                % int((~np.isfinite(_i2_cost_n)).sum()))
                        if not np.array_equal(_i2_cost_n < big, _i2_in0):
                            raise RuntimeError("ILP2: COLL moved the gate")
                        cost[:, :] = _i2_cost_n
                        motion_dist[:, :] = _i2_motion_n
                        _i2_out["ilp2_coll_tz_milli"] = int(round(1000.0 * float(_i2_T[0])))
                        _i2_out["ilp2_coll_ty_milli"] = int(round(1000.0 * float(_i2_T[1])))
                        _i2_out["ilp2_coll_tx_milli"] = int(round(1000.0 * float(_i2_T[2])))
                        _i2_out["ilp2_coll_frames"] = stats.get("ilp2_coll_frames", 0) + 1

                # ---- the TIGHT pass, cardinality freed, abstention priced ---
                # The RELAXED pass falls through to the deployed solve: its
                # cardinality is forced, and a forced-cardinality assignment IS
                # the deployed solve -- measured identical on 764/764 frames.
                if _i2_tight and np.isfinite(_i2_unl):
                    _i2_set, _i2_inf = _ilp2_ilp_assign(cost, big, float(_i2_unl))
                    _i2_rows = []
                    for (_i2_a, _i2_b) in sorted(_i2_set):
                        _i2_rows.append((
                            source_ids[int(_i2_a)], target_ids[int(_i2_b)],
                            float(raw_dist[_i2_a, _i2_b]),
                            float(motion_dist[_i2_a, _i2_b]),
                            float(prob_matrix[_i2_a, _i2_b])))
                    _i2_out["ilp2_solves"] = stats.get("ilp2_solves", 0) + 1
                    _i2_out["ilp2_edges"] = stats.get("ilp2_edges", 0) + len(_i2_rows)
                    _i2_out["ilp2_solve_ms"] = (stats.get("ilp2_solve_ms", 0)
                                                + int(round(1000.0 * _i2_inf.get("solve_s", 0.0))))
                    _i2_out["ilp2_build_ms"] = (stats.get("ilp2_build_ms", 0)
                                                + int(round(1000.0 * _i2_inf.get("build_s", 0.0))))
                    _i2_out["ilp2_vars"] = (stats.get("ilp2_vars", 0)
                                            + int(_i2_inf.get("n_vars", 0)))
                    stats.update(_i2_out)
                    return _i2_rows
                stats.update(_i2_out)
            except BaseException as _i2_e:                       # noqa: BLE001
                cost[:, :] = _i2_cost0
                motion_dist[:, :] = _i2_motion0
                stats["ilp2_error"] = "%s: %s" % (type(_i2_e).__name__,
                                                  str(_i2_e)[:160])
                stats["ilp2_fallback_frames"] = (
                    stats.get("ilp2_fallback_frames", 0) + 1)
        row_ind, col_ind = linear_sum_assignment(cost)
        matches: list[tuple[int, int, float, float, float]] = []
        for r, c in zip(row_ind, col_ind):
            if cost[r, c] >= big:
                continue
            matches.append((
                source_ids[int(r)],
                target_ids[int(c)],
                float(raw_dist[r, c]),
                float(motion_dist[r, c]),
                float(prob_matrix[r, c]),
            ))
        return matches

    times = sorted(ids_by_t)
    for t in times:
        source_ids = ids_by_t.get(t, [])
        target_ids = ids_by_t.get(t + 1, [])
        if not source_ids or not target_ids:
            continue
        unmatched_sources = set(source_ids)
        unmatched_targets = set(target_ids)
        frame_matches: list[tuple[int, int, float, float, str, float]] = []
        for pass_name, gate_um in (("tight", MOTION_RELINK_TIGHT_UM), ("relaxed", MOTION_RELINK_RELAXED_UM)):
            pass_sources = [node_id for node_id in source_ids if node_id in unmatched_sources]
            pass_targets = [node_id for node_id in target_ids if node_id in unmatched_targets]
            matches = assign_pass(pass_sources, pass_targets, gate_um)
            for source_id, target_id, raw, motion, prob in matches:
                if source_id not in unmatched_sources or target_id not in unmatched_targets:
                    continue
                unmatched_sources.remove(source_id)
                unmatched_targets.remove(target_id)
                frame_matches.append((source_id, target_id, raw, motion, pass_name, prob))
                if pass_name == "tight":
                    stats["motion_relink_tight_edges"] += 1
                else:
                    stats["motion_relink_relaxed_edges"] += 1
        for source_id, target_id, raw, motion, pass_name, prob in frame_matches:
            selected_edges.append({
                "source_id": source_id,
                "target_id": target_id,
                "edge_prob": prob,
                "distance_um": raw,
                "motion_distance_um": motion,
                "motion_relinked": 1,
                "motion_pass": pass_name,
            })
            predecessor_position_um[target_id] = position_um[source_id]
        stats["motion_relink_frames"] += 1

    stats["motion_relink_edges"] = len(selected_edges)
    return selected_edges

def close_single_frame_gaps(
    nodes_by_id: dict[int, dict[str, object]],
    edges: list[dict[str, object]],
    stats: dict[str, int],
    dataset: str | None = None,
    deepcenter_bundle: dict[str, object] | None = None,
    frame_cache: dict[int, np.ndarray] | None = None,
    deepcenter_cache: dict[tuple[str, int], np.ndarray] | None = None,
) -> tuple[dict[int, dict[str, object]], list[dict[str, object]]]:
    if not OUTPUT_GAP_CLOSE or GAP_CLOSE_MAX_GAP < 1 or not edges:
        return nodes_by_id, edges

    outgoing = {int(edge["source_id"]) for edge in edges}
    incoming = {int(edge["target_id"]) for edge in edges}
    incident = outgoing | incoming

    ends_by_t: dict[int, list[int]] = {}
    starts_by_t: dict[int, list[int]] = {}
    isolated_by_t: dict[int, list[int]] = {}
    all_ids_by_t: dict[int, list[int]] = {}
    for node_id, node in nodes_by_id.items():
        t = int(node["t"])
        all_ids_by_t.setdefault(t, []).append(node_id)
        if node_id not in outgoing:
            ends_by_t.setdefault(t, []).append(node_id)
        if node_id not in incoming:
            starts_by_t.setdefault(t, []).append(node_id)
        if node_id not in incident:
            isolated_by_t.setdefault(t, []).append(node_id)

    max_synthetic = min(
        GAP_CLOSE_MAX_ADDED_ABS,
        max(1, int(round(len(nodes_by_id) * GAP_CLOSE_MAX_ADDED_FRAC))) if GAP_CLOSE_MAX_ADDED_FRAC > 0 else 0,
    )
    next_id = _next_node_id(nodes_by_id)
    frame_cache = frame_cache if frame_cache is not None else {}
    deepcenter_cache = deepcenter_cache if deepcenter_cache is not None else {}
    used_starts: set[int] = set()
    used_isolated: set[int] = set()
    synthetic_added = 0
    new_edges: list[dict[str, object]] = []

    density_cache: dict[int, dict[int, float]] = {}

    def frame_local_spacing(t: int) -> dict[int, float]:
        cached = density_cache.get(t)
        if cached is not None:
            return cached

        frame_ids = all_ids_by_t.get(t, [])
        if len(frame_ids) <= 1:
            result = {
                node_id: GAP_DENSITY_REFERENCE_UM
                for node_id in frame_ids
            }
            density_cache[t] = result
            return result

        positions = np.stack(
            [_position_um(nodes_by_id[node_id]) for node_id in frame_ids]
        )
        tree = cKDTree(positions)
        query_k = min(
            len(frame_ids),
            max(2, GAP_DENSITY_NEIGHBORS + 1),
        )
        distances, _ = tree.query(positions, k=query_k)
        if distances.ndim == 1:
            distances = distances[:, None]

        result: dict[int, float] = {}
        for idx, node_id in enumerate(frame_ids):
            neighbour_distances = distances[idx, 1:]
            neighbour_distances = neighbour_distances[
                np.isfinite(neighbour_distances)
            ]
            spacing = (
                float(np.median(neighbour_distances))
                if neighbour_distances.size
                else GAP_DENSITY_REFERENCE_UM
            )
            result[node_id] = spacing

        density_cache[t] = result
        stats["gap_density_nodes_scored"] += len(result)
        return result

    effective_gap_max = min(GAP_CLOSE_MAX_GAP, 1)
    stats["gap_close_effective_max_gap"] = effective_gap_max
    for gap in range(1, effective_gap_max + 1):
        for t, end_ids in sorted(ends_by_t.items()):
            start_ids = [sid for sid in starts_by_t.get(t + gap + 1, []) if sid not in used_starts]
            if not end_ids or not start_ids:
                continue

            end_points = [node_point(nodes_by_id[eid]) for eid in end_ids]
            start_points = [node_point(nodes_by_id[sid]) for sid in start_ids]
            threshold_um = GAP_CLOSE_UM * (gap + 1)
            d = np.zeros(
                (len(end_ids), len(start_ids)),
                dtype=np.float64,
            )
            adaptive_threshold = np.full_like(d, threshold_um)

            source_spacing = frame_local_spacing(t)
            target_spacing = frame_local_spacing(t + gap + 1)

            for i, ep in enumerate(end_points):
                for j, sp in enumerate(start_points):
                    d[i, j] = point_distance_um(ep, sp)

                    if GAP_DENSITY_ADAPTIVE:
                        local_spacing = 0.5 * (
                            source_spacing.get(
                                end_ids[i],
                                GAP_DENSITY_REFERENCE_UM,
                            )
                            + target_spacing.get(
                                start_ids[j],
                                GAP_DENSITY_REFERENCE_UM,
                            )
                        )
                        step_delta = float(
                            np.clip(
                                GAP_DENSITY_GAIN
                                * (
                                    local_spacing
                                    - GAP_DENSITY_REFERENCE_UM
                                ),
                                -GAP_DENSITY_MAX_STEP_DELTA_UM,
                                GAP_DENSITY_MAX_STEP_DELTA_UM,
                            )
                        )
                        adaptive_threshold[i, j] = (
                            threshold_um + step_delta * (gap + 1)
                        )
                        stats[
                            "gap_density_step_delta_milli_sum"
                        ] += int(round(1000.0 * step_delta))

            base_allowed = d <= threshold_um
            adaptive_allowed = d <= adaptive_threshold

            stats["gap_density_candidates_expanded"] += int(
                (adaptive_allowed & ~base_allowed).sum()
            )
            stats["gap_density_candidates_restricted"] += int(
                (base_allowed & ~adaptive_allowed).sum()
            )
            stats["gap_candidates"] += int(adaptive_allowed.sum())

            if not np.isfinite(d).any():
                continue

            max_threshold = float(np.max(adaptive_threshold))
            big = max_threshold * 1000.0 + 1.0
            cost = np.where(adaptive_allowed, d, big)
            row_ind, col_ind = linear_sum_assignment(cost)

            for r, c in zip(row_ind, col_ind):
                if not adaptive_allowed[r, c]:
                    continue
                if not base_allowed[r, c]:
                    stats[
                        "gap_density_selected_outside_base"
                    ] += 1
                source_id = end_ids[int(r)]
                target_id = start_ids[int(c)]
                if source_id in outgoing or target_id in used_starts:
                    continue

                source = nodes_by_id[source_id]
                target = nodes_by_id[target_id]
                mid_t = int(source["t"]) + gap
                mid_point = (
                    (float(source["z"]) + float(target["z"])) / 2.0,
                    (float(source["y"]) + float(target["y"])) / 2.0,
                    (float(source["x"]) + float(target["x"])) / 2.0,
                )

                middle_id: int | None = None
                middle_reused = False
                if GAP_CLOSE_REUSE_EXISTING:
                    candidates = [nid for nid in isolated_by_t.get(mid_t, []) if nid not in used_isolated]
                    if candidates:
                        distances = [point_distance_um(node_point(nodes_by_id[nid]), mid_point) for nid in candidates]
                        best_idx = int(np.argmin(distances))
                        if distances[best_idx] <= GAP_CLOSE_REUSE_UM:
                            middle_id = candidates[best_idx]
                            middle_reused = True

                if middle_id is None:
                    if synthetic_added >= max_synthetic:
                        stats["gap_skipped_node_cap"] += 1
                        continue
                    middle_id = next_id
                    next_id += 1
                    refined_point = refine_synthetic_midpoint(dataset, mid_t, mid_point, frame_cache, stats)
                    nodes_by_id[middle_id] = {
                        "node_id": middle_id,
                        "t": mid_t,
                        "z": refined_point[0],
                        "y": refined_point[1],
                        "x": refined_point[2],
                        "gap_synthetic": 1,
                    }
                    synthetic_added += 1
                    stats["gap_inserted_synthetic"] += 1

                middle = nodes_by_id[middle_id]
                gap_span_um = float(d[r, c])
                marginal_gap = gap_span_um >= DEEPCENTER_GAP_CONFIRM_MIN_SPAN_UM
                synthetic_middle = int(middle.get("gap_synthetic", 0)) == 1
                requires_center_confirmation = (
                    DEEPCENTER_GAP_VETO and marginal_gap and synthetic_middle
                )
                if DEEPCENTER_GAP_VETO and not marginal_gap:
                    stats["deepcenter_gap_bypassed_strong_motion"] += 1
                elif DEEPCENTER_GAP_VETO and not synthetic_middle:
                    stats["deepcenter_gap_bypassed_observed_node"] += 1
                if requires_center_confirmation and not deepcenter_accept_repair_point(
                    dataset,
                    mid_t,
                    node_point(middle),
                    deepcenter_bundle,
                    frame_cache,
                    deepcenter_cache,
                    stats,
                    "gap",
                    DEEPCENTER_GAP_THRESHOLD,
                ):
                    if int(middle.get("gap_synthetic", 0)) == 1:
                        nodes_by_id.pop(middle_id, None)
                        synthetic_added = max(0, synthetic_added - 1)
                        stats["gap_inserted_synthetic"] = max(0, stats["gap_inserted_synthetic"] - 1)
                    continue
                if middle_reused:
                    used_isolated.add(middle_id)
                    stats["gap_reused_existing"] += 1

                e1 = {
                    "source_id": source_id,
                    "target_id": middle_id,
                    "edge_prob": None,
                    "distance_um": edge_distance_um(source, middle),
                    "gap_closed": 1,
                }
                e2 = {
                    "source_id": middle_id,
                    "target_id": target_id,
                    "edge_prob": None,
                    "distance_um": edge_distance_um(middle, target),
                    "gap_closed": 1,
                }
                new_edges.extend([e1, e2])
                outgoing.add(source_id)
                incoming.add(middle_id)
                outgoing.add(middle_id)
                incoming.add(target_id)
                used_starts.add(target_id)
                stats["gap_pairs_selected"] += 1
                stats["gap_added_edges"] += 2

    if new_edges:
        edges = [*edges, *new_edges]
    stats["gap_added_nodes"] = stats["gap_inserted_synthetic"]
    return nodes_by_id, edges


def _single_successor_map(edges: list[dict[str, object]]) -> dict[int, int]:
    by_source: dict[int, list[int]] = {}
    for edge in edges:
        by_source.setdefault(int(edge["source_id"]), []).append(int(edge["target_id"]))
    return {source: targets[0] for source, targets in by_source.items() if len(targets) == 1}


def _single_predecessor_map(edges: list[dict[str, object]]) -> dict[int, int]:
    by_target: dict[int, list[int]] = {}
    for edge in edges:
        by_target.setdefault(int(edge["target_id"]), []).append(int(edge["source_id"]))
    return {target: sources[0] for target, sources in by_target.items() if len(sources) == 1}


def recover_strict_gap2(
    nodes_by_id: dict[int, dict[str, object]],
    edges: list[dict[str, object]],
    stats: dict[str, int],
    dataset: str | None = None,
) -> tuple[dict[int, dict[str, object]], list[dict[str, object]]]:
    if not OUTPUT_GAP2_RECOVERY or not edges or not nodes_by_id:
        return nodes_by_id, edges

    outgoing = {int(edge["source_id"]) for edge in edges}
    incoming = {int(edge["target_id"]) for edge in edges}
    predecessor = _single_predecessor_map(edges)
    successor = _single_successor_map(edges)

    ends_by_t: dict[int, list[int]] = {}
    starts_by_t: dict[int, list[int]] = {}
    for node_id, node in nodes_by_id.items():
        t = int(node["t"])
        if node_id not in outgoing:
            ends_by_t.setdefault(t, []).append(node_id)
        if node_id not in incoming:
            starts_by_t.setdefault(t, []).append(node_id)

    cap = min(GAP2_MAX_LINKS_ABS, max(1, int(round(len(edges) * GAP2_MAX_LINKS_FRAC))))
    proposals: list[tuple[float, int, int, int, float]] = []

    def pos_um(node_id: int) -> np.ndarray:
        node = nodes_by_id[node_id]
        return np.array([float(node["z"]), float(node["y"]), float(node["x"])], dtype=np.float64) * np.array(VOXEL_SCALE_UM)

    for t, end_ids in sorted(ends_by_t.items()):
        start_ids = starts_by_t.get(t + 3, [])
        if not end_ids or not start_ids:
            continue
        for end_id in end_ids:
            end_pos = pos_um(end_id)
            for start_id in start_ids:
                start_pos = pos_um(start_id)
                dist = float(np.linalg.norm(start_pos - end_pos))
                if dist > GAP2_MAX_TOTAL_UM or dist / 3.0 > GAP2_MAX_STEP_UM:
                    continue
                step = (start_pos - end_pos) / 3.0
                context_penalty = 0.0
                if GAP2_REQUIRE_CONTEXT:
                    ok_context = False
                    prev_id = predecessor.get(end_id)
                    if prev_id is not None:
                        prev_step = end_pos - pos_um(prev_id)
                        prev_norm = float(np.linalg.norm(prev_step))
                        step_norm = float(np.linalg.norm(step))
                        if prev_norm <= 0.01 or step_norm <= 0.01:
                            ok_context = True
                        else:
                            cos = float(np.dot(prev_step, step) / (prev_norm * step_norm + 1e-9))
                            if cos > -0.25 and np.linalg.norm(prev_step - step) <= 6.0:
                                ok_context = True
                            context_penalty += max(0.0, 0.25 - cos)
                    next_id = successor.get(start_id)
                    if next_id is not None:
                        next_step = pos_um(next_id) - start_pos
                        next_norm = float(np.linalg.norm(next_step))
                        step_norm = float(np.linalg.norm(step))
                        if next_norm <= 0.01 or step_norm <= 0.01:
                            ok_context = True
                        else:
                            cos = float(np.dot(next_step, step) / (next_norm * step_norm + 1e-9))
                            if cos > -0.25 and np.linalg.norm(next_step - step) <= 6.0:
                                ok_context = True
                            context_penalty += max(0.0, 0.25 - cos)
                    if not ok_context:
                        continue
                proposals.append((dist + 2.0 * context_penalty, end_id, start_id, t, dist))

    proposals.sort(key=lambda item: item[0])
    stats["gap2_candidates"] = len(proposals)
    if not proposals:
        return nodes_by_id, edges

    selected: list[tuple[float, int, int, int, float]] = []
    used_ends: set[int] = set()
    used_starts: set[int] = set()
    per_frame_count: dict[int, int] = {}
    for proposal in proposals:
        if len(selected) >= cap:
            stats["gap2_skipped_cap"] += 1
            break
        _, end_id, start_id, t, _ = proposal
        if end_id in used_ends or start_id in used_starts:
            continue
        frame_cap = max(1, int(round(len(ends_by_t.get(t, [])) * GAP2_FRAME_FRAC_CAP)))
        if per_frame_count.get(t, 0) >= frame_cap:
            continue
        selected.append(proposal)
        used_ends.add(end_id)
        used_starts.add(start_id)
        per_frame_count[t] = per_frame_count.get(t, 0) + 1

    if not selected:
        return nodes_by_id, edges

    next_node_id = _next_node_id(nodes_by_id)
    frame_cache: dict[int, np.ndarray] = {}
    new_edges: list[dict[str, object]] = []
    for _, end_id, start_id, t, _ in selected:
        source = nodes_by_id[end_id]
        target = nodes_by_id[start_id]
        previous_id = end_id
        inserted_ids: list[int] = []
        for k in (1, 2):
            frac = k / 3.0
            mid_t = int(source["t"]) + k
            midpoint = (
                float(source["z"]) + (float(target["z"]) - float(source["z"])) * frac,
                float(source["y"]) + (float(target["y"]) - float(source["y"])) * frac,
                float(source["x"]) + (float(target["x"]) - float(source["x"])) * frac,
            )
            refined_point = refine_synthetic_midpoint(dataset, mid_t, midpoint, frame_cache, stats)
            node_id = next_node_id
            next_node_id += 1
            nodes_by_id[node_id] = {
                "node_id": node_id,
                "t": mid_t,
                "z": refined_point[0],
                "y": refined_point[1],
                "x": refined_point[2],
            }
            inserted_ids.append(node_id)
            current = nodes_by_id[node_id]
            new_edges.append({
                "source_id": previous_id,
                "target_id": node_id,
                "edge_prob": None,
                "distance_um": edge_distance_um(nodes_by_id[previous_id], current),
                "gap2_recovered": 1,
            })
            previous_id = node_id
        new_edges.append({
            "source_id": previous_id,
            "target_id": start_id,
            "edge_prob": None,
            "distance_um": edge_distance_um(nodes_by_id[previous_id], target),
            "gap2_recovered": 1,
        })
        stats["gap2_pairs_selected"] += 1
        stats["gap2_added_nodes"] += len(inserted_ids)
        stats["gap2_added_edges"] += 3

    return nodes_by_id, [*edges, *new_edges]


SAFE_DIV_REQUIRE_DIVERGENCE = os.environ.get("BIOHUB_SAFE_DIV_REQUIRE_DIVERGENCE", "0") != "0"
SAFE_DIV_DIVERGE_UM = float(os.environ.get("BIOHUB_SAFE_DIV_DIVERGE_UM", "0.0"))
SAFE_DIV_SISTER_SYMMETRY_TAU = float(os.environ.get("BIOHUB_SAFE_DIV_SISTER_SYMMETRY_TAU", "0.0"))


def add_safe_divisions_postlink(
    nodes_by_id: dict[int, dict[str, object]],
    edges: list[dict[str, object]],
    stats: dict[str, int],
    dataset: str | None = None,
    deepcenter_bundle: dict[str, object] | None = None,
    frame_cache: dict[int, np.ndarray] | None = None,
    deepcenter_cache: dict[tuple[str, int], np.ndarray] | None = None,
) -> list[dict[str, object]]:
    if not OUTPUT_SAFE_DIVISIONS or not edges or not nodes_by_id:
        return edges
    frame_cache = frame_cache if frame_cache is not None else {}
    deepcenter_cache = deepcenter_cache if deepcenter_cache is not None else {}

    out_by_source: dict[int, list[dict[str, object]]] = {}
    incoming: set[int] = set()
    for edge in edges:
        out_by_source.setdefault(int(edge["source_id"]), []).append(edge)
        incoming.add(int(edge["target_id"]))

    ids_by_t: dict[int, list[int]] = {}
    for node_id, node in nodes_by_id.items():
        ids_by_t.setdefault(int(node["t"]), []).append(node_id)

    existing_edges = {(int(edge["source_id"]), int(edge["target_id"])) for edge in edges}
    global_cap = max(1, int(round(max(1, len(edges)) * SAFE_DIV_GLOBAL_FRAC_CAP)))
    _sb_min_um = float(_sh_os.environ.get("BIOHUB_SAFE_DIV_MIN_BOUNDARY_UM", "0") or "0")
    _sb_extent = None
    added: list[dict[str, object]] = []
    used_targets: set[int] = set()

    # --- PORTE SPAN (BIOHUB_SAFE_DIV_MIN_TARGET_SPAN) --------------------------------
    # Une greffe dont la CIBLE demarre une composante COURTE greffe sur un fragment
    # isole, pas sur une vraie fille. On mesure l etendue temporelle de la composante
    # de chaque noeud dans le graphe TEL QU IL EST AU SIEGE DE LA GREFFE (apres relink
    # et comblement, avant tri/troncature) par union-find sur la liste d aretes
    # courante. N <= 0 => bloc entierement saute, comportement identique.
    SAFE_DIV_MIN_TARGET_SPAN = int(_sh_os.environ.get("BIOHUB_SAFE_DIV_MIN_TARGET_SPAN", "0") or "0")
    span_by_node: dict[int, int] = {}
    if SAFE_DIV_MIN_TARGET_SPAN > 0:
        _span_parent = {node_id: node_id for node_id in nodes_by_id}

        def _span_find(node_id: int) -> int:
            while _span_parent[node_id] != node_id:
                _span_parent[node_id] = _span_parent[_span_parent[node_id]]
                node_id = _span_parent[node_id]
            return node_id

        def _span_union(a: int, b: int) -> None:
            if a not in _span_parent or b not in _span_parent:
                return
            ra = _span_find(a)
            rb = _span_find(b)
            if ra != rb:
                _span_parent[ra] = rb

        for edge in edges:
            _span_union(int(edge["source_id"]), int(edge["target_id"]))
        _span_lo: dict[int, int] = {}
        _span_hi: dict[int, int] = {}
        for node_id, node in nodes_by_id.items():
            root = _span_find(node_id)
            t_node = int(node["t"])
            if root not in _span_lo or t_node < _span_lo[root]:
                _span_lo[root] = t_node
            if root not in _span_hi or t_node > _span_hi[root]:
                _span_hi[root] = t_node
        for node_id in nodes_by_id:
            root = _span_find(node_id)
            span_by_node[node_id] = _span_hi[root] - _span_lo[root] + 1
        stats["safe_division_span_components"] = len(set(
            _span_find(node_id) for node_id in nodes_by_id))
    # --- FIN PORTE SPAN --------------------------------------------------------------
    for t in sorted(ids_by_t):
        child_frame_ids = ids_by_t.get(t + 1, [])
        if not child_frame_ids:
            continue
        source_ids = [node_id for node_id in ids_by_t[t] if len(out_by_source.get(node_id, [])) == 1]
        candidate_ids = [node_id for node_id in child_frame_ids if node_id not in incoming and node_id not in used_targets]
        if SAFE_DIV_MIN_TARGET_SPAN > 0 and candidate_ids:
            _span_kept = [node_id for node_id in candidate_ids
                          if span_by_node.get(node_id, 0) >= SAFE_DIV_MIN_TARGET_SPAN]
            stats["safe_division_span_rejected"] = (
                stats.get("safe_division_span_rejected", 0)
                + len(candidate_ids) - len(_span_kept))
            candidate_ids = _span_kept
            if not candidate_ids:
                continue
        if not source_ids or not candidate_ids:
            continue

        frame_cap = max(1, int(round(len(source_ids) * SAFE_DIV_FRAME_FRAC_CAP)))
        proposals: list[tuple[float, int, int, float, float]] = []
        for source_id in source_ids:
            source = nodes_by_id[source_id]
            existing_child_edge = out_by_source[source_id][0]
            existing_child_id = int(existing_child_edge["target_id"])
            existing_child = nodes_by_id.get(existing_child_id)
            if existing_child is None or int(existing_child["t"]) != t + 1:
                continue
            child_dist = edge_distance_um(source, existing_child)
            if child_dist > SAFE_DIV_EXISTING_CHILD_MAX_UM:
                continue
            for candidate_id in candidate_ids:
                if (source_id, candidate_id) in existing_edges:
                    continue
                candidate = nodes_by_id[candidate_id]
                parent_dist = edge_distance_um(source, candidate)
                if parent_dist > SAFE_DIV_MAX_UM:
                    continue
                sister_dist = edge_distance_um(existing_child, candidate)
                if sister_dist > SAFE_DIV_SISTER_MAX_UM:
                    continue
                # PORTE 1 (0,941) : une vraie fourche se CONFIRME en t+2 --
                # les deux petits-enfants doivent s etre ECARTES.
                if SAFE_DIV_REQUIRE_DIVERGENCE:
                    c1_succ = out_by_source.get(existing_child_id, [])
                    q_succ = out_by_source.get(candidate_id, [])
                    if len(c1_succ) != 1 or len(q_succ) != 1:
                        stats["safe_division_divergence_rejected"] += 1
                        continue
                    c1_grandchild = nodes_by_id.get(int(c1_succ[0]["target_id"]))
                    q_grandchild = nodes_by_id.get(int(q_succ[0]["target_id"]))
                    if (
                        c1_grandchild is None or q_grandchild is None
                        or int(c1_grandchild["t"]) != t + 2
                        or int(q_grandchild["t"]) != t + 2
                    ):
                        stats["safe_division_divergence_rejected"] += 1
                        continue
                    grandchild_dist = edge_distance_um(c1_grandchild, q_grandchild)
                    if grandchild_dist - sister_dist < SAFE_DIV_DIVERGE_UM:
                        stats["safe_division_divergence_rejected"] += 1
                        continue
                if DEEPCENTER_SAFE_DIV_VETO and not deepcenter_accept_repair_point(
                    dataset,
                    int(candidate["t"]),
                    node_point(candidate),
                    deepcenter_bundle,
                    frame_cache,
                    deepcenter_cache,
                    stats,
                    "safe_div",
                    DEEPCENTER_SAFE_DIV_THRESHOLD,
                ):
                    continue
                # PORTE 2 (0,941) : deux filles d une vraie division sont a des
                # distances COMPARABLES du parent. Rejeter la proposition
                # parasite LIBERE le creneau glouton de la trame pour la vraie.
                if SAFE_DIV_SISTER_SYMMETRY_TAU > 0.0:
                    _sym_denom = max((child_dist + parent_dist) / 2.0, 1e-6)
                    if abs(child_dist - parent_dist) / _sym_denom > SAFE_DIV_SISTER_SYMMETRY_TAU:
                        stats["safe_division_symmetry_rejected"] += 1
                        continue
                if _sb_min_um > 0.0:
                    if _sb_extent is None:
                        _sb_zz = _sb_yy = _sb_xx = 0.0
                        _sb_neg = 0
                        _sb_out = 0
                        for _sb_n in nodes_by_id.values():
                            _sb_a = float(_sb_n["z"])
                            _sb_b = float(_sb_n["y"])
                            _sb_c = float(_sb_n["x"])
                            if _sb_a < 0.0 or _sb_b < 0.0 or _sb_c < 0.0:
                                _sb_neg += 1
                            if _sb_a > 63.0 or _sb_b > 255.0 or _sb_c > 255.0:
                                _sb_out += 1
                            _sb_zz = max(_sb_zz, _sb_a)
                            _sb_yy = max(_sb_yy, _sb_b)
                            _sb_xx = max(_sb_xx, _sb_c)
                        if _sb_neg:
                            raise RuntimeError(
                                "[k14] BOUNDARY: %d node(s) have a NEGATIVE coordinate; "
                                "the published field cannot be the reference" % _sb_neg)
                        _sb_extent = (63.0, 255.0, 255.0)
                        stats["safe_division_boundary_nodes_beyond_field"] = _sb_out
                        print("[k14] boundary: published field 63/255/255 ; this film's "
                              "own extent %.1f/%.1f/%.1f ; %d node(s) beyond the field"
                              % (_sb_zz, _sb_yy, _sb_xx, _sb_out), flush=True)
                    _sb_cz = float(candidate["z"])
                    _sb_cy = float(candidate["y"])
                    _sb_cx = float(candidate["x"])
                    _sb_d = min(_sb_cz * 1.625, (_sb_extent[0] - _sb_cz) * 1.625,
                                _sb_cy * 0.40625, (_sb_extent[1] - _sb_cy) * 0.40625,
                                _sb_cx * 0.40625, (_sb_extent[2] - _sb_cx) * 0.40625)
                    if _sb_d < 0.0:
                        _sb_d = 0.0
                    if _sb_d < _sb_min_um:
                        stats["safe_division_boundary_rejected"] = (
                            stats.get("safe_division_boundary_rejected", 0) + 1)
                        continue
                score = parent_dist + 0.15 * sister_dist
                proposals.append((score, source_id, candidate_id, parent_dist, sister_dist))

        stats["safe_division_candidates"] += len(proposals)
        if not proposals:
            continue
        _sk_mode = _sh_os.environ.get("BIOHUB_SAFE_DIV_SORT_KEY", "deployed").strip().lower()
        if _sk_mode == "sis_growth_12":
            # ENG/KER14 sort key -- see ship/sortkey_patch.py for why.
            _sk_rows = []
            for _sk_it in proposals:
                _sk_src, _sk_cand, _sk_sis = _sk_it[1], _sk_it[2], _sk_it[4]
                _sk_g = None
                _sk_ae = out_by_source.get(_sk_src) or []
                if len(_sk_ae) == 1:
                    _sk_a = int(_sk_ae[0]["target_id"])
                    _sk_as = out_by_source.get(_sk_a) or []
                    _sk_fs = out_by_source.get(_sk_cand) or []
                    if len(_sk_as) == 1 and len(_sk_fs) == 1:
                        _sk_an = nodes_by_id.get(int(_sk_as[0]["target_id"]))
                        _sk_fn = nodes_by_id.get(int(_sk_fs[0]["target_id"]))
                        if (_sk_an is not None and _sk_fn is not None
                                and int(_sk_an["t"]) == t + 2
                                and int(_sk_fn["t"]) == t + 2):
                            _sk_g = edge_distance_um(_sk_an, _sk_fn) - _sk_sis
                _sk_rows.append((0 if _sk_g is not None else 1,
                                 -(_sk_g if _sk_g is not None else 0.0),
                                 _sk_it[0], _sk_it))
            _sk_rows.sort(key=lambda _z: (_z[0], _z[1], _z[2]))
            proposals[:] = [_z[3] for _z in _sk_rows]
            _sk_k = sum(1 for _z in _sk_rows if _z[0] == 0)
            stats["safe_division_sortkey_keyed"] = stats.get(
                "safe_division_sortkey_keyed", 0) + _sk_k
            stats["safe_division_sortkey_unkeyed"] = stats.get(
                "safe_division_sortkey_unkeyed", 0) + len(_sk_rows) - _sk_k
        else:
            proposals.sort(key=lambda item: item[0])
        added_this_frame = 0
        for _, source_id, candidate_id, parent_dist, _ in proposals:
            if len(added) >= global_cap:
                stats["safe_division_skipped_cap"] += 1
                break
            if added_this_frame >= frame_cap:
                break
            if candidate_id in used_targets or candidate_id in incoming:
                continue
            candidate = nodes_by_id[candidate_id]
            added.append({
                "source_id": source_id,
                "target_id": candidate_id,
                "edge_prob": None,
                "distance_um": parent_dist,
                "safe_division": 1,
            })
            used_targets.add(candidate_id)
            added_this_frame += 1

    if added:
        stats["safe_divisions_added"] = len(added)
        return [*edges, *added]
    return edges


def filter_short_track_components(
    nodes_by_id: dict[int, dict[str, object]],
    edges: list[dict[str, object]],
    stats: dict[str, int],
) -> tuple[dict[int, dict[str, object]], list[dict[str, object]]]:
    if not OUTPUT_FILTER_SHORT_TRACKS or OUTPUT_MIN_TRACK_LEN <= 1 or not edges:
        return nodes_by_id, edges

    parent = {node_id: node_id for node_id in nodes_by_id}

    def find(node_id: int) -> int:
        while parent[node_id] != node_id:
            parent[node_id] = parent[parent[node_id]]
            node_id = parent[node_id]
        return node_id

    def union(a: int, b: int) -> None:
        if a not in parent or b not in parent:
            return
        ra = find(a)
        rb = find(b)
        if ra != rb:
            parent[ra] = rb

    out_count: dict[int, int] = {}
    for edge in edges:
        source_id = int(edge["source_id"])
        target_id = int(edge["target_id"])
        union(source_id, target_id)
        out_count[source_id] = out_count.get(source_id, 0) + 1

    components: dict[int, list[int]] = {}
    for node_id in nodes_by_id:
        components.setdefault(find(node_id), []).append(node_id)

    component_edges: dict[int, list[dict[str, object]]] = {root: [] for root in components}
    for edge in edges:
        source_id = int(edge["source_id"])
        target_id = int(edge["target_id"])
        if source_id in parent and target_id in parent:
            component_edges.setdefault(find(source_id), []).append(edge)

    keep: set[int] = set()
    for root, members in components.items():
        has_division = any(out_count.get(node_id, 0) >= 2 for node_id in members)
        if len(members) >= OUTPUT_MIN_TRACK_LEN or (OUTPUT_KEEP_DIVISION_COMPONENTS and has_division):
            keep.update(members)

    if not keep:
        stats["short_track_filter_skipped_all"] += 1
        return nodes_by_id, edges

    removed_before_rescue = len(nodes_by_id) - len(keep)
    if removed_before_rescue <= 0:
        return nodes_by_id, edges

    if ADAPTIVE_SHORT_TRACK_RESCUE:
        removed_frac = removed_before_rescue / max(len(nodes_by_id), 1)
        if removed_frac >= SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC:
            budget = min(
                SHORT_TRACK_RESCUE_MAX_NODES_ABS,
                max(0, int(round(len(nodes_by_id) * SHORT_TRACK_RESCUE_MAX_NODES_FRAC))),
            )
            stats["short_track_rescue_triggered"] = 1
            stats["short_track_rescue_budget"] = budget
            proposals: list[tuple[float, int, float, int, list[int]]] = []
            for root, members in components.items():
                if set(members) & keep:
                    continue
                if len(members) < SHORT_TRACK_RESCUE_MIN_LEN or len(members) >= OUTPUT_MIN_TRACK_LEN:
                    continue
                c_edges = component_edges.get(root, [])
                if not c_edges:
                    continue
                probs: list[float] = []
                dists: list[float] = []
                for edge in c_edges:
                    try:
                        prob = float(edge.get("edge_prob", 0.0))
                    except (TypeError, ValueError):
                        prob = 0.0
                    if np.isfinite(prob):
                        probs.append(prob)
                    try:
                        dist = float(edge.get("distance_um", np.nan))
                    except (TypeError, ValueError):
                        dist = np.nan
                    if np.isfinite(dist):
                        dists.append(dist)
                mean_prob = float(np.mean(probs)) if probs else 0.0
                mean_dist = float(np.mean(dists)) if dists else float("inf")
                if mean_prob < SHORT_TRACK_RESCUE_MIN_MEAN_EDGE_PROB:
                    continue
                if mean_dist > SHORT_TRACK_RESCUE_MAX_MEAN_EDGE_DIST_UM:
                    continue
                score = mean_prob - 0.02 * mean_dist + 0.004 * len(members)
                proposals.append((score, len(members), mean_prob, root, members))
            proposals.sort(reverse=True)
            rescued_nodes = 0
            rescued_components = 0
            for _, size, _, _, members in proposals:
                if budget <= 0 or rescued_nodes + size > budget:
                    continue
                keep.update(members)
                rescued_nodes += size
                rescued_components += 1
            stats["short_track_rescue_components"] = rescued_components
            stats["short_track_rescue_nodes"] = rescued_nodes

    removed_nodes = len(nodes_by_id) - len(keep)
    if removed_nodes <= 0:
        return nodes_by_id, edges

    kept_nodes = {node_id: node for node_id, node in nodes_by_id.items() if node_id in keep}
    kept_edges = [
        edge for edge in edges
        if int(edge["source_id"]) in kept_nodes and int(edge["target_id"]) in kept_nodes
    ]
    stats["short_track_components_removed"] = sum(1 for members in components.values() if not (set(members) & keep))
    stats["short_track_nodes_removed"] = removed_nodes
    stats["short_track_edges_removed"] = len(edges) - len(kept_edges)
    return kept_nodes, kept_edges


def linefit_smooth_output_graph(
    nodes_by_id: dict[int, dict[str, object]],
    edges: list[dict[str, object]],
    stats: dict[str, int],
) -> dict[int, dict[str, object]]:
    """Smooth linear track interiors without changing graph topology."""
    if not OUTPUT_LINEFIT_SMOOTH or OUTPUT_LINEFIT_WEIGHT <= 0 or OUTPUT_LINEFIT_WINDOW <= 0 or not edges:
        return nodes_by_id

    predecessor: dict[int, list[int]] = {}
    successor: dict[int, list[int]] = {}
    for edge in edges:
        source_id = int(edge["source_id"])
        target_id = int(edge["target_id"])
        source = nodes_by_id.get(source_id)
        target = nodes_by_id.get(target_id)
        if source is None or target is None:
            continue
        if int(target["t"]) != int(source["t"]) + 1:
            continue
        successor.setdefault(source_id, []).append(target_id)
        predecessor.setdefault(target_id, []).append(source_id)

    original_pos = {
        node_id: np.array([float(node["z"]), float(node["y"]), float(node["x"])], dtype=np.float64)
        for node_id, node in nodes_by_id.items()
    }
    updated_pos: dict[int, np.ndarray] = {}
    weight = float(np.clip(OUTPUT_LINEFIT_WEIGHT, 0.0, 1.0))

    for node_id in sorted(nodes_by_id):
        neighbourhood: list[tuple[int, int]] = [(0, node_id)]

        current = node_id
        for step in range(1, OUTPUT_LINEFIT_WINDOW + 1):
            prev_ids = predecessor.get(current, [])
            if len(prev_ids) != 1:
                break
            current = prev_ids[0]
            if current not in original_pos:
                break
            neighbourhood.append((-step, current))

        current = node_id
        for step in range(1, OUTPUT_LINEFIT_WINDOW + 1):
            next_ids = successor.get(current, [])
            if len(next_ids) != 1:
                break
            current = next_ids[0]
            if current not in original_pos:
                break
            neighbourhood.append((step, current))

        if len(neighbourhood) < 3:
            stats["linefit_skipped_nodes"] += 1
            continue

        dts = np.array([delta for delta, _ in neighbourhood], dtype=np.float64)
        coords = np.stack([original_pos[nid] for _, nid in neighbourhood])
        fitted = np.array([np.polyval(np.polyfit(dts, coords[:, axis], 1), 0.0) for axis in range(3)], dtype=np.float64)
        if not np.isfinite(fitted).all():
            stats["linefit_skipped_nodes"] += 1
            continue
        updated_pos[node_id] = (1.0 - weight) * original_pos[node_id] + weight * fitted

    for node_id, pos in updated_pos.items():
        nodes_by_id[node_id]["z"] = float(pos[0])
        nodes_by_id[node_id]["y"] = float(pos[1])
        nodes_by_id[node_id]["x"] = float(pos[2])

    stats["linefit_smoothed_nodes"] = len(updated_pos)
    return nodes_by_id


def filter_output_graph(
    nodes_by_id: dict[int, dict[str, object]],
    raw_edges: list[dict[str, object]],
    dataset: str | None = None,
    deepcenter_bundle: dict[str, object] | None = None,
) -> tuple[dict[int, dict[str, object]], list[dict[str, object]], dict[str, int]]:
# ---- ENG/KER13 : DUMP THE RELINK'S INPUT (env-armed, byte-identical when off) ----
    if os.environ.get("KER13_DUMP_RELINK_INPUT", "0").strip() not in ("", "0"):
        try:
            import numpy as _k13_np
            _k13_dir = os.environ.get("KER13_DUMP_RELINK_DIR",
                                      "/kaggle/working/relink_input").strip()
            os.makedirs(_k13_dir, exist_ok=True)
            _k13_film = str(dataset) if dataset else "unknown"
            # INTEGER POSITIONS, as ZEUS ordered. The chassis carries z/y/x as floats
            # at this point (the smoother has already run); the relink's own geometry
            # is computed on these values, so the dump rounds with the EXPORT's rule
            # -- int(round(v)) -- and says so in the npz, rather than truncating and
            # leaving RELINK to discover a half-voxel bias.
            _k13_ids = sorted(nodes_by_id)
            _k13_n = len(_k13_ids)
            _k13_t = _k13_np.empty(_k13_n, _k13_np.int32)
            _k13_z = _k13_np.empty(_k13_n, _k13_np.int32)
            _k13_y = _k13_np.empty(_k13_n, _k13_np.int32)
            _k13_x = _k13_np.empty(_k13_n, _k13_np.int32)
            for _k13_i, _k13_nid in enumerate(_k13_ids):
                _k13_nd = nodes_by_id[_k13_nid]
                _k13_t[_k13_i] = int(_k13_nd["t"])
                _k13_z[_k13_i] = int(round(float(_k13_nd["z"])))
                _k13_y[_k13_i] = int(round(float(_k13_nd["y"])))
                _k13_x[_k13_i] = int(round(float(_k13_nd["x"])))
            # THE EDGE LIST AS GIVEN, in the order given. The relink consumes this
            # order, so the dump preserves it rather than sorting: a sorted dump would
            # be a different object from the one the relink sees.
            _k13_src = _k13_np.asarray([int(_e["source_id"]) for _e in raw_edges],
                                       dtype=_k13_np.int32)
            _k13_tgt = _k13_np.asarray([int(_e["target_id"]) for _e in raw_edges],
                                       dtype=_k13_np.int32)
            # EDGE_PROB IS LOAD-BEARING AND I HAD OMITTED IT. The call site builds each edge
            # with exactly three keys (cell_06 l.1569-1573: source_id, target_id, edge_prob)
            # and the probability is read at three places that decide the graph --
            # `edge_sort_key` (single-parent repair, single-child repair, the division
            # geometry filter), the short-track rescue, and `learned_edge_probs`. Without it
            # a replay silently runs ARM-0 and the later stages amplify a six-edge relink
            # difference into hundreds: ENG/RELINK measured 909/658, 2 548/1 179, 241/144,
            # 4 761/3 418 on the DRY four. float64 with NaN for the driver's None, in the
            # SAME order as edge_source / edge_target.
            _k13_prob = _k13_np.asarray(
                [(_k13_np.nan if _e.get("edge_prob") is None else float(_e["edge_prob"]))
                 for _e in raw_edges], dtype=_k13_np.float64)
            # AMENDMENT 27, THE WRITE PATH. `savez_compressed` writes straight to the name
            # it is given, so a failure after the first byte would leave a TRUNCATED file
            # sitting at `<film>.npz` -- a partial dump wearing the name of a complete one,
            # which is the one outcome the amendment forbids. So the bytes go to
            # `<film>.npz.partial` and are promoted by `os.replace`, which is atomic on a
            # single filesystem: after any failure the final name either does not exist or
            # holds a COMPLETE previous dump, never a half of this one. The partial is left
            # on disk deliberately -- named as what it is, for diagnosis -- and RELINK's
            # reader takes `*.npz` only, so it cannot pick one up by accident.
            # AND IT MUST BE AN OPEN HANDLE, not a path. Given a PATH, numpy appends `.npz`
            # to anything not already ending in it, so `<film>.npz.partial` is written as
            # `<film>.npz.partial.npz`, `os.replace` then raises FileNotFoundError on the
            # name it was given, and the final `<film>.npz` is NEVER created -- 199 films
            # would print 199 DISARMED lines and produce zero dumps. Measured by ENG/RELINK
            # on numpy 2.4.6. Given a HANDLE, numpy writes exactly where it is pointed.
            # Renaming the temp to `<film>.partial.npz` would promote, but would put the
            # partial back inside the reader's `*.npz` glob -- the defect this avoids.
            _k13_p = os.path.join(_k13_dir, "%s.npz" % _k13_film)
            _k13_tmp = _k13_p + ".partial"
            with open(_k13_tmp, "wb") as _k13_fh:
                _k13_np.savez_compressed(
                    _k13_fh,
                    node_id=_k13_np.asarray(_k13_ids, dtype=_k13_np.int32),
                    t=_k13_t, z=_k13_z, y=_k13_y, x=_k13_x,
                    edge_source=_k13_src, edge_target=_k13_tgt,
                    edge_prob=_k13_prob,
                    schema=_k13_np.asarray(["ker13-relink-input-1.0"]),
                    film=_k13_np.asarray([_k13_film]),
                    rounding=_k13_np.asarray(["int(round(v)) on z,y,x -- the export's rule"]),
                    edge_order=_k13_np.asarray(["as given to filter_output_graph, unsorted"]),
                )
            # the handle is closed and flushed by the `with` before the promotion, so the
            # bytes are on disk when the rename happens. Promote only now.
            os.replace(_k13_tmp, _k13_p)
            print("[ker13-dump] %s : %d nodes, %d raw edges -> %s (%d o)"
                  % (_k13_film, _k13_n, len(_k13_src), _k13_p,
                     os.path.getsize(_k13_p)), flush=True)
        except BaseException as _k13_e:        # noqa: BLE001
            # amendment 21 : the world passes through whatever happens here.
            print("[ker13-dump] DISARMED : %s: %s"
                  % (type(_k13_e).__name__, _k13_e), flush=True)
# ---- end ENG/KER13 dump hunk ----------------------------------------------------

    stats = {
        "raw_edges": len(raw_edges),
        "dropped_nonconsecutive_edges": 0,
        "dropped_long_edges": 0,
        "dropped_multi_parent_edges": 0,
        "dropped_multi_child_edges": 0,
        "dropped_division_edges": 0,
        "gap_candidates": 0,
        "gap_pairs_selected": 0,
        "gap_reused_existing": 0,
        "gap_inserted_synthetic": 0,
        "gap_added_nodes": 0,
        "gap_added_edges": 0,
        "gap_skipped_node_cap": 0,
        "gap_density_nodes_scored": 0,
        "gap_density_candidates_expanded": 0,
        "gap_density_candidates_restricted": 0,
        "gap_density_selected_outside_base": 0,
        "gap_density_step_delta_milli_sum": 0,
        "gap_refined_synthetic": 0,
        "gap_refine_failed": 0,
        "gap_refine_rejected_shift": 0,
        "pruned_isolated_nodes": 0,
        "motion_relink_edges": 0,
        "motion_relink_tight_edges": 0,
        "motion_relink_relaxed_edges": 0,
        "motion_relink_frames": 0,
        "motion_relink_replaced_raw_edges": 0,
        "motion_relink_fallback_raw": 0,
        "motion_relink_skipped_large_frame": 0,
        "gap2_candidates": 0,
        "gap2_pairs_selected": 0,
        "gap2_added_nodes": 0,
        "gap2_added_edges": 0,
        "ker10_gap2_ms": 0,
        "gap2_skipped_cap": 0,
        "safe_division_candidates": 0,
        "safe_division_divergence_rejected": 0,
        "safe_division_symmetry_rejected": 0,
        "safe_divisions_added": 0,
        "safe_division_skipped_cap": 0,
        "deepcenter_gap_checked": 0,
        "deepcenter_gap_bypassed_strong_motion": 0,
        "deepcenter_gap_bypassed_observed_node": 0,
        "deepcenter_gap_accepted": 0,
        "deepcenter_gap_rejected": 0,
        "deepcenter_gap_missing": 0,
        "deepcenter_safe_div_checked": 0,
        "deepcenter_safe_div_accepted": 0,
        "deepcenter_safe_div_rejected": 0,
        "deepcenter_safe_div_missing": 0,
        "short_track_components_removed": 0,
        "short_track_nodes_removed": 0,
        "short_track_edges_removed": 0,
        "short_track_filter_skipped_all": 0,
        "short_track_rescue_triggered": 0,
        "short_track_rescue_components": 0,
        "short_track_rescue_nodes": 0,
        "short_track_rescue_budget": 0,
        "linefit_smoothed_nodes": 0,
        "linefit_skipped_nodes": 0,
    }

    edges: list[dict[str, object]] = []
    for edge in raw_edges:
        source = nodes_by_id.get(int(edge["source_id"]))
        target = nodes_by_id.get(int(edge["target_id"]))
        if source is None or target is None:
            continue
        if OUTPUT_ENFORCE_NEXT_FRAME and int(target["t"]) != int(source["t"]) + 1:
            stats["dropped_nonconsecutive_edges"] += 1
            continue
        distance_um = edge_distance_um(source, target)
        edge["distance_um"] = distance_um
        if OUTPUT_EDGE_MAX_UM > 0 and distance_um > OUTPUT_EDGE_MAX_UM:
            stats["dropped_long_edges"] += 1
            continue
        edges.append(edge)

    if OUTPUT_MOTION_RELINK:
        learned_edge_probs: dict[tuple[int, int], float] = {}
        for edge in edges:
            prob = edge.get("edge_prob")
            if prob is None:
                continue
            try:
                prob = float(prob)
            except (TypeError, ValueError):
                continue
            if np.isfinite(prob):
                key = (int(edge["source_id"]), int(edge["target_id"]))
                learned_edge_probs[key] = max(learned_edge_probs.get(key, float("-inf")), prob)
        motion_edges = motion_relink_edges(nodes_by_id, stats, learned_edge_probs)
        if motion_edges:
            stats["motion_relink_replaced_raw_edges"] = len(edges)
            edges = motion_edges
        else:
            stats["motion_relink_fallback_raw"] = 1

    if OUTPUT_SINGLE_PARENT_REPAIR and edges:
        best_by_target: dict[int, dict[str, object]] = {}
        for edge in edges:
            target_id = int(edge["target_id"])
            prev = best_by_target.get(target_id)
            if prev is None or edge_sort_key(edge) > edge_sort_key(prev):
                best_by_target[target_id] = edge
        kept_ids = {id(edge) for edge in best_by_target.values()}
        stats["dropped_multi_parent_edges"] = sum(1 for edge in edges if id(edge) not in kept_ids)
        edges = [edge for edge in edges if id(edge) in kept_ids]

    if OUTPUT_SINGLE_CHILD_REPAIR and edges:
        best_by_source: dict[int, dict[str, object]] = {}
        for edge in edges:
            source_id = int(edge["source_id"])
            prev = best_by_source.get(source_id)
            if prev is None or edge_sort_key(edge) > edge_sort_key(prev):
                best_by_source[source_id] = edge
        kept_ids = {id(edge) for edge in best_by_source.values()}
        stats["dropped_multi_child_edges"] = sum(1 for edge in edges if id(edge) not in kept_ids)
        edges = [edge for edge in edges if id(edge) in kept_ids]

    repair_frame_cache: dict[int, np.ndarray] = {}
    deepcenter_heatmap_cache: dict[tuple[str, int], np.ndarray] = {}
    nodes_by_id, edges = close_single_frame_gaps(
        nodes_by_id,
        edges,
        stats,
        dataset=dataset,
        deepcenter_bundle=deepcenter_bundle,
        frame_cache=repair_frame_cache,
        deepcenter_cache=deepcenter_heatmap_cache,
    )
    import time as _k10_time
    _k10_g2_t0 = _k10_time.perf_counter()
    nodes_by_id, edges = recover_strict_gap2(nodes_by_id, edges, stats, dataset=dataset)
    stats["ker10_gap2_ms"] = int(round(
        (_k10_time.perf_counter() - _k10_g2_t0) * 1000.0))
    edges = add_safe_divisions_postlink(
        nodes_by_id,
        edges,
        stats,
        dataset=dataset,
        deepcenter_bundle=deepcenter_bundle,
        frame_cache=repair_frame_cache,
        deepcenter_cache=deepcenter_heatmap_cache,
    )

    if OUTPUT_DIVISION_GEOMETRY_FILTER and edges:
        by_source: dict[int, list[dict[str, object]]] = {}
        for edge in edges:
            by_source.setdefault(int(edge["source_id"]), []).append(edge)

        filtered: list[dict[str, object]] = []
        for source_id, source_edges in by_source.items():
            if len(source_edges) <= 1:
                filtered.extend(source_edges)
                continue

            ranked = sorted(source_edges, key=edge_sort_key, reverse=True)
            source = nodes_by_id[source_id]
            top1 = ranked[0]
            top2 = ranked[1]
            d1 = float(top1["distance_um"])
            d2 = float(top2["distance_um"])
            sister = edge_distance_um(nodes_by_id[int(top1["target_id"])], nodes_by_id[int(top2["target_id"])])
            valid_division = (
                max(d1, d2) <= DIV_PARENT_MAX_UM
                and sister <= DIV_SISTER_MAX_UM
                and int(nodes_by_id[int(top1["target_id"])] ["t"]) == int(source["t"]) + 1
                and int(nodes_by_id[int(top2["target_id"])] ["t"]) == int(source["t"]) + 1
            )
            if valid_division:
                filtered.extend([top1, top2])
                stats["dropped_division_edges"] += max(0, len(ranked) - 2)
            elif DIV_DROP_TO_SINGLE_IF_BAD:
                filtered.append(top1)
                stats["dropped_division_edges"] += len(ranked) - 1
            else:
                filtered.extend(ranked)
        edges = filtered

    if OUTPUT_PRUNE_ISOLATED:
        incident = {int(edge["source_id"]) for edge in edges} | {int(edge["target_id"]) for edge in edges}
        if incident:
            kept_nodes = {node_id: node for node_id, node in nodes_by_id.items() if node_id in incident}
            stats["pruned_isolated_nodes"] = len(nodes_by_id) - len(kept_nodes)
            nodes_by_id = kept_nodes
            edges = [edge for edge in edges if int(edge["source_id"]) in nodes_by_id and int(edge["target_id"]) in nodes_by_id]

    nodes_by_id, edges = filter_short_track_components(nodes_by_id, edges, stats)
    nodes_by_id = linefit_smooth_output_graph(nodes_by_id, edges, stats)
# ---- ENG/KER13 : DUMP THE CELL-11 OUTPUT (env-armed, byte-identical when off) ----
    if os.environ.get("KER13_DUMP_CELL11_OUTPUT", "0").strip() not in ("", "0"):
        try:
            import numpy as _k13b_np
            _k13b_dir = os.environ.get("KER13_DUMP_CELL11_DIR",
                                       "/kaggle/working/cell11_output").strip()
            os.makedirs(_k13b_dir, exist_ok=True)
            _k13b_film = str(dataset) if dataset else "unknown"
            _k13b_ids = sorted(nodes_by_id)
            _k13b_n = len(_k13b_ids)
            _k13b_t = _k13b_np.empty(_k13b_n, _k13b_np.int32)
            _k13b_z = _k13b_np.empty(_k13b_n, _k13b_np.float64)
            _k13b_y = _k13b_np.empty(_k13b_n, _k13b_np.float64)
            _k13b_x = _k13b_np.empty(_k13b_n, _k13b_np.float64)
            for _k13b_i, _k13b_nid in enumerate(_k13b_ids):
                _k13b_nd = nodes_by_id[_k13b_nid]
                _k13b_t[_k13b_i] = int(_k13b_nd["t"])
                _k13b_z[_k13b_i] = float(_k13b_nd["z"])
                _k13b_y[_k13b_i] = float(_k13b_nd["y"])
                _k13b_x[_k13b_i] = float(_k13b_nd["x"])
            _k13b_src = _k13b_np.asarray([int(_e["source_id"]) for _e in edges],
                                         dtype=_k13b_np.int32)
            _k13b_tgt = _k13b_np.asarray([int(_e["target_id"]) for _e in edges],
                                         dtype=_k13b_np.int32)
            _k13b_p = os.path.join(_k13b_dir, "%s.npz" % _k13b_film)
            _k13b_tmp = _k13b_p + ".partial"
            with open(_k13b_tmp, "wb") as _k13b_fh:
                _k13b_np.savez_compressed(
                    _k13b_fh,
                    node_id=_k13b_np.asarray(_k13b_ids, dtype=_k13b_np.int32),
                    t=_k13b_t, z=_k13b_z, y=_k13b_y, x=_k13b_x,
                    edge_source=_k13b_src, edge_target=_k13b_tgt,
                    schema=_k13b_np.asarray(["ker13-cell11-output-1.0"]),
                    film=_k13b_np.asarray([_k13b_film]),
                    stage=_k13b_np.asarray(["end of filter_output_graph: after "
                                            "filter_short_track_components and after "
                                            "linefit_smooth_output_graph, before the "
                                            "cells 12-18 that build the CSV"]),
                    coords=_k13b_np.asarray(["float64 EXACT as the stage holds them; the "
                                             "CSV's integers are made later by the writer "
                                             "with int(round(v)) then a spatial clamp"]),
                    edge_order=_k13b_np.asarray(["as filter_output_graph returns them"]),
                )
            os.replace(_k13b_tmp, _k13b_p)
            print("[ker13-cell11] %s : %d nodes, %d edges -> %s (%d o)"
                  % (_k13b_film, _k13b_n, len(_k13b_src), _k13b_p,
                     os.path.getsize(_k13b_p)), flush=True)
        except BaseException as _k13b_e:        # noqa: BLE001
            print("[ker13-cell11] DISARMED by failure: %r" % (_k13b_e,), flush=True)

    return nodes_by_id, edges, stats


def dataset_shape_tzyx(dataset: str) -> tuple[int, int, int, int]:
    """Read exact array bounds from the attached OME-Zarr metadata."""
    metadata_path = TEST_DIR / f"{dataset}.zarr" / "0" / "zarr.json"
    metadata = json.loads(metadata_path.read_text())
    shape = tuple(int(value) for value in metadata["shape"])
    if len(shape) != 4 or any(value <= 0 for value in shape):
        raise ValueError(f"{dataset}: invalid tzyx shape {shape}")
    return shape


def clamp_spatial_coordinate(value: float, upper_inclusive: int) -> int:
    """Round then clamp one spatial coordinate to an exact image bound."""
    if upper_inclusive < 0:
        raise ValueError(f"upper_inclusive must be nonnegative, got {upper_inclusive}")
    return min(max(int(round(float(value))), 0), upper_inclusive)


DEEPCENTER_VETO_DETECTOR = load_deepcenter_veto_detector()

geffs = sorted((REPO_DIR / "predictions").glob(f"*/{METHOD}/split_0/*.geff"))
print(f"Found {len(geffs)} prediction graphs")
if len(geffs) != len(test_stems):
    found = {path.stem for path in geffs}
    missing = sorted(set(test_stems) - found)
    raise RuntimeError(f"Expected {len(test_stems)} graphs, found {len(geffs)}. Missing: {missing[:10]}")
# ITEM 0 : la tranche est prise sur la liste DEJA TRIEE ci-dessus, avec la
# convention k::n de cell_05.py:323. A n=1 c'est l'identite.
_sh_expected = sorted(test_stems)[_SH_K::_SH_N]
geffs = geffs[_SH_K::_SH_N]
if _SH_N > 1:
    if sorted(p.stem for p in geffs) != _sh_expected:
        raise RuntimeError(f"shard {_SH_K}::{_SH_N} : tranche incoherente "
                           f"({len(geffs)} geff pour {len(_sh_expected)} attendus)")
    print(f"POSTPROC SHARD {_SH_K}::{_SH_N} -> {len(geffs)} films")

stats_rows: list[dict[str, object]] = []
seen_datasets: set[str] = set()
row_id = 0
total_nodes = 0
total_edges = 0

_SH_SUBMISSION_PATH = _sh_path(SUBMISSION_PATH)
with _SH_SUBMISSION_PATH.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
    writer.writeheader()

    for geff_path in geffs:
        dataset = geff_path.stem
        seen_datasets.add(dataset)
        graph = graph_from_geff(geff_path)
        dataset_shape = dataset_shape_tzyx(dataset)
        t_max, z_max, y_max, x_max = (value - 1 for value in dataset_shape)
        coordinate_clamp_counts = {"z": 0, "y": 0, "x": 0}

        nodes_by_id: dict[int, dict[str, object]] = {}
        for row in graph.node_attrs().iter_rows(named=True):
            node_id = int(row["node_id"])
            nodes_by_id[node_id] = {
                "node_id": node_id,
                "t": int(row["t"]),
                "z": float(row["z"]),
                "y": float(row["y"]),
                "x": float(row["x"]),
            }

        raw_edges: list[dict[str, object]] = []
        for row in graph.edge_attrs().iter_rows(named=True):
            edge_prob = row.get("edge_prob") if hasattr(row, "get") else None
            raw_edges.append({
                "source_id": int(row["source_id"]),
                "target_id": int(row["target_id"]),
                "edge_prob": None if edge_prob is None else float(edge_prob),
            })

        raw_node_count = len(nodes_by_id)
        nodes_by_id, edges, filter_stats = filter_output_graph(nodes_by_id, raw_edges, dataset=dataset, deepcenter_bundle=DEEPCENTER_VETO_DETECTOR)
        if not nodes_by_id:
            raise AssertionError(f"{dataset}: post-processing removed every node")

        for node_id in sorted(nodes_by_id):
            node = nodes_by_id[node_id]
            node_t = int(node["t"])
            if not 0 <= node_t <= t_max:
                raise AssertionError(f"{dataset}: node {node_id} has out-of-range t={node_t}")
            raw_spatial = {
                "z": int(round(float(node["z"]))),
                "y": int(round(float(node["y"]))),
                "x": int(round(float(node["x"]))),
            }
            bounded_spatial = {
                "z": clamp_spatial_coordinate(node["z"], z_max),
                "y": clamp_spatial_coordinate(node["y"], y_max),
                "x": clamp_spatial_coordinate(node["x"], x_max),
            }
            for axis in coordinate_clamp_counts:
                coordinate_clamp_counts[axis] += int(raw_spatial[axis] != bounded_spatial[axis])
            writer.writerow({
                "id": row_id,
                "dataset": dataset,
                "row_type": "node",
                "node_id": int(node["node_id"]),
                "t": node_t,
                "z": bounded_spatial["z"],
                "y": bounded_spatial["y"],
                "x": bounded_spatial["x"],
                "source_id": -1,
                "target_id": -1,
            })
            row_id += 1

        division_sources: dict[int, int] = {}
        for edge in edges:
            source_id = int(edge["source_id"])
            target_id = int(edge["target_id"])
            if source_id not in nodes_by_id or target_id not in nodes_by_id:
                raise AssertionError(f"{dataset}: dangling edge after filtering")
            writer.writerow({
                "id": row_id,
                "dataset": dataset,
                "row_type": "edge",
                "node_id": -1,
                "t": -1,
                "z": -1,
                "y": -1,
                "x": -1,
                "source_id": source_id,
                "target_id": target_id,
            })
            row_id += 1
            division_sources[source_id] = division_sources.get(source_id, 0) + 1

        node_count = len(nodes_by_id)
        edge_count = len(edges)
        total_nodes += node_count
        total_edges += edge_count
        stats_rows.append({
            "dataset": dataset,
            "raw_nodes": raw_node_count,
            "nodes": node_count,
            "raw_edges": filter_stats["raw_edges"],
            "edges": edge_count,
            "division_like_sources": sum(1 for count in division_sources.values() if count >= 2),
            "edge_to_node_ratio": edge_count / max(node_count, 1),
            "gap_added_nodes_frac": filter_stats.get("gap_added_nodes", 0) / max(raw_node_count, 1),
            "coordinate_clamps_z": coordinate_clamp_counts["z"],
            "coordinate_clamps_y": coordinate_clamp_counts["y"],
            "coordinate_clamps_x": coordinate_clamp_counts["x"],
            "coordinate_clamps_total": sum(coordinate_clamp_counts.values()),
            **filter_stats,
        })

expected_datasets = set(_sh_expected)
missing_datasets = sorted(expected_datasets - seen_datasets)
extra_datasets = sorted(seen_datasets - expected_datasets)
if missing_datasets or extra_datasets:
    raise AssertionError({"missing": missing_datasets[:10], "extra": extra_datasets[:10]})
assert row_id == total_nodes + total_edges, "Internal row counter mismatch"
assert total_nodes > 0, "No node rows produced"

header = _SH_SUBMISSION_PATH.open().readline().strip().split(",")
assert header == CSV_COLUMNS, f"Bad CSV header: {header}"

stats = pd.DataFrame(stats_rows).sort_values("dataset").reset_index(drop=True)
stats["predict_minutes_total"] = predict_seconds / 60.0
stats["experiment_tag"] = EXPERIMENT_TAG
stats.to_csv(_sh_path(RUN_STATS_PATH), index=False)

print(f"Wrote {_SH_SUBMISSION_PATH} with {row_id:,} rows")
print(f"Node rows: {total_nodes:,} | edge rows: {total_edges:,}")
print(f"Wrote {_sh_path(RUN_STATS_PATH)}")
display(pd.read_csv(_SH_SUBMISSION_PATH, nrows=8))
