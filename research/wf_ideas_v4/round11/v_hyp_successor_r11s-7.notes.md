# v_hyp_successor R11S-7 skeptic notes (2026-09-26 ~17:50 UTC)
- No prior answer file; created notes.
- tools/e10_snapshot.py l.458-475 diff_kernels already prints `NEW <ref> pos j` and `LASTRUN ... pos i -> j` for the comp_scoreDescending list, so position changes already reach the human.
- experiments/e10_watch/20260926T1701Z-2.txt l.42-62: scoreDescending top 4 = HF v3, amanatar/optimized-biohub-max-score, kunaldesale2408, x138 (all 0.953 per browser, research/wf_ideas_v4/intel_browser.notes.md l.15), then amanatar geometric fusion 0.948.
- KEY: sort key = kernel BEST score, not latest. round10/scan_browser.notes.md l.14 (https://www.kaggle.com/code/amanatar/optimized-biohub-max-score): 'Public Score 0.910', 'Best Score 0.953 V4', yet #2 in scoreDescending. P4b(c) (CONTEXT l.2217) needs the LATEST version's score -> flag semantics mismatch.
- #1 (HF v3) is itself 0.953 -> 'new ref at #1' or 'above x138' only means best >= 0.953 (ties uninformative), cannot separate 0.953 copy from the 0.954-0.955 hole or the >= 0.956 port bar.
- A re-run keeps its old position while RUNNING/unscored (~7 h) -> flag lags; the dateRun P2 clause (CONTEXT l.2140) already fires earlier on any new/re-run kernel.
- Only sound use: negative triage (scored kernel strictly below x138 => best <= 0.953 => latest <= 0.953 => no port, not in the hole). Agents already did this by hand in round 10 (scan_plancheck.json l.8-9).
- KaggleApi kernels_list has no score field (round10/scan_plancheck.notes.md l.10) -> page read (P4c(7)) stays mandatory.
- Verdict: refuted on value (redundant, ~0 LB gain); feasibility fine (read-only, R8 n/a).
