# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-29 ~11:40 UTC (14:40 MSK), curation 39. This updates the curation-38 build of ~10:45Z, which is committed in 75f0efe with a structured copy in `research/KNOWLEDGE/_curation/38/watch.json`. Older predecessors run from `_curation/37/watch.json` down to `_curation/18/watch.json`. Rows not repeated here are unchanged there.

**Sources read for this update:**
- **`CONTEXT.md`:** 4,560 lines; `## 9. Literature` starts at l.4540. Two new entries since curation 38:
  - l.4509-4537 (**10:54Z, ROUND 38 APPLIED**, R38-A1, A2, A4-A7; A3 conditional). Card v3 = `scratchpad/card_fill_1203_v3.txt` sha8 **ae03f566** (A1). The R37-A6 addendum and the E10-after-11:30Z policy are written (A2, l.4516-4526). pre_exp89t is re-armed (A4, l.4527-4529). The exp89t read playbook is pre-registered (A5, l.4529-4535). manual_admit is armed (A6, l.4535-4537). KEY FACTS are refreshed (A7, l.4537);
  - l.4538-4539 (**11:10Z**): the timer logged "A-M2 UNUSED ... No submit". Round 39 was launched.
- **`git log`:** 75f0efe (round 38 applied; commits round38/, `_curation/38`, e10 1013Z/1041Z). **`git status`:**
  - `M CONTEXT.md` (the 11:10Z entry);
  - `?? research/wf_ideas_v4/round39/`;
  - `?? experiments/e10_watch/20260929T1110Z.txt`;
  - `?? experiments/discussions/digest_20260929T1128Z.md`.
- **`research/wf_ideas_v4/round39/`** (untracked, 11:10-11:33Z):
  - `report.json` with **R39-A1..A9**, new_facts (1)-(6), plan_issues (1)-(8) and rejected;
  - all the `scan_*` and `v_*` notes.
  - **REPORT.md is missing** again because the harness blocked the write (`round39/report.notes.md` 11:33Z). Only `round36/REPORT.md` exists among rounds 29-39.
- **`experiments/lb_poll/poll.log`:** newest header **11:28:55Z** (l.30698). exp89t 56669888 is **PENDING** (l.30701).
- **Loops:**
  - `experiments/e10_watch/watch_loop.log`: **RUN 46 ran at 10:42:07Z** (CHANGES=4, 8/8 OK). RUN 47 is due 11:41:53Z. The loop ends at 12:00Z.
  - `experiments/discussions/feed_loop.log`: **11:28:49Z**, 0 new topics, 1 new comment, E10 FLAG none. The next run is ~12:58Z.
- **Rank:** **#141** of 3,992, 0.959, count 56, **17th of 22** in the 0.959 block (ranks 125-146). The block grew from 21 to 22 when Manish joined below us at #142 (`round39/report.json` new_facts (2)).
- **`grep -c` on CONTEXT.md:**
  - "count jump" 1, "RECOMMENDED PAIR" 1, "manual-admit" 1, "E10 AFTER" 1 (all from R38 applied);
  - 0 hits: "COMPARATOR", "t7_trigger", "mk_card_1837", "slot 2 decision", "08:27Z";
  - `experiments/RESULTS.md` probe rows still end at probe 46 (l.79).
- **Round prompt:** `experiments/workflows/biohub-research-round.js` still says:
  - l.20: "ties broken by the EARLIER submission";
  - l.37: the browser agent "FIRST run `python tools/e10_snapshot.py`" (8 Kaggle calls).
- **Processes** at 11:30Z (`round39/scan_plancheck.notes.md`; `round39/report.json` new_facts (6)):
  - pre_exp89t.sh 36816; manual_admit.sh 3028; the exp89t watcher 30864; the poller 37016; the watchdog 22236 (one-shot); the E10-signal watcher 20284; the feed-signal watcher 24728; the e10 loop 18040 (ends 12:00Z);
  - timers: 11:45Z, 11:50Z, 12:03Z, hourly 13:13-18:13Z, 18:37Z, 19:43Z, 21:05Z, 00:07Z. The old jobs 18408, 35124 and 17304 are gone.

