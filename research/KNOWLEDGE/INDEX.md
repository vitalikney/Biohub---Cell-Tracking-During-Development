# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 45: state as of 2026-09-29 ~18:50 UTC (21:50 MSK). Git HEAD 2361191 (18:37Z card) after 1ae6716 (17:54Z 'Round 44 applied') (`git log`). `CONTEXT.md` has 4,741 lines; the newest entries are 17:54 ROUND 44 APPLIED l.4698-4712, 18:13 ROUND 45 LAUNCHED l.4713-4716 and 18:37 FINALS CARD l.4717-4720; `## 9. Literature` starts at l.4721. Round 45 (`research/wf_ideas_v4/round45/report.json`, 18:39Z, R45-A1..A6) is **PROPOSED and not yet in CONTEXT**. Untracked: `round45/`, `research/KNOWLEDGE/_curation/45/`, `experiments/lb_poll/_lb/e10_20260929T1141Z/`, `_night_subs.*` (`git status`). Times are UTC unless marked MSK (= UTC+3).
Deadline 29 Sep 23:59Z (30 Sep 02:59 MSK). The user ticks finals MANUALLY by 20:00Z (23:00 MSK); the session never ticks (`CONTEXT.md` l.3842-3855, l.4092). Rule anchors: PRE-REG v3 l.1576-1736; GAP RULE v2 l.4009-4020; R39 comparator l.4559-4574; **DECISION B l.4607-4617**; R41 APPLIED l.4643-4667; R43 APPLIED l.4678-4694; **R44 APPLIED l.4698-4712**.

## STATE IN 10 LINES

1. **Finals TICKED 2/2 = П3 {exp87a 56640366 (0.959), #37 56563521 (0.954)}**, re-verified by API SELECTED at 18:37:20Z (case a), the first good read since 12:37:31Z (`CONTEXT.md` l.4717-4720; `DECISIONS.md` §2 [c45] l.1029-1031).
2. **Best = P51 exp87a = 0.959 = V_pub.** Rank **#154 of 4,007 LB rows** (Chrome 18:16Z), 6th from the bottom of the 0.959 block #144-#159 (`FACTS.md` F-LB-44 l.283, C-373 l.930).
3. **No new LB score since curation 38.** P55 exp89t (56669888) is still PENDING at the 18:45:27Z header, L = 9.75 h, past the observed CI band 8.88-9.48 h; any T1 read from ~18:55:29Z on carries the ins-tail note (`experiments/lb_poll/poll.log` l.33144; `FACTS.md` F-RUN-66 l.354; `IDEAS.md` I-486).
4. **Decision B:** exp89t replaces exp87a only at a public >= 0.960 (T1/T2); 0.959 -> T3KEEP (expected); <= 0.958 -> T5; T7 at the first CLEAN header >= 19:12:17Z (22:12 MSK); admit edge 19:45:17Z (manual-admit 19:44:45Z, reader ~19:47Z); later -> T8 (`CONTEXT.md` l.4607-4617, l.4643-4667; `round45/report.json` R45-A1 (4)).
5. **Round 44 APPLIED 17:54Z (A1-A4):** read-time block `readtime.sh` befef6fb + `msg44.py` 233e5ba5 + `cardfix44.py` af903431; A5 (00:07Z stop order) was NOT logged (`CONTEXT.md` l.4698-4712; `FACTS.md` F-RUL-47 l.406).
6. **Round 45 ran 18:13-18:39Z at the user's request** (overriding R44-A1); 13th null round for levers. PROPOSES: A1 per-event push rule; A2 battery message; A3 stop-order amendment (live watchdog 16220/9596); A4 post-deadline private read on request; A5 hourly flip check (needs the user's yes); A6 write-up wordings (`round45/report.json`; `FACTS.md` F-TRN-81 l.552).
7. **Laptop on battery since 17:43Z**, 59% at 18:41Z, ~21%/h -> hibernate ~23:40-00:25 MSK; pushes are not delivered, so the chat is the only channel (`CONTEXT.md` l.4698-4712; `WATCHLIST.md` T244 l.82).
8. **Slot 2 CLOSED UNUSED since ~16:50Z;** no round proposes a submit or build (`CONTEXT.md` l.4689-4690; `round45/v_recheck_r45-nf-no-build-no-slot-no-tick-change.json`).
9. **Private-risk audit (13:21Z) stands:** keep the pair; DIS private sign unknown (-0.003..+0.0007) (`CONTEXT.md` l.4593-4606; `FACTS.md` C-374).
10. **Next, MSK [UTC]:** now: log R45-A1 + tell the user to plug in; 21:55:29 / 22:05:3x [18:55 / 19:05] headers; **22:12+ [19:12:17+] T7**; 22:43 [19:43] SELECTED (case= only); 22:44:45-22:47 [19:44:45-19:47] admit edge (ADMIT_PENDING=1 if still PENDING); **23:00 [20:00] tick**; 00:05 [21:05] SELECTED; 02:00 [23:00] hindsight commit; 02:59 [23:59] deadline; 03:07 [00:07] save / stop (watchdog 16220 first) / commit (`WATCHLIST.md` NEXT 24 H l.77). **Ideas: 634** (lb-tested 65, lab-tested 28, refuted 291, deferred 51, in-plan 197, open 2); 14 at risk; strict orphan I-233 (`IDEAS.md` l.253, ORPHANS l.1023).

