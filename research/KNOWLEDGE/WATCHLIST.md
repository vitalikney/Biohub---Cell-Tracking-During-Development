# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-29 ~13:50 UTC (16:50 MSK), curation 40. This updates the curation-39 build of ~11:40Z, which is committed in 8423ff8 with a structured copy in `research/KNOWLEDGE/_curation/39/watch.json`. Older predecessors run from `_curation/38/watch.json` down to `_curation/18/watch.json`. Rows not repeated here are unchanged there.

**Sources read for this update:**
- **`CONTEXT.md`:** 4,638 lines; `## 9. Literature` starts at l.4618. Nine new entries since curation 39:
  - l.4540-4546 (11:39Z): 744273 re-read, no knob;
  - l.4547-4548 (11:45Z): S0 fallback = `e10_20260929T1141Z` (#141 of 3,994, count 56, 17th of 22);
  - l.4549-4558 (11:54Z): **SLOT 2 HELD IN RESERVE** (user, chat ~11:56Z);
  - l.4559-4574 (11:54Z): **ROUND 39 APPLIED** (R39-A1..A6; A7/A8 scheduled);
  - l.4575-4578 (12:04Z): **finals card sent**, sha8 4fa899f9; SELECTED then = {#38, #37};
  - l.4579-4581 (12:37Z): **USER RE-TICKED П3** {exp87a 56640366, #37 56563521}, API-verified 12:37:31Z;
  - l.4582-4592 (12:59Z): feed. 744250: **a file must FINISH scoring by 23:59Z**;
  - l.4593-4606 (13:21Z): **private-risk audit**. Medal risk moderate, silver risk high; keep the pair;
  - l.4607-4617 (13:34Z): **USER DECISION B.** exp89t promotes ONLY at >= 0.960. The 17:40Z pre_exp89t job is CANCELLED.
- **`git log`:** 8423ff8, f54c9b0, fc98fa7, c3a9215, 40cc06d, ec3c5fb (11:54-13:34Z). **`git status`:**
  - `M experiments/lb_poll/ledger.md` and `poll.log`;
  - `?? research/wf_ideas_v4/round40/`;
  - `?? experiments/lb_poll/_lb/e10_20260929T1141Z/`: **the S0 fallback CSV is untracked**;
  - `?? experiments/lb_poll/_night_subs.csv` / `.err`.
- **`research/wf_ideas_v4/round40/report.json`** (13:13-13:40Z, untracked): **R40-A1..A9**, new_facts (1)-(9), plan_issues (1)-(10) and rejected. **REPORT.md is missing** (harness-blocked, `round40/report.notes.md` 13:40Z). The Russian text sits in `next_focus` as REPORT_RU.
  - **Round 40 did NOT see decision B.** Its notes say "no entry after it at 13:34Z" (`round40/report.notes.md` l.2), so R40-A2, A3 and A4 are written for the pre-B rule. See **C18**.
- **`experiments/lb_poll/poll.log`:** newest header **13:39:20Z** (l.31491). exp89t 56669888 is **PENDING**.
- **Loops:**
  - `experiments/e10_watch/watch_loop.log`: RUN 47 11:42:05Z, **END 12:00:00Z** (47 runs);
  - `experiments/discussions/feed_loop.log`: **12:58:56Z**, 4 new comments, E10 FLAG none. Next runs ~14:29Z, ~15:59Z, ~17:29Z, ~18:59Z (`round40/scan_plancheck.notes.md` 13:20Z).
- **Round prompt** `experiments/workflows/biohub-research-round.js`:
  - l.37 now has the R39-A6 text: Chrome only after 12:00Z, no `e10_snapshot.py`, 0 agent Kaggle calls in 17:30-20:00Z;
  - l.20 has the unrounded tie order and decision B;
  - but l.20 still says "Rank ~141 ... (17th of 21 ...)" and "currently ticked {#37, #38}". The PLAN CHECK text is the old W1 / 12:00 UTC boilerplate.
- **`experiments/RESULTS.md`:** probe rows still end at probe 46 (l.79).
- **Process census, 13:44Z (this curation, `ps -W` + `/proc/*/winpid`, 0 Kaggle calls).** Alive:
  - **`pre_exp89t.sh` w36816 is still alive** although CONTEXT l.4614 says it was CANCELLED;
  - `manual_admit.sh` w3028, `t7_trigger.sh` w29648, the exp89t watcher w30864, the watchdog w22236;
  - timers: 18:37Z w33156, 19:43Z w30648, 21:05Z w31720, 00:07Z w19388;
  - the feed loop w20892 with `sleep 5400` w37148;
  - the e10-signal waiter w20284: dead weight, because its log ended at 12:00Z;
  - the feed-signal waiter w24352 and the poller w37016.
  - **`mk_card_1837.py` is NOT in the scratchpad.** The files there are `card_1203_sent.txt`, `read_selected.py`, `t7_trigger.sh`, `pre_exp89t.sh`, `manual_admit.sh` and `mk_card_v3.py`.

All times are UTC. The user thinks in MSK = UTC+3 (`CONTEXT.md` l.3683-3687). IDs are stable: W = action, T = time-bound reminder, I = insight, C = contradiction. Status values: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at ~13:50Z, 29 Sep:**
- **Best display 0.959**, exp87a 56640366 = V_pub.
- **SELECTED = П3 {exp87a 56640366, #37 56563521}** (API 12:37:31Z, `CONTEXT.md` l.4579-4581). The finals are ticked. The pair changes only if exp89t reads **>= 0.960** (decision B, l.4607-4617).
- **exp89t 56669888 is PENDING** (T0 09:00:17Z). Edges:
  - typical read 18:17-18:29Z (21:17-21:29 MSK);
  - 10.2 h = 19:12:17Z;
  - admit edge 19:45:17Z (22:45 MSK).
- **Slot 2:** held in reserve (l.4549-4558). It is effectively dead after ~14:10Z (R40-A1). By default it expires unused at 23:59Z.
- **Rank:** #148 of 3,999; 17th of 22 in the 0.959 block; 131 teams above 0.959 (Chrome 13:20Z, `round40/report.json` new_facts (1)).

**Changes since ~11:40Z (curation 39):**
- **Done:**
  - W355 (l.4547-4548);
  - W354: the user overrode UNUSED with HELD IN RESERVE (l.4549-4558);
  - W346, the card sent (l.4575-4578);
  - W356, T7 armed (l.4563-4565, w29648 alive);
  - W357, the comparator (l.4565-4568);
  - W359 (1), (2) and the tie order (8423ff8; `biohub-research-round.js` l.20, l.37). The rest of it moves to **W369**;
  - W363, round 39 committed in 8423ff8. The REPORT.md renders move to **W374**;
  - **T10 (tick) done by the user at 12:37Z**;
  - C14 and C16 resolved.
- **Moot:** W358 and T214, because pre_exp89t was cancelled by decision B. The process is still alive: see **C17**.
- **New:**
  - actions **W364-W374** (= R40-A1..A9 adapted to decision B, plus the ops leftovers);
  - reminders **T230-T233**;
  - contradictions **C17-C20**;
  - insights **I440-I449**.

---

## OVERDUE / DUE NOW

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W364** (new; = **R40-A1**) | **Close the reserve slot in the log and tell the user.** <br>- **(1) One CONTEXT line, "RESERVE-SLOT EDGES".** The 12:59Z "non-CI ~9.0-9.5 h" is the safetail gate, not an observed L. Observed L: non-CI 6.69-7.81 h, CI 8.88-9.48 h, x138 verbatim 6.29-6.46 h. An E10 copy also needs the dummy (~35-45 min, GPU queues of 3-4 h have happened) and the user's yes. <br>- **Dummy-start edges:** default **14:10Z**; x138 7.5 h **15:50Z**; absolute last **16:50Z** (submit by ~17:30Z). After 14:10Z an E10 flag is info only; after 16:50Z say it cannot finish. <br>- **(2) One info line to the user** (text in R40-A1 (2)): "Запасной слот фактически закрыт ... П3 {exp87a 56640366, #37 56563521} остаётся." <br>- **Send it WITHOUT the R40-A2 question**, which decision B already answered (C18) | not started (`grep -c "RESERVE-SLOT EDGES" CONTEXT.md` = 0) | **now; before 14:10Z** (17:10 MSK) | `round40/report.json` R40-A1; `CONTEXT.md` l.4582-4588 |
| **W369** (new; = **R40-A6**; the rest of W359) | **Round-prompt refresh before round 41.** In KEY FACTS (`biohub-research-round.js` l.20): <br>- replace "Rank ~141 of 3 991 (17th of 21 ...)" with "#148 of 3 999, 17th of 22 (Chrome 13:20Z); S0 fallback e10 11:41Z = #141 of 3 994"; <br>- **delete "currently ticked {#37, #38}"**, which contradicts "The user ticked {exp87a ..., #37 ...}" in the same paragraph (C19); <br>- remove "S0 tags pre_exp89t (17:40Z)" (cancelled); <br>- slot 2 = "reserve effectively closed after ~14:10Z". <br>Also replace the PLAN CHECK boilerplate (W1 reads of probes 47-49, the 12:00 UTC slot, E10 > 0.956, PROPOSAL 12:00/18:00) with the evening chain: B-read → 18:37Z card → T7 ~19:20Z → manual-admit 19:44:45Z → 19:43Z / 21:05Z SELECTED checks → 00:07Z. Rounds 41-43 use an ops / READS-vs-CARD lens | not started (l.20 text verified 13:44Z) | **before 14:13Z** (17:13 MSK) | `round40/report.json` R40-A6, plan_issues (7) |
| **W373** (new) + **C17** | **Kill `pre_exp89t.sh` w36816, or log why it stays.** CONTEXT l.4614 says the 17:40Z save was CANCELLED, but the process was alive at 13:44Z. If it survives, it makes a Kaggle call at ~17:40Z inside the quiet window. It is on the allowed list, so it breaks no rule, but it contradicts the log. Use `taskkill /PID 36816 /F` after a fresh `/proc/<pid>/winpid` read, then add one CONTEXT line | not started | before **17:40Z** (20:40 MSK); best now | `CONTEXT.md` l.4614; census 13:44Z (`_curation/40/watch.notes.md`) |
| W126 (part 2) | Add RESULTS.md rows for probes 47-54: <br>- 47: 0.955; 48: 0.957; 49: 0.955; 50: exp85a 0.958; <br>- 51: exp87a 0.959; 52: exp89r 0.957; 53: exp75 0.955; 54: exp89p 0.956. <br>Then probe 55 (exp89t) when it reads | **overdue** (rows end at 46, l.79) | low; post-deadline OK | `experiments/RESULTS.md` l.79; `poll.log` l.31491-31500 |
| W336 | One line saying that the user's 08:27Z / 08:28Z instructions override R8's 10:00Z edge (l.1671) | not started; moot in practice | low | `CONTEXT.md` l.1671 |
| W286 / W297 / W202 + W244 / W176 / W177 / W182 / I208 / W57 / W66 / W31 / W72 / W150 / W308 | Older text and cleanup items | overdue, low | H2 29 Sep 23:00Z; post-deadline OK | `_curation/36/watch.json`, `_curation/26/watch.json` |

## CONTRADICTIONS TO RESOLVE BEFORE THEY FIRE

| ID | Conflict | Which text wins | Evidence |
|---|---|---|---|
| **C18** (new) | Round 40 (written 13:37-13:40Z) predates decision B (13:34Z). **R40-A2** asks the user a question already answered. **R40-A3 / R40-A4** and the embedded `mk_card_1837.py` still follow the pre-B rule: <br>- `PROMO = {"T1","T2","T3"}` (notes l.26); <br>- the T3 body promotes exp89t on 0.959 + UP (l.125); <br>- the PENDING line reads "основным может стать только при ≥ 0.960 или 0.959 с приписываемым UP" (l.114-115); <br>- UPWAIT promises "Если UP подтвердится, пришлю одну строку" (l.134); <br>- the T4 text cites "чемпион по порядку завершения" (l.126). <br>The HOLD rule of R40-A3 (5) has no purpose under B | **Decision B** (`CONTEXT.md` l.4607-4617): <br>- a 0.959 read = the T4 text "exp89t = 0.959 (ЧЧ:ММ МСК): по вашему решению B основной остаётся exp87a 56640366, пара {exp87a, #37} без изменений"; <br>- >= 0.960 = "снимите exp87a 56640366, отметьте exp89t 56669888 (#37 оставьте)". <br>Fix with **W366 / W367**. Never send UPWAIT or T3 | `round40/scan_hyp_exp89tmsg40.notes.md` l.15-184; `round40/report.notes.md` l.2 |
| **C17** (new) | CONTEXT l.4614 says "the 17:40Z pre_exp89t save job was CANCELLED", but w36816 `pre_exp89t.sh` was alive at 13:44Z. The round-prompt KEY FACTS also still name "pre_exp89t (17:40Z)" | **CONTEXT (cancelled).** Kill it with W373 | census 13:44Z; `biohub-research-round.js` l.20 |
| **C19** (new) | Round-prompt KEY FACTS l.20 says both "currently ticked {#37, #38}" and "The user ticked {exp87a 56640366, #37 56563521} (API 12:37Z)" | **API 12:37:31Z = П3** (`CONTEXT.md` l.4579). Fix with W369 | `biohub-research-round.js` l.20 |
| **C20** (new) | The 12:59Z reserve-slot edges ("non-CI ~9.0-9.5 h -> by ~14:30-15:00Z; CI -> by ~13:15Z") vs R40-A1 (gate vs observed L; dummy + yes; 14:10Z / 15:50Z / 16:50Z) | **R40-A1**, as a bookkeeping correction, not a rule change | `CONTEXT.md` l.4585-4588; `round40/report.json` R40-A1, plan_issues (2) |
| C15 (updated) | The 18:37Z / 19:43Z / 21:05Z timer texts push "if not the recommended pair" (w33156, w30648 and w31720 cmdlines, verified 13:44Z) | **The R39-A4 comparator** (`CONTEXT.md` l.4565-4568). **Today no push:** SELECTED = П3. Push only after exp89t >= 0.960, when V_pub changes | `CONTEXT.md` l.4565-4568, l.4579 |
| C11 (updated) | mid_<token> scope: R39-A1 (2) "void after 12:43Z" vs CONTEXT 11:54Z "ANY slot-2 submit today" | **CONTEXT 11:54Z** (R40-A7 (a), skeptic upheld) | `CONTEXT.md` l.4557-4558; `round40/v_plancheck_pc40-06.notes.md` |
| C14 / C16 | Tie order / the Fanch sentence | **Resolved.** The prompt l.20 now says unrounded order; the Fanch line never reached the user (card sent 12:04Z) | `biohub-research-round.js` l.20; `CONTEXT.md` l.4561-4563 |
| C9 / C5 / C6 / C7 / C8 | Older conflicts | Moot: the user ticked П3 and the card was sent | `_curation/39/watch.json` |

## NEXT 24 H (29 Sep ~13:50Z -> 23:59Z)

| ID | When (UTC / MSK) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W364 | **before 14:10Z** (17:10 MSK) | Reserve-slot edges line + user info line (no R40-A2 question) | not started | see OVERDUE |
| W369 | **before 14:13Z** (17:13 MSK) | Round-prompt KEY FACTS / PLAN CHECK refresh | not started | see OVERDUE |
| **T230** (new; follows T224) | **14:13, 15:13, 16:13Z** rounds 41-43; **17:13Z** round 44; **18:13Z** round 45 | Ops / READS-vs-CARD lens, Chrome-only browser, 0 Kaggle API calls. No builds, no slot work | pending | `round40/report.json` next_focus; `biohub-research-round.js` l.37 |
| **T231** (new; replaces the T100 schedule) | feed **~14:29Z, ~15:59Z, ~17:29Z** | E10 v3 trigger >= 0.960. **After 14:10Z a flag is info only** unless the user names the notebook (W364). **After 16:50Z it cannot finish in time.** No copy or submit without the user's explicit yes | live | `experiments/discussions/feed_loop.log`; `round40/report.json` R40-A1 |
| W364 edges | **15:50Z / 16:50Z** (18:50 / 19:50 MSK) | The last dummy-start edges for a verbatim-x138-length notebook (only on the user's yes). After 16:50Z: "cannot finish" | pending | `round40/report.json` R40-A1 |
| **W366** (new; = **R40-A3**, adapted to B) | install + dry-run **before 17:40Z** (20:40 MSK); used **18:37Z** | **Card builder.** <br>- **(1)** Copy l.15-184 of `round40/scan_hyp_exp89tmsg40.notes.md` (text sha8 10420089) to `<scratchpad>/mk_card_1837.py`. <br>- **(2) Patch it for decision B before the dry-run:** T3 must leave PROMO and become a non-promotion 0.959 body with the B text of CONTEXT l.4613-4614; the PENDING line becomes "основным может стать только при ≥ 0.960"; remove UPWAIT or make it unusable; the T4 text becomes the B wording. <br>- **(3)** Run `--dry-all` and log the sha8s. <br>- **(4)** At 18:37Z make 1 fresh SELECTED read (`read_selected.py`). Pass **`--lb e10_20260929T1141Z --teams 3994`** because pre_exp89t is cancelled (I442), or `post_exp89t` if the watcher saved one | **not started** (`mk_card_1837.py` absent at 13:44Z) | `round40/report.json` R40-A3; `CONTEXT.md` l.4607-4617; C18 |
| **W367** (new; = **R40-A4**, adapted to B) | log **before ~18:00Z** (21:00 MSK) | **exp89t MESSAGE SET** CONTEXT line, pre-score. Use `round40/scan_hyp_exp89tmsg40.json` case (a) П3 / case (b) П2 **with the T3 texts replaced by the B T4 text**. Also log: <br>- a fresh SELECTED read before each send; <br>- after a T1/T2 promotion, "RECOMMENDED PAIR = П3 {exp89t 56669888, #37 56563521}" first; <br>- no MASKED branch today (a count jump of 2 means the user submitted: stop and ask); <br>- the DIS line "от 0.000 до +0.002" | not started (`grep -c "MESSAGE SET"` = 0) | `round40/report.json` R40-A4; C18 |
| T225 + W361 + **W368** (new; = **R40-A5**) | **17:13Z** round prep; kill **17:29-17:35Z** (20:29-20:35 MSK) | **Liveness check** of: the watchdog 22236 (one-shot: re-arm after any alert), manual_admit 3028, t7 29648, the watcher 30864, the poller 37016 and the timers. <br>**Then stop the feed loop** w20892 and its sleep child after its ~17:29Z run. Also kill the dead e10 waiter w20284. Leave the feed-signal waiter w24352. Log one ops line. Its ~18:59Z run (~35 calls, up to 6 retries) would otherwise land in the quiet window and the read tail | pending | `round40/report.json` R40-A5; `round40/scan_plancheck.notes.md` 13:20Z |
| T228 | **17:30-20:00Z** (20:30-23:00 MSK) | Quiet window: only the poller, the watcher save, manual_admit, t7 and the SELECTED reads call Kaggle. pre_exp89t is cancelled (W373) | standing | `biohub-research-round.js` l.37; `CONTEXT.md` l.4614 |
| T213 | all afternoon and evening | Laptop on AC with the lid open. Network was lost on battery 28 Sep 15:00-15:40Z and 29 Sep 05:30-05:57Z | watch | `round39/scan_plancheck.notes.md` |
| T208 + W344 (**updated for B**) | early **~17:53Z**; typical **18:17-18:29Z**; poller headers ~18:20:14Z / ~18:30:16Z | **exp89t read under decision B:** <br>- **>= 0.960 (T1, or T2 if the poller header is > 19:12:17Z):** promote. First append the RECOMMENDED PAIR line, then push "снимите exp87a 56640366, отметьте exp89t 56669888 (#37 оставьте)" in MSK. <br>- **0.959:** T4-B text; the pair is unchanged. The UP test and post_exp89t are info only. <br>- **<= 0.958 (T5)**, **ERROR (T6):** no resubmit. <br>1 SELECTED read before each message | pending | `CONTEXT.md` l.4529-4535, l.4607-4617 |
| T226 | **18:13Z** round (21:13 MSK) | READS-vs-CARD from local files only. **Do not skip it** | pending | `round39/report.json` R39-A6 (3) |
| T152 | **18:37Z** (21:37 MSK), timer w33156 | FINAL card via the B-patched `mk_card_1837.py` (W366). Compare SELECTED with the R39-A4 comparator. The HOLD / UPWAIT branch is moot under B (C18) | pending | `CONTEXT.md` l.4565-4568 |
| T227 | **~19:20Z** (22:20 MSK), the first header >= 19:12:17Z | The T7 trigger w29648 fires. If exp89t is PENDING, make 1 SELECTED read and send the T7 text | armed | `CONTEXT.md` l.4563-4565 |
| T161 + T221 | **19:43Z** timer w30648; **19:44:45Z** manual-admit w3028 | Notify-only V_pub re-check with the comparator, then the single-attempt manual list. If exp89t is still not terminal, push the T8 '?' line | armed | `CONTEXT.md` l.4535-4537 |
| T10 (**updated**) | **20:00Z (23:00 MSK)** | Finals tick. **Already done: П3** (12:37Z). Re-tick only after an exp89t >= 0.960 read. The session never ticks | done unless exp89t >= 0.960 | `CONTEXT.md` l.4579-4581, l.4616-4617 |
| **T232** (new) | **>= 20:05Z** (23:05 MSK), optional | One manual `PYTHONIOENCODING=utf-8 python tools/kaggle_feed.py --topics 12 --no-kernels`, only if host notices are wanted after the tick | optional | `round40/report.json` R40-A5 |
| T222 | 20:00-23:59Z | New information after the tick: re-selection is allowed until 02:59 MSK. No copy or submit without the user's explicit yes | pending | `CONTEXT.md` l.4549-4558 |
| T153 / T162 | ~20:00-20:30Z; **21:05Z** timer w31720 (00:05 MSK) | Verify SELECTED against the comparator; last-call notify on a mismatch | armed | `CONTEXT.md` l.4565-4568 |
| W362 / **W371** (= **R40-A8**) | only if asked, before 20:00Z | The cap-6 partner line (R39-A9). The exp51 / exp52 / exp48 partner line: "+0 to +0.0002, оставляем П3" | conditional | `round39/report.json` R39-A9; `round40/report.json` R40-A8 |
| W370 (a) (new; = **R40-A7** (a)) | only on a slot-2 submit | Arm `timeout 180 python tools/uptest.py save mid_<token>` at the first terminal of {56669888, slot-2 ref}, whatever the time | conditional | `round40/report.json` R40-A7 |
| W177 H2 / T49 | 23:00Z / 23:00-23:45Z | LESSONS H2; the final public LB snapshot (at most 1 call) | pending | `_curation/20/watch.json`; `CONTEXT.md` l.2619 |
| T11 / T163 | **29 Sep 23:59Z** (02:59 MSK 30 Sep) | Deadline. Files must FINISH scoring by then (744250). Slot 2 expires unused by default | - | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744250 |
| W19 / W73 / W102 / W93 / W165b / W261 / T196 | standing | Standing rules: <br>- ONE poller; the header must be < 15 min old; <br>- never resubmit class-C or ERRORed files; <br>- SEC final only as V_pub; <br>- a timeout on every Kaggle call; <br>- light polling | standing | `CONTEXT.md` l.3331-3335, l.3692-3703; `memory/feedback-kaggle-api-load.md` |

## LATER (after 29 Sep 23:59Z)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T155 + **W370 (b)** | 30 Sep **00:07Z** (03:07 MSK), timer w19388 | POST-DEADLINE job: private read v2 + L1-L7. **Commit as Vitaly Neybauer with no Co-Authored-By.** Check `git log -1 --format=%B \| grep -ci co-authored` = 0 | `CONTEXT.md` l.3714-3715; `round40/report.json` R40-A7 (b); `memory/feedback-git-no-coauthor.md` |
| **W374** (new; supersedes the W363 remainder) | with the 00:07Z commit, or earlier | Commit `round40/` and **`experiments/lb_poll/_lb/e10_20260929T1141Z/lb.csv`** (the S0 fallback, untracked: I448). Render `round37`-`round40` REPORT.md; round 40's text is REPORT_RU in `report.json` next_focus | `git status` 13:42Z; `round40/report.notes.md` 13:40Z |
| **W372** (new; = **R40-A9**) | post-deadline, optional | Annotate the `RESULTS.md` l.20 "exp07+pp+steal ... keep steal off" row: superseded by the DaughterNet-ranked steal. Write "steal on in all three finals files; steal_cap 3 vs 2; the cap never binds" | `round40/report.json` R40-A9 |
| T216 / T223 / T229 + **T233** (new) | post-deadline | Lesson checks: <br>- I413 / I423 (few public divisions), I419 / I420 (the lab sign record); <br>- T229 (the MC П2 vs П3); <br>- **T233:** the audit's claim that ">= 4 thousandths (cap 6, K) are public-only" (I441), against the private exp87a vs exp75 vs #37 | `_curation/39/watch.json`; `CONTEXT.md` l.4596-4604 |
| W317 / W321 / W326 / W312 / W295 / W29 | post-deadline | Older research follow-ups; a kaggle_feed.py plausibility filter (I429) | `_curation/38/watch.json` |
| T133 / T170 | 3 Oct | GPU quota refresh | `CONTEXT.md` l.4239-4241 |

**Passed or finished time-bound items:**
- **Earlier deadlines:**
  - the R8 new-mechanism cutoff (27 Sep 12:00Z) passed;
  - the 28 Sep 12:00Z consolidation was superseded;
  - the R8 29 Sep 10:00Z edge passed.
- **Today:**
  - the S0 fallback 11:45Z (l.4547);
  - the slot-2 decision 11:54Z (l.4549);
  - R39 applied 11:54Z (l.4559);
  - the finals card sent 12:04Z (l.4575);
  - the user tick 12:37Z (l.4579);
  - feed 12:58Z (l.4582);
  - the risk audit 13:21Z (l.4593);
  - decision B 13:34Z (l.4607);
  - the e10 loop END 12:00Z (`watch_loop.log`).
- **Friend replies:** none awaited (`CONTEXT.md` l.2175-2176).
- **Standing notes:**
  - **T156:** 20:00 UTC = 23:00 MSK. Always write the zone.
  - **T204:** poller cadence ~601.5 s.
  - **T205:** LB `LastSubmissionDate` = the max submit time among SCORED files.

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I440** (new) | The embedded card builder has `PROMO = {"T1", "T2", "T3"}`. Its PENDING line says "основным может стать только при ≥ 0.960 или 0.959 с приписываемым UP", and UPWAIT adds "Если UP подтвердится, пришлю одну строку" | `round40/scan_hyp_exp89tmsg40.notes.md` l.26, l.114-115, l.134 | If it is copied verbatim per R40-A3 (1), the 18:37Z card would contradict decision B in front of the user. R40-A3 (4) calls the PENDING clause "cosmetic", but under B it is **wrong** (W366, C18). |
| **I441** (new) | "Of exp87a's +0.006 over x138, >= 4 thousandths (cap 6, K) are public-only; no lever has an out-of-embryo check ... #37 alone (0.954) ranks ~#489 today (below bronze ~#399)" | `CONTEXT.md` l.4596-4600; `research/wf_ideas_v4/risk_audit/results.json` | The hedge keeps bronze only if rival forks also lose their public gains. This is the main post-deadline lesson (T233). |
| **I442** (new) | "The e10 fallback CSV has 1,006 rows, which would print '#141 из 1 006'"; "pass '--lb e10_20260929T1141Z --teams 3994'" | `round40/report.json` R40-A3 (6), plan_issues (4) | pre_exp89t is now cancelled, so the fallback is the **default** LB input for the 18:37Z card, not an edge case. |
| **I443** (new) | "feed loop ... ~18:59:28Z (INSIDE the 17:30-20:00Z window, ~35 calls in ~8 s)"; "_retry tries=6" | `round40/scan_plancheck.notes.md` 13:20Z | Nobody wrote a stop into a script. It relies on the main session killing w20892 at 17:29-17:35Z (W368). |
| **I444** (new) | "The user ticks in the Kaggle web UI, so 'no chat message since' does not mean 'SELECTED unchanged'" (R40M-9 rejected) | `round40/report.json` rejected | Always make a fresh `read_selected.py` call before each message and card. |
| **I445** (new) | "T4 has no MASKED branch today: slot 2 is unused and only 56669888 is PENDING, so the count can move only 56 -> 57; a jump of 2 means the user submitted something, so stop and ask" | `round40/report.json` R40-A4 | This is an anomaly detector for the info-only UP compare. It is not yet in CONTEXT (W367). |
| **I446** (new) | "Five teams jumped together from 0.956-0.957 to exactly 0.963 ... looks like one private pipeline"; we fell #141 → #148 because 124 → 131 teams now sit above 0.959 | `round40/report.json` new_facts (1), (2); `round40/scan_browser.notes.md` | Compare the exp89t S0/S1 by count and score, never by rank. Rank drift is not a finals signal. |
| **I447** (new) | Observed L: "non-CI 6.69-7.81 h, CI 8.88-9.48 h, verbatim x138 (exp56) 6.29-6.46 h"; the 12:59Z "~9.0-9.5 h" is the safetail gate | `round40/report.json` R40-A1; `experiments/lb_poll/ledger.md` | Needed to answer "can we still send X?" after the tick (C20, W364). |
| **I448** (new) | `experiments/lb_poll/_lb/e10_20260929T1141Z/lb.csv` is **untracked** in git | `git status` 13:42Z; `CONTEXT.md` l.4547-4548 | It is the only S0 for the info-only UP compare and the card rank. A clean or checkout would lose it. Commit it with W374. |
| **I449** (new) | "UPWAIT text 'не позже 22:50 МСК' ... if the user answers 'keep exp87a even with UP', UPWAIT's promise line must be dropped - UP becomes info-only" | `round40/v_hyp_exp89tmsg40_r40m-8.notes.md` caveats (1)-(3) | The user did answer B (keep), so this caveat is now live. Folded into W366. |
| I436 (**updated**) | The ticked pair changed from {#37, #38} (~0.49 bronze / ~0.11 silver) to **П3 {exp87a, #37}** (audit default ~0.79 / ~0.58; ~0.56 / ~0.19 if cap 6 + K are -0.001 on private) | `CONTEXT.md` l.4579, l.4600-4602 | The card's main goal was met at 12:37Z. |
| I437 (updated) | The slot-2 edge arithmetic. It is now superseded by the stricter W364 edges (14:10Z / 15:50Z / 16:50Z) | `round40/report.json` R40-A1 | - |
| I433 | "exp89t watcher ... uses last() incl. error blocks; post_exp89t only on COMPLETE 0.959" | `round39/scan_plancheck.notes.md` | Under B, post_exp89t is info only. Still read poll.log by hand at each header after ~17:50Z. |
| I432 | "watchdog 22236 'break's on the first ON-BATTERY or POLL-STALE alert" | `round39/scan_plancheck.notes.md` | Re-arm after any alert (T225). |
| I424 / I420 / I423 | "#38 лучше #37 только если ... (P ~0.1–0.2)"; the lab CI sign was wrong; public division evidence = 1-2 fork events | `round38/report.json`; `round38/scan_recheck.notes.md` | Still not in CONTEXT. Post-deadline lessons (T216 / T223). |
| I410 / I411 | `read_selected.py`, `t7_trigger.sh`, `manual_admit.sh`, `card_1203_sent.txt` and soon `mk_card_1837.py` live **only in the session scratchpad** | `CONTEXT.md` l.4563-4565, l.4575-4578 | If the session restarts, the armed jobs die. After a restart, re-arm from CONTEXT l.4559-4617 and the round39/round40 report texts. |
| I430, I431, I434, I435, I438, I439, I427, I428, I422, I419, I421, I425, I429 and older | Resolved, in CONTEXT or moot (I434 is moot: pre_exp89t is cancelled; I435 is fixed in prompt l.37) | `_curation/39/watch.json` ... `_curation/27/watch.json` | - |
