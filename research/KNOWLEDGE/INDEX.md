# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 44: state as of 2026-09-29 ~17:50 UTC (20:50 MSK). Git HEAD is still 19149bf (16:43Z 'Round 43 applied ...'); no commit since curation 43 (`git log`). `CONTEXT.md` has 4,718 lines; the newest entry is l.4695-4697 (17:13Z LIVENESS, uncommitted) and `## 9. Literature` starts at l.4698. Round 44 (`research/wf_ideas_v4/round44/`, report.json 17:37:24Z, R44-A1..A5) is **PROPOSED and not yet in CONTEXT**. Untracked: `round44/`, `experiments/discussions/digest_20260929T1729Z.md`, `experiments/lb_poll/_lb/e10_20260929T1141Z/`, `_night_subs.*`, `research/KNOWLEDGE/_curation/43/*.json`, `_curation/44/` (`git status`). Times are UTC unless marked MSK (= UTC+3).
Deadline 29 Sep 23:59Z (30 Sep 02:59 MSK). The user ticks finals MANUALLY by 20:00Z (23:00 MSK); the session never ticks (`CONTEXT.md` l.3842-3855, l.4092). Rule anchors: PRE-REG v3 l.1576-1736; GAP RULE v2 l.4009-4020; R39 comparator l.4559-4574; **DECISION B l.4607-4617**; R40 APPLIED l.4618-4642; **R41 APPLIED l.4643-4667**; OPS 15:59 l.4668-4677; **R43 APPLIED l.4678-4694**; LIVENESS 17:13 l.4695-4697.

## STATE IN 10 LINES

