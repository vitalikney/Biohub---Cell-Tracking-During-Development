# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-27 11:40 UTC (curation 17). This updates the curation-16 build from 09:10 UTC (`research/KNOWLEDGE/_curation/16/watch.json`).

Sources read for this update:
- `CONTEXT.md` at main HEAD **9cdc047** (2,972 lines; `## 9. Literature` at l.2952). New entries since curation 16:
  - R16-A1 READ ADDENDUM 09:15 (l.2880-2913);
  - R16-A2 message 09:15 (l.2914-2916);
  - USER E10 v3 11:08 (l.2917-2926);
  - USER class-C letter (b) 11:09:39 (l.2927-2932);
  - USER yes to Q1/Q2 11:11:40 (l.2933-2936);
  - exp71 pushed 11:12 (l.2937-2939);
  - USER FREEZE lifted 11:14 (l.2940-2945);
  - aggressive mode + probe 45 11:16 (l.2946-2951).
- `git log` since 0bd1408:
  - 289bd52, 06f1a02 (R16-A1/A2);
  - 61e0737, 659cef3, 5bce47f, d1ccc85, 9cdc047 (11:08-11:16Z user items).
- `git status`:
  - modified: `tools/build_probe_kernel.py`, `tools/e10_port_gate.py`, `tools/e10_snapshot.py`, `experiments/lb_poll/e10_watch_loop.py`, `ledger.md`, `poll.log`;
  - untracked: round17/, e10v3/, bigger_levers/, exp73a-v, exp74, ds_secw_corwin_v1, the v6 folder, `e10_watch/20260927T1101Z.txt`.
- `research/wf_ideas_v4/round17/report.json`: complete, 11:28Z (R17-A0..A11). `REPORT.md` is absent (`round17/report.notes.md` 11:28:16Z).
- `research/wf_ideas_v4/e10v3/*.notes.md` and `research/wf_ideas_v4/bigger_levers/*.notes.md`.
- `experiments/lb_poll/ledger.md` (11:31:20Z) and `poll.log` (last header `=== 2026-09-27T11:31:15Z`, l.13867).
- CronList (~11:34Z).

All times are UTC. IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, superseded, moot, blocked, awaiting user.

