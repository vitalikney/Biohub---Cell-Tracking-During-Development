# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-27 ~15:55 UTC (curation 18). This updates the curation-17 build from 11:40 UTC (`research/KNOWLEDGE/_curation/17/watch.json`).

Sources read for this update:
- `CONTEXT.md` at main HEAD **b853642** (3,031 lines; `## 9. Literature` at l.3011). New entries since curation 17:
  - 12:01 UTC LINE (l.2952-2954);
  - R8 FULL RECORD 12:12 (l.2955-2971);
  - LAST-SLOT PRE-SCORE LINE 12:12 (l.2972-2982);
  - BIGGER LEVERS READY 12:49 (l.2983-2994);
  - PROBES 43/44 READ 13:14 (l.2995-3000);
  - exp71 DONE + exp72 BUILT 13:27 (l.3001-3006);
  - SUBMIT probe 46 = exp70q 14:37 (l.3007-3010).
- `git log` since 9cdc047: a6ffbc9, ac08c5e, c86fd5a, f28d5f5, 0408ab1, 2981590, b853642 (git dates are local UTC+3).
- `git status`:
  - untracked: `research/wf_ideas_v4/round18/`, `experiments/ds_secw_corwin_v1/weights/`, `e10_watch/20260927T1343Z/1443Z/1517Z/1543Z.txt`;
  - modified: `e10_watch/watch_loop*`, `ledger.md`, `poll.log`.
- `research/wf_ideas_v4/round18/`:
  - `REPORT.md` and `report.json` (complete, written 15:50Z; actions R18-A0..A10);
  - `report.notes.md`, `scan_*.notes.md`.
- `experiments/lb_poll/ledger.md`: last header 15:43:07Z.
- `experiments/e10_watch/watch_loop.log`: RUN 4 at 15:44:21Z.
- CronList (~15:50Z).

All times are UTC. IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, superseded, moot, blocked, awaiting user.

**State in one line (15:55Z 27 Sep):**
- **Finals** are unchanged: #37 56563521 + #38 56563534. Probes 43/44 both scored 0.954 with no UP, so the class-C letter (b) did not fire (`CONTEXT.md` l.2995-3000).
- **Probes 45 and 46 are PENDING** at 15:43:07Z (`ledger.md`):
  - 45 = exp70g 56606948, submitted 11:15:12Z;
  - 46 = exp70q 56611472, submitted 14:36:59Z.
- **27 Sep slots: 5 of 5 used** (l.3009).
- **The E10 v3 hourly loop has been LIVE since 12:43Z**: 4 runs, 0 signals (`experiments/e10_watch/watch_loop.log`).
- **Round 18 is complete (15:50Z).** None of R18-A0..A10 is done yet.
- **The 28 Sep plan the user was told is now stale:**
  - the chat said "exp72 at 00:05Z" and "exp75 = best chance";
  - round 18 moves both W1 defaults onto the exp70b base, as **exp76a / exp76d**, and keeps exp72 and exp75 as fallbacks;
  - it also calls exp75 a sign probe at ~0.35-0.45 (`round18/REPORT.md` §1 (3), (5); `report.json` plan_issues (10)).
- **The user's question "do research agents run every 2-3 h?"** is answered by `round18/report.json` R18-A0:
  - rounds start roughly every 2.5-3 h (mean 2 h 43 min, median 2.5 h, range 1.7-4.25 h);
  - they are **not on a fixed timer**: CronList has no research-round job (`round18/scan_plancheck.notes.md` 15:30Z);
  - the user's "~2.5 h until R8" mandate ended at 27 Sep 12:00Z (`CONTEXT.md` l.2082);
  - the E10 v3 loop runs hourly and the LB poller every ~10 min.

**Changes since 11:40Z (curation 17):**
- Done:
  - W168 (`round17/REPORT.md` tracked, ac08c5e);
  - W169 (l.2952 + l.2955);
  - W171 (l.2972);
  - W170 (l.2995, 0408ab1);
  - W174 (1): the loop is live and `tools/e10_snapshot.py` is committed (c86fd5a);
  - W181 (logging part, l.2983).
