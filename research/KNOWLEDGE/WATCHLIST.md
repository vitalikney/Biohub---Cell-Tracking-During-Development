# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-28 ~04:45 UTC (curation 23). This updates the curation-22 build of 28 Sep 01:42Z (its full text is in git history of this file; its predecessors are `research/KNOWLEDGE/_curation/21/watch.json`, `_curation/20/watch.json`, `_curation/19/watch.json`, `_curation/18/watch.json`). Rows not repeated here are unchanged there.

**Sources read for this update:**
- `CONTEXT.md` (3,453 lines; `## 9. Literature` starts at l.3433). New entries since curation 22:
  - 01:48Z CI-STACK DUMMY GATE (l.3378-3386);
  - 01:48Z PRE-SCORE CLARIFICATIONS (l.3387-3397);
  - 01:48Z RESUME POINT (l.3398-3408);
  - 01:48Z CORRECTION to the 18:56Z read (l.3409-3410);
  - 01:50Z CI-STACK DUMMY GATE READ, exp83a/b PASS (l.3411-3413);
  - 02:46Z E10 SIGNAL CHECKED, not a trigger (l.3414-3416);
  - 04:31Z 29 SEP FINALS CARD + E10 v3 NOW + S7 + SEC-STACK GATE (l.3417-3430);
  - 04:32Z USER: limits reset, research rounds resume, round 24 at 07:00Z (l.3431-3432).
- `git log`: 9ac10c6, dc6198b, e46b7ea, d251648, 95276ad, db8ba02, 46c18a2 (last, 04:32Z). Git dates are local time (UTC+3). None of the last 10 commit bodies has a Co-Authored-By trailer (`git log -10 --format=%b | grep -i co-author` = empty).
- `git status` 04:33Z: untracked are the nine stack folders `experiments/exp82a..c`, `exp83c..g`, `exp84a_k2_cap48_fc2/`, plus `experiments/ds_secw_corwin_v1/weights/`, `experiments/ext_corwin-biocel-aux/_booster/`, `experiments/ext_succskip/`, `research/KNOWLEDGE/_curation/23/`.
- `research/wf_ideas_v4/round23/report.json` (complete, written_utc 04:35Z, actions **R23-A1..A12**), `round23/REPORT.md` (committed db8ba02), `round23/report.notes.md`, `scan_plancheck.notes.md`, `scan_browser.notes.md`, `scan_hyp_stack_builds.notes.md`, `scan_recheck.notes.md`, `scan_hyp_finals_29sep.notes.md`.
- `experiments/lb_poll/poll.log` last header 04:26:37Z (l.20028); `experiments/lb_poll/ledger.md` (ledger time 04:26:38Z; 47/48/49 PENDING).
- `experiments/e10_watch/watch_loop.log`: RUN 16 at 03:43:55Z, 0 signals; next run 04:43:42Z.
- `research/wf_ideas_v4/e10v3/runbook.notes.md` l.206/l.208/l.213; the auto-memory folder `C:/Users/vital/.claude/projects/c--Users-vital-Documents-kAGGLE-Biohub---Cell-Tracking-During-Development/memory/` (listed here as `memory/`).

All times are UTC. IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at 04:40Z, 28 Sep:**
- **Best display 0.956** = exp70g (probe 45, 56606948), L (7.49, 7.67] h (`experiments/lb_poll/ledger.md`).
- **Rank:** #172 (was #168), 10th of 59 in the 0.956 block, k = 9, 162 teams strictly above (`round23/report.json` new_facts, LB 04:01:06Z; `experiments/e10_watch/20260928T0400Z.txt`).
- **W1 is PENDING at 04:26:37Z** (`poll.log` l.20028; `ledger.md`): 47 exp78b 56623073 (00:06:09Z), 48 exp79a CI 56623105 (00:06:33Z), 49 exp78a 56624341 (00:50:37Z). 47 can be terminal from ~06:58Z (`round23/report.json` new_facts).
- **exp83a/exp83b dummies PASSED** the pre-registered gate (`CONTEXT.md` l.3411-3413).
- **Nine W3/W4 stacks are built** and match the r21w-1 shas, but are **not logged in CONTEXT and not committed** (`round23/scan_hyp_stack_builds.notes.md`; `git status`).
- **Finals are unchanged:** #37 56563521 + #38 56563534 are ticked. The user picks on 29 Sep; the session proposes and never re-ticks (`CONTEXT.md` l.3398-3400, l.3417-3419).
- **Agent limits:** round-23 curators failed on the weekly limit (`CONTEXT.md` l.3428-3430); the user reset limits at 04:32Z, and research rounds resume with round 24 at 07:00Z (`CONTEXT.md` l.3431-3432).

