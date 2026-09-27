# R17P-F6 skeptic notes (2026-09-27T11:12:29Z)
- 27 Sep ~11:3xZ: CONTEXT l.2917-2926 (USER INSTRUCTION = E10 v3, 11:08Z, commit 61e0737) supersedes E10 v1/v2 thresholds: trigger = public notebook score >= 0.955 (not 0.956); actions A verbatim / B +SI / C port into K2; autonomous w/ push notif; lifts P6 'no successor + insertion' ban and R8 for this item; runtime evidence <= 12 h (not L_hi <= 7.5 h). Finding says 'v1 in force, no new OK, no-insertion only; otherwise ask' -> stale.
- research/wf_ideas_v4/e10v3/build_watch.notes.md: hourly E10 v3 watch loop being built 11:12Z -> 3 h / 13-check cadence stale.
- experiments/e10_watch/20260927T1101Z.txt: scoreDescending unchanged, top HF v3 0.953; amanatar v6 unscored (experiments/ext_optimized-biohub-max-score/v6_2026-09-27/NOTES.md). LB: 74 teams at 0.955, 254 >= 0.955 -> 0.955 band is the likeliest successor score, exactly the band v1 (>=0.956) would miss.
- tools/e10_port_gate.py l.28/78/594 hardcodes REPAIR_DEADLINE_S 27000 (x138 7.5 h) -> gate FAILS a successor that changed its deadline; v3 action C/runtime <= 12 h not covered by the static gate.
- Time arithmetic itself OK: 00:04Z check -> ~01:05Z submit -> +7.5 h ~08:35Z (+12 h worst ~13:05Z) < 20:00Z tick.
- VERDICT: refuted (stale rule; 'keep as is' would write a superseded runbook into RESUME POINT).