- Superseded:
  - W173 -> **W184** (R18-A1);
  - W175 -> **W185** (R18-A2);
  - W172 -> **W189** (R18-A6 budget);
  - W180's "exp72 at 00:05Z" -> **W190** (W1 = exp76a/exp76d; exp72 is a fallback).
- Resolved insights:
  - I172: the exp70q dummy ran, and exp70q was submitted as probe 46;
  - I173: tools committed in c86fd5a.
- New: actions **W183-W194**, reminders **T100-T108**, insights **I187-I197**.

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W185** (new; = R18-A2; replaces W175) | **No RESUME POINT since 26 Sep 22:46Z** (`grep "RESUME POINT"`: last hit l.2599). MEMORY.md l.8 still says "E10 v1 in force, v2 pending" and l.9 still says "latest 26 Sep 22:46". **No timers exist for the 45 read, the 46 read or the 00:03Z W1 batch.** The fired one-shots 5b23a3ed, 54a8f20d and cdd738f1 are still listed. `fb_ins35.py` still exists only in the session scratchpad. The E10 v3 edges are not in CONTEXT | overdue (W175 was due ~15:00Z) | now; timers before 17:50Z | `round18/report.json` R18-A2; CronList 15:50Z; `round18/v_plancheck_pc18-06.notes.md`; `memory/MEMORY.md` l.8-9 |
| **W176** (cont.) | **No ROUND 14, 15, 16, 17 or 18 RECORD** (`grep -c "ROUND 1[4-8] RECORD"` = 0). R18-A2 (5) moves them to after the 46 read | overdue (W146 was due 07:30Z) | after the 46 read (~22:40Z) | `CONTEXT.md` (grep); `round18/report.json` R18-A2 (5) |
| **W126** | **No RESULTS.md rows for probes 39-44** (all six scored); 45/46 will be added to the gap. The last row is still probe 38 (l.71), and the file was last committed 26 Sep 07:35Z (b2be382). `exp72/probe.json` and `exp75/probe.json` both carry the boilerplate "compare with exp56 ... above exp56 adopt" (I154) | overdue (D1 04:58Z) | now | `experiments/RESULTS.md` l.71; `experiments/exp72_k2_secft/probe.json`; `round18/report.json` R18-A3 (5) |
| W177 (= R17-A9) | H1 was due "today after the 43/44 read" (13:14Z). `LESSONS_draft.md` is unchanged since bf07763 (l.7 still has the old scope line) | overdue | H1 now; H2 29 Sep 23:00Z | `research/wf_ideas_v4/round9/LESSONS_draft.md` l.7; `round17/report.json` R17-A9 |
| W182 | **No NEVER_SUBMIT.md in exp70j/exp70k** (class C, "never resubmitted"). Also: the exp70n dummy was COMPLETE at 12:46Z and has no slot plan (see I196) | not started | before any 28 Sep submit | `ls experiments/exp70*/NEVER_SUBMIT*` = none (15:50Z); `CONTEXT.md` l.2992 |
| W174 (2)-(3) residue | E10 v3 submit edges and runbook v3 were never logged in CONTEXT. The loop itself is live | overdue | with W185 | `round18/scan_plancheck.notes.md` 15:20Z ("E10 v3 submit edges not logged") |
| W57 / W66 / W31 / W72 | Still missed:<br>- "frozen/duplicated frames" (2 hits);<br>- 0 hits for `out_valid` / `efpost` / `33.1%` | overdue, low priority | 26 Sep 12:00 (passed) | `grep -c` 15:50Z |
| W136 / W160 residue | R16-A2 is still logged only as "chat sent, push requested", with no sent/not-sent | moot, low priority | - | `CONTEXT.md` l.2963-2964 |
| W150 | The round prompt is unchanged (js last commit 13a27a1, 26 Sep 17:50Z). The fix is now R18-A9 (c) | overdue, low priority | before round 19 | `experiments/workflows/biohub-research-round.js`; `round18/report.json` R18-A9 (c) |

