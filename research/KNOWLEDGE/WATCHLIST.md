# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-29 ~10:45 UTC (13:45 MSK), curation 38. This updates the curation-37 build of ~09:45Z, which is committed in 66f1eeb with a structured copy in `research/KNOWLEDGE/_curation/37/watch.json`. Older predecessors run from `_curation/36/watch.json` down to `_curation/18/watch.json`. Rows not repeated here are unchanged there.

**Sources read for this update:**
- **`CONTEXT.md`:** 4,529 lines; `## 9. Literature` starts at l.4509. Two new entries since curation 37:
  - l.4488-4501 (**09:57Z, ROUND 37 APPLIED (R37-A1..A5)**). A1 says the user was told at 09:19Z; A2 turns the 11:10Z and 12:03Z timer texts into pointers; A3 sets the S0 plan (17:40Z pre_exp89t job plus an 11:45Z e10 fallback); A4 covers the 12:03Z card edits; A5 covers the 11:50Z slot-2 step, with UNUSED as the 12:00Z default;
  - l.4502-4508 (**10:00Z, FEED E10 FLAG = FALSE POSITIVE**): the 0.9812 notebook by beraterolelk belongs to another competition. `KERNEL_TITLE_EXCLUDE` now includes 'stacking'. The best genuine public notebook is still 0.953.
- **`git log`:** 66f1eeb (round 37 applied, which also committed the round37 folder and curation 37), 135788c (feed fix). **`git status`:**
  - `?? research/wf_ideas_v4/round38/`
  - `?? experiments/e10_watch/20260929T1013Z.txt`
  - `?? experiments/lb_poll/_night_subs.csv/.err`
  - `M experiments/lb_poll/ledger.md, poll.log`
- **`research/wf_ideas_v4/round38/`** (untracked, 10:13-10:38Z):
  - `report.json` with **R38-A1..A7**, new_facts (1)-(7), plan_issues (1)-(11) and rejected;
  - `report.notes.md` and all the `scan_*` and `v_*` notes.
  - **REPORT.md is missing again.** The harness blocked the write, so the main session has to render it from report.json (`round38/report.notes.md` 10:38:56Z).
- **`experiments/lb_poll/poll.log`:** the newest header is **10:38:44Z** (l.30393). exp89t 56669888 is still PENDING. The cadence is ~602 s (`round38/v_hyp_exp89tread38_r38t-h1.notes.md`).
- **Loops:**
  - `experiments/e10_watch/watch_loop.log`: the last line is RUN 45 at 09:42:06Z. **RUN 46 is due at 10:41:53Z** and was not logged at 10:41Z. A manual e10 snapshot `20260929T1013Z.txt` (round 38 P1) exists.
  - `experiments/discussions/feed_loop.log`: 09:58:41Z (the FP flag); the next run is ~11:28Z.
- **Rank:** **#141** of 3,991, 0.959, count 56, **17th of 21** in the 0.959 block (ranks 125-145). Fanch joined the block above us (`round38/scan_browser.notes.md`; `round38/report.json` new_facts (2)).
- **`grep -c` on CONTEXT.md:**
  - 0 hits: "count jump", fill_1837, "manual-admit", "RECOMMENDED PAIR", card_fill_1203_v3, "E10 AFTER";
  - Satwik 1 hit, only the "optional Satwik line" pointer at l.4500;
  - `experiments/RESULTS.md` probe rows still end at probe 46 (l.79).
- **Processes** at 10:34Z (`round38/report.notes.md`):
  - timers: 17304 (11:10Z, stale M2 text), 33456 (12:03Z, card v4 text), 24636 (11:45Z S0 build), 21496 (11:50Z slot 2), 33156 (18:37Z), 30648 (19:43Z), 31720 (21:05Z), 19388 (00:07Z);
  - jobs: 18408 (17:40Z pre_exp89t), 29636 (exp89t watcher);
  - loops: e10 loop pid 18040 (END 12:00Z), feed loop (sleep 5400).

