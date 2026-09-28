# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-27 ~23:50 UTC (curation 21). This updates the curation-20 build of 20:53 UTC (`research/KNOWLEDGE/_curation/20/watch.json`). Rows not repeated here are unchanged in `_curation/20/watch.json`, `_curation/19/watch.json` or `_curation/18/watch.json`.

**Sources read for this update:**
- `CONTEXT.md` (3,331 lines; `## 9. Literature` starts at l.3311). New entries since curation 20:
  - 21:05Z READ TABLE v3 CODES + W1/W2 v3 (l.3222-3285);
  - 21:06Z N2 PRE-REGISTRATION (l.3286-3295);
  - 21:06Z LEDGER + BUILD (l.3296-3300);
  - 21:26Z N2 DONE + GATES (l.3301-3306);
  - 22:27Z PROBE 46 READ (l.3307-3310).
- `git log`: 9d0820c (round 20 + REPORT.md), 9e81f06, cc17974, 4ac7126 (last commit, 22:27Z). Git dates are local time (UTC+3).
- `git status`: these are untracked:
  - `research/wf_ideas_v4/round21/`;
  - `experiments/ext_succskip/`;
  - `experiments/e10_watch/2026092*T2*.txt`;
  - `experiments/ds_secw_corwin_v1/weights/`.
- `research/wf_ideas_v4/round21/report.json`: complete, written_utc 23:43:24Z, actions R21-A1..A13. **There is no `round21/REPORT.md`**: the judge's write was blocked, and the Russian text is in `report_md_ru` (see note_report_md).
- The `round21/scan_*.notes.md` files and `round21/report.notes.md`.
- `experiments/lb_poll/poll.log`: last header 23:45:49Z, l.18320. Its newest ref is still 56611472; there has been no 28 Sep submit.
- `experiments/lb_poll/ledger.md`: ledger time 23:45:50Z.
- `experiments/e10_watch/watch_loop.log`: RUN 12 at 23:43:55Z, 0 signals.

All times are UTC. IDs are stable: W = action, T = time-bound reminder, I = insight. The status values are: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at 23:50Z, 27 Sep:**
- **Best display 0.956.** Two files have it:
  - probe 45, exp70g (K2 + cap 6), 56606948;
  - probe 46, exp70q (cap 6 + thr 0.3 + forkmid), 56611472. It read as **code 0**, meaning no visible UP, and was read at 22:25:30Z (`CONTEXT.md` l.3307-3310).
- **Rank:** we are #165, 9th of 52 in the 0.956 block. k = 8 (`round21/report.json` new_facts).
- **Finals are unchanged:** #37 56563521 + #38 56563534 are ticked. The user picks on 29 Sep (`CONTEXT.md` l.3211-3213).
- **The user is asleep** (autonomous night, `CONTEXT.md` l.3217).
- **W1 has not been submitted yet.** The 28 Sep slots reset at 00:00Z:
  - 00:05Z exp78b;
  - ~00:06Z exp79a (CI);
  - 00:50Z exp78a.
  - All three dummies PASSED and are logged (`CONTEXT.md` l.3214, l.3298, l.3304).
- **Round 21 is complete (23:43Z). None of R21-A1..A13 is in CONTEXT yet.**
  - **The first action (R8 COVERAGE line) must land before the exp79a submit at ~00:06Z.**

**Changes since 20:53Z (curation 20):**
- **Done:**
  - W208: exp79a dummy pushed; PASS logged 21:26Z (l.3304). It started within ~4 min of the push (`round21/scan_plancheck.notes.md` 22:45Z).
  - W209: READ TABLE v3 + W1/W2 v3 logged 21:05Z, while 46 was PENDING (header 20:55:15Z, l.3222). This was before 46 went terminal at 22:25:30Z.
  - W206: N2 pre-registration logged 21:06Z (l.3286), before exp77 completed at 21:24Z.
  - W188: ledger family `safetail_ci` added; 24 tests pass (l.3296; `tools/runtime_ledger.py` l.59, l.77-81).
  - W211: dummy gates and builds:
    - (a) exp78b PASS and (b) exp79d PASS are logged (l.3298-3299);
    - (c) exp80a is built and its dummy pushed (l.3299, l.3305).
  - W205: N2 is done. n2a sha 7029fe69 is in the private dataset `biohub-secft-n2a-v1`; exp81 is built and its dummy pushed (l.3301-3303).
  - W213: the probe 46 read was logged 22:27Z (l.3307). Its stale S0 is handled in W217 (c).
  - W204: `round20/` was committed together with `REPORT.md` (9d0820c; `git ls-files research/wf_ideas_v4/round20` lists REPORT.md).
  - T111: round 21 ran (`round21/report.json` 23:43Z).
  - T112: every W1 dummy PASSED and was logged before 23:45Z.
