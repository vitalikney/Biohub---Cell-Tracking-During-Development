"""L2 laptop CPU lab: replay our post-processing tail from Friend A's image-free cache, score with the official metric.

WHAT IT REPLAYS
    ckpt/<stem>.npz (post-gap checkpoint = the exact input of the shipped division stage)
      -> safe-division stage (one of the modes below)
      -> notebook tail through the notebook's OWN functions (division-geometry filter, prune-isolated, short-track
         filter, linefit; `filter_output_graph` of the exp29 post-processing cell with relink/gap/safe-div/DC-veto off,
         exactly the namespace experiments/local_friend_c_b31_cluster/runner.py builds)
      -> [optional] L2 division insertion AFTER linefit: tools/div_insert.insert_divisions with node p from --node-p
      -> coordinates rounded exactly like write_test_submission -> .geff -> OFFICIAL metric (tools/score_geffs.py)
    The raw -> ckpt part is NOT replayed: DeepCenter scores exist only at raw nodes, not at synthetic gap points
    (see experiments/local_friend_c_b31_cluster/README.md).

SAFE-DIVISION MODES (config key `safe_div`)
    public         exp29 control, friend C runner radius 0 verbatim: pass2_rank_divisions.candidates(9 um, k=3, add)
                   + public_key + apply.  Reference on all 199 videos: 0.9120275 / adj 0.9023109 / div 24/96/127.
    divnet_rerank  the run behind the exp39 local number (friend A B20 follow-up, pass2_public_rerank.py --ranker
                   divnet --parent-um 12 --sister-min-um 5 --min-score 0.5): public orphans <= 12 um, sister >= 5 um,
                   public hard gates/caps/DC veto, parents ordered by DivNet p, p >= 0.5.
                   Reference on all 199: 0.9143003 / adj 0.9024446 / div 23/43/128.   (preset `exp39`)
    divnet_veto    the exp39 notebook's RULE on top of the `public` port: public order, gates and caps (as `public`),
                   candidates whose parent has DivNet p < 0.5 are dropped (missing p = dropped, counted).  NOT the
                   notebook verbatim: the p2 port has no mutual-NN gate and its frame cap counts candidates, not
                   sources (same approximation as the exp29 control).  No reference number yet.  (`exp39_veto`)
    off            no safe divisions (exp45-like diagnostic).                                     (preset `nodiv`)

INSERTION (config key `insert=1`; `ins.<name>=<value>` sets a key of div_insert.DIVINS_DEFAULT_PARAMS, e.g.
    ins.cap_video=6 ins.steal=1 ins.alpha=0.5 ins.threshold=0.3)
    tools/div_insert.insert_divisions - the module the kernel embeds (--patch divinsert), so replay and kernel run one
    code path - on the FINAL (post-linefit) graph, with node p from --node-p (parquet/csv: stem, node_id, p_cont,
    p_par, p_dau [, t, z, y, x]; with coordinates present they are checked against the replayed graph).
    Node flags given to div_insert exactly as in the patched kernel: gap_synthetic from the ckpt, gap2_synthetic for
    ckpt nodes that are neither raw (absent from dc/) nor gap_synthetic (recover_strict_gap2 nodes).

LEAF PRUNE (config key `leaf_prune=<min_edge_prob>`, default 0 = off; plan L4)
    prune_weak_leaf_nodes VERBATIM from the public notebook seyitkaangunes/biohub-035-deconfounded-edge-stack, at that
    notebook's position in filter_output_graph: after short-track filtering, before linefit.  The notebook cells are
    patched by the SAME source functions the kernel builder uses (tools/build_probe_kernel.py leafprune_config_source /
    leafprune_postproc_source, --patch leafprune), and the namespace global LEAF_PRUNE_MIN_EDGE_PROB is set per tail
    task; so `leaf_prune=p` ships as `--patch leafprune --set LEAF_PRUNE_MIN_EDGE_PROB=p`.  It changes the tail, so it
    is part of the base key when > 0 (leaf_prune=0 keeps the old base keys and cached tails: the call is skipped).

EDGE FILTER (config keys `ef.<param>=<value>`; any ef.* key switches it on unless ef.enable=0; plan L5)
    edgefilter_final_graph from tools/build_probe_kernel.py (--patch edgefilter, source text applied to the replayed
    notebook cells like leafprune) on the post-tail graph, BEFORE insertion - the kernel's position (right after
    linefit, before the divinsert call).  Params = the kernel knobs (bpk.EDGEFILTER_KNOBS): enable, max_prob, alt,
    min_len_um, relink, prune, skip_forks; `ef.max_prob=0.3,ef.relink=1` ships as `--patch edgefilter --set
    EDGEFILTER_ENABLE=1 --set EDGEFILTER_RELINK=1` (the report prints the exact line).  The linker's own edges it needs
    (`ilp_probs`) are raw/<stem>.geff through the notebook's next-frame / OUTPUT_EDGE_MAX_UM filter = the kernel's
    capture before the motion relink.  Not part of the base key (applied post-tail); part of the config fingerprint.

EXPORT (--export-coords PATH)
    For every node involved in div_insert.candidate_triples of the FINAL (post-linefit, pre-insertion) graph of
    --export-base (default exp39), write rows stem,node_id,t,z,y,x (float voxel coordinates of the full-resolution
    frame, exactly the node dicts the kernel hands to daughternet.score_nodes) to PATH (.parquet or .csv), plus
    PATH.json with counts and the base fingerprint.  Candidate params = the base config's ins.* with steal=1 forced
    (superset for steal configs) unless --export-orphan-only; --export-param k=v overrides (e.g. steal_prob_max=1.01).

OUTPUTS (under --out, default .public_local_cache/l2_replay/<cache tag>, git-ignored)
    tail/<base_key>/<stem>.npz        post-tail graph per safe-division base (shared by all insertion configs)
    progress/<config>.jsonl           one row per finished video: stats + official per-video metric row (resume key)
    configs/<config>.json             resolved config + fingerprint (a changed config under the same name is refused)
    report_<split>.{md,json}          all / 44b6 / 6bba summaries, node ratio and paired bootstrap vs --control
    per_video_<split>.csv             per-video rows of every config
    predictions/<config>/<stem>.geff  only with --keep-geff

USAGE
    python experiments/l2_daughternet/replay/replay.py --cache <pkg>/cache/friend_a_b20_exp29 --split all \
        --configs exp29_control exp39 --control exp39 --workers 4
    python experiments/l2_daughternet/replay/replay.py --cache ... --split all --export-coords coords.parquet
    python experiments/l2_daughternet/replay/replay.py --cache ... --split selection --node-p p_oof.parquet \
        --config "ins3=exp39,insert=1,ins.cap_video=3" --config "ins6=exp39,insert=1,ins.cap_video=6" \
        --control exp39
    Cooperative stop: create <out>/STOP; finished videos are kept and the next launch resumes.
    Synthetic smoke cache (code-path test only, NOT a control):  --make-synthetic-cache DIR --stems A B
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import importlib
import importlib.util
import io
import json
import os
import shutil
import sys
import time
import warnings
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path
from typing import Any

import numpy as np

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TOOLS = ROOT / "tools"
for _p in (TOOLS, ROOT / "experiments" / "local_friend_b_exp02_public_port"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


def _import_file(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Reused verbatim: friend C's CPU runner (tail namespace, atomic GEFF save, control reference) and friend A's re-rank
# functions (the exp39 local number).  Both import pass2_rank_divisions and public_local from the same sys.path.
fc = _import_file("friend_c_b31_runner", ROOT / "experiments" / "local_friend_c_b31_cluster" / "runner.py")
rr = _import_file("friend_a_b20_rerank", ROOT / "experiments" / "local_friend_a_b20_divnet" / "pass2_public_rerank.py")
p2 = fc.p2
pl = fc.pl
# Kernel builder: its --patch leafprune source surgery is applied to the replayed notebook cells (one code path).
bpk = _import_file("build_probe_kernel", TOOLS / "build_probe_kernel.py")

DEFAULT_SPLITS = ROOT / "experiments" / "l2_daughternet" / "splits.json"
TAIL_VERSION = 1  # bump when the tail/base computation in this file changes
# Reused code the cached tails depend on: a change in any of these files gives new tail keys (no stale tails).
TAIL_SOURCES = (ROOT / "experiments" / "local_friend_c_b31_cluster" / "runner.py",
                ROOT / "experiments" / "local_friend_b_exp02_public_port" / "pass2_rank_divisions.py",
                ROOT / "experiments" / "local_friend_a_b20_divnet" / "pass2_public_rerank.py")
# div_insert params the kernel patch (tools/build_probe_kernel.py --patch divinsert, DIVINS_GLUE) can set via --set;
# a replay config that changes any other param cannot be shipped without extending the patch.
KERNEL_DIVINS_KNOBS = {"enable": "DIVINS_ENABLE", "steal": "DIVINS_STEAL", "cap_video": "DIVINS_CAP",
                       "cap_frame": "DIVINS_FRAME_CAP", "alpha": "DIVINS_ALPHA", "threshold": "DIVINS_THRESH"}
# (flag rebuilt by load_ckpt, counter the notebook stored in the ckpt) - compared per video
FLAG_CHECKS = (("ckpt_gap_synthetic", "ckpt_stats_gap_added_nodes"),
               ("ckpt_gap2_synthetic", "ckpt_stats_gap2_added_nodes"))

SAFE_DIV_DEFAULTS: dict[str, dict[str, Any]] = {
    "public": {"sd_parent_um": 9.0, "sd_k": 3},
    "divnet_rerank": {"sd_parent_um": 12.0, "sd_sister_min_um": 5.0, "divnet_min_p": 0.5},
    "divnet_veto": {"sd_parent_um": 9.0, "sd_k": 3, "divnet_min_p": 0.5},
    "off": {},
}
PRESETS: dict[str, dict[str, Any]] = {
    "exp29_control": {"safe_div": "public"},
    "exp39": {"safe_div": "divnet_rerank"},
    "exp39_veto": {"safe_div": "divnet_veto"},
    "nodiv": {"safe_div": "off"},
}
# All-199 references (official metric). exp29_control = friend C radius-0 / friend A control_public;
# exp39 = friend A b20_followup.json row "divnet_p_ge_0.5".
REFERENCES: dict[str, dict[str, float]] = {
    "exp29_control": dict(fc.REFERENCE_CONTROL),
    "exp39": {"score": 0.914300260391771, "adj_edge_jaccard": 0.9024445902886783,
              "division_tp": 23, "division_fp": 43, "division_fn": 128},
}
REFERENCE_VIDEOS = 199

# ------------------------------------------------------------------------------------------------ small utilities
def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _leafprune_sha() -> str:
    """Hash of the leafprune patch text (knob, function, counters, call, anchors): part of leaf_prune base keys."""
    parts = (bpk.LEAFPRUNE_KNOB, bpk.LEAFPRUNE_DISPLAY, bpk.LEAFPRUNE_FN, bpk.LEAFPRUNE_STATS, bpk.LEAFPRUNE_CALL,
             bpk._LP_SHORT_TRACK_PRINT, bpk._LP_LINEFIT_CALL)
    return _sha256_bytes("\0".join(parts).encode("utf-8"))[:16]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json_default(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"not JSON serialisable: {type(value)}")


def _dumps(obj, **kw) -> str:
    return json.dumps(obj, default=_json_default, **kw)


def _fingerprint(obj) -> str:
    return _sha256_bytes(_dumps(obj, sort_keys=True).encode("utf-8"))


def _atomic_replace(tmp: Path, dst: Path) -> None:
    for attempt in range(30):  # Windows: antivirus / a concurrent reader can hold the target briefly
        try:
            os.replace(tmp, dst)
            return
        except PermissionError:
            if attempt == 29:
                raise
            time.sleep(min(0.05 * (attempt + 1), 1.0))


def _atomic_npz(path: Path, **arrays) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.stem}.{os.getpid()}.tmp.npz")
    np.savez_compressed(tmp, **arrays)
    _atomic_replace(tmp, path)


def _atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    _atomic_replace(tmp, path)


def embryo_of(stem: str) -> str:
    return stem.split("_", 1)[0]


# ------------------------------------------------------------------------------------------------ configs
def _parse_value(text: str):
    low = text.strip().lower()
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    if low in ("none", "null"):
        return None
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return text


def parse_config_spec(spec: str) -> tuple[str, dict]:
    """'name=base,key=value,ins.alpha=0.5' -> (name, {'base': base, ...}).  A bare preset name is allowed."""
    if "=" not in spec.split(",", 1)[0]:
        name = spec.strip()
        if name not in PRESETS:
            raise SystemExit(f"unknown preset {name!r}; presets: {sorted(PRESETS)}")
        return name, {"base": name}
    head, *rest = [part.strip() for part in spec.split(",") if part.strip()]
    name, base = head.split("=", 1)
    raw: dict[str, Any] = {"base": base.strip()}
    for item in rest:
        key, _, value = item.partition("=")
        raw[key.strip()] = _parse_value(value)
    return name.strip(), raw


def resolve_config(name: str, raw: dict, defs: dict[str, dict]) -> dict:
    """Merge preset/base chain + overrides into a flat config: safe_div, sd_* params, insert, ins{}, node_p."""
    raw = dict(raw)
    base_name = raw.pop("base", None)
    if base_name is None or base_name == name:
        cfg = dict(PRESETS.get(name, {}))
        if not cfg and "safe_div" not in raw:
            raise SystemExit(f"config {name!r}: no base and no safe_div")
    elif base_name in defs and base_name != name:
        cfg = resolve_config(base_name, defs[base_name], defs)
        cfg = {k: (dict(v) if isinstance(v, dict) else v) for k, v in cfg.items() if k != "name"}
    elif base_name in PRESETS:
        cfg = dict(PRESETS[base_name])
    else:
        raise SystemExit(f"config {name!r}: unknown base {base_name!r}")
    cfg.setdefault("ins", {})
    cfg.setdefault("insert", False)
    cfg.setdefault("node_p", None)
    cfg.setdefault("leaf_prune", 0.0)
    cfg.setdefault("ef", {})
    ins = dict(cfg["ins"])
    ef = dict(cfg["ef"])
    for key, value in raw.items():
        if key.startswith("ins."):
            ins[key[4:]] = value
        elif key == "ins" and isinstance(value, dict):
            ins.update(value)
        elif key.startswith("ef."):
            ef[key[3:]] = value
        elif key == "ef" and isinstance(value, dict):
            ef.update(value)
        else:
            cfg[key] = value
    cfg["ins"] = ins
    cfg["ef"] = edgefilter_params(name, ef)
    mode = cfg.get("safe_div")
    if mode not in SAFE_DIV_DEFAULTS:
        raise SystemExit(f"config {name!r}: safe_div must be one of {sorted(SAFE_DIV_DEFAULTS)}, got {mode!r}")
    for key, value in SAFE_DIV_DEFAULTS[mode].items():
        cfg.setdefault(key, value)
    allowed = {"safe_div", "insert", "ins", "node_p", "leaf_prune", "ef", *SAFE_DIV_DEFAULTS[mode]}
    unknown = sorted(set(cfg) - allowed - {"name"})
    if unknown:
        raise SystemExit(f"config {name!r}: unknown keys {unknown} for safe_div={mode} (allowed {sorted(allowed)})")
    try:
        cfg["leaf_prune"] = float(cfg["leaf_prune"])
    except (TypeError, ValueError):
        raise SystemExit(f"config {name!r}: leaf_prune must be a number (0 = off), got {cfg['leaf_prune']!r}") from None
    if not np.isfinite(cfg["leaf_prune"]) or cfg["leaf_prune"] < 0.0:
        raise SystemExit(f"config {name!r}: leaf_prune must be finite and >= 0, got {cfg['leaf_prune']!r}")
    cfg["insert"] = bool(cfg["insert"])
    cfg["name"] = name
    return cfg


def edgefilter_params(name: str, overrides: dict) -> dict:
    """ef.* keys -> the full parameter dict of edgefilter_final_graph (kernel knob defaults, kernel types); {} = off.
    Any key switches the filter on unless enable is given explicitly."""
    if not overrides:
        return {}
    unknown = sorted(set(overrides) - set(bpk.EDGEFILTER_KNOBS))
    if unknown:
        raise SystemExit(f"config {name!r}: unknown ef keys {unknown} (kernel knobs: {sorted(bpk.EDGEFILTER_KNOBS)})")
    params = {}
    for key, (_knob, default) in bpk.EDGEFILTER_KNOBS.items():
        given = overrides.get(key, 1 if key == "enable" else default)
        try:
            value = float(given)
        except (TypeError, ValueError):
            raise SystemExit(f"config {name!r}: ef.{key} must be a number, got {given!r}") from None
        if not np.isfinite(value):
            raise SystemExit(f"config {name!r}: ef.{key} must be finite, got {given!r}")
        if default.isdigit():  # int knob in the kernel (the config cell calls int())
            if not value.is_integer():
                raise SystemExit(f"config {name!r}: ef.{key} must be an integer, got {given!r}")
            value = int(value)
        params[key] = value
    return params if params["enable"] else {}


def edgefilter_kernel_args(params: dict) -> str:
    """The build_probe_kernel.py arguments that ship an ef config (repr: the exact values the replay ran)."""
    parts = ["--patch edgefilter"]
    for key, (knob, default) in bpk.EDGEFILTER_KNOBS.items():
        value = params[key]
        if key == "enable" or float(value) != float(default):
            parts.append(f"--set {knob}={value!r}")
    return " ".join(parts)


def _edgefilter_sha() -> str:
    """Hash of the edgefilter patch text (knobs, function, capture, call, anchors): part of ef config fingerprints."""
    parts = (bpk.EDGEFILTER_KNOB, bpk.EDGEFILTER_DISPLAY, bpk.EDGEFILTER_FN, bpk.EDGEFILTER_CAPTURE,
             bpk.EDGEFILTER_CALL, bpk._EF_RELINK_ANCHOR, bpk._EF_FILTER_DEF, bpk._LP_LINEFIT_CALL,
             _dumps(bpk.EDGEFILTER_KNOBS, sort_keys=True))
    return _sha256_bytes("\0".join(parts).encode("utf-8"))[:16]


def base_params(cfg: dict) -> dict:
    """Everything the cached tail depends on. leaf_prune enters only when > 0, so leaf_prune=0 configs keep the base
    keys (and cached tails) of the code before plan L4: the guarded call is skipped, the tail is unchanged."""
    base = {"safe_div": cfg["safe_div"], **{k: cfg[k] for k in sorted(SAFE_DIV_DEFAULTS[cfg["safe_div"]])}}
    if float(cfg.get("leaf_prune", 0.0) or 0.0) > 0.0:
        base.update(leaf_prune=float(cfg["leaf_prune"]), leafprune_sha=_leafprune_sha())
    return base


def is_reference_config(cfg: dict) -> str | None:
    """Name of the reference this config must reproduce (default preset params, no insertion), else None."""
    for ref in REFERENCES:
        preset = PRESETS[ref]
        if (cfg["insert"] or cfg.get("leaf_prune", 0.0) > 0.0 or cfg.get("ef") or
                cfg["safe_div"] != preset["safe_div"]):
            continue
        if all(cfg[k] == v for k, v in SAFE_DIV_DEFAULTS[cfg["safe_div"]].items()):
            return ref
    return None


# ------------------------------------------------------------------------------------------------ div_insert binding
def _edge_maps(edges: list[dict]) -> tuple[dict[int, list[int]], dict[int, list[int]]]:
    succ: dict[int, list[int]] = {}
    pred: dict[int, list[int]] = {}
    for edge in edges:
        s, d = int(edge["source_id"]), int(edge["target_id"])
        succ.setdefault(s, []).append(d)
        pred.setdefault(d, []).append(s)
    return succ, pred


class DivInsert:
    """tools/div_insert.py, the SAME module the kernel embeds (--patch divinsert); no second implementation here."""

    def __init__(self) -> None:
        path = TOOLS / "div_insert.py"
        if not path.is_file():
            raise SystemExit("tools/div_insert.py not found (insertion and --export-coords need it)")
        self.module = importlib.import_module("div_insert")
        self.impl = "tools/div_insert.py"
        self.sha = _sha256_file(path)
        self.defaults = dict(self.module.DIVINS_DEFAULT_PARAMS)

    def resolve(self, overrides: dict) -> dict:
        try:
            params = self.module.divins_params(dict(overrides))
        except ValueError as exc:
            raise SystemExit(f"{exc}; accepted: {sorted(self.defaults)}") from None
        return json.loads(_dumps(params))  # tuples -> lists, numpy -> python: stable fingerprint, same values

    def triples(self, nodes_by_id, edges, params) -> list[tuple[int, int, int]]:
        return [tuple(int(x) for x in tr[:3]) for tr in self.module.candidate_triples(nodes_by_id, edges, params)]

    def insert(self, nodes_by_id, edges, node_p, params):
        new_edges, stats = self.module.insert_divisions(nodes_by_id, edges, node_p, params)
        return list(new_edges), dict(stats)


# ------------------------------------------------------------------------------------------------ cache I/O
def load_ckpt(cache: Path, stem: str):
    """ckpt + dc exactly as friend C's load_video, without the raw graph (peak_prob feeds no ranking used here)."""
    with np.load(cache / "ckpt" / f"{stem}.npz", allow_pickle=False) as ck:
        ids = np.asarray(ck["node_id"], dtype=np.int64)
        rows = np.asarray(ck["tzyx_syn"], dtype=np.float64)
        src = np.asarray(ck["src"], dtype=np.int64)
        dst = np.asarray(ck["dst"], dtype=np.int64)
        prob = np.asarray(ck["edge_prob"], dtype=np.float64)
        # pass1_extras stores filter_output_graph's own stats: used to self-check the synthetic-node flags below
        ck_stats = json.loads(str(ck["stats"])) if "stats" in ck.files else {}
    with np.load(cache / "dc" / f"{stem}.npz", allow_pickle=False) as dc:
        dcs = {int(i): float(v) for i, v in zip(np.asarray(dc["node_id"]), np.asarray(dc["dc"], dtype=np.float64))}
    # "syn" = gap_synthetic exactly as friend C / pass 2 read it (the safe-division pool excludes it); "gap2" = a node
    # that is neither raw (dc/ scores every raw node) nor gap_synthetic, i.e. a recover_strict_gap2 node, which the
    # patched kernel flags gap2_synthetic = 1 for div_insert.  Only div_insert reads the gap2 flag.
    nodes = {int(i): {"t": int(r[0]), "z": float(r[1]), "y": float(r[2]), "x": float(r[3]), "syn": int(r[4]),
                      "gap2": int(not int(r[4]) and int(i) not in dcs)}
             for i, r in zip(ids, rows)}
    edges = [(int(s), int(d), None if np.isnan(p) else float(p)) for s, d, p in zip(src, dst, prob)]
    expected = {f"ckpt_stats_{k}": int(ck_stats[k]) for k in ("gap_added_nodes", "gap2_added_nodes")
                if isinstance(ck_stats, dict) and k in ck_stats}
    return nodes, edges, dcs, expected