All times are UTC. The user thinks in MSK = UTC+3 (`CONTEXT.md` l.3683-3687). IDs are stable: W = action, T = time-bound reminder, I = insight, C = contradiction. Status values: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at ~11:40Z, 29 Sep:**
- **Best display 0.959**, exp87a 56640366 (probe 51; CI). V_pub = exp87a.
- **Only PENDING file:** exp89t 56669888 (T0 09:00:17Z). Edges:
  - early read ~17:53Z; typical read ~18:00-18:30Z;
  - 10.2 h = **19:12:17Z** (22:12 MSK); admit edge **19:45:17Z** (22:45 MSK);
  - the first poller header after 19:12:17Z is expected ~19:20:30Z (`round39/report.json` new_facts (6)).
- **Slots:** 1 left today. **Default UNUSED at 12:00Z.** Round 39 found no candidate (`round39/report.json` R39-A1).
- **SELECTED** is presumably still {#37 56563521, #38 56563534}, the weaker pair: ~0.49 bronze / ~0.11 silver in every MC run (`round39/report.json` new_facts (4)).

**Changes since ~10:45Z (curation 38):**
- **Done:**
  - **W347** (a)-(e): CONTEXT l.4516-4526. Only the slot-2 line remains, now **W354**;
  - **W349**: re-armed, l.4527-4529, pid 36816;
  - **W350**: playbook, l.4529-4535;
  - **W351**: manual-admit armed, l.4535-4537, pid 3028;
  - **W352**: KEY FACTS, l.4537;
  - **W353**: the round-38 commit is in 75f0efe. The REPORT.md renders are still missing and move to **W363**;
  - **C2**: the 11:10Z timer logged "A-M2 UNUSED", l.4538;
  - **C10 / C12 / C13** resolved;
  - **T207** RUN 46 at 10:42:07Z;
  - **T100** feed run at 11:28:49Z (null);
  - **T210** passed with a null result.
- **In progress:** **W346**, card v3 ae03f566. It was built; it gets filled and sent at 12:03Z.
- **New:**
  - actions **W354-W363** (= R39-A1..A9 plus the round-39 commit);
  - reminders **T224-T228**;
  - contradictions **C14-C16**;
  - insights **I430-I439**.
- **Corrected:** **I428**. Round 39 refuted the "earlier timestamp" reading of Fanch's position (C16).

---

## OVERDUE / DUE NOW

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W355** (new; = **R39-A2**) | **S0 fallback and card rank fields.** <br>- **11:45Z:** run `python <scratchpad>/mk_s0.py 20260929T1141Z`. <br>- **Fall back to `20260929T1110Z`** if the script raises StopIteration (no leaderboard_rows), the 1141Z file is missing, or our count is not 56. <br>- Log which tag is the S0. <br>- **Card l.8:** position = rank - rows > 0.959; block = rows == 0.959, now **22** (not 21). <br>- **Never** copy the R38 "Fanch ... earlier timestamp" sentence | armed (timer 11:45Z) | **11:45Z** (14:45 MSK) | `round39/report.json` R39-A2, plan_issues (6); `round39/scan_plancheck.notes.md` |
| **W354** (new; = **R39-A1**; absorbs **T209 / W342**) | **Close slot 2.** <br>- **11:50Z message:** the default is UNUSED. The inputs were already checked: feed 1128Z null; 738833 Luna-Xavier has no knob or values; glance once at the 1141Z e10 file. Do not cite R39S-4 as the reason. <br>- **12:00Z CONTEXT line:** "slot 2 decision = UNUSED (rule (a) failed: exp89r 0.957 < 0.958; no E10 >= 0.960 ...; a non-CI file had to be sent by ~12:33-12:43Z ...)". The slot stays formally open via R38-A2 (d). R38-A3 (the mid_<token> save) applies to **any** slot-2 submit before 12:43Z. <br>- **exp86c line only if asked.** <br>- **Build nothing, submit nothing** | timer 11:50Z (pid 21496) armed; log not written (`grep -c "slot 2 decision"` = 0) | **11:50Z / 12:00Z** (14:50 / 15:00 MSK) | `round39/report.json` R39-A1; `CONTEXT.md` l.4500-4501, l.4538 |
| **W346** (updated) | **Card v3 ae03f566** (built at 10:54Z). At 12:03Z fill: <br>- the header (newest non-error poll header, MSK first); <br>- SELECTED (1 read-only call); <br>- rank and block from the **W355 S0 (17 of 22 if unchanged)**; <br>- the l.40 SEC slot-2 clause from the W354 log. <br>Then send it. The 12:03Z timer (pid 33456) still names round27 v4: it is a pointer, so send v3. **Never tick.** This card is also the 12:00Z finals-tick reminder | in progress | **12:03Z** (15:03 MSK) | `CONTEXT.md` l.4511-4516, l.4521; `round39/scan_plancheck.notes.md` |
| **W359** (new; = **R39-A6**) + C14 | **Round prompt from round 40 on.** <br>- **(1)** Browser agent: Chrome only, **no `tools/e10_snapshot.py` after 12:00Z** (8 calls/run). A genuine > 0.959 biohub notebook gets 1 scoped list call by the main session, then a push. <br>- **(2)** 17:30-20:00Z: agents make 0 Kaggle calls. <br>- **(3)** Keep the hourly rounds (the user asked, CONTEXT 02:53Z (3), l.4294). The 18:13Z round uses a READS-vs-CARD lens. <br>- **(4)** KEY FACTS: in-block order = unrounded score; add "slot 2 = UNUSED" and "SELECTED comparator = R39-A4" | not started (`biohub-research-round.js` l.20, l.37 unchanged) | **before 13:13Z** (16:13 MSK) | `round39/report.json` R39-A6, plan_issues (3), (7) |
| **W363** (new; supersedes the W353 remainder) | **Commit round 39**, `e10_watch/20260929T1110Z.txt`, `digest_20260929T1128Z.md` and the 11:10Z CONTEXT entry, using named paths, as the user, with **no Co-Authored-By**. Render `round37`/`round38`/`round39` REPORT.md from report.json (the Russian text is in the report agent's final message). Rounds 29-35 also lack REPORT.md | not started | with the 12:00Z CONTEXT commit | `git status`; `round39/report.notes.md` 11:33Z; `memory/feedback-git-no-coauthor.md` |
| W126 (part 2) | Add RESULTS.md rows for probes 47-54: <br>- 47: 0.955; 48: 0.957; 49: 0.955; 50: exp85a 0.958; <br>- 51: exp87a 0.959; 52: exp89r 0.957; 53: exp75 0.955; 54: exp89p 0.956. <br>Then probe 55 (exp89t) when it reads | **overdue** (rows end at 46, l.79) | low; post-deadline OK | `experiments/RESULTS.md` l.79 |
| W336 | One line saying that the user's 08:27Z / 08:28Z instructions override R8's 10:00Z edge (l.1671) | not started (`grep -c 08:27Z` = 0). Mostly moot: the E10-after-11:30Z policy (l.4521-4524) covers the live case | low | `CONTEXT.md` l.1671, l.4521-4524 |
| W286 / W297 / W202 + W244 / W176 / W177 / W182 / I208 / W57 / W66 / W31 / W72 / W150 / W308 | Older text and cleanup items | overdue, low | H2 29 Sep 23:00Z; post-deadline OK | `_curation/36/watch.json`, `_curation/26/watch.json` |

## CONTRADICTIONS TO RESOLVE BEFORE THEY FIRE

| ID | Conflict | Which text wins | Evidence |
|---|---|---|---|
| **C14** (new) | The round-prompt KEY FACTS (`biohub-research-round.js` l.20) say "ties broken by the EARLIER submission". **Observed:** Fanch's 03:20:41Z file ranks #139 above our older exp87a, and Manish's 04:13:52Z file ranks #142 below it. So order inside a display block is the unrounded score; time breaks only byte-copy ties | **Unrounded order** (v4 FINAL_REPORT §2; R39-RC-C). Fix with W359 (4) before 13:13Z | `round39/scan_recheck.notes.md` 11:21Z; `round39/report.json` new_facts (3) |
| **C15** (new) | The **18:37Z / 19:43Z / 21:05Z timer texts** push "if not the recommended pair". **Card v3 l.50** says "если отмечено не то, что вы выбрали", and П2 {V_pub, exp75} is an allowed trade (28 Sep 16:32Z plan). The timers would push a deliberate П2 back to П3 | **The R39-A4 comparator** (W357). Treat the timer texts as pointers to it | `round39/report.json` R39-A4, plan_issues (2) |
| **C16** (new) | R38 new_facts (2) / curation-38 **I428**: "Fanch ... entered at #139 above us" (read as the earlier timestamp winning). R39-RC-C: this is a misattribution | **R39-RC-C.** Never put the Fanch sentence in the card or a message (W355). It never reached CONTEXT or card v3 | `round39/report.json` R39-A2, new_facts (3) |
| C11 (updated) | R37-A3 "56 -> 58 = MASKED" vs R26-A4 (b) | **R26-A4 (b)** via R38-A3. R39-A1 (2) extends A3 to any slot-2 submit before 12:43Z; after that it is void | `round39/report.json` R39-A1 (2), plan_issues (8) |
| C7 (updated) | The 12:03Z timer (pid 33456) names round27 v4 | Pointer: send **v3 ae03f566** | `CONTEXT.md` l.4521 |
| C8 | Card step 9 window vs the observed CI L from 8.88 h | Card v3 l.48 now says ~20:55-21:30 MSK. Watch from ~17:50Z | `round39/scan_plancheck.notes.md` |
| C9 / C5 / C6 | C9: pre-registered П3 first vs the MC favouring П2. C5: the SEC clause. C6: the R8 10:00Z edge | C9: the pre-registered order stands (R39-A9 is only a reply if asked). C5: set by the W354 log. C6: the user's instructions (W336) | `CONTEXT.md` l.4476-4478; `round39/report.json` R39-A9 |

## NEXT 24 H (29 Sep ~11:40Z -> 23:59Z)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| T207 | **11:41:53Z** RUN 47; loop END **12:00Z** | The last e10 snapshot. It is the primary S0 fallback (W355). After 12:00Z there are no e10 snapshots | due | `experiments/e10_watch/watch_loop.log` (RUN 46 10:42:07Z) |
| W355 | **11:45Z** | The S0 build with a named fallback | armed | see OVERDUE |
| W354 | **11:50Z / 12:00Z** | Slot-2 message and UNUSED log | armed | see OVERDUE |
| W346 | **12:03Z** (15:03 MSK) | Card v3 = the finals-tick reminder | in progress | see OVERDUE |
| **W356** (new; = **R39-A3**) | **arm now**, at the latest **18:13Z**; fires ~**19:20Z** (22:20 MSK) | **T7 trigger.** Arm `scratchpad/t7_trigger.sh` with run_in_background (0 Kaggle calls). It waits for the first non-error poll.log header >= 19:12:17Z and then prints the exp89t status. **If PENDING:** make 1 SELECTED call, then send the R38-A5 (6) T7 text for case (a)/(b)/(c)/(d). Log "T7 trigger armed ..." in CONTEXT | not started (`grep -c t7_trigger` = 0; no 19:1x job in the process table) | `round39/report.json` R39-A3, plan_issues (1) |
| **W357** (new; = **R39-A4**) | log with W356, **before 18:37Z** | **SELECTED CHECK COMPARATOR.** No push iff SELECTED = {V_pub, #37} (П3) or {V_pub, exp75 56656157} (П2), or else the pair the user named in chat. Otherwise push the untick/tick steps | not started (`grep -c COMPARATOR` = 0) | `round39/report.json` R39-A4; C15 |
| **W358** (new; = **R39-A5**) | log **before 17:40Z** (20:40 MSK) | **pre_exp89t S0 validity guard.** The save is valid only if our row shows count **56** and LastSubmissionDate **2026-09-29 00:46:36**. Otherwise use the e10 fallback S0 flagged stale and say so in the T3 log. Apply it by hand; no script change | not started | `round39/report.json` R39-A5, plan_issues (5) |
| **W360** (new; = **R39-A7**) | build and dry-run **before 17:40Z**; used **18:37Z** | **`scratchpad/mk_card_1837.py`** from the filled card v3 (0 calls): variants PENDING / T1..T6. Handles the l.3 time, the l.48 PENDING text ("ещё считается на 21:37 МСК ..."), the R38-A5 (1) edits on T1/T3 and the rank label "(ЛБ 20:40 МСК)". Keep the token asserts. Log the sha8s | not started (`grep -c mk_card_1837` = 0) | `round39/report.json` R39-A7, plan_issues (4) |
| T219 → **T224** (new) | **13:13, 14:13, 15:13, 16:13Z** rounds 40-43 | Apply W359 first. Chrome-only scan with 0 API calls; build W360; no builds or slot work | pending | `round39/report.json` next_focus |
| T100 | feed **~12:58Z**, then ~14:28, 15:58, 17:28, 18:58, 20:28, 21:58, 23:28Z | E10 v3 trigger >= 0.960. It is the only automatic watcher after 12:00Z and is not scoped to this competition. For any flag: 1 scoped list call, then push. **No copy or submit** without the user's explicit yes | live | `experiments/discussions/feed_loop.log`; `CONTEXT.md` l.4521-4524 |
| **T225** (new) + **W361** (= **R39-A8**) | **17:13Z** round (20:13 MSK); re-arm on any alert | **Liveness check** of the watchdog 22236 (one-shot: it stops after the first alert), pre_exp89t 36816, manual_admit 3028, the exp89t watcher 30864, the T7 trigger and the poller 37016. Confirm that A3/A4/A5/A7 are logged | pending | `round39/report.json` R39-A8, plan_issues (6) |
| T213 | all afternoon and evening | Laptop on AC with the lid open (AC, 78% at 11:30Z). Network was lost on battery 28 Sep 15:00-15:40Z and 29 Sep 05:30-05:57Z | watch | `round39/scan_plancheck.notes.md`; `round39/report.json` R39-A8 why |
| T214 | **17:40Z** (20:40 MSK) | pre_exp89t save (pid 36816, reads the newest non-error block; 1 retry). **Apply the W358 guard** to its output | armed | `CONTEXT.md` l.4527-4529 |
| T208 + W344 | **~17:53Z** early; typical **18:00-18:30Z**; **19:12:17Z**; **19:45:17Z** | **exp89t read**, coded T1-T8 per the pre-registered playbook (`CONTEXT.md` l.4529-4535): <br>- 1 SELECTED call before each message; <br>- after a promotion, first append "RECOMMENDED PAIR = П3 {exp89t 56669888, #37 56563521}"; <br>- push the user in MSK at once on any V_pub change | pending | `CONTEXT.md` l.4529-4535 |
| **T226** (new) | **18:13Z** round (21:13 MSK) | READS-vs-CARD round from local files only (poll.log, the pre_/post_exp89t saves, card v3, T-codes). **Do not skip it** | pending | `round39/report.json` R39-A6 (3) |
| T152 | **18:37Z** (21:37 MSK), timer pid 33156 | FINAL card via `mk_card_1837.py` (W360). Compare SELECTED with the **W357 comparator**, not the literal "recommended pair" | pending | `round39/report.json` R39-A4, R39-A7 |
| **T227** (new) = T220 | **~19:20:30Z** (22:20 MSK), the first header >= 19:12:17Z | The T7 trigger fires (W356). If exp89t is PENDING, send the T7 text for the SELECTED case. It gives the user ~40 min instead of 17 | pending (the trigger is not armed yet) | `round39/report.json` R39-A3 |
| T161 + T221 | **19:43Z** timer (pid 30648); **19:44:45Z** manual-admit (pid 3028) | Notify-only V_pub re-check (W357 comparator), then the single-attempt manual list. If exp89t is not terminal after it, push the T8 '?' line | pending | `CONTEXT.md` l.4535-4537 |
| T10 | **20:00Z (23:00 MSK)** | **The user ticks the finals.** The session never ticks. If the user does nothing, {#37, #38} stay (~0.49 bronze / ~0.11 silver) | pending | `CONTEXT.md` l.3844-3855; `round39/report.json` new_facts (4) |
| T222 | after 20:00Z until 23:59Z | E10 or exp89t information after the tick: re-selection is allowed until 02:59 MSK. No copy or submit without the user's explicit yes | pending | `CONTEXT.md` l.4521-4524 |
| T153 / T162 | ~20:00-20:30Z; **21:05Z** timer (pid 31720) | Verify SELECTED against the **W357 comparator**; last-call notify on a mismatch | pending | `CONTEXT.md` l.4092, l.4099; `round39/report.json` R39-A4 |
| W362 (new; = **R39-A9**) | only if asked, before 20:00Z | The corrected cap-6 partner line: bronze cap 4 > cap 6; silver exp85a > #37 12/12 but exp75 > exp85a 10/12. **Never** say "cap 4 выше в 12 из 12 при любом априоре" | conditional | `round39/report.json` R39-A9, rejected |
| W177 H2 / T49 | 23:00Z / 23:00-23:45Z | LESSONS H2; the final public LB snapshot. It is not an e10 run: at most 1 call | pending | `_curation/20/watch.json`; `CONTEXT.md` l.2619 |
| T11 / T163 | **29 Sep 23:59Z** (02:59 MSK 30 Sep) | Deadline. Slot 2 expires unused. No slot reset before it | - | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/overview |
| W19 / W73 / W102 / W93 / W165b / W261 / T196 + **T228** (new) | standing | Standing rules: <br>- ONE poller; the header must be < 15 min old; <br>- never resubmit class-C or ERRORed files; <br>- SEC final only as V_pub; <br>- a timeout on every Kaggle call; <br>- light polling. **T228:** 17:30-20:00Z, only the poller, pre_exp89t, the watcher save, manual_admit and the registered SELECTED reads call Kaggle | standing | `CONTEXT.md` l.3331-3335, l.3692-3703; `memory/feedback-kaggle-api-load.md`; `round39/report.json` R39-A6 (2) |

## LATER (after 29 Sep 23:59Z)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T155 | 30 Sep 00:07Z, timer | POST-DEADLINE job: private read v2 + L1-L7 | `CONTEXT.md` l.3714-3715 |
| T216 / T223 | post-deadline | Lesson checks: Satwik's "few public divisions" (I413, I423); the lab sign record on CI and DIS (I419, I420) | `_curation/38/watch.json` |
| **T229** (new) | post-deadline | Lesson check: the R39-RC-B C-prior MC predicted П2 >= П3 on silver 12/12. Compare with the private exp75 vs #37 once private scores are visible | `round39/report.json` new_facts (4) |
| W317 / W321 / W326 / W312 / W295 / W29 | post-deadline | Older research follow-ups; a kaggle_feed.py plausibility filter (I429) | `_curation/38/watch.json` |
| T133 / T170 | 3 Oct | GPU quota refresh | `CONTEXT.md` l.4239-4241 |

**Passed or finished time-bound items:**
- **Earlier deadlines:**
  - the R8 new-mechanism cutoff (27 Sep 12:00Z) passed;
  - the 28 Sep 12:00Z consolidation was superseded;
  - the R8 29 Sep 10:00Z edge passed.
- **Today:**
  - round 38 applied 10:54Z;
  - timer 11:10Z logged (l.4538);
  - the last slot-2 sighting moment (T210, ~11:15Z) passed with a null result;
  - feed 11:28Z null;
  - round 39 report at 11:33Z.
- **Friend replies:** none awaited (`CONTEXT.md` l.2175-2176).
- **Standing notes:**
  - **T156:** 20:00 UTC = 23:00 MSK. Always write the zone.
  - **T204:** poller cadence 601-603 s.
  - **T205:** LB `LastSubmissionDate` = the max submit time among SCORED files.

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I430** (new) | "Fanch sub #58 submitted 2026-09-29 03:20:41 -> 0.959 ... ranks 139 ABOVE us ... our 0.959 file exp87a submitted 28 Sep 12:14:57, 15 h earlier ... Manish sub #18 04:13:52 -> 0.959 ranks 142 BELOW us ... unrounded ordering confirmed" | `round39/scan_recheck.notes.md` 11:21Z | It kills the "EARLIER submission" tie folklore still in the round prompt (C14). Any 0.959 file that ties us on display can rank either side of us. I-542 (re-submit for tie order) stays refuted. |
| **I431** (new) | "mk_s0.py has no try/except around the leaderboard_rows lookup; the e10 loop LB fetch can fail (RUN 41 05:41Z)" | `round39/report.json` R39-A2 why | Without the named 1110Z fallback, the exp89t UP test could start with no count-56 S0. The fallback is lost for good after the 12:00Z loop end. |
| **I432** (new) | "watchdog 22236 'break's on the first ON-BATTERY or POLL-STALE alert" | `round39/scan_plancheck.notes.md` 11:30Z; `round39/report.json` R39-A8 | After one transient alert, the whole 17:40-19:50Z chain runs unwatched. Re-arm after every alert. |
| **I433** (new) | "exp89t watcher (win 30864; uses last() incl. error blocks; post_exp89t only on COMPLETE 0.959)" | `round39/scan_plancheck.notes.md` | This is the same error-block pattern that R38-A4 fixed for pre_exp89t, and no round fixed it for the watcher. An error block at read time may delay or skip the watcher's reaction. Read poll.log by hand at each header after ~17:50Z rather than trusting the watcher alone. |
| **I434** (new) | "If exp89t completes in the ~10 min between the poller header and the 17:40Z save (L 8.66 h; P ~1-3%) the S0 already contains it -> count check S0 -> S1 reads +0 -> spurious lag re-save -> BLIND with k = 0; a genuine UP is lost" | `round39/report.json` R39-A5 why | This is why W358 exists. It is a hand check, so it is easy to forget at 17:40Z. |
| **I435** (new) | "tools/e10_snapshot.py = 8 CLI calls per run (5 kernel lists, 2 statuses, 1 LB download)" and the round prompt tells the browser agent to run it FIRST | `round39/scan_plancheck.notes.md`; `biohub-research-round.js` l.37 | Five more rounds would make ~40 calls that overlap the single-attempt 19:44:45Z manual-admit, and the user reported a ban on 28 Sep. W359 must land before 13:13Z. |
| **I436** (new) | "{#37,#38} ticked: bronze 0.487-0.488 silver 0.106-0.110 in all runs"; "P2 >= P3 on silver 12/12 ... bronze within 0.011" | `round39/scan_recheck.notes.md` 11:20Z; `round39/report.json` new_facts (4) | Leaving the default tick costs roughly 0.25 bronze probability, so the card's "отметьте сейчас" line matters more than the П2/П3 choice. The П2 edge is judgmental (mc26 on one embryo) and does not change the card (rejected list). |
| **I437** (new) | "non-CI safetail L (7.03, 7.19] h -> latest submit reading by 19:45:17Z = 12:33:53Z; CI -> latest 10:15-10:52Z = already passed. New build ... ~35-45 min" | `round39/scan_hyp_slot2last39.notes.md` 11:14Z | This is the arithmetic behind "slot 2 is dead after ~12:43Z". If the user asks at 13:00Z+ to "try one more thing", the answer is that it cannot read before the tick (T222 path only). |
| **I438** (new) | "Luna-Xavier (738833, 10:51Z): nuclear marker H2A.F/Z-mCherry only? same for 44b6/6bba/test? rescaled/normalised/deconvolved/fused/bleach-corrected?" with no host answer | `round39/report.json` new_facts (1); `experiments/discussions/digest_20260929T1128Z.md` | Info only: x138 preprocessing is fixed. A host answer claiming different test preprocessing would matter for the post-deadline lessons, not for tonight. |
| **I439** (new) | "exp86c ... dummy lab -0.0001 vs exp85a with identical TP/FP/FN (2049/99/78) ... only live branch would swap the CI V_pub for a non-CI public-fit file" | `round39/scan_recheck.notes.md` 11:19Z | The canned reply if the user asks "why not READMIT 0.92" (R39-A1 (3)). Do not quote "-0.0005" (rejected as unsourced). |
| I428 (**corrected**) | Fanch entered the 0.959 block at #139 above us. **Not because of an earlier timestamp** (C16): the order is by unrounded score | `round39/report.json` new_facts (3) | The card rank line must not explain a block position by time. |
| I427 | "No CI file ever > 9.5 h" | `round38/v_hyp_exp89tread38_r38t-h1.notes.md` | exp89t still PENDING at ~18:40Z is anomalous; the T7 trigger (W356) covers 19:12Z. |
| I426 | The weaker {#37, #38} is ticked | `round38/report.json` R38-A1 | Addressed by card v3 section 5. The 12:03Z send is still pending. |
| I424 | "#38 лучше #37 только если сама базовая вставка делений вредит на привате (P ~0.1–0.2)" | `round38/report.json` new_facts (6) | Still not in CONTEXT. Keep it ready for chat. |
| I423 / I420 | Public division evidence = 1-2 fork events; lab CI sign wrong (-0.00509 vs three public +0.001) | `round38/scan_recheck.notes.md`; `round38/v_recheck_r38-rc-a-...notes.md` | I419 reached CONTEXT (l.4524-4526). **I420 and I423 are still not in CONTEXT** (post-deadline lessons T216 / T223). |
| I422 | "timer.sh ... only prints a message; its notification is queued until the session is free" | `round38/v_hyp_exp89tread38_r38t-h1.notes.md` | W356 follows it: t7_trigger.sh runs with run_in_background so its exit wakes the session. The 18:37Z, 19:43Z and 21:05Z timers are still plain timers. |
| I410 / I411 | `mk_s0.py`, `mk_card_v3.py`, `card_fill_1203_v3.txt`, `pre_exp89t.sh`, `manual_admit.sh`, `lastok.sh` and soon `t7_trigger.sh` / `mk_card_1837.py` live **only in the session scratchpad** | `round39/report.json` R39-A3, R39-A7; `CONTEXT.md` l.4511, l.4527, l.4535 | If the session restarts, all armed jobs die. After a restart, re-arm from the CONTEXT l.4509-4537 text and the round39 R39-A3 script body. |
| I419, I421, I425, I429, I409, I413, I416, I417/I418, I412/I414/I415/I402/I403 and older | Unchanged or now in CONTEXT (I409 → l.4517-4518; I413 → l.4519; I419 → l.4524-4526; I429 → l.4521-4524) | `_curation/38/watch.json` ... `_curation/27/watch.json` | - |
