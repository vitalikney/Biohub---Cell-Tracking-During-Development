"""Tables for the tight-5.5 lab: replay reports (5.5 cache) next to the 6.0 lab, per split / embryo, share of gains.

    python experiments/l2_daughternet/relink55/summarise_t55.py
Writes experiments/l2_daughternet/relink55/t55_report.{md,json}.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT55 = ROOT / ".public_local_cache" / "l2_replay_t55"
OUT60 = ROOT / ".public_local_cache" / "l2_replay" / "friend_a_b20_exp29"
CONFIGS = ("exp39", "ef_a3_rl_pr", "ef_a0")


def load(out: Path, split: str):
    path = out / f"report_{split}.json"
    if not path.is_file():
        return None, None
    rep = json.loads(path.read_text(encoding="utf-8"))
    pv = pd.read_csv(out / f"per_video_{split}.csv")
    return rep, pv


def rows_for(rep, pv, split: str, lab: str) -> list[dict]:
    out = []
    for name in CONFIGS:
        if rep is None or name not in rep["configs"]:
            continue
        entry = rep["configs"][name]
        row = {"lab": lab, "split": split, "config": name, "videos": rep["videos"], "score": entry["all"]["score"],
               "adj_edge": entry["all"]["adj_edge_jaccard"],
               "div": f"{int(entry['all']['division_tp'])}/{int(entry['all']['division_fp'])}/"
                      f"{int(entry['all']['division_fn'])}",
               "node_ratio": entry["all"]["node_ratio_vs_control"]}
        for sub in ("all", "44b6", "6bba"):
            s = entry.get(sub) or {}
            b = s.get("bootstrap_vs_control") or {}
            row[f"score_{sub}"] = s.get("score")
            row[f"d_{sub}"] = b.get("delta")
            row[f"lo_{sub}"] = b.get("ci90_lo")
            row[f"hi_{sub}"] = b.get("ci90_hi")
        g = pv[pv["config"] == name]
        for sub in ("all", "44b6", "6bba"):
            gg = g if sub == "all" else g[g["embryo"] == sub]
            if len(gg):
                row[f"gain_{sub}"] = float((gg["video_score"] > gg["ctrl_video_score"] + 1e-12).mean())
                row[f"loss_{sub}"] = float((gg["video_score"] < gg["ctrl_video_score"] - 1e-12).mean())
                row[f"n_{sub}"] = int(len(gg))
        if name != "exp39":
            row["edge_fp"] = int(g["edge_fp"].sum())
            row["edge_fp_ctrl"] = int(pv[pv["config"] == "exp39"]["edge_fp"].sum())
            for k in ("edgefilter_candidates", "edgefilter_dropped", "edgefilter_relinked_fwd", "edgefilter_relinked_bwd",
                      "edgefilter_pruned_nodes"):
                if k in g.columns:
                    row[k] = int(g[k].fillna(0).sum())
        out.append(row)
    return out


def main() -> None:
    table = []
    for split in ("all", "selection", "confirmation"):
        for lab, out in (("t55", OUT55), ("t60", OUT60)):
            rep, pv = load(out, split)
            if rep is not None:
                table += rows_for(rep, pv, split, lab)
    df = pd.DataFrame(table)

    def f(x, spec="+.4f"):
        return "-" if x is None or x != x else format(x, spec)

    lines = ["# Tight-5.5 lab (cache friend_a_b20_exp29_t55) vs the 6.0 lab", "",
             "| split | lab | config | videos | score | delta | 90% CI | d44b6 [CI] | d6bba [CI] | gain / loss videos "
             "(all; 44b6; 6bba) | div TP/FP/FN | node ratio |",
             "|---|---|---|---:|---:|---:|---|---|---|---|---:|---:|"]
    for r in table:
        ci = "-" if r.get("lo_all") is None else f"[{f(r['lo_all'])}, {f(r['hi_all'])}]"
        e44 = "-" if r.get("d_44b6") is None else f"{f(r['d_44b6'])} [{f(r['lo_44b6'])}, {f(r['hi_44b6'])}]"
        e6b = "-" if r.get("d_6bba") is None else f"{f(r['d_6bba'])} [{f(r['lo_6bba'])}, {f(r['hi_6bba'])}]"
        gains = "; ".join(f"{r.get(f'gain_{s}', float('nan')):.0%}/{r.get(f'loss_{s}', float('nan')):.0%}"
                          for s in ("all", "44b6", "6bba") if f"gain_{s}" in r)
        lines.append(f"| {r['split']} | {r['lab']} | {r['config']} | {r['videos']} | {r['score']:.6f} | "
                     f"{f(r.get('d_all'))} | {ci} | {e44} | {e6b} | {gains if r['config'] != 'exp39' else '-'} | "
                     f"{r['div']} | {r['node_ratio']:.5f} |")
    (HERE / "t55_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (HERE / "t55_report.json").write_text(json.dumps(table, indent=1, default=float), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