def safe_divisions(cfg: dict, cache: Path, stem: str, nodes, edges, dcs) -> tuple[list, dict]:
    mode = cfg["safe_div"]
    peak: dict[int, float] = {}
    if mode == "off":
        return list(edges), {"sd_candidates": 0, "sd_added": 0}
    if mode in ("public", "divnet_veto"):
        cands, succ, pred = p2.candidates(nodes, edges, dcs, peak, float(cfg["sd_parent_um"]), int(cfg["sd_k"]), "add")
        scores = np.asarray([(-key if (key := p2.public_key(f)) is not None else -np.inf) for *_, f in cands],
                            dtype=np.float64)
        stats = {"sd_candidates": len(cands)}
        if mode == "divnet_veto":
            parent_p = rr.load_parent_scores(cache / "divnet", stem)
            missing = vetoed = 0
            for index, (parent, *_rest) in enumerate(cands):
                p = parent_p.get(int(parent))
                if p is None:
                    missing += 1
                    scores[index] = -np.inf
                elif p < float(cfg["divnet_min_p"]):
                    vetoed += 1
                    scores[index] = -np.inf
            stats.update(sd_divnet_missing=missing, sd_divnet_vetoed=vetoed)
        new_edges, added = p2.apply(nodes, edges, cands, scores, succ, pred, "add", min_score=-np.inf)
        stats["sd_added"] = int(added)
        return new_edges, stats
    if mode == "divnet_rerank":
        cands, _, pred = p2.candidates(nodes, edges, dcs, peak, float(cfg["sd_parent_um"]), 0, "add")
        parent_p = rr.load_parent_scores(cache / "divnet", stem)
        scores, counts = rr.proposal_scores(cands, parent_p, "divnet", float(cfg["sd_sister_min_um"]))
        new_edges, added = rr.apply_public_caps(nodes, edges, cands, scores, pred, float(cfg["divnet_min_p"]))
        return new_edges, {"sd_candidates": counts["candidates"], "sd_eligible": counts["eligible"],
                           "sd_divnet_missing": counts["missing_scored_parents"], "sd_added": int(added)}
    raise ValueError(mode)