## WHERE THINGS ARE

The knowledge base is `research/KNOWLEDGE/`, written only by `experiments/workflows/biohub-curator.js`:
- `INDEX.md` is this page. `CHANGES.md` holds per-curation deltas (v4, 2-41, 43-45). Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,41,43,44,45}/` (`*.json` answers, `*.notes.md` crash-safe logs).
- `IDEAS.md` + `ideas.json` (I-001..I-634): CHANGES (45) l.253, ranking l.267; FINALS l.286, LADDER l.395, BASE l.525, RUN l.569, LOC l.660, DIV l.696, MODEL l.769, NODES l.822, INFER l.862, EF l.885, LINK l.905, VALID l.944, TESTSET l.1004; ORPHANS l.1023.
- `FACTS.md`: state l.3; §1 metric l.198; §2 data l.215; §3 LB l.236 (F-LB-44 l.283); §4 runtime l.285 (F-RUN-66 l.354); §5 rules l.356 (F-RUL-47 l.406); §6 models l.408; §7 lab-to-LB l.468 (F-TRN-81 l.552); CONTRADICTIONS l.554 (C-366..C-376 l.923-933).
- `DECISIONS.md`: probes §1 l.150 (P55 l.213; [c45] l.580); finals §2 l.647 ([c45] snapshot l.1029-1031); E10 rule §2f l.1417; ladder §2h l.1603; R1-R10 §3 l.1802 ([c45] rows l.1968-1972); changelog [c45] l.2194.
- `WATCHLIST.md` (~18:45Z): DUE NOW l.47 (W398-W404); CONTRADICTIONS l.61 (C36-C40); NEXT 24 H l.77; LATER l.98; INSIGHTS l.124 (I485-I496).

Key sources (paths from the repo root):
- Logs and LB: `CONTEXT.md` (anchors above); `experiments/RESULTS.md` (rows only to P46); `experiments/lb_poll/poll.log`, `ledger.md`; card LB csv `experiments/lb_poll/_lb/e10_20260929T1141Z/lb.csv` (1,006 rows; card only, with `--teams 3994`; never a baseline for N or the drop test).
- Kernels (each with `probe.json`): V_pub `experiments/exp87a_k2cap6_div04_ra094_ci/`; final #37 `experiments/exp58_x138_safe_lowref/`; pending `experiments/exp89t_k2cap6_k_dis225_ci/`; П2 alternative `experiments/exp75_k2_coordinject/`.
- Tools: `tools/uptest.py`, `tools/runtime_ledger.py`, `tools/build_probe_kernel.py`, `tools/kaggle_feed.py`. Round prompt `experiments/workflows/biohub-research-round.js` (KEY FACTS l.20 stale). Read-time scripts (`r44dry/readtime.sh`, `msg44.py`, `cardfix44.py`, `mk_card_1837.py`, card `card_1837_PENDING.txt` 2e46a239) live in the session scratchpad (`CONTEXT.md` l.4698-4720).
- Rounds: `research/wf_ideas_v4/round45/` (report.json R45-A1..A6, Russian text in next_focus; 4 scans; 11 v_*.json; no REPORT.md); `round44/` (R44-A1..A5); `round43/`. Private-risk audit `research/wf_ideas_v4/risk_audit/`; background `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md` CHANGES (45) l.253 and ORPHANS l.1023)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-627 | R45 per-event rule: pushtext44 only at the first terminal read, T7 and the admit edge; later act on readtime's `SELECTED case=` only; never send msg44's 'neither' line; ADMIT_PENDING=1 at the edge; '[ERROR' header is not clean | In plan, at risk; log before T7 19:12Z | R45-A1; `FACTS.md` C-366..C-368 |
| I-629 | Battery message (re-measure first; plug in before 23:00 MSK, lid open); optional <= 25% one-shot | In plan, at risk; now | R45-A2; `FACTS.md` C-370 |
| I-620 / I-623 | Read-time block (one Bash call, timeout 600000, HOLD guard; L_hi when F >= 1) | Logged 17:54Z; runs at each header to 19:45:17Z | R44-A2; `CONTEXT.md` l.4698-4712 |
| I-624 / I-607 / I-600 | 00:07Z: save final_0007Z; stop CURRENT watchdog 16220/9596 first, then 37016 and the rest; git add round44/ + round45/; commit with no trailer | At risk; needs AC power | R44-A5 + R45-A3; `FACTS.md` C-369 |
| I-630 | Post-deadline private read on request: 1 submissions call `--page-size 100`, privateScore flip detector, sign pairs, medal lines; read_private.py only after 23:59Z | In plan, at risk; log tonight | R45-A4; `FACTS.md` C-371, C-372 |
| I-631 | Hourly private-flip check | Waits for the user's explicit yes | R45-A5; `WATCHLIST.md` C39 |
| I-336 / I-407 / I-252 / I-516 | Hindsight prediction quoting the audit grid; cap-family private line; lessons (with R45-A6 wordings); truncation line | At risk; before 23:00Z (02:00 MSK) | `IDEAS.md` ORPHANS l.1023 |
| I-233 | Poller logs error_description | Strict orphan, no owner | `IDEAS.md` ORPHANS l.1023 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/45/{ideas,facts,watch}.json`)

