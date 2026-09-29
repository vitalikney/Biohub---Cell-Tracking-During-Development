# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-29 ~17:45 UTC (20:45 MSK), curation 44. This updates the curation-43 build of ~16:45Z (committed in 19149bf; structured copy in `research/KNOWLEDGE/_curation/43/watch.json`). Older predecessors run from `_curation/41/watch.json` down to `_curation/18/watch.json` (there was no curation 42). Rows not repeated here are unchanged there.

**Sources read for this update:**
- **`CONTEXT.md`:** 4,718 lines; `## 9. Literature` starts at l.4698. Two new entries since curation 43:
  - l.4678-4694 (16:43Z): **ROUND 43 APPLIED** (A1-A5, A7; A6 at 17:13Z; A8 at 00:07Z). Watchdog v2 on clean headers (A1, l.4679-4680); manual-admit reader (A2, l.4680-4683); SELECTED failed-read rule (A3, l.4684-4687); `--hdr` from awk first terminal header + manual 'ins-tail?' note (A4, l.4687-4688); card rank line (A5, l.4688-4689); **SLOT 2 CLOSED UNUSED from ~16:50Z** (A7, l.4689-4690); new header phase and 3 error blocks (l.4691-4694).
  - l.4695-4697 (17:13Z): **LIVENESS (R43-A6)**: all evening jobs alive, pre_exp89t 0 processes, on AC; round 44 launched.
  - **Nothing is logged after 17:13Z** (checked 17:40Z). Round 44 is NOT yet applied.
- **`git log`:** **19149bf** (16:43Z, round 43 + curation 43). **`git status`** (start of this session): `M` CONTEXT.md, ledger.md, poll.log, discussions files, KNOWLEDGE files; `??` **`research/wf_ideas_v4/round44/`**, `experiments/discussions/digest_20260929T1729Z.md`, **`_lb/e10_20260929T1141Z/` (still untracked)**, `_night_subs.*`, `_curation/43/*.json`.
- **`research/wf_ideas_v4/round44/report.json`** (written 17:37:24Z, untracked, **not yet applied**): **R44-A1..A5**, new_facts (1)-(9), plan_issues (1)-(8), rejected; the Russian report text is in `next_focus` (no REPORT.md). Also `round44/report.notes.md`, `scan_plancheck.notes.md`, `scan_hyp_ops44.notes.md`, `scan_browser.notes.md`, `scan_recheck.json`.
- **`experiments/lb_poll/poll.log`:** newest header **17:35:08Z** (l.32717); exp89t 56669888 **PENDING** (l.32720); `ledger.md` (17:35:10Z) gives L > 8.58 h (l.20).
- **`experiments/discussions/feed_loop.log`:** the last run was **17:29:24Z** (rc=0, 1 "new" comment = Selina Wu 744250 16:04Z, E10 FLAG none); the loop is stopped (census below).
- **Round prompt `experiments/workflows/biohub-research-round.js`:** unchanged since 55ec8ab. l.20 still has "#151 of 3 999", "S0 tags pre_exp89t (17:40Z)", "polls every 5 min" (per `round44/scan_plancheck.notes.md`); l.37 still lists pre_exp89t among the callers (C22, C24, C25 open in the prompt).
- **`experiments/RESULTS.md`:** probe rows still end at probe 46 (l.79).
- **Process census 17:40Z (this curation, Win32_Process, read-only, 0 Kaggle calls):**
  - Alive: poller 37016; orphans of the dead claude 15852: old exp89t watcher 29636->30864, manual_admit 29032->13708 + 3028; new session (claude 12724): exp89t waiter 9016->29828, t7_trigger 34124->6344 + 16748, timers 30820 (18:13Z, wrapper 18108/28716), 29184 (18:37Z, 12616/30288), 20960 (19:43Z, 37052/21048), 24260 (21:05Z, 9828/22556), 21232 (00:07Z, 23564/35912), **watchdog v2 30176->16728**, **manual-admit reader 1364->19012**.
  - Gone: the blind watchdog 22680/5024 (W383 done), feed loop 10924/20892 and the feed stop job 32220 (also `round44/report.notes.md` 17:33:14Z), pre_exp89t.
  - No `post_exp89t` folder in `experiments/lb_poll/_lb/` (only S0_0729Z, S1_*, e10_20260929T1141Z, post_exp75).
  - Battery: BatteryStatus 2 (AC), 79%.

