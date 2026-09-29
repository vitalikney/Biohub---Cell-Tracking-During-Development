# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 41: state as of 2026-09-29 ~14:55 UTC (17:55 MSK). Git HEAD 2fcbedd (13:59:01Z 'Round 40 applied: reserve-slot edges, 18:37Z card builder with decision B, quiet window'), which follows ec3c5fb (13:34Z decision B) (`git log`). `CONTEXT.md` has 4,663 lines. The newest entry is l.4618-4642 (13:58Z ROUND 40 APPLIED), and `## 9. Literature` starts at l.4643; nothing was logged after 13:58Z. Uncommitted: `research/KNOWLEDGE/*` (curation-41 edits), `experiments/lb_poll/ledger.md`, `poll.log`, `experiments/discussions/feed_loop.log`, `state.json`. Untracked: `research/wf_ideas_v4/round41/` (report.json R41-A1..A8, 4 scans, 7 verdicts, NO REPORT.md), `research/KNOWLEDGE/_curation/41/`, `experiments/lb_poll/_lb/e10_20260929T1141Z/`, `experiments/discussions/744357.md`, `digest_20260929T1428Z.md`, `experiments/lb_poll/_night_subs.csv`, `_night_subs.err` (`git status`). Previous curation: 40 (~13:55Z). Times are UTC unless marked MSK (= UTC+3).
Deadline 29 Sep 23:59Z (30 Sep 02:59 MSK). The user ticks finals MANUALLY by 20:00Z (23:00 MSK); the session never ticks (`CONTEXT.md` l.3842-3855, l.4092). Rule anchors: PRE-REG v3 l.1576-1736 (R8 l.1671); GAP RULE v2 l.4009-4020; RULE v2.1 l.4104-4126; 09:00Z exp89t read rule l.4459-4470; R38 playbook l.4509-4537; R39 (T7 trigger, SELECTED comparator) l.4559-4574; **13:34Z DECISION B l.4607-4617**; **13:58Z R40 APPLIED (T3KEEP) l.4618-4642**.

## STATE IN 10 LINES

