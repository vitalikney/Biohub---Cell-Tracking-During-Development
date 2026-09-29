# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-29 ~01:57 UTC (curation 30). This updates the curation-29 build of 28 Sep ~20:58Z. The full text of that build is in the git history of this file, and a structured copy is in `research/KNOWLEDGE/_curation/29/watch.json`. Older predecessors run from `_curation/28/watch.json` down to `_curation/18/watch.json`. Rows not repeated here are unchanged there. The TASK_LOCAL_SESSION, TASK_CLOUD_SESSION and v3 FINAL_REPORT rows have not changed since `_curation/20/watch.json`.

**Sources read for this update:**
- **`CONTEXT.md`:** it now has 4,293 lines, and `## 9. Literature` starts at l.4273. Entries new since curation 29:
  - l.4134-4152 (28 Sep 21:11Z): NIGHT TEXT POINTER + CARD v5 + A-M2 PRECEDENCE.
  - l.4153-4160 (21:45Z): READ, probe 51 = 0.959.
  - l.4161-4167 (21:45Z): exp89l BUILT + DUMMY.
  - l.4168-4173 (22:16Z): exp89l GATE PASS.
  - l.4174-4253 (23:34Z): **W4 FREEZE**.
  - l.4254-4264 (29 Sep 00:06Z): NIGHT BATCH, probes 52 + 53.
  - l.4265-4272 (00:47Z): NIGHT BATCH DONE, probe 54.
- **`git log`:** e42769c .. **afebb5d** (00:47Z). Round 29 is committed as 6dc7088; round 30 is untracked.
- **`research/wf_ideas_v4/round30/`:** untracked, written 01:13-01:45Z.
  - `report.json` holds **R30-A1..A5**, new_facts (1)-(9) and plan_issues (a)-(h).
  - Also read: `report.notes.md`, `scan_*` notes and `v_recheck_r30-rc-c*` notes.
  - **There is no `REPORT.md`**, because the harness blocked it (`round30/report.json` report_md_ru_note).
- **`experiments/lb_poll/poll.log`:** the newest header is **01:44:02Z** (l.27278). In it, 56656147, 56656157 and 56657612 are PENDING, and 56640366 is COMPLETE 0.959.
- **Loops:**
  - `experiments/e10_watch/watch_loop.log`: RUN 37 at 01:42:07Z, signals 0, next run 02:41:53Z.
  - `experiments/discussions/feed_loop.log`: 00:57:54Z, 0 new, E10 FLAG none.
- **Local read-only checks at ~01:50Z:**
  - sha8 of card v5 = aadead83, of `night_checklist.md` = 2b442e87, of the freeze template = dcdfeebc. All three equal the logged values, so **the R30-A1 card edits are not applied**.
  - `round27/finals_card_v4_ru.md` l.1 carries the SUPERSEDED banner.
  - `grep -c` on CONTEXT.md returns 0 for each of: "MORNING/FINALS TEXT RESOLUTIONS", "running champion", DET_THRESHOLD, int-casting.
  - `experiments/RESULTS.md` probe rows still end at probe 46 (l.79).
  - `research/wf_ideas_v4/e10v3/runbook.notes.md` l.66 still reads "OUR = 0.957 ... SC >= 0.958".
  - `round29/REPORT.md` and `round30/REPORT.md` are both absent.

All times are UTC; the user thinks in MSK, which is UTC+3 (`CONTEXT.md` l.3683-3687). IDs are stable: W is an action, T a time-bound reminder, I an insight. Status values are: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at ~01:57Z, 29 Sep:**
- **Best display: 0.959**, from exp87a (probe 51, 56640366), which is a CI file. V_pub = exp87a.
- **Rank** at 01:13Z: #132 of 3,979, 18th of 22 in the 0.959 block, with 114 teams at >= 0.960 (`round30/report.json` new_facts (2)).
- **Branch A.** STACK = exp89r (freeze l.4174-4253).
- **Night submissions, all PENDING at 01:44:02Z:**
  - 52 exp89r (56656147, 00:05:28Z) reads ~09:25-09:35Z. The 10.2 h mark is 10:17:28Z; the admit edge is 10:50:28Z.
  - 53 exp75 (56656157, 00:05:34Z) reads ~09:05-10:05Z.
  - 54 exp89p (56657612, 00:46:36Z) reads 07:38-08:35Z, expected ~07:47-07:58Z. Its 8.0 h gate is 08:46:36Z.