## NEXT 24 H (27 Sep 15:55 -> 28 Sep 15:55 UTC)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| **W183** (new; = R18-A0) | **now (next chat turn)** | Answer the user's cadence question with the ready Russian text. It must carry the 3 plan corrections:<br>- exp75 is a sign probe, not "the best chance";<br>- rebase onto exp70b (exp76a/exp76d);<br>- the exp75 queue stall.<br>Offer a fixed round timer (local-time cron fields), e.g. every 2.5 h until 29 Sep 18:00Z | in progress (the user's question is this relay) | `round18/report.json` R18-A0; `round18/report.notes.md` 15:38Z |
| **W193** (new; = R18-A10) | with W184 | Commit `round18/` + the W184 CONTEXT entry (+ later the W188 ledger edit) **by named paths**. Do NOT commit `experiments/ds_secw_corwin_v1/weights/`, `e10_watch/*` or `ledger.md`/`poll.log` in that commit. Commit as the user with no trailer; grep for "claude", then push | not started (`round18/` untracked) | `round18/report.json` R18-A10; `git status` |
| **W186** (new; = R18-A3) | **exp76a/exp76d build + dummy push NOW (~16:00Z)**; exp76c/exp76g ~17:00-18:00Z; exp76e/exp73m after the 45 read; every W1 dummy COMPLETE by **23:45Z** | Build with `MSYS_NO_PATHCONV=1` (I193). Expected sha: exp76a 1bc05bc9, exp76d 87d257ba; builder d46a8b2d; coordinject_patch 78cae2a9. Diff against the exp70b notebook. Log the gates PASS/FAIL with values:<br>- CI files: videos=4/4, replaced > 0, <= 130 s/video;<br>- secFT files: SHA ed8c616b;<br>- nodes -2%/+1%.<br>**Read the GPU quota before step (3)** (I185). Log exp72's gates now (step 5) | not started (`ls experiments/exp76*` = none at 15:50Z) | `round18/report.json` R18-A3; `round18/scan_hyp_slots_28sep.notes.md` 15:40Z |
| **W184** (new; = R18-A1; replaces W173) | **before 17:50Z** (45 can score from ~17:56Z) | ROUND 18 PRE-SCORE CARD in CONTEXT:<br>- codes P5/U4/N4/NEG/ERR/MASKED + suffix "v";<br>- finals clause L_hi <= 9.0 h, non-CI files only;<br>- coordinject and secFT files are public-only;<br>- `--family` until W188;<br>- the 28 Sep W1 branch table (drops DC 0.15 rungs, exp73s/c, exp76b);<br>- CI and FT outcome rules;<br>- the 46 "v" rule;<br>- the private-read list += 56606948, 56611472 and every 28 Sep ref | not started (0 hits for "R17-A5"/"PRE-SCORE CARD" after l.3010) | `round18/report.json` R18-A1, plan_issues (1) |
| **W187** (new; = R18-A4) | **20-30 min after the exp76a push; decide by 19:00Z** | exp75 has been QUEUED since 13:19Z with idle lanes (2 h 20 min at 15:39Z), while exp72 (pushed later) already ran. The only metadata difference is dataset `yuki0731/biohub-coord-inject`. Rules:<br>- if exp76a is also stuck for 30 min or more, re-push it once;<br>- if it is still stuck at 19:00Z, drop CI from W1 and tell the user;<br>- before every CI submit, run a read-only `kaggle datasets files` check (10 files, dated 2026-08-25) | not started | `round18/report.json` R18-A4; `round18/report.notes.md` 15:39Z |
| **W188** (new; = R18-A5) | **before 28 Sep 00:05Z** | `tools/runtime_ledger.py` has no rules for exp72-76, so they read as "family unknown". Add `safetail_ci` (10.75 h) plus the exp75/76/72-74 rules and a test. Until then, pass `--family` | not started | `round18/report.json` R18-A5; `round18/report.notes.md` 15:39Z |
| **W189** (new; = R18-A6; replaces W172) | **after the 46 read (~22:40Z), before 23:45Z** | Log the 28 Sep slot table:<br>- W1 = 3 files in the P5/U4 rows, 2 in N4/NEG;<br>- 1 slot held for E10 v3 until 12:00Z 28 Sep;<br>- W2 at ~09:30-10:30Z;<br>- 29 Sep W4 <= 5, all before 02:00Z.<br>Send ONE short Russian brief with honest odds (P(>= 0.955 by 29 Sep 19:00Z) ~0.35-0.45) and **2 yes/no questions: (1) lift the 29 Sep 02:00Z cap? (2) exp74 as idle-slot filler?** Both default to no | not started | `round18/report.json` R18-A6 |
| **W190** (new; = R18-A7; replaces the W180 submit step) | **28 Sep 00:03Z timer; submits 00:05 / 00:25 / 00:45Z** | For each W1 file:<br>- check `kaggle competitions submissions` (no duplicate);<br>- check the last poll header is < 15 min old and not a 429;<br>- check its dummy gates are PASS in CONTEXT;<br>- run the CI dataset check.<br>Fallback chain: exp76a -> exp72 -> exp75. The finals stay untouched | not started (no 00:03Z timer: CronList 15:50Z) | `round18/report.json` R18-A7 |
| **W191** (new; = R18-A8) | tonight at each 45/46 COMPLETE; **28 Sep 06:30Z** | Take one LB download right after each COMPLETE and count TeamIds passed. Restart the ladder watcher at 06:30Z with a new `--s0` (the newest e10_watch snapshot) and `--hard-cap 2026-09-28T12:00Z`: `run_ladder_watch.sh` hardcodes the 27 Sep S0 and cap | not started | `round18/report.json` R18-A8; `round18/report.notes.md` 15:44Z |
| **W194** (new) | **round 19 ~18:30-19:30Z; round 20 ~22:30-23:15Z** | Audit rounds planned in `next_focus`:<br>- R19: check that W184/W185 were logged before 17:50Z; the 45 read; the exp76a/d dummy gates and CI stall; the GPU quota; E10;<br>- R20: the row choice, W1 files with passed dummies by 23:45Z, W188, the W189 brief.<br>**No cron launches them** (I187), so they run only if the main session starts them | not scheduled | `round18/report.json` next_focus; CronList 15:50Z |
| W180 (updated) | - | exp72 chain:<br>- exp71 COMPLETE 13:25Z;<br>- dataset `biohub-secft-all-v1` created;<br>- exp72 built (f3d23bcd), dummy clean: 121,061 nodes (-0.158%), sha d78093ac, 80 forks.<br>**Gates not logged in CONTEXT** (W186 step 5). **Q3 still unanswered -> public-only** | done except gate log; submit step superseded by W190 | `CONTEXT.md` l.3001-3006; `round18/report.notes.md` 15:44Z |
| W165b | any time up to 29 Sep ~18:00Z | exp70b-as-final letter (still open; default = no change) | awaiting user | `round17/report.json` R17-A7 (c) |
| W19 / W73 | until 29 Sep 20:00 | ONE poller. Before any submit, the last header must be < 15 min old and not a 429 | in progress (last header 15:43:07Z) | `experiments/lb_poll/poll.log` |
| W102 / W93 | standing | Never resubmit class C (exp70j/k) or any ERRORed rung. exp65/66 and the dry-run kernel stay never-submit | standing | `round18/report.json` R18-A1 (4) |
| T100 (new) | hourly at **hh:43Z** (next 16:43:42Z) until 29 Sep 12:00Z | E10 v3 watch loop run (read-only). Any signal -> page look (I174) | loop live, 0 signals in 4 runs | `experiments/e10_watch/watch_loop.log` |
| T101 (new; replaces T94) | **17:50Z** | W184 card + W193 commit deadline | - | `round18/report.json` R18-A1 |
| T95 (updated) | window **17:56-18:59Z**; 8.0 h mark **19:15Z**; 9.0 h mark 20:15:12Z; proposed read timer **19:05Z** (cron `5 22 27 9 *`, local); hard edge 20:30Z | Probe 45 (56606948) score -> code it per W184 | - | `round18/report.notes.md` 15:38Z; `round18/report.json` R18-A2 (2) |
| T102 (new) | **19:00Z** | CI-stall decision (W187) | - | `round18/report.json` R18-A4 |
| T96 (updated) | window **21:18-22:21Z**; 8.0 h mark **22:37Z**; proposed read timer **22:45Z** (cron `45 1 28 9 *`); hard edge 00:00Z | Probe 46 (56611472) score. If L_hi > 8.0 h, add the "v" suffix | - | `round18/report.notes.md`; `round18/report.json` R18-A1 (7) |
| T103 (new) | **23:45Z** | Every W1 dummy COMPLETE and PASS; slot table + brief sent (W189) | - | `round18/report.json` R18-A3, R18-A6 |
| T18 / T42 (updated) | **28 Sep 00:00Z** reset; **00:05 / 00:25 / 00:45Z** | W1 per the branch row (W190); timer `3 3 28 9 *` (local) = 00:03Z | - | `round18/report.json` R18-A2 (2), R18-A7 |
| T104 (new) | **28 Sep 06:30Z**; W1 scores ~07:30-10:00Z | Ladder watcher restart (W191) | - | `round18/report.json` R18-A8 |
| T105 (new) | **28 Sep ~09:30-10:30Z** | W2 (<= 2 files) after the W1 reads | - | `round18/report.json` R18-A6 |
| T106 (new) | **28 Sep 12:00Z** | The held E10 v3 slot is released if unused | - | `round18/report.json` R18-A6 |
| T32 / T39 | 18:04, 21:04, 00:04 ... (timer 2e87e414) | Backup E10 P1 checks; they are redundant while the hourly loop runs | timer alive (CronList 15:50Z) | CronList |
| T67 | standing | **All timers are session-only; cron fields are LOCAL (UTC+3)**. Live: 2e87e414, 012fa6dd, 328f7392, 18ff4796, bb224de9. Fired but still listed: 5b23a3ed, 54a8f20d, cdd738f1 | - | CronList 15:50Z; `round18/report.json` R18-A2 |

