# notes x138-budget-aware-deadline SCHEDULE skeptic — Fri Sep 25 11:10:16 UTC 2026
- start: read BRIEF.md; no prior JSON; read value-skeptic notes (v_ensembles-and-private_..._value.notes.md): key point latency(#34)<7.5h proves guard never fired.
- Verified x138 code cell 0 l.70-74 (REPAIR_DEADLINE_S=27000 env, ILP 1200, VALIDATOR off) and cell 5 l.19-45 (_deadline_degrade), l.2072 sorted geffs, l.2115-2117 check at each dataset start; sticky flag. write_test_submission called once (cell 5 l.2219; cell 10 re-write only if validator sweep selects, validator OFF). Repair loop runs AFTER all prediction (cell 4 'Prediction completed').
- No exp56/exp57b logs in repo (notebooks without outputs); runtime split GPU vs repair unknown here.
- Dummy runtimes (RESULTS.md l.60-68): exp51 ~29 min, exp52 ~43 min (same compute! => Kaggle run-to-run variance ~1.5x), exp56/57b ~40 min T4 on 4 clips.
- Latencies: #29/#30 09:41 -> ~16:40-16:55 (7.0-7.2 h, no DaughterNet); #28 7.5 h; #31 7.5 h; #32/#33 ~7.8 h.
- build tool: x138 base allows only divinsert/leafprune patches, BUT --set KEY=V appends os.environ lines at END of cell 0 -> '--base x138 --set REPAIR_DEADLINE_S=36000' works with ZERO new code (cell 5 reads env at import).
- FLAW in the idea's rule: 'degrade if elapsed + remaining x est_full > 11 h' is ALL-OR-NOTHING: when the full tail cannot fit, it degrades the whole remainder after a few datasets, i.e. repairs FEWER datasets than the author's fixed 7.5 h guard. Simulating.
