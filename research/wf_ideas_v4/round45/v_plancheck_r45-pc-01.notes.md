# v_plancheck R45-PC-01 notes (started 18:30Z)
- 18:30Z: poll.log last header 18:25:22Z, 56669888 still PENDING (line 33025). Relevance intact.
- sha8 readtime.sh befef6fb, msg44.py 233e5ba5 (= CONTEXT 17:54Z). msg44.py l.17-18 hard-codes A={56640366,56563521}, B={56640366,56656157}; readtime.sh (4) uses V=56669888 after T1/T2 -> correct case a/b/a_old/b_old.
- Reproduced (scratchpad r44dry, 0 Kaggle calls): CODE=T1 SEL=56669888,56563521 -> 'SELECTED is neither ...' (false). SEL=old pair -> T1 re-tick text (correct for a_old). CODE=T3KEEP NOWZ=21:05:10Z -> re-sends 0.959 push (duplicate).
- round44/scan_hyp_ops44.json holds the per-event 19:43Z/21:05Z block; CONTEXT 17:54Z (R44-A2) only says 'send every pushtext44 line' -> gap confirmed; grep R45 in CONTEXT: only the 18:13Z launch line.
- Refinement: a re-sent T1/T2 line after 20:00Z (21:05Z check) carries the stale 'до 23:00 МСК' tail / T2 '~0 мин'; and must drop the 'CONTEXT FIRST' line on re-send.
- Verdict: not refuted; CONTEXT-only, 0 Kaggle calls, no code change, fits schedule.