## LATER (28 Sep 15:55 -> 29 Sep 23:59 UTC, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T46 | **28 Sep 12:00** | F1 consolidation (R8 lifted by the user for E10 v3, exp72 and the division rungs) | `CONTEXT.md` l.1671; l.2955-2971 |
| T19 / W77 | **28 Sep 17:57** (012fa6dd) | API SELECTED + page read of the ticks, in plain numbers | CronList |
| T35 | 28 Sep 22:00 | Final admission table: 45, 46, W1/W2 files, E10 v3 copies | `research/wf_ideas_v3/FINAL_REPORT.md` l.178; `round18/report.json` R18-A1 |
| T20 / T107 (new) | **29 Sep 00:00** reset; W4 <= 5 files from 00:05Z, **all before 02:00Z** (the R8 ladder cap). A W5 at ~09:30Z (CI) / ~11:15Z (K2-like) only if the user lifts the cap (W189 Q1) | `round18/report.json` R18-A6 |
| T98 (updated) | **29 Sep 02:00Z** target for a verbatim E10 copy; it can be a final only if submitted <= 19:00Z minus (latency + 0.5 h). The loop ends 29 Sep 12:00Z | `round18/report.json` R18-A2 (1); `experiments/e10_watch/watch_loop.log` l.1 |
| T60 | **29 Sep 12:00** | G2 must have landed for exp72/exp76d to be finals-eligible (Q3 = yes only) | `CONTEXT.md` l.2736 |
| T09 / W77 | **29 Sep 11:57** (328f7392) / **17:57** (18ff4796) | Tick checks + reminder to the user | CronList |
| T86 | 29 Sep ~18:00Z | Practical expiry of the exp70b letter (W165b) | `round16/report.json` R16-A8 (i) |
| T48 (= W131) | **29 Sep ~19:00** | L9 last read. Never two byte-identical files; never a non-COMPLETE file; CI/secFT files are public-only unless the user re-ticks | `CONTEXT.md` l.2510-2518; `round18/report.json` R18-A1 (2) |
| T10 | **29 Sep 20:00** | **Our buffer**, not a Kaggle freeze: re-ticks are allowed until 23:59Z. Read F = API SELECTED after 23:59Z | `round18/report.json` R18-A2 (1) |
| W178 (= R17-A10) | before 29 Sep 23:00Z; hourly 30 Sep | Private-read addenda. "Private board appeared" = a non-empty privateScore (I180) | `round17/report.json` R17-A10 |
| T49 | 29 Sep 23:00-23:45 (bb224de9 at 23:27) | Final public LB snapshot to `experiments/private_read/` | CronList |
| T11 | 29 Sep 23:59 | Deadline. A submit must **finish** before it | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 |
| T30 / T50 | 30 Sep from 00:15Z | Private read v2 + L1-L7 + W178 | `CONTEXT.md` l.2570-2598 |
| **W192** (new; = R18-A9) + W179 / W147 / W166 | by 30 Sep | Curator edits:<br>- I-028 / exp75 wording;<br>- the exp74 card (3 fixes);<br>- the template "~4 h headroom" fix;<br>- NL-4..7 info lines;<br>- post-deadline list (N1 narrow, N2, primary head FT + V1284, LOEO DC) | `round18/report.json` R18-A9 |
| W29 | after 29 Sep | Post-deadline list | `round18/report.json` R18-A9 (e) |

