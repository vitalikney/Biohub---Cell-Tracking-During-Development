# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-29 ~09:45 UTC (curation 37). This updates the curation-36 build of 29 Sep ~08:40Z, which is committed in 7caa068 with a structured copy in `research/KNOWLEDGE/_curation/36/watch.json`. Older predecessors run from `_curation/35/watch.json` down to `_curation/18/watch.json`. Rows not repeated here are unchanged there.

**Sources read for this update:**
- **`CONTEXT.md`:** 4,508 lines; `## 9. Literature` starts at l.4488. Four new entries since curation 36:
  - l.4441-4452 (**08:51Z, CLARIFY + ORDER (1) SEC EXCEPTION**, R36-A2): logged pre-score at header 08:48:23Z. It also marks R36-A1 RESOLVED and says slot 2 is decided at ~11:50-12:00Z, not at exp89r's header;
  - l.4453-4457 (**08:51Z, 08:30Z TIMER NOTE**, R36-A3): includes the 744273 edge-only null line. OPS: laptop on battery at 08:50Z (78%);
  - l.4458-4470 (**09:00Z, PROBE 55 SUBMITTED**): exp89t, ref **56669888**, at 09:00:17Z. Gate PASS, CSV 6edc1f180116, 1 submit left today;
  - l.4471-4478 (**09:09Z, READ probe 53**): exp75 = **0.955**, clean. CI now has 3 of 3 public '+' reads. P2 {exp87a, exp75} is a TRADE; П3 {exp87a, #37} stays recommended;
  - l.4479-4487 (**09:19Z, READ probe 52**): exp89r = **0.957**, so DIS ~0 (dd = 0, '?'). Rule (a) is **not met**, so exp89s is **not sent**; the slot-2 default is now UNUSED. V_pub stays exp87a.
- **`git log`:** 7caa068 (round 36, 08:51Z), 9693f08 (probe 55 submitted), 782eed2 (probe 53), 348b9dc (probe 52, 09:19Z). `git status`: `?? research/wf_ideas_v4/round37/`, `?? experiments/e10_watch/20260929T0941Z.txt`, `M experiments/lb_poll/ledger.md, poll.log`, `M experiments/e10_watch/*`.
- **`research/wf_ideas_v4/round37/`** (untracked, 09:13-09:40Z): `report.json` (**R37-A1..A8**, with `report_md_ru` embedded), `report.notes.md`, and all `scan_*` / `v_*` notes. **REPORT.md is missing**: the Write tool refused it, so the orchestrator must write it (`round37/report.notes.md` 09:40Z). The round read CONTEXT up to the 09:19Z entry, so **it is current**.
- **`experiments/lb_poll/poll.log`:** newest header **09:38:34Z** (l.30027): exp89t 56669888 PENDING; exp89p 0.956, exp75 0.955, exp89r 0.957, exp87a 0.959.
- **Loops:**
  - `experiments/e10_watch/watch_loop.log`: RUN 45 at 09:42:06Z (8/8, CHANGES=13, signals 0); next run 10:41:53Z. `e10_watch_loop.py` l.64 ends the loop at 12:00Z, so the last run is ~11:41Z.
  - `experiments/discussions/feed_loop.log`: the last loop line is 08:28:33Z. A `digest_20260929T0918Z.md` exists (committed in 348b9dc) and shows E10 FLAG none (l.42).
- **Rank:** `experiments/e10_watch/20260929T0941Z.txt` l.280 and l.1164 show **#140**, 0.959, SubmissionCount 56, 16th of 20 in the 0.959 block (ranks 125-144), 124 teams at >= 0.960, 3,989 teams.
- **`grep -c` on CONTEXT.md** returns 0 for: Satwik, "count jump", mk_s0, card_fill, pre_exp89t, "few divisions", fill_1837, 19:47. `experiments/RESULTS.md` probe rows still end at probe 46 (l.79).
- **Timers** (per `round37/report.notes.md` 09:36Z and `round37/scan_plancheck.notes.md`):
  - stale texts: 11:10Z (pid 17304, "M2 NON-CI ... submit by 11:30 UTC") and 12:03Z (pid 33456, "fill ... **round27/finals_card_v4_ru.md**");
  - OK: **11:50Z** (pid 21496, SLOT 2 DECISION), 18:37Z, 19:43Z, 21:05Z and 30 Sep 00:07Z; hourly rounds 10:13-18:13Z;
  - the exp89t watcher (pids 29636 / 30864) saves post_exp89t **only at COMPLETE 0.959**;
  - **no pre_exp89t save job exists**.

All times are UTC; the user thinks in MSK = UTC+3 (`CONTEXT.md` l.3683-3687). IDs are stable: W = action, T = time-bound reminder, I = insight, C = contradiction. Status values: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at ~09:45Z, 29 Sep:**
- **Best display 0.959**, exp87a 56640366 (probe 51; CI). V_pub = exp87a (`CONTEXT.md` l.4485-4487).
- **Rank #140** (09:42Z), unchanged since 09:08Z (k = 0). Medal lines: silver #200 (0.957 block), bronze #399 (0.955 block) (`round37/report.json` new_facts).
- **Today's reads:** exp89p 0.956 (SEC '-'), exp75 0.955 (CI '+', clean), exp89r 0.957 (DIS ~0).
- **Only PENDING file:** exp89t 56669888. Typical read ~18:00-18:30Z, early edge ~17:53Z, 10.75 h admit edge 19:45:17Z (`round37/report.json` R37-A7).
- **Slots:** 4 used today, **1 left** (slot 2). It is held until 11:50-12:00Z, and the default is now **UNUSED** (`CONTEXT.md` l.4484-4485).
- **SELECTED** is expected to be {#37 56563521, #38 56563534}. The user must re-tick by 20:00Z (`CONTEXT.md` l.3844-3855).

**Changes since ~08:40Z (curation 36):**
- **Done:**
  - **W330** (CLARIFY, l.4441-4452) and **W331** (08:30Z note, l.4453-4457), both logged pre-score;
  - **W337** (the 744273 line, l.4455-4456);
  - **T206 / W329**: exp89t gated and submitted 09:00:17Z (l.4458-4470);
  - **T159 / T182** exp75 read (l.4471);
  - **W332 / W325 / W323**: the exp89r read is coded with the DIS estimate, the B25 side line and rule (a) (l.4479-4487);
  - **W296** for round 36: REPORT.md committed in 7caa068.
- **Resolved:** **C1** (l.4452, then exp89r read 0.957) and **C4** (l.4451 "R36-A1 RESOLVED").
- **Moot:**
  - **W335 / T211 / C3**: exp89s is not sent by default (l.4484);
  - **I405**: "no CI in the finals" required V_pub = exp89s;
  - **I401**: the conditional table is superseded by the exp89t-aware MC in I412;
  - **I406**: not needed while exp89s stays unsent;
  - **W330 (iii) fallback**: no SEC file can be champion now; exp89p is 0.956 and exp89r 0.957 (`round37/scan_hyp_readscard37.notes.md` 09:20Z).
- **No longer forgotten:** **W334**. An 11:50Z timer now exists (pid 21496).
- **New:** actions **W338-W345** (= R37-A1..A8); reminders **T213-T218**; contradictions **C7-C9**; insights **I409-I418**.

---

## OVERDUE / DUE NOW

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W338** (new; = **R37-A1**) | **Slot-2 status message to the user, in MSK:** "exp89r = 0.957 (12:18 МСК): по правилу (a) exp89s не отправляем; других кандидатов нет. Последний слот дня останется пустым, если до ~14:15 МСК не появится публичный ноутбук ≥ 0.960 или новая раскрытая настройка ... exp89t ждём ~20:55–21:30 МСК." Skip it if the user has already been told after 09:19Z. 0 Kaggle calls | **not started**: no CONTEXT line after l.4487 | now; useless after **~11:15Z** | `round37/report.json` R37-A1 |
| **W339** (new; = **R37-A2**) | **Timer hygiene.** Kill **pid 17304** (the 11:10Z stale "submit by 11:30 UTC" text) and **pid 33456** (the 12:03Z text pointing at **card v4**). Re-arm both as pointers: <br>- **11:10Z**: "LOG ONLY: A-M2 UNUSED ... no submit; slot 2 = 11:50Z decision"; <br>- **12:03Z**: "send scratchpad card_fill_1203.txt (template round29/finals_card_v5_ru.md a134d5e4, NOT v4) per R37-A4". <br>If they are not re-armed, act on these texts when the old timers fire | **not started** | **before 11:10Z** | `round37/report.json` R37-A2; `round37/scan_plancheck.notes.md` (timer list) |
| **W340** (new; = **R37-A3 (2)**) | **Arm the pre_exp89t save job now.** At **17:40Z**, if 56669888 is still PENDING: `PYTHONIOENCODING=utf-8 timeout 180 python tools/uptest.py save pre_exp89t` (1 LB download). The count must be 56. No count-56 S0 exists yet (post_exp75 has count 55), so without this save a 0.959 exp89t is scored MASKED/BLIND | **not started** (`grep -c pre_exp89t` = 0) | arm now; the job fires at 17:40Z | `round37/report.json` R37-A3; `round37/report.notes.md` 09:36Z ("NO pre_exp89t save job exists") |
| **W343** (new; = **R37-A6**) | **One CONTEXT addendum**; do not duplicate the 09:19Z read. It should record: <br>- **(a)** the e10 0913Z count jump 55 -> 56 with LastSubmissionDate unchanged, which gives exp89r L (9.06, 9.14] h and k = 0 (method: I409); <br>- **(b)** Satwik 744273 on few public divisions (I413); <br>- **(c)** the exp89t prior: P(>= 0.960) <= ~0.11, P(0.959 with an attributable UP) ~0.25-0.3; <br>- **(d)** the stale timers are superseded | **not started** (`grep -c Satwik` = 0) | now, with the next commit | `round37/report.json` R37-A6 |
| W296 / W303 (updated) | Commit **round 37** (still untracked) with named paths, as the user, with no Co-Authored-By. Write `round37/REPORT.md` verbatim from `report.json` `report_md_ru`; the subagent could not write it. Rounds 29-35 still have no REPORT.md | overdue (low), except round 36 (done, 7caa068) | with the next CONTEXT commit | `ls research/wf_ideas_v4/round29..37` (REPORT.md only in round36); `round37/report.notes.md` 09:40Z; `memory/feedback-git-no-coauthor.md` |
| W126 (part 2) | Add RESULTS.md rows for probes **47-54**: <br>- 47: 0.955; 48: 0.957; 49: 0.955; 50: exp85a 0.958; 51: exp87a 0.959; <br>- **52: exp89r 0.957; 53: exp75 0.955; 54: exp89p 0.956**. <br>Then probe 55 (exp89t) when it reads | **overdue**: rows still end at 46 (l.79) | before the 12:03Z card (low); post-deadline OK | `experiments/RESULTS.md` l.79; `experiments/lb_poll/poll.log` l.30027 |
| W336 | One line saying that the user's 08:27Z / 08:28Z instructions override R8's 10:00Z edge (l.1671) and l.3685's "no midday slot" | not started, low. Mostly moot if slot 2 stays UNUSED, but exp89t (built 08:23Z) is still outside R8 | with the next CONTEXT entry | `CONTEXT.md` l.1671, l.3685, l.4426-4440 |
| W286 / W297 / W202 + W244 / W176 / W177 / W182 / I208 / W57 / W66 / W31 / W72 / W150 / W308 | The floatout int-casting line; the stale runbook l.66; the cron-defect line; old info and curator lines; ROUND RECORD; LESSONS H1; old text fixes; the I-045 curator note | overdue, low | H2, 29 Sep 23:00Z; post-deadline OK | `_curation/36/watch.json`, `_curation/35/watch.json`, `_curation/26/watch.json` |

## CONTRADICTIONS TO RESOLVE BEFORE THEY FIRE

| ID | Conflict | Which text wins | Evidence |
|---|---|---|---|
| **C2** (still live) | The **11:10Z timer** (pid 17304) still reads "M2 NON-CI DEADLINE CHECK ... submit by 11:30 UTC" | The user's 08:28Z hold and rule (a), which failed at 0.957. **No submit at 11:10Z.** Fix it with W339 | `round37/report.notes.md` 09:36Z; `CONTEXT.md` l.4433-4440, l.4484 |
| **C7** (new) | The **12:03Z timer** (pid 33456) says "fill research/wf_ideas_v4/round27/finals_card_v4_ru.md ... R27-A8". R32-A3 says the template is **card v5** `round29/finals_card_v5_ru.md` (sha8 a134d5e4) | **Card v5**, through the pre-filled block `scratchpad/card_fill_1203.txt` (sha8 dd1bdc22). v4 lacks the GAP RULE v2 pool, the running-champion order and exp89t | `round37/scan_plancheck.notes.md`; `round37/report.json` R37-A2, R37-A4 |
| **C8** (new) | **Card step 9** gives exp89t's window as 9.27-9.45 h. The observed CI-family L starts at **8.88 h**, so the early edge is ~17:53Z. The **19:43Z reminder** also falls 2 min **before** the 10.75 h admit edge (19:45:17Z) | **R37-A7:** watch from ~17:50Z; push immediately on any V_pub change; re-read poll.log once more at **~19:47Z** if exp89t is still PENDING at 19:43Z | `round37/scan_hyp_readscard37.notes.md` ("CI family L observed"); `round37/scan_plancheck.notes.md` (exp89t times) |
| **C9** (new, info) | The **pre-registered order "П3 {V_pub, #37} first, П2 as trade"** (EXP75 PARTNER RULE v2 (b), `CONTEXT.md` l.4476-4478) is not what the standing-prior model ranks first. It puts P2 {exp87a, exp75} ahead on bronze at CI sd <= 0.0012 | **The pre-registered order stands** (a change now would be post-hoc). The user gets the break-even number only as an optional chat caption (W345), **never on the card** | `round37/report.json` plan_issues (7), R37-A8; `round37/scan_recheck.notes.md` (mc37_p2p3) |
| C5 (updated) | Card l.59 must state the **actual slot-2 outcome**. It is most likely "UNUSED (rule (a) not met; 08:28Z hold)", unless the user gives a new yes at 11:50Z | Set it from W342's outcome in W341 (2) | `round37/report.json` R37-A4 (2), R37-A5 |
| C6 | R8's 10:00Z edge vs exp89t / slot 2 | The user's explicit instructions win. Log W336 | `CONTEXT.md` l.1671, l.4426-4440 |

## NEXT 24 H (29 Sep ~09:45Z -> 23:59Z)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| **T212** (continued) | **10:13Z** round 38, then hourly at hh:13Z | Round 38: a **browser-only** scan for E10 >= 0.960 or a disclosed x138-family value. It is the last scan that can still feed slot 2. Also check that W338 / W339 / W340 are done. From 13:13Z to 17:13Z the rounds are light browser scans or skipped; 0 Kaggle API calls beyond the loops | pending | `round37/report.json` next_focus |
| T207 | **10:41:53Z** e10 RUN 46, then the last at **~11:41Z**; loop END 12:00Z | Rank / block snapshots. **The 11:41Z snapshot is the S0 fallback for exp89t** (W340a) | pending | `experiments/e10_watch/watch_loop.log` RUN 45; `e10_watch_loop.py` l.64 |
| T100 | feed every 90 min: next ~**09:58Z** (the last loop line is 08:28:33Z), then ~11:28Z, and on until 23:59Z | E10 v3 trigger >= 0.960. The best public notebook is 0.953 (`digest_20260929T0918Z.md` l.42). If no 09:58Z line appears, check that the feed loop is alive | live, null | `experiments/discussions/feed_loop.log` |
| **T210** | a slot-2 candidate must be **first seen by ~11:15Z** | A >= 0.960 non-CI public notebook, or a new disclosed setting, needs a build, a dummy and the R22-A1 gate (35-45 min in total). After ~11:15Z a sighting is information only | watch | `round37/report.json` R37-A1 (why), plan_issues (5) |
| C2 / W339 | **11:10Z** timer (14:10 MSK) | **No submit.** Log only "A-M2 UNUSED; the 11:30Z cutoff is replaced by the 12:00Z hold" | pending | `round37/report.json` R37-A2 |
| **W340a** (new; = **R37-A3 (1)**) | **~11:45Z**, after the 11:41Z e10 run | Build the exp89t S0 fallback: `python <scratchpad>/mk_s0.py 20260929T1141Z` (it slices from the 'Rank,' line into `experiments/lb_poll/_lb/e10_<ts>/lb.csv`). Check count 56 and log "S0_fallback = e10_<ts>, count 56, rank R". 0 Kaggle calls | not started | `round37/report.json` R37-A3 (1); `round37/scan_plancheck.notes.md` (KeyError 'TeamId') |
| **T209 + W342** (updated; = **R37-A5**) | **11:50Z** timer (pid 21496; 14:50 MSK); **log by 12:00Z** (15:00 MSK) | **Slot-2 decision.** <br>- **(1)** Glance once at the newest digest and the e10 diff (a record only). <br>- **(2)** Message the user: "Слот 2: по правилу (a) exp89s не отправляется (exp89r 0.957, DIS ≈ 0) ... основным он может стать только случайно (~3–6%) ... По правилу слот остаётся пустым." <br>- **(3)** With no answer by 12:00Z, log "slot 2 UNUSED (rule (a) not met; 08:28Z hold). DIS 1.75 / exp89e not revived". <br>**Only on the user's explicit new yes:** `nb_try exp89s,exp89q $KS "$M56S"` with G1 / G2 (used_today 4) / G3 / G5, then arm a post_exp89s watcher | timer armed; not started | `round37/report.json` R37-A5; `CONTEXT.md` l.4433-4440, l.4484 |
| **W341** (new; = **R37-A4**, supersedes W333) + W266 (2) / T60 / W302 / W307 / W311 (c) / W320 / W324 | **12:03Z** (15:03 MSK); pre-fill by ~11:40Z | **Card fill.** This is also the **12:00Z finals-tick reminder**. Start from `scratchpad/card_fill_1203.txt` (sha8 dd1bdc22); the template a134d5e4 stays untouched. <br>- **(1)** Refresh the poll header (<= 15 min), SELECTED (1 read-only call) and rank (e10 1141Z or the W340a build). <br>- **(2)** Set the slot-2 clause from W342 (C5). <br>- **(3a)** Section 3: replace the two false-condition exp75 lines with "exp75 прочитан: 0.955, чистый ...". <br>- **(3b)** Section 5: the admit clause becomes "≥ 0.960 или 0.959 с приписываемым UP". <br>- **(3c)** Section 5: the push promise becomes "сразу после чтения exp89t (и проверю в 22:43 МСК)". <br>- Optional: the Satwik line in section 6 (I413). <br>Re-run the token checks (П1 0, "рекомендую" 0, '<' 0, '[если' 0, П4 0). Keep the П3/П2 order and step 10. **Never tick** | pending | `round37/report.json` R37-A4; `round29/finals_card_v5_ru.md` |
| **W345** (new; = **R37-A8**, optional) | with the 12:03Z card, **in chat only** | The P2/P3 caption with the break-even (CI private mean ~+0.0004..+0.0006). **Do not** use the scan's "9 из 12" or "треть" wording | optional | `round37/report.json` R37-A8; `scratchpad/r37skep/mc_std_grid.txt` |
| W19 / W73 / W102 / W93 / W165b / W261 / T196 | standing | ONE poller; header < 15 min old; never resubmit class-C or ERRORed files; SEC final only as V_pub (Q3); every Kaggle call wrapped in a timeout (`uptest.py save` always under `timeout 180`) | standing | `CONTEXT.md` l.3331-3335, l.3692-3703, l.4112-4114 |
| **T213** (new) | 13:13-17:13Z | Hourly rounds are light or skipped. The laptop was on battery at 08:50Z (78%), so keep it on AC and the lid open through the evening | watch | `CONTEXT.md` l.4456-4457, l.4327 |
| **T214** (new; = W340 firing) | **17:40Z** | The pre_exp89t save fires if 56669888 is still PENDING; the count must be 56 | armed? (W340) | `round37/report.json` R37-A3 (2) |
| **T208 + W344** (updated; = **R37-A7**) + W316 | **~17:53Z** early edge; typical **18:00-18:30Z**; 10.2 h mark **19:12:17Z**; admit edge **19:45:17Z**; tail ~19:54Z | **exp89t read**, coded at once against the running champion exp87a 0.959: <br>- **>= 0.960**: new V_pub (CI, 4 levers); <br>- **0.959**: V_pub only with an attributable UP (`uptest.py compare pre_exp89t post_exp89t`; count 56 -> 57, otherwise one lag re-save; 56 -> 58 = MASKED); <br>- **below**: no change. <br>With L_hi between 10.2 and 10.75 h, a '+' or '0u' is UNPROVEN-ins. **Push the user in MSK immediately on any V_pub change**, with П3 = {exp89t 56669888, #37 56563521} and П2 = {exp89t, exp75 56656157} as a trade | pending | `CONTEXT.md` l.4466-4470; `round37/report.json` R37-A7 |
| T152 + W344 (4) | **18:37Z** (21:37 MSK), timer | FINAL proposal: reuse the 12:03Z filled copy, updating only the header, SELECTED, rank and the exp89t read. **Rank source:** post_exp89t / pre_exp89t, otherwise `timeout 180 python tools/uptest.py save fill_1837` (1 call). Never "рекомендую". If V_pub changed, re-run `scratchpad/r31v/mc31v.py` | pending | `round37/report.json` R37-A7 (4); `round31/report.json` R31-A4 (5) |
| T161 + **T215** (new) | **19:43Z** timer, then **~19:47Z** one extra poll.log read | Notify-only reminder plus a V_pub re-check. If exp89t is still PENDING at 19:43Z, re-read at ~19:47Z; the admit edge is 19:45:17Z (C8) | pending | `round37/report.json` R37-A7 (3) |
| T10 | **20:00Z (23:00 MSK)** | **The user ticks the finals.** The session never ticks. If the user does nothing, #37 + #38 stay | pending | `CONTEXT.md` l.3844-3855, l.4091-4092 |
| T153 / T162 | ~20:00-20:30Z; **21:05Z** timer | Verify that the API SELECTED set matches the user's pair; last-call notify on a mismatch | pending | `CONTEXT.md` l.3474, l.4092, l.4099 |
| W177 H2 / T49 | 23:00Z / 23:00-23:45Z | LESSONS H2; final public LB snapshot | pending | `_curation/20/watch.json`; `CONTEXT.md` l.2619 |
| T11 / T163 | **29 Sep 23:59Z** (02:59 MSK 30 Sep) | Deadline: re-ticks are allowed until then. No submission slot resets before the deadline (the next 00:00Z reset is 30 Sep, after it) | - | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/overview |

## LATER (after 29 Sep 23:59Z)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T155 | 30 Sep 00:07Z, timer (armed) | POST-DEADLINE job: private read v2 + L1-L7 | `CONTEXT.md` l.3714-3715, l.4131; `round37/report.notes.md` (timer list) |
| **T216** (new) | post-deadline | Lesson check: was **Satwik's "public has few divisions"** right? Compare the private deltas of the division levers (cap 6, K) with their public '+' reads (I413) | `round37/scan_browser.notes.md` |
| W317 (a)(c)(d) / W321 / W326 / W312 / W295 / W29 | post-deadline | BH-0005 alias; the E10 validator env; full-tree external scans; Charannoo divrelax; the Kai-Gowers negatives (I394 / I395); division agenda; 744093; z-shift I-029; MAX_UM 2.0 | `round33`-`round35/report.json` |
| T133 / T170 | 3 Oct | GPU quota refresh (about 2.7 h left) | `CONTEXT.md` l.4239-4241 |

**Passed or finished time-bound items:**
- **Earlier deadlines:** the R8 new-mechanism cutoff (27 Sep 12:00Z) passed; the 28 Sep 12:00Z consolidation was superseded (T46); the R8 29 Sep 10:00Z hard edge passes at 10:00Z today; the only new mechanism after it is exp89t, covered by the user's yes (C6).
- **This morning:**
  - probe 54 read 07:58Z; rule (a) 08:19Z; the user's yes 08:27Z; slot 2 held 08:28Z;
  - CLARIFY + 08:30Z note (08:51Z); exp89t submitted 09:00:17Z;
  - exp75 read 09:09Z; exp89r read 09:19Z.
- **Friend replies:** none awaited (`CONTEXT.md` l.2175-2176).
- **Standing notes:**
  - **T156:** the tick is at 20:00 UTC = 23:00 MSK. Never write "20:00" without "UTC".
  - **T204:** the poller drifts +2 s per 10 min.
  - **T205:** LB `LastSubmissionDate` = the max submit time among SCORED files (see I409).

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I409** (new) | "Count +1 with no display change = one new terminal completion between 09:08:57Z and 09:14:09Z ... Method: a count jump with an unchanged LastSubmissionDate time-stamps a completion between poll headers" | `round37/scan_hyp_readscard37.notes.md` 09:17Z; `round37/report.json` R37-A6 (a) | It tightens L (exp89r to 9.06-9.14 h) and gives an early read signal for exp89t from any LB save. It is not in CONTEXT (`grep -c "count jump"` = 0) until W343. |
| **I410** (new) | "Builder must slice the leaderboard_rows block from the 'Rank,' line: the first line 'CSV rows with Score >= 0.953: ...' makes csv.DictReader fail with KeyError 'TeamId' ... No e10-built _lb folder exists yet ... R32-A2 path untested until now" | `round37/scan_plancheck.notes.md` | The e10 -> S0 fallback path crashes if done naively. `mk_s0.py` lives **only in the session scratchpad**, so a new session would not find it (W340a). |
| **I411** (new) | The 12:03Z card block (`card_fill_1203.txt`, sha8 dd1bdc22), `mk_s0.py`, `r37skep/mc_std_grid.txt` and `r37/mc37_*.txt` sit in `C:\Users\vital\AppData\Local\Temp\claude\...\acabaea6-...\scratchpad`, not in the repo | `round37/report.json` R37-A3 / A4 / A8 | W341 and W340a depend on files that are not git-tracked. If the session restarts, rebuild them from `round37/scan_hyp_readscard37.json` R37-F4, which embeds the card block (`scan_hyp_readscard37.notes.md` 09:3xZ). |
| **I412** (new) | "MC exp89s vs exp89t ... P(exp89s becomes V_pub \| d_R) = 0 if exp89t on time; with p_late 0.03: .0001/.0031/.016/.029 at d_R .957/.958/.959/.960 ... R36H-1 (pre-exp89t) had P(exp89s V_pub \| .958) .29-.38" | `round37/scan_recheck.notes.md` | This is the number behind "slot 2 UNUSED": with exp89t on the board, exp89s has essentially no V_pub value. It replaces I401. It is not in CONTEXT. |
| **I413** (new) | Satwik (744273, ~09:06Z): "I believe the public LB has very few divisions ... local division gains ... no change or slight drop on LB ... public = easier/less dense embryo"; Yassine Alouini: shake-up "Very highly" | `round37/scan_browser.notes.md`; `experiments/discussions/digest_20260929T0918Z.md`; https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744273 | Our '+' division levers (cap 6, K) were read on the "easy" embryo. The partners #37 and exp75 carry neither, which is what hedges them. It is a second external null after SGHWR's. Not in CONTEXT (`grep -c Satwik` = 0); W343 (b), and the optional card line in W341. |
| **I414** (new) | "P2{87a,75} vs P3{87a,#37} bronze ... CI 0 .713 vs .741; CI -.0003 .663 vs .718 ... Break-even CI private mean ~+0.0003 (sd .0012) / ~+0.0005 (sd .0015)"; skeptic: "break-even ~+0.0004..+0.0006" | `round37/scan_recheck.notes.md`; `round37/report.notes.md` 09:39Z | This is the one decision-relevant number for the user's П3 vs П2 choice (C9, W345). The card has no model numbers by rule. |
| **I415** (new) | "SEC+DIS on CI base = -0.002 (consistent with SEC -0.002 on non-CI base)" | `round37/scan_hyp_readscard37.notes.md` 09:20Z | SEC reads additive at -0.002 on both bases. That closes the I400 "SEC x CI interaction" worry: DIS really is ~0, not masked. |
| **I416** (new) | "exp89t watcher saves post_exp89t only at COMPLETE 0.959" | `round37/report.notes.md` 09:36Z; `round37/scan_plancheck.notes.md` | At >= 0.960 or <= 0.958 no post-read LB save is made, so the 18:37Z card rank needs `save fill_1837` (W344 (4)). |
| **I417** (new) | "Card v5 ... no 'exp89t = ' token_ref; step 5 lever list lacks exp89t (=4 ...); step 9 windows stale (A-M2); l.60 stale A-M2 sentence; l.64 CI line lists probes 48/51 only (probe 53 exp75 +0.001 missing)" | `round37/scan_plancheck.notes.md` | The template is known-stale in 5 places. Only the filled block fixes them, so never send the raw template. |
| **I418** (new) | "exp89s folder ... no NEVER_SUBMIT, probe.json no 'never submit'" | `round37/scan_plancheck.notes.md` | exp89s is technically submittable. Only rule (a) and the 08:28Z hold keep it out, so a stale-timer misread (C2) could still send it. That is why W339 is due before 11:10Z. |
| I402 (updated) | exp89t: "GIVEN exp89r <= 0.957: P(>= 0.960) 0.09-0.11"; round 37: P(0.959 with an attributable UP) ~0.25-0.3; private effect ~0 | `round36/report.json` R36-A1; `round37/report.json` R37-A6 (c) | Now conditioned (exp89r read 0.957). The most likely outcome is a 0.959 tie with exp87a (`CONTEXT.md` l.4486). |
| I403 | "not a sign instrument for division or coordinate levers, and not for exp75 / exp89t" | `round36/report.json` new_facts (6) | Still live: quote no lab prediction for exp89t. |
| I404 | 744273 SGHWR edge-only null | `experiments/discussions/744273.md` | **Now logged** (`CONTEXT.md` l.4455-4456). |
| I400 | SEC x CI interaction (-0.0016 vs -0.0012) | `round36/scan_recheck.notes.md` | Largely answered by I415. |
| I391 / I392 | Card l.54 exp75 = no partner with a CI V_pub; `uptest compare` does not enforce counts, so the `_b` re-save is the only guard against a lag | `round35/*` | Live for W341 and the exp89t UP test (W344). |
| I394 / I395 | Kai-Gowers readmission negatives; the single-process 27000 s degrade costs -0.021 LB | `round35/scan_hyp_external35.notes.md` | Post-deadline lessons (W326). |
| I384 / I385 / I386 | No mc34_* number on the card; P2 beats P3 on bronze in 9-10 of 13 runs; exp89u stays off | `round34/*` | Consistent with I414. The card still carries no model numbers. |
| I356 | `tools/runtime_ledger.py --print` also rewrites `experiments/lb_poll/ledger.md` | `round32/scan_plancheck.notes.md` | `M experiments/lb_poll/ledger.md` is in `git status` again. |
| I407 / I408 | Round-36 staleness; the timer inventory | `round36/*` | I407 resolved (C1 / C4 closed). I408 superseded by the round-37 inventory (sources above). |
| I352-I399 (rest), I338-I348, I329/I330, I334-I337, I316-I326, I303-I313, I287-I302, I278, I72, I116, I145 | Unchanged older insights | `_curation/36/watch.json` ... `_curation/27/watch.json` | - |