All times are UTC. The user thinks in MSK = UTC+3 (`CONTEXT.md` l.3683-3687). IDs are stable: W = action, T = time-bound reminder, I = insight, C = contradiction. Status values: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at ~17:40Z, 29 Sep:**
- **Best display 0.959**, exp87a 56640366 = V_pub.
- **SELECTED = П3 {exp87a 56640366, #37 56563521}** (API 12:37:31Z, `CONTEXT.md` l.4579-4581).
- **Decision B:** exp89t promotes only at **>= 0.960** (l.4607-4617).
- **exp89t 56669888 PENDING** (T0 09:00:17Z; L > 8.58 h at 17:35:08Z, `ledger.md` l.20). Projected clean headers, step 10:02.3 (`round44/report.json` new_facts (5)):
  - **18:15:17, 18:25:19, 18:35:22Z** (21:15-21:35 MSK), then 18:45:24, 18:55:26, 19:05:29Z;
  - **T7 ~19:15:31Z** (22:15 MSK); 19:25:33Z;
  - **last admissible header ~19:35:36Z**; the next, ~19:45:38Z, comes ~20 s after the 19:45:17Z edge, so manual-admit 19:44:45Z is the only record in between.
- **Slot 2:** CLOSED UNUSED since ~16:50Z (`CONTEXT.md` l.4689-4690). No new file can finish by 23:59Z.
- **Rank:** **#154**, 0.959 block #144-#158, 5th from its bottom; **4,005 LB rows** / 4,003 teams on Overview (Chrome 17:14:40-17:17:53Z, `round44/report.json` new_facts (1)). Top: yu4u 0.978.

**Changes since ~16:45Z (curation 43):**
- **Done:**
  - **W383** (= R43-A1): watchdog v2 30176/16728 is armed and the blind 22680/5024 is gone (`CONTEXT.md` l.4679-4680; census 17:40Z);
  - **W384** (= R43-A2 (a)): reader 1364/19012 is armed (l.4680-4683);
  - **W388** (= R43-A6): liveness logged (l.4695-4697); feed stop verified by PID (`round44/report.notes.md` 17:33:14Z);
  - **W391**: round 43 logged (l.4678) and committed (19149bf);
  - **T237**: round 44 ran 17:13-17:37Z (Chrome rank read 17:14:40Z, 744250 look 17:14:59Z);
  - **C26, C27, C28 resolved** in CONTEXT (l.4684-4687, l.4693-4694, l.4695-4697).
- **Partly done:** **W385**: the CONTEXT line "SLOT 2 CLOSED UNUSED" is in (l.4689-4690), but the prompt KEY FACTS (l.20 / l.37) were never refreshed (`round44/report.json` plan_issues (5)). W395 (R44-A4) now carries the refresh into CONTEXT instead.
- **Logged, apply at events:** W386 (l.4684-4687), W387 (l.4688-4689, now refined by W394), W389 (l.4687-4688).
- **Superseded / moot:** T226 (round 45 at 18:13Z) is now a NO-OP (R44-A1, W392); T238's phase is replaced by the R44 projection (T241); the old --lb rule of R41-A4 (1) / R43-A2 (b) is replaced by R44-A2 (g) (C31); the T234 feed run is done.
- **New:**
  - actions **W392-W396** (= R44-A1..A5) and **W397** (round 44 bookkeeping);
  - reminders **T241-T243**;
  - contradictions **C31-C35**;
  - insights **I474-I484**.

---

## OVERDUE / DUE NOW

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W392** (new; = **R44-A1**) | **Round 45 = NO-OP.** Append one CONTEXT line: the 18:13Z timer (timer.sh 30820, wrappers 18108/28716, text "HOURLY RESEARCH ROUND 45 (21:13 MSK): READS-vs-CARD") is a NO-OP, and a resumed session must not act on it. When it fires, ignore it and keep the session free for the 18:15:17 / 18:25:19 / 18:35:22Z reads and the 18:37Z card. Optional exception: a minimal local-files round only if the card was sent by 18:40Z AND the code was T1/T2, with a hard stop at 19:00Z. Keep 19:05-19:50Z free of rounds. **Do NOT kill 30820** (a `-match` kill could hit the other timer.sh PIDs) | **not started** (CONTEXT newest 17:13Z; l.4697 lists the 18:13Z timer without "NO-OP") | **before 18:13Z** (21:13 MSK) | `round44/report.json` R44-A1, plan_issues (1); `round44/scan_plancheck.notes.md` "Finding" |
| **W395** (new; = **R44-A4**) | **One CONTEXT OPS line + KEY FACTS:** <br>- feed ran 17:29:24Z (rc=0) and stopped cleanly (0 kaggle_feed.py processes at 17:33:14Z); <br>- the 17:34Z alive list; <br>- step 10:02.3, projected headers 18:15:17 ... 19:15:31 (T7) ... 19:35:36, 19:45:38Z; <br>- KEY FACTS for any later round: **#154 of 4 005 LB rows** (Chrome 17:15Z = 20:15 MSK), polls every ~10 min 2 s, slot 2 CLOSED UNUSED since ~16:50Z, feed stopped 17:29Z, round 45 NO-OP. <br>This also closes W385's unfinished prompt refresh for practical purposes (C24 / C25) | **not started** | **now, with W392** (before 18:13Z) | `round44/report.json` R44-A4, plan_issues (5) |
| **W397** (new; bookkeeping) | Log "ROUND 44 APPLIED (R44-A1..A5)" in CONTEXT. `research/wf_ideas_v4/round44/` is untracked | not started | with W392 / W395 | `git status`; `CONTEXT.md` l.4695-4697 |
| W385 (partly done) | Prompt `biohub-research-round.js` l.20 / l.37 refresh (stale #151 of 3 999, 5-min polls, "S0 tags pre_exp89t", "T7 ~19:20Z"; pre_exp89t in l.37) | **CONTEXT part done** (l.4689-4694); **prompt part not done** (unchanged since 55ec8ab). Moot if no further round runs; W395 puts the facts in CONTEXT | only before any further round | `round44/scan_plancheck.notes.md` "KEY FACTS ... still stale"; R44-A4 |
| W126 (part 2) | Add RESULTS.md rows for probes 47-54 (47: 0.955; 48: 0.957; 49: 0.955; 50: exp85a 0.958; 51: exp87a 0.959; 52: exp89r 0.957; 53: exp75 0.955; 54: exp89p 0.956), then probe 55 (exp89t) when it reads | **overdue** (rows end at 46, l.79); values are in `ledger.md` | low; post-deadline OK | `experiments/RESULTS.md` l.79; `experiments/lb_poll/ledger.md` |
| W336 | One line saying that the user's 08:27Z / 08:28Z instructions override R8's 10:00Z edge (l.1671) | not started; moot in practice | low | `CONTEXT.md` l.1671 |
| W286 / W297 / W202 + W244 / W176 / W177 / W182 / I208 / W57 / W66 / W31 / W72 / W150 / W308 | Older text and cleanup items | overdue, low | H2 29 Sep 23:00Z; post-deadline OK | `_curation/36/watch.json`, `_curation/26/watch.json` |

## CONTRADICTIONS TO RESOLVE BEFORE THEY FIRE

| ID | Conflict | Which text wins | Evidence |
|---|---|---|---|
| **C31** (new) | **Card `--lb`.** CONTEXT R41-A4 (l.4662-4663) and R43-A2 (b) say: pass `--lb post_exp89t` if the watcher output has "post_exp89t: rank" with SubmissionCount 57. R44-A2 (g) says: never pass it; the folder does not exist and `uptest.load` would crash; drop the `bud7lhxmi.output` card read | **R44-A2 (g):** always the default `--lb e10_20260929T1141Z --teams 3994` (already in `cardcmd`). Confirmed: no `post_exp89t` folder in `_lb/` at 17:40Z. Fix in CONTEXT when R44 is applied (W397) | `round44/report.json` R44-A2 (g); `ls experiments/lb_poll/_lb/` 17:40Z |
| **C32** (new; refines C29) | **Rank-line denominator.** CONTEXT R43-A5 (l.4688-4689): "#154 of 4 003" (16:15Z). Round 44: 4 003 is the Overview team count, while the LB shows 4 005 rows at 17:15Z; round 43's 4 003 was an LB-row count | **R44-A3:** "Chrome 20:15 МСК", "#154 из 4 005, лучший паблик 0.959, 5-е снизу в блоке 0.959 (блок до #158)." The 4 003 default is also accepted by the cardfix asserts. Cosmetic | `round44/report.json` R44-A3, plan_issues (4); `round44/scan_hyp_ops44.notes.md` DEFECTS (4) |
| **C33** (new) | **Edge keying.** R41-A3 / the builder key "late" and T8 on the header (`CONTEXT.md` l.4659-4661); R38-A5 keys on L_hi = hdr + 210 s x F - T0. `scan_hyp_ops44` said the projected headers are outside the disagreement windows; the report found that the **projected 19:05:29Z header is inside the F=2 window (19:05:17, 19:12:17]** | **R44-A2 (h):** follow R41-A3 (header-keyed); if the terminal header carries F >= 1 failed attempts, also log L_hi in CONTEXT. Only the UNPROVEN-ins / DIS «?» wording can differ, never the pair | `round44/report.json` R44-A2 (h), plan_issues (3), rejected |
| **C34** (new) | **Who said "It must finish before 23:59 UTC".** Curation 43 (T239, I469) called Chris Deotte's line "the only host statement". Round 44's Chrome read: Deotte is a participant ("2870th in this Competition", no staff tag) | **Round 44:** there is **no host/staff statement** on when selection locks. The plan (tick by 23:00 MSK) does not change | `round44/scan_plancheck.notes.md` 17:14:59Z; `round44/report.json` new_facts (2) |
| **C35** (new) | **The 18:13Z timer.** Its text asks for "HOURLY RESEARCH ROUND 45 (21:13 MSK): READS-vs-CARD"; the 17:13Z CONTEXT line (l.4697) lists it as a normal timer; curation 43 T226 had round 45 as pending | **R44-A1 (W392):** NO-OP, not launched. The first possible read header is 2 min later (18:15:17Z) and a round takes ~30 min | `round44/report.json` R44-A1; `round44/scan_plancheck.notes.md` |
| C24 (updated) | **Header phase.** Prompt l.20 "T7 trigger ~19:20Z"; CONTEXT l.4691-4692 (R43): T7 ~19:15:35Z, last admissible ~19:35:40Z. Round 44 re-measured step 10:02.3 over 10 clean headers | **`round44/report.json` new_facts (5):** T7 ~19:15:31Z, last admissible ~19:35:36Z, next ~19:45:38Z. The difference to R43 is 4 s; the prompt stays stale (W385) | `round44/report.notes.md` "poll.log" line |
| C25 (open in the prompt) | Prompt l.20 "status polls every 5 min" vs ~10 min 2 s | **Real cadence** (CONTEXT l.4691). W395 | `round44/scan_plancheck.notes.md` |
| C30 (partly resolved) | T1 'ins-tail?' footnote: R43-A4 manual note is logged (l.4687-4688). **Still open:** l.3750 "L_hi in (9.6, 10.2]" vs l.4014 / l.4688 "L_lo > 9.6 h". The r44dry `cardfix44.py` adds the note (dry scenario "T1instail (L_lo 9.75)") | **l.4014 / R43-A4 (L_lo)** | `CONTEXT.md` l.3750, l.4014, l.4688; `round44/scan_hyp_ops44.notes.md` |
| C22 (open) | Prompt l.37 lists pre_exp89t among the allowed callers and keeps the e10_snapshot fallback | **R39-A6 (Chrome only, 0 Kaggle calls after 12:00Z).** Round 44's browser scan made 0 calls (`round44/scan_browser.notes.md`) | `biohub-research-round.js` l.37 |
| C15 | The 18:37Z / 19:43Z / 21:05Z timer texts push "if not the recommended pair" | **The R39-A4 comparator plus R43-A3** (now inside the R44-A2 block). No push while SELECTED = П3 | `CONTEXT.md` l.4565-4568, l.4684-4687 |
| C26 / C27 / C28 / C29 | - | **Resolved** (C26: l.4693-4694; C27: l.4684-4687; C28: l.4695-4697; C29 -> C32) | `CONTEXT.md` |
| C11 / C17 / C21 / C23 | - | Resolved earlier | `_curation/43/watch.json` |

## NEXT 24 H (29 Sep ~17:45Z -> 23:59Z)

| ID | When (UTC / MSK) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W392 + W395 + W397 | **now; before 18:13Z** (21:13 MSK) | CONTEXT: round 45 NO-OP, OPS line + KEY FACTS, "ROUND 44 APPLIED" | not started | see OVERDUE |
| T213 | all evening | **Laptop on AC with the lid open and a stable network** until 23:00 MSK. AC 79% at 17:40Z. Watchdog v2 alerts on battery or > 25 min without a clean header | watch | `CONTEXT.md` l.4668-4680; census 17:40Z |
| T228 | **17:30-20:00Z** (20:30-23:00 MSK) | Quiet window: only the poller, the old watcher's save, manual_admit and the SELECTED reads call Kaggle. The feed is stopped | standing | `round44/report.notes.md` 17:33:14Z |
| **T226** (superseded) | 18:13Z, timer 30820 | Round 45: **NO-OP** (W392). Do not kill the timer | moot | R44-A1 |
| **W393** (new; = **R44-A2**) + T208 + W344 + W386 + W389 | **every event:** read headers **18:15:17 / 18:25:19 / 18:35:22Z** (any time up to 19:45:17Z); card 18:37Z; T7 ~19:15:31Z; reader ~19:47Z; checks 19:43Z and 21:05Z | **READ-TIME BLOCK** (scratchpad `r44dry/readtime.sh` befef6fb, `msg44.py` 233e5ba5, `cardfix44.py` af903431; real builder `mk_card_1837.py` a19e1bd6). <br>- **One Bash call per event, tool `timeout: 600000`** (worst case ~250 s > the 120 s default). <br>- Source `readtime.sh` on its own line, **never under a pipe**; never define a shell function named `msg` (Windows msg.exe). <br>- **HOLD guard:** status COMPLETE with an empty score -> no push, no card; if HOLD repeats, take by hand the first header whose 56669888 row has a score (the awk still picks the scoreless row). <br>- **Send every `pushtext44` line except "CONTEXT FIRST: RECOMMENDED PAIR"**; on T1/T2 append that line to CONTEXT before the push. <br>- Check the "READ:" line against poll.log by eye. <br>- SELECTED via `selread` (timeout 90); failed read -> one retry after 60 s, max 2 calls per event (R43-A3). <br>- If the terminal header is 18:35:22Z, one run serves both push and card. Still PENDING at 18:35:22Z -> PENDING card; a later read gets the push only. <br>- F >= 1 on the terminal header -> log L_hi too (C33). <br>- If `r44dry` fails, use the manual R43-A4 / R41-A4 path. <br>Codes (decision B): **>= 0.960 T1** (T2 if header > 19:12:17Z); **0.959 T3KEEP**; **<= 0.958 T5**; ERROR T6; after 19:45:17Z T8. **Expected: T3KEEP** (I452) | pending; **not yet logged in CONTEXT** (W397) | `round44/report.json` R44-A2; `CONTEXT.md` l.4607-4617, l.4648-4667, l.4684-4688 |
| T152 + **W394** (new; = **R44-A3**) + W387 | **18:37Z** (21:37 MSK), timer 29184 | **FINAL card**: `cardcmd && cardfix` in the W393 call. Default `--lb e10_20260929T1141Z --teams 3994` (C31). Rank line: RANKSRC="Chrome 20:15 МСК", RANKBODY="#154 из 4 005, лучший паблик 0.959, 5-е снизу в блоке 0.959 (блок до #158)." (C32); on T1/T2 cardfix adds ", до чтения exp89t". Log the card's sha8 next to a19e1bd6. **Never send an `r44dry/card_1837_*.txt`** (dry artefacts, I461). Never quote #151 / #148 / #141 / 3 999 / 3 994 / 17 из 22 | pending | `round44/report.json` R44-A3, R44-A2 (i) |
| **T241** (new; replaces T238) | headers **~19:05:29Z, ~19:15:31Z (T7), ~19:25:33Z, ~19:35:36Z, ~19:45:38Z** | Step 10:02.3. **The last admissible header before 19:45:17Z is ~19:35:36Z.** manual-admit 19:44:45Z is the only record in between; a result first seen at ~19:45:38Z is T8. The 19:05:29Z header is inside the F=2 edge window (C33) | info | `round44/report.json` new_facts (5), R44-A2 (h) |
| T227 | **~19:15:31Z** (22:15 MSK), t7_trigger 16748 | T7 (first header >= 19:12:17Z). If still PENDING: W393 block (1 SELECTED read with retry), then the **R41-A2 T7 text** (a, П3 ticked) | armed | `CONTEXT.md` l.4648-4655 |
| T161 + T221 + W384 | **19:43Z** timer 20960; **19:44:45Z** manual_admit 3028 (orphan); reader 1364/19012 fires by **19:47Z** (22:47 MSK) | Comparator check (W393). The reader output: first terminal header <= 19:45:17Z -> code per R41-A2 (>= 0.960 T2; 0.959 T3KEEP "(после 22:12 МСК)"; <= 0.958 T5 late) after 1 SELECTED read; still PENDING or "call FAILED" -> one log line, T8 path | **armed** (reader alive 17:40Z) | `CONTEXT.md` l.4680-4683 |
| T10 | **20:00Z (23:00 MSK)** | Finals tick. **Done: П3** (12:37Z). Re-tick only after exp89t >= 0.960 read by 19:45:17Z. The session never ticks. The user's own "2 of 2 selected" check is the last line of defence (I471) | done unless >= 0.960 | `CONTEXT.md` l.4579-4581, l.4617 |
| **T242** (new) | **after the 23:00 MSK tick is confirmed**, optional, once | Tell the user the laptop may sleep: the finals are ticked, and timer.sh re-checks the clock, so the 00:07Z step runs on wake (R44-A5 (2)). Note: watchdog v2 alerts on battery, so an unplug after 20:00Z will trigger it (expected, ignore) | optional | `round44/report.json` R44-A5 (2) |
| T232 | >= 20:05Z, optional | One manual kaggle_feed run | optional | `round40/report.json` R40-A5 |
| T222 / T153 / T162 | 20:00-23:59Z; **21:05Z** timer 24260 | Re-selection is assumed allowed until 02:59 MSK (no staff statement either way, C34). Comparator check with the W393 block; last-call notify on a mismatch. No submit without the user's yes | armed | `CONTEXT.md` l.4524, l.4549-4558, l.4565-4568 |
| T239 (updated) | any time before 23:59Z | **744250:** Selina Wu (16:04Z) "when does submission selection lock?" and kostopr4v (02:00 UTC private release) are unanswered; Deotte's "It must finish before 23:59 UTC" is a **participant** reply (C34). No further Chrome reads are planned after 17:30Z (R44 plan_issues (8)); quote any host answer verbatim if one is seen | watch | `round44/scan_plancheck.notes.md` 17:14:59Z |
| W382 | only if the user asks, before 20:00Z | The corrected answer lines (decision B cost ≈ 0; not "в лучшем случае ~0.0005"; K is not a "floor"; exp11 LOEO validated the score level only; no detector-side hedge partner) | conditional | `round41/report.json` R41-A8; `round43/report.json` rejected (2), (3) |
| W177 H2 / T49 | 23:00Z / 23:00-23:45Z | LESSONS H2; the final public LB snapshot (at most 1 call) | pending | `_curation/20/watch.json`; `CONTEXT.md` l.2619 |
| T11 / T163 | **29 Sep 23:59Z** (02:59 MSK 30 Sep) | Deadline. Files must FINISH scoring by then | - | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744250 |
| W19 / W73 / W102 / W93 / W165b / W261 / T196 | standing | ONE poller (header < 15 min); no resubmit of class-C or ERRORed files; SEC only as V_pub; a timeout on every Kaggle call; light polling | standing | `CONTEXT.md` l.3331-3335, l.3692-3703; `memory/feedback-kaggle-api-load.md` |

## LATER (after 29 Sep 23:59Z)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T155 + W376 + W390 + **W396** (new; = **R44-A5**) | 30 Sep **00:07Z** (03:07 MSK), timer 21232 | **POST-DEADLINE:** <br>- **(1)** `PYTHONIOENCODING=utf-8 timeout 180 python tools/uptest.py save final_0007Z`; log whether the LB is public or private. <br>- **(2)** 1 read_selected call + 1 submissions list. <br>- **(3) Stop watchdog v2 (30176/16728) FIRST** (else a false "NO CLEAN POLL" alert at ~00:32Z / 03:32 MSK), then the poller **37016** (loops forever), the old watcher 29636/30864, manual_admit 3028 (+29032/13708), waiter 9016/29828, t7 16748 (+34124/6344), reader 1364/19012; verify each by exact PID with Get-Process. <br>- **(4)** git add CONTEXT.md, poll.log, ledger.md, **`_lb/e10_20260929T1141Z/`**, `_lb/final_0007Z`, `experiments/discussions/`, **`research/wf_ideas_v4/round44/`**, `_night_subs.*` (evidence). <br>- **(5)** Commit as Vitaly Neybauer with **no Co-Authored-By** (the memory rule beats the harness reminder), then push | `round44/report.json` R44-A5 (1); `round43/report.json` R43-A8; `memory/feedback-git-no-coauthor.md` |
| **T243** (new) | post-deadline write-up | R44 rechecks, wording as corrected by the skeptics: **RC-A** CI makes same-frame node pairs < 2 um (exp87a 67 vs exp85a 17; GT 0), score identical after reverting, 102 of 104 not within 7 um of GT -> a pair-count dummy gate if CI is reused; **RC-B** exp03B "+0.0048 real gain" is within the seed spread (seed 7 -0.0025); **RC-C** dummy-lab K-base signs are 6bba reads (~96% of ~2.2k edges; 44b6 clips never moved); divset36 is 32/36 6bba and does NOT flag 44b6 | `round44/report.json` R44-A5 (3), new_facts (8), rejected |
| W372 | post-deadline, optional | RESULTS.md l.20 "keep steal off" annotation | `round40/report.json` R40-A9 |
| T216 / T223 / T229 / T233 / T236 / T240 | post-deadline | Lesson checks (I413 / I423, I419 / I420, MC П2 vs П3, audit claim, the 0.963 cluster, medal check: silver #199 in the 0.957 block, bronze #399 in the 0.955 block at 11:41Z) | `round43/report.json` new_facts (10) |
| W317 / W321 / W326 / W312 / W295 / W29 | post-deadline | Older research follow-ups | `_curation/38/watch.json` |
| T133 / T170 | 3 Oct | GPU quota refresh | `CONTEXT.md` l.4239-4241 |

**Passed or finished time-bound items:**
- **Earlier deadlines:** the R8 new-mechanism cutoff (27 Sep 12:00Z), the 28 Sep 12:00Z consolidation (superseded) and the R8 29 Sep 10:00Z edge all passed.
- **Today:**
  - the tick 12:37Z; decision B 13:34Z; round 40 applied 13:58Z; pre_exp89t killed ~14:48Z; round 41 applied 14:59Z;
  - 15:08-15:54Z network loss; round 42 lost; restart and re-arm 15:59Z (l.4668);
  - **round 43 applied 16:43Z** (l.4678, 19149bf); **slot 2 closed unused ~16:50Z** (l.4689-4690);
  - **liveness 17:13Z** (l.4695); **round 44 17:13-17:37Z** (report not yet applied);
  - **last feed run 17:29:24Z; feed loop stopped** (`feed_loop.log`; `round44/report.notes.md`).
- **Friend replies:** none awaited (`CONTEXT.md` l.2175-2176).
- **Standing notes:**
  - **T156:** 20:00 UTC = 23:00 MSK. Always write the zone.
  - **T204:** poller cadence ~602 s (step 10:02.3), not 5 min.
  - **T205:** LB `LastSubmissionDate` = the max submit time among SCORED files.

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I474** (new) | "readtime.sh l.25: DISP empty on COMPLETE -> d+0 = 0 -> T5 (skeptic gap 3) ... Caveat: at the next header awk still picks the first (scoreless) COMPLETE row -> manual path needed if HOLD repeats" | `round44/report.notes.md` | A COMPLETE row before its score lands would push a false "exp89t lost" (T5). Only the HOLD guard in W393 stops it; not yet in CONTEXT |
| **I475** (new) | "a function named msg falls through to Windows MSG.exe when undefined (Bash tool state does not persist between calls)"; "'. readtime.sh \| grep' runs in a subshell -> functions lost" | `round44/scan_hyp_ops44.notes.md` DEFECTS (1), (2) | A silent no-op or a Windows popup instead of the push at the one decisive event (W393 rules (a)) |
| **I476** (new) | "pushtext44 line 1 = 'Не смог проверить отметку финалов…', line 2 = T1 promotion text ... confirms skeptic fix (b): send all lines but CONTEXT FIRST" | `round44/report.notes.md` (dry run SELMOCK=FAIL) | "Send line 1 only" would drop the untick/tick steps on a T1/T2 read with failed SELECTED reads |
| **I477** (new) | "worst case is selread 90 s + sleep 60 s + selread 90 s + the card build, about 250 s, more than the 120 s default" | `round44/report.json` R44-A2 | A killed tool call mid-block = no push; set the Bash `timeout: 600000` |
| **I478** (new) | "read_selected.py has no timeout -> block wraps it in 'timeout 90' (a hang = failed read)" | `round44/scan_hyp_ops44.notes.md` DEFECTS (3) | A hang (not only an SSL error, I465) must count as a failed read |
| **I479** (new) | "the projected 19:05:29Z header falls in the F=2 late window, where only the UNPROVEN-ins / DIS «?» wording differs, never the pair" | `round44/report.json` R44-A2 (h) | Corrects the scan's "all outside" claim (C33); log L_hi when F >= 1 |
| **I480** (new) | "Chris Deotte (participant, '2870th in this Competition', no staff tag) ... NO HOST ANSWER on when selection locks" | `round44/scan_plancheck.notes.md` 17:14:59Z | Curation 43 mislabelled it as a host statement (C34); do not cite it to the user as official |
| **I481** (new) | "Chrome MCP: the tab group was removed once during the scan and a stray Overview tab appeared and vanished; another client may share the Chrome MCP session"; "tab 1196280440 in the group belongs to another agent, not touched" | `round44/report.json` new_facts (9); `round44/scan_plancheck.notes.md` 17:17:53Z | Do not rely on an MCP tab persisting for any post-deadline Chrome read (T49) |
| **I482** (new) | "stopping the poller before watchdog v2 triggers a false alert at ~00:32Z" | `round44/report.json` plan_issues (6), R44-A5 (1) | A 03:32 MSK false alarm to the user; stop order in W396 |
| **I483** (new) | "the B31 premise ('3 um NMS excludes near pairs') is FALSE on x138/CI outputs (same-frame NN < 1/2/3 um: exp56 2/18/58, exp85a 6/34/100, exp87a 24/134/210), but the score is identical after reverting them" | `round44/report.json` new_facts (8) | A structural CI artefact (GT has 0 such pairs) that only matters for the write-up / reuse (T243) |
| **I484** (new) | "LB rows 4 005; Overview 17:17:53Z: 4 003 teams"; movers "Sam Barnett 0.963->0.969 (#25)", "slime 0.970->0.971 (#9)"; "None of them disclosed anything" | `round44/report.json` new_facts (1); `round44/scan_browser.notes.md` | Denominator for the card (C32); the 0.963 cluster (T236) keeps moving with no public pipeline |
| I471 (open) | "during a real outage this session is offline too ... the user's own «2 of 2 selected» check before 23:00 MSK remains the last line of defence." | `round43/report.json` plan_issues (11) | Say it with any read push before 20:00Z |
| I461 (**extended**) | Test runs leave ready-looking cards: round 44 wrote `r44dry/card_1837_*.txt` ("two were rewritten during the skeptic check"), "never evidence" | `round44/report.json` R44-A2 (i) | At 18:37Z build fresh; no `<SP>/card_1837_*.txt` exists (`round44/report.notes.md`) |
| I452 (open) | "exp87a unrounded ... ~0.95875 -> exp89t needs DIS_pub >= ~+0.00075 ... to display 0.960" | `round41/scan_recheck.notes.md` | **T3KEEP is the most likely read** |
| I448 (open) | `_lb/e10_20260929T1141Z/lb.csv` is still **untracked** | `git status` (this session) | The only S0 and the card's default `--lb` (C31). Commit it at 00:07Z (W396) |
| I410 / I411 (open) | read_selected.py, t7_trigger.sh, manual_admit.sh, mk_card_1837.py and now **`r44dry/readtime.sh`, `msg44.py`, `cardfix44.py`** live **only in the session scratchpad** | `CONTEXT.md` l.4657-4677; `round44/report.notes.md` | After a restart, re-arm from CONTEXT l.4643-4697 and `round44/report.json`; check the sha8s (befef6fb, 233e5ba5, af903431, a19e1bd6) |
| I462-I467 | Blind watchdog, orphan outputs, lastok skipping data-carrying error blocks, read_selected without retry, missing 'ins-tail?' footnote, stop-job self-count | `round43/*` | **Resolved or logged** by R43-A1..A6 (`CONTEXT.md` l.4678-4697) |
| I468 / I470 / I472 / I473 | Medal blocks; CI cost and exp11 scope; wording rules ("closed unused"); network loss on battery | `round43/report.json` | Post-deadline lessons (T240) and answer wording (W382) |
| I469 | 744250 lock-time question | `round43/report.json` new_facts (2) | Updated by I480 / C34 |
| I424 / I420 / I423 | "#38 лучше #37 только если ... (P ~0.1–0.2)"; the lab CI sign was wrong; the public division evidence is 1-2 fork events | `round38/report.json` | Post-deadline lessons (T216 / T223) |
| I430-I461 and older | Resolved, in CONTEXT, or moot | `_curation/43/watch.json` ... `_curation/27/watch.json` | - |