1. **Finals TICKED 2/2 = П3 {exp87a 56640366 (0.959), #37 56563521 (0.954)}**, API SELECTED 12:37:31Z (`CONTEXT.md` l.4579-4581; `DECISIONS.md` §2 [c41] l.1014-1016).
2. **Best = P51 exp87a (K + CI) = 0.959 = V_pub.** Unrounded it is ~0.95875 (`research/wf_ideas_v4/round41/scan_recheck.notes.md`). Rank #151 of 3,999, 18th of 23 in the 0.959 block (Chrome 14:19Z). The 0.963 cluster now has 7 teams (`research/wf_ideas_v4/round41/scan_browser.json` r41-lb-rank-151, r41-cluster-0963-seven; `FACTS.md` F-LB-41 l.277).
3. **No new LB score since curation 38.** P55 exp89t (K + DIS 2.25 + CI, 56669888) is still PENDING at the 14:49:35Z header (L > 5.82 h). Expected read ~18:17-18:29Z (21:17-21:29 MSK) (`experiments/lb_poll/poll.log` l.31918-31921; `FACTS.md` F-RUN-61 l.343).
4. **Decision B (13:34Z):** exp89t replaces exp87a ONLY at a display of >= 0.960; 0.959 keeps exp87a (code T3KEEP) (`CONTEXT.md` l.4607-4617, l.4618-4642). exp89t needs about +0.00075 public over exp87a to display 0.960, so a 0.959 read with no re-tick is the likely outcome (`WATCHLIST.md` I452).
5. **Round 40 applied at 13:58Z:** reserve-slot edges logged (the 14:10Z default edge has passed, so slot 2 expires unused); builder `mk_card_1837.py` installed as sha8 59c54168 with T3KEEP; decision-B message set; KEY FACTS refreshed (`CONTEXT.md` l.4618-4642; `DECISIONS.md` §3 l.1879; `FACTS.md` F-RUL-42 l.391).
6. **Round 41 (14:42Z) is NOT applied:** R41-A1..A8 are PROPOSED only, and nothing in CONTEXT is newer than 13:58Z (`research/wf_ideas_v4/round41/report.json`; `WATCHLIST.md` W381).
7. **The cancelled pre_exp89t job (w36816) is still ALIVE.** Curators saw it at 14:45Z and 14:48Z, and a local Get-Process check saw it at 14:55:18Z. At 17:40:00Z it will make 1-2 LB downloads inside the quiet window (`FACTS.md` C-335 l.874; `research/KNOWLEDGE/_curation/41/index.notes.md`).
8. **Background jobs alive at 14:55:18Z:** manual_admit w3028 (fires 19:44:45Z), feed loop w20892 (runs at ~15:59Z and ~17:29Z, then stopped by job w32220), poller w37016 (loops forever), FEED SIGNAL waiter w24700. The e10 waiter w20284 is gone (`WATCHLIST.md` l.97-127; `_curation/41/index.notes.md`).
9. **Private-risk audit (13:21Z) still stands:** medal risk moderate, silver risk high, keep the pair. Round 41 refuted the claim that the audit's harsh K value is a 'floor'. Keeping exp87a costs ~0 on average (±0.0007) (`CONTEXT.md` l.4593-4606; `FACTS.md` F-TRN-76 l.532, F-TRN-78 l.534).
10. **Next decision points, MSK [UTC]:** 18:13 [15:13] next round; before 20:40 [17:40] kill w36816 and apply patch a19e1bd6; 20:13 [17:13] liveness census; 20:29-20:35 [17:29-17:35] feed loop stops; before 21:00 [18:00] log the R41-A2 texts; ~21:17-21:29 [~18:17-18:29] exp89t read; 21:37 [18:37] card; ~22:20 [~19:20] T7; 22:43 [19:43] SELECTED check; 22:44:45 [19:44:45] manual-admit; 23:00 [20:00] tick; 00:05 [21:05] SELECTED check; 02:59 [23:59] deadline; 03:07 [00:07] post-deadline step (`WATCHLIST.md` l.97-127). **Ideas: 608** (lb-tested 65, lab-tested 28, refuted 279, deferred 50, in-plan 184, open 2). At-risk 13; strict orphan I-233 (`IDEAS.md` l.243, ORPHANS l.987).

## WHERE THINGS ARE

The knowledge base is `research/KNOWLEDGE/`, written only by `experiments/workflows/biohub-curator.js`:
- `INDEX.md` is this page. `CHANGES.md` holds per-curation deltas (v4, then 2-41). Curator logs are in `research/KNOWLEDGE/_curation/{v4,2,...,41}/`: `*.json` answers and `*.notes.md` crash-safe logs.
- `IDEAS.md` + `ideas.json` (I-001..I-608): CHANGES (41) l.243, ranking l.257, FINALS l.276, LADDER l.382, BASE l.504, RUN l.548, LOC l.633, DIV l.669, MODEL l.742, NODES l.795, INFER l.833, EF l.855, LINK l.875, VALID l.913, TESTSET l.968, ORPHANS l.987 (at-risk list l.995-1009).
- `FACTS.md`: state l.3; §1 metric l.195; §2 data l.212; §3 LB l.233 (F-LB-41 l.277); §4 runtime l.279 (F-RUN-61/62 l.343-344); §5 rules l.346 (F-RUL-42 l.391); §6 models l.393; §7 lab-to-LB l.453 (F-TRN-78 l.534); CONTRADICTIONS l.536 (C-335..C-343 l.874-882).
- `DECISIONS.md`: probes §1 l.147 (P55 l.210; [c41] l.571); finals §2 l.638 ([c41] snapshot l.1014-1016); E10 rule §2f l.1342; ladder/cards §2h l.1528; R1-R10 §3 l.1727 ([c41] rows l.1879-1882); changelog [c41] l.2098.
- `WATCHLIST.md` (~14:50Z): DUE NOW l.74 (W373, W380); CONTRADICTIONS l.85 (C21-C23 l.89-91); NEXT 24 H l.97; LATER l.128; INSIGHTS l.153 (I450-I461 l.157-168).

Key sources (paths from the repo root):
- `CONTEXT.md` (anchors above). LB: `experiments/RESULTS.md` (rows to P46 only); `experiments/lb_poll/poll.log`, `ledger.md`; fallback LB csv `experiments/lb_poll/_lb/e10_20260929T1141Z/lb.csv` (use with `--teams 3994`). Feed: `experiments/discussions/feed_loop.log`, `digest_20260929T1428Z.md`, `744357.md`.
- Kernels, each with a `probe.json`: V_pub `experiments/exp87a_k2cap6_div04_ra094_ci/`; final #37 `experiments/exp58_x138_safe_lowref/`; pending `experiments/exp89t_k2cap6_k_dis225_ci/`; П2 alt `experiments/exp75_k2_coordinject/` (0.955).
- Tools: `tools/uptest.py` (LB save / UP test), `tools/runtime_ledger.py`, `tools/build_probe_kernel.py`, `tools/dummy_gates.py`, `tools/kaggle_feed.py`. Round prompt: `experiments/workflows/biohub-research-round.js` (KEY FACTS l.20, stale; l.37 fallback contradiction C22).
- Round 41: `research/wf_ideas_v4/round41/` contains report.json (R41-A1..A8), report.notes.md (the PATCHR41 block, program sha8 e6df7fd1), scan_plancheck, scan_hyp_evedry41, scan_recheck, scan_browser and v_*.json. Round 40: `research/wf_ideas_v4/round40/` (scan_hyp_exp89tmsg40 = message pack). Rounds 29-35 and 37-41 have no REPORT.md.
- Private-risk audit: `research/wf_ideas_v4/risk_audit/` (results.json, skeptic.md, answer_ru.md). The card builder lives only in the scratchpad (`mk_card_1837.py`, sha8 59c54168). Background: `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v3/FINAL_REPORT.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md` CHANGES (41) l.243 and ORPHANS l.987)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-601 | Kill the cancelled pre_exp89t job: `Stop-Process -Id 36816 -Force` | At risk, overdue; hard edge 17:40Z (20:40 MSK) | R41-A1; `FACTS.md` C-335 |
| I-603 | Guard patch for `mk_card_1837.py`: 59c54168 -> a19e1bd6, `--dry-all` 35 ok | At risk; before 17:40Z (20:40 MSK) | R41-A3; `FACTS.md` C-337, F-RUN-62 |
| I-602 | Decision-B T7 (a/b) texts and manual-admit mapping (0.959 -> T3KEEP) | At risk; log before 18:00Z (21:00 MSK) | R41-A2; `FACTS.md` C-336 |
| I-604 | Evening input rules (`--lb`, PYTHONIOENCODING, `--lhi`, status-less headers) | At risk; applies at 18:37Z, ~19:20Z and 19:44:45Z | R41-A4; `FACTS.md` C-343 |
| I-607 (+ I-600) | 00:07Z post-deadline step: final save, stop poller and waiters, commit with no trailer | At risk; 30 Sep 00:07Z (03:07 MSK) | R41-A7; `FACTS.md` C-334 |
| I-336 / I-407 / I-252 / I-516 | Hindsight prediction (quote the audit grid), cap-family private line, H2/H3 lessons, truncation line | At risk; before 23:00Z (02:00 MSK) | `IDEAS.md` ORPHANS l.995-1001 |
| I-608 | Lines to use only if the user asks (K is not a floor; ~0 ±0.0007) | Conditional | R41-A8; `FACTS.md` F-TRN-78 |
| I-233 | Poller logs error_description | Strict orphan, no owner | `IDEAS.md` l.993 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/41/{ideas,facts,watch}.json`)

1. [now] **Kill pre_exp89t w36816 (R41-A1 = I-601 = W373 = C-335).** It was still alive at 14:55:18Z. Run `Stop-Process -Id 36816 -Force`, then check that `Get-Process -Id 36816` returns nothing and that w3028 is still alive. Leave w3028, w29648, w30864, w37016, w22236 and w32220 alone. Log the OPS line. Sources: `research/wf_ideas_v4/round41/report.json` R41-A1; `CONTEXT.md` l.4607-4617; `FACTS.md` C-335 l.874.
2. [now] **Round-prompt KEY FACTS, second refresh (R41-A6 = W380, plus C22).** Replace '#148 / 17th of 22' with #151 of 3,999 / 18th of 23. Add dates to the 28 Sep OPS times. Drop 'S0 tags pre_exp89t' and remove pre_exp89t from the l.37 allowed list. Drop the 'FIRST run e10_snapshot.py' fallback. Rounds 42-43 run Chrome-only, with no recheck lens. Do this before 15:13Z (18:13 MSK). Sources: `experiments/workflows/biohub-research-round.js` l.20, l.37; `report.json` R41-A6; `WATCHLIST.md` C22 l.91. (Curators disagreed: ideas and facts said [today], watch said [now]. Settled as [now] because the edge is 15:13Z.)
3. [today] **Card builder guard patch (R41-A3 = I-603 = W377 = C23).** Save the `<<<PATCHR41 .. PATCHR41>>>` block from `research/wf_ideas_v4/round41/report.notes.md` and run it; it must print 'patched sha8 a19e1bd6'. Then run it with `--write`, run `--dry-all` (35 ok) and log the sha8. Deadline: before 17:40Z. If the patch is not applied, use the manual rule: T1/T2 only at >= 0.960, T3KEEP at 0.959, T5 at <= 0.958, never T3/T4/UPWAIT. Sources: `report.json` R41-A3; `FACTS.md` C-337, F-RUN-62 l.344.
4. [today] **T7 and manual-admit texts still promote at '0.959 с UP' (R41-A2 = I-602 = W375 = C21 = C-336).** Before 18:00Z, log T7 (a) and (b) with '≥ 0.960 ... при 0.959 по вашему решению B остаётся exp87a'. Mapping: >= 0.960 -> T2; 0.959 -> T3KEEP; <= 0.958 -> T5_late. Never send T3_interim, T3_promotion, T4_k0, T4_BLIND or T4_question. Sources: `report.json` R41-A2; `research/wf_ideas_v4/round40/scan_hyp_exp89tmsg40.json`; `WATCHLIST.md` C21 l.89.
5. [today] **Evening crash paths and stale inputs (R41-A4 = I-604 = W378 = C-343).** Pass `--lb post_exp89t` only if the watcher printed 'post_exp89t: rank' with count 57; otherwise pass `--lb e10_20260929T1141Z --teams 3994`. Set `PYTHONIOENCODING=utf-8` on every call. T6 needs `--lhi`. If a header shows no status, read the newest `^ref,` block by hand. The card's rank label should read 14:41 МСК, not 14:45. Build the card fresh; never send an old `card_1837_*` file (I461). Do not restart armed jobs. Sources: `report.json` R41-A4; `WATCHLIST.md` I454-I456, I461.
6. [today] **Quiet window 17:30-20:00Z.** At 17:13Z run the liveness census (36816 should be gone; the FEED SIGNAL waiter is now w24700/11836). Confirm that stop job w32220 kills 20892/10924 after the ~17:29:20Z feed run. Sources: `FACTS.md` C-331, F-RUN-61; `report.json` R41-A5; `WATCHLIST.md` W379, T234.
7. [today] **exp89t read under decision B.** A 0.959 display is the likely read, so the T3KEEP message ('ничего менять не нужно') is the default. Only a display of >= 0.960 with a poller header <= 19:45:17Z triggers the swap line. Headers after 19:12:17Z are UNPROVEN-ins. Sources: `WATCHLIST.md` I452; `DECISIONS.md` §2 [c41] l.1016; `CONTEXT.md` l.4607-4642.
8. [before-finals] **Finals tick by 20:00Z (23:00 MSK).** П3 is already ticked. Run SELECTED checks at 18:37, 19:43 and 21:05Z with the R39-A4 comparator. T7 fires at ~19:20Z and manual-admit at 19:44:45Z. Sources: `CONTEXT.md` l.4559-4581; `DECISIONS.md` §2 l.1014.
9. [before-finals] **Hindsight guard.** Before 23:00Z (02:00 MSK), push one I-336 prediction commit that quotes the 13:21Z audit grid, plus the I-407 line. Also I-252 and I-516. Sources: `CONTEXT.md` l.4593-4606; `research/wf_ideas_v4/risk_audit/results.json`; `IDEAS.md` l.997-1001.
10. [info] **00:07Z post-deadline step (R41-A7 = I-607 = W376).** Run `timeout 180 python tools/uptest.py save final_0007Z`, then 1 SELECTED read and 1 submissions list. Stop w37016, w22236 and the waiters. `git add` the untracked evidence. Commit as the user with NO Co-Authored-By trailer (the user's memory rule overrides the harness reminder), check `git log -1 --format=%B | grep -ci co-authored` = 0, then push. Sources: `report.json` R41-A7; `FACTS.md` C-334. (Curators disagreed: ideas said [before-finals], facts and watch said [info]. Settled as [info] because it fires after the deadline.)
11. [info] **Only-if-asked lines (R41-A8 = I-608).** Do not call the audit's K a 'floor'. The cost of keeping exp87a is ~0 on average (±0.0007), not 'at best ~0.0005'. The insertion evidence is the two public +0.001 reads. Sources: `FACTS.md` C-339..C-341, F-TRN-78 l.534.
12. [today / info] **Bookkeeping.** Log 'ROUND 41 APPLIED' in CONTEXT once A1-A6 are done (W381). After the tick: add `experiments/RESULTS.md` rows P47-P55 (the file ends at P46, l.79), render REPORT.md for rounds 37-41, and commit `round41/`. Sources: `WATCHLIST.md` W381, W126; `IDEAS.md` I-232.

**RESOLVED since curation 40:**
- R40-A1, A3, A4 and A6 were applied at 13:58Z and committed in 2fcbedd, together with `round40/` (`CONTEXT.md` l.4618-4642).
- R40-A2 was answered by decision B.
- The reserve-slot 14:10Z edge passed; the default is that slot 2 expires unused.
- The e10 waiter w20284 is gone.
- Closed contradictions: C-328, C-329, C-332 and C-333 in FACTS; C18, C19 and C20 in the watchlist.
- Dropped from the top list: 'do not send R40-A2' (moot), and the {exp75, #37} ready answer (folded into I-608).

## HOW TO USE

- "Score of probe N?" -> `DECISIONS.md` §1 l.147; `experiments/RESULTS.md` (to P46); `experiments/lb_poll/ledger.md` / `poll.log`; `experiments/<exp>/probe.json`.
- "exp89t scored; what now?" -> decision B `CONTEXT.md` l.4607-4617 and T3KEEP l.4618-4642; R41-A2 texts in `research/wf_ideas_v4/round41/report.json`; I-602 / I-604; `WATCHLIST.md` NEXT 24 H l.97.
- "Which finals pair / is SELECTED ok?" -> `DECISIONS.md` §2 [c41] l.1014-1016; comparator `CONTEXT.md` l.4559-4574; audit `research/wf_ideas_v4/risk_audit/answer_ru.md`; `FACTS.md` F-TRN-76/78.
- "Which jobs run / what to kill?" -> `FACTS.md` F-RUN-61 l.343; `WATCHLIST.md` l.74-127; `report.json` R41-A1, R41-A5, R41-A7.
- "Which rule decides this?" -> `DECISIONS.md` §3 l.1727; `FACTS.md` §5 l.346 and CONTRADICTIONS l.536. "Was it tried?" -> `IDEAS.md`. "Is it true?" -> `FACTS.md`. "What is next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~14:55Z 29 Sep, read the tail of `CONTEXT.md` §14 (above `## 9.`), the newest `===` header in `poll.log`, and `research/wf_ideas_v4/round42/` or later.
