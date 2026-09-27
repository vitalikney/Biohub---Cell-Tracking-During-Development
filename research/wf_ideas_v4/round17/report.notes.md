# round17 report notes

- 2026-09-27T11:18:29Z: started report synthesis; report.json absent. Inputs: round17 scan_*.json + v_*.json skeptic files.
- 2026-09-27T11:22:05Z: CONTEXT tail read to l.2952 (E10 v3 11:08Z, class-C (b) 11:09:39Z, Q1/Q2 yes 11:11:40Z, exp71 pushed 11:11:50Z, FREEZE lifted 11:14Z, aggressive mode 11:16Z: probe 45 exp70g submitted ~11:15Z; combos exp70q/exp70r built; exp70n dummy running). Commit 9cdc047. Scans were built on pre-11:08Z state.
- poll.log headers 11:11:11Z and 11:21:13Z: 43/44 PENDING. Watch loop experiments/lb_poll/e10_watch_loop.py (457 lines, hourly, ends 29 Sep 12:00Z, no watch_loop.log yet = not started). fb_ins35.py + out.json exist only in scratchpad r16rcb/.
- cap 6 lab (CONTEXT 26 Sep 21:56Z): pooled -0.00057, boot 90% -0.00125..-0.00011, 85 extra insertions 0 TP/4 FP/81 unannotated. DIVINS_THRESH 0.3: no lab support (I-310). amanatar V6 (div/det gates loosened bundle) public 0.901.
- 2026-09-27T11:23:51Z: probe 45 = 56606948 exp70g submitted 11:15:12Z (poll header 11:21:13Z, PENDING); 27 Sep slots used 4 (42, 43, 44, 45), 1 left. Expected 45 score ~18:07-18:50Z (L 6.87-7.58 h); 9.0 h clock 20:15:12Z. Skeptic tally: 25 verdicts, 5 upheld (PC17-04, F9, F11, RC-A, RC-B), 20 refuted (all with fixes; mostly stale vs 11:08-11:16Z). Writing report.json + REPORT.md now.
- 2026-09-27T11:28:16Z: REPORT.md write blocked for the subagent (tool refusal); Russian report stored in report.json field report_md_ru; R17-A0 asks the main session to save it as REPORT.md. report.json final.