1. **Finals TICKED 2/2 = П3 {exp87a 56640366 (0.959), #37 56563521 (0.954)}.** The last good API SELECTED read was at 12:37:31Z (`CONTEXT.md` l.4579-4581, l.4678-4694 A3; `DECISIONS.md` §2 [c44] l.1024-1026).
2. **Best = P51 exp87a = 0.959 = V_pub.** Rank **#154 of 4,005 LB rows** (Chrome 17:15Z; the Overview shows 4,003 teams). The 0.959 block is #144-#158, so we are 5th from its bottom (`FACTS.md` F-LB-43 l.281, C-355 l.907).
3. **No new LB score since curation 38.** P55 exp89t (56669888) is still PENDING at the 17:45:10Z header, L > 8.74 h (`experiments/lb_poll/poll.log` l.32778-32781; `IDEAS.md` I-486). The poller step is 10:02.3, so the read headers are projected at **18:15:17, 18:25:19 and 18:35:22Z** (21:15-21:35 MSK) (`FACTS.md` F-RUN-65 l.351).
4. **Decision B:** exp89t replaces exp87a only at a public display of >= 0.960. Mapping: >= 0.960 -> T1/T2; 0.959 -> T3KEEP (expected); <= 0.958 -> T5; first terminal header after 19:45:17Z -> T8. T7 is ~19:15:31Z; the last admissible header is ~19:35:36Z, and the 19:44:45Z manual-admit list is the only record before the edge (`CONTEXT.md` l.4607-4617, l.4643-4667; `FACTS.md` F-RUN-65).
5. **LIVENESS 17:13Z (R43-A6) is logged:** every evening-chain job is alive, pre_exp89t has 0 processes, the laptop is on AC (`CONTEXT.md` l.4695-4697). The feed ran at 17:29:24Z and stopped cleanly (0 kaggle_feed.py at 17:33:14Z). New PIDs: watchdog v2 30176/16728, awk reader 1364/19012 (`FACTS.md` F-RUN-64 l.350, F-RUN-65).
6. **Round 44 PROPOSES (none logged):** A1 round 45 at 18:13Z = NO-OP; A2 read-time block `readtime.sh` befef6fb (HOLD guard, 600 s timeout, no-pipe sourcing, all pushtext44 lines except 'CONTEXT FIRST', never `--lb post_exp89t`); A3 card rank line '#154 из 4 005 (Chrome 20:15 МСК)'; A4 OPS/KEY FACTS line; A5 00:07Z stop order with watchdog v2 first (`research/wf_ideas_v4/round44/report.json`; `FACTS.md` F-RUL-46 l.402).
7. **Slot 2 CLOSED UNUSED since ~16:50Z;** no round proposes a submit or build (`CONTEXT.md` l.4689-4690). Round 44 is the twelfth null round for levers (`FACTS.md` F-TRN-80 l.547).
8. **Round prompt still stale:** `experiments/workflows/biohub-research-round.js` l.20/l.37 say '#151 of 3 999', '5 min', 'T7 ~19:20Z', pre_exp89t. This only matters if another round runs (`WATCHLIST.md` l.61; `FACTS.md` C-345).
9. **Private-risk audit (13:21Z) stands:** keep the pair; keeping exp87a costs ~0 on average (±0.0007) (`CONTEXT.md` l.4593-4606; `FACTS.md` F-TRN-78, F-TRN-79 l.546).
10. **Next, MSK [UTC]:** now: log R44-A1/A4 before 21:13 [18:13]; 21:13 [18:13] timer 30820 = NO-OP; 21:15:17 / 21:25:19 / 21:35:22 [18:15-18:35] exp89t read; 21:37 [18:37] card + SELECTED; ~22:15:31 [~19:15:31] T7; 22:43 [19:43] SELECTED; 22:44:45 [19:44:45] manual-admit (reader to 19:47Z); **23:00 [20:00] tick**; 00:05 [21:05] SELECTED; 02:00 [23:00] hindsight commit; 02:59 [23:59] deadline; 03:07 [00:07] post-deadline step (`WATCHLIST.md` NEXT 24 H l.83). **Ideas: 626** (lb-tested 65, lab-tested 28, refuted 286, deferred 51, in-plan 194, open 2); 13 at risk; strict orphan I-233 (`IDEAS.md` l.247, ORPHANS l.1011).

## WHERE THINGS ARE

The knowledge base is `research/KNOWLEDGE/`, written only by `experiments/workflows/biohub-curator.js`:
- `INDEX.md` is this page. `CHANGES.md` holds per-curation deltas (v4, 2-41, 43, 44). Curator logs are in `research/KNOWLEDGE/_curation/{v4,2,...,41,43,44}/` (`*.json` answers, `*.notes.md` crash-safe logs).
- `IDEAS.md` + `ideas.json` (I-001..I-626): CHANGES (44) l.249, ranking l.263; FINALS l.282, LADDER l.391, BASE l.519, RUN l.563, LOC l.653, DIV l.689, MODEL l.762, NODES l.815, INFER l.854, EF l.877, LINK l.897, VALID l.935, TESTSET l.992; ORPHANS l.1011.
- `FACTS.md`: state l.3; §1 metric l.197; §2 data l.214; §3 LB l.235 (F-LB-43 l.281); §4 runtime l.283 (F-RUN-65 l.351); §5 rules l.353 (F-RUL-46 l.402); §6 models l.404; §7 lab-to-LB l.464 (F-TRN-80 l.547); CONTRADICTIONS l.549 (C-355..C-365 l.907-917).
- `DECISIONS.md`: probes §1 l.149 (P55 l.212; [c44] l.577); finals §2 l.644 ([c44] snapshot l.1024-1026); E10 rule §2f l.1392; ladder §2h l.1578; R1-R10 §3 l.1777 ([c44] rows l.1939-1942); changelog [c44] l.2162.
- `WATCHLIST.md` (~17:45Z): DUE NOW l.54 (W392, W395, W397); CONTRADICTIONS l.66 (C31-C35); NEXT 24 H l.83; LATER l.106; INSIGHTS l.131 (I474-I484).

Key sources (paths from the repo root):
- Logs and LB: `CONTEXT.md` (anchors above); `experiments/RESULTS.md` (rows only to P46); `experiments/lb_poll/poll.log`, `ledger.md`; card LB csv `experiments/lb_poll/_lb/e10_20260929T1141Z/lb.csv` (always with `--teams 3994`). Feed: `experiments/discussions/digest_20260929T1729Z.md` (last run), `744250.md` (selection-lock question).
- Kernels (each with `probe.json`): V_pub `experiments/exp87a_k2cap6_div04_ra094_ci/`; final #37 `experiments/exp58_x138_safe_lowref/`; pending `experiments/exp89t_k2cap6_k_dis225_ci/`; П2 alternative `experiments/exp75_k2_coordinject/`.
- Tools: `tools/uptest.py`, `tools/runtime_ledger.py`, `tools/build_probe_kernel.py`, `tools/kaggle_feed.py`. Round prompt: `experiments/workflows/biohub-research-round.js` (KEY FACTS l.20 and l.37, stale). Read-time scripts (`r44dry/readtime.sh`, `msg44.py`, `cardfix44.py`, `mk_card_1837.py` a19e1bd6) live in the session scratchpad (`FACTS.md` F-RUN-65).
- Rounds: `research/wf_ideas_v4/round44/` (report.json R44-A1..A5 with the Russian text in next_focus; report.notes.md; 4 scans; 12 v_*.json; no REPORT.md); `round43/` (R43-A1..A8); `round41/` (PATCHR41).
- Other: private-risk audit `research/wf_ideas_v4/risk_audit/`; background `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md` CHANGES (44) l.249 and ORPHANS l.1011)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-617 | Round 45 at 18:13Z = NO-OP; do not kill timer 30820 (I-619); keep 19:05-19:50Z free | In plan, at risk; log before 18:13Z | R44-A1; `FACTS.md` C-357 |
| I-620 (+ I-623) | Read-time block: one Bash call with timeout 600000, source without a pipe, HOLD on a scoreless COMPLETE, all push lines except 'CONTEXT FIRST'; log L_hi when F >= 1 | In plan, at risk; every event from 18:15:17Z | R44-A2; `FACTS.md` C-356, C-358..C-360 |
| I-613 / I-622 | Card rank line '#154 из 4 005 (Chrome 20:15 МСК)'; default `--lb e10_20260929T1141Z`, never `post_exp89t` | In plan; 18:37Z (21:37 MSK) | R44-A3; `FACTS.md` C-355 |
| I-614 / I-259 | R44-A4 OPS line + KEY FACTS (#154 of 4 005, ~10 min 2 s, slot 2 closed, feed stopped, round 45 NO-OP) | At risk; not logged | R44-A4; `FACTS.md` C-345 |
| I-624 / I-607 / I-600 | 00:07Z: final save; stop watchdog v2 FIRST, then 37016 and the rest; git add evidence; commit with no trailer | At risk; 30 Sep 00:07Z (03:07 MSK) | R44-A5 + R43-A8; `FACTS.md` C-361 |
| I-336 / I-407 / I-252 / I-516 | Hindsight prediction quoting the audit grid; cap-family private line; lessons; truncation line | At risk; before 23:00Z (02:00 MSK) | `IDEAS.md` ORPHANS l.1011 |
| I-625 | If CI is reused, the same-frame near-pair count (< 2 um) becomes a dummy gate | Deferred (write-up) | R44-RC-A; `FACTS.md` F-TRN-80 |
| I-233 | Poller logs error_description | Strict orphan, no owner | `IDEAS.md` ORPHANS l.1011 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/44/{ideas,facts,watch}.json`)

1. [now] **Round 44 not logged before the 18:13Z timer (R44-A1 + R44-A4 = I-617 / I-614 = W392 / W395 / W397 = C-357 / C35).** Append the round-45 NO-OP line, the OPS/KEY FACTS line and 'ROUND 44 APPLIED' before 21:13 MSK. Ignore the notification; leave 30820 alive (a -match kill could hit 29184 / 20960 / 24260 / 21232) (`research/wf_ideas_v4/round44/report.json` R44-A1, R44-A4; `v_plancheck_r44-pc-02.json`).
2. [now] **Read-time block traps (R44-A2 = I-620 / I-621 = W393 = C-359 / C-360 = I474-I478).** Use one Bash call with timeout 600000 (worst case ~250 s). Source `readtime.sh` on its own line, never under a pipe, and never define a shell 'msg' (it resolves to msg.exe). A COMPLETE with an empty score = HOLD. Send every pushtext44 line except 'CONTEXT FIRST'; on T1/T2, log RECOMMENDED PAIR in CONTEXT before the push. If r44dry fails, use the manual R43-A4 / R41-A4 path (`round44/report.json` R44-A2 (a)-(i); `round44/report.notes.md` 17:35:44Z). Curators split (ideas [now], watch [today]); settled [now] because the first header is 18:15:17Z.
3. [today] **Card inputs (C-358 = C31; C-355 = C32 = R44-A3).** Always use the default `--lb e10_20260929T1141Z --teams 3994`; `post_exp89t` does not exist and uptest.load would crash on it. The rank line is '#154 из 4 005 (Chrome 20:15 МСК)'. Never quote #151 / #148 / #141 / 3 999 / 3 994 / '17 из 22'. Log the card sha8 next to a19e1bd6, and never send an `r44dry/card_1837_*.txt` (`round44/v_hyp_ops44_r44-ops-postexp89t-lb.json`, `v_hyp_ops44_r44-ops-rankline-count.json`).
4. [today] **Edge keying (C-356 = C33 = I-623).** Follow R41-A3 (header-keyed). If the terminal header carries F >= 1 failed attempts, also log L_hi = hdr + 210 s x F - T0. The projected 19:05:29Z header lies in the F=2 window; only the UNPROVEN-ins / DIS wording can differ, never the pair (`round44/v_hyp_ops44_r44-ops-edge-keying.json`; `CONTEXT.md` l.4659-4661).
5. [before-finals] **exp89t timing (T241, F-RUN-65).** Headers 18:15:17 / 18:25:19 / 18:35:22Z; T7 ~19:15:31Z; last admissible ~19:35:36Z; the next, ~19:45:38Z, falls after 19:45:17Z. Code per decision B; a read at 18:35:22Z serves both the push and the card in one run (`FACTS.md` F-RUN-65 l.351; `DECISIONS.md` §2 [c44]).
6. [before-finals] **SELECTED checks at 18:37, 19:43 and 21:05Z (R43-A3, F-RUL-45).** No 'SELECTED at' line, or a 90 s selread timeout = FAILED read: retry once after 60 s, at most 2 calls. After two failures, push 'проверьте сами: «2 of 2 selected»'. The user ticks by 20:00Z (23:00 MSK); keep the laptop on AC (79% at 17:40Z) (`CONTEXT.md` l.4684-4687).
7. [before-finals] **00:07Z post-deadline step (R44-A5 + R43-A8 = I-624 / I-607 / I-600 = W396 = C-361).** Save final_0007Z. Stop watchdog v2 30176/16728 FIRST (otherwise a false 'NO CLEAN POLL' alert fires at ~00:32Z), then 37016, 30864, 3028 + wrappers, 29828, 16748 and reader 1364/19012, checking each exact PID with Get-Process. `git add` `round44/`, `_lb/e10_20260929T1141Z/` and the digest. Commit as the user with NO Co-Authored-By (memory rule); `git log -1 --format=%B | grep -ci co-authored` must print 0. Curators split (facts [info]); settled [before-finals].
8. [before-finals] **Hindsight guard (I-336 / I-407 / I-252 / I-516).** Before 23:00Z (02:00 MSK), push one prediction commit quoting the 13:21Z audit grid (`CONTEXT.md` l.4593-4606; `research/wf_ideas_v4/risk_audit/results.json`).
9. [info] **Chris Deotte is NOT the host (I-584, C34, F-RUL-41).** Round 43's 'only host statement' was wrong: he is a participant ('2870th in this Competition', no staff tag). Selina Wu's 16:04Z lock question in 744250 is unanswered. The tick plan does not change (`round44/scan_plancheck.json` R44-PC-04; https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744250). Curators split (watch [today]); settled [info] (2 of 3).
10. [info] **Write-up rechecks (RC-A/B/C = I-625 / I-626 = T243, C-362..C-364).** CI makes near pairs < 2 um (exp87a 67 vs exp85a 17; GT 0) with no score effect. exp03B's '+0.0048' is within the seed spread. Dummy-lab signs are 6bba reads; 'divset36 flags 44b6' is refuted (`FACTS.md` F-TRN-80 l.547).
11. [info] **Bookkeeping (W126, W385).** After the tick, add `experiments/RESULTS.md` rows P47-P55 (the file ends at P46). Refresh the prompt KEY FACTS only if another round runs.

**RESOLVED since curation 43** (`CONTEXT.md` l.4695-4697; `research/wf_ideas_v4/round44/report.notes.md` 17:33:14Z):
- R43-A6 census done at 17:13Z with the new PID list (C-351, I-529, W388). Feed loop 10924/20892 and stop job 32220 are gone with no orphan (C-354 (c), I-610 (c), R44-PC-06).
- Watchdog v2 (W383) and the manual-admit reader (W384) are confirmed alive. R43-A2 (b) (the `post_exp89t` card branch) is dropped by R44-A2 (g). Round 44's 'eleventh null round' miscount is corrected to the twelfth (C-365).

## HOW TO USE

- "Score of probe N?" -> `DECISIONS.md` §1 l.149; `experiments/RESULTS.md` (to P46); `experiments/lb_poll/ledger.md` / `poll.log`; `experiments/<exp>/probe.json`.
- "exp89t scored; what now?" -> `round44/report.json` R44-A2 (read-time block); decision-B mapping `CONTEXT.md` l.4643-4667; `WATCHLIST.md` NEXT 24 H l.83 (W393, T241); `IDEAS.md` I-620.
- "Which finals pair / is SELECTED ok?" -> `DECISIONS.md` §2 [c44] l.1024-1026; comparator `CONTEXT.md` l.4559-4574; failed-read rule l.4684-4687; audit `research/wf_ideas_v4/risk_audit/answer_ru.md`.
- "Which jobs run / what to stop?" -> `FACTS.md` F-RUN-65 l.351, C-361; `round44/report.json` R44-A5; `round43/report.json` R43-A8; `WATCHLIST.md` l.110.
- "Which rule decides this?" -> `DECISIONS.md` §3 l.1777; `FACTS.md` §5 l.353, CONTRADICTIONS l.549. "Was it tried?" -> `IDEAS.md`. "Is it true?" -> `FACTS.md`. "Next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~17:50Z 29 Sep, read the tail of `CONTEXT.md` §14 (above `## 9.`), the newest `===` header in `poll.log`, and `research/wf_ideas_v4/round45/` or later.