- **Moot or resolved:**
  - T116: the exp79a queue estimate is moot.
  - I229: "CI must be submitted before ~01:30Z" rested on the queue premise. CI does not queue by itself (see I231).
  - I215, I212 (the W1 order conflict is resolved by l.3222) and I203 are also resolved.
- **New:** actions **W216-W223**, reminders **T122-T128**, insights **I231-I248**.

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W216** (new; = **R21-A1**; was R20-A3 (e), PC19-11) | **R8 COVERAGE line, one CONTEXT line, BEFORE the exp79a submit.** It covers:<br>- the coordinject files (exp75/76a/79a/exp83\*);<br>- the secFT files (exp72/76d/79d/exp81/exp82\*).<br>These go under the 27 Sep 11:14Z/11:16Z aggressive-mode directive; SEC also has Q2 yes and N2 has the 18:19:11Z yes. **The user never named coordinject.** All of these files are public-only. None becomes a final without the user's re-tick. Not a precedent.<br>**Fallback:** if the line is not written by 00:06Z, submit exp78b/exp78a on schedule, then write the line, then submit exp79a by 03:00Z at the latest | **overdue**: required since round 19. `grep "R8 COVERAGE" CONTEXT.md` = 0 at 23:37Z | **~00:06Z 28 Sep** (hard 03:00Z) | `round21/report.json` R21-A1; `round21/report.notes.md` 23:37Z; `round21/scan_plancheck.notes.md` ("exp79a at ~00:06Z is the FIRST CI submit") |
| **W185** (= R16-A6 -> R17-A7 -> R18-A2 -> R19-A5 -> R20-A3 -> **R21-A4**) | **RESUME POINT + CORRECTION + MEMORY**, with the text ready in R21-A4 (A)-(C).<br>- The RESUME POINT gets updated facts: best exp70g #165; 46 = code 0; exp77 COMPLETE; the dummy PASS list; the rules list, including the W2 TABLE v4, W4 AMEND 2, CI-RAN GATE and finals card; the timers.<br>- The correction to the 18:56Z read: the right S0 gives 127 passed, not 113; exp70g is **class C** under L9, not class B.<br>- MEMORY rewrite: `memory/project-lb-probe-approval.md` (last written 26 Sep 22:46Z) and MEMORY.md index lines 8/9 still say "E10 port rule proposed" and "26 Sep post-score" | **overdue, 6th round** | ~00:10-01:30Z 28 Sep, after the W1 submits and never delaying them | `grep -n "RESUME POINT" CONTEXT.md` -> l.2599 (26 Sep 22:46Z) is the last; `round21/report.json` R21-A4; `ls -la memory/` (project-lb-probe-approval.md 27 Sep 01:46 local) |
| **W214** (= R20-A9 -> **R21-A9**) | **Finals card lines + E10 SI line.**<br>- V_pub = non-CI, non-SEC while Q3 is open; L_hi <= 9.0 h; the gate did NOT fire. Plus an INFO line for the "best display overall".<br>- Ties go to: UP, then non-CI, then fewer levers, then the earlier submit. F2 = #37 always; never the stack's own cap parent.<br>- Ranges: {V_pub, #37} bronze ~0.55-0.8 / silver ~0.2-0.55; the ticked {#37, #38} ~0.35-0.65 / ~0.03-0.23.<br>- A Russian 12:00Z message.<br>- E10 (v): the trigger is >= 0.957, and SI = BASE's DIVINS settings (cap 6 / fc 1 / thr 0.4), not cap 4 | **overdue** (R20-A9 said "tonight with W209"); not landed per `grep "FINALS CARD"` = 0 | before the first W1 terminal header (~07:30Z 28 Sep); message 29 Sep 12:00Z, refreshed 18:00Z | `round21/report.json` R21-A9; `round20/report.json` R20-A9 |
| **W202** (= R19-A10 + R20-A10 + **R21-A12**) | **Info lines**, no rule:<br>- R20-A10 (1)-(5) and R20-A13 are still missing.<br>- k = 10 (20:02Z) / 8 (22:30Z).<br>- exp70g is ~0.95634 unrounded.<br>- exp70q is in (-8.4e-4, +2e-5] vs exp70g.<br>- L_hi drift 7.54 -> 7.81 h.<br>- Cap rungs are nearly nested.<br>- Curator items: I-084 succskip TP-empty; I-190 geometry filter -0.0087, single-child a no-op; I-051 par10 = one DC-unscored TP; the LESSONS entry "exp60 replay is DC-blind" | **overdue** (R20-A10 said "before round 21") | any CONTEXT write on 28 Sep; R20-A13 before 29 Sep 23:59Z | `round21/report.json` R21-A12; `round21/scan_recheck.notes.md` |
| **W212** (= R20-A7 -> **R21-A11**) | **Read the GPU quota once** and log "<used>/30 h at <time>". This is now information only; triage applies only if < 3 h are left. Always keep >= 1 h for an E10 dummy. Estimate: ~19.5-21 h used | **overdue**: exp80a and exp81 were pushed without the reading R20-A7 required | before the R21-A6 (2) dummies (~08:40Z 28 Sep) | `CONTEXT.md` l.2542 (last reading 07:55/30 h, 26 Sep); `round21/report.json` R21-A11 |
| W126 | **No RESULTS.md rows for probes 39-46.** The last row is probe 38; the last commit to it is b2be382 (26 Sep 07:35Z). **Neither 0.956 file (45, 46) has a row** | overdue (4th round) | before the finals read (29 Sep ~19:00Z) | `experiments/RESULTS.md` (last "LB probe 38" row); `git log -1 -- experiments/RESULTS.md` = b2be382 |
| W174 residue (-> R21-A9 (v)) | The E10 texts still say ">= 0.955" (`experiments/lb_poll/e10_watch_loop.py` l.28, l.78). The runbook SI uses `DIVINS_CAP=4` (`research/wf_ideas_v4/e10v3/runbook.json`, 1 hit) | overdue | with W214; fix at the next loop edit | grep 23:48Z |
| W176 / W177 / W182 | Low priority, still outstanding:<br>- no ROUND 14-21 RECORD;<br>- LESSONS H1 not done (H2 29 Sep 23:00Z);<br>- no `NEVER_SUBMIT.md` in exp70j/exp70k (the folders hold only the ipynb, kernel-metadata and probe.json) | overdue, low | H1 now; H2 29 Sep 23:00Z | `ls experiments/exp70j_k2_dc020 experiments/exp70k_k2_dc0225` 23:48Z; `research/wf_ideas_v4/round9/LESSONS_draft.md` |
| I208 / W202 (a) | The amanatar V6 misattribution is still uncorrected | overdue, low | with W202 | `CONTEXT.md` l.2976-2977 |
| W57 / W66 / W31 / W72 / W150 | Old low-priority text fixes; the round prompt is unchanged | overdue, low | passed | `_curation/20/watch.json`, `_curation/18/watch.json` |

