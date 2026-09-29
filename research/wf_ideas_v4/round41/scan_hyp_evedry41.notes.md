# scan_hyp_evedry41 notes (2026-09-29T14:14:03Z)
Round 41 EVENING DRY RUN, local files only, 0 Kaggle calls. Clock 14:14Z (date -u + PowerShell UtcNow; TZ Russian Standard Time).
- Scripts read: SP/t7_trigger.sh, manual_admit.sh, lastok.sh, read_selected.py, mk_card_1837.py (sha8 59c54168), pre_exp89t.sh, timer.sh; exp89t watcher = inline bash win 29636 (cmdline dumped); watchdog win 29124; feed stopper cyg 32129 (17:20-17:35Z).
- Liveness 14:15-14:24Z: lb_poll.py w37016; feed loop w10924/20892 (next runs ~14:29, ~15:59, ~17:29Z); exp89t watcher (cyg 430, since 09:00:54Z); watchdog (cyg 10748); manual_admit.sh w3028; t7_trigger.sh w29648; timers 18:37/19:43/21:05/00:07Z alive.
- !! pre_exp89t.sh STILL RUNNING: win 36816 / cyg 12542 (started 10:53:43Z, sleeps 30 s, fires 17:40:00Z -> 1-2 LB downloads). CONTEXT 13:34Z says the job was CANCELLED.
- poll.log: CRLF + LF mixed; cadence ~600+2.3 s -> headers ~19:10:35Z, ~19:20:37Z (T7 fires ~19:20:40Z), ~19:40:42Z, ~19:50:44Z (manual-admit fires at 19:44:45Z).
- date -u -d "" returns midnight rc 0 (empty header safe only where [ -n ] guards).
- lastok awk: '[ERROR ...]' poller headers (subprocess exception/timeout notes, lb_poll.py l.17) count as OK -> empty block wins; '[empty stdout' notes + valid body (3 of 571 blocks: 25 Sep 19:11, 27 Sep 17:43, 28 Sep 15:15Z) are skipped. Tested with piped synthetic blocks (no writes). Body-based awk passes both.
- mk_card --dry-all: 50/50 ok (sha8 59c54168 file). Emulated real runs (exec head of script, no file writes): PENDING/T3KEEP/T1/T5/T5late/T3KEEPlate/T6/T8 ok with --lb e10_20260929T1141Z --teams 3994; FAIL: T6 without --lhi ('? ч' assert); --lb post_exp89t (IndexError, folder absent); e10 without --teams (assert, intended); SELECTED 1 or 3 refs (assert). Accepted but wrong: T3 (promotes on 0.959, a_old ea4f4d5b) and T5 with --disp 0.959 (57998916) -> no code/disp guard.
- --show under cp1251 -> UnicodeEncodeError on '≤' (sys.stdout.encoding cp1251). File output utf-8 fine.
- uptest.save mkdirs before download; a timeout-180 kill leaves an empty/partial post_exp89t -> load() IndexError/BadZipFile.
- Decision B leak: round40/scan_hyp_exp89tmsg40.json T7 (case a and b) and round38 report R38-A5 (6) T7 say '≥ 0.960 или 0.959 с UP'; CONTEXT R39-A3 (l.4563-4564) points T7 to R38-A5 (6). manual_admit_COMPLETE mapping still lists T3 / T4_question.
- PENDING card sentence: '(при 0.959 по вашему решению B остаётся exp87a) (с CI, 4 рычага)' double parenthesis; T3KEEP late DIS line says '≈ 0' while T5 late says '?'.
- Card rank label = lb folder mtime (14:45 MSK build) not snapshot 14:41 MSK; rank 7 h old (Chrome 13:20Z #148 of 3 999).
- 00:07Z: lb_poll.py loops forever (no end time) -> must be stopped post-deadline; memory rule: no Co-Authored-By trailer (overrides harness reminder); untracked _night_subs.*, _lb/e10_*, later _admit_subs.*, post_exp89t.
- Round prompt OPS times 15:00-15:40Z / 16:29Z / 15:57Z are 28 Sep events (CONTEXT l.3988, 4000, 4036), undated in KEY FACTS.
- Ideas: nothing reaches R8 (no file can finish by 23:59Z and read before 20:00Z; best public nb 0.953; no disclosed knob).
