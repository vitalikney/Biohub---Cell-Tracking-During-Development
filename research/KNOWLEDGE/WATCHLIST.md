# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-29 ~02:55 UTC (curation 31). This updates the curation-30 build of 29 Sep ~01:57Z. That build is committed in d6deab5, and a structured copy is in `research/KNOWLEDGE/_curation/30/watch.json`. Older predecessors run from `_curation/29/watch.json` down to `_curation/18/watch.json`. Rows not repeated here are unchanged there.

**Sources read for this update:**
- **`CONTEXT.md`:** it now has 4,314 lines, and `## 9. Literature` starts at l.4294. There is one new entry since curation 30: l.4273-4293 (**02:02Z, MORNING/FINALS TEXT RESOLUTIONS**, R30-A1).
- **`git log`:** **d6deab5** (02:02Z) committed round 30, curation 30 and the card v5 edits.
- **`research/wf_ideas_v4/round31/`:** untracked, written 02:13-02:45Z. Read:
  - `report.json`, which holds **R31-A1..A5**, new_facts (1)-(5), plan_issues (a)-(g), the rejected items and next_focus;
  - `report.notes.md`;
  - all `scan_*.notes.md` and `v_*.notes.md` files.
  - **There is no `REPORT.md`**, because the harness blocked it; the Russian text is in `report.json` next_focus.
- **`experiments/lb_poll/poll.log`:** the newest header is **02:34:11Z** (l.27583). In it, 56656147, 56656157 and 56657612 are PENDING, and 56640366 is COMPLETE 0.959.
- **Loops:**
  - `experiments/e10_watch/watch_loop.log`: RUN 37 at 01:42:07Z, signals 0, next 02:41:53Z.
  - `experiments/discussions/feed_loop.log`: 02:28:02Z, 0 new, E10 FLAG none.
- **Local read-only checks at ~02:50Z:**
  - Card v5 sha8 = **aab8801a**, which equals `CONTEXT.md` l.4290. `night_checklist.md` = 2b442e87.
  - `grep -c` on CONTEXT.md returns 0 for each of: DET_THRESHOLD, int-casting, "cron defect". "battery standby" still returns 1 (l.4096).
  - `experiments/RESULTS.md` probe rows still end at probe 46.
  - `research/wf_ideas_v4/e10v3/runbook.notes.md` l.66 still reads "OUR = 0.957 ... SC >= 0.958".
  - `round29/REPORT.md`, `round30/REPORT.md` and `round31/REPORT.md` are all absent.

All times are UTC; the user thinks in MSK, which is UTC+3 (`CONTEXT.md` l.3683-3687). IDs are stable: W is an action, T a time-bound reminder, I an insight. Status values are: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at ~02:50Z, 29 Sep:**
- **Best display: 0.959**, from exp87a (probe 51, 56640366), which is a CI file. V_pub = exp87a, the running champion under the conservative reading (`CONTEXT.md` l.4278-4285).
- **Rank** at 02:14Z: #132 of 3,979, 17th of 21 in the 0.959 block, with 115 teams at >= 0.960 (`round31/report.json` new_facts (2)).
- **Medal lines have moved up one block since mc26:**
  - bronze is at about #398, inside the 0.955 block;
  - silver is at about #199, inside the 0.957 block.
- **Night submissions, all PENDING at 02:34:11Z:**
  - 54 exp89p reads 07:38-08:35Z.
  - 53 exp75 reads ~09:05-10:05Z.
  - 52 exp89r reads ~09:25-09:35Z. Its 10.2 h mark is 10:17:28Z; the admit edge is 10:50:28Z.
- **Slots:** 2 left on 29 Sep, reserved for A-M1 (exp89l) and A-M2 (exp89s / exp89q) (`CONTEXT.md` l.4265-4272).
- **User:** asleep, autonomous mode (`CONTEXT.md` l.4081-4093). The session never ticks.
- **CRITICAL (new):** R30-A2 (a) is the A-M2 text that the 07:23Z prep is told to paste (`CONTEXT.md` l.4291-4293). It drops the **Rr '+'** condition. Pasted as is, it would send exp89q in cells where MORNING TABLE v1.1 says UNUSED, for example d_R = d_P = 0.959. This must be fixed PRE-SCORE (before the earliest read at 07:38Z) through **W304 = R31-A1**.