All times are UTC. The user thinks in MSK = UTC+3 (`CONTEXT.md` l.3683-3687). IDs are stable: W = action, T = time-bound reminder, I = insight, C = contradiction. Status values: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at ~10:45Z, 29 Sep:**
- **Best display 0.959**, exp87a 56640366 (probe 51; CI). V_pub = exp87a (`CONTEXT.md` l.4485-4487).
- **Rank #141** (10:14Z). Medal lines: silver #200 (0.957 block), bronze #399 (0.955 block) (`round37/report.json` new_facts).
- **Only PENDING file:** exp89t 56669888 (T0 09:00:17Z). Early edge ~17:53Z; typical read ~18:00-18:30Z; 10.2 h edge 19:12:17Z; admit edge 19:45:17Z (`round38/scan_hyp_exp89tread38.notes.md`).
- **Slots:** 4 used today, **1 left**. The 12:00Z default is **UNUSED** (`CONTEXT.md` l.4500-4501).
- **SELECTED** is presumably still {#37 56563521, #38 56563534}, the weaker pair. The user must re-tick by 20:00Z (`round38/report.json` R38-A1 why; `CONTEXT.md` l.3844-3855).
- **exp89t outcome odds** (disputed priors): P(0.960) 0.01-0.08, P(0.959 with UP) 0.14-0.47, P(0.959 with k = 0) 0.23-0.40, P(<= 0.958) 0.18-0.56 (`round38/report.json` new_facts (5)).

**Changes since ~09:45Z (curation 37):**
- **Done:**
  - **W338**: the user was told at 09:19Z (`CONTEXT.md` l.4489-4490);
  - **W339**: the timer texts are superseded as pointers (l.4490-4492). Killing them was rejected as unnecessary (`round38/report.json` rejected);
  - **W296 for round 37**: committed in 66f1eeb;
  - **T100 09:58Z**: the feed ran; its flag was a false positive (l.4502-4508).
- **Armed but defective:** **W340**. The pre_exp89t job pid 18408 is armed but skips an error block and never retries, so it is replaced by **W349** (R38-A4).
- **Still overdue, folded into W347:** **W343** (the R37-A6 addendum was never written; `round38/report.json` plan_issues (7)).
- **Superseded:**
  - **W341 / C7**: now card **v3** (W346);
  - **T215**: the 19:47Z re-read is replaced by the 19:44:45Z manual list (W351, C12).
- **New:**
  - actions **W346-W353** (= R38-A1..A7, plus the round-38 commit);
  - reminders **T219-T223**;
  - contradictions **C10-C13**;
  - insights **I419-I429**.

---

## OVERDUE / DUE NOW

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W352** (new; = **R38-A7**) | **Refresh the KEY FACTS in the round prompt** for rounds 39+. <br>- Set: best public 0.959 = exp87a 56640366; E10 trigger >= 0.960 (>= 0.961 after a promotion); exp89t PENDING with T0 09:00:17Z; the slot-2 outcome; the S0 tags; the rank. <br>- Drop: "best public 0.958 = exp85a", "E10 >= 0.959", and the probe-51 / NIGHT / MORNING lines | not started (the round-38 prompt was still stale) | **before round 39, 13:13Z (16:13 MSK)** | `round38/report.json` R38-A7; `round38/scan_hyp_exp89tread38.notes.md` ("Task preamble stale") |
| **W353** (new) | **Commit round 38** (untracked) and `e10_watch/20260929T1013Z.txt` with named paths, as the user, with **no Co-Authored-By**. Render `round38/REPORT.md` and `round37/REPORT.md` from report.json (both were blocked by the harness). Rounds 29-35 also have no REPORT.md | not started | with the 12:00Z CONTEXT commit (W347) | `git status`; `round38/report.notes.md` 10:38:56Z; `memory/feedback-git-no-coauthor.md` |
| W126 (part 2) | Add RESULTS.md rows for probes **47-54**: <br>- 47: 0.955; 48: 0.957; 49: 0.955; 50: exp85a 0.958; 51: exp87a 0.959; <br>- 52: exp89r 0.957; 53: exp75 0.955; 54: exp89p 0.956. <br>Then probe 55 (exp89t) when it reads | **overdue**: rows still end at 46 (l.79) | low; post-deadline OK | `experiments/RESULTS.md` l.79; `experiments/lb_poll/poll.log` l.30393-30400 |
| W336 | One line saying that the user's 08:27Z / 08:28Z instructions override R8's 10:00Z edge (l.1671) and l.3685's "no midday slot" | not started, low. The 10:00Z edge has now passed; exp89t is the only post-edge mechanism | with the 12:00Z entry | `CONTEXT.md` l.1671, l.3685, l.4426-4440 |
| W286 / W297 / W202 + W244 / W176 / W177 / W182 / I208 / W57 / W66 / W31 / W72 / W150 / W308 | The floatout int-casting line; the stale runbook l.66; the cron-defect line; old info and curator lines; ROUND RECORD; LESSONS H1; old text fixes; the I-045 curator note | overdue, low | H2, 29 Sep 23:00Z; post-deadline OK | `_curation/36/watch.json`, `_curation/35/watch.json`, `_curation/26/watch.json` |

## CONTRADICTIONS TO RESOLVE BEFORE THEY FIRE

| ID | Conflict | Which text wins | Evidence |
|---|---|---|---|
| **C10** (new) | **Card v2 l.54** (`scratchpad/card_fill_1203_v2.txt`, built 10:01Z) ends the Satwik line with "Это довод за страховку #37." and lacks "Не подтверждено". R37-A4 dropped that argument because exp75 hedges cap 6 and K just as #37 does. The CONTEXT 09:57Z summary shortened R37-A4 to "optional Satwik line", which is how the argument came back | **The R37-A4 text verbatim**, or drop the line (W346 (1)). Log "no «довод за #37»" in CONTEXT (W347 (c)). Do **not** use the R38-RC-B wording ("0.036", "1–2 деления") | `round38/scan_plancheck.notes.md` 10:22Z; `round38/report.json` R38-A1 (1), plan_issues (1); `CONTEXT.md` l.4500 |
| **C11** (new, conditional) | R37-A3 "56 -> 58 = MASKED" contradicts card step 4 / R26-A4 (b): a file with a strictly lower display does not mask. This matters only if slot 2 is used | **R26-A4 (b)**, through R38-A3 (W348) | `round38/report.json` plan_issues (6); `round38/scan_hyp_exp89tread38.notes.md` GAPS (2) |
| **C12** (new; supersedes the T215 half of C8) | The **~19:47Z poll.log re-read** (R37-A7 (3)) sees only the ~19:40:33Z header. A completion in (19:40:33, 19:45:17] would code '?' even at 0.960 | **The R38-A6 manual list at 19:44:45Z** (W351) replaces the re-read | `round38/v_hyp_exp89tread38_r38t-h1.notes.md`; `round38/report.json` R38-A6 |
| **C13** (new) | The **round prompt KEY FACTS** say best public 0.958 = exp85a and E10 >= 0.959. `CONTEXT.md` 28 Sep 21:45Z says 0.959 = exp87a and the trigger is >= 0.960 | CONTEXT. Fix with W352 before 13:13Z | `round38/report.json` R38-A7, plan_issues (11) |
| C2 (updated) | The **11:10Z timer** (pid 17304) still reads "submit by 11:30 UTC" | **Pointer only:** log "A-M2 UNUSED (exp89r 0.957 < 0.958; the user's 12:00Z hold governs slot 2)". **No submit** | `CONTEXT.md` l.4490-4491; `round38/report.json` R38-A2 (b) |
| C7 (updated) | The **12:03Z timer** (pid 33456) names card v4 (round27) | Pointer only: send **card_fill_1203_v3** (W346), never v4 | `CONTEXT.md` l.4491-4492; `round38/report.json` R38-A2 (b) |
| C8 (updated) | Card step 9 gives exp89t's window as 9.27-9.45 h, but the observed CI-family L starts at 8.88 h, so the early edge is ~17:53Z | Watch from ~17:50Z. The 19:43Z half is now C12 | `round37/report.json` R37-A7 |
| C9 | The pre-registered order puts П3 {V_pub, #37} first and П2 as a trade; the standing-prior MC favours P2 | **The pre-registered order stands.** The break-even figure goes in chat only (W345) | `CONTEXT.md` l.4476-4478; `round37/report.json` R37-A8 |
| C5 / C6 | C5: card l.40 SEC clause vs the slot-2 outcome. C6: R8's 10:00Z edge vs exp89t | C5: set it after the 12:00Z log (W346 (3)). C6: the user's instructions win (W336) | `round38/report.json` R38-A1 (3); `CONTEXT.md` l.1671 |

## NEXT 24 H (29 Sep ~10:45Z -> 23:59Z)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| T207 | **10:41:53Z** RUN 46, **~11:41Z** RUN 47; loop END **12:00Z** | e10 snapshots. **RUN 47 (11:41Z) is the S0 fallback for exp89t.** `20260929T1013Z` (count 56) is the fallback-of-fallback. After 12:00Z no e10 snapshots exist | due (RUN 46 not logged at 10:41Z) | `experiments/e10_watch/watch_loop.log`; `e10_watch_loop.py` l.64; `round38/report.json` new_facts (2) |
| T210 | **~11:15Z** | The last moment a slot-2 candidate can be first seen. After it, a sighting is information only. Round 38 found nothing to build (E10 not met) | watch; null so far | `round38/report.json` new_facts (1), (7) |
| C2 | **11:10Z** timer (14:10 MSK) | **No submit.** Log only "A-M2 UNUSED" | pending | `CONTEXT.md` l.4490-4491 |
| T100 | feed **~11:28Z**, then ~12:58Z, 14:28Z, 15:58Z, 17:28Z, 18:58Z ... | E10 v3 trigger >= 0.960. After 12:00Z the feed is the only watcher, and it is not competition-scoped (see I429) | live | `experiments/discussions/feed_loop.log`; `round38/scan_plancheck.notes.md` 10:29Z |
| W340a | **11:45Z** (timer pid 24636) | Build the S0 fallback from the newest e10 snapshot <= 12:00Z (`scratchpad/mk_s0.py`; slice from the 'Rank,' line; count 56) | armed | `CONTEXT.md` l.4494-4495; `round37/scan_plancheck.notes.md` |
| **T209 + W342** | **11:50Z** timer (pid 21496; 14:50 MSK); **log by 12:00Z** (15:00 MSK) | **Slot-2 decision.** Send the final message; with no new yes, log "slot 2 UNUSED (rule (a) not met; 08:28Z hold)". **Only on the user's explicit new yes:** submit plus W348 | timer armed | `CONTEXT.md` l.4500-4501; `round37/report.json` R37-A5 |
| **W348** (new; = **R38-A3**, conditional) | at a slot-2 submit, ~12:00Z | **Only if the user says yes.** <br>- Log the pre-read UP-test line: count S0 + 1; a slot-2 file completing first at <= 0.958 does not mask; S0 = the count-57 save. <br>- Arm one job that runs `timeout 180 python tools/uptest.py save mid_<token>` at the first terminal of {56669888, slot-2 ref}. <br>- Add a card v3 section-5 PENDING line. <br>**Void if UNUSED** | conditional | `round38/report.json` R38-A3; C11 |
| **W347** (new; = **R38-A2**, absorbs **W343** / R37-A6) | **12:00Z** (15:00 MSK), merged with the slot-2 log | **One CONTEXT entry:** <br>- **(a)** the R37-A6 facts: exp89r L (9.06, 9.14] h from the count jump 55 -> 56 at 09:14:09Z with LastSubmissionDate unchanged; k = 0; the Satwik 744273 null; exp89t P(>= 0.960) <= ~0.11. Leave `ledger.md` alone; <br>- **(b)** the timers are pointers (11:10Z log only; 12:03Z = card v3 sha8); <br>- **(c)** the Satwik line = the R37-A4 text, with **no "довод за #37"**; <br>- **(d)** the **E10 policy after 11:30Z**: verify that a flag is a biohub notebook (1 call), then push the user in MSK. No copy, dummy or submit unless the user explicitly accepts a file that reads after 23:00 MSK; <br>- **(e)** optional: only the corrected R38-RC-A INFO line. <br>Commit as the user, with no co-author | not started (`grep -c "count jump"` = 0; `grep -c Satwik` = 1) | **12:00Z** | `round38/report.json` R38-A2; plan_issues (4), (7) |
| **W346** (new; = **R38-A1**, supersedes W341 / W333) + T60 / W266 (2) / W302 / W307 / W311 (c) / W320 / W324 | pre-fill by **~11:40Z**; header and rank after 11:45Z; SEC clause after 12:00Z; **send 12:03Z** (15:03 MSK) | **Card v3.** Write `scratchpad/card_fill_1203_v3.txt` from v2; keep v2 and the template a134d5e4 untouched. <br>- **(1)** l.54: the R37-A4 Satwik text verbatim, or drop it (C10). <br>- **(2)** l.3 / l.7 / l.8: the newest **non-error** poll header (<= 15 min old, MSK first); SELECTED from 1 read-only call; rank and block position from the 11:45Z S0 (position = rank - rows > 0.959). <br>- **(3)** l.40: the SEC clause from the 12:00Z log. <br>- **(4)** l.48: the 22:45-23:00 MSK '?' parenthesis. <br>- **(5)** section 5: "exp89t ещё не прочитан: отметьте выбранную пару сейчас ...". <br>- **(6)** token checks: П1, рекомендую, '<', '[если', П4, **довод** each 0; "подтверждено" 2 (or 1 if the line is dropped). <br>This card is also the **12:00Z finals-tick reminder**. **Never tick.** Record the v3 sha8 in CONTEXT | not started (v2 exists and is stale) | **12:03Z** | `round38/report.json` R38-A1; `round38/report.notes.md` 10:33Z |
| W345 (optional) | with the 12:03Z card, **in chat only** | The P2/P3 break-even caption (CI private mean ~+0.0004..+0.0006) | optional | `round37/report.json` R37-A8 |
| **T219** (new) | **13:13-17:13Z** rounds 39-43 | Do W352 first. Then a light browser scan only (0 API calls beyond the loops), or skip. **Check that R38-A1..A6 were applied:** the card v3 sha8 and the playbook are in CONTEXT, pre_exp89t is re-armed, and the manual-admit script is alive. The recheck lens is saturated | pending | `round38/report.json` next_focus |
| T213 | all afternoon and evening | Keep the laptop on AC with the lid open (AC, 78% at 10:30Z) | watch | `round38/scan_plancheck.notes.md` 10:30Z |
| **W349** (new; = **R38-A4**, fixes W340) | **before 17:40Z** (20:40 MSK) | **Re-arm the pre_exp89t save.** <br>- **Why:** job 18408 greps only the LAST block; an error block (05:34:41Z, 05:46:17Z today) prints "no pre-save", and a failed save is never retried. <br>- **Fix:** kill 18408/35124. At 17:40:00Z take the newest **non-error** block; run `PYTHONIOENCODING=utf-8 timeout 180 python tools/uptest.py save pre_exp89t` unless 56669888 is COMPLETE or ERROR; retry once after 5 min if 'SubmissionCount' is missing. <br>- **Alternative:** on an 18408 "no longer PENDING" notice while the newest non-error block still shows PENDING, run the same save by hand at once | not started | **17:40Z** | `round38/report.json` R38-A4, plan_issues (5); `round38/report.notes.md` 10:34Z |
| **W350** (new; = **R38-A5**) | **log before 17:53Z** (20:53 MSK); apply at the first terminal header | **Log the exp89t read playbook T0-T8 pre-score.** <br>- **Inputs:** L_hi = H + 210 s x F - T0, from headers only (e10 ends 12:00Z). <br>- **Before any message:** 1 SELECTED call, cases (a)-(d); every message says "сначала снимите, потом отметьте ... «2 of 2 selected» до 23:00 МСК". <br>- **T1 / T2 (promotion):** first append **"RECOMMENDED PAIR = П3 {exp89t 56669888, #37 56563521} ..."** so the 18:37Z / 19:43Z / 21:05Z timers do not push back to exp87a. The card gets the exp89t token row {56669888, CI, SEC нет, 4 рычага, dummy CSV 6edc1f180116}. <br>- **T3 '0u' UP test:** retries on a download failure at most 2 times, last start 19:40Z. <br>- **T4 / T5 / T6 / T7 / T8:** use the report's exact MSK texts | not started (`grep -c "RECOMMENDED PAIR"` = 0) | **17:53Z** | `round38/report.json` R38-A5, plan_issues (8)-(9) |
| **W351** (new; = **R38-A6**) | **arm and log before 17:53Z**; fires **19:44:45Z** (22:44:45 MSK) | **Manual-admit list.** <br>- **Script:** ONE self-contained background bash script, copied from `night_guards.sh` l.59-60 (**not** timer.sh). Sleep to 19:44:30Z, then step 1 s to 19:44:45Z. <br>- **Skip if:** 56669888 is already terminal, or a poller header is stamped >= 19:44:30Z. <br>- **Otherwise:** `timeout 60 python -m kaggle competitions submissions biohub-cell-tracking-during-development -v > experiments/lb_poll/_admit_subs.csv`, and append `=== $TS [manual-admit]` plus `head -60` to poll.log only if `^ref,` matches. Single attempt. <br>- **If COMPLETE:** run the W350 read at once (UNPROVEN-ins). <br>- **Log the corrected odds:** ~0.1-0.15% of reads matter; private EV ~0 | not started (`grep -c manual-admit` = 0) | arm by **17:53Z** | `round38/report.json` R38-A6; `round38/v_hyp_exp89tread38_r38t-h1.notes.md` |
| T214 | **17:40Z** | The pre_exp89t save fires (W349). The count must be 56 | armed (defective until W349) | `CONTEXT.md` l.4493-4494 |
| **T208 + W344** (updated) | **~17:53Z** early edge; typical **18:00-18:30Z** (21:00-21:30 MSK); 10.2 h **19:12:17Z**; admit edge **19:45:17Z** | **exp89t read**, coded per W350 T1-T8 against the running champion exp87a 0.959: <br>- **>= 0.960**: new V_pub; <br>- **0.959**: V_pub only with an attributable UP (`uptest.py compare pre_exp89t post_exp89t`; count 56 -> 57); <br>- **below**: no change. <br>**Push the user in MSK at once** on any V_pub change | pending | `CONTEXT.md` l.4466-4470, l.4493-4497; `round38/report.json` R38-A5 |
| T152 | **18:37Z** (21:37 MSK), timer pid 33156 | FINAL proposal: reuse the 12:03Z v3 copy, updating the header, SELECTED, rank and the exp89t read. **Rank source:** post_exp89t / pre_exp89t, otherwise `timeout 180 python tools/uptest.py save fill_1837` (the watcher saves only on 0.959, I416). Compare against the logged RECOMMENDED PAIR | pending | `round37/report.json` R37-A7 (4); `round38/report.json` R38-A5 (1) |
| **T220** (new) | **19:12:17Z** (22:12 MSK) | 10.2 h edge. If exp89t is still PENDING at the first header after it, push the T7 text (with the (a)-(d) SELECTED variants) | pending | `round38/report.json` R38-A5 (6) |
| T161 + **T221** (new; replaces T215) | **19:43Z** timer (pid 30648), then **19:44:45Z** manual-admit (W351) | Notify-only V_pub re-check, then the manual list. If exp89t is not terminal after the manual list, push the T8 '?' line right after it | pending | `round38/report.json` R38-A5 (7), R38-A6 |
| T10 | **20:00Z (23:00 MSK)** | **The user ticks the finals.** The session never ticks. If the user does nothing, the weaker #37 + #38 stay (see I426) | pending | `CONTEXT.md` l.3844-3855, l.4091-4092 |
| **T222** (new) | **after 20:00Z** until 23:59Z | E10 or exp89t information arriving after the tick: re-selection is allowed until 02:59 MSK (23:59 UTC). No copy or submit unless the user explicitly accepts it (W347 (d)) | pending | `round38/report.json` R38-A2 (d), R38-A5 (7) |
| T153 / T162 | ~20:00-20:30Z; **21:05Z** timer (pid 31720) | Verify that API SELECTED matches the user's pair (or the logged RECOMMENDED PAIR); last-call notify on a mismatch | pending | `CONTEXT.md` l.3474, l.4092, l.4099 |
| W177 H2 / T49 | 23:00Z / 23:00-23:45Z | LESSONS H2; final public LB snapshot | pending | `_curation/20/watch.json`; `CONTEXT.md` l.2619 |
| T11 / T163 | **29 Sep 23:59Z** (02:59 MSK 30 Sep) | Deadline. Re-ticks are allowed until then. No slot resets before it (the next 00:00Z reset is 30 Sep) | - | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/overview |
| W19 / W73 / W102 / W93 / W165b / W261 / T196 | standing | Standing rules: <br>- ONE poller; the header must be < 15 min old; <br>- never resubmit class-C or ERRORed files; <br>- SEC final only as V_pub (Q3); <br>- every Kaggle call wrapped in a timeout; <br>- light API polling (`memory/feedback-kaggle-api-load.md`) | standing | `CONTEXT.md` l.3331-3335, l.3692-3703, l.4112-4114 |

## LATER (after 29 Sep 23:59Z)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T155 | 30 Sep 00:07Z, timer pid 19388 | POST-DEADLINE job: private read v2 + L1-L7 | `CONTEXT.md` l.3714-3715, l.4131 |
| T216 | post-deadline | Lesson check: was Satwik's "public has few divisions" right? Compare the private deltas of the division levers (cap 6, K) with their public '+' reads (I413, I423) | `round37/scan_browser.notes.md`; `round38/scan_recheck.notes.md` |
| **T223** (new) | post-deadline | Lesson check: the lab sign record on CI (lab -0.00509 vs three public +0.001) and on DIS (lab +0.00089 vs public ~0) (I419, I420) | `round38/v_recheck_r38-rc-a-running-champion-conservative-rea.notes.md` |
| W317 (a)(c)(d) / W321 / W326 / W312 / W295 / W29 | post-deadline | BH-0005 alias; the E10 validator env; full-tree external scans; Charannoo divrelax; the Kai-Gowers negatives; division agenda; 744093; z-shift I-029; MAX_UM 2.0. Optional: a kaggle_feed.py plausibility filter instead of the title blacklist (I429) | `round33`-`round35/report.json`; `round38/report.json` rejected |
| T133 / T170 | 3 Oct | GPU quota refresh (about 2.7 h left) | `CONTEXT.md` l.4239-4241 |

**Passed or finished time-bound items:**
- **Earlier deadlines:**
  - the R8 new-mechanism cutoff (27 Sep 12:00Z) passed;
  - the 28 Sep 12:00Z consolidation was superseded (T46);
  - the **R8 29 Sep 10:00Z hard edge passed**. exp89t is the only mechanism after it, covered by the user's yes (C6).
- **Today:**
  - probe 54 read 07:58Z; the user's yes 08:27Z; exp89t submitted 09:00:17Z;
  - exp75 read 09:09Z; exp89r read 09:19Z; the user was told about slot 2 at 09:19Z;
  - round 37 applied 09:57Z; the feed FP was logged 10:00Z; round 38 ran 10:13-10:38Z.
- **Friend replies:** none awaited (`CONTEXT.md` l.2175-2176).
- **Standing notes:**
  - **T156:** the tick is at 20:00 UTC = 23:00 MSK. Never write "20:00" without "UTC".
  - **T204:** the poller drifts +2 s per 10 min (~602 s cadence).
  - **T205:** LB `LastSubmissionDate` = the max submit time among SCORED files.

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I419** (new) | "exp89t-exp87a total +0.00089 = edge-only +0.00041 (the single FP flip) + node multiplier +0.00048 ... Node part is constant (deterministic from deletion) ... node bonus is embryo-independent in sign => it is ALSO in the public read" | `round38/v_recheck_r38-rc-a-running-champion-conservative-rea.notes.md` | The dummy-lab "+" for exp89t is **not** independent private evidence. Do not let a post-read narrative ("lab said DIS helps") override the running-champion rule. Only the corrected optional INFO line may be logged (W347 (e)). |
| **I420** (new) | "Lab reliability on this base: CI on K in dummy lab -0.00509 vs three public +0.001 reads (probes 48/51/53) -> lab sign-wrong on the CI half of the K+CI base" | same file | This is the third lab-vs-LB sign failure, after the edge filter (`memory/project-edge-filter-finding.md`). It is not in CONTEXT. It is the reason to quote no lab number on the card. |
| **I421** (new) | "Poller cadence ~602 s ... headers ~19:30:31, 19:40:33, 19:50:35Z -> the real loss window is (19:40:33, 19:45:17] ~4.7 min ... The 19:47Z poll.log re-read ... adds nothing" | `round38/v_hyp_exp89tread38_r38t-h1.notes.md` | This is why W351 exists and T215 is dropped (C12). |
| **I422** (new) | "FEASIBILITY TRAP: scratchpad timer.sh polls the clock every 30 s and only prints a message; its notification is queued until the session is free ... Must be a self-contained background script" | same file | This applies to **every** edge-critical action tonight (19:44:45Z, 17:40Z). If a timer only reminds the session, the call can land after the edge. |
| **I423** (new) | "Probe 26 ... 0.1 x div_J_pub = 0.036, J_pub ~0.36 ... One fork event = 0.1/(TP+FP+FN) ~ 0.0007-0.002 ... our public fork-set reads (+0.001..+0.002) are 1-2 events" | `round38/scan_recheck.notes.md` | The public '+' of cap 6 and K rests on 1-2 division events, which fits Satwik's null (I413). The R38 verifier refuted using it as card wording (R38-RC-B), but it is still the honest size of the division evidence. It is not in CONTEXT. |
| **I424** (new) | "#37 = #38 + x (base insertion); max(V,#37) - max(V,#38) >= 0 in every world iff x > 0; honest OOF +0.0019 (90% CI [-0.0007, +0.0050]) gives P(x > 0) ~0.85 ... Canned answer: '#38 лучше #37 только если сама базовая вставка делений вредит на привате (P ~0.1–0.2 ...)'" | `round38/report.json` new_facts (6); `round38/v_recheck_r38-rc-c-noins-38-partner-stays-out-base-i.notes.md` | This is the ready answer if the user proposes the "division-free" #38 after reading 744273. It is not in CONTEXT. |
| **I425** (new) | "tools/uptest.py compare = TeamIds above us in S0 with rank in S1 > ours; stale S0 cannot create a false UP (public bests never fall); only biases k to 0" | `round38/scan_plancheck.notes.md` 10:27Z; `round38/scan_hyp_exp89tread38.notes.md` | So k >= 1 from the stale 11:45Z fallback S0 still promotes exp89t (R38T-G6). Without this, a session might wrongly discard a stale-S0 UP. |
| **I426** (new) | "The user currently has the weaker {#37, #38} ticked, so the card should say to tick the chosen pair now" (I-227 provisional tick) | `round38/report.json` R38-A1 why and (5) | If exp89t reads late or the session fails, the default finals are the weaker pair. The W346 (5) line is the fix. |
| **I427** (new) | "Observed CI-family L: 8.88-9.05 (exp75), 9.04-9.22 (exp89r), 9.27-9.45 (exp48), 9.30-9.48 (exp87a). No CI file ever > 9.5 h" | `round38/v_hyp_exp89tread38_r38t-h1.notes.md` | exp89t should read by ~18:32Z (9.5 h). If it is still PENDING at ~18:40Z, that is already anomalous, so prepare the T7 text early. |
| **I428** (new) | "Fanch 0.958 -> 0.959 entered at #139 above us"; ours "#141, 17th of 21 in the 0.959 block (ranks 125-145)" | `round38/scan_browser.notes.md`; `round38/report.json` new_facts (2) | The card rank (v2 says #140, 16 of 20) is stale. Block position must be recomputed from the 11:45Z S0 (W346 (2)). |
| **I429** (new) | "after that [12:00Z] only tools/kaggle_feed.py (every 90 min; searches 'biohub' across all Kaggle, drops titles with xgboost/lgbm/optuna/stacking, flags score > 0.959)" | `round38/scan_plancheck.notes.md` 10:29Z | The feed can false-flag (0.9812 at 09:58Z) and can miss a real notebook with a blacklisted word in its title. Any flag after 12:00Z needs the 1-call competition-scoped check (W347 (d)). |
| I409 | "Count +1 with no display change = one new terminal completion between ... poll headers" (the count-jump timing method) | `round37/scan_hyp_readscard37.notes.md` 09:17Z | **Still not in CONTEXT** (`grep -c "count jump"` = 0). Due in W347 (a). |
| I410 / I411 | The e10 -> S0 builder must slice from the 'Rank,' line (KeyError 'TeamId'). `mk_s0.py`, `card_fill_1203*.txt`, `r38/dummy_lab*.py` and `r38/mc38_t.py` live **only in the session scratchpad** | `round37/scan_plancheck.notes.md`; `round38/scan_recheck.notes.md` | Still live. If the session restarts, rebuild the card from `round37/scan_hyp_readscard37.json` R37-F4 plus the R38-A1 edits. |
| I413 | Satwik (744273): "public LB has very few divisions ... local division gains ... no change or slight drop on LB" | `round37/scan_browser.notes.md`; https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744273 | Only a pointer is in CONTEXT (l.4500). The fact itself is due in W347 (a). |
| I416 | "exp89t watcher saves post_exp89t only at COMPLETE 0.959" | `round38/report.notes.md` 10:34Z (pid 29636) | The 18:37Z card rank needs `save fill_1837` on any other read (T152). |
| I417 / I418 | Card v5 is stale in 5 places; exp89s has no NEVER_SUBMIT flag | `round37/scan_plancheck.notes.md` | Never send the raw template. Only rule (a) and the hold keep exp89s out, so the 11:10Z timer stays log-only. |
| I412 / I414 / I415 / I402 / I403 | exp89s has ~0 V_pub value with exp89t on the board; the P2/P3 break-even; SEC -0.002 additive on both bases; the exp89t prior; the lab is not a sign instrument for exp89t | `round37/scan_recheck.notes.md`; `round36/report.json` | Unchanged. I403 is reinforced by I419 and I420. |
| I352-I401, I404-I408, I338-I348, I329/I330, I334-I337, I316-I326, I303-I313, I287-I302, I278, I72, I116, I145 | Unchanged older insights | `_curation/37/watch.json` ... `_curation/27/watch.json` | - |
