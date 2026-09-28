# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-28 ~14:00 UTC (curation 26). This updates the curation-25 build of 28 Sep ~11:00Z (full text in the git history of this file; structured copy `research/KNOWLEDGE/_curation/25/watch.json`). Older predecessors: `_curation/24/watch.json`, `_curation/23/watch.json`, `_curation/22/watch.json`, `_curation/21/watch.json`, `_curation/20/watch.json`, `_curation/18/watch.json`. Rows not repeated here are unchanged there. The TASK_LOCAL_SESSION, TASK_CLOUD_SESSION and v3 FINAL_REPORT rows are unchanged since `_curation/20/watch.json`.

**Sources read for this update:**
- `CONTEXT.md` has 3,944 lines; `## 9. Literature` starts at l.3924. New entries since curation 25 (l.3717-3923):
  - 11:17Z R25 PRE-SCORE 1/2 (W2b AMENDMENT A2, l.3717) and 2/2 (W4 AMEND 4, l.3753); GATE LINES exp88c + exp86c WAIVER (l.3794); exp75 LINE (l.3810);
  - 11:19Z exp88c PASS, exp89a/e built, ledger, `tools/uptest.py`, KEY FACTS refreshed (l.3824);
  - 11:26Z user Q3 = YES (l.3834); 11:27Z fallback tick allowed (l.3842); **11:28Z correction: the session will NOT tick; notify-only** (l.3851);
  - 12:16Z **probe 50 exp85a = 0.958, R+, UP 21, rank 134** (l.3856); 12:16Z **probe 51 exp87a submitted** (l.3863);
  - 12:17Z night list under R+ + exp89p build (l.3871); 12:23Z risk stack exp89q/exp89r (l.3885); **12:25Z user confirmed the night + standing override** (l.3899);
  - 12:40Z exp89p gate PASS + discussion 743006 (l.3908); 13:14Z exp89q and exp89r gates PASS (l.3915).
- `git log`: a04ab40, 439fa9b, fedfe87, e569075, 67b3a9e, 6b043ab, c481495, eeec7d6, f1a9c50, 2ba51cc, 88c945d, 5e5fd1b (last = 16:14 local = 13:14Z). `git log -12 --format=%b | grep -ci co-author` = 0.
- `git status` 13:52Z: `research/wf_ideas_v4/round26/` untracked; loop logs modified.
- `research/wf_ideas_v4/round26/report.json` (13:50Z) with **R26-A1..A7** and plan_issues 1-11; `report.notes.md`; `scan_plancheck.notes.md`, `scan_hyp_finals.notes.md`, `scan_hyp_morning.notes.md`, `scan_recheck.notes.md`, `scan_browser.notes.md`, `v_plancheck_pc26-04.notes.md`, `v_hyp_finals_r26f-2.notes.md`, `v_hyp_morning_r26m-5.notes.md`.
- `experiments/lb_poll/poll.log` header **13:44:04Z** (l.23017): 56640366 (probe 51) PENDING; 56629533 COMPLETE 0.958.
- `experiments/e10_watch/watch_loop.log` RUN 25 13:22:51Z CHANGES=0, signals 0; `experiments/discussions/feed_loop.log` 13:38:27Z, 0 new, E10 FLAG none; `experiments/discussions/digest_20260928T1338Z.md` (top public notebook 0.953; flag > 0.958).
- Code/file checks 13:55Z: `tools/runtime_ledger.py` l.82 regex `exp89[abcghilmnor]` (no `t`); `tools/kaggle_feed.py` l.172 default 0.958; `experiments/lb_poll/e10_watch_loop.py` l.78 LOOK text "0.958 ... so >= 0.959"; `tools/uptest.py` exists; `ls experiments | grep exp89` = a, e, p, q, r (no s/l/t/u); `experiments/RESULTS.md` probe rows end at probe 46 (l.78-79); `ls research/wf_ideas_v4/round2*/REPORT.md` = rounds 20-23 only.

