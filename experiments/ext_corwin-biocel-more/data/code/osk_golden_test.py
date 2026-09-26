#!/usr/bin/env python3
"""Golden test for the ten bag checkpoints: prove they LOADED, in the kernel, before use.

A checkpoint is a pickled dict. It travels between torch versions, and a load that silently
produces the wrong tensors -- or a `MitosisHead` built with the wrong width -- would change
every logit without raising. D-353's answer is a golden test: a FROZEN input, the expected
per-model outputs computed once where the weights are known good, and a re-check wherever
they are used.

The input is generated from a fixed integer seed with numpy's default_rng, so it needs no
file of its own and cannot drift. The check runs on CPU in fp32, which is the most portable
arithmetic available on both sides.

  generate:  python osk_golden_test.py generate --bag-dir B --mitose-impl D --out GOLDEN.json
  check:     python osk_golden_test.py check    --bag-dir B --mitose-impl D --golden GOLDEN.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SEEDS = (1, 2, 3, 4, 5)
EMBRYOS = ("44b6", "6bba")
GOLDEN_SEED = 20260908
N_SAMPLES = 4
FED_SHAPE = (4, 11, 40, 40)
# fp32 on CPU is reproducible to about this across machines and torch builds; a real
# load failure moves logits by whole units, not by 1e-5.
TOLERANCE = 1e-4


def read_utc() -> str:
    try:
        return subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "UNREAD"


def frozen_input() -> np.ndarray:
    rng = np.random.default_rng(GOLDEN_SEED)
    return rng.standard_normal((N_SAMPLES,) + FED_SHAPE, dtype=np.float32)


def run_bag(bag_dir: Path, mitose_impl: Path) -> dict:
    sys.path.insert(0, str(mitose_impl.resolve()))
    import torch
    import mh_data as D
    import mh_net as NET

    torch.backends.cudnn.benchmark = False
    x = torch.from_numpy(frozen_input())
    out = {}
    meta = {}
    for e in EMBRYOS:
        for s in SEEDS:
            name = f"h{e}_s{s}"
            path = bag_dir / f"{name}__best_held_{e}.pt"
            st = torch.load(str(path), map_location="cpu", weights_only=False)
            m = NET.MitosisHead(in_channels=st.get("in_channels", D.N_CHANNELS),
                                width=st.get("width", 32))
            m.load_state_dict(st["model"])
            m.eval()
            with torch.no_grad():
                y = m(x).float().numpy()
            out[name] = [float(v) for v in y]
            meta[name] = {
                "held_embryo": st.get("held_embryo"),
                "width": st.get("width"),
                "in_channels": st.get("in_channels"),
                "epoch": st.get("epoch"),
                "is_ema": st.get("is_ema"),
                "n_state_tensors": len(st["model"]),
                "n_parameters": int(sum(p.numel() for p in m.parameters())),
            }
    return {"logits": out, "meta": meta, "torch": torch.__version__}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("generate", "check"))
    ap.add_argument("--bag-dir", required=True, type=Path)
    ap.add_argument("--mitose-impl", required=True, type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--golden", type=Path)
    args = ap.parse_args()

    got = run_bag(args.bag_dir, args.mitose_impl)

    if args.mode == "generate":
        doc = {
            "schema": "BIOCEL_GOLDEN_HEAD_V1",
            "date_u": read_utc(),
            "generated_by": "osk_golden_test.py generate",
            "input": {"rng": "numpy.random.default_rng", "seed": GOLDEN_SEED,
                      "call": "standard_normal", "shape": [N_SAMPLES] + list(FED_SHAPE),
                      "dtype": "float32"},
            "device": "cpu", "precision": "fp32", "tolerance": TOLERANCE,
            "torch_at_generation": got["torch"],
            "meta": got["meta"],
            "logits": got["logits"],
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        print(f"golden written: {len(got['logits'])} models, torch {got['torch']} -> {args.out}")
        return 0

    ref = json.loads(args.golden.read_text(encoding="utf-8"))
    worst = 0.0
    worst_name = None
    failures = []
    if sorted(ref["logits"]) != sorted(got["logits"]):
        print(f"GOLDEN FAILED: model set differs. expected {sorted(ref['logits'])}, "
              f"got {sorted(got['logits'])}", file=sys.stderr)
        return 6
    for name, exp in ref["logits"].items():
        gotv = got["logits"][name]
        d = float(np.max(np.abs(np.asarray(exp) - np.asarray(gotv))))
        if d > worst:
            worst, worst_name = d, name
        if d > ref.get("tolerance", TOLERANCE):
            failures.append({"model": name, "max_abs_delta": d,
                             "expected": exp, "got": gotv})
    verdict = {
        "date_u": read_utc(), "n_models": len(got["logits"]),
        "worst_max_abs_delta": worst, "worst_model": worst_name,
        "tolerance": ref.get("tolerance", TOLERANCE),
        "torch_at_generation": ref.get("torch_at_generation"),
        "torch_here": got["torch"],
        "verdict": "GOLDEN PASSED" if not failures else "GOLDEN FAILED",
        "failures": failures[:5],
    }
    print(json.dumps(verdict, indent=1))
    if failures:
        print("GOLDEN FAILED: the checkpoints did not load to the same network here as "
              "where they were sealed. REFUSE to score.", file=sys.stderr)
        return 6
    return 0


if __name__ == "__main__":
    sys.exit(main())