## NEXT 24 H (28 Sep 00:00Z -> 29 Sep 00:00Z)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| T18 | **28 Sep 00:00Z** | Daily slot reset: 5 submits for 28 Sep | - | `CONTEXT.md` l.3217-3221 |
| **W203** (= R20-A11 -> **R21-A2**) | **00:05Z exp78b; ~00:06Z exp79a (only after W216); 00:50Z exp78a** | **W1 submit procedure**, per file:<br>- `kaggle kernels status` = COMPLETE, and the live code diffed against the local notebook;<br>- **submit `-v 1` only; no re-push before 00:50Z** (a re-push invalidates the dummy PASS);<br>- no duplicate; the poll header must be < 15 min old and not a 429;<br>- for exp79a: the CI dataset check (yuki0731/biohub-coord-inject = 10 files dated 2026-08-25);<br>- descriptions "probe 47: exp78b ...", "probe 48: exp79a ...", "probe 49: exp78a ...";<br>- after the submits: the ledger must show exp79a = `safetail_ci`; one waiter per ref;<br>- log "N2 proxy PASS (0.998/1.010, at the band edge)" | not started (poll 23:45:49Z shows no new ref) | `round21/report.json` R21-A2; `CONTEXT.md` l.3250-3257 (v3 (2)), l.565 (submit template) |
| **W217** (new; = **R21-A3**) | tonight; (b) at the latest before exp79a's first terminal header (~09:40Z) | **One CONTEXT write:**<br>(a) **exp81 DUMMY PASS**: SHA 7029fe69; 121,085 nodes (-0.14%); 87 forks; 1,250 s; CSV 8132ef2811d0. **exp80a DUMMY PASS**: 121,252 nodes; 116 forks; 1,388 s; CSV a109ad024ace. Neither is logged; exp79d = fallback only.<br>(b) **CI-RAN GATE**: dL = L_hi(CI) - L_hi(the same-batch non-CI sibling, exp78b):<br>&nbsp;&nbsp;- dL <= 0.5 h -> CI NO-OP (the lever codes '?');<br>&nbsp;&nbsp;- 0.5-1.2 h -> '?';<br>&nbsp;&nbsp;- >= 1.2 h -> the v3 codes apply;<br>&nbsp;&nbsp;- a latency-coded NO-OP never licenses a resubmit.<br>(c) **46 read addendum**: S0 should have been `e10_watch/20260927T2143Z.txt` (#163, k = 8). The re-run gives 0 passed, so code 0 stands. For W1, S0 = the newest download showing the count just before that file's completion.<br>(d) **ERROR rules**: exp79a ERROR at > 10 h -> no resubmit. **Do not delete, re-version or change visibility of `biohub-secft-n2a-v1`, `secft-all-v1`, `ft-weights` or `coord-inject`** until every submission using them is COMPLETE.<br>(e) NO-GO list: exp75, 76a, 72, 76d, 79d; exp76e is filler only | not started | `round21/report.json` R21-A3; `round21/scan_hyp_risk_check.notes.md` |
| **W218** (new; = **R21-A5**) | **before the first exp83\* dummy push (~00:55Z)** | `tools/runtime_ledger.py`: insert `(r"exp83[a-z]*", "safetail_ci")` ABOVE `(r"exp8\d[a-z]*", "safetail")` (now l.81), plus tests (exp83a/c/d/g -> safetail_ci; exp82a-c/84a/80a/81 -> safetail). Until it lands, pass `--family <ref>=safetail_ci` | not started (no exp83 rule; the rules are at l.77-81) | `round21/report.json` R21-A5; `round21/report.notes.md` (EXP_RULES l.70-84) |
| **W219** (new; = **R21-A6**) | (1) **~00:55Z**; (2) by ~12:00Z / ~19:00Z | **CI stack builds + dummy schedule.** Build with the r21w-1 env block exactly (`MSYS_NO_PATHCONV=1`) and check the sha prefix.<br>(1) Push the dummies for **exp83a (exp78b + CI, 80a0856f) and exp83b (exp78a + CI, d9b0834d)** together on 2 lanes. exp83c (e8f5a8a6) is optional if >= 5 h of quota remain.<br>(2) After the DIV reads (~08:40Z), push the SEC and SEC+CI stacks for BASE (exp82a/83e or exp82b/83d). If exp80a becomes BASE: exp83f/82c/83g. exp84a (4cb1e47b) runs only under S3.<br>(3) A dummy QUEUED > 45 min is never re-pushed | not started (no `experiments/exp83*` folders) | `round21/report.json` R21-A6; `round21/scan_hyp_w2_w4_plan.notes.md` (shas) |
| **W185** | ~00:10-01:30Z | See OVERDUE | overdue | R21-A4 |
| T03 fallback | **03:00Z** | The last time exp79a may go if W216 slipped | - | R21-A1 |
| **W220** (new; = **R21-A7**) | **before exp78b's terminal header (~07:30Z)**, quoting the last PENDING header | **W2 TABLE v4 + DIV STOP RULES S1-S6.**<br>- W2a = v3 (3) unchanged: exp80a, else exp81.<br>- W2b 12:00Z order: E10 first; then (i) CI '+' -> exp83a/exp83b by BASE; (ii) exp81; (iii) exp80a; (iv) CI '?' -> the BASE + CI stack; **(v) BASE = exp70g with CI '+' -> the slot moves to W3 (<= 23:30Z)**. v3 (4) would otherwise name exp79a, which is a duplicate.<br>- The BASE lookup table (4).<br>- S3: exp84a only if exp80a displays > exp78b.<br>- S6: no DIV-only file after 29 Sep 01:45Z | not started (`grep "W2 TABLE v4"` = 0) | `round21/report.json` R21-A7; `round21/scan_plancheck.notes.md` (v3 (4) duplicate) |
| **W221** (new; = **R21-A8**) | with W220 (before ~07:30Z) | **29 SEP W4 AMEND 2.**<br>- Order: E10, FULL stack, one file per '?' lever, exp84a only under S3, the non-CI twin of a FULL with CI.<br>- K2-like files at 00:05/00:45/01:25Z; CI files at 00:06/00:46Z.<br>- **At most 4 planned files; the 5th slot is held for E10.**<br>- A stack that reads '0'/'-' after '+' parts = NON-ADDITIVE.<br>- Never: knob, thr, N1, fresh-N2, tau or DC rungs; cap 10/16; fc2 on cap 8.<br>- After 02:00Z: only with the cap-lift yes. An E10 copy is allowed until ~10:00Z | not started | `round21/report.json` R21-A8 |
| T104 (updated) | **~07:35-07:55Z exp78b; ~08:20-08:40Z exp78a; ~09:50-10:40Z exp79a** | Expected completions: cap rungs L ~7.4-7.8 h (drift, I237); CI L 9.7-10.5 h, worst ~10.9 h.<br>- Take one manual `leaderboard -d` within ~10 min of each terminal header.<br>- S0 = the count just before (48, then 49, ...). Log k; k = 0 -> BLIND '?'.<br>- The CI-RAN GATE for exp79a (W217 (b)) | - | `CONTEXT.md` l.3275-3279 (v3 (7)); `round21/report.json` R21-A3 (c), new_facts |
| **W199 + W222** (W222 new; = R20-A12 + **R21-A10**) | **~08:00-09:30Z**, after the first W1 reads | **ONE Russian morning message**: the W1 codes, the W2 choice, the V_pub skeleton. It asks two yes/no questions:<br>(1) lift the 29 Sep 02:00Z cap?<br>(2) **copy a public notebook > our best (>= 0.957) under E10 v3 after 02:00Z 29 Sep, until ~10:00Z?** (default: yes).<br>Answers are needed by ~23:00Z 28 Sep | awaiting user (asleep); **needs a NEW user answer** (covered_by_existing_approval = false) | `round21/report.json` R21-A10; `round20/report.json` R20-A12 |
| T113 | **~08:00-10:30Z** | **Round 22**:<br>- verify that R21-A1..A9 landed BEFORE the relevant headers;<br>- code W1 by count (CI-RAN GATE, 'v');<br>- set BASE; W2a by TABLE v4;<br>- push the BASE dummies; the morning message; the quota | - | `round21/report.json` next_focus |
| W212 | before ~08:40Z | Quota reading (see OVERDUE) | overdue | R21-A11 |
| T117 | **08:45-10:00Z** | **W2a**: exp80a iff exp78b '+', disp(exp78b) >= disp(exp78a), 46 not '-' (it is 0) and the exp80a dummy PASSED (to be logged in W217 (a)). Otherwise exp81 | - | `CONTEXT.md` l.3258-3261; R21-A7 (1) |
| T122 (new) | **11:45Z** | The exp83a/exp83b dummy must have PASSED to be a W2b candidate | - | R21-A7 (2) (i) |
| T106 | **12:00Z** | **W2b** by TABLE v4 (W220). E10 goes first | - | R21-A7 (2) |
| T46 | **12:00Z** | F1 consolidation (R8 lifted for named items) | - | `CONTEXT.md` l.1671 |
| T123 (new) | **~16:15-17:45Z** | The exp80a read, if W2a took it. S3 decides exp84a; push exp83f/82c/83g within ~15 min if exp80a becomes BASE | - | `round21/report.json` R21-A6 (2) |
| T124 (new) | **~17:00-19:00Z** | **Round 23**: the exp80a/exp81 reads, the W3 decision, the W4 file list with PASSED dummies by 00:00Z | - | `round21/report.json` next_focus |
| T19 / W77 | 17:57Z (012fa6dd) | API SELECTED + a page read of the ticks | - | `_curation/18/watch.json` |
| T118 | **~23:00Z** | Latest useful answer to the W222 questions for W4 | - | R20-A12, R21-A10 |
| **W223** (new; = **R21-A13**) | 28 Sep, after R21-A1..A7 | **Commit** `research/wf_ideas_v4/round21/`. **Write `REPORT.md` first** from `report_md_ru`. Also commit CONTEXT, the ledger + test (W218) and `experiments/exp83a*/exp83b*`.<br>- Named paths only; as the user; **no Co-Authored-By trailer** (I72).<br>- Not `_dl/`, `ds_secw_corwin_v1/weights/`, or `ext_succskip/` unless wanted | not started (`round21/` untracked; no REPORT.md) | `round21/report.json` R21-A13, note_report_md; `git status` 23:48Z |
| T114 / T125 (new) | **W3 dummies PASS by ~23:15Z; submit <= 23:30Z** | Only if W2b moved (TABLE v4 (v)): the max stack of '+' levers on BASE not yet scored | - | R21-A6 (2), R21-A7 (2) (v) |
| T100 | hourly at hh:43Z until 29 Sep 12:00Z | E10 v3 watch. 12 runs, 0 signals. Never use it as S0/S1 by time | live | `experiments/e10_watch/watch_loop.log` RUN 12 |
| W19 / W73 | until 29 Sep 20:00Z | ONE poller. The header must be < 15 min old | in progress (23:45:49Z) | `poll.log` l.18320 |
| W102 / W93 / W165b | standing | Never resubmit class C or an ERRORed stack; exp79a is never resubmitted (R21-A7 (2)). Q3 (SEC as a final) stays open | standing / awaiting user | `CONTEXT.md` l.3160-3161; R21-A7 |