TAIL_STAT_KEYS = ("dropped_division_edges", "pruned_isolated_nodes", "short_track_components_removed",
                  "short_track_nodes_removed", "short_track_rescue_nodes", "leaf_prune_nodes", "leaf_prune_edges",
                  "linefit_smoothed_nodes")


def save_tail(path: Path, nodes_by_id: dict, edges: list[dict], stats: dict) -> None:
    ids = np.asarray(sorted(nodes_by_id), dtype=np.int64)
    _atomic_npz(
        path,
        node_id=ids,
        t=np.asarray([int(nodes_by_id[i]["t"]) for i in ids], dtype=np.int64),
        zyx=np.asarray([[float(nodes_by_id[i][k]) for k in ("z", "y", "x")] for i in ids], dtype=np.float64).reshape(-1, 3),
        syn=np.asarray([int(nodes_by_id[i].get("gap_synthetic", 0) or 0) for i in ids], dtype=np.int8),
        gap2=np.asarray([int(nodes_by_id[i].get("gap2_synthetic", 0) or 0) for i in ids], dtype=np.int8),
        src=np.asarray([int(e["source_id"]) for e in edges], dtype=np.int64),
        dst=np.asarray([int(e["target_id"]) for e in edges], dtype=np.int64),
        edge_prob=np.asarray([np.nan if e.get("edge_prob") is None else float(e["edge_prob"]) for e in edges],
                             dtype=np.float64),
        distance_um=np.asarray([float(e.get("distance_um", np.nan)) for e in edges], dtype=np.float64),
        stats=np.asarray(_dumps(stats)),
    )


def load_tail(path: Path) -> tuple[dict, list[dict], dict]:
    with np.load(path, allow_pickle=False) as z:
        ids, t, zyx, syn, gap2 = z["node_id"], z["t"], z["zyx"], z["syn"], z["gap2"]
        src, dst, prob, dist = z["src"], z["dst"], z["edge_prob"], z["distance_um"]
        stats = json.loads(str(z["stats"]))
    nodes = {}
    for i, tt, (zz, yy, xx), s, g2 in zip(ids.tolist(), t.tolist(), zyx.tolist(), syn.tolist(), gap2.tolist()):
        node = {"node_id": i, "t": tt, "z": zz, "y": yy, "x": xx}
        if s:
            node["gap_synthetic"] = 1
        if g2:
            node["gap2_synthetic"] = 1
        nodes[i] = node
    edges = []
    for s, d, p, dd in zip(src.tolist(), dst.tolist(), prob.tolist(), dist.tolist()):
        edge = {"source_id": s, "target_id": d, "edge_prob": None if p != p else p}
        if dd == dd:
            edge["distance_um"] = dd
        edges.append(edge)
    return nodes, edges, stats


