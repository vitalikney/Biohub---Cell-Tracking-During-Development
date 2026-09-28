# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-28 ~01:42 UTC (curation 22). This updates the curation-21 build of 27 Sep 23:50Z (`research/KNOWLEDGE/_curation/21/watch.json`). Rows not repeated here are unchanged in `_curation/21/watch.json`, `_curation/20/watch.json`, `_curation/19/watch.json` or `_curation/18/watch.json`.

**Sources read for this update:**
- `CONTEXT.md` (3,398 lines; `## 9. Literature` starts at l.3378). New entries since curation 21:
  - 00:00Z R8 COVERAGE (l.3311-3315);
  - 00:00Z ROUND 21 GATES + READ RULES (R21-A3) (l.3316-3337);
  - 00:06Z W1 SUBMITS 47/48 (l.3338-3341);
  - 00:50Z W1 SUBMIT 49 (l.3342-3343);
  - 01:02Z R21-A5/A6 (l.3344-3346);
  - 01:02Z W2 TABLE v4 + DIV STOP RULES (l.3347-3365);
  - 01:02Z 29 SEP W4 AMEND 2 (l.3366-3377).
- `git log`: d36a4b2 (round 21 + REPORT.md), b0bac2e, 978124d, ad5cbaf, bb3c299, acbea01 (last, 01:02Z). Git dates are local time (UTC+3). None of the last 8 commit bodies has a Co-Authored-By trailer (`git log -8 --format=%b`).
- `git status`: untracked are `research/wf_ideas_v4/round22/`, `experiments/ext_succskip/`, `experiments/ext_corwin-biocel-aux/_booster/`, `experiments/ds_secw_corwin_v1/weights/`, `experiments/e10_watch/20260928T0043Z.txt`, `experiments/e10_watch/20260928T0103Z.txt`.
- `research/wf_ideas_v4/round22/REPORT.md` and `report.json` (complete, written_utc 01:32:52Z, actions **R22-A1..A11**), `round22/report.notes.md`, and the five `round22/scan_*.notes.md` files.
- `experiments/lb_poll/poll.log`: last header 01:26:07Z (l.18930). `experiments/lb_poll/ledger.md`: ledger time 01:26:09Z; 47/48/49 all PENDING.
- `experiments/e10_watch/watch_loop.log`: RUN 13 at 00:43:54Z, 0 signals; next run 01:43:42Z.
- `tools/runtime_ledger.py` l.80; `experiments/lb_poll/e10_watch_loop.py` l.28/l.78; `experiments/RESULTS.md`; the auto-memory folder `C:/Users/vital/.claude/projects/c--Users-vital-Documents-kAGGLE-Biohub---Cell-Tracking-During-Development/memory/` (listed here as `memory/`).

All times are UTC. IDs are stable: W = action, T = time-bound reminder, I = insight. The status values are: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at 01:40Z, 28 Sep:**
- **Best display 0.956** = exp70g (probe 45, 56606948), L (7.49, 7.67] h (`experiments/lb_poll/ledger.md`). exp70q (46) also shows 0.956 and read code 0 (`CONTEXT.md` l.3307-3310).
- **Rank:** #168, 10th of 59 in the 0.956 block, k = 9, 158 teams strictly above us (`round22/report.json` new_facts; `experiments/e10_watch/20260928T0103Z.txt`).
- **W1 is submitted and PENDING at 01:26:07Z** (`poll.log` l.18930; `ledger.md`):
  - 47 exp78b 56623073 at 00:06:09Z;
  - 48 exp79a (CI) 56623105 at 00:06:33Z;
  - 49 exp78a 56624341 at 00:50:37Z.
  - Two 28 Sep slots are left: W2a ~08:45-10:00Z and W2b 12:00Z (`CONTEXT.md` l.3342-3343).
- **CI stack dummies** exp83a/exp83b were pushed at 01:01Z and were RUNNING at 01:28:54Z (`CONTEXT.md` l.3344-3346; `round22/report.notes.md`).
- **Finals are unchanged:** #37 56563521 + #38 56563534 are ticked. The user picks on 29 Sep (`CONTEXT.md` l.3211-3213).
- **The user is asleep** (autonomous night, `CONTEXT.md` l.3217).
- **Round 22 is complete (01:32:52Z). None of R22-A1..A11 is in CONTEXT yet** (`grep` for "CI-STACK DUMMY GATE", "PRE-SCORE CLARIF", "FINALS CARD" and "CORRECTION to the 18:56" = 0 at 01:36Z).
  - **R22-A1 must land before the exp83a/b outputs are read (~01:40Z).**
  - **R22-A2/A3/A4 must land by the hard stop at 06:45Z.** 47 could go terminal at ~06:58Z at the earliest (`round22/report.notes.md`).