All times are UTC. The user thinks in MSK (UTC+3) (`CONTEXT.md` l.3683-3687). IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at 13:55Z, 28 Sep:**
- **Best display 0.958** = exp85a (probe 50, 56629533; exp70g + ILP_DIVISION_WEIGHT 0.4 + READMIT_MIN_SCORE 0.94; **non-CI**). UP 21 teams, R+ (`CONTEXT.md` l.3856-3862). V_pub = exp85a.
- **Rank:** #134 of 3,966, 121 teams strictly above; 13th of 20 in the 0.958 block (`round26/report.json` new_facts 2).
- **Probe 51 exp87a** (K + CI, 56640366, submitted 12:14:57Z) is PENDING at 13:44:04Z (`poll.log` l.23017). Read expected 21:30-22:15Z (00:30-01:15 MSK), tail ~23:09Z. REF = exp85a; '+' >= 0.959; '0u' = 0.958 with attributable UP (`CONTEXT.md` l.3863-3870).
- **28 Sep slots:** 5 of 5 used ("0 submissions remaining today", l.3865).
- **Night 29 Sep (user confirmed 12:25Z, l.3899-3907):** 00:05 exp89r (if 51 reads '+'/'0u') else exp89q; 00:06 exp75; 00:46 exp89p; fallbacks: stack variant swap; exp89p fail -> exp83c at 00:07. If 51 is not terminal at the freeze -> exp89q.
- **Dummies PASSED:** exp89p (l.3908), exp89q + exp89r (l.3915), exp75 (l.3810), exp83c, exp86c (waiver), exp87a, exp88a/b/c (l.3824).
- **Q3 = YES** (11:26Z, l.3834): a SEC file may be a final only as V_pub, never the hedge.
- **Finals:** #37 + #38 still ticked. The user ticks by 20:00 UTC (23:00 MSK) 29 Sep. **The session never ticks** (classifier block, l.3851-3855); notify-only jobs 22:43 MSK and 00:05 MSK.
- **GPU unmeasured since 04:55Z:** estimates 2.2 h / 2.5-3 h / ~3.6 h (`round26/report.json` new_facts 11; `CONTEXT.md` l.3922-3923).
- **Ops:** poller, E10 watch loop and discussion feed alive (`round26/report.notes.md` 13:46Z). Session cron per l.3709-3716 (session-only). Research round 26 finished 13:50Z; next 15:17Z.
- **The user just asked "ресерчеры активны?"** — the R26-A6 message is the answer (W267).

**Changes since ~11:00Z (curation 25):**
- **Done:**
  - W248 (l.3717), W249 (l.3753), W250 (a)(b) (l.3794, l.3824), W251 (l.3810);
  - W252 (a) ledger + builds exp89a/e (l.3824; `tools/runtime_ledger.py` l.82); W255 (a) KEY FACTS (l.3832-3833), W255 (b) `tools/uptest.py` (l.3832), W255 (e) feed/watch thresholds 0.958 (`tools/kaggle_feed.py` l.172, `e10_watch_loop.py` l.78);
  - W253 (c)(d)(e) answered: Q3 yes (l.3834), tick fallback yes then blocked (l.3842-3855); W260 resolved: CI morning cutoff **08:45Z** adopted (l.3792-3793, l.3904);
  - W258 wake-ups: moot, probe 50 read at 12:16Z; T145 read (l.3856); T146 submit (l.3863).
- **Moot / superseded:**
  - The R0/R-/R? night branch (exp88c, exp89a, exp88b), exp89e, exp86c night slot, M1 exp89h/exp89b/exp89o, M2 exp89j/k/f: superseded by the 12:17Z/12:25Z night and R26-A2 morning table (l.3871-3907; `round26/report.json` plan_issues 2).
  - W256 exp90a spare: moot (CI MAX_UM 2.0 is on the closed list, `round26/report.json` rejected).
  - W254 finals card v3 -> **W266** (card v4, R26-A5). T154 (fallback tick) -> **T162** (notify-only).
  - I289 (no fallback authorised) -> the user authorised it, the classifier blocked it; the user's own tick is the only path (I310).
- **New:** actions **W262-W270**, reminders **T157-T164**, insights **I303-I314**.

---