**Changes since 01:42Z (curation 22):**
- **Done:**
  - W224 (R22-A1): gate line at 01:48Z (l.3378), before the outputs were read at 01:49/01:50Z (`round23/scan_plancheck.notes.md` 04:19Z); both PASS (l.3411-3413).
  - W185 (R22-A2): RESUME POINT (l.3398), CORRECTION (l.3409); `memory/project-lb-probe-approval.md` and `memory/MEMORY.md` rewritten (mtime 28 Sep 04:49 local = 01:49Z; the index now says "E10 v3 ... latest 28 Sep 01:48 UTC").
  - W225 (R22-A3): PRE-SCORE CLARIFICATIONS (1)-(6) logged 01:48Z (l.3387-3397), header 01:46:10Z.
  - W214 (R22-A4 -> R23-A1/A2/A3): FINALS CARD + E10 v3 NOW + S7 + SEC-STACK GATE logged 04:31Z, header 04:26:37Z with 47/48/49 PENDING (l.3417-3430). Residues are W230 and W231.
  - W226 (R22-A6) build part: nine stacks rebuilt byte-identical to an independent scratch build (`round23/scan_hyp_stack_builds.notes.md`). The log line and commit go to W229.
  - Round 23 REPORT.md saved and committed (db8ba02), fixing R23 plan issue 12 (`round23/report.json` plan_issues 12).
  - T130: round 23 ran 04:00-04:36Z (`round23/report.notes.md`).