- **Slots:** 3 of 5 used on 29 Sep, **2 left** for the morning files (`CONTEXT.md` l.4265-4272).
- **Morning files:** exp89l PASS at 22:16Z (CSV 2c1868375972), exp89s PASS, exp89q PASS. All are v1, and nb_try hard-codes `-v 1` (`round30/report.json` new_facts (8)).
- **User:** asleep, autonomous mode (`CONTEXT.md` l.4081-4093). The session never ticks.
- **CRITICAL (new): three logged texts disagree in realistic morning cells, and this must be fixed PRE-SCORE (before exp89p is terminal, earliest 07:38Z). See W298 = R30-A1.**
  - P '0u' is now unreachable.
  - The tie order in card v5 l.21 contradicts R26-A4 (d).
  - The SEC/Rr collision cell is unresolved.
  - Sources: `round30/report.json` plan_issues (a)-(c).

**Changes since ~20:58Z (curation 29):**
- **Done:**
  - W289: the stored texts were fixed. The checklist is now 2b442e87 and the template dcdfeebc (l.4134-4140).
  - W290: the pointer entry (1)-(6) plus the v4 banner (l.4134-4152).
  - W291 / T165 / W283: 51 was read as '+', UP 12 (l.4153-4160). exp89l was built, dummied and gated PASS (l.4161-4173).
  - T143 / W284: the freeze was written at 23:34Z (l.4174-4253).
  - T20 / T107 / T167: the night batch ran 52/53 at 00:05Z and 54 at 00:46Z, with no fallback (l.4254-4272).
  - T126: the slot reset happened.
  - T177 / T178: no workflow round ran from 23:25Z to 00:50Z. Round 30 started at 01:13:48Z, after all three night files were listed (`round30/scan_browser.notes.md`).
  - W286 (3): KEY FACTS were updated in the 21:45Z read (l.4157-4160).
- **Resolved insights:** I338-I343, I345, I346 (details in the table below).
- **New:**
  - actions **W298-W303**;
  - reminders **T181-T186**;
  - insights **I349-I357**.

---

