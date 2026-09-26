# v_hypotheses_r6h-2 notes (2026-09-26T06:03:22Z)
- 06:03Z: no prior v_hypotheses_r6h-2.json; started fresh.
- 06:05Z poll.log header 06:03:58Z: #37 56563521 and #38 56563534 both PENDING -> v4 can still be pre-score. HEAD 2f6ec9d.
- Sources read: CONTEXT.md l.1640-1730 (R1-R10, §f), l.1880-1900 (f2), l.1955-2074 (READ TABLE, v2 C1-C6, v3 V1-V7, OK request 04:04Z, K2'' builder);
  round6/scan_hypotheses.json (R6H-1..8), round6/scan_plancheck.json (PC6-01..06), round5/report.json l.15/19 (late-OK text).
- W1 DEFECT: 'floor, row 2 and C4 read the LATER of the two' is anti-conservative. Twin expected first (~06:15-07:40Z), K2 later
  (~07:00-09:30Z). An OK sent after poll.log shows twin = 0.952 but before K2's result would COUNT for the floor = exactly the
  post-hoc case PC6-01 names ('twin = 0.952 followed by yes to the floor'). Also contradicts W1's own 'first result it reads'
  and round5 report.json l.19 ('floor ... post-hoc if the twin's score was visible'). Fix: EARLIER of the two (floor: twin's result).
- W1 over-strict on event items: C2(a) K2 resubmit, row-1/C2(c) K1 and W7 twin resubmit respond to an ERROR class (no score);
  PC6-01 says they may be OK'd after the event. W1 as drafted labels them 'late'.
- W6 DEFECT: K2 resubmit to +8.0 h only; its R5(a) mark is 9.5 h (same file as K2; V7 keeps K2 to +9.5 h). Use +9.5 h.
- W7: EV ~5e-6; adding item 8 to an already 7-item OK message dilutes attention; with corrected W1 it is an event item that can be
  asked when (if) the twin gets 'Kaggle Error' (P~0.01). Slot cost ~0 (5/day on 27-28 Sep too). Recommend: no pre-OK item; ask on event.
- W2/W5/W8: correct but mostly restate table + C3 + V1 (row 4 'No K1' + V1 already gives {twin, exp52} / {#34, exp52}).
- W3: consistent with §f +0.002 simpler-file rule and R7; fine.
- W4: fine for K2''; note row 5->4 moves the runtime risk to K1 (same 8.0 h gate, 9.5 h repair), but K1 must be R5-admissible, so
  the 9.5 h degrade is rule-guarded; mention only.
- Value: procedural (no mis-tick, no unlogged post-hoc choice); score EV ~1e-5. Feasibility: text only, ~10 min, must be committed
  before the first #37/#38 COMPLETE/ERROR line; fallback 'post-hoc NOTES' already stated.