- **Resolved:** T122 (exp83a/b PASSED by 11:45Z: l.3411); I258 (CI-? SCOPE landed l.3388-3391); I216 (correction l.3409); I249 (gate used, l.3378); I261 (the Q2 threshold is now quotable: card landed); I239/I223 (card in CONTEXT, l.3418-3422).
- **Re-mapped:** W212 -> R23-A5; W226/W229 -> R23-A7; W202 -> R23-A8; W199+W222 -> R23-A9; W228 -> R23-A11; W227 -> R23-A12.
- **New:** actions **W230-W234**, reminders **T135-T138**, insights **I262-I273**.

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W228** (= R22-A10 -> **R23-A11**) | **Workflow task template key facts.** Replace them with: BEST exp70g 0.956 (#172 at 04:01Z); W1 refs 56623073/56623105/56624341; finals #37+#38 ticked, the user picks on 29 Sep, proposal {V_pub, #37} per the 04:31Z card; E10 v3 trigger above our best display over all refs (now >= 0.957), SI = BASE's DIVINS settings; R8 COVERAGE; **no 28 Sep 12:00Z consolidation**; W2 TABLE v4 + S1-S7, W4 AMEND 2; point agents to the RESUME POINT 28 Sep 01:48Z and every dated entry after it | **overdue, 2nd deferral**: this curation-23 task text still lists "consolidation 28 Sep 12:00" and "R8 new-mechanism cutoff 27 Sep 12:00" as live reminders | **before round 24 launches (07:00Z)** | `round23/report.json` R23-A11, plan_issues 10; `round23/scan_plancheck.notes.md` ("R22-A10 template ... still says 'consolidation 28 Sep 12:00'"); `CONTEXT.md` l.3431-3432 (round 24 at 07:00Z) |
| **W232** (new; = **R23-A4**) | **E10 runbook SI recipe.** Edit `research/wf_ideas_v4/e10v3/runbook.notes.md` section 9:<br>(a) K from the BASE folder's probe.json change keys in order (no DEGRADE_KEEP_DIV/PATCHES), ONE build call with --patch divinsert/safetail/lowrefine, REF = experiments/&lt;BASE&gt;;<br>(b) the K1 fallback = a LOCAL never-pushed exp73ref_k1_&lt;base&gt; with LOWREFINE_ENABLE=0 (exp58t is cap 4 only);<br>(c) forks expectation = the BASE dummy delta vs x138 (62): exp70g +19, exp78a +24, exp78b +33; flag outside 0.5x-2x.<br>Rehearse once read-only with `tools/e10_port_gate.py --mode si ... --si-ref experiments/exp70g_k2_cap6` (PASS expected) | **not started**: l.206 still `DIVINS_CAP=4`, l.208 `REF=experiments/exp58_x138_safe_lowref`, l.213 exp58t | before 06:45Z if time allows; **at the latest before any E10 trigger is acted on** (E10 open until ~10:00Z 29 Sep) | `round23/report.json` R23-A4; `round23/scan_plancheck.notes.md` 04:15Z (SI gate FAIL with the runbook REF); `grep -n "CAP\|REF=" research/wf_ideas_v4/e10v3/runbook.notes.md` 04:33Z |
| **W212** (= R20-A7 -> R22-A5 -> **R23-A5**) | **Read the GPU quota once** (https://www.kaggle.com/settings) and log "GPU quota &lt;used&gt;/30 h at &lt;time&gt;". Hours left: >= 5 h -> tables only; 3-5 h -> no speculative stack dummies, keep >= 1 h for E10; &lt; 3 h -> a dummy only for the chosen FULL/BASE member, keep 1 h for E10. With no reading, apply 3-5 h. The reading never triggers a submit | **overdue, 4th deferral** (`grep "GPU quota"` in CONTEXT: last l.2542, 07:55/30 h on 26 Sep) | **before the first dummy push of 28 Sep (~08:45Z)** | `round23/report.json` R23-A5, plan_issues 6 (~20 GPU runs since; 2.5-5 h may be left) |
| **W229** (= R22-A11 -> **R23-A7**) | **Log the builds + ONE commit.** CONTEXT line "R22-A6 BUILDS: 9 stacks rebuilt, sha prefixes match r21w-1 (82a ffc00631, 82b 7cd1e3ed, 82c ee431244, 83c e8f5a8a6, 83d 22ccc1dd, 83e a016cf0f, 83f c8a2fccb, 83g 00f8cb36, 84a 4cb1e47b); independent scratch build byte-identical; finals exp58 1f1ddb6d / exp58n 55038fd6 rebuild identical; T4, internet off; ledger 82a-c/84a safetail, 83c-g safetail_ci; no push, no dummy yet". Then one commit **as the user, no Co-Authored-By trailer** (I72), named paths only: CONTEXT.md, the nine folders, runbook.notes.md if W232 edited it, new e10 snapshots and loop files, lb_poll files. **Never `git add -A`**; `ds_secw_corwin_v1/weights/` and `ext_corwin-biocel-aux/_booster/` stay untracked | **not started**: `grep "R22-A6 BUILDS"` = 0; the nine folders are untracked | after W230/W231 land, **before ~07:00Z** | `round23/report.json` R23-A7; `git status` 04:33Z |
| W126 | **No RESULTS.md rows for probes 39-46** (and 47-49 after their reads). **Neither 0.956 file (45, 46) has a row** | overdue (6th round) | before the finals read (29 Sep ~19:00Z) | `git log -1 -- experiments/RESULTS.md` = b2be382 (26 Sep 10:35 local) |
| W202 (= R19-A10 ... R22-A9 -> **R23-A8**) | **Info line + curator rows**, no rule, only after A1-A3 (these have landed):<br>- "R22-A9 INFO LINE: (a)-(h)" verbatim from `round22/report.json`;<br>- "IDEAS curation already landed in 9ac10c6"; "R22-A11 amended: e10_watch snapshots stay tracked";<br>- curator rows: READMIT_MIN_SCORE (in-sample band blind; coupled with lowrefine; closed for 28-29 Sep), ILP_DIVISION_WEIGHT (CLOSED; no direct fork channel), the softened lab caveat (I265) | not started (`grep "R22-A9 INFO"` = 0) | 28 Sep, no time pressure; R20-A13 before 29 Sep 23:59Z | `round23/report.json` R23-A8, plan_issues 8 |
| W174 residue / I217 | The E10 loop text still says ">= 0.955": `experiments/lb_poll/e10_watch_loop.py` l.28/l.78; RUN 15 printed "E10 v3 trigger = own public score >= 0.955". The rule is now "strictly above our best display, now >= 0.957" (`CONTEXT.md` l.3423-3425). **Do not restart the loop for a text change** | overdue, low | at the loop's next planned edit | `experiments/e10_watch/watch_loop.log` (RUN 15 signal line); `round23/report.notes.md` |
| W176 / W177 / W182 | Low priority:<br>- no ROUND 14-23 RECORD;<br>- LESSONS H1 not done (H2 29 Sep 23:00Z);<br>- no `NEVER_SUBMIT.md` in exp70j/exp70k (they hold only ipynb, kernel-metadata, probe.json) | overdue, low | H1 now; H2 29 Sep 23:00Z | `ls experiments/exp70j_k2_dc020 experiments/exp70k_k2_dc0225` 04:34Z; `research/wf_ideas_v4/round9/LESSONS_draft.md` |
| I208 / W202 (a) | The amanatar V6 misattribution is still uncorrected | overdue, low | with W202 | `CONTEXT.md` l.2976-2977 |
| W57 / W66 / W31 / W72 / W150 | Old low-priority text fixes; unchanged | overdue, low | passed | `_curation/20/watch.json`, `_curation/18/watch.json` |

## NEXT 24 H (28 Sep 04:40Z -> 29 Sep 00:00Z)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| T100 | **04:43Z**, then hourly at hh:43Z until 29 Sep ~10:00Z | E10 v3 watch. 16 runs, 0 real signals (RUN 15's anvithpothula item was a dataset sample, `CONTEXT.md` l.3414-3416). **The 23:30-02:00Z burst scores ~07-09Z; Burhan Ul Tayyab 0.969 is pending (submitted 03:22Z).** The trigger is a public notebook strictly above our best display (>= 0.957 now). Never S1 | live | `experiments/e10_watch/watch_loop.log`; `round23/report.json` new_facts, next_focus (5) |
| **W230** (new; R23-A1 residue) | **before 48's terminal header (~09:40Z)**; the Russian text by 29 Sep 12:00Z | The 04:31Z card has only a short CI note ("post-CSV coordinate shift, in-sample 4-clip lab, no like-for-like LB record", l.3420-3421). Missing:<br>(1) the **R22-A4 (A) balanced CI caveat** verbatim: "a0.5 pooled +0.0022 ... sign flips with alpha (a0.3 -0.0013, a1.0 -0.005) ... Eric lab +0.0078 -> LB -0.002 twice, V1284 head probe 31 LB +0.002 (confounded by -2.9% nodes); private risk = in-sample refiner on new embryos". It replaces the Eric-only line in v2 (9) (`CONTEXT.md` l.3187), which still stands;<br>(2) the (iv) Russian draft (sha 646f5d466a38...) with the R23-A10 fixes, pasted or cited;<br>(3) after 48 COMPLETE + CI-RAN "executed": "public read: probe 48 &lt;display/code&gt; vs exp70g (one embryo, public-only)" | not started | `round22/report.json` R22-A4 (A); `round23/report.json` R23-A1 (3)-(5), "the CI caveat must still land before 48's terminal header" |
| **W231** (new; R23-A3 residue) | **before any exp82*/exp83c-g/exp84a dummy is gated (earliest ~08:45Z)** | The logged SEC-STACK GATE (l.3426-3428) omits parts of R23-A3:<br>(a)(5) the CSV must differ from both the non-SEC sibling and exp81;<br>(b) SEC+CI files must also show Secondary 7029fe69 (not exp83f);<br>(c) **download the exp81 and exp80a dummy outputs into `_dl/` first and match CSV sha12 8132ef2811d0 / a109ad024ace; on a mismatch do not gate**; exp83d/e/g only after their exp82 sibling PASSES;<br>(d) **exp84a gate**: R21-A3 (e) cap-rung rules + node rows identical to exp70g.<br>Add R22-A1's caveat if any output was listed first | not started | `round23/report.json` R23-A3; `round23/report.json` new_facts ("The exp81/exp80a dummy CSVs are NOT in _dl") |
| **W228** | **before 07:00Z** | Template key facts (see OVERDUE) | overdue | R23-A11 |
| **W232** | before 06:45Z if possible | E10 runbook SI recipe (see OVERDUE) | not started | R23-A4 |
| **T129** | **06:45Z** | **Hard stop for pre-score rule lines.** A1-A3 landed at 04:31Z. What is left and still pre-score: W232 (best before 06:45Z), W230 (1) (before 48's terminal header). Anything logged after a W1 score is flagged POST-&lt;ref&gt;-READ | - | `round22/report.notes.md` ("Earliest W1 terminal ... 06:58Z"); `round23/report.json` R23-A1 |
| **W229** | **before ~07:00Z** | Builds line + one commit (see OVERDUE) | not started | R23-A7 |
| **T135** (new) | **07:00Z**, then every ~2.5 h | **Round 24**: grep-verify A1-A4 landed before the first W1 terminal header (quote the headers); the 47/49 reads by the count rule; BASE by v3 (5)/S1-S3/S7; the W2a pick; which SEC member to push; the quota; the brief. **Round 25 ~10:30-12:00Z**: CI-RAN for 48, W2b (E10 first), the SEC gate, the template check | - | `CONTEXT.md` l.3431-3432; `round23/report.json` next_focus |
| **W227** (= R22-A7 -> **R23-A12**) + T104 | **~06:58Z to ~11:00Z**. Expected: **47 ~07:00-08:00Z; 49 ~07:40-08:45Z; 48 (CI) ~09:40-10:40Z** | **W1 read procedure**, unchanged from R22-A7:<br>- **S0 = `experiments/e10_watch/20260928T0400Z.txt` (count 48, #172, k = 9)** or a fresher count-48 download; hourly snapshots may be S0, never S1;<br>- S1 = a manual `kaggle competitions leaderboard -d` into a new folder within ~10 min of each terminal header; each S1 becomes the next S0 (count 49, 50);<br>- log k; k = 0 -> BLIND '?';<br>- 48: CI-RAN gate vs exp78b (exp70g 7.67 h if 47 is not COMPLETE), then CI-? SCOPE (l.3388-3391);<br>- apply S7 at the W2a decision | - | `round23/report.json` R23-A12; `CONTEXT.md` l.3320-3331, l.3406-3408 (timers) |
| **W233** (new; = **R23-A6**) | **BASE decision 08:45-10:00Z**; SEC+CI after the 48 read; all W4 dummies PASSED by 00:00Z 29 Sep | **Dummy push order by BASE. Push NOTHING before the reads.**<br>(a) After 47+49 (or at 10:00Z per PRE-SCORE (2)): push only that BASE's SEC member: exp78a -> exp82a; exp78b -> exp82b; exp70g -> none (exp81 passed).<br>(b) After the 48 read: the SEC+CI member (exp83e/83d/83c) only if CI is not '-'/'0' and not a NO-OP/'v'/ERROR '?'.<br>(c) Under S3: exp82c, then exp83f/g after the exp80a read; exp84a only after the second strict step.<br>(d) A dummy QUEUED > 45 min is not re-pushed.<br>(e) With &lt; 3 h quota left, skip (b), keep >= 1 h for E10 | not started (by design); **not yet in CONTEXT** (`grep "R23-A6\|push order"` = 0) | `round23/report.json` R23-A6; rejected r23sb-4 |
| **W199 + W222** (= R22-A8 -> **R23-A9**) | **first header with 47 AND 49 terminal (~07:00-08:50Z); latest 09:30Z; never wait for 48** | **ONE Russian morning message** (r22mb-1 template + r22mb-2 fill rules + the 7 R22-A8 edits) with the R23 edits:<br>(1) Q2 threshold = our best display over ALL refs + 0.001 (0.957 now; 0.958 if any of 47/48/49 displays 0.957);<br>(2) block 3 cites the 04:31Z card entry, not the finals draft;<br>(3) {Q} = the quota reading or "квота GPU не читалась (~21-26.5/30 ч по оценке)";<br>(4) no R23F-6 absence-insurance line, no READMIT 0.94 offer;<br>(5) under S7: "стоп на cap 8 (S7): W2a = exp81".<br>After sending, log "MORNING BRIEF SENT hh:mmZ; defaults Q1=НЕТ, Q2=ДА" | awaiting reads; **Q1 (cap lift) needs a NEW user answer** | `round23/report.json` R23-A9; `round22/report.json` R22-A8 |
| W212 | before the first dummy push (~08:45Z) | Quota reading (see OVERDUE) | overdue | R23-A5 |
| T117 | **08:45-10:00Z** | **W2a**: exp80a iff exp78b '+', disp(exp78b) >= disp(exp78a), 46 not '-' and the exp80a dummy PASSED; otherwise exp81. **S7**: both '+' with disp(exp78a) > disp(exp78b) -> W2a = exp81, no exp80a/exp84a, BASE = exp78a. A DIV ref not terminal at 10:00Z -> exp81 | - | `CONTEXT.md` l.3349-3350, l.3390-3392 (PRE-SCORE (2)), l.3425-3426 (S7) |
| T106 | **12:00Z** | **W2b** by TABLE v4 (l.3351-3356) with CI-? SCOPE (l.3388-3391). An E10 copy goes first; exp79a is never resubmitted | - | `CONTEXT.md` l.3351 |
| T46 | 12:00Z | ~~F1 consolidation~~ **SUPERSEDED** and now logged: no finals decision on 28 Sep; proposals 29 Sep 12:00/18:00Z | superseded | `CONTEXT.md` l.3392-3394 (PRE-SCORE (3)) |
| T123 | **~16:15-17:45Z** | The exp80a read, if W2a took it. S3 decides exp84a, with the lab prior "cap48fc2 vs cap24fc2 = 0 TP / +4 FP; weak, not a veto" (l.3396-3397). If exp80a becomes BASE: exp82c then exp83f/g dummies (W233 (c)) | - | `CONTEXT.md` l.3362-3364, l.3396-3397 |
| T124 | **~17:00-19:00Z** | An evening round: the exp80a/exp81 reads, the W3 decision, the W4 file list with PASSED dummies by 00:00Z | - | `round21/report.json` next_focus; R23-A6 |
| T19 / W77 | 17:57Z (012fa6dd) | API SELECTED + a page read of the ticks | - | `_curation/18/watch.json` |
| **T132** | **~21:00Z** | The last sensible dummy push for any W4 stack (SEC+CI dummies ~0.5 h plus queueing) | - | `round22/report.json` R22-A6 deadline |
| T118 | **~23:00Z** | Latest useful answer to Q1 (the cap lift) for W4 | awaiting user | R23-A9 deadline |
| T114 / T125 | **W3 dummies PASS by ~23:15Z; submit &lt;= 23:30Z** | Only if W2b moved to W3 (TABLE v4 (2)(v)) | - | `CONTEXT.md` l.3354-3356 |
| W19 / W73 | until 29 Sep 20:00Z | ONE poller; the header must be &lt; 15 min old | in progress (04:26:37Z) | `poll.log` l.20028 |
| W102 / W93 / W165b | standing | Never resubmit class C or an ERRORed stack; exp79a is never resubmitted. Datasets `biohub-secft-n2a-v1`, `secft-all-v1`, `ft-weights`, `coord-inject` are not touched until every user is COMPLETE. Q3 (SEC as a final) stays open; SEC excluded from V_pub while Q3 is open | standing / awaiting user | `CONTEXT.md` l.3331-3335, l.3351, l.3419-3420 |

## LATER (29 Sep 00:00Z -> 23:59Z, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T126 | **29 Sep 00:00Z** | Slot reset; every W4 file must have a PASSED dummy (gates: l.3378 CI, l.3426-3428 SEC/SEC+CI + W231) | `CONTEXT.md` l.3367 |
| T20 / T107 | **29 Sep 00:05-01:45Z** | **W4**: E10, FULL, one file per '?' lever (CI only within CI-? SCOPE), exp84a under S3 (not under S7), the non-CI twin. K2-like at 00:05/00:45/01:25Z; CI at 00:06/00:46Z; **&lt;= 4 planned + 1 held for E10**; no DIV-only file after 01:45Z (S6) | `CONTEXT.md` l.3366-3373, l.3364-3365, l.3425-3426 |
| T127 | **29 Sep 02:00-~10:00Z** | An E10 copy is allowed under E10 v3 until ~10:00Z. Other files need the Q1 yes. **No CI file after 02:00Z**. Non-CI T_last ~10:25Z | `CONTEXT.md` l.3374-3377, l.3393-3394 |
| T119 | ~07:40-09:30Z | W4 reads land | `round22/report.json` R22-A8 (1) |
| **W234** (new; = **R23-A10**) | **by 29 Sep 11:57Z** (fixes belong in the card, W230 (2)) | **Fix the finals draft_ru** (`round23/scan_hyp_finals_29sep.json`) before the send: (1) DIV caveat when V_PUB has cap > 4 ("в лабе cap > 4 = 0 TP / 4 FP / 81 без разметки"); (2) replace the "own cap parent" line (never call #37 a cap parent; drop it when V_PUB = exp70g); (3) V_PUB from the whole v2 (9) pool incl. E10 copies, "строго больший дисплей или равный с подтверждённым UP"; (4) conditional SEC wording (Q3); (5) neutral exp70b line; (6) corrected #38 bullet and alternative gap (bronze -0.05..-0.15, silver -0.03..-0.09); (7) **the 11:57Z push (timer 328f7392) carries the full 5 tick steps with refs** | `round23/report.json` R23-A10, plan_issues 9 |
| T09 / W77 | 11:57Z (328f7392) / 17:57Z (18ff4796) | Tick checks + user reminder. Timers die with the session (I116): verify they still exist | `round19/report.json` R19-A5 |
| T120 | **12:00Z** (refresh **18:00Z** only on a change) | **Finals proposal message**: {V_pub, #37} vs ticked {#37, #38}, with the card ranges (bronze ~0.50-0.76 vs ~0.34-0.66) and the W230 CI caveat. The user ticks; the session never re-ticks | `CONTEXT.md` l.3417-3422; R23-A10 |
| T60 | 12:00Z | G2 must have landed for a SEC file to be finals-eligible | `CONTEXT.md` l.2736 |
| T121 | 17-18Z | Log N954, for sizing the ranges only | R20-A9 (f) |
| T115 / T48 | **~19:00Z** | FINALS READ and the L9 last read. Q3 deadline. Never a non-COMPLETE file; the insertion gate must read "did NOT fire" | `CONTEXT.md` l.3194, l.2510-2518, l.3421 |
| T10 | **20:00Z** | Our buffer for the ticks; re-ticks stay allowed until 23:59Z | R20-A3 (a) |
| W177 H2 | 23:00Z | LESSONS H2 | `_curation/20/watch.json` |
| W178 / W215 | before 23:00Z; hourly 30 Sep | Private-read addenda (priors C/C8/C_thr) | R20-A13; `CONTEXT.md` l.3056, l.3195 |
| T49 | 23:00-23:45Z (bb224de9 23:27) | Final public LB snapshot | `_curation/18/watch.json` |
| T11 | **29 Sep 23:59Z** | Deadline. A submit must **finish** before it | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 |
| T30 / T50 | 30 Sep from 00:15Z | Private read v2 + L1-L7 | `CONTEXT.md` l.2570-2598 |
| **T136** (new) | 2 Oct | The weekly agent limit reset date quoted when round 23 failed; moot while the user's 04:32Z reset holds. If agents fail again, the main session carries reads/submits/finals alone | `CONTEXT.md` l.3428-3432 |
| T133 | 3 Oct | The GPU quota reset comes after the deadline: no quota relief before 29 Sep | `round22/report.json` R22-A5 |
| W29 / curator | after 29 Sep / by 30 Sep | Post-deadline list: N1 k 1.5; DaughterNet v2 at high cap (I222); synthetic pretraining; untested CI if its read was a NO-OP; N2 if SEC reads '-'/'0'; a theft-aware division ranker + the R8-RC-C far-daughter slot + I-082 (I253); MITO3 only after a pm_* adapter (I254); **new: READMIT_MIN_SCORE 0.94 as a late-submission test with lowrefine decoupled, after the 56-clip exp60 replay (I264)** | R20-A6; R22-A9 (f)/(g); R23-A8 (1) |

**Passed or finished time-bound items:**
- R8 new-mechanism cutoff 27 Sep 12:00Z has passed; round 23 found nothing that reaches R8 (`round23/report.json` rejected, "Any new mechanism: none reaches R8").
- The 28 Sep 00:00Z slot reset passed; W1 used 3 slots; 2 are left today (W2a, W2b) (`CONTEXT.md` l.3342-3343).
- The 28 Sep 12:00Z consolidation is superseded (T46).
- Friend replies: there has been no open friend item since 26 Sep (`CONTEXT.md` l.2175-2176).

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I262** (new) | "`--si-ref experiments/exp58_x138_safe_lowref` -> [FAIL] notebook-bytes ... only in SI: BIOHUB_DIVINS_CAP "6", only in ref: "4"; with --si-ref experiments/exp70g_k2_cap6 -> [PASS] ... => a cap-6 SI built per the rule but gated per the runbook would FAIL and drop to (C)" | `round23/scan_plancheck.notes.md` 04:15Z | The only E10 path to beat our best silently breaks unless W232 lands. The runbook still has CAP=4/REF=exp58 (l.206/l.208). |
| **I263** (new) | "The exp81/exp80a dummy CSVs are NOT in _dl" | `round23/report.json` new_facts | The SEC and SEC+CI gates compare against these sibling CSVs. The CONTEXT gate line (l.3426-3428) does not say to download them and match sha12 8132ef2811d0 / a109ad024ace first (W231 (c)). |
| **I264** (new) | "READMIT_MIN_SCORE is also lowrefine's threshold (_LOWREFINE_MIN_SCORE = BIOHUB_READMIT_MIN_SCORE, tools/build_probe_kernel.py l.1650-1652; builder INFO l.2435-2443)" | `round23/report.json` new_facts | John Taylor's +0.001 step (I255) is not one knob on our K2 base. Only in round-23 JSON; the curator row is W202 (R23-A8 (1)). |
| **I265** (new) | "99.5% of GT nuclei that have a pool peak carry >= 0.965 ... readmitted nodes are 3.5-6x depleted near GT"; "if memorisation, the bias is one-sided: lab gains from DROPPING readmit/gapfill nodes are optimistic ..., lab costs of ADDING them are an upper b[ound]" | `round23/report.json` new_facts, R23-A8 (3); `round23/scan_recheck.notes.md` | The in-sample exp60 lab cannot sign sub-threshold node levers. It matters for any post-deadline node-addition work and for reading old lab verdicts. Not yet in CONTEXT (W202). |
| **I266** (new) | "r23sb-4 ('lanes idle, push now') ignores that the three dummies are mutually exclusive by BASE ... at least 2 of 3 are certain waste" | `round23/report.json` plan_issues 11, rejected | With idle lanes and a quota under 5 h, pushing exp82a/82b/83c now wastes GPU. The push-by-BASE rule (W233) is not in CONTEXT. |
| **I267** (new) | "#38's 'bronze 0' comes from the field-retention prior be >= 0, not from a copy-block tie (#38 is not a byte copy of x138)" | `round23/report.json` new_facts; `round23/scan_hyp_finals_29sep.notes.md` 04:12Z | The draft's #38 rationale is wrong. The 29 Sep message must use the corrected bullet (W234 (6)), or the user gets a false reason. |
| **I268** (new) | "{exp70g,exp70b} bronze: +0.024 / +0.012 / -0.008 at forkmid mean +5e-5 / 0 / -1e-4" | `round23/report.json` new_facts | A pair with exp70b looks slightly better in the model, but the sign rests on an unmeasured private forkmid effect. Keep the neutral wording (W234 (5)); do not reopen forkmid. |
| **I269** (new) | "Dummy forks: x138 62, K2 75, exp70g 81, exp78a 86, exp78b 95" | `round23/report.json` new_facts | The runbook's forks check ("+5..+25", `round23/report.notes.md`) would flag an exp78b-based SI (+33) as abnormal. W232 (c) fixes it. |
| **I270** (new) | "outputs downloaded 01:49/01:50Z, after the 01:48Z gate line" | `round23/report.json` new_facts; `round23/scan_plancheck.notes.md` 04:19Z | This is independent proof that the exp83a/b gate was pre-registered. Cite it if the CI stack reaches the finals card. |
| **I271** (new) | Rank drift: #168 at 01:03Z -> #172 at 04:01Z; four teams passed us (Ojaswy 0.963, Agnes 0.959, Dragibus 0.959, Thomas Greissler 0.958); Burhan Ul Tayyab 0.969 pending | `round23/scan_browser.notes.md` | This continues I248 (about 1 place per hour). It is the context for the brief, not a reason to change the plan. |
| **I272** (new) | "The line stops an E10 copy of a 0.955-0.956 notebook (below our 0.956)"; the threshold "must count 48" (CI) | `round23/report.json` R23-A1 why | The loop still prints ">= 0.955" (W174). A tired reader of a loop signal at 0.955-0.956 could copy a notebook below our own best. |
| **I273** (new) | The 04:31Z card's CI note is shorter than the R22-A4 (A) caveat, and v2 (9) still carries "nearest transfer record: Eric sub-voxel lab +0.0078 -> LB -0.002" | `CONTEXT.md` l.3187, l.3420-3421; `round22/report.json` R22-A4 | The one-sided Eric record stays the only transfer record in CONTEXT, with no V1284 probe 31 +0.002 counter-record. W230 (1). |
| I250 | "Earliest W1 terminal: safetail latency floor 6.69 h -> 47 could be terminal ~06:58-07:06Z" | `round22/report.notes.md` | Sets T129 (06:45Z). |
| I251 | "~20.6-22 h used at 1x billing or ~25-26.5 h if T4x2 bills at 2x" | `round22/report.json` new_facts | Quota still unread (4th deferral). |
| I252 | "the in-gate thr>=0.4 orphan supply is exhausted at cap 24 fc2" | `round22/scan_recheck.notes.md` | Now logged as the exp84a prior (l.3396-3397). In-sample; never private support. |
| I253 / I254 | Theft-aware ranker; MITO3 probmat features NaN as deployed | `round22/scan_recheck.notes.md` | Post-deadline list (W29). |
| I255 | John Taylor knob steps; "0 of 2,212 edges changed" | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743929 | Round 23 closed both knobs (R23-RC-A/B refuted or closed). Log only via W202. |
| I256 | "The ~23:30-02:00Z submit burst scores ~07-09Z" | `round22/report.json` new_facts | The burst lands in the W1 read window: take S0 late (W227). |
| I257 / I238 | Diff rebuilt stacks against parents; exp70g does not rebuild with the r21 order | `round22/report.json` R22-A6 | Resolved for the nine stacks (byte-identical, `round23/scan_hyp_stack_builds.notes.md`); still applies to any E10 SI build. |
| I259 | "cap6_fc2 +0.000208 [-0.00019, +0.00081] ... 0 TP/1 FP/29 ign" | `round22/scan_hyp_extra_levers_29sep.notes.md` | Closed unless a new user OK. |
| I260 | "untracked experiments/ds_secw_corwin_v1/weights (8 MB, not ignored)" | `git status` 04:33Z | W229: never `git add -A`. |
| I236 | "exp70g ~0.95634 unrounded ... a 0.957 on the exp70g base needs only ~+1.6e-4" | `round21/report.json` new_facts | A W1 '+' may be a +1.6e-4 change. Do not quote it as a large lever effect. |
| I237 | "Latency drift K2-family L_hi: 7.54 -> 7.58 -> 7.74 -> 7.67 -> 7.81 h (46)" | `round21/scan_plancheck.notes.md` | A cap rung can get 'v' (L_hi > 8.0 h) with no code cause (W227). |
| I240 / I241 | "exp60 replay (DCLookup) is DC-blind"; "OUTPUT_SINGLE_CHILD_REPAIR=1: exact no-op" | `round21/scan_recheck.notes.md` | Still not in FACTS/LESSONS (W202). |
| I247 | "exp79a vs exp70g: same 238,335 keys, 78,320 rows with changed z/y/x" | `round21/scan_hyp_risk_check.notes.md` | Basis of the CI gate (5). |
| I248 | k fell 11 -> 8 on 27 Sep; 9 at 01:03Z and 04:01Z | `round23/report.json` new_facts | k -> 0 makes every UP test BLIND '?'. |
| I206 | "tools/dummy_gates.py: no coordinject/secswap mode" | `round22/scan_plancheck.notes.md` | Every SEC/CI gate is a manual pandas check (W231). |
| I209 | N1 staging folders `_dl/secft_x2_ds` / `_dl/secft_x3_ds` | `round19/scan_hyp_n1_prep.notes.md` | Easy to upload by mistake; N1 banned in W3/W4 (l.3373). |
| I218 / I219 | Keep FRAME_CAP &lt;= 2; all lab gain for cap >= 8 comes from 2 6bba clips | `round20/scan_hyp_insertion_direction.notes.md` | Rule at l.3373; W234 (1) adds it to the finals message. |
| I227 | John Taylor: "finals = best + closest one-line neighbour" | `round20/scan_browser.notes.md` | Contradicts {V_pub, #37}; the card chose #37 (l.3421-3422). |
| I72 | The harness adds a co-author trailer; the user's rule says no Co-Authored-By | `memory/feedback-git-no-coauthor.md` | Applies to W229. The last 10 commits comply. |
| I116 / T67 | Agents label local times as "Z"; cron fields are LOCAL (UTC+3); timers die with the session | `round18/report.json` R18-A2 (2) | CONTEXT has "01:48 UTC UTC" stamps (l.3378, l.3387). Check `date -u` before quoting a header; verify the 11:57Z/17:57Z timers exist on 29 Sep. |
| I145 | A submit must finish before the deadline | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 | T11. No CI file after 02:00Z 29 Sep. |
| Older I-rows | Unchanged | `_curation/21/watch.json`, `_curation/20/watch.json` | - |

**Resolved since 01:42Z (curation 22):**
- I249: the CI-stack gate was used as written (l.3378, l.3411).
- I258: CI-? SCOPE landed (l.3388-3391).
- I216: the 18:56Z S0 correction landed (l.3409-3410).
- I261: the Q2 threshold is quotable (card landed at 04:31Z).
- I239 / I223: the finals card with its ranges is in CONTEXT (l.3417-3422).
- I217 (runbook part) continues as I262/W232; the loop-text part stays under W174.
