# notes x138-budget-aware-deadline SCHEDULE skeptic — Fri Sep 25 11:10:16 UTC 2026
- start: read BRIEF.md; no prior JSON; read value-skeptic notes (v_ensembles-and-private_..._value.notes.md): key point latency(#34)<7.5h proves guard never fired.
- Verified x138 code cell 0 l.70-74 (REPAIR_DEADLINE_S=27000 env, ILP 1200, VALIDATOR off) and cell 5 l.19-45 (_deadline_degrade), l.2072 sorted geffs, l.2115-2117 check at each dataset start; sticky flag. write_test_submission called once (cell 5 l.2219; cell 10 re-write only if validator sweep selects, validator OFF). Repair loop runs AFTER all prediction (cell 4 'Prediction completed').
- No exp56/exp57b logs in repo (notebooks without outputs); runtime split GPU vs repair unknown here.
- Dummy runtimes (RESULTS.md l.60-68): exp51 ~29 min, exp52 ~43 min (same compute! => Kaggle run-to-run variance ~1.5x), exp56/57b ~40 min T4 on 4 clips.
- Latencies: #29/#30 09:41 -> ~16:40-16:55 (7.0-7.2 h, no DaughterNet); #28 7.5 h; #31 7.5 h; #32/#33 ~7.8 h.
- build tool: x138 base allows only divinsert/leafprune patches, BUT --set KEY=V appends os.environ lines at END of cell 0 -> '--base x138 --set REPAIR_DEADLINE_S=36000' works with ZERO new code (cell 5 reads env at import).
- FLAW in the idea's rule: 'degrade if elapsed + remaining x est_full > 11 h' is ALL-OR-NOTHING: when the full tail cannot fit, it degrades the whole remainder after a few datasets, i.e. repairs FEWER datasets than the author's fixed 7.5 h guard. Simulating.
- SIM (scratchpad sim.py; 110 datasets, lognormal sigma 0.5 repair times, degraded = 0.1 x full): fraction fully repaired orig(7.5h) / idea rule / fixed 10h / greedy:
  G=6.5h R=2.5h: 0.43 / 0.07 / 1.00 / 1.00; G=6h R=4h: 0.40 / 0.03 / 1.00 / 1.00; G=7h R=2.5h: 0.23 / 0.06 / 1.00 / 1.00; G=5h R=4h: 0.62 / 0.06 / 1.00 / 1.00.
  Idea rule degrades almost all when G + ~2.2 R > 11 h (1.3 x p90 applied to ALL remaining) -> worse than the author's guard; inside the idea's own T=8-8.5h, R=1.5-2.5h scenario range (G=6-6.5, R=2-2.5).
  fixed 10h finishes <= 10.3 h at dfrac 0.1; worst finish grows with degraded cost d x remaining (exp57b: divinsert UNGATED -> d larger; bound d by full-repair seconds from the exp56 dummy log).
- Confirmed DIVINS_CALL ungated (build_probe_kernel.py l.302): frame reads + DaughterNet GPU per dataset inside the loop -> exp57b pushes later datasets past 27000 s; #35 vs #34 comparison may be confounded by the guard -> compare their latencies.
- --set on --base x138 accepted (no knob whitelist, l.1395-1400; block appended at end of cell 0 after l.74) -> REPAIR_DEADLINE_S=34200 needs zero new code.
- Critical path: 25 Sep 17-20 UTC #34/#35 latencies -> build (15 min) -> 26 Sep 00:00 reset: 1 dummy (~40 min T4, queue behind other ideas, 2 concurrent) -> sha check vs exp56/57b dummy CSV -> submit ~01:00-03:00 with pre-given OK -> scored 26 Sep ~09:00-14:00 UTC. ~70 h buffer. P(scored by 29 Sep 10:00) ~0.9 conditional on user OK and x138 base.
- VERDICT: schedule OK, but the rule AS DESCRIBED is defective -> refuted=true with fix (fixed 9.5-10 h via --set, or greedy rule), carried as rider on the x138-based F1 build.
