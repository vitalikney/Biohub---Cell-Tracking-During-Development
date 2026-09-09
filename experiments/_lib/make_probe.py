"""Build an LB-probe kernel folder from the exp06 base notebook (public 0.941 pipeline + exp03B primary = LB 0.945).

One probe = one (or, for a combination probe, a few) env overrides on top of the base. The script
  * renames BIOHUB_PRESET and sets/overrides `os.environ[KEY]` lines in the config cell (cell 0),
  * keeps the configuration guard (cell 1) consistent for numeric keys it checks,
  * re-applies the override in the setup cell (cell 3) for keys that cell re-sets (e.g. SECONDARY_*),
  * optionally swaps the secondary (seed314159) weights for a subfolder of vitaliineibauer/biohub-ft-weights
    (--secondary-override exp08) and relaxes the secondary SHA check in that case,
  * disables the validator (LB run), writes kernel-metadata.json and probe.json.

Example (candidate list in CONTEXT.md section 11a):
  python experiments/_lib/make_probe.py --name exp21_ft03B_minlen4 --env BIOHUB_OUTPUT_MIN_TRACK_LEN=4
  python experiments/_lib/make_probe.py --name exp22_ft03B_sec-exp08 --secondary-override exp08
  python experiments/_lib/make_probe.py --name exp23_ft03B_det095_secdet05 --env BIOHUB_DET_THRESHOLD=0.95 --env BIOHUB_SECONDARY_DETECTION_WEIGHT=0.5
Then: python -m kaggle kernels push -p experiments/<name>  (only when the probe protocol allows a new kernel).
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_NB = ROOT / "experiments/exp06_pipeline_ft03B/exp06-pipeline-ft03B.ipynb"
BASE_META = ROOT / "experiments/exp20_ft03B_secdet05/kernel-metadata.json"
BASE_PRESET = "exp06_pipeline_ft03B"

SECONDARY_OVERRIDE_CODE = '''# ---- probe: optional secondary-weights override from vitaliineibauer/biohub-ft-weights/<sub> ----
import shutil as _shutil
_sec_ovr = os.environ.get("BIOHUB_SECONDARY_OVERRIDE", "").strip()
if _sec_ovr:
    _sec_cands = [Path("/kaggle/input/datasets/vitaliineibauer/biohub-ft-weights") / _sec_ovr,
                  Path("/kaggle/input/biohub-ft-weights") / _sec_ovr]
    _sec_src = next((p for p in _sec_cands if (p / "edge_predictor_best.pth").exists()), None)
    if _sec_src is None:
        raise FileNotFoundError(f"secondary override weights not found: {_sec_cands}")
    for _f in ("edge_predictor_best.pth", "config.json"):
        _shutil.copy(_sec_src / _f, SECONDARY_WEIGHTS_PATH.parent / _f)
    print(f"SECONDARY OVERRIDE: {_sec_ovr} -> {SECONDARY_WEIGHTS_PATH}  config={SECONDARY_CONFIG_PATH.read_text()}")
_secondary_actual_sha256 = _sha256_file(SECONDARY_WEIGHTS_PATH)
if not _sec_ovr and _secondary_actual_sha256 != _secondary_expected_sha256:
'''
SHA_BLOCK_OLD = '''_secondary_actual_sha256 = _sha256_file(SECONDARY_WEIGHTS_PATH)
if _secondary_actual_sha256 != _secondary_expected_sha256:
'''


def _sub_once(src: str, pattern: str, repl: str, label: str) -> str:
    out, n = re.subn(pattern, repl, src, count=1, flags=re.M)
    if n != 1:
        raise RuntimeError(f"{label}: pattern not found: {pattern}")
    return out


def build(name: str, env: dict, secondary_override, note: str, out_root: Path, base_nb: Path = BASE_NB) -> Path:
    nb = json.loads(base_nb.read_text(encoding="utf-8"))
    cells = nb["cells"]
    src = ["".join(c["source"]) for c in cells]
    all_env = dict(env)
    if secondary_override:
        all_env["BIOHUB_SECONDARY_OVERRIDE"] = secondary_override
    all_env["BIOHUB_VALIDATOR_ENABLE"] = "0"

    # cell 0: preset + env
    c0 = _sub_once(src[0], r"^BIOHUB_PRESET = '" + BASE_PRESET + "'$", f"BIOHUB_PRESET = '{name}'", "preset")
    tail = [f"\n# ---- probe {name}: {note} ----"]
    for k, v in all_env.items():
        pat = r'^os\.environ\["' + k + r'"\] = .*$'
        line = f'os.environ["{k}"] = "{v}"  # probe {name}'
        if re.search(pat, c0, flags=re.M):
            c0 = _sub_once(c0, pat, line.replace("\\", "\\\\"), f"cell0 {k}")
        else:
            tail.append(line)
    src[0] = c0.rstrip("\n") + "\n" + "\n".join(tail) + "\n"

    # cell 1: configuration guard expected values
    for k, v in all_env.items():
        pat = r'^(\s*"' + k + r'": )[-0-9.eE]+,'
        if re.search(pat, src[1], flags=re.M):
            src[1] = _sub_once(src[1], pat, r"\g<1>" + repr(float(v)) + ",", f"guard {k}")

    # cell 3: the setup cell re-sets some keys -> override there too
    for k, v in all_env.items():
        pat = r'^os\.environ\["' + k + r'"\] = "[^"]*"'
        if re.search(pat, src[3], flags=re.M):
            src[3] = _sub_once(src[3], pat, f'os.environ["{k}"] = "{v}"  # probe {name}', f"cell3 {k}")
    if secondary_override:
        if src[3].count(SHA_BLOCK_OLD) != 1:
            raise RuntimeError("secondary sha block not found in setup cell")
        src[3] = src[3].replace(SHA_BLOCK_OLD, SECONDARY_OVERRIDE_CODE)

    for c, s in zip(cells, src):
        c["source"] = s.splitlines(keepends=True)
        if c["cell_type"] == "code":
            c["outputs"] = []
            c["execution_count"] = None

    out_dir = out_root / name
    out_dir.mkdir(parents=True, exist_ok=True)
    nb_name = name.replace("_", "-") + ".ipynb"
    (out_dir / nb_name).write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    meta = json.loads(BASE_META.read_text(encoding="utf-8"))
    slug = "biohub-" + name.replace("_", "-").lower()
    meta.update({"id": f"vitaliineibauer/{slug}", "title": slug, "code_file": nb_name})
    (out_dir / "kernel-metadata.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    (out_dir / "probe.json").write_text(json.dumps({"name": name, "base": BASE_PRESET, "env": all_env,
                                                    "secondary_override": secondary_override, "note": note}, indent=1),
                                        encoding="utf-8")
    return out_dir


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True, help="folder / preset name, e.g. exp21_ft03B_minlen4")
    ap.add_argument("--env", action="append", default=[], help="KEY=VALUE override (repeatable)")
    ap.add_argument("--secondary-override", default=None, help="subfolder of biohub-ft-weights to use as secondary")
    ap.add_argument("--note", default="", help="one-line description for probe.json / comments")
    ap.add_argument("--out-root", default=str(ROOT / "experiments"))
    a = ap.parse_args(argv)
    env = dict(kv.split("=", 1) for kv in a.env)
    note = a.note or ", ".join(f"{k}={v}" for k, v in env.items()) or f"secondary := {a.secondary_override}"
    out = build(a.name, env, a.secondary_override, note, Path(a.out_root))
    print("built", out)
    print("push:  python -m kaggle kernels push -p", out)


if __name__ == "__main__":
    main()