def write_geff(path: Path, nodes_by_id: dict, edges: list[dict]) -> None:
    """Same rounding as write_test_submission / friend C _write_prediction."""
    import networkx as nx

    graph = nx.DiGraph()
    for node_id, node in nodes_by_id.items():
        graph.add_node(int(node_id), t=int(node["t"]),
                       z=float(max(0, round(float(node["z"])))),
                       y=float(max(0, round(float(node["y"])))),
                       x=float(max(0, round(float(node["x"])))))
    for edge in edges:
        graph.add_edge(int(edge["source_id"]), int(edge["target_id"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    fc._save_graph_atomic(graph, path)


def load_node_p_table(path: Path):
    import pandas as pd

    frame = (pd.read_parquet(path) if path.suffix.lower() in (".parquet", ".pq")
             else pd.read_csv(path, dtype={"stem": str}, float_precision="round_trip"))
    need = {"stem", "node_id", "p_cont", "p_par", "p_dau"}
    missing = need - set(frame.columns)
    if missing:
        raise SystemExit(f"--node-p {path}: missing columns {sorted(missing)} (have {list(frame.columns)})")
    frame = frame.copy()
    frame["stem"] = frame["stem"].astype(str)
    dup = frame.duplicated(["stem", "node_id"]).sum()
    if dup:
        raise SystemExit(f"--node-p {path}: {dup} duplicated (stem, node_id) rows")
    probs = frame[["p_cont", "p_par", "p_dau"]].to_numpy(np.float64)
    finite = np.isfinite(probs)
    if ((probs < 0.0) | (probs > 1.0))[finite].any():
        raise SystemExit(f"--node-p {path}: p outside [0, 1] (logits instead of softmax probabilities?)")
    row_ok = finite.all(axis=1)
    off = int(np.sum(np.abs(probs[row_ok].sum(axis=1) - 1.0) > 1e-3))
    if off:
        print(f"WARNING --node-p {path}: {off} rows whose p_cont + p_par + p_dau is not 1 (not a 3-class softmax?)",
              flush=True)
    return frame


def oof_check(frame, folds: dict[str, int] | None) -> dict:
    """Label-leakage guard. With a `fold` column (= held-out fold of the model that scored the row, as in
    kdn_train's OOF files) every row must carry its video's fold from splits.json; otherwise p for a video came from a
    model trained on it and the replay numbers are optimistic. Without the column OOF cannot be verified (reported)."""
    if "fold" not in frame.columns:
        return {"status": "UNVERIFIED", "detail": "no fold column: cannot check that p is out-of-fold"}
    if not folds:
        return {"status": "UNVERIFIED", "detail": "fold column present but no splits.json folds to compare with"}
    want = frame["stem"].map(lambda s: folds.get(str(s), -999)).to_numpy()
    have = frame["fold"].to_numpy()
    bad = frame.loc[want != have, "stem"]
    if len(bad):
        raise SystemExit(f"node-p leakage guard: {len(bad)} rows in {bad.nunique()} videos (e.g. {sorted(set(bad))[:3]}) "
                         "have fold != the video's fold in splits.json, i.e. p from a model that trained on the video")
    return {"status": "PASS", "detail": f"all {len(frame)} rows scored by their video's held-out fold model"}


def split_node_p(path: Path, out_dir: Path, folds: dict[str, int] | None = None) -> Path:
    """Split the node-p table into per-stem npz files once (workers then load only their video)."""
    target = out_dir / "node_p" / _sha256_file(path)[:16]
    done = target / "_done.json"
    if done.is_file() and "oof" in json.loads(done.read_text(encoding="utf-8")):
        return target
    frame = load_node_p_table(path)
    oof = oof_check(frame, folds)
    has_xyz = all(c in frame.columns for c in ("t", "z", "y", "x"))
    for stem, group in frame.groupby("stem", sort=True):
        arrays = {"node_id": group["node_id"].to_numpy(np.int64),
                  "p": group[["p_cont", "p_par", "p_dau"]].to_numpy(np.float64)}
        if has_xyz:
            arrays["tzyx"] = group[["t", "z", "y", "x"]].to_numpy(np.float64)
        _atomic_npz(target / f"{stem}.npz", **arrays)
    _atomic_text(done, _dumps({"source": str(path.resolve()), "rows": len(frame), "stems": int(frame["stem"].nunique()),
                               "has_coordinates": has_xyz, "oof": oof}, indent=2))
    return target


def flag_self_check(per_video: dict[str, dict]) -> dict | None:
    """Rebuilt synthetic-node flags (gap_synthetic from the ckpt, gap2 = not raw and not gap_synthetic) vs the
    notebook's own counters stored in each ckpt, per video (totals alone could cancel out)."""
    totals: dict[str, int] = {}
    bad: list[str] = []
    checked = 0
    for stem, stats in sorted(per_video.items()):
        pairs = [(flag, stat) for flag, stat in FLAG_CHECKS if stat in stats and flag in stats]
        if not pairs:
            continue
        checked += 1
        for flag, stat in pairs:
            totals[flag] = totals.get(flag, 0) + int(stats[flag])
            totals[stat] = totals.get(stat, 0) + int(stats[stat])
        if any(int(stats[flag]) != int(stats[stat]) for flag, stat in pairs):
            bad.append(stem)
    if not checked:
        return None
    return {"status": "OK" if not bad else "MISMATCH", "videos_checked": checked, "videos_mismatch": len(bad),
            "mismatch_examples": bad[:5], "totals": totals}


def load_node_p(node_p_dir: Path, stem: str) -> tuple[dict[int, tuple], np.ndarray | None, np.ndarray | None]:
    path = node_p_dir / f"{stem}.npz"
    if not path.is_file():
        return {}, None, None
    with np.load(path, allow_pickle=False) as z:
        ids = np.asarray(z["node_id"], dtype=np.int64)
        p = np.asarray(z["p"], dtype=np.float64)
        tzyx = np.asarray(z["tzyx"], dtype=np.float64) if "tzyx" in z.files else None
    return {int(i): (float(a), float(b), float(c)) for i, (a, b, c) in zip(ids.tolist(), p.tolist())}, ids, tzyx


# ------------------------------------------------------------------------------------------------ worker context
_CTX: dict[str, Any] = {}


def _patched_notebook_cells(original):
    """pl.notebook_cells with the kernel builder's leafprune source surgery applied to the constants cell (knob) and the
    post-processing cell (prune_weak_leaf_nodes + counters + guarded call before linefit), found by the same needles
    public_local uses. With LEAF_PRUNE_MIN_EDGE_PROB = 0 the call is skipped and the tail is the unpatched one."""
    def cells_for(path):
        cells = list(original(path))
        const = pl.find_cell(cells, "COMP_DIR_CANDIDATES", "CONFIG_DISPLAY")
        post = pl.find_cell(cells, "def filter_output_graph", "def add_safe_divisions_postlink")
        cells[const] = bpk.leafprune_config_source(cells[const])
        cells[post] = bpk.leafprune_postproc_source(cells[post])
        # edgefilter (plan L5): same text as --patch edgefilter; its in-tail call stays off here (the replay runs the
        # function on the post-tail graph in run_config_video, see compute_tail / run_config_video)
        cells[const] = bpk.edgefilter_config_source(cells[const])
        cells[post] = bpk.edgefilter_postproc_source(cells[post])
        return cells
    return cells_for


def init_context(settings: dict) -> None:
    """Build the notebook tail namespace, scorer and insertion adapter (once per process)."""
    if _CTX.get("settings") == settings:
        return
    os.environ["BIOHUB_DATA_DIR"] = settings["data_dir"]
    shim = type("TailCfg", (), {"output_dir": Path(settings["out"]), "data_dir": Path(settings["data_dir"])})
    original_cells = pl.notebook_cells
    pl.notebook_cells = _patched_notebook_cells(original_cells)  # friend C's _tail_namespace reads cells through it
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            namespace = fc._tail_namespace(shim)
    finally:
        pl.notebook_cells = original_cells
    if "prune_weak_leaf_nodes" not in namespace or "LEAF_PRUNE_MIN_EDGE_PROB" not in namespace:
        raise RuntimeError("leafprune patch did not reach the tail namespace")
    if "edgefilter_final_graph" not in namespace or "EDGEFILTER_PARAMS" not in namespace:
        raise RuntimeError("edgefilter patch did not reach the tail namespace")
    scorer = importlib.import_module("score_geffs")
    if Path(str(scorer.DATA)).resolve() != Path(settings["data_dir"]).resolve():
        raise RuntimeError(f"score_geffs was imported with DATA={scorer.DATA}, expected {settings['data_dir']}")
    _CTX.clear()
    _CTX.update(
        settings=settings,
        cache=Path(settings["cache"]),
        out=Path(settings["out"]),
        filter_output_graph=namespace["filter_output_graph"],
        namespace=namespace,
        scorer=scorer,
        div_insert=DivInsert() if settings["need_insert"] else None,
    )


def compute_tail(cfg: dict, stem: str) -> dict:
    """ckpt -> safe divisions -> notebook tail; saved to tail/<base_key>/<stem>.npz."""
    cache = _CTX["cache"]
    started = time.time()
    nodes, edges, dcs, expected = load_ckpt(cache, stem)
    edges, sd_stats = safe_divisions(cfg, cache, stem, nodes, edges, dcs)
    node_records = {i: {"node_id": i, "t": n["t"], "z": n["z"], "y": n["y"], "x": n["x"],
                        **({"gap_synthetic": 1} if n["syn"] else {}), **({"gap2_synthetic": 1} if n["gap2"] else {})}
                    for i, n in nodes.items()}
    edge_records = [{"source_id": s, "target_id": d, "edge_prob": p} for s, d, p in edges]
    # the kernel reads BIOHUB_LEAF_PRUNE_MIN_EDGE_PROB once in its config cell; here one namespace serves every base
    _CTX["namespace"]["LEAF_PRUNE_MIN_EDGE_PROB"] = float(cfg.get("leaf_prune", 0.0) or 0.0)
    # the in-tail edgefilter call must stay off whatever BIOHUB_EDGEFILTER_* says (tails are shared by ef configs)
    _CTX["namespace"]["EDGEFILTER_PARAMS"] = {"enable": 0}
    with contextlib.redirect_stdout(io.StringIO()):
        node_records, edge_records, tail_stats = _CTX["filter_output_graph"](
            node_records, edge_records, dataset=stem, deepcenter_bundle=None)
    stats = {"ckpt_nodes": len(nodes), "ckpt_gap_synthetic": sum(n["syn"] for n in nodes.values()),
             "ckpt_gap2_synthetic": sum(n["gap2"] for n in nodes.values()), **expected, **sd_stats,
             **{k: int(tail_stats.get(k, 0)) for k in TAIL_STAT_KEYS},
             "tail_nodes": len(node_records), "tail_edges": len(edge_records),
             "tail_seconds": round(time.time() - started, 3)}
    save_tail(Path(cfg["_tail_path"]) / f"{stem}.npz", node_records, edge_records, stats)
    return {"stem": stem, "base_key": cfg["_base_key"], "stats": stats}


def load_ilp_probs(cache: Path, stem: str) -> dict[tuple[int, int], float]:
    """The linker's edges as filter_output_graph holds them before the motion relink: raw/<stem>.geff (the notebook's
    post-processing input; edge_anatomy re-runs the notebook's relink on it and reproduces every ckpt) through the
    notebook's own first loop (both endpoints known, next frame, edge_distance_um <= OUTPUT_EDGE_MAX_UM), finite p,
    max per pair - what the kernel's edgefilter capture builds."""
    ns = _CTX["namespace"]
    graph = fc._load_raw_graph(cache / "raw" / f"{stem}.geff")
    na, ea = graph.node_attrs(), graph.edge_attrs()
    raw_nodes = {int(i): {"t": int(t), "z": float(z), "y": float(y), "x": float(x)}
                 for i, t, z, y, x in zip(na["node_id"].to_list(), na["t"].to_list(), na["z"].to_list(),
                                          na["y"].to_list(), na["x"].to_list())}
    probs: dict[tuple[int, int], float] = {}
    for s, d, p in zip(ea["source_id"].to_list(), ea["target_id"].to_list(), ea["edge_prob"].to_list()):
        a, b = raw_nodes.get(int(s)), raw_nodes.get(int(d))
        if a is None or b is None:
            continue
        if ns["OUTPUT_ENFORCE_NEXT_FRAME"] and int(b["t"]) != int(a["t"]) + 1:
            continue
        if ns["OUTPUT_EDGE_MAX_UM"] > 0 and ns["edge_distance_um"](a, b) > ns["OUTPUT_EDGE_MAX_UM"]:
            continue
        if p is None or not np.isfinite(float(p)):
            continue
        key = (int(s), int(d))
        probs[key] = max(probs.get(key, float("-inf")), float(p))
    return probs


def export_video(cfg: dict, stem: str, params: dict) -> dict:
    nodes, edges, tail_stats = load_tail(Path(cfg["_tail_path"]) / f"{stem}.npz")
    triples = _CTX["div_insert"].triples(nodes, edges, params)
    involved = sorted({i for tr in triples for i in tr})
    rows = np.asarray([[nodes[i]["t"], nodes[i]["z"], nodes[i]["y"], nodes[i]["x"]] for i in involved],
                      dtype=np.float64).reshape(-1, 4)
    flags = {k: tail_stats[k] for pair in FLAG_CHECKS for k in pair if k in tail_stats}
    return {"stem": stem, "node_id": np.asarray(involved, dtype=np.int64), "tzyx": rows, "triples": len(triples),
            "flags": flags}


def run_config_video(cfg: dict, stem: str) -> dict:
    """Tail (cached) -> optional insertion -> GEFF -> official per-video metric row."""
    started = time.time()
    nodes, edges, tail_stats = load_tail(Path(cfg["_tail_path"]) / f"{stem}.npz")
    stats = dict(tail_stats)
    if cfg.get("ef"):
        ef_stats: dict = {}
        nodes, edges = _CTX["namespace"]["edgefilter_final_graph"](nodes, [dict(e) for e in edges], ef_stats,
                                                                   dict(cfg["ef"]), load_ilp_probs(_CTX["cache"], stem))
        stats.update(ef_stats)
    if cfg["insert"]:
        node_p, p_ids, p_tzyx = load_node_p(Path(cfg["_node_p_dir"]), stem)
        stats["node_p_rows"] = len(node_p)
        if p_tzyx is not None and len(p_ids):
            present = [k for k, i in enumerate(p_ids.tolist()) if i in nodes]
            stats["node_p_absent_from_graph"] = int(len(p_ids) - len(present))
            if present:
                ours = np.asarray([[nodes[int(p_ids[k])][c] for c in ("t", "z", "y", "x")] for k in present])
                stats["node_p_coord_mismatch"] = int(np.sum(np.abs(ours - p_tzyx[present]).max(axis=1) > 1e-3))
        edges, ins_stats = _CTX["div_insert"].insert(nodes, [dict(e) for e in edges], node_p, dict(cfg["_ins_params"]))
        stats.update(ins_stats)
    out = _CTX["out"]
    geff = out / "predictions" / cfg["name"] / f"{stem}.geff"
    write_geff(geff, nodes, edges)
    with contextlib.redirect_stdout(io.StringIO()):
        _, rows = _CTX["scorer"].score([geff], quiet=True)
    metric = {k: (v.item() if hasattr(v, "item") else v) for k, v in rows[0].items()}
    if not cfg["_keep_geff"]:
        shutil.rmtree(geff, ignore_errors=True)
    stats.update(final_nodes=len(nodes), final_edges=len(edges),
                 final_forks=sum(1 for v in _edge_maps(edges)[0].values() if len(v) >= 2))
    return {"dataset": stem, "config": cfg["name"], "config_fp": cfg["_fp"], "stats": stats, "metric": metric,
            "seconds": round(time.time() - started, 3)}


def _task(kind: str, cfg: dict, stem: str, settings: dict, extra: dict | None = None) -> dict:
    init_context(settings)
    if kind == "tail":
        return compute_tail(cfg, stem)
    if kind == "export":
        return export_video(cfg, stem, extra["params"])
    return run_config_video(cfg, stem)


# ------------------------------------------------------------------------------------------------ scheduling
def stop_requested(out: Path) -> bool:
    return (out / "STOP").exists()


_POOL: dict[str, Any] = {}


def _pool(workers: int) -> ProcessPoolExecutor:
    """One worker pool for all phases (each worker builds the notebook namespace once, ~10 s)."""
    if "pool" not in _POOL:
        _POOL["pool"] = ProcessPoolExecutor(max_workers=workers)
    return _POOL["pool"]


def close_pool() -> None:
    pool = _POOL.pop("pool", None)
    if pool is not None:
        pool.shutdown(wait=True, cancel_futures=True)


def run_tasks(tasks: list[tuple], settings: dict, workers: int, on_result, label: str) -> None:
    """Run (kind, cfg, stem, extra) tasks; results are handled in the main process in completion order."""
    out = Path(settings["out"])
    total = len(tasks)
    if not total:
        return
    started = time.time()
    done = 0

    def report(result):
        nonlocal done
        done += 1
        on_result(result)
        if done == total or done % max(1, total // 20) == 0:
            rate = (time.time() - started) / done
            print(f"  [{label}] {done}/{total}  {rate:.2f} s/task  eta {rate * (total - done) / 60:.1f} min", flush=True)

    if workers <= 1:
        init_context(settings)
        for kind, cfg, stem, extra in tasks:
            if stop_requested(out):
                raise KeyboardInterrupt(f"STOP file present in {out}; finished work is kept")
            report(_task(kind, cfg, stem, settings, extra))
        return
    pending = list(reversed(tasks))
    pool = _pool(workers)
    running = set()
    while pending or running:
        while pending and len(running) < 2 * workers and not stop_requested(out):
            kind, cfg, stem, extra = pending.pop()
            running.add(pool.submit(_task, kind, cfg, stem, settings, extra))
        if not running:
            raise KeyboardInterrupt(f"STOP file present in {out}; finished work is kept")
        finished, running = wait(running, return_when=FIRST_COMPLETED)
        for future in finished:
            report(future.result())


# ------------------------------------------------------------------------------------------------ summaries
def _metrics_module():
    importlib.import_module("score_geffs")  # puts tools/official/src on sys.path
    return importlib.import_module("tracking_cellmot.metrics")


def summarise_rows(rows: list[dict]) -> dict | None:
    if not rows:
        return None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        s = _metrics_module().summarise(rows)
    s = {k: (float(v) if isinstance(v, (int, float, np.integer, np.floating)) else v) for k, v in s.items()}
    s["videos"] = len(rows)
    s["num_pred_nodes"] = int(sum(int(r["num_pred_nodes"]) for r in rows))
    return s


def _score_vectors(rows: list[dict]) -> dict[str, np.ndarray]:
    def col(name):
        return np.asarray([float(r[name]) for r in rows], dtype=np.float64)

    edge_tp = col("edge_tp")
    valid = edge_tp == edge_tp
    w = np.where(valid, col("edge_tp") + col("edge_fp") + col("edge_fn"), 0.0)
    adj = col("adj_edge_jaccard")
    adj_ok = valid & (adj == adj)
    return {
        "wa": np.where(adj_ok, w * np.nan_to_num(adj), 0.0),
        "w": np.where(adj_ok, w, 0.0),
        "tp": np.where(valid, np.nan_to_num(col("division_tp")), 0.0),
        "fp": np.where(valid, np.nan_to_num(col("division_fp")), 0.0),
        "fn": np.where(valid, np.nan_to_num(col("division_fn")), 0.0),
    }


def _scores_from_counts(counts: np.ndarray, vec: dict[str, np.ndarray], div_weight: float) -> np.ndarray:
    with np.errstate(invalid="ignore", divide="ignore"):
        adj = (counts @ vec["wa"]) / (counts @ vec["w"])
        tp, fp, fn = counts @ vec["tp"], counts @ vec["fp"], counts @ vec["fn"]
        total = tp + fp + fn
        div_j = np.where(total > 0, tp / np.where(total > 0, total, 1.0), 0.0)
    return np.where(total > 0, adj + div_weight * div_j, adj)


def paired_bootstrap(rows_cfg: list[dict], rows_ctrl: list[dict], draws: int, seed: int) -> dict | None:
    if not rows_cfg:
        return None
    n = len(rows_cfg)
    div_weight = float(_metrics_module().SCORE_DIVISION_WEIGHT)
    vc, vk = _score_vectors(rows_cfg), _score_vectors(rows_ctrl)
    ones = np.ones((1, n))
    point = float(_scores_from_counts(ones, vc, div_weight)[0] - _scores_from_counts(ones, vk, div_weight)[0])
    official = summarise_rows(rows_cfg)["score"] - summarise_rows(rows_ctrl)["score"]
    if not np.isclose(point, official, atol=1e-12, rtol=0):
        raise RuntimeError(f"bootstrap score formula disagrees with official summarise: {point} vs {official}")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(draws, n))
    counts = np.zeros((draws, n), dtype=np.float64)
    np.add.at(counts, (np.repeat(np.arange(draws), n), idx.ravel()), 1.0)
    delta = _scores_from_counts(counts, vc, div_weight) - _scores_from_counts(counts, vk, div_weight)
    delta = delta[np.isfinite(delta)]
    return {"videos": n, "draws": int(len(delta)), "seed": seed, "delta": official,
            "boot_mean": float(delta.mean()), "ci90_lo": float(np.percentile(delta, 5)),
            "ci90_hi": float(np.percentile(delta, 95)), "p_delta_gt_0": float(np.mean(delta > 0)),
            "p_delta_lt_0": float(np.mean(delta < 0))}


def _video_score(metric: dict) -> float:
    adj = float(metric["adj_edge_jaccard"])
    tp, fp, fn = (float(metric[k]) for k in ("division_tp", "division_fp", "division_fn"))
    return adj + 0.1 * tp / (tp + fp + fn) if tp + fp + fn > 0 else adj


def check_reference(ref: str, summary: dict) -> dict:
    expect = REFERENCES[ref]
    failures = []
    for key in ("score", "adj_edge_jaccard"):
        if abs(float(summary[key]) - float(expect[key])) > 5e-6:
            failures.append(f"{key} {summary[key]:.7f} != {expect[key]:.7f}")
    for key in ("division_tp", "division_fp", "division_fn"):
        if int(summary[key]) != int(expect[key]):
            failures.append(f"{key} {int(summary[key])} != {int(expect[key])}")
    return {"reference": ref, "status": "PASS" if not failures else "FAIL", "failures": failures, "expected": expect}


# ------------------------------------------------------------------------------------------------ synthetic cache
def make_synthetic_cache(root: Path, stems: list[str], data_dir: Path, seed: int = 0) -> Path:
    """Fake Friend-A package from GT (code-path smoke test only; scores are meaningless, NOT a control).

    ckpt = GT nodes + small jitter; the edge to the second daughter of every GT division is removed (orphan daughter,
    or - for every other division - re-attached by a low-probability edge to a decoy single-child track, i.e. a steal
    candidate); isolated distractors; 3% of interior nodes flagged gap_synthetic, 2% left out of dc/ and raw/ (they
    look like recover_strict_gap2 nodes); dc/divnet/peak scores random with GT-informed means.
    """
    import networkx as nx

    rng = np.random.default_rng(seed)
    cache = root / "cache" / "synthetic"
    for sub in ("ckpt", "dc", "divnet", "raw"):
        (cache / sub).mkdir(parents=True, exist_ok=True)
    manifest = {"format": "biohub-friend-c-b31-cache-v1 (SYNTHETIC from GT, smoke test only)", "tag": "synthetic",
                "seed": seed, "stems": stems, "videos": {}}
    for stem in stems:
        gt = fc._load_raw_graph(data_dir / f"{stem}.geff")
        na, ea = gt.node_attrs(), gt.edge_attrs()
        ids = na["node_id"].to_numpy().astype(np.int64)
        coords = {int(i): [int(t), float(z), float(y), float(x)] for i, t, z, y, x in zip(
            ids, na["t"].to_numpy(), na["z"].to_numpy(), na["y"].to_numpy(), na["x"].to_numpy())}
        edges = {(int(s), int(d)) for s, d in zip(ea["source_id"].to_numpy(), ea["target_id"].to_numpy())}
        succ: dict[int, list[int]] = {}
        for s, d in sorted(edges):
            succ.setdefault(s, []).append(d)
        nodes = {i: [c[0], c[1] + rng.normal(0, 0.15), c[2] + rng.normal(0, 0.6), c[3] + rng.normal(0, 0.6), 0]
                 for i, c in coords.items()}
        next_id = int(max(nodes)) + 1
        low_prob: set[tuple[int, int]] = set()
        parents = sorted(s for s, ch in succ.items() if len(ch) >= 2)
        daughters = set()
        for k, parent in enumerate(parents):
            kids = sorted(succ[parent])
            daughters.update(kids)
            orphan = kids[1]
            edges.discard((parent, orphan))
            if k % 2 == 1:  # decoy predecessor chain ending at the orphan -> steal candidate
                t0, z0, y0, x0 = nodes[orphan][:4]
                prev = None
                for back in (3, 2, 1):
                    if t0 - back < 0:
                        continue
                    nodes[next_id] = [t0 - back, z0 + 1.0, y0 + 9.0, x0 - 6.0, 0]
                    if prev is not None:
                        edges.add((prev, next_id))
                    prev = next_id
                    next_id += 1
                if prev is not None:
                    edges.add((prev, orphan))
                    low_prob.add((prev, orphan))
        for i in list(coords):
            if rng.random() < 0.08:
                t0, z0, y0, x0 = nodes[i][:4]
                nodes[next_id] = [t0, z0 + rng.uniform(-2, 2), y0 + rng.uniform(12, 18), x0 + rng.uniform(-8, 8), 0]
                next_id += 1
        indeg: dict[int, int] = {}
        outdeg: dict[int, int] = {}
        for s, d in edges:
            outdeg[s] = outdeg.get(s, 0) + 1
            indeg[d] = indeg.get(d, 0) + 1
        gap2 = set()
        for i in nodes:
            if indeg.get(i, 0) == 1 and outdeg.get(i, 0) == 1 and i not in daughters and i not in parents:
                draw = rng.random()
                if draw < 0.03:
                    nodes[i][4] = 1
                elif draw < 0.05:
                    gap2.add(i)
        node_ids = np.asarray(sorted(nodes), dtype=np.int64)
        tzyx = np.asarray([nodes[i] for i in node_ids], dtype=np.float32)
        edge_list = sorted(edges)
        probs = rng.uniform(0.55, 0.99, size=len(edge_list)).astype(np.float32)
        probs[rng.random(len(edge_list)) < 0.1] = np.nan
        for k, e in enumerate(edge_list):
            if e in low_prob:
                probs[k] = rng.uniform(0.05, 0.25)
        np.savez_compressed(cache / "ckpt" / f"{stem}.npz", node_id=node_ids, tzyx_syn=tzyx,
                            src=np.asarray([e[0] for e in edge_list], dtype=np.int64),
                            dst=np.asarray([e[1] for e in edge_list], dtype=np.int64),
                            edge_prob=probs, stats=json.dumps({"synthetic": 1, "gap_added_nodes": int(tzyx[:, 4].sum()),
                                                               "gap2_added_nodes": len(gap2)}))
        real = [int(i) for i in node_ids if not nodes[int(i)][4] and int(i) not in gap2]
        dc = rng.uniform(0.25, 1.0, size=len(real))
        dc[rng.random(len(real)) < 0.1] = rng.uniform(0.0, 0.2)
        np.savez_compressed(cache / "dc" / f"{stem}.npz", node_id=np.asarray(real, dtype=np.int64),
                            dc=dc.astype(np.float32))
        outd: dict[int, int] = {}
        for s, _ in edge_list:
            outd[s] = outd.get(s, 0) + 1
        single = sorted(i for i, c in outd.items() if c == 1)
        score = np.asarray([rng.uniform(0.7, 0.95) if i in parents else rng.beta(1.0, 5.0) for i in single])
        np.savez_compressed(cache / "divnet" / f"{stem}.npz", p=np.asarray(single, dtype=np.int64),
                            score=score.astype(np.float32))
        raw = nx.DiGraph()
        for i in real:
            t, z, y, x, _ = nodes[i]
            raw.add_node(i, t=int(t), z=float(z), y=float(y), x=float(x), peak_prob=float(rng.uniform(0.9, 1.0)))
        raw.add_edges_from((s, d) for s, d in edge_list if s in raw and d in raw)
        fc.postproc.save(raw, cache / "raw" / f"{stem}.geff")
        manifest["videos"][stem] = {"nodes": len(nodes), "edges": len(edge_list), "gt_divisions": len(parents),
                                    "synthetic_nodes": int(tzyx[:, 4].sum()), "gap2_like_nodes": len(gap2),
                                    "low_prob_decoy_edges": len(low_prob)}
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return cache


# ------------------------------------------------------------------------------------------------ main
def select_stems(args, cache: Path, need_divnet: bool) -> list[str]:
    ckpt = {p.stem for p in (cache / "ckpt").glob("*.npz")}
    if not ckpt:
        raise SystemExit(f"no ckpt/*.npz under {cache} (pass --cache <pkg>/cache/<tag>)")
    if args.stems:
        wanted = list(args.stems)
    elif args.split == "all":
        wanted = sorted(ckpt)
    else:
        splits = json.loads(Path(args.splits).read_text(encoding="utf-8"))
        wanted = sorted(splits[args.split])
    missing = {"ckpt": sorted(set(wanted) - ckpt),
               "dc": sorted(s for s in wanted if not (cache / "dc" / f"{s}.npz").is_file())}
    if need_divnet:
        missing["divnet"] = sorted(s for s in wanted if not (cache / "divnet" / f"{s}.npz").is_file())
    missing = {k: v for k, v in missing.items() if v}
    if missing:
        detail = "; ".join(f"{k}: {len(v)} e.g. {v[:3]}" for k, v in missing.items())
        if not args.allow_partial:
            raise SystemExit(f"cache incomplete for split {args.split!r} ({detail}); --allow-partial to use the rest")
        drop = set().union(*missing.values())
        print(f"WARNING: dropping {len(drop)} stems missing from the cache ({detail})", flush=True)
        wanted = [s for s in wanted if s not in drop]
    if not args.stems and args.split == "all" and args.expected_videos and len(wanted) != args.expected_videos:
        raise SystemExit(f"expected {args.expected_videos} videos, found {len(wanted)} (--expected-videos 0 disables)")
    if not wanted:
        raise SystemExit("no videos selected")
    return wanted


def cache_fingerprint(cache: Path) -> str:
    """Content hash of ckpt/, dc/, divnet/ (tails and results are only valid for these exact files)."""
    digest = hashlib.sha256()
    for sub in ("ckpt", "dc", "divnet"):
        for path in sorted((cache / sub).glob("*.npz")):
            digest.update(f"{sub}/{path.name}:{_sha256_file(path)}".encode("utf-8"))
    return digest.hexdigest()


def read_progress(path: Path, fp: str) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                if row.get("config_fp") == fp:
                    rows[str(row["dataset"])] = row
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache", help="<pkg>/cache/<tag> with ckpt/, dc/, divnet/ (raw/ is not read)")
    ap.add_argument("--data-dir", default=str(pl.DEFAULT_DATA), help="train dir with GT <stem>.geff")
    ap.add_argument("--out", default="", help="output dir (default .public_local_cache/l2_replay/<cache tag>)")
    ap.add_argument("--split", choices=["selection", "confirmation", "all"], default="all")
    ap.add_argument("--splits", default=str(DEFAULT_SPLITS))
    ap.add_argument("--stems", nargs="*", default=[], help="explicit videos (overrides --split; smoke tests)")
    ap.add_argument("--expected-videos", type=int, default=REFERENCE_VIDEOS, help="checked for --split all; 0 = off")
    ap.add_argument("--allow-partial", action="store_true", help="drop split videos that are missing from the cache")
    ap.add_argument("--configs", nargs="*", default=[], help="preset names: " + ", ".join(PRESETS))
    ap.add_argument("--config", action="append", default=[], metavar="NAME=BASE,k=v,...",
                    help="custom config; keys: safe_div, sd_parent_um, sd_k, sd_sister_min_um, divnet_min_p, "
                         "leaf_prune (0 = off), insert, node_p, ins.<div_insert param>, ef.<edgefilter param>")
    ap.add_argument("--grid", default="", help="JSON {name: {base: ..., key: value, ins: {...}}}")
    ap.add_argument("--control", default="exp39", help="config the paired bootstrap compares against")
    ap.add_argument("--node-p", default="", help="parquet/csv stem,node_id,p_cont,p_par,p_dau[,t,z,y,x]")
    ap.add_argument("--export-coords", default="", help="write triple-node coordinates of --export-base to this file")
    ap.add_argument("--export-base", default="exp39")
    ap.add_argument("--export-orphan-only", action="store_true", help="do not force steal candidates into the export")
    ap.add_argument("--export-param", action="append", default=[], metavar="K=V",
                    help="div_insert param override for the export's candidate_triples, repeatable")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--keep-geff", action="store_true", help="keep prediction GEFFs (default: scored then deleted)")
    ap.add_argument("--reset", nargs="*", default=[], help="forget stored results of these config names")
    ap.add_argument("--make-synthetic-cache", default="", metavar="DIR",
                    help="write a synthetic package from the GT of --stems into DIR and exit (smoke test only)")
    args = ap.parse_args()

    data_dir = Path(args.data_dir).resolve()
    t_start = time.time()

    def phase(msg: str) -> None:
        print(f"[{time.time() - t_start:7.1f} s] {msg}", flush=True)

    if args.make_synthetic_cache:
        if not args.stems:
            raise SystemExit("--make-synthetic-cache needs --stems")
        make_synthetic_cache(Path(args.make_synthetic_cache), list(args.stems), data_dir, args.seed)
        return
    if not args.cache:
        raise SystemExit("--cache is required")
    cache = Path(args.cache).resolve()
    out = Path(args.out).resolve() if args.out else ROOT / ".public_local_cache" / "l2_replay" / cache.name
    out.mkdir(parents=True, exist_ok=True)

    # ---- configs
    defs: dict[str, dict] = {}
    for name in args.configs:
        defs[name] = parse_config_spec(name)[1]
    for spec in args.config:
        name, raw = parse_config_spec(spec)
        defs[name] = raw
    if args.grid:
        for name, raw in json.loads(Path(args.grid).read_text(encoding="utf-8")).items():
            defs[name] = dict(raw)
    if not defs and not args.export_coords:
        defs = {"exp29_control": {"base": "exp29_control"}, "exp39": {"base": "exp39"}}
    if defs and args.control not in defs:
        if args.control not in PRESETS:
            raise SystemExit(f"--control {args.control!r} is neither a defined config nor a preset")
        defs = {args.control: {"base": args.control}, **defs}
    configs = {name: resolve_config(name, raw, defs) for name, raw in defs.items()}
    export_cfg = None
    if args.export_coords:
        raw = defs.get(args.export_base) or {"base": args.export_base}
        export_cfg = resolve_config(args.export_base, raw, {**defs, args.export_base: raw})

    need_insert = any(c["insert"] for c in configs.values()) or export_cfg is not None
    need_divnet = any(c["safe_div"].startswith("divnet") for c in [*configs.values(), *([export_cfg] if export_cfg else [])])
    stems = select_stems(args, cache, need_divnet)
    adapter = DivInsert() if need_insert else None

    run_manifest = {"cache": str(cache), "data_dir": str(data_dir), "cache_fp": cache_fingerprint(cache)}
    manifest_path = out / "run.json"
    if manifest_path.is_file() and json.loads(manifest_path.read_text(encoding="utf-8")) != run_manifest:
        raise SystemExit(f"{out} belongs to another cache, cache content or data dir ({manifest_path}); "
                         "use a different --out")
    _atomic_text(manifest_path, _dumps(run_manifest, indent=2))
    notebook_sha = _sha256_file(pl.DEFAULT_NOTEBOOK)
    tail_sources_sha = {path.name: _sha256_file(path) for path in TAIL_SOURCES}
    node_p_dirs: dict[str, Path] = {}
    node_p_info: dict[str, dict] = {}
    if any(c["insert"] for c in configs.values()):
        paths = {c["node_p"] or args.node_p for c in configs.values() if c["insert"]}
        if "" in paths or None in paths:
            raise SystemExit("an insertion config needs --node-p (or node_p=<path> in the config)")
        splits_path = Path(args.splits)
        folds = (json.loads(splits_path.read_text(encoding="utf-8")).get("folds") if splits_path.is_file() else None)
        node_p_dirs = {p: split_node_p(Path(p).resolve(), out, folds) for p in paths}
        for p, target in node_p_dirs.items():
            node_p_info[p] = json.loads((target / "_done.json").read_text(encoding="utf-8"))
            oof = node_p_info[p]["oof"]
            print(f"node-p {p}: {node_p_info[p]['rows']} rows, {node_p_info[p]['stems']} videos; "
                  f"OOF check {oof['status']} ({oof['detail']})", flush=True)
    settings = {"cache": str(cache), "data_dir": str(data_dir), "out": str(out),
                "need_insert": need_insert}

    def prepare(cfg: dict) -> dict:
        base = base_params(cfg)
        base_key = f"{cfg['safe_div']}_" + _fingerprint({"base": base, "notebook_sha": notebook_sha,
                                                          "tail_version": TAIL_VERSION,
                                                          "tail_sources_sha": tail_sources_sha})[:12]
        cfg = dict(cfg, _base_key=base_key, _tail_path=str(out / "tail" / base_key), _keep_geff=args.keep_geff)
        fp_payload = {"base_key": base_key, "insert": cfg["insert"]}
        if cfg.get("ef"):  # only when on: configs without ef keep their fingerprints (and stored rows)
            fp_payload.update(ef=cfg["ef"], edgefilter_sha=_edgefilter_sha())
        if cfg["insert"]:
            cfg["_ins_params"] = adapter.resolve(cfg["ins"])
            cfg["_node_p_dir"] = str(node_p_dirs[cfg["node_p"] or args.node_p])
            fp_payload.update(ins_params=cfg["_ins_params"], div_insert=adapter.impl, div_insert_sha=adapter.sha,
                              node_p_sha=Path(cfg["_node_p_dir"]).name)
        cfg["_fp"] = _fingerprint(fp_payload)[:16]
        (out / "tail" / base_key).mkdir(parents=True, exist_ok=True)
        _atomic_text(out / "tail" / base_key / "base.json", _dumps({"base": base, "notebook": str(pl.DEFAULT_NOTEBOOK),
                                                                    "notebook_sha": notebook_sha,
                                                                    "tail_version": TAIL_VERSION,
                                                                    "tail_sources_sha": tail_sources_sha}, indent=2))
        return cfg

    def kernel_unsupported(cfg: dict) -> list[str]:
        """div_insert params this config changes that the kernel patch has no --set knob for."""
        if not cfg["insert"]:
            return []
        defaults = adapter.resolve({})
        return sorted(k for k, v in cfg["_ins_params"].items() if k not in KERNEL_DIVINS_KNOBS and v != defaults.get(k))

    phase("cache fingerprint + node-p split done")
    configs = {name: prepare(cfg) for name, cfg in configs.items()}
    for name in args.reset:
        for path in (out / "progress" / f"{name}.jsonl", out / "configs" / f"{name}.json"):
            path.unlink(missing_ok=True)
    for name, cfg in configs.items():
        path = out / "configs" / f"{name}.json"
        public = {k: v for k, v in cfg.items() if not k.startswith("_") or k in ("_fp", "_base_key", "_ins_params")}
        if path.is_file():
            old = json.loads(path.read_text(encoding="utf-8"))
            if old.get("_fp") != cfg["_fp"]:
                raise SystemExit(f"config {name!r} changed since its results were stored (old fp {old.get('_fp')}, "
                                 f"new {cfg['_fp']}); use a new name or --reset {name}")
        _atomic_text(path, _dumps(public, indent=2, sort_keys=True))
    if export_cfg is not None:
        export_cfg = prepare(dict(export_cfg, insert=False))  # the export reads the PRE-insertion graph of its base

    print(f"cache {cache}\nout   {out}\nsplit {args.split}: {len(stems)} videos "
          f"(44b6 {sum(s.startswith('44b6') for s in stems)}, 6bba {sum(s.startswith('6bba') for s in stems)})",
          flush=True)
    for name, cfg in configs.items():
        extra = f" insert={adapter.impl} {cfg['_ins_params']}" if cfg["insert"] else ""
        print(f"  config {name}: {base_params(cfg)} base_key={cfg['_base_key']} fp={cfg['_fp']}{extra}", flush=True)
        if kernel_unsupported(cfg):
            print(f"  WARNING config {name}: div_insert params {kernel_unsupported(cfg)} have no kernel knob "
                  f"(--patch divinsert sets only {sorted(KERNEL_DIVINS_KNOBS)}); not shippable as is", flush=True)

    # ---- phase 1: post-tail graphs per (base, video)
    bases = {cfg["_base_key"]: cfg for cfg in [*configs.values(), *([export_cfg] if export_cfg else [])]}
    tail_tasks = [("tail", cfg, stem, None) for cfg in bases.values() for stem in stems
                  if not (Path(cfg["_tail_path"]) / f"{stem}.npz").is_file()]
    phase(f"phase 1: {len(tail_tasks)} tail tasks")
    run_tasks(tail_tasks, settings, args.workers, lambda r: None, "tail")

    # ---- phase 2: coordinate export
    if export_cfg is not None:
        overrides = dict(export_cfg["ins"])
        if not args.export_orphan_only:
            overrides["steal"] = 1
        for item in args.export_param:
            key, _, value = item.partition("=")
            overrides[key.strip()] = _parse_value(value)
        params = adapter.resolve(overrides)
        collected: list[dict] = []
        phase(f"phase 2: export of {len(stems)} videos")
        run_tasks([("export", export_cfg, stem, {"params": params}) for stem in stems], settings, args.workers,
                  collected.append, "export")
        collected.sort(key=lambda r: r["stem"])
        import pandas as pd

        frame = pd.DataFrame({
            "stem": pd.Series([r["stem"] for r in collected for _ in range(len(r["node_id"]))], dtype=str),
            "node_id": pd.Series([int(i) for r in collected for i in r["node_id"].tolist()], dtype=np.int64),
        })
        tzyx = np.concatenate([r["tzyx"] for r in collected] + [np.zeros((0, 4))])
        frame["t"] = tzyx[:, 0].astype(np.int64)
        for k, col in enumerate(("z", "y", "x"), start=1):
            frame[col] = tzyx[:, k]
        target = Path(args.export_coords).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.suffix.lower() in (".parquet", ".pq"):
            frame.to_parquet(target, index=False)
        else:
            frame.to_csv(target, index=False, float_format="%.17g")
        flags = flag_self_check({r["stem"]: r["flags"] for r in collected})
        side = {"file": str(target), "rows": len(frame), "videos": len(collected), "split": args.split,
                "export_base": args.export_base, "base_key": export_cfg["_base_key"], "base": base_params(export_cfg),
                "candidate_params": params, "div_insert": adapter.impl, "div_insert_sha": adapter.sha,
                "coordinates": "float voxel units of the full-resolution frame, post-linefit, pre-rounding",
                "flag_self_check": flags,
                "per_video": {r["stem"]: {"triples": r["triples"], "nodes": int(len(r["node_id"]))} for r in collected}}
        Path(str(target) + ".json").write_text(_dumps(side, indent=2), encoding="utf-8")
        print(f"EXPORT {target}: {len(frame)} node rows from "
              f"{sum(r['triples'] for r in collected)} triples over {len(collected)} videos", flush=True)
        if flags is not None:
            print(f"Synthetic-node flag self-check: {flags['status']} ({flags['videos_mismatch']}/"
                  f"{flags['videos_checked']} videos mismatch, e.g. {flags['mismatch_examples']}; {flags['totals']})",
                  flush=True)
        if not configs:
            return

    # ---- phase 3: per (config, video) insertion + scoring
    progress_dir = out / "progress"
    progress_dir.mkdir(parents=True, exist_ok=True)
    progress = {name: read_progress(progress_dir / f"{name}.jsonl", cfg["_fp"]) for name, cfg in configs.items()}
    tasks = [("run", cfg, stem, None) for name, cfg in configs.items() for stem in stems if stem not in progress[name]]
    print(f"{len(tasks)} (config, video) tasks to run, "
          f"{sum(len(v) for v in progress.values())} stored rows reused", flush=True)

    def on_result(row: dict) -> None:
        with (progress_dir / f"{row['config']}.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(_dumps(row) + "\n")
        progress[row["config"]][row["dataset"]] = row

    phase("phase 3: configs")
    run_tasks(tasks, settings, args.workers, on_result, "configs")
    phase("phase 4: report")

    # ---- phase 4: report
    control = args.control
    report = {"split": args.split, "videos": len(stems), "control": control, "cache": str(cache),
              "bootstrap": {"draws": args.bootstrap, "seed": args.seed, "resample": "videos, paired"}, "configs": {}}
    ctrl_rows = [progress[control][s]["metric"] for s in stems]
    csv_rows = []
    for name, cfg in configs.items():
        rows = [progress[name][s]["metric"] for s in stems]
        entry: dict[str, Any] = {"config": {k: v for k, v in cfg.items() if not k.startswith("_")},
                                 "fp": cfg["_fp"], "base_key": cfg["_base_key"]}
        for subset in ("all", "44b6", "6bba"):
            keep = [i for i, s in enumerate(stems) if subset == "all" or embryo_of(s) == subset]
            summary = summarise_rows([rows[i] for i in keep])
            if summary is not None:
                ctrl_nodes = sum(int(ctrl_rows[i]["num_pred_nodes"]) for i in keep)
                summary["node_ratio_vs_control"] = summary["num_pred_nodes"] / ctrl_nodes if ctrl_nodes else None
                summary["bootstrap_vs_control"] = (
                    None if name == control else
                    paired_bootstrap([rows[i] for i in keep], [ctrl_rows[i] for i in keep], args.bootstrap, args.seed))
            entry[subset] = summary
        stats_keys = sorted({k for s in stems for k in progress[name][s]["stats"]})
        entry["stats_total"] = {k: float(sum(float(progress[name][s]["stats"].get(k, 0) or 0) for s in stems))
                                for k in stats_keys}
        if kernel_unsupported(cfg):
            entry["kernel_unsupported_params"] = kernel_unsupported(cfg)
        ref = is_reference_config(cfg)
        if ref and args.split == "all" and not args.stems and len(stems) == REFERENCE_VIDEOS:
            entry["reference_check"] = check_reference(ref, entry["all"])
            print(f"REFERENCE {name} vs {ref}: {entry['reference_check']['status']} "
                  f"{entry['reference_check']['failures']}", flush=True)
        report["configs"][name] = entry
        for s in stems:
            m, st = progress[name][s]["metric"], progress[name][s]["stats"]
            csv_rows.append({"config": name, "dataset": s, "embryo": embryo_of(s), "video_score": _video_score(m),
                             **{k: m[k] for k in ("adj_edge_jaccard", "edge_jaccard", "edge_tp", "edge_fp", "edge_fn",
                                                  "division_tp", "division_fp", "division_fn", "num_pred_nodes",
                                                  "total_node_ratio", "node_recall")},
                             "ctrl_video_score": _video_score(progress[control][s]["metric"]),
                             **{k: st.get(k) for k in ("sd_added", "leaf_prune_nodes", "edgefilter_candidates",
                                                       "edgefilter_dropped", "edgefilter_relinked_fwd",
                                                       "edgefilter_relinked_bwd", "edgefilter_pruned_nodes",
                                                       "divins_triples",
                                                       "divins_missing_p", "divins_eligible", "divins_added",
                                                       "divins_added_steal", "final_nodes", "final_edges",
                                                       "final_forks")}})
    _atomic_text(out / f"report_{args.split}.json", _dumps(report, indent=2))
    with (out / f"per_video_{args.split}.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0]))
        writer.writeheader()
        writer.writerows(csv_rows)

    def fmt(x, spec=".6f"):
        return "-" if x is None or (isinstance(x, float) and x != x) else format(x, spec)

    lines = [f"# L2 replay - split `{args.split}` ({len(stems)} videos), control `{control}`", "",
             f"cache `{cache}`; official metric; paired bootstrap over videos ({args.bootstrap} draws, seed {args.seed}).",
             "", "| config | score | delta | 90% CI | P(d>0) | adj edge | div TP/FP/FN | 44b6 | d44b6 | 6bba | d6bba "
             "| node ratio |", "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, entry in report["configs"].items():
        a = entry["all"]
        b = a["bootstrap_vs_control"]
        sub = {k: entry.get(k) or {} for k in ("44b6", "6bba")}
        dsub = {k: (sub[k].get("bootstrap_vs_control") or {}).get("delta") for k in sub}
        ci = "-" if not b else "[%+.5f, %+.5f]" % (b["ci90_lo"], b["ci90_hi"])
        divs = "%d/%d/%d" % (int(a["division_tp"]), int(a["division_fp"]), int(a["division_fn"]))
        lines.append(
            f"| {name} | {fmt(a['score'])} | {fmt(b['delta'] if b else 0.0, '+.6f')} | {ci} | "
            f"{fmt(b['p_delta_gt_0'] if b else None, '.3f')} | {fmt(a['adj_edge_jaccard'])} | {divs} | "
            f"{fmt(sub['44b6'].get('score'))} | {fmt(dsub['44b6'], '+.6f')} | {fmt(sub['6bba'].get('score'))} | "
            f"{fmt(dsub['6bba'], '+.6f')} | {fmt(a['node_ratio_vs_control'], '.6f')} |")
    ins_lines = []
    for name, entry in report["configs"].items():
        tot = entry["stats_total"]
        if entry["config"]["insert"]:
            ins_lines.append(
                f"| {name} | {int(tot.get('divins_triples', 0))} | {int(tot.get('divins_triples_steal', 0))} | "
                f"{int(tot.get('divins_missing_p', 0))} | {int(tot.get('divins_eligible', 0))} | "
                f"{int(tot.get('divins_added', 0))} | {int(tot.get('divins_added_steal', 0))} | "
                f"{int(tot.get('node_p_coord_mismatch', 0))} |")
            if tot.get("divins_missing_p", 0):
                print(f"WARNING {name}: {int(tot['divins_missing_p'])} candidate triples had a node without p "
                      "(the node-p file does not cover the final graph of this base)", flush=True)
    if ins_lines:
        lines += ["", "| insertion config | triples | of which steal | missing p | eligible | added | added steal "
                  "| p coord mismatch |", "|---|---:|---:|---:|---:|---:|---:|---:|", *ins_lines]
        for name, entry in report["configs"].items():
            if entry.get("kernel_unsupported_params"):
                lines.append(f"\nWARNING `{name}`: div_insert params {entry['kernel_unsupported_params']} have no "
                             "kernel knob in --patch divinsert (not shippable without extending the patch).")
    if node_p_info:
        report["node_p"] = node_p_info
        for p, info in node_p_info.items():
            lines.append(f"\nnode-p `{p}`: {info['rows']} rows / {info['stems']} videos; OOF check "
                         f"**{info['oof']['status']}** ({info['oof']['detail']})")
    for name, entry in report["configs"].items():
        lp = float(entry["config"].get("leaf_prune", 0.0) or 0.0)
        if lp > 0.0:
            # repr, not :g - the shipped knob must be the exact threshold the replay ran (":g" keeps 6 digits)
            entry["kernel"] = f"--patch leafprune --set LEAF_PRUNE_MIN_EDGE_PROB={lp!r}"
            pruned = int(entry["stats_total"].get("leaf_prune_nodes", 0))
            lines.append(f"\n`{name}`: leaf_prune {lp:g} pruned {pruned} leaf nodes; "
                         f"kernel: tools/build_probe_kernel.py <name> {entry['kernel']}")
    for name, entry in report["configs"].items():
        ef = entry["config"].get("ef") or {}
        if ef:
            entry["kernel_edgefilter"] = edgefilter_kernel_args(ef)
            tot = entry["stats_total"]
            lines.append(f"\n`{name}`: edgefilter {ef}: candidates {int(tot.get('edgefilter_candidates', 0))}, dropped "
                         f"{int(tot.get('edgefilter_dropped', 0))}, re-linked {int(tot.get('edgefilter_relinked_fwd', 0))}"
                         f"+{int(tot.get('edgefilter_relinked_bwd', 0))}, pruned nodes "
                         f"{int(tot.get('edgefilter_pruned_nodes', 0))}; kernel: tools/build_probe_kernel.py <name> "
                         f"{entry['kernel_edgefilter']}")
    for name, entry in report["configs"].items():
        if "reference_check" in entry:
            rc = entry["reference_check"]
            lines.append(f"\nReference `{name}` vs `{rc['reference']}`: **{rc['status']}** {'; '.join(rc['failures'])}")
    # per-video self-check of the synthetic-node flags against the notebook's own counters stored in each ckpt
    # (the ckpt stats are the same for every base, so the first config's rows suffice)
    first = next(iter(configs))
    flags = flag_self_check({s: progress[first][s]["stats"] for s in stems})
    if flags is not None:
        report["flag_self_check"] = flags
        tot = flags["totals"]
        parts = [f"{flag} {tot.get(flag)} vs {stat} {tot.get(stat)}" for flag, stat in FLAG_CHECKS if stat in tot]
        examples = f", e.g. {flags['mismatch_examples']}" if flags["mismatch_examples"] else ""
        lines.append(f"\nSynthetic-node flag self-check: **{flags['status']}** ({flags['videos_mismatch']}/"
                     f"{flags['videos_checked']} videos mismatch{examples}; totals {'; '.join(parts)})")
    if report.get("flag_self_check") or node_p_info:
        _atomic_text(out / f"report_{args.split}.json", _dumps(report, indent=2))
    _atomic_text(out / f"report_{args.split}.md", "\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)
    phase("done")


if __name__ == "__main__":
    try:
        main()
    finally:
        close_pool()