**Changes since ~01:57Z (curation 30):**
- **Done:** W298 = R30-A1 was logged at 02:02Z (`CONTEXT.md` l.4273-4293), quoting header 01:54:04Z with the 3 refs PENDING. It covers:
  - (1) the A-M1 trigger;
  - (2) the running champion, conservative reading;
  - (3) the SEC/Rr collision -> A-M2 UNUSED;
  - (4) the wording fixes;
  - (5) the R30-A2 pointer;
  - the card v5 edits, with the new sha8 aab8801a.
  - **Not folded in:** W279 (1) DET_THRESHOLD and W297, which remain open.
- **Half done:** W303, round 30 was committed in d6deab5.
- **Resolved insights:**
  - I349: '0u' unreachable, logged in (1).
  - I350: the tie order, logged in (2).
  - I351: the collision, logged in (3).
- **New:**
  - actions **W304-W308**;
  - reminders **T187-T191**;
  - insights **I358-I365**.

---

## OVERDUE / DUE NOW

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W304** (new; = **R31-A1**) | **ONE PRE-SCORE CONTEXT ENTRY + ONE CARD v5 EDIT**, above `## 9. Literature` (l.4294). It must quote a poll header that still shows the 3 night refs PENDING (02:34:11Z qualifies). <br>**(1) A-M2 function, branch A:** <br>- DIS '+' -> exp89s. <br>- Else, if Rr '+' (d_R >= 0.960, COMPLETE, header + 210 s x f <= 10:50:28Z): DIS '-' -> UNUSED; DIS '?' -> exp89q iff P is '+' or '?'; P '0' / '-' -> UNUSED. <br>- In every other case -> UNUSED. <br>Add grid rows: d_R = 0.959 -> UNUSED; d_R <= 0.958 -> UNUSED. For A-M2, P is read at the A-M2 header, so a late COMPLETE counts. GAP RULE v2 still applies to P after ~10:58:36Z. <br>**(2) The "08:40Z header"** = the last header stamped <= 08:40:36Z. At the 08:30Z timer, if exp89p is PENDING, run one `[manual-A-M1]` list at 08:40:00Z. <br>**(3) Round schedule:** <br>- the 07:13, 08:13, 09:13 and 10:13Z rounds are read-only, <= 5 min; <br>- the 06:07Z round runs only if it starts before 06:45Z; <br>- the next full round is the tail of the 11:10Z timer. <br>**(4) Card v5:** l.17 and l.124: non-CI L_hi <= 9.0 h (8.0-9.0 h flagged 'v'). Record the new sha8 | **not started**: CONTEXT's last entry is 02:02Z; card sha8 is still aab8801a at ~02:50Z | **NOW.** At the latest by the 07:23Z prep; the hard limit is before the first terminal night header (earliest ~07:38Z = 10:38 MSK) | `research/wf_ideas_v4/round31/report.json` R31-A1, plan_issues (a)-(e); `round31/v_plancheck_pc31-01.notes.md`; `round31/v_plancheck_pc31-05.notes.md`; `CONTEXT.md` l.3931-3960, l.4147, l.4286-4293 |
| W126 (part 2) | Add RESULTS.md rows for probes **47 (0.955), 48 (0.957), 49 (0.955), 50 (0.958) and 51 (0.959, UP 12)**, then the night probes 52-54 and the morning probes | **overdue**: probe rows still end at 46 | before the finals card (29 Sep 12:03Z) | `experiments/RESULTS.md`; `CONTEXT.md` l.3530, l.3615, l.3639, l.3856, l.4153-4160 |
| W296 + W303 (updated) | Write REPORT.md for **round 29, round 30 and round 31**. Rounds 30 and 31 must be copied verbatim from `report.json` (report_md_ru / next_focus), because the harness blocked the writes. **Commit round 31** (untracked) with named paths, as the user, with no Co-Authored-By | round 29/30 committed (6dc7088, d6deab5) but all 3 REPORT.md files are absent; round 31 is not committed | with the W304 commit | `round31/report.json` next_focus NOTE; `round31/report.notes.md` 02:38Z; `git status`; `memory/feedback-git-no-coauthor.md` |
| W286 (updated) | **(1)** Add a CONTEXT line: floatout probes 32/33 were no-ops under an int-casting scorer. **(2)** Fix `e10v3/runbook.notes.md` l.66 to "OUR = 0.959 (exp87a), so SC >= 0.960". CONTEXT l.4159-4160 already has the right trigger | (1)(2) **overdue**: `grep int-casting` = 0; l.66 unchanged at ~02:50Z; the E10 02:41Z read has passed | (2) before the next E10 read (03:41Z); (1) low | `round28/report.json` R28-A6; `research/wf_ideas_v4/e10v3/runbook.notes.md` l.66 |
| W279 (1) | Log RC-C: "DET_THRESHOLD stays closed for 29 Sep and is never a morning filler" | not started (not in 02:02Z; `grep -c DET_THRESHOLD CONTEXT.md` = 0) | before **07:23Z**; fold it into W304 | `round27/report.json` R27-A9 (1) |
| W297 | CONTEXT l.4096 still blames "a busy session / battery standby" for the lost rounds. The cause was the cron defect (round 28). Fold a one-line correction into W304 | not started | with W304; low | `round28/report.json` new_facts 5; `CONTEXT.md` l.4096 |
| W202 + W244 / W176 / W177 / W182 / I208 / W57 / W66 / W31 / W72 / W150 | Old info and curator lines; the ROUND RECORD; LESSONS H1; no NEVER_SUBMIT in exp70j/exp70k; old text fixes | overdue, low | H2, 29 Sep 23:00Z | `_curation/24/watch.json`, `_curation/26/watch.json` |

