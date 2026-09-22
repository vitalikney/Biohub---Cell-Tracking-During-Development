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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="folder/kernel name, e.g. exp40_relink_off (lowercase, digits, _ or -)")
    ap.add_argument("--set", action="append", default=[], help="KNOB=value (without BIOHUB_), repeatable")
    ap.add_argument("--divnet", choices=["0", "1"], default="1", help="DivNet veto on (1, exp39) or off (0, exp29)")
    ap.add_argument("--note", default="", help="one line for probe.json")
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