## OVERDUE / DUE NOW

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W267** (new; = **R26-A6**) | **Answer the user's "ресерчеры активны?"** in ONE Russian message (MSK first): (i) yes: poller 16:44 MSK, E10 watch 16:22 MSK CHANGES=0, feed 16:38 MSK 0 new; round 26 done ~16:50 MSK; next rounds 18:17 / 20:47 / 23:17 MSK; (ii) the night is unchanged; (iii) morning v1.1: a slot is used only for a stack of levers that read '+'; otherwise unused; (iv) **Q-M1:** branch A, if exp89p does not read '+', may M1 be exp89t (K + DIS 2.25 + CI)? default NO; (v) **Q-M2:** exp89u (#37 + K) as fallback partner if exp75 fails? default NO; (vi) the session reads "stack of the night winners" as lifting the "cap + 2 levers" cap for {K, SEC, DIS 2.25, CI} only — object if not. Log the answers | not started (covered_by_existing_approval **false**) | **now**; answers needed before ~21:30Z (00:30 MSK) | `round26/report.json` R26-A6, next_focus last line |
| **W262** (new; = **R26-A1**) | **R8 COVERAGE line for the night files** exp89p/q/r (secFT n2a 7029fe69; exp89r also coordinject as exp79a); mark the 00:00Z line's "Q3 open" superseded by the 11:26Z yes. Without it, the 00:04Z pre-submit check "this R8 COVERAGE line is present" fails for all three night files. Do not pre-cover unbuilt names (exp89l gets its line when built) | not started (`grep "R8 COVERAGE EXTENDED"` = 0; coverage lines l.3311-3315, l.3604, l.3831 only) | **now**; hard latest 23:30Z freeze / 00:04Z checklist | `round26/report.json` R26-A1, plan_issues 1; `round26/v_plancheck_pc26-04.notes.md` |
| **W264** (1)(2) (new; = **R26-A3**) | **(1) Build exp89s_k2cap6_k_dis225** (K + DIS 2.25, non-CI); STOP unless sha8 = **8ed72e32**. Before the push: GPU quota read (W269) and dataset baseline check (W261). Log the gate BEFORE reading the output: vs exp85a dummy 122,328 / 118,137 / 85; nodes 120,860-121,839; no 'Secondary SHA256' line; forks 85 +-5; LOWREFINE 148,020 +-1%; rule v2 <= 2,100 s (expect ~1,600-1,670 s). exp89s is the only morning file both branches can use. **(2)** Add `t` to `tools/runtime_ledger.py` l.82 -> `exp89[abcghilmnort]` + a test (exp89t -> safetail_ci; exp89s/u -> safetail) | not started (no exp89s folder; l.82 has no `t`) | **now** (~13:50Z) | `round26/report.json` R26-A3 (1)(2), new_facts 5 |
| **W269** (new) | **Read the GPU quota** on the Kaggle Settings page before the next push; else assume the conservative 2.2 h. Budget exp89s + exp89l <= ~1.05 GPU-h, leaving >= ~1.1 h for one E10 dummy | not started (unmeasured since 04:55Z) | before the exp89s push | `round26/report.json` plan_issues 10, new_facts 11; `CONTEXT.md` l.3922-3923 |
| **W268** (new; = **R26-A7**) | Refresh KEY FACTS in the round-27 task text: best 0.958 exp85a (non-CI, UP 21, rank 134); probe 51 exp87a PENDING, read 21:30-22:15Z; the confirmed night; dummies PASSED; E10 >= 0.959 + standing override; GPU 2.2-3.6 h unmeasured; morning = table v1.1; closed: DIS 1.75, READMIT 0.92/0.90, ILP_DIVISION_WEIGHT < 0.4, exp89u as default. (This curation task text is also stale: it still names the passed R8 27 Sep and consolidation 28 Sep 12:00 examples) | not started | before round 27 (**15:17Z**) | `round26/report.json` R26-A7, plan_issues 11 |
| W126 (part 2) | RESULTS.md rows for probes **47 (0.955), 48 (0.957), 49 (0.955), 50 (0.958)**; later 51 and the night probes 52-54 | **overdue** (probe rows end at 46, `experiments/RESULTS.md` l.78-79) | before the finals card (29 Sep 12:03Z) | `CONTEXT.md` l.3530, l.3615, l.3639, l.3856 |
| W246 / W257 | REPORT.md for rounds 24, 25, 26 never rendered (subagent rule; Russian text in `report_md_ru` of each `report.json`). Round 25 folder committed (a04ab40); **round 26 untracked**. Commit named paths only, as the user, no Co-Authored-By; never `git add -A` | round 26 not started | with the next CONTEXT commit | `round26/report.notes.md`; `git status` 13:52Z |
| W238 (residue) | `tools/gate_dummy.py` still missing (gate scripts in scratchpad; `tools/dummy_gates.py` is the 25 Sep v3 plan tool). The 13:14Z line notes the scratchpad script still flags at the old 1,900 s threshold | in progress, low | before the exp89s gate | `CONTEXT.md` l.3920; `ls tools` 13:55Z |
| W202 + W244 | Info/curator lines R22-A9 (a)-(h); R24-A10 (a)-(f) (incl. I278 José Freitas vs hengck23 at l.3510) | not started (`grep "R22-A9 INFO\|I-412"` = 0) | today, low | `round23/report.json` R23-A8; `round24/report.json` R24-A10 |
| W176 / W177 / W182 | ROUND 14-26 RECORD; LESSONS H1; no `NEVER_SUBMIT.md` in exp70j/exp70k | overdue, low | H1 now; H2 29 Sep 23:00Z | `_curation/24/watch.json` |
| I208 / W57 / W66 / W31 / W72 / W150 | Old low-priority text fixes | overdue, low | passed | `_curation/20/watch.json` |