**State in one line (11:40Z 27 Sep):**
- **Finals ticked 2/2** = [56563521 #37 K2 0.954, 56563534 #38 twin 0.953]. SELECTED was last re-read at 07:41:28Z (`CONTEXT.md` l.2878).
- **The user changed the regime at 11:08-11:16Z:**
  - E10 v3: copy any public notebook scoring >= 0.955 (l.2917);
  - class-C letter **(b)** = {V*_C, #37}, pre-registered (l.2927);
  - **Q1/Q2 = YES**: exp71 pushed 11:11:50Z (RUNNING, done ~15:15-15:45Z), exp72 submits 28 Sep 00:05Z; **Q3 is open** (l.2933-2939);
  - **the FREEZE is LIFTED** (l.2940);
  - **aggressive mode** (l.2946).
- **Probe 45 = exp70g (K2 + cap 6), 56606948**, submitted 11:15:12Z and PENDING (`ledger.md`). **27 Sep slots: 4 used, 1 left**, for exp70q or exp70r at ~13:00Z (l.2949-2950; `round17/report.notes.md` 11:23:51Z).
- **Probes 43/44 are PENDING** at 11:31:15Z (L > 6.04 h). First terminal header expected ~12:21-13:11Z; the conservative earliest is 12:11Z (`round17/report.json` R17-A2).
- **Round 17 is complete** (11:28Z). **None of R17-A0..A11 is done.** Most urgent:
  - R17-A1 = **the corrected 12:00:00Z line; do NOT log the old R16-A3 text**;
  - R17-A3 = the last-slot pre-score line before the first 43/44 terminal header.
- **The E10 v3 hourly loop is built but NOT running.** No `experiments/e10_watch/watch_loop*.log` exists, and the loop's `tools/e10_snapshot.py` changes are uncommitted (`e10v3/build_watch.notes.md`).
- **exp70q / exp70r have no dummy yet** (no `_dl/biohub-exp70q*`/`exp70r*`). Both GPU lanes are busy: exp71 RUNNING, exp70n dummy QUEUED (`bigger_levers/prep_corwin_secondary.notes.md` 11:28Z). See I172.

**Changes since 09:10Z (curation 16):**
- Done:
  - W158 (l.2880, 289bd52);
  - W159 (`round16/REPORT.md` tracked);
  - W160 (l.2914, chat; push only "requested");
  - W154 (letter (b) 11:09:39Z, bracket headers 11:01:09Z / 11:11:11Z both PENDING; l.2928, `round17/report.json` R17-A1);
  - W135 Q1/Q2 (l.2933).
- Superseded:
  - W161 (R16-A3 text) -> **W169** (R17-A1);
  - W165a (E10 v2) -> E10 v3;
  - W164 (3-hourly P1) -> **W174** (hourly loop);
  - W156a FREEZE: **lifted 11:14Z**;
  - W163 -> **W175**.
- New: actions **W168-W182**, reminders **T87-T99**, insights **I172-I186**.

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W176** (= R17-A8; absorbs W146 / W155 / W162) | **No ROUND 14, 15, 16 or 17 RECORD in CONTEXT** (`grep -c "ROUND 1[4-7] RECORD"` = 0). Also still open:<br>- v6 `NOTES.md` item 4 still says "past the R8 line";<br>- the v6 folder, `e10_watch/20260927T1101Z.txt`, `ledger.md` and `poll.log` are not committed;<br>- `fb_ins35.py` exists only in the session scratchpad `r16rcb/` | overdue (W146 was due 07:30Z) | today, with or after the 12:00Z commit | `round17/report.json` R17-A8; `experiments/ext_optimized-biohub-max-score/v6_2026-09-27/NOTES.md` l.5; `round17/scan_plancheck.notes.md` |
| **W126** | **No RESULTS.md rows for probes 39-42** (all scored; the last row is probe 38, `experiments/RESULTS.md` l.71). No score field in any `exp70*/probe.json`, and every exp70*/exp73*/exp74 `probe.json` carries the boilerplate "above exp56 adopt" (I154) | overdue (D1 04:58Z, D2 07:41Z) | now; soon rows 43-45 will be missing too | `experiments/RESULTS.md` l.71; `experiments/exp70q_k2_maxdiv/probe.json` "rule" |
| W182 (= W142 cont.) | **No NEVER_SUBMIT.md in exp70j / exp70k.** These are class C, "never resubmitted" (R17-A2 (ii)). exp70g is now a legitimate probe 45 and has left this list | not started | before any 28-29 Sep submit | `ls experiments/exp70*/NEVER_SUBMIT*` = none (11:32Z); `round17/report.json` R17-A2 |
| W57 / W66 / W31 / W72 (curator CONTEXT records) | Still missed:<br>- "frozen/duplicated frames" is still in CONTEXT (2 hits);<br>- 0 hits for `out_valid`, `efpost`, `33.1%` | overdue | 26 Sep 12:00 (passed) | `grep -c` (11:33Z) |
| W136 / W160 residue | R16-A2 was logged as "chat + push requested"; **whether the push was sent is still not logged**. R17-A1 asks for "<sent/not-sent>" in the 12:00Z line | partly done | with W169 (12:00Z) | `CONTEXT.md` l.2914; `round17/report.json` R17-A1 |
| W150 | The round prompt is still unchanged (js last commit 13a27a1). R17-A11 (f) adds "~4 h headroom", "R8 hard line" and "no public knob ladders" as stale | overdue, low priority | before round 18 (~13:00Z) | `experiments/workflows/biohub-research-round.js`; `round17/report.json` R17-A11 (f), plan_issues (11) |
| W03 / W02 | The friend A card is stale; Task 0 reply | moot, low priority | - | `PROMPT_FRIEND_A.md` l.7-9; `research/wf_ideas_v3/TASK_FRIEND_A.md` l.17-22 |

## NEXT 24 H (27 Sep 11:40 -> 28 Sep 11:40 UTC)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| **W168** (new; = R17-A0) | with the 12:00Z commit | Save `report_md_ru` of `round17/report.json` as `round17/REPORT.md`. Commit round17/ **by named paths only**: other agents have dirty tools/tests. Commit as the user, no trailer; push | not started (`REPORT.md` absent) | `round17/report.json` R17-A0 |
| **W169** (new; = R17-A1; **replaces W161**) | **12:00:00Z (`date -u`)** | **Log the CORRECTED R8 line, not the R16-A3 template.** The old template would state falsehoods: "no letter", "E10 v2 lapsed", "2 slots left", "exp72 only on a yes". The new line must contain:<br>- E10 v2 superseded by v3; R8 lifted for exp72 and for the public division rungs;<br>- the user messages 11:08, 11:09:39, 11:11:40, 11:14 and 11:16Z;<br>- the bracket check (11:11:11Z header both PENDING);<br>- push sent/not-sent;<br>- the E10 11:01Z baseline;<br>- slots 4 used / 1 left;<br>- the last poll header;<br>- a DEVIATION RECORD (exp71 + post-FREEZE rungs, under user instruction, not a precedent);<br>- E10 cadence.<br>Commit + push | not started | `round17/report.json` R17-A1, plan_issues (2) |
| **W171** (new; = R17-A3) | **before the first 43/44 terminal header (conservative earliest 12:11Z)**; target the 12:00Z commit | Pre-score line for the last 27 Sep slot:<br>(1) exp70r if 43 >= 0.955, else exp70q; 43 not terminal by the decision time -> exp70q;<br>(2) neutral facts for the user: amanatar V6 0.901; cap 6 lab -0.00057 with 85 extra insertions = 0 TP / 4 FP; thr 0.3 has no lab support; exp70q stacks on probe 45's unread knob;<br>(3) submit ~13:00Z (score ~20:00-20:50Z) vs wait for 45 (score ~01:30-02:30Z 28 Sep);<br>(4) the max(43,44) <= 0.953 branch.<br>**AND: neither exp70q nor exp70r has a dummy yet (I172)** | not started | `round17/report.json` R17-A3; `CONTEXT.md` l.2946-2951; no `_dl/biohub-exp70q*` |
| **W170** (new; = R17-A2; continues W156) | **first header with both refs terminal: expected ~12:21-13:11Z, earliest 12:11Z; hard trigger = first header at/after 14:28:22Z (~14:31Z); ListSubmissions fallback 14:40Z** | Read 43/44 with the pruned card:<br>(i) a V*_C exists (COMPLETE, L_hi <= 9.0 h with the ledger gate text, display >= 0.955, the other rung >= 0.954 or ERROR/unscored; a tie -> 44) -> write the re-tick text from API SELECTED (today: untick 56563534, tick V*_C, keep 56563521); the user re-ticks; re-read SELECTED;<br>(ii) otherwise the pair is unchanged;<br>(iii) any other candidate -> facts to the user.<br>Then: CONTEXT line, commit + push, ONE user line. The 43 display also picks exp70r vs exp70q | not started (PENDING at 11:31:15Z) | `round17/report.json` R17-A2; `CONTEXT.md` l.2880-2913, l.2927-2932 |
| **W172** (new; = R17-A4) | only if an E10 v3 trigger passes its gates before the last 27 Sep slot is used | Collision default: the (A) verbatim copy takes the slot and exp70q/r moves to 28 Sep. **Needs the user's one-line OK** (ask in the post-read line). From 28 Sep: keep 2 slots per day for E10 v3 until 29 Sep 12:00Z | awaiting user (not covered by an existing approval) | `round17/report.json` R17-A4 |
| **W174** (new; = R17-A6; replaces W164) | **loop live before 15:00Z**; edges in the RESUME POINT | (1) Commit `tools/e10_snapshot.py`: the committed loop (9cdc047) calls its uncommitted `take_snapshot`. Then start `bash experiments/lb_poll/run_e10_watch_loop.sh` in the background, confirm 2 good runs, and keep 2e87e414 as a backup.<br>(2) Log the E10 v3 edges: target <= 29 Sep 02:00Z; hard ~11:00Z for a 7.5 h notebook, ~06:30Z for a 12 h one.<br>(3) Runbook v3: page score >= 0.955; (A) byte-identical with no 27000 s check; (B) only if the anchors apply once; (C) otherwise; push at trigger and at each submit | not started (no `watch_loop*.log`; `git diff --stat` shows `tools/e10_snapshot.py`) | `round17/report.json` R17-A6; `research/wf_ideas_v4/e10v3/build_watch.notes.md` (NOTE) |
| **W175** (new; = R17-A7; replaces W163) | **after the 43/44 read, by ~15:00Z** | New RESUME POINT, regenerated from CONTEXT; do not paste the R17P-F3/F4/F5/F8 texts. It needs:<br>- finals + SELECTED; the A2 and A5 cards;<br>- answered vs open decisions: exp70b as a final, Q3, finals if a new file >= 0.955;<br>- slots; the schedule;<br>- a RESTORE CARD keyed by action + UTC time, not by timer id; delete the past one-shots 5b23a3ed / 54a8f20d / cdd738f1.<br>Then fix MEMORY.md: the LB-probe line (E10 v3; OC stopped) and the resume line (it still says "latest 26 Sep 22:46 UTC") | not started (last RESUME POINT l.2599) | `round17/report.json` R17-A7; `memory/MEMORY.md` l.9 |
| **W180** (new; exp72 chain) | exp71 done **~15:15-15:45Z** -> T3 dataset -> T5 build (`--patch secswap`) -> dummy + T6 gates -> **submit 28 Sep 00:05Z** -> score ~07:00-08:00Z | Q1/Q2 = YES; **Q3 (exp72 as a final) not answered -> public-only**. Pre-register its read in W173 before it scores | in progress (exp71 RUNNING 11:12Z) | `CONTEXT.md` l.2933-2939, l.2942-2943 |
| **W173** (new; = R17-A5) | **before 17:50Z** (earliest plausible 45 score ~17:56Z) | One pre-score card for probe 45, exp70q/r, exp72 and any E10 v3 copy:<br>- display >= 0.955 + COMPLETE + L_hi <= 9.0 h -> a finals proposal in chat, default partner #37, no mechanical re-tick;<br>- two or more qualify -> one message, the user picks;<br>- <= 0.954 -> info only.<br>Add all of them to the private-read list | not started | `round17/report.json` R17-A5 |
| **W181** (new) | before any of them is dummied or submitted on 28 Sep | **Builds that no CONTEXT entry mentions:**<br>- 20 division rungs exp73a..exp73v (caps 8/12/16, frame cap 2, thr 0.2, DC 0.15-0.225 x forkmid packages; decision table in `bigger_levers/prep_div_combos.json`);<br>- exp74 = K2 + Corwin's CC0 secondary. It needs the private dataset `vitaliineibauer/biohub-secw-corwin-v1` to be **uploaded (not done, needs a go)**;<br>- exp75 coord-inject (prep only).<br>Log them with a pre-score card before any 28 Sep slot use; the dummy queue competes with exp72 (I172, I185) | not started | `research/wf_ideas_v4/bigger_levers/prep_div_combos.notes.md` 11:24-11:33Z; `prep_corwin_secondary.notes.md`; `prep_coord_refiner.notes.md` |
| **W177** (new; = R17-A9; absorbs W98 and W148) | **H1 today after the 43/44 read**; H2 29 Sep by 23:00Z; H3 after the 23:27Z snapshot, before 23:59Z | Replace `round9/LESSONS_draft.md` with the R17LF-1 text, but only after a STALENESS DIFF (~7 stale claims). Apply (a) "not identified" with OOF CI [-0.0007, +0.0050] and (b) the override-budget lesson with the tally READ 1 / USER 6 / SESSION 1. Commit + push as the user | not started (l.7 still has the "~29%" caveat) | `round17/report.json` R17-A9; `research/wf_ideas_v4/round9/LESSONS_draft.md` l.7 |
| W165b | any time up to 29 Sep ~18:00Z | exp70b-as-final letter (still open; default = no change) | awaiting user | `round17/report.json` R17-A7 (c); `CONTEXT.md` l.2883-2885 |
| W19 / W73 | until 29 Sep 20:00 | ONE poller (PID 20052). Before any submit, the last header must be < 15 min old and not a 429 | in progress (last header 11:31:15Z) | `poll.log` l.13867; `round17/v_hyp_post_r8_plan_r17p-f9.notes.md` |
| W102 / W93 (updated) | standing | Never resubmit class C (exp70j/k). **exp70g and exp71 are now user-authorised (11:11-11:16Z)**; exp65/66 and the dry-run kernel stay never-submit | standing (partly superseded) | `CONTEXT.md` l.2933-2951; `round17/report.json` R17-A2 (ii) |
| W76 | **round 18 ~13:00-15:00Z** | Audit, not ideas:<br>- the 43/44 read and the last-slot choice (did the R17-A3 facts reach the user before the submit?);<br>- the 12:00Z line, the A5 card and the hygiene commit, all pushed;<br>- the E10 v3 loop is live and the restore card matches CronList;<br>- the exp71 -> exp72 chain;<br>- browser: notebook page scores | round 17 done (untracked) | `round17/report.json` next_focus |
| T87 (new) | **12:00:00Z** | W169 line + the W168/W171 commit (supersedes T03's "E10 v2 lapse") | - | `round17/report.json` R17-A1 |
| T88 (new) | **12:11Z** (conservative earliest), **12:21-13:11Z** expected | First 43/44 terminal header. W171 must be logged before it | - | `round17/v_plancheck_pc17-04.notes.md` |
| T89 (new) | **~12:15-12:30Z** | Latest start of an exp70q/exp70r dummy (~1,464-1,740 s run + queue) for a ~13:00Z submit. Only one GPU lane is free once exp70n's dummy ends (I172) | - | `CONTEXT.md` l.2448 (dummy ~1,464 s); `bigger_levers/prep_corwin_secondary.notes.md` 11:28Z |
| T90 (new) | **~13:00Z** | Last 27 Sep slot: exp70q or exp70r (score ~20:00-20:50Z) | - | `CONTEXT.md` l.2949-2950; `round17/report.json` R17-A3 |
| T91 (new) | **~14:21Z / 14:28:22Z / 14:40Z** | Last header that can satisfy L_hi <= 9.0 h / read trigger / ListSubmissions fallback | - | `round17/report.json` R17-A2 |
| T92 (new) | **~15:00Z** | E10 v3 loop live (W174); RESUME POINT (W175) | - | `round17/report.json` R17-A6, R17-A7 |
| T93 (new) | **~15:15-15:45Z** | exp71 done -> T3 dataset -> T5 exp72 build -> dummy/T6 | - | `CONTEXT.md` l.2937-2939 |
| T94 (new) | **17:50Z** | W173 card deadline | - | `round17/report.json` R17-A5 |
| T95 (new) | **~18:07-18:50Z**; 9.0 h clock **20:15:12Z** | Probe 45 (56606948) score | - | `round17/report.notes.md` 11:23:51Z |
| T96 (new) | **~20:00-20:50Z** | exp70q/r score (if sent ~13:00Z) | - | `round17/report.json` R17-A3 (3) |
| T32 / T39 | 27 Sep 12:04, 15:04, 18:04, 21:04 (timer 2e87e414, hh:04) | Backup E10 P1 checks until the hourly loop runs; the 12:04Z tick is a no-op by the 2.5 h staleness rule | timer alive (CronList 11:34Z) | `round17/report.json` R17-A1 last sentence |
| T18 / T42 (updated) | **28 Sep 00:00** | Slot reset, 5 slots:<br>- exp72 at 00:05Z;<br>- 2 kept for E10 v3 (W172, needs the user's OK);<br>- the rest for the 28 Sep division rungs (W181) | - | `CONTEXT.md` l.2942-2943; `round17/report.json` R17-A4, R17-A7 (d) |
| T97 (new) | **28 Sep ~07:00-08:00Z** | exp72 score (public-only unless Q3 = yes) | - | `round17/report.json` R17-A5 |
| T67 | standing | **All timers are session-only and fire only while the REPL is idle** (I181). Live: 2e87e414, 012fa6dd, 328f7392, 18ff4796, bb224de9. Stale one-shots still listed: 5b23a3ed, 54a8f20d, cdd738f1 | - | CronList ~11:34Z; `round17/v_hyp_post_r8_plan_r17p-f9.notes.md` |

## LATER (28 Sep 11:40 -> 29 Sep 23:59 UTC, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T46 | **28 Sep 12:00** | F1 consolidation under R8 (the user lifted R8 for E10 v3, exp72 and the division rungs) | `CONTEXT.md` l.1671; l.2917-2951 |
| T19 / W77 + W166 (e) | **28 Sep 17:57** (012fa6dd) | API SELECTED + page read of the ticks; N954 / N955 / team count as plain numbers | CronList; `round16/report.json` R16-A9 (e) |
| T84 | 28 Sep ~18:30Z | Old "last exp72 yes" edge: **moot** (Q2 = yes 11:11:40Z). What remains is Q3 | `CONTEXT.md` l.2933 |
| T60 | **29 Sep 12:00** | G2 must have landed for exp72 to be finals-eligible (Q3 = yes only). R17 calls Q3 "effectively closed unless G2 starts today" | `CONTEXT.md` l.2736; `round17/report.json` R17-A7 (c) |
| T35 | 28 Sep 22:00 | Final admission table: ladder + class C (43/44) + 45 + exp70q/r + exp72 + E10 v3 copies | `research/wf_ideas_v3/FINAL_REPORT.md` l.178; `round17/report.json` R17-A5 |
| T20 | **29 Sep 00:00** | Last slot reset | `CONTEXT.md` l.2355 |
| T98 (new; replaces T29/T47/T85) | **29 Sep 02:00Z target; hard ~06:30Z (12 h notebook) / ~11:00Z (7.5 h x138-family)** | E10 v3 submit edges. The hourly loop ends 29 Sep 12:00Z | `round17/report.json` R17-A6 (2) |
| T09 / W77 | **29 Sep 11:57** (328f7392) / **17:57** (18ff4796) | Tick checks + remind the user (plain numbers) | CronList |
| T86 | 29 Sep ~18:00Z | Practical expiry of the exp70b letter (W165b) | `round16/report.json` R16-A8 (i) |
| T48 (= W131) | **29 Sep ~19:00** | L9 last read + class C (b) + 45/q/r/exp72/E10 v3 per W173. Never two byte-identical files; never a non-COMPLETE file | `CONTEXT.md` l.2510-2518; `round17/report.json` R17-A5 |
| T10 (updated) | **29 Sep 20:00** | **Our buffer**, not a Kaggle freeze. Re-ticks are allowed until 23:59Z, so the ~20:05Z SELECTED check must not say "FINALS FROZEN". Read F = API SELECTED after 23:59Z and log "FINALS FINAL [refs]" | `round17/report.json` plan_issues (7), R17-A7 (e) |
| W178 (new; = R17-A10) | **definitions line before 29 Sep 23:00Z**; hourly saves 30 Sep | Private-read addenda:<br>- save the public LB hourly into per-call folders;<br>- "private board appeared" = a non-empty privateScore for #37/#38 (I180);<br>- a definitions line for S, D, X and X rank;<br>- the LF-3 row;<br>- read list += 45, q/r, exp72, E10 v3 copies | `round17/report.json` R17-A10 |
| T49 | 29 Sep 23:00-23:45 (bb224de9 at 23:27) | Final public LB snapshot to `experiments/private_read/` (the CLI creates the folder itself) | CronList; `round17/scan_hyp_post_r8_plan.notes.md` 11:12Z |
| T11 | 29 Sep 23:59 | Deadline. A submit must **finish** before it (participant comment only) | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 |
| T30 / T50 | 30 Sep from 00:15Z, hourly | Private read v2 + L1-L7 + DC-DOSE + W166 (d) + W178 | `CONTEXT.md` l.2570-2598; `round17/report.json` R17-A10 |
| **W179** (new; = R17-A11) + W147 / W166 | by 30 Sep | Curator edits: DoG/optional-node closed reasons; dorado division-blind; I-171 detail; I-310 deviation note; amanatar V6 row; the round-template fix. The W147/W166 list is unchanged | `round17/report.json` R17-A11; `round16/report.json` R16-A9 |
| W29 | after 29 Sep | Post-deadline list (+ LOEO OOF division-transfer bed, z-re-localisation) | `round17/report.json` R17-A11 (a)-(b) |

**Done, superseded or moot since 09:10Z (for the record):**
- W158 (R16-A1): READ ADDENDUM in `CONTEXT.md` l.2880-2913, commit 289bd52, pushed before any 43/44 terminal header.
- W159 (R16-A0): `research/wf_ideas_v4/round16/REPORT.md` tracked.
- W160 (R16-A2): message sent 09:15Z (l.2914). The push result is still open (see OVERDUE).
- W154: class-C letter (b) at 11:09:39Z, pre-registered (l.2927-2932). The 11:11:11Z header was also PENDING (`round17/report.json` R17-A1).
- W135 / W128 / W106: Q1/Q2 YES 11:11:40Z (l.2933); exp71 pushed (l.2937). Q3 is still open.
- W156a FREEZE: lifted by the user 11:14Z (l.2940). T58/T83/T84 edges moot.
- W161 (R16-A3 text): superseded by W169 (R17-A1). W165a (E10 v2): superseded by E10 v3 (l.2917).
- W164 (3-hourly P1): the 11:01Z P1 was not met (`experiments/e10_watch/20260927T1101Z.txt`); replaced by W174.
- W163: replaced by W175.

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I172** (new) | "GPU sessions: exp71 RUNNING, exp70n QUEUED -> no free session now"; "GPU at 11:28Z: exp71 RUNNING + exp70n dummy QUEUED = 2 sessions -> no dummy push" | `research/wf_ideas_v4/bigger_levers/prep_coord_refiner.notes.md`; `prep_corwin_secondary.notes.md` | **exp70q/exp70r have no dummy** (no `_dl` folder), and a dummy takes ~1,464-1,740 s (`CONTEXT.md` l.2448). exp70n (thr 0.3 alone) has **no slot today** (1 slot left), yet it holds the only free lane. The ~13:00Z plan (l.2949) silently depends on this queue |
| **I173** (new) | "the main session's commit 9cdc047 already contains experiments/lb_poll/e10_watch_loop.py ... but tools/e10_snapshot.py (take_snapshot) is still uncommitted: the loop needs it; commit both" | `research/wf_ideas_v4/e10v3/build_watch.notes.md` | A checkout, reset or other agent's edit breaks the only E10 v3 watcher. `tools/build_probe_kernel.py` (+372 lines, SI builder) and `tools/e10_port_gate.py` (+316) are also uncommitted (`git diff --stat`) |
| **I174** (new) | "e10_snapshot's amanatar status line said 'no change' (it tracks run status only, not the page Public Score) -> P1 blind spot"; "the kernel API has no score field, so a signal starts a page look" | `round17/scan_browser.notes.md` ~11:16Z; `round17/report.json` new_facts (6) | The E10 v3 trigger is a **page** score >= 0.955, and no tool reads it. A signal needs a browser look, so latency matters (ties at 0.955 go to the earlier submission) |
| **I175** (new) | Corwin secondary: "pilkwang's secondary beat theirs by +0.006 public on placement -> EV plausibly <= 0"; "checkpoint wrapping/key format not re-verified" | `bigger_levers/prep_corwin_secondary.notes.md` | Together with "exp23 secondary swap ... lost 0.007 on the LB" (`CONTEXT.md` l.2726-2727) and "FT weights on public stacks 0 of 5" (I143), the prior for **exp74 and exp72** (both secswap) is negative. Say so in W173 |
| **I176** (new) | "the per-video cap binds hard at cap 4 (eligible 14/0/33/142 -> added 4/0/4/4) ... the cap, not the threshold, is the binding insertion knob; thr only matters on clips with < cap eligible"; "I4 ultra is a real cliff risk (up to ~1,200-1,600 extra insertions)" | `bigger_levers/prep_div_combos.notes.md` 11:21-11:33Z | exp70n (thr 0.3 alone) is likely near-inert on the public set. The thr part of exp70q adds little beyond cap 6. The lab cap-6 extras were "0 TP / 4 FP / 81 unannotated" (`round17/report.notes.md`). amanatar V6 (looser gates) fell to 0.901 |
| **I177** (new) | "amanatar/optimized-biohub-max-score V6 now shows public 0.901 (-0.052 vs x138) ... a public read that 'more divisions via looser gates' can crash" | `round17/report.json` new_facts (1); https://www.kaggle.com/code/amanatar/optimized-biohub-max-score | Reaches the user only via R17-A3 (2). **It must be stated before the exp70q/r submit** (the premise of aggressive mode) |
| **I178** (new) | Rule-break tally 23-27 Sep: "8 breaks/reopenings ... surprise-triggered 1 of 8 ... dominant trigger = user rank pressure" | `round17/v_hyp_lessons_final_r17lf-4.notes.md` | Lesson for W177: pre-declare an override budget, not just the surprise branch |
| **I179** (new) | "The tick-check wording treats 20:00Z as a Kaggle freeze; it is our own buffer (Kaggle allows re-ticks until 23:59Z)" | `round17/report.json` plan_issues (7) | Timers 18ff4796 / T10 texts say "last check before the 20:00 UTC"; finals F must be read after 23:59Z |
| **I180** (new) | "board check 'top-50 differs from 23:30Z snapshot AND our Score == max over F' can false-fire on 30 Sep 00-08Z ... key the switch on privateScore" | `round17/v_hyp_post_r8_plan_r17p-f11.notes.md` | Private-read v2 (d) (`CONTEXT.md` l.2578-2595) still has the flawed signal; W178 |
| **I181** (new) | CronCreate: "Jobs live only in this Claude session"; "jobs only fire while the REPL is idle"; the RESUME POINT (l.2618) names stale ids 2f0d1fa1 / c7cd2e6b | `round17/v_hyp_post_r8_plan_r17p-f9.notes.md` | A busy main session (builds, workflows) can **delay** the 29 Sep 11:57Z / 17:57Z tick checks. The user's own alarms are the backstop (I159) |
| **I182** (new) | "exp72 moves to 00:05 UTC 28 Sep" but "Q3 (exp72 as a final) NOT answered -> exp72 is public-only"; G2 must land by 29 Sep 12:00 | `CONTEXT.md` l.2935-2936, l.2942-2943, l.2736 | If the user expects exp72 to count, Q3 must be asked **before** it scores (~07-08Z 28 Sep), or it cannot become a final |
| **I183** (new) | "the lab is against bigger caps (ins_cap6) but was wrong in sign for DC; the only large public signal is 'fewer divisions = -0.005', so the rows lean to 'more divisions'" | `bigger_levers/prep_div_combos.notes.md` 11:33Z | One confounded public read drives 20 rungs. The 43/44 (DC 0.20/0.225) and 45 (cap 6) reads are the real test of "more divisions" (R17-A3 (4)) |
| **I184** (new) | Corwin dataset: "LAYOUT DOES NOT MATCH x138's finder ... FileNotFoundError in cell 3"; fix = repack as `vitaliineibauer/biohub-secw-corwin-v1`, "prepared, NOT uploaded" | `bigger_levers/prep_corwin_secondary.notes.md` | exp74 cannot even run its dummy until the dataset upload (a Kaggle write that needs a go) |
| **I185** (new) | GPU quota "07:55 / 30 h used" (26 Sep ~21:5x); Q1 "~4.5 GPU-h; ~22 h quota left"; weekly reset was 26 Sep 00:00 UTC | `CONTEXT.md` l.2542, l.2729, l.1545 | exp71 (4.5 h) + ~25 queued dummies (exp70n/q/r, exp73a-v, exp74, exp72; ~0.4-0.5 h each) is about 10-12 h of the quota before 29 Sep. Nobody has re-read the Settings page since. The next reset is after the deadline |
| **I186** (new) | Letter-window blind gap: "R16-A1 (4) letter window uses the header BEFORE the letter: up to ~10 min blind gap" | `round17/scan_plancheck.notes.md` | Moot for the (b) letter (bracket 11:11:11Z also PENDING). It applies again to any future pre-score letter (45, q/r, exp72) |
| I161 | "X's own private rank is modelled at or below the bronze line (~#400) in every field" | `round16/scan_hyp_forecast_update.notes.md` | Partly surfaced (forecast line `CONTEXT.md` l.2914-2916). Keep for the 29 Sep ~19:00Z read |
| I163 | The user's "one final aimed at PUBLIC (best public-scoring variant)"; exp70b is that file | `CONTEXT.md` l.2388, l.2407 | W165b still open; R17-A7 lists it as open, default no change |
| I165 | `fb_ins35.py` + out.json only in the session scratchpad `r16rcb/`; forecast scripts `r16/forecast_mc*.py` are session-only | `round17/scan_plancheck.notes.md`; `round17/report.json` R17-A8 (5) | Lost with the session unless W176 (5) runs |
| I142 / I143 | "+0.006 is the exp60 IN-SAMPLE number ... honest +0.0019"; FT weights "0 of 5" on the LB | `round14/report.json` new_facts (12)-(13); `round16/report.json` R16-A2 | Still not in CONTEXT (W176). I143 now bears on exp72/exp74 (I175) |
| I154 | `probe.json` "rule" boilerplate "above exp56 adopt" | every exp70*/exp73*/exp74 `probe.json` | Still unfixed (W126). It is now copied into 22 more builds |
| I114 | "x138 cell 1 = configuration guard: BIOHUB_DET_THRESHOLD must equal 0.965 ... else RuntimeError" | `reach0955/v_intel.notes.md` | Matters for E10 v3 (B)/(C) of a DET-changed fork (V6 used DET 0.960) |
| I116 | Agents label local (UTC+3) times as "Z"; cron hours are local | `reach0955/discussions_2026-09-26.notes.md` | e.g. `bigger_levers/*.notes.md` file mtimes are local; CronList "57 14 29 9" = 29 Sep 11:57Z |
| I72 | The harness asks for a Co-Authored-By trailer; the user's rule forbids it | `memory/feedback-git-no-coauthor.md` | For W168 / W169 / W176 / W177 |
| I95 | The harness has refused the round-report Write 10 rounds running (8-17) | `round17/report.notes.md` 11:28:16Z | W168 |
| I145 | "It has to finish before the deadline to count" | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 | For E10 v3 edges (T98) |
| I149 / I150 / I151 / I155 / I157 / I162 / I164 / I166-I171 and older | Unchanged | `_curation/16/watch.json`, `_curation/15/watch.json` | I164 (the user's refusal (7)) and I166 (letter window as an event) are now moot: Q1 yes 11:11:40Z, letter logged 11:09:39Z |

**Resolved since 09:10Z:**
- I171 ((b) partner ambiguity): the letter names #37 (`CONTEXT.md` l.2931).
- I166: the letter was logged before any terminal header.
- I164: the user answered Q1 explicitly (l.2933).
- I159 residue: still open (I181).
- Details: `_curation/16/watch.json`.