## LATER (29 Sep 00:00Z -> 23:59Z, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T126 (new) | **29 Sep 00:00Z** | Every W4 file must have a PASSED dummy | R21-A6 (2), R21-A8 (1) |
| T20 / T107 (updated) | **29 Sep 00:05-01:45Z** | **W4**:<br>- K2-like files at 00:05/00:45/01:25Z; CI files at 00:06/00:46Z;<br>- **<= 4 planned files + 1 held for E10**;<br>- the last submit is 01:45Z unless the user lifts the cap | R21-A8 (W221); `CONTEXT.md` l.3280-3285 |
| T127 (new) | **29 Sep 02:00-~10:00Z** | E10 copy window, only under E10 v3 / W222. Non-CI T_last is ~10:25Z; CI T_last is ~07:30Z | R21-A8 (5) |
| T119 | ~09:30Z | W4 reads land | `round20/report.json` plan_issues |
| T09 / W77 | 11:57Z (328f7392) / 17:57Z (18ff4796) | Tick checks + user reminder | `round19/report.json` R19-A5 |
| T120 | **12:00Z** (refresh **18:00Z**) | **Finals proposal message** {V_pub, #37} using the W214 card. The user ticks; the session never re-ticks | R21-A9 (iv); `CONTEXT.md` l.3211-3213 |
| T60 | 12:00Z | G2 must have landed for a SEC file to be finals-eligible | `CONTEXT.md` l.2736 |
| T121 | 17-18Z | Log N954, for sizing the ranges only | R20-A9 (f) |
| T115 / T48 | **~19:00Z** | FINALS READ and the L9 last read. Q3 deadline. Never a non-COMPLETE file | `CONTEXT.md` l.3194, l.2510-2518 |
| T10 | **20:00Z** | Our buffer for the ticks; re-ticks stay allowed until 23:59Z | R20-A3 (a) |
| W177 H2 | 23:00Z | LESSONS H2 | `_curation/20/watch.json` |
| W178 / W215 | before 23:00Z; hourly 30 Sep | Private-read addenda (priors C/C8/C_thr) | R20-A13; `CONTEXT.md` l.3056, l.3195 |
| T49 | 23:00-23:45Z (bb224de9 23:27) | Final public LB snapshot | `_curation/18/watch.json` |
| T11 | **29 Sep 23:59Z** | Deadline. A submit must **finish** before it | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 |
| T30 / T50 | 30 Sep from 00:15Z | Private read v2 + L1-L7 | `CONTEXT.md` l.2570-2598 |
| W29 / curator | after 29 Sep / by 30 Sep | Post-deadline list:<br>- N1 k 1.5;<br>- DaughterNet v2 at high cap (weights not local, I222);<br>- synthetic pretraining;<br>- untested CI if its read was a NO-OP (W217 (b));<br>- N2 if SEC reads '-'/'0' | R20-A6, R21-A3 (b), R21-A12 |

**Passed or finished time-bound items:**
- The R8 new-mechanism cutoff (27 Sep 12:00Z) has passed. Round 21 kept succskip, geometry filter and par10 closed because of it (`round21/report.json` rejected).
- 46 was read at 22:27Z.
- W1 dummies were logged by 23:45Z.
- Friend replies: there has been no open friend item since 26 Sep (`CONTEXT.md` l.2175-2176).

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I231** (new) | "CI is not queued by itself — exp79a started 20:32:27Z within ~4 min of its push; exp81 and exp80a both started 21:26Z; the account runs 2 GPU lanes; the afternoon 2-3.3 h waits were lane contention or Kaggle-side delay" | `round21/report.json` new_facts | This refutes the queue premise behind I202/I229 and the r21w-3 triage. Dummy timing is set by lane use: never push 3 at once. |
| **I232** (new) | "A fail-soft CI leaves exp70g's CSV byte-identical (visible only by latency)" | `round21/report.json` new_facts; `round21/scan_hyp_risk_check.notes.md` (coordinject "all inside try -> fail-soft") | Without the CI-RAN GATE (W217 (b)), a hidden no-op reads as a false '0' or a noise '+'. It must land before ~09:40Z. |
| **I233** (new) | "secswap ... raise FileNotFoundError (module level, NOT fail-soft) only if no manifest with the sha exists"; mount layout "/kaggle/input/<slug>" vs "/kaggle/input/datasets/<owner>/<slug>" varies per run | `round21/scan_hyp_risk_check.notes.md` | Any cleanup or re-version of `biohub-secft-n2a-v1` before exp81/exp82\* are COMPLETE turns a SEC file into an ERROR (W217 (d)). |
| **I234** (new) | "main-process RAM at ~100 videos + 2 CI workers (each loads one 100x64x256x256 uint16 video, 0.84 GB raw) is untested -> residual CI ERROR mode" | `round21/scan_hyp_risk_check.notes.md` | This is the only unbounded CI ERROR mode (< ~5%). An exp79a ERROR at > 10 h must not trigger a resubmit (R21-A3 (d)). |
| **I235** (new) | "ledger rule exp8\d[a-z]* -> safetail (9.5 h) catches any CI stack named exp82*/exp83* ... would print UNPROVEN/REJECT + 'v' wrongly" | `round21/scan_plancheck.notes.md`; `round21/scan_hyp_w2_w4_plan.notes.md` | This could drop an eligible CI stack from the W/finals cards. W218 must land before ~00:55Z. |
| **I236** (new) | "exp70g ~0.95634 unrounded (uniform density), so a 0.957 on the exp70g base needs only ~+1.6e-4; exp70q in (-8.4e-4, ~+2e-5] vs exp70g" | `round21/report.json` new_facts; `round21/scan_hyp_w2_w4_plan.notes.md` | A '+' on the cap-6 base can come from a +1.6e-4 change, within noise. Do not quote it as a large lever effect. This is only in the W202 info lines. |
| **I237** (new) | "Latency drift K2-family L_hi: 7.54 (26 Sep) -> 7.58 -> 7.74 -> 7.67 -> 7.81 h (46)" | `round21/scan_plancheck.notes.md` | A cap rung can get 'v' (L_hi > 8.0 h) with no code cause, which matters for V_pub's L_hi <= 9.0 h clause. |
| **I238** (new) | "exp70g does NOT reproduce with this order (762c16.. vs repo 52c182..): older K-with-CAP=4-then-override order" | `round21/scan_hyp_w2_w4_plan.notes.md` 22:40Z | Any "exp70g + X" stack must be built with the r21w-1 env block and diffed against exp70g. It cannot be regenerated byte-identically. |
| **I239** (new) | MC: "partner choice dominates (#37 vs own parent: -0.17..-0.34 bronze); F1 choice among cap-family stacks moves P by <= ~0.04" | `round21/scan_hyp_w2_w4_plan.notes.md` | This is the core of the finals message (W214). Picking F1 barely matters, while pairing a file with its own cap parent does real harm. |
| **I240** (new) | "exp60 replay (DCLookup) is DC-blind for arms that loosen a gate before DeepCenter ... round-13 par10/sis16/nomnn/div1.75 ... are unfiltered upper bounds (~3.5-4x volume)" | `round21/scan_recheck.notes.md`; R21-A12 | LESSONS gap: old round-13 numbers overstate volume. It is not in LESSONS_draft yet (W177). |
| **I241** (new) | "OUTPUT_SINGLE_CHILD_REPAIR=1: exact no-op ... presafe graphs hold 0 forks ... On x138 every fork is a safe division or an insertion" | `round21/scan_recheck.notes.md` 23:5xZ | A structural FACT about x138 that is not yet in FACTS/CONTEXT (R21-A12). It closes every "ILP-fork" idea. |
| **I242** (new) | "S0 = ladder_watch/20260927T185549Z, not 'newest count-47 download' ... k not logged"; the judge: "a stale S0 can hide an UP" | `round21/scan_plancheck.notes.md`; `round21/report.json` rejected (PC21-06) | The same mistake as the 45 read (I216). The W1 reads need S0 = the count just before (W217 (c)). |
| **I243** (new) | Submit template "-k <kernel> -v 1": "W1 kernels must have exactly the dummy-gated version" | `CONTEXT.md` l.565; `round21/scan_plancheck.notes.md` | Any re-push of exp78b/79a/78a before 00:50Z would submit an ungated version (R21-A2). |
| **I244** (new) | "E10 loop runs to 29 Sep 12:00Z but last submit 01:45Z 29 Sep and W4 may use all 5 slots -> a trigger 02:00-12:00Z has no slot/permission" | `round21/scan_plancheck.notes.md` | This is fixed only if W221 (the 5th slot held) and W222 (the user's yes) both land. |
| **I245** (new) | "v2 (4) 'K2-like files >= 40 min apart' -> max 3 K2-like (00:05/00:45/01:25) in that window" | `round21/scan_plancheck.notes.md` | W4 cannot hold 5 K2-like files. A plan listing 5 silently breaks the stagger rule. |
| **I246** (new) | "N2 n2a proxy 0.998/1.010 vs pre-reg band ~0.99-1.01 ... boundary, no explicit PASS word in the 21:26Z line" | `round21/scan_plancheck.notes.md`; `CONTEXT.md` l.3302 | The PASS must be logged in words (R21-A2). The stricter <= 1.007 idea was rejected as post-hoc. |
| **I247** (new) | "exp79a vs exp70g: same 238,335 keys, 78,320 rows with changed z/y/x (CI survived to the final CSV)" | `round21/scan_hyp_risk_check.notes.md` | This is the dummy proof that CI changes the output. On the hidden set only latency shows it (I232). |
| **I248** (new) | "k = 8 (it was 11 at 18:55Z, 10 at 20:02Z, 9 at 20:43Z, 8 at 21:43Z and 22:43Z)"; "Four new teams strictly above us all came from our block or below" | `round21/report.json` new_facts | We lose ~1 place per hour without submitting. k -> 0 makes every UP test BLIND '?'. Take a fresh S0 near each completion. |
| I216 | The 18:56Z read used the wrong S0 (113 vs 127) and called exp70g class B, but it is class C | `round20/scan_plancheck.notes.md` | Still uncorrected in CONTEXT (W185 (B)). |
| I217 | The runbook SI uses DIVINS_CAP=4; the loop LOOK text says >= 0.955 | `research/wf_ideas_v4/e10v3/runbook.json`; `experiments/lb_poll/e10_watch_loop.py` l.28/l.78 | Verified at 23:48Z. W214 (v). |
| I201 | CONTEXT still says "L ~9.6-9.8 h" for CI | `CONTEXT.md` l.3068 | The current model is 9.4-10.6 h, worst ~10.9 h (`round21/report.json` new_facts). |
| I206 | "tools/dummy_gates.py: no coordinject/secswap mode" | `round19/scan_plancheck.notes.md` | The exp83\*/exp82\* gates stay manual (W219). |
| I209 | N1 staging folders `_dl/secft_x2_ds` / `_dl/secft_x3_ds` | `round19/scan_hyp_n1_prep.notes.md` | Easy to upload by mistake. N1 is banned in W3/W4 (R21-A8 (4)). |
| I218 / I219 | Keep FRAME_CAP <= 2. All lab gain for cap >= 8 comes from 2 6bba clips | `round20/scan_hyp_insertion_direction.notes.md` | Now in the R21-A8 (4) "never fc2 on cap 8 / cap 10/16" rule. Never quote the lab as private support. |
| I223 | "#37 wins iff y<0<x ... as F1's cap rises \|y\| grows -> #37 dominates" | `round20/scan_recheck.notes.md` | This supports I239 when V_pub moves to cap 8/12/24. |
| I227 | John Taylor: "finals = best + closest one-line neighbour"; José Freitas: synthetic data at 0.960 | `round20/scan_browser.notes.md`; https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/732103 | This contradicts {V_pub, #37}. Round 21 saw no new discussion (`round21/scan_browser.notes.md`). |
| I72 | The harness adds a co-author trailer; the user's rule says no Co-Authored-By | `memory/feedback-git-no-coauthor.md` | Applies to W223. |
| I116 / T67 | Agents label local times as "Z"; cron fields are LOCAL (UTC+3); timers die with the session | `round18/report.json` R18-A2 (2) | Applies to every W1 waiter and to the round 22 timer. |
| I145 | A submit must finish before the deadline | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 | T11; CI T_last ~07:30Z 29 Sep. |
| Older I-rows | Unchanged | `_curation/20/watch.json`, `_curation/19/watch.json` | - |

**Resolved since 20:53Z:**
- I215: exp79a was pushed and PASSED (`CONTEXT.md` l.3304).
- I229 and I202: the queue premise is refuted (I231).
- I212: the W1 order was settled by v3 (`CONTEXT.md` l.3250-3257).
- I203: the S0/S1 rule was written into v3 (7).
- I228: exp80a has 116 forks, inside (86, 153] (`round21/scan_hyp_risk_check.notes.md`).
