# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-27 ~20:50 UTC (curation 20). Updates the curation-19 build of 18:40 UTC (`research/KNOWLEDGE/_curation/19/watch.json`); rows not repeated here are unchanged there or in `_curation/18/watch.json`.

Sources read for this update:
- `CONTEXT.md` (3,242 lines; `## 9. Literature` at l.3222). New entries since curation 19:
  - 18:50Z PRE-SCORE AMENDMENT (l.3075-3111) and 28 SEP READ TABLE v2 (l.3112-3195);
  - 18:56Z PROBE 45 READ: exp70g = **0.956**, #162 (l.3196-3200);
  - 19:01Z cap-direction rungs exp78a/exp78b/exp76e (l.3201-3205);
  - 19:05Z exp76a dummy clean, exp77 (N2) pushed, exp79a/exp79d built (l.3206-3210);
  - 19:10:58Z USER: finals picked on 29 Sep after all variants (l.3211-3213);
  - 20:02Z exp78a/exp76e dummies clean, round 20 launched, 46 waiter set (l.3214-3216);
  - 20:30Z USER: autonomous night, W1 = 3 cap-family files (l.3217-3221).
- `git log`: a2e0696 (round 19), ca663c1 (probe 45), 7cd6a0e, bd7d7a4, cdeeb2d, 32eeedd, 771a608 (last, 20:30Z). Git dates are local (UTC+3).
- `git status`: untracked `research/wf_ideas_v4/round20/`, `experiments/e10_watch/20260927T2043Z.txt`, `experiments/ds_secw_corwin_v1/weights/`.
- `research/wf_ideas_v4/round20/report.json` (complete, written_utc 20:45:36Z; actions R20-A1..A14). **No `round20/REPORT.md`**: the judge's write was blocked, and the Russian text sits in `report_md_ru` (`report.json` note_report_md).
- `round20/scan_*.notes.md`, `round20/report.notes.md`.
- `experiments/lb_poll/ledger.md` (ledger time 20:45:15Z); `poll.log` (last header 20:45:13Z, l.17222).
- `experiments/e10_watch/watch_loop.log` (RUN 9 at 20:43:55Z, 0 signals).

All times are UTC. IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State in one line (20:50Z 27 Sep):**
- **New team best: probe 45 exp70g (K2 + insertion cap 6) 56606948 = 0.956**, #162 -> #163 at 20:02Z (`CONTEXT.md` l.3196; `ledger.md` row 56606948: L (7.49, 7.67] h, insertion gate did NOT fire).
- **Finals are unchanged**: #37 56563521 + #38 56563534. The user picks on 29 Sep after all variants are scored (`CONTEXT.md` l.3211-3213).
- **Probe 46 exp70q 56611472 is PENDING** (`ledger.md` 20:45:13Z, L > 6.13 h; 8.0 h mark 22:36:59Z). Waiter set (l.3215).
- **The user is asleep (20:30Z, autonomous night)** (l.3217). Every question now waits until ~08:00Z 28 Sep.
- **Round 20 is complete (20:45Z).** **None of R20-A1..A14 is in CONTEXT yet**: the last entry is 20:30Z (l.3217). The session's 20:30Z W1 plan (exp78a, exp78b, exp76e) differs from the judge's (exp78b, CI exp79a, exp78a) (`round20/report.json` R20-A2 (2)).
- **Kaggle state (20:33Z judge check, `round20/report.notes.md`):**
  - exp78b and exp79d dummies COMPLETE (exp78b gate recounted, not yet logged; exp79d not gated);
  - exp77 (N2 training) RUNNING;
  - **exp79a (the CI dummy on the cap-6 base) = 404, never pushed**, although l.3208 says it follows in the lane.
- **E10 v3 loop:** 9 runs, 0 signals (`watch_loop.log`).

**Changes since 18:40Z (curation 19):**
- **Done:**
  - W195: pre-score amendment logged 18:50Z (l.3075), before 45 was terminal (18:54:54Z);
  - W196: READ TABLE v2 logged 18:50Z (l.3112); now partly superseded by R20-A2 (W209);
  - W198: exp76a dummy clean, 121,252 / 74 forks / 117,076 edges (l.3206);
  - W202 (b): exp72 gate values logged (l.3101-3102);
  - W205 (push part): exp77 pushed 19:04Z (l.3207); `NEVER_SUBMIT.md` added;
  - W207: 46 waiter set (l.3215);
  - W204 (round 19 part): `round19/` committed (a2e0696); `exp77_secft_n2/` committed (7cd6a0e/bd7d7a4);
  - W199 (partly): finals question sent 19:01Z (l.3204); user answered 19:10:58Z (l.3211);
  - T95: probe 45 read 18:56Z (l.3196).