**Done, superseded or moot since 11:40Z (for the record):**
- W168: `round17/REPORT.md` tracked (ac08c5e).
- W169: 12:01 line (l.2952) + R8 FULL RECORD (l.2955-2971).
- W171: last-slot pre-score line logged 12:12Z, before any 43/44 score (l.2972-2982).
- W170: 43/44 read at 13:14Z (first terminal header 13:12:33Z). Both 0.954, 0 TeamIds passed, no V*_C; pair unchanged (l.2995-3000, 0408ab1).
- W174 (1): E10 v3 loop live since 12:43:42Z; `tools/e10_snapshot.py` committed (c86fd5a).
- W181: bigger levers logged (l.2983-2994). The exp73 decision table is **superseded** by the W184 branch table. exp74's dataset is still not uploaded and needs a user OK (W189 Q2).
- T87-T91, T93: passed.
  - Last slot: exp70q submitted 14:36:59Z as probe 46.
  - exp75 missed that slot because its dummy stayed QUEUED (l.3007-3010).
- W172 -> W189. W173 -> W184. W175 -> W185. T84: moot.

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I187** (new) | "No timer for the 45 read (~19:00Z), 46 read (~22:40Z), 28 Sep 00:03Z submit batch. **No research-round cron in this session.**" | `research/wf_ideas_v4/round18/scan_plancheck.notes.md` 15:30Z | This is the direct answer to the user's question: rounds are not guaranteed every 2-3 h. Rounds 19/20 exist only as `next_focus` text. Timers fire only while the REPL is idle (I181). Unless W185 creates timers, the 45/46 reads and the 00:05Z batch depend on the main session being awake |
| **I188** (new) | exp71 training: "T4 session shows n_visible_gpus=2 (one GPU idle!)" | `round18/scan_hyp_new_levers.notes.md` 15:25Z | Any further training (N2, rejected for now) wasted half the T4x2. Keep this for the post-deadline list |
| **I189** (new) | "x138 re-aligns secondary logits per frame to primary mean/std (clamp 0.5-2) BEFORE 0.2/0.8 blend -> a global bias shift cancels; only shape changes of the secondary map matter". exp71's largest change is "detect_head.bias rel 0.50 (a global logit shift)" | `round18/scan_hyp_new_levers.notes.md` | exp71's largest weight change is mostly cancelled inside x138, so expect exp72/exp76d ~= parent (nodes only -0.16%). Together with I175 ("FT weights 0 of 5") and imissher's adapted secondary at -0.008 (discussion 743222, same notes), the fine-tune line has a weak prior. W184 (6) handles the read |
| **I190** (new) | "tools/build_probe_kernel.py l.106 + l.2318 SUCC_TOKEN='exp73': E10 v3 SI copies are named exp73[x]_si_<author>, colliding with division rungs exp73a..exp73v" | `round18/scan_plancheck.notes.md` | An E10 v3 copy would be mislabelled in ledger tokens and CONTEXT. R18-A5 only says "always pass --family"; the name collision itself is not fixed |
| **I191** (new) | "exp70q 33ab04d1 (needs the exp70q knob order: CAP/THRESH set AFTER LOWREFINE; with the standard K block the sha is 95cf730f = same content, different line order)"; "Git Bash needs MSYS_NO_PATHCONV=1 for the secswap manifest path (/kaggle/... gets rewritten to C:/Program Files/Git/kaggle/...)" | `round18/scan_hyp_slots_28sep.notes.md` 15:40Z | Two silent traps for W186. The sha check fails on the knob order (exp76c/g use the exp70q family). The path rewrite would break the secswap manifest of exp76d/g |
| **I192** (new) | Latencies are rising: "K2 7.36-7.54 h -> 43/44 7.56-7.74 h"; exp70q dummy "1,874 s vs K2 ~1,512 s"; dummy runtime "no usable correlation" with latency; insertion gate DIVINS_DEADLINE_S 28800 (8.0 h) | `round18/scan_recheck.notes.md` 15:35Z; `CONTEXT.md` l.3008 | The headroom to the 8.0 h insertion gate is ~0.26 h. A cap-6 file (45/46) could silently skip insertion on late clips, so its read must carry "v" (W184 (7)). Also check the log for "DIVINS SKIPPED (deadline)" |
| **I193** (new) | Coordinject: "total latency ~8.75 h est -> exceeds the 9.0 h L_hi ceiling" (bounds); deadline KERNEL_START+37800 s; "per-video skip when now+1.25*slowest > deadline"; "'no video was refined; submission.csv unchanged' (no-op)" at `tools/coordinject_patch.py` l.324 | `round18/scan_plancheck.notes.md`; `round18/scan_hyp_slots_28sep.notes.md` | CI files can be a partial or total silent no-op on the hidden set, and are finals-ineligible under the 9.0 h clause. R18-A1 makes them public-only; the user should hear this if exp76a displays 0.955 |
| **I194** (new) | "exp70b (fm45) ... our exact score is near the TOP of [0.9535,0.9545) ... gap to 0.9545 ~5e-5"; in-bin position history 26 Sep 16:20 12/95 ... 27 Sep 15:17 6/113 | `round18/scan_hyp_slots_28sep.notes.md` 15:35Z | This is the whole basis of the exp70b rebase. It assumes a uniform or exponential in-bin density, a model that rests on one embryo. Meanwhile ~5 teams per hour pass us (`round18/REPORT.md` §2), so the in-bin rank drifts |
| **I195** (new) | "If exp76a also stays QUEUED >= 30 min while exp76d runs, treat CI kernels as blocked"; exp72 "(13:27Z) already passed" while exp75 is QUEUED | `round18/report.notes.md` 15:39Z | The chat told the user exp75 was "the best chance, ready at 00:05Z". If CI stays blocked, W1 silently loses its headline file. Tell the user by 19:00Z (W187) |
| **I196** (new) | "exp70n dummy COMPLETE 12:46Z (not submitted)"; "the cap, not the threshold, is the binding insertion knob" | `CONTEXT.md` l.2992; `bigger_levers/prep_div_combos.notes.md` (I176) | An orphan build that held a GPU lane all morning. It has no row in the W184 branch table; say so explicitly so it is not submitted by default |
| **I197** (new) | Masking: "a W1 file that completes after another W1 UP is masked, so 'no UP' would wrongly close its lever. The ladder watcher has been off since 07:37Z" | `round18/report.json` plan_issues (8) | The 20-min stagger and the 06:30Z watcher restart (W191) are the only guard. The watcher needs new CLI args; the script's defaults are stale |
| I174 | "the kernel API has no score field, so a signal starts a page look" | `round17/scan_browser.notes.md` | The E10 v3 loop still reads run status, not the page score. A signal needs a browser look |
| I175 | Corwin secondary "EV plausibly <= 0"; exp23 secondary swap lost 0.007 on the LB | `bigger_levers/prep_corwin_secondary.notes.md`; `CONTEXT.md` l.2726 | Now reflected in W184 (6) and W189 Q2 (exp74 defaults to no) |
| I177 | amanatar V6 0.901: "more divisions via looser gates can crash" | `CONTEXT.md` l.2976-2977 | It was logged, but only in the pre-score line; bear it in mind for the aggressive exp73 rungs after 45/46 |
| I180 | Private-board switch must key on privateScore | `round17/v_hyp_post_r8_plan_r17p-f11.notes.md` | W178 |
| I181 | Timers fire only while the REPL is idle; they are session-only | `round17/v_hyp_post_r8_plan_r17p-f9.notes.md` | Now critical for the 00:03Z batch (I187) |
| I182 | Q3 unanswered -> exp72 (and now exp76d/g) public-only; G2 must land by 29 Sep 12:00 | `CONTEXT.md` l.2935-2936, l.3005-3006 | Ask Q3 before the W1 secFT file scores (~07-10Z 28 Sep), or it cannot become a final |
| I185 | GPU quota "~22 h left" (26 Sep); nobody has re-read the Settings page since | `CONTEXT.md` l.2729 | exp71 (2.1 h train) + ~6 dummies used since then. R18-A3 (3) now says to read it before the later dummies and skip them if < 6 GPU-h |
| I165 | `fb_ins35.py` + out.json only in the session scratchpad `r16rcb/` | `round18/v_plancheck_pc18-06.notes.md` | Still not copied (W185 (4)) |
| I154 | `probe.json` "rule" boilerplate "above exp56 adopt" | `experiments/exp72_k2_secft/probe.json`, `experiments/exp75_k2_coordinject/probe.json` | W126 / R18-A3 (5) |
| I72 | The harness asks for a Co-Authored-By trailer; the user's rule forbids it | `memory/feedback-git-no-coauthor.md` | For W193 |
| I116 | Agents label local (UTC+3) times as "Z"; cron fields and file mtimes are local | `round18/report.json` R18-A2 (2) | For the new timers (19:05Z = `5 22 27 9 *`) |
| I145 | "It has to finish before the deadline to count" | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 | For T98 / T107 |
| I161 / I163 / I178 / I179 / I183 / I184 / I186 and older | Unchanged | `_curation/17/watch.json` | I183: DC is now closed (13:14Z); the "more divisions" test rests on 45/46 |

**Resolved since 11:40Z:**
- I172: the exp70q dummy ran and exp70q became probe 46 (l.3007).
- I173: tools committed (c86fd5a).
- I176: exp70n was never submitted, so the concern is moot (see I196).
- I186: moot for 43/44, which were read at 13:14Z.
- Details: `_curation/17/watch.json`.