1. [now] **R45-A1 per-event rule not in CONTEXT (I-627 / I-628 = W398 = C37 = C-366..C-368 = I485 / I487).** Under R44-A2 as logged, a correct re-tick to exp89t makes msg44.py (pairs hard-coded to exp87a) print a false 'SELECTED is neither' at 19:43Z / 21:05Z, and a T3KEEP / T5 push repeats at every later event. Append the R45 PER-EVENT RULE line before T7 (22:12 MSK); act only on `SELECTED case=` (`round45/report.json` R45-A1; `round45/v_plancheck_r45-pc-01.json`).
2. [now] **Battery (I-629 = W399 / T244 = C-370).** On battery since 17:43Z, ~21%/h, hibernate ~23:40-00:25 MSK: the 00:05 MSK check is a coin flip and the 03:07 MSK save/stop/commit a near-certain miss; watchdog 16220 ignores percent. Re-measure Win32_Battery, then tell the user in chat (MSK first) to plug in before 23:00 MSK. No power-plan change without the user's OK (`round45/report.json` R45-A2; `round45/v_plancheck_r45-pc-03.json`).
3. [now] **exp89t read chain (F-RUN-66, C-367, C-368).** Headers ~18:55:29 / 19:05:3xZ (T1 carries the ins-tail note); T7 at the first clean header >= 19:12:17Z; at the admit edge run `ADMIT_PENDING=1 pushtext44` in the same Bash call if still PENDING (plain pushtext44 prints the wrong T7 text); all messages go to the chat (`round45/report.notes.md` PC-02 dry run; `poll.log` l.33144). Curators split (facts [before-finals]); settled [now].
4. [today] **00:07Z stop order names dead PIDs (I-624 = W400 (b) = C38 = C-369).** 30176/16728 are gone; stop the live watchdog 16220/9596 (or its re-arm) first by exact PID, then 37016 and the rest; otherwise a false NO CLEAN POLL fires ~00:32Z. On a BACK ON AC alert before ~19:50Z, re-arm watchdog v2 (`round45/report.json` R45-A3; `round45/scan_plancheck.json` R45-PC-04).
5. [today] **SELECTED checks 19:43Z / 21:05Z (R43-A3, R45-A1 (2)).** Act on case= only; after 20:00Z an a_old / b_old case says 'смените до закрытия в 02:59 МСК'. The user confirms '2 of 2 selected' by 23:00 MSK (`CONTEXT.md` l.4684-4687; `DECISIONS.md` §2 [c45]).
6. [today] **Round 45 not logged as applied (W404) + private-read plan only in report.json (I-630 = W401 = C-371 / C-372 = C40).** Log 'ROUND 45 APPLIED' and a PRIVATE READ (R45) line; never use the 1,006-row e10 lb.csv as a baseline; 0 Kaggle calls before 00:07Z. After the tick, ask once (MSK) about the hourly check (I-631 = W402 = C39) (`round45/report.json` R45-A4, R45-A5). Curators split (ideas [before-finals], facts [info]); settled [today].
7. [before-finals] **Hindsight guard (I-336 / I-407 / I-252 / I-516).** Before 23:00Z (02:00 MSK), push one prediction commit quoting the 13:21Z audit grid (`CONTEXT.md` l.4593-4606; `research/wf_ideas_v4/risk_audit/results.json`).
8. [info] **Stale KEY FACTS + rank line (I-614 / I-259, C-373).** The round prompt l.20 still says '#151 of 3 999', '5 min'; current: #154 of 4,007 (Chrome 18:16Z), 6th from the bottom of the 0.959 block (to #159), ~10-min polls, slot 2 closed. Refresh only if round 46 runs (local files + Chrome, 0 Kaggle calls, clear of 19:12-19:50Z) (`experiments/workflows/biohub-research-round.js` l.20; `round45/scan_browser.json`).
9. [info] **Write-up wordings (R45-A6 = I-633 / I-634 / I-384 = C-374..C-376 = I491 / I492).** DIS private sign unknown (-0.003..+0.0007; the 7x near-GT depletion is in-sample selection); I-384 sub-form CLOSED by probe 54 ('trigger did not fire'); FLOW_Z_WEIGHT 0.85 untested, predicted inert (`round45/scan_recheck.json`; `FACTS.md` F-TRN-81 l.552).
10. [info] **Bookkeeping (W126).** After the tick, add `experiments/RESULTS.md` rows P47-P55 (file ends at P46).