## NEXT 24 H (29 Sep ~02:50Z -> 23:59Z)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W304 | **now** | A-M2 function + 08:40Z header + round schedule + card pool L (above) | not started | R31-A1 |
| T181 (updated) + **T187** (new) | **03:13Z** round 32; 04:13Z and 05:13Z rounds (06:13-08:13 MSK) | Keep them **light, with no new mechanisms** (R8; both slots reserved). **(1)** Check that W304 is logged with a PENDING header and that the card sha8 changed; if not, log it in the next free slot. **(3)** Read-only LB / E10 / feed. Only a disclosure from a team at >= 0.959, or a public notebook >= 0.959, is actionable, and then only dummy + ask the user. **(4)** Pre-stage the 12:03Z card values (W307) | pending | `round31/report.json` next_focus; `CONTEXT.md` l.1671 (R8) |
| **T188 = W305** (new; = **R31-A2**) | **04:13Z** push (07:13 MSK); **06:07Z** conditional re-push | **ONE PushNotification in Russian, MSK times:** results from ~10:38; A-M1 by 11:45; A-M2 by 14:30; card at 15:03; "put the laptop on charge, keep the lid open"; "if it is offline by ~11:40, the A-M1 slot simply stays unused". **Do not ask the user to tick.** <br>**At 06:07Z,** if BatteryStatus != 2: push again, and **re-arm a battery-tolerant watchdog** that notifies when the header is > 25 min old and does not break on battery. The session never changes power settings | pending | `round31/report.json` R31-A2, plan_issues (d); `CONTEXT.md` l.3999-4008, l.4066-4072 |
| T100 (updated) | E10 hourly at hh:41Z until **12:00Z** (next 03:41Z); feed every 90 min (next ~03:58Z) until 23:59Z | The E10 v3 trigger is **>= 0.960** (l.4159-4160). **The 02:00Z E10 cutoff has passed:** a copy now needs the user's yes | live (RUN 37 01:42Z; feed 02:28Z) | `experiments/e10_watch/watch_loop.log`; `experiments/discussions/feed_loop.log` |
| T173 | **05:10-06:00Z** (08:10-09:00 MSK) | The user travels and the laptop sleeps. timer.sh fires on wake. The watchdog 10576 and the read watcher 13516 are one-shot (I353) | info | `CONTEXT.md` l.4066-4072 |
| T174 + W301 | **06:07Z** post-wake (09:07 MSK) | Check AC, poll-header age and loops. Re-arm the dead watchdog in the battery-tolerant form of W305. Chain read watchers on the remaining refs, plus one per morning submit ref (W294). **Launch a round only if it starts before 06:45Z and none has run since 05:13Z** (W304 (3)) | pending | `round30/report.json` R30-A4; `round31/report.json` R31-A1 (3), R31-A2 |
| W302 (4) | 06:07-07:23Z | First MSK message: "Both morning slots may end UNUSED by rule; that is expected. exp89t/exp89u stay off unless you say yes" | pending | `round30/report.json` R30-A5 (4) |
| **T189** (new; = R31-A1 (3), supersedes T185) | **07:13, 08:13, 09:13, 10:13Z** timers | The timer text says "launch the next research round". **Once W304 is logged, it is only a read-only check of <= 5 min:** newest poll header, e10_watch file and digest. No workflow, no subagents, no Kaggle calls. Decision headers, watchers and the 07:23Z, 08:30Z and 11:10Z steps take precedence | pending (depends on W304) | `round31/v_plancheck_pc31-05.notes.md` (timer texts read live); `round31/report.json` plan_issues (e) |
| T151 + W299 (updated) | **07:23Z** prep (10:23 MSK) | **Do NOT rebuild or re-push exp89l / exp89s / exp89q:** submit `-v 1`, which is the gated dummy (`CONTEXT.md` l.4291). Re-run G5. Paste the grid + commands from R30-A2, **but replace the R30-A2 (a) A-M2 bullets with the W304 (1) function.** Also log the pending L lower bounds of the 3 night refs (W306) | pending | `round30/report.json` R30-A2; `round31/report.json` R31-A1 (1), R31-A3 |
| T159 / T182 + **W306** (new; = **R31-A3**) | **exp89p 07:38-08:35Z**; exp75 ~09:05-10:05Z; exp89r ~09:25-09:35Z | **Night reads:** P = exp89p vs exp85a 0.958 (P '+' only at >= 0.959). Rr = exp89r vs exp87a 0.959. exp75 vs #37 0.954 (partner rule v2). DIS per R26-A2 (1). At each first terminal header, **log the L interval next to the family range: non-CI 6.87-7.81 h, CI 9.27-9.48 h.** Add a card line only if L_lo exceeds the family maximum by > 0.5 h ("a read after ~19:30Z cannot be a final"). Log KEY FACTS + RESULTS (W126) | pending (all PENDING at 02:34:11Z) | `CONTEXT.md` l.4254-4293; `round31/report.json` R31-A3, new_facts (4) |
| W300 | at each terminal header, 07:38-11:00Z | **UP-test protocol:** <br>- **P at 0.958:** '0', no call (now logged in l.4274-4277). <br>- **P at 0.959:** submit exp89l first, then `uptest.py save S1_P`. It is valid only with count 54 and date 00:46:36. <br>- **exp89r:** test only on a top-display tie; an exp75 jump is exempt. <br>- **Budget:** <= 3 LB calls, and a download never delays a submit | pending | `round30/report.json` R30-A3 |
| T151 A-M1 / T183 + **T190** (new) | first header with 56657612 terminal; **the 08:40Z header** (= last header <= 08:40:36Z), submit by **08:45Z** (11:45 MSK) | **A-M1:** d_P >= 0.959, COMPLETE -> `nb_try exp89l $KL "$M55L"`; anything else -> UNUSED (l.4274-4277). **T190: the poller drifts +2 s per cycle, so its headers land at ~08:35:1x and ~08:45:1x.** At the 08:30Z timer, if exp89p is PENDING: arm ONE waiter that runs one list at 08:40:00Z, tagged `[manual-A-M1]` in poll.log (1 Kaggle call; this needs W304 (2) logged first). Guards G1-G5 and exit codes as in R30-A2 | pending | `round31/report.json` R31-A1 (2), plan_issues (c); `round31/report.notes.md` PC31-03 |
| T151 A-M2 / T184 (updated) | first header with 56656147 terminal; **latest 11:00Z header, submit by 11:30Z** (14:30 MSK); 11:10Z timer | **Use the W304 (1) function, NOT the R30-A2 (a) bullet.** P = '0' / '-' -> SEC-free only (exp89s on DIS '+'), else UNUSED (l.4286-4289). A hidden-run ERROR of exp89r -> UNUSED, not branch B. Nothing depends on exp75 | pending | `round31/report.json` R31-A1 (1); `CONTEXT.md` l.4286-4289 |
| T180 / W294 | at each morning submit | Start a late-read watcher per morning ref. exp89l sent at 08:45Z reads ~18:03-18:15Z; an M2 non-CI file sent at 11:30Z reads by ~19:20Z at the 7.81 h max | pending | `round29/report.json` R29-A7; `round31/report.json` R31-A3 why |
| W19 / W73 / W102 / W93 / W165b / W261 | standing | ONE poller; header < 15 min old; never resubmit class C or ERRORed files. SEC may be a final only as V_pub (Q3). Dataset pre-push check | standing | `CONTEXT.md` l.3331-3335, l.3692-3703, l.4112-4114 |
| T186 | **11:41Z** last E10 snapshot; the E10 loop exits at 12:00Z | Take RANK, block position **and medal-line ranks (W307 (3))** for the 12:03Z card from the 11:41Z snapshot. After that, use <= 3 `uptest.py save` calls | pending | `round30/report.json` R30-A4 (c), R30-A5 (1) |
| **T191** (new) | ~11:10-11:30Z, the tail of the 11:10Z timer | **The next full round runs only after A-M2 is submitted or logged UNUSED.** Check the card fill against the reads (P, Rr, DIS, exp75 partner rule v2) and the running-champion V_pub | pending | `round31/report.json` next_focus, R31-A1 (3) |
| W266 (2) / T60 / W302 (1)(3) + **W307** (new; = **R31-A4**) | **12:03Z** (15:03 MSK), timer | Fill card v5 **with the sha8 from W304** (aab8801a until then). <br>**W307 new numbers (V_pub exp87a):** <br>- П2 {exp87a, exp75}: bronze ~0.63-0.85 / silver ~0.43-0.68 (replaces l.37-38); <br>- П3 {exp87a, #37}: ~0.61-0.83 / ~0.39-0.64; <br>- the ticked {#37, #38}: bronze 0.20-0.58 (base 0.38) / silver 0.02-0.16 (base 0.07) (replaces l.46); <br>- l.47 re-dated; <br>- the silver caveat for {V_pub, exp85a}; <br>- a medal-line rank line from the newest e10_watch file. <br>(4) is optional, in placeholder form only. **Never "не медаль" or "рекомендую".** Add the W302 (3) info lines. Send only the ===== block; never tick | pending | `round31/report.json` R31-A4, plan_issues (g), rejected; `round31/v_recheck_r31-rc-a-*.notes.md`; `research/wf_ideas_v4/round29/finals_card_v5_ru.md` l.37-47 |
| **W308** (new; = **R31-A5**) | any free slot after the morning decisions; post-deadline is acceptable | Curator note on **I-045**: "WEAKENED on public by CI (2x +0.001 at rounding level, one embryo, a different model); stays closed; post-deadline only". Never write "overturned" or cite ~11.5 h as measured | not started | `round31/report.json` R31-A5; `round31/v_recheck_r31-rc-c-*.notes.md` |

## LATER (29 Sep ~12:00Z -> 23:59Z, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T152 + W302 (2) + W307 (5) | **18:37Z** (21:37 MSK), timer | FINAL proposal from card v5: "the pair by the card", **never "рекомендую"**. **If V_pub changed** (only a later file at >= 0.960 or with an attributable UP at 0.959, per l.4278-4285), re-run `scratchpad/r31v/mc31v.py` with the new VPUB and replace the numbers. List the still-PENDING files with MSK windows | `round31/report.json` R31-A4 (5); `round30/report.json` R30-A5 (2) |
| T161 | **19:43Z** (22:43 MSK), timer | Notify-only reminder + V_pub re-check. **Any read after ~19:30Z cannot be a final** (user rule, not 19:40Z) | `CONTEXT.md` l.3685, l.4054-4056; `round31/v_recheck_r31-rc-b-*.notes.md` |
| T10 | **20:00Z (23:00 MSK)** | **The user ticks the finals.** The session never ticks. If the user does nothing, #37 + #38 stay; the ticked pair's modelled bronze is only ~0.38 at base (W307) | `CONTEXT.md` l.3851-3855, l.4091-4092; `round31/report.json` new_facts (5) |
| T153 | ~20:00-20:30Z | Verify that API SELECTED = the user's pair | `CONTEXT.md` l.3474 |
| T162 | **21:05Z** (00:05 MSK 30 Sep), timer | Last-call notify: if SELECTED is not the proposed pair, push the exact pair | `CONTEXT.md` l.4092, l.4099 |
| W177 H2 / T49 | 23:00Z / 23:00-23:45Z | LESSONS H2; final public LB snapshot | `_curation/20/watch.json`; `CONTEXT.md` l.2619 |
| T11 / T163 | **29 Sep 23:59Z** (02:59 MSK 30 Sep) | Deadline: a submit must **finish** before it; re-ticks are allowed until then | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765; `CONTEXT.md` l.3848, l.3855 |
| T155 | 30 Sep 00:07Z, timer | POST-DEADLINE job: private read v2 + L1-L7 | `CONTEXT.md` l.3714-3715, l.4131 |
| W295 | next CONTEXT entry / curation pass | The 744093 integer check covers every finals candidate; an I-320 narrow annotation; do not publish the "5/14" class table | `round29/report.json` R29-A8 |
| T133 / T170 | 3 Oct | GPU quota refresh (about 2.7 h left) | `CONTEXT.md` l.4239-4241 |
| W29 / curator / W308 | after 29 Sep | Post-deadline list, plus z-shift I-029, the MAX_UM 2.0 note and the I-045 "weakened" note | `round25/report.json` R25-A8 (d); `round28/report.json` R28-A6 (1); `round31/report.json` R31-A5 |

**Passed or finished time-bound items:**
- **Earlier deadlines:**
  - The R8 new-mechanism cutoff (27 Sep 12:00Z) has passed.
  - The 28 Sep 12:00Z consolidation is superseded (T46; l.3392-3394).
  - The **E10 02:00Z cutoff (T172)** has passed: any E10 copy now needs the user's yes (`CONTEXT.md` l.4089-4091).
- **Overnight 28-29 Sep:**
  - The 51 read (21:43Z).
  - The freeze (23:34Z).
  - The slot reset (00:00Z).
  - The night batch (00:05-00:46Z).
  - **W298 / R30-A1**, logged at 02:02Z (l.4273-4293).
- **Friend replies:** none awaited. The last friend instruction was on 26 Sep (l.2175-2176).
- **T156:** the tick deadline is 20:00 UTC = 23:00 MSK. Never write "20:00" without "UTC".

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I358** (new) | "bullet 'DIS ? -> exp89q only if P is + or ?' lacks the Rr '+' condition of MORNING TABLE v1.1 (2) ('DIS + -> exp89s; else Rr + -> exp89q; else UNUSED')"; "Cell (i) d_R=d_P=0.959: DIS '?' ..., P '+', Rr not '+' (needs >=0.960) -> v1.1 UNUSED, literal bullet exp89q. Real and plausible" | `round31/scan_plancheck.notes.md` FINDING A; `round31/v_plancheck_pc31-01.notes.md` | CONTEXT l.4291-4293 tells the 07:23Z prep to paste R30-A2. Until W304 (1) is logged, the modal cell sends a SEC file no read supports into the last slot. |
| **I359** (new) | "headers 01:13:57 ... 02:24:09 -> 601.7 s/cycle; extrapolated 08:35:1x and 08:45:1x"; "A read in the ~08:40:36-08:44 window is lost for lack of a header" | `round31/report.notes.md` (PC31-03); `round31/scan_plancheck.notes.md` FINDING C | A-M1 is defined at "the 08:40Z header", which may not exist. The standby window 05:10-06:00Z shifts the phase unpredictably (T190). |
| **I360** (new) | "the bronze line moved UP one block ... #37 (0.954) and a 0.954 exp75 now sit 34-169 ranks BELOW the public bronze line; card v5 has no medal-line field"; "mid rate ... ~5.5/h vs model ... 1.4-2.5/h" | `round31/scan_hyp_private31.notes.md`; `round31/scan_recheck.notes.md` | The card numbers (l.37-47) were computed for exp85a on the old field. With stale numbers, the card understates the cost of leaving {#37, #38} ticked (W307). |
| **I361** (new) | "R28 CI prior (0.0002/0.0010) base SILVER: {87a,85a} .528 > {87a,75} .520 > {87a,#37} .499 ... 'exp85a never better' ... is false for silver; ordering claim holds for bronze only" | `round31/v_recheck_r31-rc-a-c02-rank-arithmetic-x138-block-no.notes.md` | This is the only caveat against the P2/P3 ordering. If the card states the silver order as settled, it steers the user (W307 (2)). |
| **I362** (new) | "exp89p margin: ... vs exp85a L_hi 7.19 margin 0.70 h (as claimed), but vs family max 7.81 only ~0.08 h" | `round31/v_recheck_r31-rc-b-v3-queue-growth-latency-risk-not-.notes.md` | A late exp89p read makes A-M1 UNUSED by rule. This is not an error, but the 08:30Z check should expect it (T190). |
| **I363** (new) | "15 COMPLETE x138-family rows ... Non-CI safetail L is 6.87-7.81 h and CI is 9.27-9.48 h, with no growth trend and no time-of-day effect"; "same-family jitter ... 0.48 h" | `round31/report.json` new_facts (4); `round31/v_recheck_r31-rc-b-*.notes.md` | This closes the v3 FINAL_REPORT (g)6 fear of > 10 h. Only a jump beyond the family max + 0.5 h should change the card (W306). |
| **I364** (new) | "CI (I-324, same class ...) read + twice on LB ... -> the value/transfer objections are contradicted in sign on the public embryo"; the skeptic says "'OVERTURNED' is too strong" | `round31/scan_recheck.notes.md` RC-C; `round31/v_recheck_r31-rc-c-*.notes.md` | I-045 must be recorded as "weakened", never "overturned" (W308). This is post-deadline material. |
| **I365** (new) | "tools/uptest.py counts a missing TeamId as 'not passed', so a removed or banned team cannot fake an UP"; "Ideas never named in any recheck file: I-006, I-045, I-068, I-100, I-133, I-154, I-167, I-192" | `round31/report.json` new_facts (1); `round31/scan_recheck.notes.md` 02:25Z | The first is a safety property of the W300 UP test. The second lists recheck gaps that are only for the post-deadline lessons. |
| I356 (repeated) | "running 'python tools/runtime_ledger.py --print' regenerated experiments/lb_poll/ledger.md" happened again in round 31 | `round31/scan_recheck.notes.md` NOTE | This keeps `M experiments/lb_poll/ledger.md` in `git status`. It is harmless, but it is not read-only. |
| I352 / I353 / I354 / I355 / I357 | The stale timer "build/dummy exp89l" vs nb_try `-v 1`; one-shot watchdog/watchers; an exp75-masked UP; no dataset channel in the feed; "deadline degrade" wording | `round30/*` (see `_curation/30/watch.json`) | **I352** is logged (l.4291). I353-I357 stay open, via W305/W301, W300, T181 and W302 (3). |
| I349 / I350 / I351 | '0u' unreachable; the tie-order conflict; the SEC/Rr collision | `round30/scan_plancheck.notes.md` | **Resolved** by `CONTEXT.md` l.4273-4290 (02:02Z). |
| I338-I348, I329/I330, I334-I337, I316-I326, I303-I313, I287-I302, I278, I72, I116, I145 | Unchanged older insights | `_curation/30/watch.json`, `_curation/29/watch.json`, `_curation/27/watch.json` | - |
