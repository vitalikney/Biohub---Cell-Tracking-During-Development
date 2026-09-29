# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-29 ~08:40 UTC (curation 36). This updates the curation-35 build of 29 Sep ~07:40Z, which is committed in 332ace7 with a structured copy in `research/KNOWLEDGE/_curation/35/watch.json`. Older predecessors run from `_curation/34/watch.json` down to `_curation/18/watch.json`. Rows not repeated here are unchanged there.

**Sources read for this update:**
- **`CONTEXT.md`:** 4,461 lines; `## 9. Literature` starts at l.4441. Six new entries since curation 35:
  - l.4381-4393 (**07:46Z, ROUND 35**): logs R35-A1..A3 and R35-A5 as procedures;
  - l.4394-4403 (**07:59Z, READ probe 54**): exp89p = **0.956**, so P is '-' and A-M1 is UNUSED. SEC is removed from the morning files, and the C11 record is logged;
  - l.4404-4414 (**08:19Z, A-M2 RULE (a)**, the user's choice): send exp89s if exp89r is COMPLETE and >= 0.958 (L_hi <= 10.2 h), or >= 0.959 (L_hi <= 10.75 h);
  - l.4415-4425 (**08:23Z**): exp89t (K + DIS 2.25 + CI) is built and its dummy was pushed at 08:22:49Z;
  - l.4426-4432 (**08:27Z, USER**): "отправляй exp89t". It goes into free slot 1 at dummy PASS;
  - l.4433-4440 (**08:28Z, USER: SLOT 2 HELD UNTIL 15:00 MSK = 12:00Z**): exp89s is **not** sent automatically. The slot-2 decision moves to ~11:55-12:00Z.
- **`git log`:** 332ace7 (round 35), ce88ccf (probe 54), 2fdf387 (rule (a)), 096d533 (exp89t built), 6a3f778 (user yes), 785be93 (slot 2 held; 08:28Z). `git status`: `?? research/wf_ideas_v4/round36/`, `?? experiments/discussions/744273.md, 744278.md, digest_20260929T0828Z.md`, `M experiments/lb_poll/ledger.md`.
- **`research/wf_ideas_v4/round36/`** (untracked, 08:13-08:33Z): `REPORT.md` (present this time), `report.json` (**R36-A1..A5**), `report.notes.md`, and all `scan_*` and `v_*` notes. **The round-36 report read CONTEXT only up to l.4425 (08:23Z)** (`round36/report.notes.md` 08:27Z). It did not see the 08:27Z user yes or the 08:28Z slot-2 hold; see C1 / C4 below.
- **`experiments/lb_poll/poll.log`:** newest header **08:28:19Z** (l.29600): exp89p 56657612 COMPLETE 0.956; exp89r 56656147 and exp75 56656157 PENDING; exp87a 56640366 0.959.
- **Loops:**
  - `experiments/e10_watch/watch_loop.log`: RUN 43 at 07:42:05Z (8/8, CHANGES=14, signals 0); next run 08:41:53Z.
  - `experiments/discussions/feed_loop.log`: 08:28:33Z FEED SIGNAL, 2 new topics (744273, 744278), E10 FLAG none. The best public notebook is still 0.953 (`digest_20260929T0828Z.md`).
- **Local read-only checks at ~08:36Z:**
  - Battery: BatteryStatus 2 (AC), 79%.
  - Processes alive: lb_poll 37016, e10 18040, feed 10924; watchers 1760 (exp89r) and 17532 (exp75); save jobs 8368 (post_exp75) and 17300 (post_exp89r); watchdog 28052. The post_exp89p job 27192 has exited, which is expected because exp89p did not read 0.959 (`CONTEXT.md` l.4398).
  - `grep -c` on CONTEXT.md returns 0 for: R36, CLARIFY, 744273, int-casting, "cron defect", DET_THRESHOLD, I-045, BH-0005, "UNUSED by rule". It returns 5 for R35 and 1 for Kai-Gowers.
  - `experiments/RESULTS.md` probe rows still end at probe 46 (l.79); last commit 59e14e2 (28 Sep 05:03Z).
  - Timers (per `round36/scan_plancheck.notes.md`): 08:30 (pid 13740, stale CI-M1 text), 09:13, 10:13, 11:10 (17304), 12:03, hourly 13:13-18:13, 18:37, 19:43, 21:05, and 30 Sep 00:07Z. **There is no 11:55Z timer** (`grep 11:55 CONTEXT.md` hits only l.4435 / l.4439).

All times are UTC; the user thinks in MSK = UTC+3 (`CONTEXT.md` l.3683-3687). IDs are stable: W = action, T = time-bound reminder, I = insight, C = contradiction. Status values: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at ~08:40Z, 29 Sep:**
- **Best display 0.959**, exp87a (probe 51); V_pub = exp87a (`CONTEXT.md` l.4278-4285).
- **Rank** at 08:13:59Z: **#139** of 3,987, 16th of 20 in the 0.959 block (ranks 124-143). 123 teams are at >= 0.960 (+4 since 07:14Z). SubmissionCount 54 (`round36/report.json` new_facts (2)).
- **Medal lines unchanged:** silver #199 (0.957 block), bronze #398 (0.955 block).
- **Night reads:**
  - exp89p read **0.956** (P '-', `CONTEXT.md` l.4394);
  - exp75 is PENDING, window ~09:05-10:05Z;
  - exp89r is PENDING, window ~09:23-09:34Z, latest the 11:00Z header.
- **Slots:** 3 used today, 2 left.
  - **Slot 1 = exp89t**: user yes at 08:27Z; sent at dummy PASS.
  - **Slot 2 is held** until the decision at 11:55-12:00Z (`CONTEXT.md` l.4426-4440).
- **User:** awake, laptop on AC. The session never ticks.

**Changes since ~07:40Z (curation 35):**
- **Done:**
  - **T151 A-M1**: UNUSED, because P is '-' (0.956) (l.4394-4403);
  - **W315**: P was on time (L_hi 7.19 h < 8.0 h);
  - **W317 (b)**: the C11 record at l.4400-4402 does not say "OVERTURNED";
  - **W323 / W324 / W325 / W327**: logged as procedures in the 07:46Z entry (l.4381-4393);
  - round 35 committed (332ace7).
- **Moot:**
  - **T201 / T203 / W328**: A-M1 did not fire; exp89p was not 0.959, so no UP test was needed (l.4398);
  - **W302 (4)**: the user has since engaged directly and approved exp89t, and exp89u stays off;
  - **W279 (1)**: the morning slots are now user-directed.
- **Superseded:**
  - **T151 A-M2 / T184** (the 02:53Z function): replaced by rule (a) (08:19Z), which is itself amended by the 08:28Z hold;
  - **T192 / T200** (E10 cut-offs 09:30Z / 10:00Z): for slot 2 only, the user's 08:28Z hold now allows a >= 0.960 non-CI candidate until 12:00Z.
- **New:** actions **W329-W337** (R36-A1..A5 plus 4 gaps found by this curation); reminders **T206-T212**; contradictions **C1-C6**; insights **I400-I408**.

---

## OVERDUE / DUE NOW

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W331** (new; = **R36-A3**) | Log only, 0 Kaggle calls: "08:30Z: A-M1 UNUSED (P '-' 0.956 at 07:58:14Z); no manual 08:40Z list; exp89l not submitted. exp89t (slot-1 reuse) is outside MORNING TABLE v1.1 and outside this timer; the 08:45Z cutoff neither applies to nor triggers it." Do not start the 08:40Z waiter. Optional: the 744273 line (W337) | **overdue**: the 08:30Z timer (pid 13740) has passed; `grep -c 744273` = 0 and no 08:30Z line after l.4440 | 08:30Z (passed) | `round36/report.json` R36-A3; `round36/scan_plancheck.notes.md` (timer 13740 "stale M1 text") |
| **W330** (new; = **R36-A2**) | **ONE pre-score CLARIFY line**, stamped with the current poll header: <br>- **(i)** SEC files stay in the V_pub pool (Q3, card l.27). The 07:59Z sentence "SEC files ... cannot be V_pub unless another file beats 0.959" means only that a SEC file must beat the running champion; <br>- **(ii)** in rule (a) and card step 9, "champion exp87a" reads as "running champion"; <br>- **(iii)** optional ORDER (1) SEC exception: a later SEC-free file that ties a SEC champion replaces it; <br>- **(iv)** exp89t has 4 levers | **not started** (`grep -c CLARIFY` = 0) | **before exp89r's first terminal header**: earliest ~09:23Z, latest the 11:00Z header | `round36/report.json` R36-A2, plan_issues (a)-(c); `CONTEXT.md` l.4402-4403 |
| W126 (part 2) | Add RESULTS.md rows for probes **47 (0.955), 48 (0.957), 49 (0.955), 50 (0.958), 51 (0.959), 54 (exp89p 0.956, SEC '-')**, then 52 / 53 (exp89r / exp75) and 55 / 56 (exp89t / slot 2) | **overdue**: probe rows still end at 46 (l.79); last commit 59e14e2 | before the finals card (12:03Z) | `experiments/RESULTS.md` l.79; `experiments/lb_poll/poll.log` l.29600 |
| W296 + W303 (updated) | REPORT.md for **rounds 29-35**, copied verbatim from `report_md_ru`. Round 36 has its own REPORT.md, still untracked. Commit round 36 with named paths, as the user, with no Co-Authored-By | round 35 committed without REPORT.md (332ace7); round 36 untracked | with the next CONTEXT commit | `git status`; `memory/feedback-git-no-coauthor.md` |
| W286 (downgraded) | **(1)** CONTEXT line that floatout probes 32/33 were no-ops under an int-casting scorer. **(2)** `e10v3/runbook.notes.md` l.66 still reads "OUR = 0.957 ... SC >= 0.958" | overdue, but **low**: the loop's own trigger text already says "0.959 ... so >= 0.960" (`experiments/lb_poll/e10_watch_loop.py` l.78), so l.66 is a stale doc, not a live threshold | low | `research/wf_ideas_v4/e10v3/runbook.notes.md` l.66; `e10_watch_loop.py` l.78 |
| W297 / W202 + W244 / W176 / W177 / W182 / I208 / W57 / W66 / W31 / W72 / W150 | cron-defect line; old info and curator lines; ROUND RECORD; LESSONS H1; old text fixes | overdue, low | H2, 29 Sep 23:00Z | `_curation/35/watch.json`, `_curation/26/watch.json` |

## CONTRADICTIONS TO RESOLVE BEFORE THEY FIRE

| ID | Conflict | Which text wins | Evidence |
|---|---|---|---|
| **C1** | **R36-A4 (1)** says: at exp89r's header, if rule (a) holds, "nb_try exp89s ... at once, cutoff 11:30Z". The **user's 08:28Z hold** says exp89s is **NOT** sent automatically, and slot 2 is decided at ~11:55-12:00Z | **The user's 08:28Z line** (later, and the user's own words). At exp89r's read, only **log** the rule (a) condition result (the slot-2 candidate (1) flag), the DIS estimate, the B25 line and any UP test. **Send nothing** | `CONTEXT.md` l.4433-4440; `round36/report.json` R36-A4; `round36/report.notes.md` (read to l.4425 only) |
| **C2** | The **11:10Z timer** (pid 17304) carries the old A-M2 text ("latest the 11:00Z header, submit by 11:30Z") | Timer texts are pointers only (R32-A3, `CONTEXT.md` l.4322). At 11:10Z: no submit; re-read l.4433-4440 | `round36/scan_plancheck.notes.md`; `CONTEXT.md` l.4322 |
| **C3** | `CONTEXT.md` l.3685: "non-CI submitted by ~11:30 UTC ... **No separate midday slot**" and "every final must read by ~19:30 UTC". Slot 2 at 12:00Z, sent as exp89s (L 7.01-7.81 h), reads **~19:01-19:49Z** | The user's 08:28Z hold (it states the ~19:05-19:15Z read). The **tick margin shrinks** to 11-59 min, and T161 "any read after ~19:30Z cannot be a final" can then bite. Covered by W335 | `CONTEXT.md` l.3683-3687, l.4438-4439; ledger exp85a (7.01, 7.19] h, exp70q (7.64, 7.81] h (`round36/report.notes.md`) |
| **C4** | **R36-A1** asks the user whether and when to send exp89t (options (1) ungated / (2) gated / (3) no). The user already said "отправляй exp89t" at **08:27Z**, before the report was written (08:33Z) | R36-A1 is **answered**: a plain yes = option (1), per the report's own text. **Do not re-ask.** Optional: tell the user the MC numbers in the next message (I402) | `CONTEXT.md` l.4426-4432; `round36/report.json` R36-A1 |
| **C5** | **R36-A5 (b)** would replace card l.59 with "слот A-M2: exp89s, если exp89r ≥ 0.958 (правило (a))". That text is stale after the 08:28Z hold | The filled card must state the **actual 12:00Z slot-2 outcome**: exp89s sent at HH:MM with a PENDING line, a different candidate, or UNUSED | `research/wf_ideas_v4/round29/finals_card_v5_ru.md` l.59; `CONTEXT.md` l.4433-4440 |
| **C6** | **R8** (`CONTEXT.md` l.1671): "after 29.09 02:00 only an emergency repeat (hard edge 10:00)". exp89t (built 08:23Z) and slot 2 at 12:00Z are both outside R8 | **The user's explicit instructions** (08:27Z, 08:28Z) override the pre-registration. Log one line saying so, for honest post-deadline lessons (W336) | `CONTEXT.md` l.1671, l.4426-4440 |