**Changes since 23:50Z (curation 21):**
- **Done:**
  - W216 (R21-A1): R8 COVERAGE logged 00:00Z (`CONTEXT.md` l.3311), before the exp79a submit at 00:06:33Z (l.3338). The pre-submit check "this line is present" is part of it (l.3315).
  - W203 (R21-A2): the W1 submits went on time (l.3338-3343). The checks were: kernels COMPLETE with v1 = the dummy, header 23:55:50Z with no 429, no duplicate, R8 line present, CI dataset 10 files dated 2026-08-25 (l.3339-3340). The ledger shows exp79a = `safetail_ci` (10.75 h) (`ledger.md`). **Residue:** the probe 49 CONTEXT record lacks the ref, time and family; that goes in W225 (5).
  - W217 (R21-A3) (a)-(e): logged 00:00Z (l.3316-3337), with N2 proxy "0.998/1.010 at the band edge" (l.3318).
  - W218 (R21-A5): the ledger rule `exp83[a-z]*` -> `safetail_ci` is at `tools/runtime_ledger.py` l.80; 25 tests pass (`CONTEXT.md` l.3344).
  - W219 (1) (R21-A6): exp83a (80a0856f) and exp83b (d9b0834d) are built and their dummies pushed (l.3344-3345). Part (2) continues as W226.
  - W220 (R21-A7): logged 01:02Z (l.3347-3365), quoting the 00:56:01Z PENDING header.
  - W221 (R21-A8): logged 01:02Z (l.3366-3377).
  - W223 (R21-A13): `round21/` was committed with `REPORT.md` (d36a4b2; `git ls-files research/wf_ideas_v4/round21` lists REPORT.md), with no trailer.
  - T113: round 22 ran early, 01:03-01:33Z (`round22/report.notes.md`).
  - T18: the 00:00Z slot reset passed; 3 of 5 slots are used (l.3342).
- **Moot or resolved:**
  - T03 fallback (03:00Z exp79a) is moot: exp79a went at 00:06:33Z.
  - I235, I243, I245, I246, I242, I232, I233, I234 and I201 have landed in CONTEXT (see "Resolved" at the end).
  - T46 (F1 consolidation 28 Sep 12:00Z) is **superseded** by the user letter of 27 Sep 19:10:58Z (l.3211). The supersession line is pending as W225 (3).
- **Re-mapped:**
  - W185 -> R22-A2;
  - W214 -> R22-A4;
  - W212 -> R22-A5;
  - W202 += R22-A9;
  - W222 -> R22-A8.