## OVERDUE / DUE NOW

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W298** (new; = **R30-A1**) | **ONE PRE-SCORE CONTEXT ENTRY + CARD v5 EDITS**, directly above `## 9. Literature`, NOT in the freeze header shape. The entry must quote a poll header that still shows the 3 night refs PENDING. <br>**(1) A-M1 trigger.** P '+' means display >= 0.959, COMPLETE, no ERROR, and terminal by the 08:40Z header; it sends exp89l. A 0.958 display is '0': the UP test is BLIND by construction, so there is no uptest call and A-M1 is UNUSED. This supersedes freeze (9)'s "V_pub stays exp85a". <br>**(2) Tie order (1) = R26-A4 (d), the running champion by completion order.** A later file replaces the champion only with an attributable UP. Otherwise the tie is broken by (2) non-CI, (3) fewer levers, (4) earlier submit. An UP earned at a lower display never counts. This replaces CONTEXT l.3181 and card v5 l.21. **Log exactly one reading:** the conservative alternative, "exp87a stays on a k = 0 tie", is also legitimate pre-score. <br>**(3) SEC/Rr collision.** In the cell (P 0.958, exp89r 0.960, DIS '?'), A-M2 is UNUSED. Otherwise 21:11Z (6) stands. <br>**(4) Wording:** "L_hi <= 7.9 h + 210 s x failed attempts"; "attributable UP". <br>**Card v5 edits:** l.21, l.59, step 5, l.106 (exp87a 0.959, L (9.30, 9.48], UP 12) and l.114 (exp89l CSV 2c1868375972). Record the new sha8 in the same entry | **not started**: card sha8 is still aadead83; the CONTEXT grep for the title and for "running champion" returns 0 at ~01:50Z | **NOW.** Ideally by the 07:23Z prep; the hard limit is before the first header where 56657612 is terminal (earliest 07:38Z = 10:38 MSK) | `round30/report.json` R30-A1, plan_issues (a)(b)(c)(h); `round30/scan_hyp_morning30.notes.md`; `CONTEXT.md` l.3181, l.4147-4150, l.4247 |
| W126 (part 2) | Add RESULTS.md rows for probes **47 (0.955), 48 (0.957), 49 (0.955), 50 (0.958) and 51 (0.959, UP 12)**, then the night probes 52-54 and the morning probes | **overdue**: probe rows end at 46 (`experiments/RESULTS.md` l.79) | before the finals card (29 Sep 12:03Z) | `CONTEXT.md` l.3530, l.3615, l.3639, l.3856, l.4153-4160 |
| **W296 + W303** (updated) | **(a) Round 29:** committed (6dc7088), but `round29/REPORT.md` is still absent. **(b) Round 30:** write `round30/REPORT.md` verbatim from `report.json` report_md_ru, because the harness blocked the write. Commit round 30 (untracked) with named paths, as the user, with no Co-Authored-By | (a) half done; (b) not started | with the next CONTEXT commit (the W298 entry) | `round30/report.json` report_md_ru_note; `git status` (`?? research/wf_ideas_v4/round30/`); `memory/feedback-git-no-coauthor.md` |
| W286 (updated) | **(1)** Add a CONTEXT line: floatout probes 32/33 were no-ops under an int-casting scorer. **(2)** Fix `e10v3/runbook.notes.md` l.66, which is now two steps stale: it should read "OUR = 0.959 (exp87a), so SC >= 0.960" (`CONTEXT.md` l.4159-4160 already says the trigger is >= 0.960). **(3)** KEY FACTS: done (l.4157-4160) | (1)(2) **overdue**: `grep int-casting` = 0; l.66 unchanged | (2) before the next E10 read (02:41Z); (1) low | `round28/report.json` R28-A6; `CONTEXT.md` l.4159-4160 |
| W279 (1) | Log RC-C: "DET_THRESHOLD stays closed for 29 Sep and is never a morning filler" | not started (`grep -c DET_THRESHOLD CONTEXT.md` = 0) | before **07:23Z** 29 Sep; fold it into W298 | `round27/report.json` R27-A9 (1) |
| W297 | CONTEXT l.4095-4096 still blames "a busy session / battery standby" for the lost rounds. The cause was the cron defect (round 28). Fold a one-line correction into W298 | not started: not in the 21:11Z entry | with W298; low | `round28/report.json` new_facts 5; `CONTEXT.md` l.4096, l.4127-4129 |
| W202 + W244 / W176 / W177 / W182 / I208 / W57 / W66 / W31 / W72 / W150 | Old info and curator lines; the ROUND RECORD; LESSONS H1; no NEVER_SUBMIT in exp70j/exp70k; old text fixes | overdue, low | H2, 29 Sep 23:00Z | `_curation/24/watch.json`, `_curation/26/watch.json` |