- **Superseded or moot:**
  - W197 (exp76c/exp76g): replaced by the cap-6-base builds exp79a/exp79d (l.3208; `round20/scan_plancheck.notes.md`); exp76e built and clean (l.3214);
  - W200 (tau rung exp77a): moot, no user yes; row C is gone from v3 (R20-A2 (2));
  - W201 (W2 stacks exp76f/i/j/k): superseded by R20-A2 (3)-(4) and R20-A5 (e);
  - I198 (N2 banned by round 19): resolved by R20-A6 (W206), once logged;
  - I200 (exp77 name collision): the tau rung is dropped; exp77 carries `NEVER_SUBMIT.md`.
- **New:** actions **W208-W215**, reminders **T116-T121**, insights **I214-I230**.

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W208** (new; = R20-A1) | **Push the exp79a dummy NOW** (`vitaliineibauer/biohub-exp79a-k2cap6-coordinject`, sha 5f9b265d = exp70g + coordinject a0.5, 3 um). CI kernels queue 2-3.3 h. **Never re-push it once QUEUED.** Gate: validate ok; nodes 121,252; edges and forks == the exp70g dummy (81 forks); COORDINJECT 4/4, ~91.5% moved; 0 error markers | **overdue**: 404 at 20:33Z, although l.3208 put it in the lane at 19:05Z | now (<= 21:00Z); PASS by 03:00Z 28 Sep, else the CI slot falls back to exp76a | `round20/report.json` R20-A1; `round20/report.notes.md` 20:33Z; `CONTEXT.md` l.3208 |
| **W185** (= R18-A2 -> R19-A5 -> **R20-A3**) | **RESUME POINT + R8 coverage line + correction line + MEMORY rewrite** (text ready in R20-A3 (A)-(C)).<br>- The last RESUME POINT is 26 Sep 22:46Z (l.2599).<br>- `memory/project-lb-probe-approval.md` (modified 25 Sep) still says "E10 v1 in force ... retrain needs explicit yes".<br>- No "R8 coverage" line: the user never named coordinject.<br>- Correction: the 18:56Z read used S0 = ladder_watch 131353Z (113 passed); the pre-registered S0 gives **127**; exp70g is **class C** under L9, not class B | **overdue, 5th round** (R16-A6, R17-A7, R18-A2, R19-A5, R20-A3) | now (<= 21:30Z), before R20-A2 if possible | `grep -n "RESUME POINT" CONTEXT.md` -> l.2599 last; `CONTEXT.md` l.3196-3197; `round20/scan_plancheck.notes.md`; `round20/report.json` R20-A3 |
| **W209** (new; = R20-A2) | **READ TABLE v3 CODES + W1/W2 v3**, one CONTEXT line, **before 46 is terminal**.<br>- Own-base codes (exp70g 0.956 for cap-6-base files; exp70b 0.954 for exp76*; #37 for exp75/exp72); 46 = 0.955 is '-' for its increment only, never row D.<br>- W1: 00:05Z exp78b; CI exp79a on PASS (<= 03:00Z, else exp76a at 03:00Z); 00:50Z exp78a; exp76e dropped (filler only); no thr-0.3/0.2 rung.<br>- W2a (08:45-10:00Z): exp80a on condition, else the ONE SEC file (N2, else exp79d). W2b 12:00Z held for E10.<br>- DIV stop rules; reads within ~10 min of each terminal header; W4 amend (one DIV step) | not started; **it conflicts with the logged 20:30Z plan** (exp78a, exp78b, exp76e) | before 56611472 is terminal (target <= 21:45Z; earliest ~22:00Z) | `round20/report.json` R20-A2; `CONTEXT.md` l.3217-3221; `poll.log` l.17222 (20:45:13Z, 46 PENDING) |
| **W206** (updated; = R20-A6) | **N2 PRE-REGISTRATION**:<br>- N2 file = exp70g + the GPU0 epoch-2 secondary only; the GPU1 recipe is never submitted;<br>- gates: SHA256 line, detection proxy ~0.99-1.01, nodes -2%/+1% of 121,252, <= 1,920 s;<br>- the ONE SEC file of 28 Sep (exp79d = fallback); public-only while Q3 is open;<br>- never a new single rung in W3/W4. | not started; exp77 RUNNING at 20:33Z | before exp77 completes (~22:00Z); at the latest before its dummy | `round20/report.json` R20-A6; `CONTEXT.md` l.3070-3074 (18:19Z entry targets the stale exp70b base) |
| W126 | **No RESULTS.md rows for probes 39-45.** The last row is probe 38 (l.71); last commit b2be382 (26 Sep 07:35Z). **Probe 45 = 0.956, the team best, has no RESULTS row** | overdue | before the finals read | `experiments/RESULTS.md` l.71; `git log -1 -- experiments/RESULTS.md` |
| W176 | No ROUND 14-20 RECORD in CONTEXT (`grep -c "ROUND 1[4-9] RECORD"` = 0) | overdue, low priority | after the 46 read | `CONTEXT.md` grep 20:50Z |
| W177 (= R17-A9) | LESSONS H1. `LESSONS_draft.md` has not changed since bf07763 | overdue | H1 now; H2 29 Sep 23:00Z | `research/wf_ideas_v4/round9/LESSONS_draft.md`; `git log -1` = bf07763 |
| W182 | No `NEVER_SUBMIT.md` in exp70j/exp70k (class C). exp70n still has no row (I196) | not started | before any 28 Sep submit | `ls experiments/exp70j_k2_dc020 experiments/exp70k_k2_dc0225` 20:50Z |
| W174 residue (-> R20-A10 (5)) | E10 v3 text: the trigger is now own public score > 0.956 (>= 0.957). `e10_watch_loop.py` l.28/l.78 and runbook l.66 still say ">= 0.955"; **runbook SI (B) l.206 uses DIVINS_CAP=4 while our best is cap 6** | overdue | with W185 | `round20/scan_plancheck.notes.md`; `round20/report.json` R20-A10 (5) |
| W57 / W66 / W31 / W72 | "frozen/duplicated frames"; `out_valid` / `efpost` / `33.1%` | overdue, low priority | passed | `_curation/18/watch.json` |
| W150 | Round prompt unchanged (js 13a27a1, 26 Sep). Rounds 19-20 still produced no ROUND RECORD | overdue, low priority | before round 21 | `git log -1 -- experiments/workflows/biohub-research-round.js` |

## NEXT 24 H (27 Sep 20:50 -> 28 Sep 20:50 UTC)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| **W213** (new; = R20-A8; was T96) | **~22:00-22:40Z**; 8.0 h mark **22:36:59Z**; hard edge 00:00Z | **Probe 46 read.**<br>- S0 = newest download with count 47 (e.g. `e10_watch/20260927T2002Z.txt`: #163, k = 10);<br>- S1 = the first manual download with count 48 (LSD cross-check 14:36:59);<br>- v3 codes: >= 0.957 '+'; 0.956 + UP '+'; 0.956, 0 passed '0'; <= 0.955 '-' (drop exp80a).<br>Log L next to exp70g's (7.49, 7.67] h | PENDING (L > 6.13 h at 20:45:13Z) | `round20/report.json` R20-A8; `ledger.md` row 56611472 |
| **W211** (new; = R20-A5) | W1 gates by **23:45Z**; exp79a by **03:00Z**; exp80a and N2 by **~08:30Z 28 Sep** | **Dummy gates and builds:**<br>(a) log exp78b PASS (121,252 / 117,092 / 95 forks, ~1,368 s, cap_video 12, cap_frame 2);<br>(b) download and gate exp79d (Secondary ed8c616b line, nodes -2%/+1%, <= 1,920 s);<br>(c) build exp80a (cap 24, FRAME_CAP 2); push after exp79a is QUEUED; forks in (86, 153], expected ~115;<br>(e) the exp78b + CI stack only if quota used <= ~24 h (W212) | (a) recounted by the judge, not logged; (b) COMPLETE, not gated; (c) no `exp80*` folder | `round20/report.json` R20-A5; `ls experiments` 20:50Z |
| **W212** (new; = R20-A7; was I210) | **tonight, before pushing exp80a (~21:30-22:30Z)** | **Read the GPU quota once** (Kaggle Settings) and log "<used>/30 h at <time>". Priority when short: exp79a > N2 dummy > exp80a > exp78b + CI stack. Skip the stack if > ~24 h; also exp80a if > ~26 h; keep only exp79a + N2 if > ~28 h. Reset Sat 3 Oct 00:00Z | not started; last reading 07:55/30 h at ~21:56Z 26 Sep; estimate ~19-25 h used | `round20/report.json` R20-A7; `CONTEXT.md` l.2542 |
| **W188** (= R18-A5 -> R19-A6 -> **R20-A4**) | **before 00:05Z** (at the latest before the first W1 read ~07:30Z) | `tools/runtime_ledger.py`:<br>- `FAMILIES['safetail_ci']` (10.75 h / divins 10.2 h);<br>- rules before exp70: exp75*, exp76[acfhi], exp79a* -> safetail_ci; exp7[2-9]*, exp8\d* -> safetail;<br>- tests for exp78a/78b/80a/76e/79d (safetail) and exp79a/76a (safetail_ci);<br>- re-run: exp70g row unchanged, 56611472 no longer "family unknown" | not started, **4th round** (EXP_RULES ends at l.76 `exp70[a-z]*`) | `round20/report.json` R20-A4; `tools/runtime_ledger.py` l.76 |
| **W214** (new; = R20-A9) | tonight with W209; at the latest before the first W1 terminal header (~07:30Z 28 Sep) | **29 SEP FINALS CARD LINES**:<br>- V_pub = highest display among COMPLETE cap-family files (non-CI; SEC excluded while Q3 is open), L_hi <= 9.0 h, gate did NOT fire;<br>- a higher dose replaces exp70g only on a strictly higher display or an attributable UP; ties go to the smaller dose;<br>- proposal {V_pub, #37}; never two DIV-volume files; never {V_pub, exp70b};<br>- model ranges, per-partner hedges, the DIV caveat (winner's curse); the session never re-ticks | not started | `round20/report.json` R20-A9 |
| **W202** (updated; = R19-A10 + **R20-A10**) | next CONTEXT write, before round 21 (22:30Z) | Info lines:<br>(1) R20ID-1 is a lab NULL (CI90 includes 0; dropping 2 6bba clips flips every arm); keep fc <= 2;<br>(2) probe 45 falsifies the R15 closure on the PUBLIC embryo only;<br>(3) cap/fc/thr cost ~0 runtime;<br>(4) no R8 item in round 20;<br>(5) E10 v3 text (W174).<br>Still open from R19-A10: (a) amanatar V6 is not a division read; (d) N1 x2/x3 weights stay local.<br>Curator items by 30 Sep (I-066/067, R20ID-6, I-076-078, I-063, I-069, R14-RC-C) | not started | `round20/report.json` R20-A10; `round19/report.json` R19-A10 |
| **W203** (updated; = R19-A11 -> **R20-A11**) | **28 Sep 00:05Z exp78b; CI exp79a on PASS (<= 03:00Z, else exp76a at 03:00Z); 00:50Z exp78a** | Per file: no duplicate; poll header < 15 min old, not a 429; dummy PASS logged; for CI the dataset check (yuki0731/biohub-coord-inject = 10 files dated 2026-08-25). Knob values in the description; a waiter per ref; push notification at each submit. **The 00:05Z waiter from R19-A5 (PID 18920) echoes "exp72, exp75": stale** | not started | `round20/report.json` R20-A11; `round19/report.json` R19-A5 |
| **W215** (new; = R20-A13; extends W178) | any CONTEXT write before 29 Sep 23:59Z | PRIVATE-READ addendum, priors for the 3-dp contrasts: C = exp70g - #37 .30/.25/.45; C8 = exp78a - #37 .30/.20/.50; C_thr = exp70q - exp70g .35/.30/.35; C_fm only if both score. Never a finals input | not started | `round20/report.json` R20-A13 |
| **W204** (updated; = R20-A14) | tonight, after W209/W185/W188 | Commit `research/wf_ideas_v4/round20/` (**write `REPORT.md` first from `report_md_ru`**), CONTEXT, ledger + test, `experiments/exp80a*/`. Named paths only; no `_dl/`, `ds_secw_corwin_v1/weights/`, `e10_watch/*`, `ledger.md`/`poll.log` unless intended; **no Co-Authored-By trailer** (I72) | not started (`round20/` untracked) | `round20/report.json` R20-A14, note_report_md; `git status` 20:50Z |
| **W205** (updated) | exp77 done ~22:00-22:30Z (pushed 19:04Z, ~2.5-3 h) | **N2 outputs -> NEW private datasets** (never re-version `biohub-secft-all-v1`, I199) -> N2 file on exp70g -> dummy by ~08:30Z. Only the GPU0 recipe (W206) | in progress (RUNNING at 20:33Z) | `CONTEXT.md` l.3207, l.3218-3219; `round20/report.notes.md` |
| **W199** (updated; = **R20-A12**) | **28 Sep ~08:00-09:30Z**, after the first W1 reads | ONE Russian message: W1 codes (display, UP, k), the W2a/W2b choice, V_pub and the {V_pub, #37} skeleton with R20-A9 ranges. **ONE yes/no question: lift the 29 Sep 02:00Z cap** (default: W4 00:05-01:45Z). Q3 stays open; ask it only if a SEC file tops the display | awaiting user (asleep since 20:30Z); needs a NEW user answer (covered_by_existing_approval = false) | `round20/report.json` R20-A12 |
| W165b / Q3 | 29 Sep 19:00Z | SEC file as a final. Open; not asked again unless a SEC file tops the display | awaiting user | `round20/report.json` R20-A3 (f), R20-A12 |
| W19 / W73 | until 29 Sep 20:00 | ONE poller. Header < 15 min old and not a 429 before any submit | in progress (last header 20:45:13Z) | `experiments/lb_poll/poll.log` l.17222 |
| W102 / W93 | standing | Never resubmit class C (exp70j/k) or an ERRORed stack; an ERRORed single gets one unchanged resubmit only if its ERROR latency < 10 h. exp77 (training) is never a submission | standing | `CONTEXT.md` l.3160-3161; `experiments/exp77_secft_n2/NEVER_SUBMIT.md` |
| T100 | hourly at **hh:43Z** (next 21:43:42Z) until 29 Sep 12:00Z | E10 v3 watch run. **Never use its snapshot as S1** (R20-A2 (7)); the trigger is now >= 0.957 (W174) | live, 0 signals in 9 runs | `experiments/e10_watch/watch_loop.log` |
| T111 (updated) | **22:30Z** (timer set, l.3215) | **Round 21**: checks that W209 and W185 were logged BEFORE 46 was terminal; codes 46; dummy PASS table by 23:45Z; quota; ledger rules; E10; 00:05Z readiness | - | `round20/report.json` next_focus |
| T116 (new) | **~23:15Z-00:40Z** | Expected exp79a dummy PASS if pushed ~21:00Z (queue 2-3.3 h + ~0.5 h run) | - | `round20/report.json` R20-A1 why |
| T112 (updated) | **23:45Z** | Every W1 dummy PASSED and logged (exp78b, exp78a; exp79a has until 03:00Z) | - | `round20/report.json` R20-A5 deadline |
| T18 / T42 (updated) | **28 Sep 00:00Z** reset; **00:05Z exp78b; 00:50Z exp78a; CI on PASS <= 03:00Z** | W203 | - | `round20/report.json` R20-A2 (2) |
| T104 (updated) | **28 Sep ~07:30-11:00Z** (CI later, see I229) | Expected W1 completions: exp78b ~07:30-07:50Z, exp78a ~08:20-08:40Z (cap rungs L ~7.4-7.7 h); CI ~9.7-10.5 h after its submit. One manual `kaggle competitions leaderboard -d` within ~10 min of each terminal header | - | `round20/report.json` R20-A2 (7) |
| T113 (updated) | **28 Sep ~08:00-10:30Z** | Round 22: W1 reads by count; W2a/W2b choice; the morning message (W199) | - | `round20/report.json` next_focus |
| T117 (new) | **28 Sep 08:45-10:00Z** | **W2a**: exp80a if exp78b '+', exp78b >= exp78a, 46 not '-', exp80a PASSED; else the ONE SEC file (N2, else exp79d) | - | `round20/report.json` R20-A2 (3) |
| T106 (updated) | **28 Sep 12:00Z** | **W2b**, held for E10 v3 until then. Order: E10 copy; CI '+' -> best base + CI; else SEC; else exp80a; else best base + CI | - | `round20/report.json` R20-A2 (4) |
| T46 | **28 Sep 12:00** | F1 consolidation (R8 lifted for the named items) | - | `CONTEXT.md` l.1671; l.2955-2971 |
| T19 / W77 | **28 Sep 17:57** (012fa6dd) | API SELECTED + page read of the ticks | - | `_curation/18/watch.json` |
| T67 | standing | Timers are session-only; cron fields are LOCAL (UTC+3). Background Bash waiters die with the session | - | `round19/report.json` R19-A5 |

## LATER (28 Sep 20:50 -> 29 Sep 23:59 UTC, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T118 (new) | **28 Sep ~23:00Z** | Latest useful answer to the 02:00Z cap question (W199) for it to change W4 | `round20/report.json` R20-A12 deadline |
| T114 | **28 Sep <= 23:30Z** | W3 (if a slot is left): only + levers that B* lacks; never knob rungs, DC, tau or N1; N2 only inside the full stack (W206) | `CONTEXT.md` l.3163-3170; `round20/report.json` R20-A6 |
| T35 | 28 Sep 22:00 | Final admission table: 45, 46, W1/W2/W3 files, E10 v3 copies | `research/wf_ideas_v3/FINAL_REPORT.md` l.178 |
| T20 / T107 (updated) | **29 Sep 00:00Z** reset; **W4 00:05-01:45Z, <= 5 files, E10 first**; allowed: the full '+' stack (N2 inside), '?'-lever stacks, at most ONE DIV step (cap 48 fc2 only after two strict steps). Last submit 01:45Z unless the cap is lifted | `round20/report.json` R20-A2 (8); `CONTEXT.md` l.3171-3175 |
| T98 | **29 Sep 02:00Z** target for a verbatim E10 copy; the loop ends 29 Sep 12:00Z | `experiments/e10_watch/watch_loop.log` l.1 |
| T119 (new) | **29 Sep ~09:30Z** | W4 reads land (structural: three read rounds W1 -> W2 -> W4) | `round20/report.json` plan_issues "Structural" |
| T60 | **29 Sep 12:00** | G2 must have landed for a SEC file to be finals-eligible (Q3 = yes only) | `CONTEXT.md` l.2736 |
| T120 (new) | **29 Sep 12:00Z and 18:00Z** | **Finals proposal to the user** ({V_pub, #37}, R20-A9 card); the user ticks; the session never re-ticks | `CONTEXT.md` l.3211-3213; `round20/report.json` R20-A3 (a) |
| T09 / W77 | **29 Sep 11:57** (328f7392) / **17:57** (18ff4796) | Tick checks + user reminder | `round19/report.json` R19-A5 |
| T121 (new) | **29 Sep 17-18Z** | Log N954 (count of teams >= 0.954) for range sizing only; no count flips the pick | `round20/report.json` R20-A9 (f) |
| T115 | **29 Sep 19:00Z** | Q3 answer deadline; FINALS READ ~19:00Z | `CONTEXT.md` l.3194 |
| T48 (= W131) | **29 Sep ~19:00** | L9 last read. Never two byte-identical files; never a non-COMPLETE file | `CONTEXT.md` l.2510-2518 |
| T10 | **29 Sep 20:00** | Our buffer, not a Kaggle freeze; re-ticks are allowed until 23:59Z | `round20/report.json` R20-A3 (a) |
| W178 / W215 | before 29 Sep 23:00Z; hourly 30 Sep | Private-read addenda; key on a non-empty privateScore (I180). Add 56606948, 56611472 and every 28/29 Sep ref | `CONTEXT.md` l.3056, l.3195 |
| T49 | 29 Sep 23:00-23:45 (bb224de9 at 23:27) | Final public LB snapshot | `_curation/18/watch.json` |
| T11 | 29 Sep 23:59 | Deadline. A submit must **finish** before it | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 |
| T30 / T50 | 30 Sep from 00:15Z | Private read v2 + L1-L7 + W178/W215 | `CONTEXT.md` l.2570-2598 |
| W192 + W179 / W147 / W166 + R19-A10 / R20-A10 curator items | by 30 Sep | Curator edits (see W202) | `round20/report.json` R20-A10 |
| W29 | after 29 Sep | Post-deadline list: N1 k = 1.5 (I-384), DaughterNet v2 ranker at high cap (I-063), synthetic-data pretraining (thread 732103), primary head FT, LOEO DC; N2 if SEC reads '-' or '0' | `round20/report.json` R20-A6, R20-A10 |

**Passed or finished time-bound items (for the record):** R8 new-mechanism cutoff 27 Sep 12:00Z (passed; W4 rules keep "no new mechanism", `CONTEXT.md` l.3112); T95 (45 read 18:56Z); T109 (exp76c push, superseded); T110 (message sent 19:01Z, l.3204); T96 -> W213. Friend replies: no open friend item since 26 Sep (`CONTEXT.md` l.2175-2176; `_curation/18/watch.json`).

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I214** (new) | "The judge's Write of round20/REPORT.md was blocked by the harness ... the Russian report is in report_md_ru for the main session to write" | `round20/report.json` note_report_md | A commit of `round20/` without REPORT.md leaves the only readable round-20 report inside a 49 KB JSON. W204 |
| **I215** (new) | exp79a "404 (never pushed)" at 20:33Z, while CONTEXT 19:05Z says its dummy follows exp78b "in the lane (79d first, then 79a)" | `round20/report.notes.md` 20:33Z; `CONTEXT.md` l.3208-3209 | The lane chain did not push exp79a. Each hour of delay moves the only on-base CI read toward the 03:00Z cutoff. W208 |
| **I216** (new) | "CONTEXT 18:56 used S0 = ladder_watch 131353Z (#268) and logs 113 -> S0 deviation + wrong count"; "cap is NOT in the [L9 class B] list -> exp70g is class C by L9; 18:56 entry calls it class B" | `round20/scan_plancheck.notes.md` | The live CONTEXT entry misstates the pre-registered read and the finals class of our best file. The fix is only in R20-A3 (B) (W185) |
| **I217** (new; part of W174) | "runbook l.206 SI K uses DIVINS_CAP=4"; `e10_watch_loop.py` l.28/l.78 LOOK text say ">= 0.955" | `round20/report.notes.md`; `round20/scan_plancheck.notes.md` | An E10 (B) copy built from the runbook would use cap 4, not our best cap 6. The loop text would treat a 0.955/0.956 notebook as a signal |
| **I218** (new) | "unc_fcU (no frame cap) -0.00022 ... 519 steals; adj edge -0.00055 (steal edge damage)"; "cap40_fc3 +0.00088 ... -> frame cap 3 worse than 2" | `round20/scan_hyp_insertion_direction.notes.md` | The only robust lab result of round 20: keep FRAME_CAP <= 2 in any W4 DIV step. It sits in an info line (R20-A10 (1)), not in the W4 rule text |
| **I219** (new) | "44b6 stays -0.00079 vs K2 for every cap >= 6 (one FP fork in 44b6_e29f0176)"; "Dropping 6bba_9a41d029 and 6bba_337b1b3a flips every arm negative" | `round20/scan_hyp_insertion_direction.notes.md`; `round20/report.json` R20-A10 (1) | Every lab argument for cap >= 8 comes from 2 clips of one embryo. It must not be quoted as private support in the 29 Sep finals message |
| **I220** (new) | "Controls: 43/44 DC 0.20/0.225 (more SAFE divisions, 96/88 dummy forks) = 0.954 tie -> extra safe-div forks do NOT pay publicly; extra INSERTION forks do" | `round20/scan_recheck.notes.md` | Not in any plan text. It argues against any DC rung (already closed) and explains why only insertion knobs moved the LB |
| **I221** (new) | "Both flips same direction: lab undervalues forks" (dc0.30 and cap 6); "probe 45 shows the exp60 lab is blind (not mis-signed) for small marginal add sets" | `round20/scan_recheck.notes.md`; `round20/report.json` R20-A10 curator | Two lab/public sign flips on division knobs. The judge calls the lab "blind", the scan calls it "wrong in one direction". The finals caveat must say which |
| **I222** (new) | "nosteal0 44b6 0.0000 -> lab's 44b6 TP came from a steal"; "DaughterNet v2 weights NOT local (weights_dataset/vitalii_daughternet has only v1 fold_0..4.pt)" | `round20/scan_recheck.notes.md` | Steal OFF is closed for a reason (I-068). The post-deadline "v2 ranker at high cap" (I-063) needs weights that are not on disk |
| **I223** (new) | "#37 wins iff y<0<x; #38 wins iff x<0 ... At cap 6 a wash (~1e-4); as F1's cap rises \|y\| grows -> #37 dominates" | `round20/scan_recheck.notes.md` | The finals pair rule {V_pub, #37} grows more important if V_pub moves to cap 8/12/24. R20-A9 (d) has the cap-6 numbers only |
| **I224** (new) | MC "P(probe 46 display): 0.955 0.19, 0.956 0.57, 0.957 0.08, >=0.958 0.11, <=0.954 0.05"; "cap 8 is the weakest volume rung" (E +0.0007, P(>= 0.957) 0.40) | `round20/scan_hyp_insertion_direction.notes.md` | A 0.956 for 46 is the modal outcome (a '0' or '+' by UP). exp78a at 00:50Z is the least informative W1 file by this model |
| **I225** (new) | "Knobs: cap, frame cap and thr leave nodes_scored identical (3869/6988/661/20770)"; "Dummy-time spread is Kaggle noise; do not call exp70q's 1,874 s an insertion cost" | `round20/report.json` new_facts, R20-A10 (3) | Cap-family L_hi > 8.0 h is a Kaggle slowdown ('v'), not a code cost. Matters for V_pub's L_hi <= 9.0 h clause |
| **I226** (new) | Field growth ">=0.960 0.83/h, 0.955-0.959 2.3/h"; "N_final ~4,008 -> bronze #400, silver #200"; "X+ (exact x138) private rank median 540" | `round20/scan_hyp_private_view.notes.md` | The medal cut-offs used by every finals range. Private rank ~540 for a verbatim public copy explains why E10 copies are never finals by default |
| **I227** (new) | John Taylor (97th): "finals = best + closest one-line neighbour (not diversity)"; José Freitas: synthetic data "I'm at 0.960", details after the deadline | `round20/scan_browser.notes.md`; https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743929 ; https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/732103 | The outside finals advice conflicts with our {V_pub, #37} hedge. Round 20 rejects porting it (no mechanism). Synthetic data is post-deadline only (W29) |
| **I228** (new) | "exp80a fork expectation corrected to ~115 (105-120): at cap 12, 6bba_05b6850b skipped 21 on cap_video and 6bba_05db0fb1 skipped 116"; R20ID-3 had said ~104 | `round20/report.notes.md` 20:33Z | A copied gate band from the scan (~104) would false-FAIL exp80a. Use (86, 153], expected ~115 (W211 (c)) |
| **I229** (new; derived) | CI L is "~9.7-10.5 h" and the CI slot runs "up to 03:00Z", while W2b is decided at 12:00Z | `round20/report.json` R20-A2 (2), (4), (7) | Arithmetic: a CI file submitted at 03:00Z completes ~12:40-13:30Z, after W2b. Only a CI submit before ~01:30Z reads before 12:00Z; otherwise W2b runs with CI = '?' (v2 (3), `CONTEXT.md` l.3139). Push exp79a now (W208) |
| **I230** (new) | "cap6 steal_frac 1.0 -0.00009"; "cap6_nosteal -0.00202"; "size-scaled cap ... +0.0003 / 0.37" | `round20/scan_hyp_insertion_direction.notes.md` | Closed by schedule, not refuted (R20-A10 curator). They must not be re-proposed as new mechanisms in W4 (R8 cutoff passed) |
| I199 | The secondary loader is HARD-fail on a sha mismatch; a missing file -> ERROR | `round19/scan_plancheck.notes.md` | Still live for N2: new datasets only (W205). exp79d/exp76d/exp72 attach `biohub-secft-all-v1` (`round20/scan_plancheck.notes.md`) |
| I201 | CI hidden stage 2.2-2.85 h; CONTEXT l.3067 says "L ~9.6-9.8 h" | `round19/scan_plancheck.notes.md` | Now also in R20-A2 (7) (~9.7-10.5 h); CONTEXT l.3067 is still stale |
| I202 | CI kernels queue for hours; the CI submission rerun may queue too | `round19/report.notes.md` 18:22Z | See I229 |
| I203 | Never use the hourly E10 snapshot as S0/S1 by time | `round19/report.json` R19-A1 (1) | Now written into v2 (l.3077-3090) and R20-A2 (7). Resolved once W209 is logged |
| I205 | dc0.30 lab-positive, public -0.005 | `round19/scan_recheck.notes.md` | Joined by probe 45 (I221) |
| I206 | "tools/dummy_gates.py: no coordinject/secswap mode" | `round19/scan_plancheck.notes.md` | Every CI/SEC/N2/cap gate stays manual (W211). exp79a's gate is exp70g's counts, not exp75's |
| I207 | Latency order inversion; >= 40-min stagger | `round19/scan_hyp_reads_table.notes.md` | exp78b 00:05Z and exp78a 00:50Z keep 45 min apart (R20-A2 (2)) |
| I208 | amanatar V6 is not a division read; `CONTEXT.md` l.2976-2977 still cites it | `round19/scan_recheck.notes.md` | Still not corrected (W202 (a)) |
| I209 | N1 staging folders `_dl/secft_x2_ds` / `_dl/secft_x3_ds` with ready dataset ids | `round19/scan_hyp_n1_prep.notes.md` | Easy to upload by mistake tonight next to the N2 upload (W205) |
| I211 | The user never named coordinject | `round19/scan_plancheck.notes.md` | Still no R8 coverage line (W185, R20-A3 (e)); exp79a/exp76a go at 00:05-03:00Z |
| I212 (updated) | The 00:05Z waiter (PID 18920) echoes "exp72, exp75"; the 20:30Z plan and R20-A2 now disagree on W1 | `round19/report.json` R19-A5; `CONTEXT.md` l.3217-3221 | A resumed session without W209 would follow the 20:30Z order (exp76e in W1) |
| I213 | exp71 was a tiny change: "rel L2 0.3-2.7%, detection proxy 0.995-1.007" | `round20/report.json` R20-A6 why | Reason N2 GPU0 is the one SEC read; log its node delta vs exp79d |
| I188 | exp71 used one GPU of the T4x2 | `round18/scan_hyp_new_levers.notes.md` | Check that exp77 kept both GPUs busy in its log |
| I72 | Harness trailer vs the user's no-co-author rule | `memory/feedback-git-no-coauthor.md` | For W204 |
| I116 | Agents label local times as "Z"; cron fields are local | `round18/report.json` R18-A2 (2) | For every new waiter |
| I145 | A submit must finish before the deadline | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 | T107 / T11 |
| I154 / I165 / I174 / I175 / I180 / I181 / I182 / I190 / I191 / I192 / I194 / I196 and older | Unchanged | `_curation/19/watch.json`, `_curation/18/watch.json` | I194 now: 11th of 52 in the 0.956 block (`round20/scan_plancheck.notes.md`) |

**Resolved since 18:40Z:**
- I198: N2 gets a slot via R20-A6 (W206), pending its CONTEXT line.
- I200: the tau rung exp77a is dropped; `exp77_secft_n2/NEVER_SUBMIT.md` exists.
- I204: superseded by the v3 own-base codes (R20-A2 (1)).
- I210: moved into W212.
- I187: the 46 waiter exists (`CONTEXT.md` l.3215).
