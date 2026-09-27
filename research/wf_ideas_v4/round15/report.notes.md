# Round 15 report notes
- 2026-09-27T05:52Z start; report.json absent -> composing. Inputs: scan_*.json, v_*.json in round15/.
- 05:55Z read CONTEXT l.2560-2834 (R12-A9 v2, RESUME 22:46Z, R13-A1 L5v2 (1)-(6), R13-A3, R14-A2, READ SHEET v1, D1 04:58Z, post-D1 04:59Z, submits 05:28Z); round14 REPORT.md/report.json shape (R14-A0 save-report pattern: harness blocks subagent .md reports -> report_md_ru field + A0).
- poll.log header 05:50:18Z: 42 exp70b 56592350, 43 56598763, 44 56598765 all PENDING; 39/40/41 = 0.949/0.954/0.949. calls.jsonl 05:41:30/05:46:31/05:51:33Z rc 0 (300 s cadence).
- ladder_watch.stdout.log: 0 'pause' lines -> PC15-06 (c) confirmed; the 05:28 'watcher paused' wording is wrong.
- E10 P3 (CONTEXT l.2141): port needs own displayed score >= 0.956 AND diff vs x138 = 1-2 explainable mechanisms, no knob sweep. amanatar V6 = ~9 knob changes + 2 new code blocks -> P3 would FAIL even at >= 0.956; E10 path is not bound by R8 (round-13 record (6)), so the browser's 'post-deadline because of R8' reason is wrong but the verdict (watch only) stands.
- Push lengths checked (python len): P-A 177 chars with 'ждём ~08:30Z', P-B 178 with a 5-char score.
- R15FP-1 skeptic sensitivity (finals_arith_eps0.py): p0=P(eps==0) 0 -> (a) lowest cliff 11/12; 0.5 -> a 8/12, b 4/12; 1 -> b lowest cliff and highest E[max] 12/12. => no world counts in CONTEXT/brief; qualitative reason only.
- Reconciliation: one merged pre-score entry (PC15-01 deviation+freeze, class-C table = R15FP-1 mechanics + PC15-02 plateau/ERROR + R15FP-2 pair shapes + PC15-05 re-tick order, priors PC15-04/RC-B/R15DS-4 spread, R15DS-3 NARROW/BROAD, L6/L7). exp70m (R15DS-5) dropped.
- 06:00Z report.json written (9 actions R15-A0..A8; 18 skeptic verdicts: 10 upheld, 8 refuted with fixes; REPORT.md delegated to main session via report_md_ru + R15-A0 per harness no-.md-report rule, same as R14-A0). Generator: session scratchpad r15_report.py.
