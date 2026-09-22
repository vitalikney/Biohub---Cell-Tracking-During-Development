"""Build an LB-probe kernel = exp29 realised config + env-knob overrides (+ optional DivNet veto), one command.

    python tools/build_probe_kernel.py exp40_relink_off --set MOTION_RELINK_TIGHT_UM=0 --set DEEPCENTER_GAP_THRESHOLD=0.35 \
        --divnet 0 --note "relink off" [--push]

Base = experiments/exp39_sjlee947_tight55_divnetveto (exp29 + DivNet veto cell). `--divnet 0` disables the veto through
BIOHUB_DIVNET_VERIFY=0 (the cell stays, the model is not loaded), so `--divnet 0` with no --set is exp29 bit-for-bit.
Knob names are given WITHOUT the BIOHUB_ prefix. Overrides are appended to the config cell AFTER the base values and the
configuration guard's expected values are patched for the keys it checks. Output folder:
experiments/<name>/ with the notebook, kernel-metadata.json and probe.json; `--push` runs `kaggle kernels push`.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = ROOT / "experiments/exp39_sjlee947_tight55_divnetveto"
BASE_NB = BASE_DIR / "exp39-sjlee947-tight55-divnetveto.ipynb"
NL = chr(10)


def _rep1(s: str, old: str, new: str) -> str:
    assert s.count(old) == 1, f"anchor count {s.count(old)} != 1: {old[:70]!r}"
    return s.replace(old, new)


def patch_gshift(cells_src: dict) -> None:
    """takaito/biohub-a951-gshift (2026-09-22): per-frame global displacement = median of mutual-nearest-neighbour
    shifts between consecutive frames (MNN radius BIOHUB_MOTION_RELINK_GLOBAL_SHIFT_MNN_UM, default 8; his run: 12),
    subtracted inside the motion relink cost (raw distance and velocity prediction). Ported line for line; the only
    difference is that our relink has no density-adaptive per-call velocity/bonus overrides (we use the constants)."""
    c2 = cells_src[2]
    c2 = _rep1(c2, 'MOTION_RELINK_LEARNED_BONUS = float(os.environ.get("BIOHUB_MOTION_RELINK_LEARNED_BONUS", "0.75"))' + NL,
               'MOTION_RELINK_LEARNED_BONUS = float(os.environ.get("BIOHUB_MOTION_RELINK_LEARNED_BONUS", "0.75"))' + NL
               + 'MOTION_RELINK_GLOBAL_SHIFT = os.environ.get("BIOHUB_MOTION_RELINK_GLOBAL_SHIFT", "0") != "0"' + NL
               + 'MOTION_RELINK_GLOBAL_SHIFT_MNN_UM = float(os.environ.get("BIOHUB_MOTION_RELINK_GLOBAL_SHIFT_MNN_UM", "8.0"))' + NL
               + 'MOTION_RELINK_GLOBAL_SHIFT_MIN_PAIRS = int(os.environ.get("BIOHUB_MOTION_RELINK_GLOBAL_SHIFT_MIN_PAIRS", "20"))' + NL
               + 'MOTION_RELINK_GLOBAL_SHIFT_MIN_UM = float(os.environ.get("BIOHUB_MOTION_RELINK_GLOBAL_SHIFT_MIN_UM", "0.0"))' + NL)
    cells_src[2] = c2
    c7 = cells_src[7]
    c7 = _rep1(c7, '''    position_um = {node_id: _position_um(node) for node_id, node in nodes_by_id.items()}
    predecessor_position_um: dict[int, np.ndarray] = {}
    selected_edges: list[dict[str, object]] = []

    def assign_pass(
        source_ids: list[int],
        target_ids: list[int],
        gate_um: float,
    ) -> list[tuple[int, int, float, float, float]]:
        if not source_ids or not target_ids:
            return []
''', '''    position_um = {node_id: _position_um(node) for node_id, node in nodes_by_id.items()}
    predecessor_position_um: dict[int, np.ndarray] = {}
    selected_edges: list[dict[str, object]] = []

    # --- gshift: per-frame global displacement (median of mutual-nearest-neighbour shifts) ---
    _zero_shift = np.zeros(3, dtype=np.float64)
    global_shift_um: dict[int, np.ndarray] = {}
    if MOTION_RELINK_GLOBAL_SHIFT:
        for _t in sorted(ids_by_t):
            if _t + 1 not in ids_by_t:
                continue
            _src = np.stack([position_um[i] for i in ids_by_t[_t]])
            _tgt = np.stack([position_um[i] for i in ids_by_t[_t + 1]])
            if len(_src) < MOTION_RELINK_GLOBAL_SHIFT_MIN_PAIRS or len(_tgt) < MOTION_RELINK_GLOBAL_SHIFT_MIN_PAIRS:
                continue
            _d1, _j = cKDTree(_tgt).query(_src, distance_upper_bound=MOTION_RELINK_GLOBAL_SHIFT_MNN_UM)
            _d2, _i = cKDTree(_src).query(_tgt, distance_upper_bound=MOTION_RELINK_GLOBAL_SHIFT_MNN_UM)
            _pairs = [(a, int(_j[a])) for a in range(len(_src)) if np.isfinite(_d1[a]) and _i[int(_j[a])] == a]
            if len(_pairs) < MOTION_RELINK_GLOBAL_SHIFT_MIN_PAIRS:
                continue
            _shift = np.median(np.stack([_tgt[b] - _src[a] for a, b in _pairs]), axis=0)
            if float(np.linalg.norm(_shift)) < MOTION_RELINK_GLOBAL_SHIFT_MIN_UM:
                continue
            global_shift_um[_t] = _shift
        stats["motion_relink_global_shift_frames"] = len(global_shift_um)
        stats["motion_relink_global_shift_sum_um"] = float(
            sum(float(np.linalg.norm(v)) for v in global_shift_um.values())
        )

    def assign_pass(
        source_ids: list[int],
        target_ids: list[int],
        gate_um: float,
        shift_um: np.ndarray = _zero_shift,
        prev_shift_um: np.ndarray = _zero_shift,
    ) -> list[tuple[int, int, float, float, float]]:
        if not source_ids or not target_ids:
            return []
''')
    c7 = _rep1(c7, '''            prev_pos = predecessor_position_um.get(source_id)
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
''', '''            prev_pos = predecessor_position_um.get(source_id)
            shifted_pos = source_pos + shift_um
            if prev_pos is None:
                predicted = shifted_pos
            else:
                predicted = shifted_pos + MOTION_RELINK_VELOCITY_WEIGHT * (source_pos - prev_pos - prev_shift_um)
            for j, target_id in enumerate(target_ids):
                target_pos = position_um[target_id]
                raw_true = float(np.linalg.norm(target_pos - source_pos))
                raw = float(np.linalg.norm(target_pos - shifted_pos))
                if raw > gate_um:
                    continue
                motion = float(np.linalg.norm(target_pos - predicted))
                prob = learned_prob(source_id, target_id)
                raw_dist[i, j] = raw_true
''')
    c7 = _rep1(c7, '            matches = assign_pass(pass_sources, pass_targets, gate_um)' + NL,
               '            matches = assign_pass(' + NL
               + '                pass_sources,' + NL
               + '                pass_targets,' + NL
               + '                gate_um,' + NL
               + '                global_shift_um.get(t, _zero_shift),' + NL
               + '                global_shift_um.get(t - 1, _zero_shift),' + NL
               + '            )' + NL)
    cells_src[7] = c7


PATCHES = {"gshift": patch_gshift}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="folder/kernel name, e.g. exp40_relink_off (lowercase, digits, _ or -)")
    ap.add_argument("--set", action="append", default=[], help="KNOB=value (without BIOHUB_), repeatable")
    ap.add_argument("--divnet", choices=["0", "1"], default="1", help="DivNet veto on (1, exp39) or off (0, exp29)")
    ap.add_argument("--note", default="", help="one line for probe.json")
    ap.add_argument("--patch", action="append", default=[], choices=sorted(PATCHES), help="code surgery to apply, repeatable")
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]+", a.name):
        sys.exit("name must be lowercase letters/digits/_/-")
    overrides = {}
    for item in a.set:
        k, _, v = item.partition("=")
        if not k or not _:
            sys.exit(f"bad --set {item!r}")
        overrides["BIOHUB_" + k.strip().removeprefix("BIOHUB_")] = v.strip()
    overrides["BIOHUB_DIVNET_VERIFY"] = a.divnet

    nb = json.load(open(BASE_NB, encoding="utf-8"))
    cells = nb["cells"]
    code = [i for i, c in enumerate(cells) if c["cell_type"] == "code"]

    def src(i):
        return "".join(cells[i]["source"])

    def set_src(i, s):
        cells[i]["source"] = s.splitlines(keepends=True)
        cells[i]["outputs"] = []
        cells[i]["execution_count"] = None

    c0 = src(code[0])
    assert "BIOHUB_PRESET = 'exp39_sjlee947_tight55_divnetveto'" in c0
    c0 = c0.replace("BIOHUB_PRESET = 'exp39_sjlee947_tight55_divnetveto'", f"BIOHUB_PRESET = '{a.name}'")
    block = NL + f"# ---- {a.name}: probe overrides (tools/build_probe_kernel.py) ----" + NL
    block += NL.join(f'os.environ["{k}"] = "{v}"' for k, v in overrides.items()) + NL
    c0 = c0.rstrip(NL) + NL + block
    set_src(code[0], c0)

    c1 = src(code[1])
    for k, v in overrides.items():
        m = re.search(r'^(\s*"%s": )([^,\n]+),' % re.escape(k), c1, re.M)
        if m:
            c1 = c1[:m.start(2)] + (v if re.fullmatch(r"-?\d+(\.\d+)?", v) else json.dumps(v)) + c1[m.end(2):]
    set_src(code[1], c1)

    if a.patch:
        cells_src = {k: src(code[k]) for k in range(len(code))}
        for name in a.patch:
            PATCHES[name](cells_src)
        for k, s in cells_src.items():
            if s != src(code[k]):
                set_src(code[k], s)
        overrides["PATCHES"] = "+".join(a.patch)

    out_dir = ROOT / "experiments" / a.name
    out_dir.mkdir(exist_ok=True)
    nb_name = a.name.replace("_", "-") + ".ipynb"
    json.dump(nb, open(out_dir / nb_name, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    for i in code:
        compile(src(i), f"cell{i}", "exec")
    meta = json.load(open(BASE_DIR / "kernel-metadata.json"))
    slug = "biohub-" + a.name.replace("_", "-")
    meta["id"] = "vitaliineibauer/" + slug
    meta["title"] = slug
    meta["code_file"] = nb_name
    json.dump(meta, open(out_dir / "kernel-metadata.json", "w", encoding="utf-8"), indent=1)
    probe = {
        "base": "exp29 realised config (tight55, pilkwang primary, validator off) = LB 0.947; built by tools/build_probe_kernel.py from the exp39 notebook",
        "change": {k.removeprefix("BIOHUB_"): v for k, v in overrides.items()},
        "note": a.note,
        "rule": "compare with exp29 0.947; >= 0.950 adopt; ties recorded; <= 0.944 drop",
    }
    json.dump(probe, open(out_dir / "probe.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("built", out_dir.relative_to(ROOT), "overrides", overrides)
    if a.push:
        r = subprocess.run([sys.executable, "-m", "kaggle", "kernels", "push", "-p", str(out_dir)])
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