- **New:** actions **W224-W229**, reminders **T129-T134**, insights **I249-I261**.

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W224** (new; = **R22-A1**) | **CI-STACK DUMMY GATE line, one CONTEXT line, BEFORE either exp83a/exp83b dummy output is pulled or read.** An exp83a (exp83b) dummy PASSES iff all of these hold:<br>(1) validate ok;<br>(2) 0 Traceback/FAILED/DEADLINE:/FALLING BACK;<br>(3) COORDINJECT 4/4 with ~91.5% of rows moved;<br>(4) the 7 non-coordinate columns are identical to the exp78b (exp78a) dummy CSV: 121,252 nodes / 117,092 (117,086) edges / 95 (86) forks;<br>(5) a changed integer z/y/x fraction of 0.60-0.69 (ref 0.646);<br>(6) <= 2,100 s.<br>Check it with a pandas compare. If the output was already listed first, add "(written after the output was listed ...)" | **due now**: both dummies were RUNNING at 01:28:54Z with ~01:30-01:40Z expected; `grep "CI-STACK DUMMY GATE" CONTEXT.md` = 0 at 01:36Z | **~01:40Z 28 Sep**; PASS check by 11:45Z | `round22/report.json` R22-A1; `round22/scan_plancheck.notes.md` (exp70g vs exp79a 0.6459; _dl dummy counts) |
| **W185** (= R16-A6 -> ... -> R21-A4 -> **R22-A2**) | **RESUME POINT + CORRECTION + MEMORY**, with the text ready in R22-A2 (1)-(3).<br>(1) A new RESUME POINT: finals, BEST #168 k = 9, the W1 refs, the dummy PASS list, rule pointers (l.2917, l.2927, l.3171-3194, l.3222, l.3311, l.3316, l.3347, l.3366 + the round-22 lines), OPEN items (Q3, cap lift, E10 after 02:00Z, finals pair) and the timers.<br>(2) CORRECTION to the 18:56Z read: S0 = `e10_watch/20260927T1743Z.txt` (count 46, #288) -> 127 passed, not 113; exp70g is **class C**, not B.<br>(3) Rewrite `memory/project-lb-probe-approval.md`: the description still says "E10 v1 in force"; mtime 27 Sep 01:46 local. Also MEMORY.md index lines 8/9 | **overdue, 7th deferral** | "now (~01:45Z)"; **hard stop 06:45Z** | `grep -n "RESUME POINT" CONTEXT.md` -> l.2599 (26 Sep 22:46Z) is the last; `round22/report.json` R22-A2; `ls -la memory/` |
| **W214** (= R20-A9 -> R21-A9 -> **R22-A4**) | **FINALS CARD + E10 v3 NOW line.** R21-A9 goes in verbatim, with (iii) superseding (c). Two changes:<br>(A) **a balanced CI caveat**: the lab a0.5 +0.0022 with the sign flipping by alpha; Eric lab +0.0078 -> LB -0.002 twice vs V1284 probe 31 +0.002 (confounded by -2.9% nodes); private risk = an in-sample refiner on new embryos;<br>(B) **the E10 trigger = a public notebook above our best display (now >= 0.957; 0.958 if 47/49 shows 0.957)**; SI = BASE's DIVINS settings (exp70g: CAP 6, FC 1, THRESH 0.4, STEAL 1, ALPHA 1), not cap 4; E10 files join V_pub with no 0.955 floor.<br>Quote a header showing all three W1 refs PENDING | **overdue, 2nd deferral** (`grep "FINALS CARD"` = 0) | **hard stop 06:45Z 28 Sep**; Russian message 29 Sep 12:00Z, refreshed 18:00Z | `round22/report.json` R22-A4; `round21/report.json` R21-A9 |
| **W225** (new; = **R22-A3**) | **PRE-SCORE CLARIFICATIONS, one entry quoting a header with 47/48/49 PENDING:**<br>(1) **CI-? SCOPE**: W2 v4 (2)(iv) and W4 AMEND 2 (1)-2 stack CI only for a '?' from MASKED/BLIND or 0.5 < dL < 1.2 h with L_hi <= 10.2 h. A NO-OP, 'v' or ERROR CI gets no CI stack; W2b falls to (v).<br>(2) If a DIV ref is not terminal at 10:00Z, the exp80a condition fails -> W2a = exp81; exp80a may still take W2b (iii).<br>(3) R13-A1 (5) "F1 consolidation by 28 Sep 12:00Z" is SUPERSEDED.<br>(4) The CI T_last after 02:00Z is moot.<br>(5) Probe 49 record: ref 56624341, 00:50:37Z, header 00:45:59Z, family safetail.<br>(6) The S3 exp84a pre-submit prior: cap48fc2 vs cap24fc2 = 0 TP / +4 FP | not started (`grep "PRE-SCORE CLARIF\|CI-? SCOPE"` = 0) | **before the first W1 terminal header; hard stop 06:45Z** (it becomes post-hoc after) | `round22/report.json` R22-A3; `CONTEXT.md` l.2709-2710 (R13-A1 (5)), l.3320-3334 vs l.3353-3354, l.3368 (the conflict) |
| **W212** (= R20-A7 -> R21-A11 -> **R22-A5**) | **Read the GPU quota once** (https://www.kaggle.com/settings) and log "<used>/30 h at <time>". It also settles whether T4x2 bills at 1x or 2x: ~20.6-22 h used at 1x, ~25-26.5 h at 2x. By hours left:<br>- >= 5 h -> the tables only;<br>- 3-5 h -> no speculative stack dummies; keep >= 1 h for E10;<br>- < 3 h -> the FULL dummy only; keep 1 h for E10.<br>With no reading, assume the 3-5 h case | **overdue, 3rd deferral**: the exp83a/b dummies were pushed 01:01Z without a reading | **before the next dummy push** | `CONTEXT.md` l.2542 (last reading 07:55/30 h, 26 Sep); `round22/report.json` R22-A5 |
| W126 | **No RESULTS.md rows for probes 39-46** (and 47-49 after their reads). The last row is probe 38 (`experiments/RESULTS.md` l.71); the last commit to it is b2be382 (26 Sep). **Neither 0.956 file (45, 46) has a row** | overdue (5th round) | before the finals read (29 Sep ~19:00Z) | `git log -1 -- experiments/RESULTS.md` = b2be382 |
| W202 (= R19-A10 + R20-A10 + R21-A12 + **R22-A9**) | **Info lines + curation**, no rule:<br>- the R21-A12 set (k values, exp70g ~0.95634, exp70q bounds, L_hi drift, nested cap rungs, I-084/I-190/I-051, "exp60 replay is DC-blind");<br>- plus R22-A9 (a)-(h): the insertion-knob lab (fc2 at cap 6 +0.0002 = -1 FP; a05 0; a0 = volume; a2/a3 -0.0017/-0.0022); ALPHA closed; DaughterNet fold subset refuted; I-046 "nearest failure-class record, counter-record probe 31"; the division-supply anatomy on I-080/059/060/064; the I-082 MITO3 rewrite; the John Taylor knobs as log-only | overdue (R21-A12 part); R22-A9 not started | 28 Sep after A1-A4; R20-A13 before 29 Sep 23:59Z | `round22/report.json` R22-A9; `round21/report.json` R21-A12 |
| W174 residue / I217 (-> R22-A4 (B)) | The E10 texts still say ">= 0.955": `experiments/lb_poll/e10_watch_loop.py` l.28 and l.78. The runbook SI hardcodes `DIVINS_CAP=4`, and its finals default is "display >= 0.955, #37" (`research/wf_ideas_v4/e10v3/runbook.json`). **Do not restart the loop for a text change** | overdue | fix at the loop's next planned edit | grep 01:36Z; `round22/scan_plancheck.notes.md` |
| W176 / W177 / W182 | Low priority, still outstanding:<br>- no ROUND 14-22 RECORD;<br>- LESSONS H1 not done (H2 29 Sep 23:00Z);<br>- no `NEVER_SUBMIT.md` in exp70j/exp70k (the folders hold only the ipynb, kernel-metadata and probe.json) | overdue, low | H1 now; H2 29 Sep 23:00Z | `ls experiments/exp70j_k2_dc020 experiments/exp70k_k2_dc0225` 01:36Z; `research/wf_ideas_v4/round9/LESSONS_draft.md` |
| I208 / W202 (a) | The amanatar V6 misattribution is still uncorrected | overdue, low | with W202 | `CONTEXT.md` l.2976-2977 |
| W57 / W66 / W31 / W72 / W150 | Old low-priority text fixes; unchanged | overdue, low | passed | `_curation/20/watch.json`, `_curation/18/watch.json` |

## NEXT 24 H (28 Sep 01:40Z -> 29 Sep 00:00Z)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| **W224** | **~01:40Z** | CI-STACK DUMMY GATE line, then the pandas check (see OVERDUE) | due now | R22-A1 |
| T100 | **01:43Z**, then hourly at hh:43Z until 29 Sep 12:00Z | E10 v3 watch. 13 runs, 0 signals. **The 23:30-02:00Z submit burst scores at ~07-09Z**: watch for P2 clusters and any public notebook > 0.956. Never use it as S1 | live | `experiments/e10_watch/watch_loop.log` RUN 13; `round22/report.json` new_facts, next_focus (5) |
| **W185** | **~01:45Z**, hard 06:45Z | RESUME POINT + CORRECTION + MEMORY | overdue | R22-A2 |
| **W226** (new; = **R22-A6**, continues W219 (2)) | builds **tonight, before ~06:45Z**; dummies when reachable, **no later than ~21:00Z** for W4 | **Rebuild the 9 missing stacks, CPU only, no push.** Only exp80a/81/83a/83b exist in `experiments/`. Use the r21w-1 commands (Git Bash, `MSYS_NO_PATHCONV=1`, the exact `--set` order). Expected sha prefixes:<br>82a ffc00631 · 82b 7cd1e3ed · 82c ee431244 · 83c e8f5a8a6 · 83d 22ccc1dd · 83e a016cf0f · 83f c8a2fccb · 83g 00f8cb36 · 84a 4cb1e47b.<br>- On a mismatch: diff against the parent and log it; do not "fix" knobs.<br>- Check the ledger families (82* safetail, 83* safetail_ci, 84a safetail).<br>- Push a dummy only when a read makes that stack reachable, subject to the W212 thresholds | not started | `round22/report.json` R22-A6; `research/wf_ideas_v4/round21/v_hyp_w2_w4_plan_r21w-1-verified-build-commands.json`; `ls -d experiments/exp8*` 01:36Z (4 folders) |
| **W228** (new; = **R22-A10**) | **before round 23 (~03:30Z)** | Update the **workflow task template key facts**. It still says "E10 successor >= 0.956", "finals by row 3", "R8 hard line" and "consolidation 28 Sep 12:00". New facts:<br>- E10 trigger > our best (>= 0.957), SI = BASE's DIVINS;<br>- finals #37+#38 ticked, the user picks 29 Sep, proposal {V_pub, #37} at 12:00/18:00Z;<br>- BEST exp70g 0.956; W1 refs;<br>- R8 COVERAGE; no 28 Sep 12:00Z consolidation | not started | `round22/report.json` R22-A10 (PC22-11) |
| **T130** (new) | **~03:30-04:00Z** | **Round 23**, a SHORT verification round with no lever search:<br>(1) R22-A1..A4 landed, with header quotes;<br>(2) the exp83a/b gate result;<br>(3) the quota and 1x/2x billing;<br>(4) the nine rebuilt shas;<br>(5) the E10 burst;<br>(6) pre-fill the morning brief | - | `round22/report.json` next_focus |
| **W225** | **by 06:45Z (hard)** | PRE-SCORE CLARIFICATIONS (see OVERDUE) | not started | R22-A3 |
| **W214** | **by 06:45Z (hard)** | FINALS CARD + E10 v3 NOW line | overdue | R22-A4 |
| **T129** (new) | **06:45Z** | **Hard stop for every pre-score rule line** (R22-A2/A3/A4). The safetail latency floor is 6.69 h, so 47 can be terminal from ~06:58Z. Anything logged after a W1 score is post-hoc | - | `round22/report.notes.md` ("Earliest W1 terminal") |
| **W229** (new; = **R22-A11**) | after W226, **before ~07:00Z** | **Commit named paths only**, as the user with **no Co-Authored-By trailer** (I72): CONTEXT.md, IDEAS.md, `research/wf_ideas_v4/round22/`, the nine `experiments/exp82*/exp83[c-g]*/exp84a*` folders, and `experiments/lb_poll/ledger.md` if changed.<br>- Never `git add -A`.<br>- Leave `ds_secw_corwin_v1/weights/` (8 MB), `ext_corwin-biocel-aux/_booster/` and the e10 snapshots untracked | not started (`round22/` untracked) | `round22/report.json` R22-A11; `git status` 01:35Z |
| **W227** (new; = **R22-A7**) + T104 (updated) | **from ~06:58Z to ~11:00Z**. Expected: **47 ~07:28-08:00Z; 49 ~08:12-08:45Z; 48 (CI) ~09:30-10:42Z** | **W1 read procedure:**<br>- one waiter per ref;<br>- **S0 = the newest download showing count 48** before 47's terminal header; an hourly e10 snapshot may be S0, never S1;<br>- S1 = a manual `leaderboard -d` within ~10 min of each terminal header;<br>- log k; k = 0 -> BLIND '?'; each S1 becomes the next S0;<br>- code with READ TABLE v3 (1) against exp70g 0.956;<br>- for 48: the CI-RAN GATE with dL = L_hi(48) - L_hi(47) (exp70g 7.67 h if 47 is not COMPLETE), then CI-? SCOPE (W225 (1));<br>- 'v' for L_hi > 8.0 h (cap rungs) or > 10.2 h (CI) | - | `round22/report.json` R22-A7; `CONTEXT.md` l.3320-3331; `round22/scan_hyp_morning_brief.notes.md` (expected times) |
| **W199 + W222** (= R20-A12 -> R21-A10 -> **R22-A8**) | **at the first header with 47 AND 49 terminal (~08:15-08:50Z); latest 09:30Z; never wait for 48** | **ONE Russian morning message**, using the r22mb-1 template + the r22mb-2 fill rules with **7 edits**:<br>(1) Q1 wording: no CI after 02:00Z; results 29 Sep ~07:40-09:30Z; the neutral clause; answer by ~23:00Z 28 Sep; default NO;<br>(2) the W2b else-branch follows CI-? SCOPE;<br>(3) case (f) = 49 not terminal at 10:00Z -> W2a = exp81;<br>(4) case (e) wording;<br>(5) Q2 threshold = our best + 0.001, quoted only after W214 (B);<br>(6) the quota placeholder if W212 has not landed;<br>(7) block 3 cites the card.<br>After sending, log "MORNING BRIEF SENT hh:mmZ; defaults Q1=нет, Q2=да" | awaiting user (asleep); **Q1 (cap lift) needs a NEW user answer** | `round22/report.json` R22-A8; `research/wf_ideas_v4/round22/scan_hyp_morning_brief.json` |
| **T131** (new) | **~07:30-09:30Z** | **Round 24**: the W1 reads by the count rule (S0 = count 48), the CI-RAN GATE for 48, the W2a choice, the brief send | - | `round22/report.json` next_focus |
| W212 | before any dummy push | Quota reading (see OVERDUE) | overdue | R22-A5 |
| T117 (updated) | **08:45-10:00Z** | **W2a**: exp80a iff exp78b '+', disp(exp78b) >= disp(exp78a), 46 not '-' (it is 0) and the exp80a dummy PASSED (logged l.3318-3319). Otherwise exp81. **New branch (W225 (2)):** if a DIV ref is not terminal at 10:00Z -> exp81 | - | `CONTEXT.md` l.3349-3350; R22-A3 (2) |
| T122 | **11:45Z** | The exp83a/exp83b dummy must have PASSED the W224 gate to be a W2b candidate | - | `CONTEXT.md` l.3351-3352 |
| T106 | **12:00Z** | **W2b** by TABLE v4 (l.3351-3356), with **CI-? SCOPE** (W225 (1)) applied. An E10 copy goes first; exp79a is never resubmitted | - | `CONTEXT.md` l.3351; R22-A3 (1) |
| T46 | 12:00Z | ~~F1 consolidation~~ **SUPERSEDED**: no finals decision on 28 Sep. Proposals go out 29 Sep 12:00/18:00Z. The supersession line is pending in W225 (3) | superseded | `CONTEXT.md` l.2709-2710, l.1671, l.3211; R22-A3 (3) |
| T123 | **~16:15-17:45Z** | The exp80a read, if W2a took it. S3 decides exp84a, with the lab prior "0 TP / +4 FP, weak, not a veto" (W225 (6)). If exp80a becomes BASE: exp83f/82c/83g dummies within ~15 min | - | `CONTEXT.md` l.3362-3364; R22-A3 (6) |
| T124 (updated) | **~17:00-19:00Z** | An evening round (round 25 or later): the exp80a/exp81 reads, the W3 decision, the W4 file list with PASSED dummies by 00:00Z | - | `round21/report.json` next_focus; R22-A6 |
| T19 / W77 | 17:57Z (012fa6dd) | API SELECTED + a page read of the ticks | - | `_curation/18/watch.json` |
| **T132** (new) | **~21:00Z** | The last sensible dummy push for any W4 stack. SEC+CI dummies need ~0.5 h plus possible queueing | - | `round22/report.json` R22-A6 deadline |
| T118 | **~23:00Z** | Latest useful answer to Q1 (the cap lift) for W4 | - | R22-A8 (1) |
| T114 / T125 | **W3 dummies PASS by ~23:15Z; submit <= 23:30Z** | Only if W2b moved to W3 (TABLE v4 (2)(v)): the max stack of '+' levers on BASE not yet scored | - | `CONTEXT.md` l.3354-3356 |
| W19 / W73 | until 29 Sep 20:00Z | ONE poller. The header must be < 15 min old | in progress (01:26:07Z) | `poll.log` l.18930 |
| W102 / W93 / W165b | standing | Never resubmit class C or an ERRORed stack; exp79a is never resubmitted. Datasets `biohub-secft-n2a-v1`, `secft-all-v1`, `ft-weights` and `coord-inject` are not touched until every user is COMPLETE. Q3 (SEC as a final) stays open | standing / awaiting user | `CONTEXT.md` l.3331-3335, l.3351 |

## LATER (29 Sep 00:00Z -> 23:59Z, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T126 | **29 Sep 00:00Z** | Every W4 file must have a PASSED dummy | `CONTEXT.md` l.3367 |
| T20 / T107 | **29 Sep 00:05-01:45Z** | **W4** in this order: E10, FULL, one file per '?' lever (CI only within CI-? SCOPE), exp84a under S3, the non-CI twin.<br>- K2-like files at 00:05/00:45/01:25Z; CI files at 00:06/00:46Z;<br>- **<= 4 planned + 1 held for E10**;<br>- no DIV-only file after 01:45Z (S6) | `CONTEXT.md` l.3366-3373, l.3364-3365 |
| T127 | **29 Sep 02:00-~10:00Z** | An E10 copy is allowed under E10 v3 until ~10:00Z. Other files need the Q1 yes. **No CI file after 02:00Z**. Non-CI T_last ~10:25Z | `CONTEXT.md` l.3374-3377; R22-A3 (4) |
| T119 | ~07:40-09:30Z | W4 reads land | `round22/report.json` R22-A8 (1) |
| T09 / W77 | 11:57Z (328f7392) / 17:57Z (18ff4796) | Tick checks + user reminder | `round19/report.json` R19-A5 |
| T120 | **12:00Z** (refresh **18:00Z**) | **Finals proposal message** {V_pub, #37}, using the W214 card with the balanced CI caveat. The user ticks; the session never re-ticks | R22-A4; `CONTEXT.md` l.3211-3213 |
| T60 | 12:00Z | G2 must have landed for a SEC file to be finals-eligible | `CONTEXT.md` l.2736 |
| T121 | 17-18Z | Log N954, for sizing the ranges only | R20-A9 (f) |
| T115 / T48 | **~19:00Z** | FINALS READ and the L9 last read. Q3 deadline. Never a non-COMPLETE file | `CONTEXT.md` l.3194, l.2510-2518 |
| T10 | **20:00Z** | Our buffer for the ticks; re-ticks stay allowed until 23:59Z | R20-A3 (a) |
| W177 H2 | 23:00Z | LESSONS H2 | `_curation/20/watch.json` |
| W178 / W215 | before 23:00Z; hourly 30 Sep | Private-read addenda (priors C/C8/C_thr) | R20-A13; `CONTEXT.md` l.3056, l.3195 |
| T49 | 23:00-23:45Z (bb224de9 23:27) | Final public LB snapshot | `_curation/18/watch.json` |
| T11 | **29 Sep 23:59Z** | Deadline. A submit must **finish** before it | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 |
| T30 / T50 | 30 Sep from 00:15Z | Private read v2 + L1-L7 | `CONTEXT.md` l.2570-2598 |
| T133 (new) | 3 Oct | The GPU quota reset comes after the deadline, so no quota relief before 29 Sep | `round22/report.json` R22-A5 |
| W29 / curator (updated) | after 29 Sep / by 30 Sep | Post-deadline list:<br>- N1 k 1.5;<br>- DaughterNet v2 at high cap (I222);<br>- synthetic pretraining;<br>- untested CI if its read was a NO-OP;<br>- N2 if SEC reads '-'/'0';<br>- **new: one division-ADD item = a theft-aware ranker (unmatched, motion-relinked claimants) + the R8-RC-C far-daughter slot + I-082 (I253)**;<br>- **MITO3 only after a pm_\* adapter and a held-out lab (I254)** | R20-A6; R22-A9 (f)/(g) |

**Passed or finished time-bound items:**
- The R8 new-mechanism cutoff (27 Sep 12:00Z) has passed. Round 22 found no admissible new mechanism (`round22/report.json` R22-A9 (d), rejected).
- The 28 Sep 00:00Z slot reset passed. W1 used 3 slots (`CONTEXT.md` l.3338-3343).
- The R8 COVERAGE line was logged before the CI submit.
- Friend replies: there has been no open friend item since 26 Sep (`CONTEXT.md` l.2175-2176).

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I249** (new) | "CI equality gate test: _dl exp70g vs exp79a: non-coord columns (id,dataset,row_type,node_id,t,source_id,target_id) identical = True; integer coord change among nodes 0.6459. tools/dummy_gates.py has no CI mode" | `round22/scan_plancheck.notes.md` | This is the only mechanical PASS test for the exp83a/b dummies. It exists only in a scan note until W224 lands. |
| **I250** (new) | "Earliest W1 terminal: safetail latency floor 6.69 h -> 47 could be terminal ~06:58-07:06Z -> pre-score deadline 06:45Z" | `round22/report.notes.md` | This sets the hard stop (T129). Earlier rounds used ~07:30Z, which is later than the real risk point. |
| **I251** (new) | "19 GPU runs since the 07:55/30 h reading ... ~20.6-22 h used at 1x billing or ~25-26.5 h if T4x2 bills at 2x"; "At 2x billing only ~3.5-5 h are left" | `round22/report.json` new_facts, R22-A5 | Under 2x, the W4 dummies + an E10 dummy may not fit. The quota was unread for the 3rd round, and dummies were pushed anyway. |
| **I252** (new) | "Division TP/FP: control 16/25 ... cap6 25/35, cap12fc2 28/42, cap24fc2 30/47, cap48fc2 30/51, uncapped 30/59 -> the in-gate thr>=0.4 orphan supply is exhausted at cap 24 fc2" | `round22/scan_recheck.notes.md` (01:45Z (B)) | This is a lab prior against the S3 step exp84a (cap 48). It reaches the plan only as W225 (6) "weak, not a veto". It is in-sample; never quote it as private support (I218/I219). |
| **I253** (new) | "claimed daughter 32 ... Claimed (control, 35): claimant w unmatched to GT in 34/35 ...; 32/35 claiming edges are motion_relinked ...; DaughterNet score >= 0.4 on only 3/35" | `round22/scan_recheck.notes.md` | The main missed division pool (32/99 GT divisions) is invisible to more cap. It is the post-deadline "theft-aware ranker" item (R22-A9 (f)) and is easy to lose after 29 Sep. |
| **I254** (new) | "Corwin's MITO3 booster ... has linker-probmat features at the top (q_m_d2 12.6% gain; q/margin 16.5%). The ship path passes no --probmat, so as deployed these features are NaN" | `round22/report.json` new_facts; `round22/scan_recheck.notes.md` (C) | It overturns the RC-C claim "MITO3 pluggable, post-deadline #1". IDEAS I-082 needs the R22-A9 (g) rewrite. |
| **I255** (new) | John Taylor: "ILP_DIVISION_WEIGHT 1.2 → 0.4" (0.957->0.958) and "READMIT_MIN_SCORE 0.965 → 0.94" (0.958->0.959); for the readmit step "0 of 2,212 edges changed" in his annotated-edge Jaccard | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743929; `round22/scan_browser.json` | A +0.001 public step with 0 annotated edges changed locally is rounding/noise on one embryo. This supports not chasing knob ladders. It contradicts our r11 closure only on its face (fork precision 0.149 < 0.161). Log only (R22-A9 (h)). |
| **I256** (new) | "Newly scored rows are submissions from 14:56-19:39Z 27 Sep (latency ~7h)"; "The ~23:30-02:00Z submit burst scores ~07-09Z" | `round22/scan_browser.notes.md`; `round22/report.json` new_facts | The burst lands exactly in the W1 read window, so k and the count can jump between S0 and S1. Take S0 as late as possible before each terminal header (W227). |
| **I257** (new) | "Rebuild exp82a... 84a ... If a prefix differs, diff it against its parent and log the cause; do not 'fix' knobs"; "9 of 11 stack builds exist only as round-21 sha claims" | `round22/report.json` R22-A6, plan_issues 7) | A late build error (path mangling, `--set` order) would cost a W4 slot. See also I238: exp70g itself does not rebuild byte-identically. |
| **I258** (new) | "W2 v4 (2)(iv) and W4 AMEND 2 (1)-2 would stack CI after a NO-OP, v or ERROR CI, which the CI-RAN GATE and R21-A3 (d) forbid" | `round22/report.json` plan_issues 2); `CONTEXT.md` l.3322-3326 vs l.3353-3354, l.3368 | This is a live contradiction in CONTEXT until W225 (1) lands. A NO-OP CI read at ~10:00Z would otherwise license a CI stack at 12:00Z. |
| **I259** (new) | "cap6_fc2 +0.000208 [-0.00019, +0.00081] ... 30 swapped-in (0 TP/1 FP/29 ign)"; "alpha 0.5 = exact lab null at cap 6; alpha 0 = volume-in-disguise" | `round22/scan_hyp_extra_levers_29sep.notes.md` | fc2 at cap 6 is the only equal-volume re-rank, and its CI includes 0. It is admissible only as an exp76e-filler replacement with a new user OK (`round22/report.json` rejected R22XL-2). Otherwise it is closed. |
| **I260** (new) | "untracked experiments/ds_secw_corwin_v1/weights (8 MB, not ignored)" | `round22/scan_plancheck.notes.md`; `git status` 01:35Z | A `git add -A` would commit 8 MB of weights. W229 names paths explicitly. |
| **I261** (new) | "Q2 threshold = our best display + 0.001 (0.957, or 0.958 if 47/49 displays 0.957). Quote it only after R22-A4 (B) is logged" | `round22/report.json` R22-A8 (5) | The E10 trigger moves with our display. If 47/49 shows 0.957, the loop text (still ">= 0.955") is two steps stale. |
| I239 | MC: "partner choice dominates (#37 vs own parent: -0.17..-0.34 bronze); F1 choice among cap-family stacks moves P by <= ~0.04" | `round21/scan_hyp_w2_w4_plan.notes.md` | The core of the finals card (W214). It is still not in CONTEXT. |
| I236 | "exp70g ~0.95634 unrounded ... a 0.957 on the exp70g base needs only ~+1.6e-4" | `round21/report.json` new_facts | A W1 '+' can come from a +1.6e-4 change. Do not quote it as a large lever effect. It is still only in the W202 info lines. |
| I237 | "Latency drift K2-family L_hi: 7.54 -> 7.58 -> 7.74 -> 7.67 -> 7.81 h (46)" | `round21/scan_plancheck.notes.md` | A cap rung can get 'v' (L_hi > 8.0 h) with no code cause. This matters for the W227 reads. |
| I238 | "exp70g does NOT reproduce with this order (762c16.. vs repo 52c182..)" | `round21/scan_hyp_w2_w4_plan.notes.md` 22:40Z | Applies to W226: diff every rebuilt stack against its parent. |
| I240 / I241 | "exp60 replay (DCLookup) is DC-blind ..."; "OUTPUT_SINGLE_CHILD_REPAIR=1: exact no-op ... every fork is a safe division or an insertion" | `round21/scan_recheck.notes.md` | Still not in FACTS/LESSONS (W202). |
| I247 | "exp79a vs exp70g: same 238,335 keys, 78,320 rows with changed z/y/x" | `round21/scan_hyp_risk_check.notes.md` | The dummy proof that CI changes the output. It is the basis for W224 (5). |
| I248 | k fell 11 -> 8 on 27 Sep; it is now 9 at 01:03Z | `round21/report.json` new_facts; `round22/report.json` new_facts | We lose ~1 place per hour without submitting. k -> 0 makes every UP test BLIND '?'. |
| I216 | The 18:56Z read used the wrong S0 (113 vs 127) and called exp70g class B, but it is class C | `round20/scan_plancheck.notes.md`; R22-A2 (2) | Still uncorrected in CONTEXT (W185). |
| I217 | The runbook SI uses DIVINS_CAP=4; the loop LOOK text says >= 0.955 | `research/wf_ideas_v4/e10v3/runbook.json`; `experiments/lb_poll/e10_watch_loop.py` l.28/l.78 | Verified at 01:36Z. W214 (B) / W174. |
| I206 | "tools/dummy_gates.py: no coordinject/secswap mode" | `round19/scan_plancheck.notes.md`; `round22/scan_plancheck.notes.md` | This is why W224 is a manual pandas check. |
| I209 | N1 staging folders `_dl/secft_x2_ds` / `_dl/secft_x3_ds` | `round19/scan_hyp_n1_prep.notes.md` | Easy to upload by mistake. N1 is banned in W3/W4 (`CONTEXT.md` l.3373). |
| I218 / I219 | Keep FRAME_CAP <= 2. All lab gain for cap >= 8 comes from 2 6bba clips | `round20/scan_hyp_insertion_direction.notes.md` | Now a rule (`CONTEXT.md` l.3373). Never quote the lab as private support. |
| I223 | "#37 wins iff y<0<x ... as F1's cap rises \|y\| grows -> #37 dominates" | `round20/scan_recheck.notes.md` | This supports I239 when V_pub moves to cap 8/12/24. |
| I227 | John Taylor: "finals = best + closest one-line neighbour"; José Freitas: synthetic data at 0.960 | `round20/scan_browser.notes.md`; https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/732103 | This contradicts {V_pub, #37}. Round 22 adds John Taylor's knob steps (I255). |
| I72 | The harness adds a co-author trailer; the user's rule says no Co-Authored-By | `memory/feedback-git-no-coauthor.md` | Applies to W229. The last 8 commits comply. |
| I116 / T67 | Agents label local times as "Z"; cron fields are LOCAL (UTC+3); timers die with the session | `round18/report.json` R18-A2 (2); `round22/scan_recheck.notes.md` ("the 01:25Z/01:30Z/01:45Z stamps above were estimates") | This recurred in round 22. Check `date -u` before quoting a stamp as a header. |
| I145 | A submit must finish before the deadline | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 | T11. No CI file after 02:00Z 29 Sep. |
| Older I-rows | Unchanged | `_curation/21/watch.json`, `_curation/20/watch.json` | - |

**Resolved since 23:50Z (curation 21):**
- I235: the exp83 ledger rule landed (`tools/runtime_ledger.py` l.80).
- I243: W1 was submitted as v1 = the dummy (`CONTEXT.md` l.3339).
- I245: the W4 stagger was written into W4 AMEND 2 (2) (l.3370-3371).
- I244: resolved in part. The 5th slot is held for E10 and an E10 copy is allowed until ~10:00Z (l.3371, l.3375-3377). The user confirmation is still pending in the morning message (W222 Q2).
- I246: the N2 proxy is logged as "at the band edge" (l.3318).
- I242: the S0 addendum is logged (l.3327-3331).
- I232: the CI-RAN GATE is logged (l.3320-3326).
- I233 / I234: the dataset no-touch and ERROR > 10 h rules are logged (l.3331-3335).
- I201: CONTEXT now says CI "hidden L 9.4-10.9 h" (l.3337).
- I231: kept for reference. The 2-lane rule held: exp83a/b were pushed as a pair (l.3345).