**RESOLVED since curation 44** (`CONTEXT.md` l.4698-4720): round 44 logged (A1-A4; I-620, I-613, I-597 = W392 / W393 / W395 / W397); round 45 timing overridden by the user (I-617, C36); 18:37Z card built (2e46a239, no push needed) and SELECTED read case a (I-592, I-589, C-357 / C-358); watchdog v2 30176/16728 replaced by 16220/9596 (C-361 -> C-369).

## HOW TO USE

- "Score of probe N?" -> `DECISIONS.md` §1 l.150; `experiments/RESULTS.md` (to P46); `experiments/lb_poll/ledger.md` / `poll.log`; `experiments/<exp>/probe.json`.
- "exp89t scored; what now?" -> decision B `CONTEXT.md` l.4607-4617, l.4643-4667; read-time block l.4698-4712; per-event rule `round45/report.json` R45-A1; `WATCHLIST.md` W398 l.51, NEXT 24 H l.77; `IDEAS.md` I-627.
- "Which finals pair / is SELECTED ok?" -> `DECISIONS.md` §2 [c45] l.1029-1031; comparator `CONTEXT.md` l.4559-4574; failed-read rule l.4684-4687; audit `research/wf_ideas_v4/risk_audit/answer_ru.md`.
- "Which jobs run / what to stop at 00:07Z?" -> `FACTS.md` F-RUN-66 l.354, C-369; `WATCHLIST.md` l.102; `round45/report.json` R45-A3; `round44/report.json` R44-A5.
- "Private score after the deadline?" -> `round45/report.json` R45-A4 / A5; `IDEAS.md` I-630, I-631; `FACTS.md` C-371, C-372.
- "Which rule decides this?" -> `DECISIONS.md` §3 l.1802; `FACTS.md` §5 l.356, CONTRADICTIONS l.554. "Was it tried?" -> `IDEAS.md`. "Is it true?" -> `FACTS.md`. "Next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~18:50Z 29 Sep, read the tail of `CONTEXT.md` §14 (above `## 9.`), the newest `===` header in `poll.log`, and `research/wf_ideas_v4/round46/` or later.