## NEXT 24 H (29 Sep ~08:40Z -> 23:59Z)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| **T206 + W329** (new; = **R36-A1** as answered) | exp89t **dummy gate ~08:55-09:05Z**; submit at PASS, **no later than ~09:30Z** (CI rule, l.3685) | Gate R22-A1 against the exp87a dummy CSV **db3faf078781**: <br>- nodes within +-1.5% of 122,328; <br>- COORDINJECT 4/4, replaced 0.90-0.93; <br>- change 0.60-0.69; <br>- integer z/y/x; 0 errors; RULE v2.1 runtime. <br>Guards: G1 header < 15 min; G2 used_today = 3 and token exp89t absent; G3 ft-weights; G5 COMPLETE. <br>`-m 'probe 55: exp89t = exp70g (cap 6) + ILP_DIVISION_WEIGHT 0.4 + READMIT_MIN_SCORE 0.94 + ILP_DISAPPEARANCE_WEIGHT 2.25 + coordinject ALPHA 0.5 MAX_UM 3.0 (K + DIS + CI; best + DIS)'`. <br>If the gate FAILS: no submit, push the user | **in progress** (user yes 08:27Z; dummy pushed 08:22:49Z) | `CONTEXT.md` l.4415-4432; `experiments/exp89t_k2cap6_k_dis225_ci/probe.json` |
| W316 (for exp89t) | right after the exp89t submit | Arm the R33-A3 late-read watcher `post_exp89t` (`timeout 180 python tools/uptest.py save post_exp89t`). S0 = `post_exp89s` if count-matched, otherwise the newest count-matched save. Budget <= 3 | not started | `round36/report.json` R36-A4 (5); `CONTEXT.md` l.4336-4342 |
| **T207** | **08:41:53Z** e10 RUN 44, then 09:41, 10:41 and the last at **11:41Z**; loop exits 12:00Z | Rank / block snapshot; free S0 / S1 for UP tests | pending | `experiments/e10_watch/watch_loop.log` (RUN 43 07:42:05Z) |
| T100 | feed every 90 min: next ~**09:58Z**, then ~11:28Z, and on until 23:59Z | E10 v3 trigger >= 0.960 (loop text `e10_watch_loop.py` l.78). The best public notebook is 0.953 (digest 0828Z). **For slot 2 only**, the user's hold allows a >= 0.960 **non-CI** candidate until 12:00Z (T210) | live, null | `experiments/discussions/digest_20260929T0828Z.md`; `CONTEXT.md` l.4436-4438 |
| **T212** (= T202 continued) | **09:13Z** round 37 (12:13 MSK), then hourly at hh:13Z | READS-vs-CARD lens, light (R35-A5). Check: <br>- W330 / W331 are logged before exp89r's header; <br>- the exp89t gate result and submit; <br>- exp75 / exp89r reads are coded per rule (a) **and the 08:28Z hold (C1)**. <br>**Rebase the round-36 items on l.4426-4440** | pending | `round36/report.json` next_focus |
| T159 / T182 (exp75) | **~09:05-10:05Z** | exp75 vs #37 0.954. **EXP75 PARTNER RULE v2 (b)**: with a CI V_pub it becomes П2 only at >= 0.955 and clean, and only as a trade. GAP RULE v2 (5) applies. exp75 cannot become V_pub. S0 for exp89r = `post_exp75` (job 8368) | pending | `round36/report.json` R36-A4 (6); `CONTEXT.md` l.4351-4360 |
| T159 / T182 (exp89r) + **W332** (new; = **R36-A4** amended by C1) + W325 + W323 | **~09:23-09:34Z**, latest the 11:00Z header | **The read line logs:** <br>- display and L (ledger); <br>- whether **rule (a)'s condition** holds: COMPLETE, no ERROR, >= 0.958 with L_hi <= 10.2 h, or >= 0.959 with L_hi <= 10.75 h. This is **only the slot-2 candidate (1) flag**, with no submit (08:28Z); <br>- DIS estimate = d_R - 0.959 + 0.002 (+-0.002 rounding); <br>- the B25 side line (R35-A3); <br>- at 0.959, the UP test with S0 = `post_exp75` and S1 = `post_exp89r`, plus one `_b` re-save if the LB lagged; <br>- V_pub coding under W330 (i)/(iii). A >= 0.960 read makes exp89r V_pub (CI, SEC) | pending | `CONTEXT.md` l.4404-4414, l.4433-4440; `round36/report.json` R36-A4; `round35/report.json` R35-A1/A3 |
| T195 | 09:13-10:13Z | No timer in this gap; exp75 and exp89r land in it. Watchers 1760 / 17532 and save jobs 8368 / 17300 are alive (08:36Z) | guarded | Win32_Process 08:36Z |
| **T210** (new) | a slot-2 E10 candidate must be **first seen by ~11:15Z** | A >= 0.960 **non-CI** public notebook copy needs a build, a dummy (35-40 min) and the W317 (c) validator gate before 12:00Z. The last feed before then is ~11:28Z and the last E10 run is 11:41Z, so a sighting at those runs is information only. The session proposes it; the user decides | watch | `round36/scan_recheck.notes.md` ("build+dummy 35-40 min"); `CONTEXT.md` l.4436-4438 |
| C2 / T184 | **11:10Z** timer (14:10 MSK) | Pointer only: **no submit**. Re-read l.4433-4440. Optional pre-draft of the 11:55Z message | pending | `round36/scan_plancheck.notes.md` |
| **T209 + W334** (new; **forgotten: no timer**) | **~11:50-11:55Z** ask the user (14:50-14:55 MSK); **decision by 12:00Z** (15:00 MSK) | **Slot-2 message with a recommendation.** Candidates: <br>- **(1)** exp89s (K + DIS, non-CI; v1 dummy PASS 14:40Z 28 Sep, CSV 8956f46c6824) if rule (a)'s condition held at exp89r's read; <br>- **(2)** a >= 0.960 non-CI E10 candidate. <br>No answer by 12:00Z -> apply (1), otherwise UNUSED. `nb_try exp89s,exp89q $KS "$M56S"` (probe 56 is then the correct number, I406). Guards G1 / G2 (used_today = 4) / G3 / G5. **The timer list has 11:10Z and 12:03Z but no 11:55Z**: arm a one-shot timer at 11:50Z or fold the ask into the 11:10Z step | **not started** | `CONTEXT.md` l.4433-4440; `round36/scan_plancheck.notes.md` (timer list) |
| **W335** (new) | at the exp89s submit (~12:00Z) | Arm the `post_exp89s` late-read watcher **with an immediate MSK push to the user at the terminal header** (read ~19:01-19:49Z; C3). Log the PENDING line with the actual submit time (+6.87..7.81 h). S0 for exp89s = the 11:41Z e10 snapshot if its count is S1 - 1, otherwise one `timeout 180 python tools/uptest.py save pre_exp89s` at submit + 6.7 h | not started | `round36/report.json` R36-A4 (4)(5); `CONTEXT.md` l.3685 |
| W266 (2) / T60 / W302 (1)(3) / W307 / W311 (c) / W320 / W324 + **W333** (new; = **R36-A5** amended by C5) | **12:03Z** (15:03 MSK) fill; re-check **18:37Z** and 19:43Z | Fill card v5 `round29/finals_card_v5_ru.md` (**sha8 a134d5e4**; edit the FILLED copy only). <br>**R35-A2 deletions for a CI V_pub:** the l.39 sentence, all of l.48, all of l.54; the 'П1' count between the ===== lines must be 0; the l.45 neighbour is exp85a 56629533. <br>**R36-A5 additions:** <br>- **(a)** the token 'exp89t = ': CI yes, SEC no, 4 levers, window +9.27..9.48 h (tail 10.9 h; after 23:00 MSK it is not a final); add it to step 5 and the V_CI list (l.129); <br>- **(b)** l.59: state the **actual 12:00Z slot-2 outcome** (C5); <br>- **(c)** SEC_READ = "«−»: exp89p 56657612 = 0.956 против exp85a 0.958". DIS_READ is indirect via exp89r until exp89s reads; <br>- **(d)** PENDING lines in MSK, including "**if V_pub = exp89s and exp75 ≤ 0.953, the finals carry no CI**" (I405). <br>**Other rules:** no mc34_* numbers; never "рекомендую"; never tick. SELECTED is expected to be {#37, #38}, so the user must re-tick | pending | `round36/report.json` R36-A5; `round35/report.json` R35-A2 |
| W330 (iii) fallback | 12:03Z / 18:37Z | If the ORDER (1) exception was not logged: under a SEC V_pub, add an info line naming the tying SEC-free file, the SEC LB read -0.002, and the pair it unlocks | conditional | `round36/report.json` R36-A2 |
| W336 (new) + W337 (new) | with the next CONTEXT entry; low | **W336:** one line saying that the user's 08:27Z / 08:28Z instructions override R8's 10:00Z edge and l.3685's "no midday slot" (C3 / C6). **W337:** a 744273 line: "an edge-only post-proc tweak A/B-d twice on public came back flat; external null replication of our edge-filter closure (probes 29/30); no values" (I404) | not started | `CONTEXT.md` l.1671, l.3685; `experiments/discussions/744273.md` |
| W19 / W73 / W102 / W93 / W165b / W261 | standing | ONE poller; header < 15 min old; never resubmit class-C or ERRORed files; SEC final only as V_pub (Q3); every Kaggle call wrapped in a timeout (`uptest.py save` always under `timeout 180`, T196) | standing | `CONTEXT.md` l.3331-3335, l.3692-3703, l.4112-4114 |
| W308 | any free moment; post-deadline OK | Curator note on I-045: "WEAKENED on public by CI; stays closed" | not started (`grep -c I-045` = 0) | `round31/report.json` R31-A5 |
| T199 (info) | on a feed signal | **744250** (time of publishing private results): still no host answer at ~08:20Z | watch | `round36/scan_browser.notes.md` |

## LATER (29 Sep ~12:00Z -> 23:59Z, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| **T208** (new) | exp89t read **~18:16-18:35Z** if submitted ~09:00-09:05Z (L 9.27-9.48 h; tail 10.9 h -> ~19:59Z) | The typical read ends **~2 min before the 18:37Z card re-check**. If exp89t is still PENDING at 18:37Z, re-fill at its terminal header. **'+' = >= 0.960 = new V_pub (CI)**; 0.959 needs an attributable UP over exp87a | `CONTEXT.md` l.4418-4421; `round36/report.notes.md` (timing) |
| **T211** (new) + W335 | exp89s read **~19:01-19:49Z** if it was sent at ~12:00Z | Push the user at once; re-tick before 20:00Z. exp89s is read against exp85a 0.958: '+' >= 0.959 is a clean DIS read. It becomes V_pub only at >= 0.960, or at 0.959 with an attributable UP over the running champion | `CONTEXT.md` l.4410-4414, l.4438-4439 |
| T152 + W302 (2) + W307 (5) + W320 + W324 + W333 | **18:37Z** (21:37 MSK), timer | FINAL proposal from card v5: "the pair by the card", **never "рекомендую"**. Re-check the edits against the then-current V_pub (exp87a, or exp89r / exp89t / exp89s if one of them won). If V_pub changed, re-run `scratchpad/r31v/mc31v.py` (standing prior) | `round31/report.json` R31-A4 (5); `round36/report.json` R36-A5 |
| T161 | **19:43Z** (22:43 MSK), timer | Notify-only reminder plus a V_pub re-check. After the 08:28Z hold, exp89s may read as late as ~19:49Z (C3). This timer is the last scheduled look before the tick | `CONTEXT.md` l.3685, l.4054-4056 |
| T10 | **20:00Z (23:00 MSK)**; the 12:00Z reminder is built into the 12:03Z card fill | **The user ticks the finals.** The session never ticks. If the user does nothing, #37 + #38 stay | `CONTEXT.md` l.3851-3855, l.4091-4092 |
| T153 | ~20:00-20:30Z | Verify that the API SELECTED set matches the user's pair | `CONTEXT.md` l.3474 |
| T162 | **21:05Z** (00:05 MSK 30 Sep), timer | Last-call notify on a SELECTED mismatch | `CONTEXT.md` l.4092, l.4099 |
| W177 H2 / T49 | 23:00Z / 23:00-23:45Z | LESSONS H2; final public LB snapshot | `_curation/20/watch.json`; `CONTEXT.md` l.2619 |
| T11 / T163 | **29 Sep 23:59Z** (02:59 MSK 30 Sep) | Deadline: a submission must **finish** before it; re-ticks are allowed until then. Overview ~08:18Z: "16 HOURS TO GO" | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/overview; `round36/scan_browser.notes.md` |
| T155 | 30 Sep 00:07Z, timer (armed) | POST-DEADLINE job: private read v2 + L1-L7 | `CONTEXT.md` l.3714-3715, l.4131 |
| W317 (a)(c)(d) / W321 / W326 / W312 / W295 / W29 | next curation / post-deadline | BH-0005 alias; the E10 validator env; full-tree external scans; Charannoo divrelax; Kai-Gowers negatives (the K replication is logged at l.4384-4385; the readmission negatives are not); division agenda; 744093; z-shift I-029; MAX_UM 2.0 | `round33`-`round35/report.json`; `CONTEXT.md` l.4384-4385 |
| T133 / T170 | 3 Oct | GPU quota refresh (about 2.7 h left) | `CONTEXT.md` l.4239-4241 |

**Passed or finished time-bound items:**
- **Earlier deadlines:** R8 new-mechanism cutoff (27 Sep 12:00Z) passed; the 28 Sep 12:00Z consolidation superseded (T46); the E10 02:00Z cutoff (T172) passed.
- **Overnight 28-29 Sep:** as in curation 35.
- **This morning:**
  - W322 (06:09Z); W319 (06:20Z); T198 (06:42Z); T151 prep (07:23Z); round 35 (07:46Z);
  - **probe 54 read 07:58:14Z → A-M1 UNUSED** (07:59Z);
  - rule (a) (08:19Z); exp89t build (08:23Z); the user's yes (08:27Z); slot 2 held (08:28Z).
- **Friend replies:** none awaited (`CONTEXT.md` l.2175-2176).
- **Standing notes:**
  - **T156:** the tick is at 20:00 UTC = 23:00 MSK. Never write "20:00" without "UTC".
  - **T196:** always run `uptest.py save` under `timeout 180`.
  - **T197:** the timer schedule is in the source header; there is no 11:55Z timer (W334).
  - **T204:** the poller drifts +2 s per 10 min.
  - **T205:** LB `LastSubmissionDate` = the max submit time among SCORED files.

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I400** (new) | "SEC x CI interaction in the lab: SEC costs -0.0016 on K but -0.0012 on the CI base ... branch-A dd ... biased UP by ~+0.0004 ... a d_R = 0.959 (dd +0.002) is explainable by interaction + rounding, not DIS" | `round36/scan_recheck.notes.md` | Rule (a) treats exp89r >= 0.958 as "DIS estimate >= +0.001". The report did not adopt this, because the lab is 0/2 on CI. It is still worth one sentence in the 11:55Z slot-2 message, so the user knows that a 0.958 read is weak DIS evidence. |
| **I401** (new) | "P(89s wins given d_R) .955 .001-.006 / .956 .02-.04 / .957 .10-.15 / .958 .29-.38 / .959 .57-.66 / >=.960 .83-.90 ... Gate d_R >= 0.958 captures 77-84% of all exp89s wins" | `round36/scan_hyp_readscard.notes.md` | These are the numbers the 11:55Z slot-2 recommendation needs (T209). They appear nowhere in CONTEXT. |
| **I402** (new) | exp89t: "UNGATED: P(exp89t >= 0.960) 0.32-0.37 ... GIVEN exp89r <= 0.957: P(>= 0.960) 0.09-0.11; E[DIS given switch] only +0.0004 ... private effect ~0" | `round36/report.json` R36-A1; `round36/report.notes.md` 08:31Z | The user approved exp89t (08:27Z) before this MC existed (08:33Z). It is information only (C4), but it sets expectations: about a 1/3 chance of a new V_pub. |
| **I403** (new) | "DUMMY-LAB SIGN RECORD ... MISSED cap 4 -> 6 (lab 0.0000, LB +0.002) ... 0/2 on CI ... not a sign instrument for division or coordinate levers, and not for exp75 / exp89t" | `round36/report.json` new_facts (6) | Do not quote a lab prediction for exp89t or exp75 on the card or to the user. R36-RC-A's "3 of 3" claim was cherry-picked and rejected. |
| **I404** (new) | 744273 (sghwr): "we A/B'd the same edge-only post-processing tweak twice on the public LB after it looked like a solid win offline, and both times it came back flat"; "division-Jaccard ... swings a lot on just one or two forks" | `experiments/discussions/744273.md`; https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744273 | An external null replication of our edge-filter closure (probes 29/30; `memory/project-edge-filter-finding.md`). The fork-luck point bears on reading 0.001 display gaps. It is not in CONTEXT (W337). |
| **I405** (new) | "if V_pub = exp89s and exp75 <= 0.953, the finals carry no CI" | `round36/report.json` R36-A5 (d); `round36/REPORT.md` step 5 | This scenario appears only in the round-36 report. The card must warn the user (W333 (d)). |
| **I406** (new) | "M56S text says 'probe 56'; if exp89s goes as the 4th submit today it is probe 55" | `round36/scan_plancheck.notes.md` | Resolved by ordering: exp89t is probe 55, so exp89s at 12:00Z is correctly probe 56. If exp89t is not sent (gate FAIL), exp89s's -m must say 55. |
| **I407** (new) | "08:27Z CONTEXT read to l.4425 (last entry 08:23Z exp89t built ...)" | `round36/report.notes.md` | Round 36 is stale on two points: the user's yes and the slot-2 hold. R36-A1 / A4 (1) / A5 (b) must be rebased (C1 / C4 / C5) before round 37 or the session acts on them. |
| **I408** (new) | "timers 08:30 (13740, stale M1 text), 09:13, 10:13, 11:10 (17304), 12:03, 13:13-18:13, 18:37, 19:43, 21:05, 30 Sep 00:07" | `round36/scan_plancheck.notes.md` | This is the only live timer inventory. It shows the missing 11:55Z slot-2 ask (W334). |
| I391 | Card l.54 "exp75 = 0.954 и чистый: П1 и П3 почти равны": with a CI V_pub, exp75 at 0.954 is no partner | `round35/report.notes.md` | Now logged as R35-A2 (l.4389-4392). Still live for the 12:03Z fill. |
| I392 | `uptest compare` prints counts but does not enforce them; the `_b` re-save is the only guard against a +0 LB lag | `round35/report.json` R35-A1 | Logged (l.4386-4388). Live at any 0.959 read (exp89r, exp89t, exp89s). |
| I394 / I395 | Kai-Gowers readmission negatives (0.955 / 0.954); the single-process 27000 s degrade costs -0.021 LB | `round35/scan_hyp_external35.notes.md` | Only the K replication reached CONTEXT (l.4384-4385). The negatives and the runtime penalty are post-deadline lessons (W326). |
| I384 / I385 / I386 | No mc34_* number on the card; P2 {exp87a, exp75} beats P3 on bronze in 9-10 of 13 runs; exp89u stays off | `round34/*` | Still live for the card and the finals (W324 / W333). |
| I393 / I396 / I397 / I398 / I399 | The 3 teams passing us are all at 0.960; the round-prompt Chrome contradiction; the x138 author is at 0.958 and silent; the exp89l coord-inject guard gap (moot now); the GAP_CLOSE_MAX_GAP 2 no-op | `_curation/35/watch.json` | Unchanged; I398 is moot (exp89l not sent). |
| I356 (repeated) | `tools/runtime_ledger.py --print` also rewrites `experiments/lb_poll/ledger.md` | `round32/scan_plancheck.notes.md` | `M experiments/lb_poll/ledger.md` is still in `git status`. |
| I352-I390, I338-I348, I329/I330, I334-I337, I316-I326, I303-I313, I287-I302, I278, I72, I116, I145 | Unchanged older insights | `_curation/35/watch.json` ... `_curation/27/watch.json` | - |
