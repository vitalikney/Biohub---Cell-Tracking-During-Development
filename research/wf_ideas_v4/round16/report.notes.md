# Round 16 report notes

- 2026-09-27T08:51:00Z start; report.json absent; round16 has scan_* (browser, plancheck, hyp_forecast_update, hyp_answers_prep, recheck) + 17 v_* skeptic files.
- 08:51Z poll.log last header 08:50:47Z: 56598763/56598765 PENDING (ledger L > 3.37 h). exp70b ledger (7.41, 7.58] h, 'did NOT fire'. git HEAD 0bd1408; untracked e10_watch/20260927T0831Z.txt, ext_optimized-biohub-max-score/v6_2026-09-27/, round16/; ledger.md + poll.log modified.
- CONTEXT has no entry after 07:41Z D2 (no user letter logged). 'ROUND 15 RECORD' grep = 0 hits (R15-A6 text sits in round15/report.json). Last RESUME POINT = l.2599 (26 Sep 22:46Z) -> stale (PC16-06 confirmed).
- v6 NOTES.md item 4 still says 'past the R8 line in practice' (PC16-07 confirmed; R15-A7 says E10 not bound by R8, P3 blocks).
- R15-A1 (4)(b) literal: '{V*_C, the L9 insertion final (#37 or exp70b)}' with exp70b only if 42 is L9 V* (it is not: 0.954) -> pre-registered (b) partner = #37.
- Skeptic conflicts resolved: PC16-02 fix (INS in (b)) vs R16AP-1 fix (no exp70b substitution) vs RC-A fix (class-C (b) uses exp70b on yes) vs r16fc-3 fix (prefer #37): chosen rule = (b) partner #37 unless the user's letter explicitly names exp70b as the (b) partner; (a)+exp70b yes -> {exp70b, #38}; E10 '#37' = INS only for a no-insertion port (R16AP-6 clause A).
- Refuted (with fixes folded): r16fc-3 (MC table), r16fc-4 (numeric hedge bound), r16fc-5 (thresholds/MC at tick check), R16AP-6 (unified table; 78/144 literal defects), R16AP-10 (dup of R16AP-4), RC-A ('weakly dominates'/recommend yes).
- Unverified scan items judged here: PC16-03 -> folded into neutral exp70b facts (RC-A fix); PC16-05/06/07/08, r16fc-1/7, R16AP-0/2/5/9 -> kept (hygiene/info); r16fc-6 -> keep 'only the better final counts', drop '#38 weakest second file' (contradicted by r16fc-4 skeptic beta<0 world).
- REPORT.md: harness note forbids subagent .md reports (same as R14/R15) -> Russian text in report.json 'report_md_ru', action R16-A0 saves it.
- 2026-09-27T08:57:32Z report.json written (complete=true, 10 actions R16-A0..A9; report_md_ru embedded because the harness blocked writing REPORT.md from this subagent -> R16-A0). Builder: scratchpad r16judge/build_report.py.