## NEXT 24 H (28 Sep 13:55Z -> 29 Sep 13:55Z)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W267, W262, W264 (1)(2), W269, W268 | **now** | User message, R8 coverage, exp89s build/gate/dummy, ledger `t`, GPU read, KEY FACTS | not started | R26-A1, A3, A6, A7 |
| **T157** (new) | **15:17Z** (18:17 MSK) | Round 27 checks: W262 in CONTEXT; W263 and W266 (1) logged pre-score with a poll header; exp89s sha 8ed72e32, gate before output, dummy result; ledger `t` + test; GPU read; user answers to W267; E10 >= 0.959 / disclosure scan; KEY FACTS refreshed | scheduled | `round26/report.json` next_focus; `CONTEXT.md` l.3711-3712 |
| **W263** (new; = **R26-A2**) | before probe 51 reads (~21:30Z); latest in the 23:30Z freeze line; evaluated at the 07:23Z prep | **PRE-SCORE "MORNING TABLE v1.1"** (supersedes the 12:17Z MORNING clause). (0) depth-cap supersede for {K, SEC n2a, DIS 2.25, CI} only; KEY = the stack actually submitted at 00:05Z. (1) codes P (exp89p vs 0.958), Rr (exp89r vs exp87a), DIS (branch B: exp89q vs exp89p; branch A: double difference dd, '+' only if dd >= +0.002 AND exp89r > max(exp87a, exp89p)). (2) Branch A: M1 (CI, by 08:45Z) = exp89l (cad1d47f) on P '+'/'0u', else UNUSED; M2 (non-CI, by 11:30Z) = exp89s on DIS '+', else exp89q on Rr '+', else UNUSED. (3) Branch B: M1 (non-CI, decide by the 10:30Z header, submit by 10:50Z) = exp89s on DIS '+', else UNUSED; M2 UNUSED (exp89u only on user yes). (4) a chosen file without a PASSED dummy -> UNUSED | not started (`grep "MORNING TABLE"` = 0) | `round26/report.json` R26-A2, plan_issues 2-4 |
| **W266** (1) (new; = **R26-A5** (1)) | before **00:06Z** (exp75 submit) | **PRE-SCORE "EXP75 PARTNER RULE v2"** (amends R25-A1 (5)): clean = COMPLETE, no ERROR, CI-RAN (dL = L_hi - 7.54 h > 0.5 h), L_hi <= 10.2 h. V_pub non-CI: exp75 >= 0.955 clean -> B {V_pub, exp75} model-favoured next to A {V_pub, #37}; 0.954 clean and 51 not '-' -> near-equal trade; 0.954 with 51 '-' -> A first; V_pub CI -> R25 rule; <= 0.953/ERROR/NO-OP -> #37 + CI-risk flag; C {V_pub, exp70g} info row | not started (`grep "PARTNER RULE v2"` = 0) | `round26/report.json` R26-A5 (1); `round26/v_hyp_finals_r26f-2.notes.md` |
| T148 | **~21:30-22:15Z** (00:30-01:15 MSK); tail ~23:09Z | **Read probe 51** (exp87a vs REF exp85a 0.958): '+' >= 0.959 -> night stack exp89r (branch A); '0u' -> exp89r; '0' = NON-ADDITIVE stop; '-' -> exp89q (branch B) + CI-risk flag on every CI card file; not terminal at the freeze -> exp89q. Update RESULTS (W126) | pending (PENDING 13:44:04Z) | `CONTEXT.md` l.3863-3870, l.3899-3904; `round26/scan_hyp_morning.notes.md` (51 reads 21:31-21:42Z) |
| **T158** (new; = **R26-A3** (3)) | at probe 51's read, only if it reads '+'/'0u' before 23:30Z | **Branch A only:** log the depth-cap supersede line + coverage line for exp89l (secFT + coordinject; V_pub only); build exp89l_k2cap6_k_sec_ci (STOP unless sha8 = cad1d47f); push its dummy; gate vs exp89p dummy (topology identical, Secondary 7029fe69, COORDINJECT 4/4 replaced >= 0.90, integer change 0.60-0.69, rule v2; thin-margin flag above 2,000 s). exp89t/exp89u only on the user's yes (W267) and with >= 1.5 GPU-h left | pending | `round26/report.json` R26-A3 (3)(4) |
| T100 | hourly at hh:22Z until 29 Sep 12:00Z; feed every 30 min until 29 Sep 23:59Z | E10 v3 watch, trigger **>= 0.959**. **Standing override (user 12:25Z):** a public notebook >= 0.959 or a new disclosed knob -> build + dummy at once and propose the swap; after 02:00Z an E10 copy needs the user's yes per notebook | live (RUN 25 13:22Z; feed 13:38Z, 0 new) | `CONTEXT.md` l.3904-3907; `experiments/e10_watch/watch_loop.log`; `experiments/discussions/feed_loop.log` |
| T135 | 28 Sep: 15:17, 17:47, 20:17Z; 29 Sep: 22:47 (28th), 01:17, 03:47, 06:17, 08:47, 11:17, 13:47, 16:17Z | Research rounds (session cron; session-only) | scheduled | `CONTEXT.md` l.3711-3713 |
| T19 / W77 | 17:57Z | Tick check: API SELECTED still #37 + #38 (timer 012fa6dd dead; not in the 10:52Z cron) | at risk (W270) | `CONTEXT.md` l.2365, l.3709-3716 |
| **T143** + **W265** (new; = **R26-A4**) | **23:30Z** (02:30 MSK; cron 23:33Z) | **W4 FREEZE line**, pre-score, quoting the last poll header: R; the frozen list with slot times; dummy status (all PASS); the stack choice (exp89r vs exp89q). Plus R26-A4: **(a)** read codes exp89r (REF exp87a display), exp89q (REF 0.958), exp89p (vs exp85a), DIS as in W263; V_pub rule unchanged (highest display; ties: attributable UP > non-CI > fewer levers > earlier submit, l.3181/l.3419). **(b)** MASKING: a completion strictly below our LB display cannot mask the other file's UP test (covers exp75 vs exp89r overlap); S0 = freeze download; S1 = first download after each completion from 07:00Z; fallback = hourly E10 snapshots. **(c)** hygiene: non-CI spacing from the ACTUAL submit time; -m starts with the file's own token ('probe 52: exp89r = ...', 'probe 53: exp75 = ...', 'probe 54: exp89p = ...'); submit exp75 v1, never re-push; dataset baseline check right before the batch. **(d)** finals pool/PENDING clause + a notify-only 19:30Z job. **(e)** morning exclusions: no ILP_DIVISION_WEIGHT < 0.4, no READMIT 0.92/0.90, DIS 1.75 not built | pending | `round26/report.json` R26-A4 (a)-(e), plan_issues 4-7 |
| T126 | 29 Sep 00:00Z | Slot reset (5 new slots) | - | `CONTEXT.md` l.3367 |
| T20 / T107 | **29 Sep: 00:04Z cron; 00:05 / 00:06 / 00:46Z** | **Night batch:** 00:05 exp89r or exp89q; 00:06 exp75; 00:46 exp89p (>= 40 min after the previous non-CI file's actual submit); fallback exp89p fail -> exp83c at 00:07. Pre-submit: R8 coverage (W262), dataset baseline (W261), no duplicate, header < 15 min | pending | `CONTEXT.md` l.3899-3907, l.3713; `round26/report.json` R26-A4 (c) |
| **T159** (new) | 29 Sep: exp89q **06:57-07:54Z**; exp89p **07:38-08:35Z**; exp75 **~09:06-09:36Z**; exp89r **09:21-09:32Z** (tail 11:00Z) | **Night reads**, coded per W263/W265 (a); UP tests per W265 (b) | pending | `round26/scan_hyp_morning.notes.md` (timing line); `round26/scan_plancheck.notes.md` |
| T151 | 29 Sep **07:23Z** prep (10:23 MSK); **M1 CI by 08:45Z** (11:45 MSK; branch A, decide by the 08:40Z header); **branch B M1 non-CI** decide by the 10:30Z header, submit by 10:50Z; **M2 non-CI by 11:30Z** (14:30 MSK) | **Morning batch (<= 2 files)** mechanically from MORNING TABLE v1.1 (W263). UNUSED is the honest default. Only PASSED dummies | pending | `CONTEXT.md` l.3792-3793, l.3904; `round26/report.json` R26-A2 |
| W266 (2) | store before 07:23Z; send **12:03Z** 29 Sep (15:03 MSK) | **FINALS CARD v4** (Russian, MSK first) from the R26F-8 draft with fixes: logged tie order (UP > non-CI > fewer levers > earlier), no "РЕКОМЕНДУЮ" default, row {V_CI, exp75} labelled "CI не застрахован", Q3 note (SEC only as основной), risk column (cap 6 high; SEC high, weight swaps 0/5 on LB; K medium; DIS 2.25 ~0; CI medium-low), 743006 as unverified, PENDING line | not started | `round26/report.json` R26-A5 (2); `round26/report.notes.md` (0/5, tie order) |
| W19 / W73 / W102 / W93 / W165b | standing | ONE poller; header < 15 min old; never resubmit class C or ERRORed files; a SEC file may be a final only as V_pub (Q3 yes, l.3834) | standing | `CONTEXT.md` l.3331-3335, l.3480-3484, l.3834-3836 |
| W261 | before every push | **Dataset pre-push rule:** ft-weights lastUpdated 2026-09-23 23:54:03; n2a 2026-09-27 21:25:35; a change -> stop, diff, tell the user. Never authenticate as a teammate | standing (last checked at probe 51, l.3865-3866) | `CONTEXT.md` l.3692-3703, l.3865-3866 |

## LATER (29 Sep ~12:00Z -> 23:59Z, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| W266 (2) / T60 | **12:03Z** (15:03 MSK) | Send card v4. SEC files may appear only as V_pub (Q3 yes) | `CONTEXT.md` l.3713, l.3834 |
| T152 | **18:37Z** (21:37 MSK) | FINAL proposal. Show any still-PENDING file with its pre-agreed swap (a CI M1 sent near 08:45Z reads 18:03-19:39Z) | `CONTEXT.md` l.3714; `round26/report.json` R26-A4 (d), plan_issues 6 |
| **T160** (new; = R26-A4 (d)) | **19:30Z** (22:30 MSK) | Notify-only job (proposed): re-read the poll; push a one-line V_pub update if it changed. Must be created in the session cron | `round26/report.json` R26-A4 (d) |
| **T161** (new) | **19:43Z** (22:43 MSK) | Notify-only reminder if SELECTED differs from the proposal | `CONTEXT.md` l.3849, l.3854-3855 |
| T10 | **20:00Z (23:00 MSK)** | **The user ticks the finals.** The session never ticks by any route (browser, API, later turn) | `CONTEXT.md` l.3683-3685, l.3851-3855 |
| T153 | ~20:00-20:30Z | Verify API SELECTED = the user's pair (no cron for it; W270) | `CONTEXT.md` l.3474 |
| **T162** (new; supersedes T154) | **21:05Z** (00:05 MSK 30 Sep) | Notify-only job: read SELECTED read-only; if it is not the proposed pair, push the user the exact pair | `CONTEXT.md` l.3851-3855 |
| W177 H2 | 23:00Z | LESSONS H2 | `_curation/20/watch.json` |
| T49 | 23:00-23:45Z | Final public LB snapshot (timer bb224de9 dead; not in the cron; W270) | `CONTEXT.md` l.2619 |
| T11 / **T163** | **29 Sep 23:59Z** (02:59 MSK 30 Sep) | Deadline: a submit must **finish** before it; Kaggle allows re-ticks until then | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765; `CONTEXT.md` l.3848, l.3855 |
| T155 | 30 Sep 00:07Z cron | POST-DEADLINE job: private read v2 + L1-L7 | `CONTEXT.md` l.3714-3715, l.2570-2598 |
| T133 | after the deadline | GPU weekly reset | `CONTEXT.md` l.3689-3690 |
| W29 / curator | after 29 Sep | Post-deadline list, plus z-shift +0.1 after CI; MAX_UM 2.0 note | `round25/report.json` R25-A8 (d) |
| **W270** (new; W258 residue) | before 17:57Z | Confirm the session cron holds: the 22:43 MSK reminder and the 00:05 MSK notify job (l.3849, l.3854-3855); add the 19:30Z notify job (T160), the 17:57Z tick check (T19), a post-tick SELECTED check (T153) and the 23:00-23:45Z LB snapshot (T49). All are session-only | `CONTEXT.md` l.3709-3716, l.3851-3855 |

**Passed or finished time-bound items:**
- R8 new-mechanism cutoff (27 Sep 12:00Z) passed; R8/no-retrain lifted for the rounds (`CONTEXT.md` l.3459-3460). The 28 Sep 12:00Z consolidation is superseded (T46; l.3392-3394). The curation task template still names both as examples.
- T145/T146 done: probe 50 read, probe 51 submitted (l.3856-3870). The 13:00Z hard slot deadline was met.
- Friend replies: none awaited (last friend instruction 26 Sep, l.2175-2176). Teammates are a GPU reserve only (l.3688-3698).
- T156: the tick deadline is 20:00 UTC = 23:00 MSK; never write "20:00" without "UTC" (l.3683-3687).

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I303** (new) | "12:23Z line says 'stack vs exp89p isolates DIS 2.25' - true only for exp89q; if exp89r (CI) goes at 00:05 UTC, exp89r - exp89p = DIS + CI" | `round26/scan_recheck.notes.md`; `CONTEXT.md` l.3896 | In branch A, DIS is readable only as a double difference needing |dd| >= 0.002 (W263 (1)). Tell the user the stack is cleanly readable only in the non-CI variant (plan_issues 4). |
| **I304** (new) | "UP '0' code: 0 teams passed is not proof of 'lower' ... read '0' as 'not higher by more than ~0.0001' = unresolved, never as 'lower'" | `round26/scan_hyp_finals.notes.md` | The finals pool rule (W265 (d)) must not drop a '0' file as lower. |
| **I305** (new) | Dummy-clip GT lab: exp85a 0.92184 (+0.0013 vs exp70g, sign right), exp89q 0.92063 vs exp89p 0.92024, exp88a -0.0008; "Use it only as a gate sanity check, never as a sign read" | `round26/report.json` new_facts 7; `round26/scan_recheck.notes.md` | Only 3 GT divisions and 4 train-copy clips; lives in a scratchpad (`r26/dummy_lab.py`), not in the repo. |
| **I306** (new) | "The DIS 2.25 dummies ran +15-20% vs their siblings (exp88a 1,894 s vs 1,654 s; exp89q 1,576 s vs 1,313 s)"; exp89r at 1,959 s vs rule v2 2,100 s | `round26/report.json` new_facts 6; `CONTEXT.md` l.3920 | exp89l / exp89t gates may run close to 2,100 s; the thin-margin flag above 2,000 s must be logged (T158). |
| **I307** (new) | "K's READMIT adds +0.84% nodes, which costs ~-0.0008 on any embryo, so the raw public K gain was ~+0.0028" | `round26/report.json` new_facts 10; `round26/scan_hyp_finals.notes.md` | The node cost transfers to private for sure; the edge gain does not. Card v4 risk column (K medium). |
| **I308** (new) | Georgy Mamarin 26 Sep in 743006: host says the hidden test shares no embryos with train, roughly train-sized; "a public-best improvement also beat the replaced submission on private ~8/10" | `round26/scan_hyp_finals.notes.md` (743006 line) | Only in a scan note; CONTEXT l.3908-3914 logs only g john rao's claim. Useful base rate for the card. |
| **I309** (new) | "{exp85a, exp75} is FIRST on bronze in all 16 exp85a runs with CI mean >= -0.0003"; "ticked {#37, #38} .48-.66 / .10-.23" | `round26/scan_hyp_finals.notes.md` RESULT 1; `round26/report.json` new_facts 9 | Model-conditional; the crossover is ~-0.0002 at sd .0008 (`v_hyp_finals_r26f-2.notes.md`). |
| **I310** (new; replaces I289) | "Per the denial the session does not pursue the finals tick by any route (browser, API, later turn) ... The user's own tick is the ONLY path." | `CONTEXT.md` l.3851-3855 | If the user does nothing, #37 (0.954) + #38 (0.953) stay. Every proposal and notify job must say so plainly. |
| **I311** (new) | "exp12/exp13 raw ILP geffs in %TEMP% are EMPTY dirs ... cannot re-score" | `round26/scan_recheck.notes.md` 13:25Z | Old lab data is gone; DIS priors rest on logged numbers only (exp13 non-transferable, `round26/report.json` rejected). |
| **I312** (new) | "tools/runtime_ledger.py l.82 maps exp89t to 'safetail' (wrong; it is a CI file)" | `round26/report.json` new_facts 5; `tools/runtime_ledger.py` l.82 | Same class as I276; fix before any exp89t dummy (W264 (2)). |
| **I313** (new) | "CONTEXT l.3187 SEC caveat 'weight swaps were 0/5 on our LB' (R26F-4 said 7) -> use 0/5"; "R26F-8 draft has UP sign wrong AND 2/3 order swapped" | `round26/report.notes.md` | Card v4 text errors already caught once; re-check at the 12:03Z fill. |
| **I314** (new) | "M2 at 11:00Z reads 18:47Z"; a CI M1 at 08:40Z "reads 18:07Z (tail 19:34Z)"; the user "may tick from 20:00 MSK (17:00Z)" | `round26/scan_hyp_morning.notes.md`; `round26/v_hyp_morning_r26m-5.notes.md` | Morning reads land after an early tick; the 18:37Z proposal needs the PENDING branch (W265 (d)). |
| I287 | "The CI_lo 2.2 h model is contradicted: the measured dL is 1.60-2.18 h" | `CONTEXT.md` l.3749-3752 (now logged) | 'ins-tail?' footnote for CI reads with L_hi in (9.6, 10.2] h; applies to exp89r/exp75/exp89l reads. |
| I290 | "exp75 = exp79a node positions + #37 edges"; not an independent CI read | `CONTEXT.md` l.3744-3745, l.3812-3815 | Still true for card v4. |
| I294 | CI lab per clip mixed; the refiner is also z-biased | `round25/scan_plancheck.notes.md` | Card v4 CI caveat (W266 (2)). |
| I295 / I310 | GPU: 2.2 / 2.5-3 / ~3.6 h, unmeasured since 04:55Z | `round26/report.json` new_facts 11 | W269. |
| I297 | Two files completing in one poll window are MASKED | `round25/v_hyp_sched29_r25s-7.notes.md` | Relaxed for a strictly lower completion (W265 (b)); still applies to exp89q/exp89p if both display >= 0.958. |
| I301 | ft-weights has no sha pin; a new dataset version is picked up silently | `CONTEXT.md` l.3697-3703 | W261 before every push and right before the night batch. |
| I302 | Team keeps 5 submits/day in total, from the account that ran the kernel | `CONTEXT.md` l.3692-3693 | - |
| I278 | The synthetic set is José Freitas's kernel output, not hengck23's | `round24/report.json` R24-A10 (b) | CONTEXT l.3510 still says hengck23 (W244). |
| I72 / I116 / I145 | No Co-Authored-By; timers die with the session; a submit must finish before the deadline | `memory/feedback-git-no-coauthor.md`; `CONTEXT.md` l.3715-3716 | Last 12 commit bodies comply (0 hits). The cron is session-only. |
| Older I-rows | Unchanged | `_curation/25/watch.json`, `_curation/24/watch.json` | - |

**Resolved since ~11:00Z (curation 25):**
- I288 (morning CI cutoff): 08:45Z adopted (`CONTEXT.md` l.3792-3793, l.3904).
- I291 (never rebuild exp75): logged (l.3810-3813).
- I292 (uptest.py not in repo): `tools/uptest.py` (l.3832).
- I293 (exp88c gate before output): logged 11:17Z, PASS 11:19Z (l.3794-3803, l.3824).
- I296 (crowd-source hypothesis): probe 50's read did not cite it (l.3856-3862).
- I298 / I299 (exp88b / exp88a priors): moot; R0 branch not realised.
- I300 (feed/watch thresholds): raised to 0.958 (`tools/kaggle_feed.py` l.172; `e10_watch_loop.py` l.78).
- I274 (SI gate on a K BASE): gates now run vs the exp85a dummy (l.3908-3920).
