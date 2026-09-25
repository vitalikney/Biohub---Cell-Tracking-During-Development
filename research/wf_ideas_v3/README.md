# Ideas workflow v3 (started 2026-09-25 ~11:00 UTC) — target 0.99 by 29 Sep

Context for every agent: `BRIEF.md`. Script: `experiments/workflows/biohub-hunt-v3.js` (run 6 times in parallel,
one per lens group; the workflow runner allows only 2 concurrent agents per run in this 4-CPU container).

Lens groups: [metric-math, redteam-past], [detector-retrain, external-data-training],
[localisation-training-free, linking-on-x138], [divisions, ensembles-and-private], [github-intel, kaggle-intel],
[literature].

Files (each agent writes only its own pair; `*.notes.md` = running log, `*.json` = final structured answer):
- `h_<lens>.json` — hunter output: lens summary, challenged assumptions, browser_todo, 4 researched ideas with
  resources and wall-clock to a scored LB probe.
- `v_<lens>_<idea>_<value|schedule>.json` — two independent skeptics per idea (value/transfer; schedule/feasibility).
- Synthesis (second workflow, after all hunts): `s_*.json`, `FINAL_REPORT.md`, task cards for friend A / friend C / Colab,
  `BROWSER_TODO.md`.