## NEXT 24 H (29 Sep ~02:00Z -> 23:59Z)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W298 | **now** | Pre-score resolutions entry + card v5 edits (above) | not started | R30-A1 |
| **T181** (new; = R30 next_focus (1)) | **02:13-06:17Z** hourly rounds 31-35 (05:13-09:17 MSK) | Keep them **SHORT and in-session, with no new mechanisms** (R8). **Step 0:** newest header, the 3 refs PENDING, AC status. Confirm W298 is logged. **At 03:13Z:** run the feed only if the digest is > 100 min old. An optional single INFO-only datasets call is allowed (I355). Aggressive mode acts only on a disclosed knob or an E10 notebook >= **0.960** | pending | `round30/report.json` next_focus (1); `CONTEXT.md` l.4151-4152 (checklist section 5 first) |
| T100 (updated) | E10 hourly at hh:41Z until **12:00Z**, when the loop exits (next 02:41Z). Feed every 90 min (next ~02:27Z) until 23:59Z | The E10 v3 trigger is now **>= 0.960** (l.4159-4160; runbook l.66 is stale, see W286 (2)). **Before 02:00Z:** build + dummy an E10 copy per the rule. **After 02:00Z:** it needs the user's yes | live (RUN 37 01:42Z; feed 00:57Z) | `experiments/e10_watch/watch_loop.log`; `round30/scan_plancheck.notes.md` (E10 loop ends 12:00Z) |
| T172 | **02:00Z** (05:00 MSK) | E10 cutoff: after it, any E10 copy needs the user's yes (dummy it, then ask) | standing | `CONTEXT.md` l.4089-4091 |
| T173 | **05:10-06:00Z** (08:10-09:00 MSK) | The user travels and the laptop sleeps. timer.sh fires on wake. **The watchdog (PID 10576) and the read watcher (13516) are one-shot** (I353) | info | `CONTEXT.md` l.4066-4072; `round30/report.notes.md` 01:36Z |
| T174 + **W301** (new; = **R30-A4**) | **06:07Z** post-wake (09:07 MSK) | Check AC, poll-header age and loops. **Re-arm the power/poll watchdog** as run_in_background once BatteryStatus = 2. Re-arm only dead waiters, never to fix their texts. After the first read, chain read watchers on the remaining refs `^(56656147\|56656157),.*(COMPLETE\|ERROR)`, then on the last ref, plus one per morning submit ref (W294) | pending | `round30/report.json` R30-A4 (a)(b), plan_issues (d) |
| **W302 (4)** (new; = R30-A5 (4)) | 06:07-07:23Z | First MSK message to the user: "Both morning slots (A-M1 by 11:45 MSK, A-M2 by 14:30 MSK) may end UNUSED by rule; that is expected. exp89t/exp89u stay off unless you say yes" | pending | `round30/report.json` R30-A5 (4) |
| **T151 + W299** (updated; = **R30-A2**) | **07:23Z** prep (10:23 MSK), timer | **Do NOT rebuild or re-push exp89l / exp89s / exp89q.** The timer text "build/dummy exp89l" is stale: a v2 would break nb_try's `-v 1`. Re-run G5 (3 status calls). Paste (a) the branch-A decision table, including the d_R = 0.960 / 0.961 grids, (b) the exact commands (KL, KS, M55L, M56S, M56Q) and (c) timing | pending | `round30/report.json` R30-A2, plan_issues (e); `round30/report.notes.md` 01:35-01:36Z |
| **T159 / T182** (updated) | **exp89p 07:38-08:35Z** (expected 07:47-07:58Z); exp75 ~09:05-10:05Z; exp89r ~09:25-09:35Z | **Night reads:** P = exp89p vs exp85a 0.958. Rr = exp89r vs exp87a 0.959. exp75 vs #37 0.954 (partner rule v2). DIS per R26-A2 (1) branch A. Apply the table at every header. Log each read line + KEY FACTS + RESULTS (W126) | pending (all PENDING at 01:44:02Z) | `CONTEXT.md` l.4254-4272; `round30/report.json` new_facts (1) |
| **W300** (new; = **R30-A3**) | at each terminal header, 07:38-11:00Z | **UP-test protocol.** <br>- **P at 0.958:** "0 (k = 0 by construction)", no call. <br>- **P at 0.959:** submit exp89l first, then `uptest.py save S1_P`. It is valid only with count 54 AND LastSubmissionDate 2026-09-29 00:46:36. Then run `compare S1_51 S1_P`. <br>- **exp89r:** test only on a top-display tie. An exp75 jump is exempt (R26-A4 (b)): log "count +2, exp75 exempt". <br>- **exp75:** no UP call. <br>- **Budget:** <= 3 LB calls. **An LB download never delays a submit** | pending | `round30/report.json` R30-A3, plan_issues (f) |
| T151 A-M1 / **T183** (new) | first header with 56657612 terminal; **latest 08:40Z header, submit by 08:45Z** (11:45 MSK) | **A-M1:** d_P >= 0.959 -> `nb_try exp89l $KL "$M55L"`. Anything else -> UNUSED. **The 08:30Z timer ("M1 CI DEADLINE CHECK") fires before the 08:40Z header:** if exp89p is still PENDING, wait for 08:40Z. Guards: G1 < 15 min; G2 used_today = 3; G3 ft-weights + n2a; G5. Exit codes: 2 -> UNUSED; 3 -> STOP + push; 1 -> retry every 10 min until the cutoff | pending | `round30/report.json` R30-A2 (a)(b)(c) |
| T151 A-M2 / **T184** (new) | first header with 56656147 terminal; **latest 11:00Z header, submit by 11:30Z** (14:30 MSK); 11:10Z timer | **A-M2:** <br>- **Rr '+':** needs d_R >= 0.960 and header + 210 s x f <= 10:50:28Z. A read after 10:17:28Z is flagged UNPROVEN-ins. <br>- **DIS '+':** send exp89s. <br>- **DIS '-':** UNUSED. <br>- **DIS '?':** send exp89q only if P is '+' or '?'. <br>A hidden-run ERROR of exp89r = Rr '?', not branch B. Nothing depends on exp75. The 11:10Z timer uses the 11:00Z header | pending | `round30/report.json` R30-A2 (a)(c) |
| **T185** (new) | 07:13-11:13Z hourly rounds | Keep them read-only or skip them, so that the session is free at the decision headers | pending | `round30/report.json` next_focus (4) |
| T180 / W294 | at each morning submit | Start a local late-read watcher per morning ref. The expected reads are: exp89l sent ~07:55Z reads ~17:13-17:25Z; sent at 08:45Z it reads ~18:03-18:15Z; an M2 file sent at 11:30Z reads ~18:30-18:42Z | pending | `round29/report.json` R29-A7; `round30/report.json` R30-A2 (c) |
| W19 / W73 / W102 / W93 / W165b / W261 | standing | ONE poller; header < 15 min old; never resubmit class C or ERRORed files. SEC may be a final only as V_pub (Q3). Dataset pre-push check | standing | `CONTEXT.md` l.3331-3335, l.3692-3703, l.4112-4114 |
| **T186** (new; = R30-A5 (1), R30-A4 (c)) | **11:41Z** last E10 snapshot; the E10 loop exits 12:00Z | Take RANK and block position for the 12:03Z card from the 11:41Z snapshot. After 12:00Z use one `uptest.py save` per need (<= 3). Do not restart the E10 loop | pending | `round30/report.json` R30-A4 (c), R30-A5 (1), rejected |
| W266 (2) / T60 / **W302 (1)(3)** | **12:03Z** (15:03 MSK), timer | Fill and send **card v5 with the new sha8 from W298**, not v4, whatever the timer text says. Add the two section-4 info lines: (i) silent private-only failure; (ii) deadline degrade (non-CI impossible, CI "probably absent, not proven"; never cite the 10.2 h mark). Send only the ===== block; never tick | pending | `round30/report.json` R30-A5 (1)(3); `CONTEXT.md` l.4142-4147 |

