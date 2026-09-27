# v_hyp_reads_table_r19rt-1 notes (2026-09-27T18:12:56Z)
- 18:13Z read scan_hyp_reads_table.json R19RT-1..8, scan_plancheck.json PC19-01..09, scan_recheck.json; CONTEXT l.2940-3071 (16:08Z card, 17:21Z exp75).
- poll.log last header 2026-09-27T18:04:40Z: 45 (56606948, L>6.82h) and 46 (56611472, L>3.46h) PENDING. Table not yet pasted in CONTEXT (last entry 17:21Z).
- LastSubmissionDate semantics = MAX submit time over SCORED submissions, not the most recently completed one:
  e10_watch/20260926T1620Z.txt, 1701Z, 2001Z and 20260927T0147Z.txt show 2026-09-26 00:02:18 (#38, completed 06:54:06Z) although #37 (00:02:12) completed LATER (07:34:12Z) (ledger.md). Snapshot with 21:38:33 (exp70d) while exp70b pending also fits.
  -> Table (3) submits CI FIRST (00:05Z) but CI completes LAST (~09:40-10:45Z). After SEC(00:10)/DIV(00:45) score, our LastSubmissionDate = 00:45 and never equals 00:05 -> the (2)(a) S1 proof is unsatisfiable for the CI ref; same for W2 file 1 (CI stack, ~11:30Z) vs file 2 (no-CI, after 12:00Z, completes ~2 h earlier by design). N4/U4 for CI cannot be coded.
  SubmissionCount increments by 1 per scored file (40 @01:47Z -> 44 after 39-42 -> 46 after 43/44; 46 @17:43Z) -> usable instead (PC19-07).
- W2 file 2 'same stack without CI, if >=2 levers + incl. CI': with exactly 2 levers + it equals the other W1 single (exp76f minus CI = exp76d; exp76i minus CI = exp76e; exp76h minus CI = exp76g) -> duplicate. Only valid when all 3 are +.
- Not absorbed from plancheck: PC19-02 (row for 46 still PENDING at 23:45Z), PC19-05 (CI gate uses CI_hi -> anti-conservative; repeated in table (8)), PC19-08 (ladder_watch.py hardcodes refs; 'watcher from 06:30Z' not doable as written).
- (8) turns card (2) 'CI >= 0.955 = info only' into 'proposal {V_pub,#37}' without an AMEND mark (table claims only 2 amendments).
- Verdict: the idea (pre-registered read table, bookkeeping, 0 slots, no mechanism) is sound; the paste-ready text as written is refuted on the S1 proof + file-2 rule. Fix is small.