## LATER (29 Sep ~12:00Z -> 23:59Z, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T152 + W302 (2) | **18:37Z** (21:37 MSK), timer | FINAL proposal from card v5. Word it as "the pair by the card (P3/P1/P2 by the logged rules)" and **never "рекомендую"**, although the timer text says "recommended pair". List still-PENDING files with MSK windows (T180) | `CONTEXT.md` l.3714; `round30/report.json` R30-A5 (2), plan_issues (g) |
| T161 | **19:43Z** (22:43 MSK), timer | Notify-only reminder + V_pub re-check (same wording rule) | `CONTEXT.md` l.4054-4056, l.4092 |
| T10 | **20:00Z (23:00 MSK)** | **The user ticks the finals.** The session never ticks by any route. If the user does nothing, #37 + #38 stay (the API still shows SELECTED {#37, #38}, `round30/report.json` new_facts (4)) | `CONTEXT.md` l.3851-3855, l.4091-4092 |
| T153 | ~20:00-20:30Z | Verify that API SELECTED = the user's pair | `CONTEXT.md` l.3474 |
| T162 | **21:05Z** (00:05 MSK 30 Sep), timer | Last-call notify: if SELECTED is not the proposed pair, push the exact pair | `CONTEXT.md` l.4092, l.4099 |
| W177 H2 / T49 | 23:00Z / 23:00-23:45Z | LESSONS H2; final public LB snapshot | `_curation/20/watch.json`; `CONTEXT.md` l.2619 |
| T11 / T163 | **29 Sep 23:59Z** (02:59 MSK 30 Sep) | Deadline: a submit must **finish** before it; re-ticks are allowed until then | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765; `CONTEXT.md` l.3848, l.3855 |
| T155 | 30 Sep 00:07Z, timer | POST-DEADLINE job: private read v2 + L1-L7 | `CONTEXT.md` l.3714-3715, l.4131 |
| W295 | next CONTEXT entry / curation pass | The 744093 integer check covers every finals candidate. An I-320 narrow annotation. Do not publish the "5/14" class table | `round29/report.json` R29-A8 |
| T133 / T170 | 3 Oct | GPU quota refresh (about 2.7 h were left at 23:34Z; freeze (8)) | `CONTEXT.md` l.4239-4241 (freeze (8)) |
| W29 / curator | after 29 Sep | Post-deadline list, plus z-shift I-029 and the MAX_UM 2.0 note | `round25/report.json` R25-A8 (d); `round28/report.json` R28-A6 (1) |

**Passed or finished time-bound items:**
- **Earlier deadlines:**
  - The R8 new-mechanism cutoff (27 Sep 12:00Z) has passed.
  - The 28 Sep 12:00Z consolidation is superseded (T46; l.3392-3394).
  - No new lever reaches R8 (`round30/scan_hyp_morning30.notes.md`).
- **Overnight 28-29 Sep:**
  - The 51 read was at 21:43:19Z (l.4153).
  - The freeze was at 23:34Z (l.4174).
  - The slot reset was at 00:00Z.
  - The night batch ran 00:05-00:46Z (l.4254-4272).
  - The 00:20Z backup found nothing to do (l.4270-4271).
- **Friend replies:** none awaited. The last friend instruction was on 26 Sep (l.2175-2176).
- **T156:** the tick deadline is 20:00 UTC = 23:00 MSK. Never write "20:00" without "UTC".

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I349** (new) | "P '0u' is mechanically unreachable: LB shows max public over ALL submissions (SELECTED = #37/#38 yet LB 0.959); exp89p 0.958 < best 0.959 cannot move our row -> k = 0 by construction." Also: "SubmissionCount ... count and date move only on scoring" | `round30/scan_plancheck.notes.md` 01:20Z; `round30/scan_hyp_morning30.notes.md` | MORNING TABLE v1.1, R29-A6 and freeze (9) were all written when the row was 0.958. Until W298 (1) is logged, a 0.958 exp89p could be mis-coded as '0u' or "masked". |
| **I350** (new) | Card v5 tie order (1) "differ[s] when exp89p reads 0.959 with k=0 (literal card -> exp87a because it has UP 12; R26-A4 (d) -> unresolved -> (2) non-CI -> exp89p)". The pairwise fix "can cycle (exp89r > exp87a by UP, exp89l > exp89r by (3), exp87a > exp89l by (3))" | `round30/scan_plancheck.notes.md`; `round30/report.json` rejected | This decides the V_pub final. The only safe fix is the running-champion form, logged pre-score (W298 (2)). |
| **I351** (new) | "Conflict cell: P = 0.958 ('0') and exp89r = 0.960 -> dd = 0.001 -> DIS '?' ; Rr '+' -> exp89q carries a SEC that read '0'"; "only at (d_P 0.958, d_R 0.960)" | `round30/scan_plancheck.notes.md`; `round30/report.notes.md` 01:40Z | This is the modal P read. Resolve it on the merits, not by recency: freeze (9) is an INFO copy of R28-A4 (vi), which is older than 21:11Z (W298 (3)). |
| **I352** (new) | "nb_try (round29/night_checklist.md l.62) hard-codes '-v 1'"; the 07:23Z timer says "build/dummy exp89l" although it "PASSED at 22:16Z as v1" | `round30/scan_plancheck.notes.md`; `round30/report.json` R30-A2 | Obeying the stale timer text would create v2, and nb_try would then submit a version other than the gated one. Covered only by W299. |
| **I353** (new) | "Watchdog PIDs 10576/25988 'break' on first battery/stale alarm -> one-shot; will die at the 05:10Z battery sleep"; the read watcher "fires ONCE (first completion ...); nothing re-arms for exp75/exp89r" | `round30/scan_plancheck.notes.md` | Nothing would watch exp89r, whose terminal header is the A-M2 decision header, or battery and poll staleness for the rest of 29 Sep (W301). |
| **I354** (new) | "under the count rule, exp89r's UP would be MASKED by exp75 completing in the same window, although R26-A4 (b) exempts it" | `round30/report.json` plan_issues (f) | A wrongly MASKED UP could move the V_pub final (W300). |
| **I355** (new) | "Feed (tools/kaggle_feed.py) searches TOPIC+KERNEL only (l.78, l.158); e10_snapshot = kernels list + LB only -> no dataset channel"; "A 'biohub' search misses non-biohub slugs (corwin1979/biocel-secw-3f1c84ad)" | `round30/scan_recheck.notes.md` 01:24Z; `round30/v_recheck_r30-rc-c-*.notes.md` | Refuted as a build trigger (EV ~0; no port fits the 11:30Z cutoff). It stays an INFO-only gap for the scans (T181). |
| **I356** (new) | "'python tools/runtime_ledger.py --print' regenerated experiments/lb_poll/ledger.md as a side effect" | `round30/scan_recheck.notes.md` 01:24Z | This explains the `M experiments/lb_poll/ledger.md` in `git status`. It is harmless, but a "read-only" ledger check is not read-only. |
| **I357** (new) | "Deadline degrade ... For CI files (exp79a, exp87a: L_hi <= 9.48 h) it is probably absent but not proven ... Do not cite a '10.2 h mark' for the CI proof"; non-CI candidates "L_hi <= 7.67 h < 8.0 h DIVINS" | `round30/report.json` R30-A5 (3)(ii), rejected (RC-B) | The card must not overclaim runtime insurance for V_pub exp87a (W302 (3)). |
| I338-I342 | nb_try fail-open dedupe; empty T54; "Successfully submitted" never printed; PowerShell fake 'Z'; the vacuous `-F` freeze grep | `round29/report.notes.md` | **Resolved**: the fixes are in checklist 2b442e87, logged at l.4134-4146. The night batch ran clean (l.4254-4272). |
| I343 / I345 / I346 | gate85.py is unsuitable for exp89l; admit-edge sign; A-M2 precedence | `round29/*` | **Resolved**: the v2.1 gate was used (l.4168-4173); the sign was corrected in freeze (1) [R29]; the precedence was logged (l.4147-4150). It is superseded in part by I351. |
| I344 / I348 | LastSubmissionDate is not a best marker; nothing checks for LATE files between 01:30Z and 06:07Z | `round29/scan_plancheck.notes.md` | I344 is extended by I349. I348 is moot: all three night files were sent by 00:46Z. |
| I347 | Division-lever lab signs barely transfer between embryos, but geometry levers do | `round29/scan_recheck.notes.md` (B) | Unchanged. It supports an LB-driven finals choice. |
| I329 / I330 | A VS Code restart kills the waiters; Modern Standby delays timers | `round28/report.json` new_facts 5 | The residual risk is unchanged; the user can say "продолжи". |
| I334-I337, I316-I326, I303-I313, I287-I302, I278, I72, I116, I145 | Unchanged older insights | `_curation/29/watch.json`, `_curation/27/watch.json`, `_curation/26/watch.json` | - |
