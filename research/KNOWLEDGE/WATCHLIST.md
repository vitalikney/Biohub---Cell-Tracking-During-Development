# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-27 09:10 UTC (curation 16). This is an incremental update of the curation-15 build from 06:10 UTC (`research/KNOWLEDGE/_curation/15/watch.json`).

Sources read for this update:
- `CONTEXT.md` at main HEAD **0bd1408** (2,900 lines; `## 9. Literature` at l.2880). Entries new since curation 15:
  - **PROBES 43/44 PRE-SCORE ENTRY** 06:19 (l.2814-2871; R15-A1 (1)-(9); committed 4161226);
  - **LADDER READ D2** 07:41 (l.2872-2879; committed 0bd1408).
- `git log` since da9766e: 4161226 (06:19:26Z), 0bd1408 (07:41:52Z). `git status -sb` = `main...origin/main` (both pushed). Untracked: `research/wf_ideas_v4/round16/`, `experiments/e10_watch/20260927T0831Z.txt`, `experiments/ext_optimized-biohub-max-score/v6_2026-09-27/`; modified: `experiments/lb_poll/ledger.md`, `poll.log`.
- `research/wf_ideas_v4/round16/report.json` (**complete**, written 08:57:27Z; R16-A0..A9, new_facts, plan_issues, rejected, next_focus) and the `scan_*.notes.md` files. `REPORT.md` is absent for the 9th round running (`round16/report.notes.md`).
- `experiments/lb_poll/ledger.md` (43/44 rows at 08:50:47Z, l.20-21; exp70b row l.22), `poll.log` (last header `=== 2026-09-27T08:50:47Z`, l.12891), `experiments/RESULTS.md` (last probe row l.71 = probe 38).
- CronList (read-only, ~09:03Z).

All times are UTC. IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, superseded, moot, blocked.

**State in one line (09:10Z 27 Sep):**
- **Finals ticked 2/2** = [56563521 #37 K2 0.954, 56563534 #38 twin 0.953]; API SELECTED re-read 07:41:28Z after probes 39-44 (`CONTEXT.md` l.2876-2877).
- **Ladder D2 is read:** probe 42 exp70b = **0.954** COMPLETE at 07:40:36Z, UP **attributable** (U4, fm45 POS), ledger L (7.41, 7.58] h, "insertion gate 8.0 h did NOT fire". BASE none -> no combo; < 0.955 -> not V*; **no re-tick by rule** (l.2872-2876).
- **exp70b is now our best public file** (8th of 113 in the 0.954 block, #255; `round16/report.json` new_facts). Whether the user wants it as the public-aimed final is asked in the brief; default = no change (l.2876-2877).
- **Probes 43 exp70j (56598763) / 44 exp70k (56598765) are PENDING** at 08:50:47Z (L > 3.37 h; `ledger.md` l.20-21). Earliest terminal ~12:10Z; 9.0 h clocks 14:28:13Z / 14:28:22Z (`round16/report.json` new_facts).
- **The pre-score entry R15-A1 is logged and pushed** (06:19Z, 4161226) with the FREEZE and the class-C table (l.2814-2871).
- **The watcher is stopped** (07:37:07Z, 64 calls, 0 x 429; l.2876). poll.log is the only record for 43/44.
- **Morning brief sent in chat ~07:45Z**; timer 65b1b746 deleted (l.2877). **No user letter is logged since** (`round16/report.notes.md`).
- **Round 16 is complete** (08:57Z). None of R16-A0..A9 is done yet. Most urgent: **R16-A1 (read addendum) now, hard 11:45Z / before the first 43/44 terminal header**, then **R16-A2 (one user message) by 11:00Z**.
- **2 slots left on 27 Sep; 5 on 28 Sep** (`round16/report.json` R16-A3). The FREEZE holds (l.2821-2826).

**Changes since 06:10Z (curation 15):**
- Done: W151 (l.2814, pushed 06:19Z before any 43/44 header; `round16/scan_plancheck.notes.md` 08:45Z), W152 (`round15/REPORT.md` in 4161226), W141 D2 (l.2872), W153 (SELECTED 07:41:28Z, l.2876), W136 (brief in chat ~07:45Z, l.2877; the push status is not logged), W140 (quiet window ended 06:45Z), W145/T68/T70 (watcher stopped 07:37:07Z), E10 P1 at 08:31Z (not met; `experiments/e10_watch/20260927T0831Z.txt`).
- The FREEZE (W156a) is now **standing** (l.2821-2826).
- New: actions **W158-W167** (= R16-A0..A9 + hygiene), reminders **T77-T86**, insights **I161-I171**.
- Superseded: the W135 "~09:00Z last useful yes" edge (T58) is moot; exp72 timing is now "last yes with ERROR room ~28 Sep 08:00Z, last yes at all ~28 Sep 18:30Z" (`round16/report.json` R16-A8 (iv), rejected).

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W126** | **Ladder records are missing:**<br>- no RESULTS.md row for probes 39-42 (all four are scored; the last row is probe 38, l.71);<br>- no score field in any `experiments/exp70*/probe.json`;<br>- all exp70* probe.json carry the builder boilerplate "above exp56 adopt", which contradicts class C for exp70j/k (I154) | overdue (D1 04:58Z, D2 07:41Z) | now; with R16-A5 at the latest | `experiments/RESULTS.md` l.71; `round15/scan_plancheck.notes.md` |
| **W146 / W155** (ROUND 14 / ROUND 15 RECORD) | Neither record is in CONTEXT (`grep -c "ROUND 14 RECORD"` = 0, `"ROUND 15 RECORD"` = 0). W146 was due before 07:30Z. R16-A5 (i) now carries the R15-A6 text verbatim; the R14-A6 text is still only in `round14/report.json` | overdue | W146 07:30Z (passed); now with R16-A5 | `round14/report.json` R14-A6; `round15/report.json` R15-A6; `round16/report.json` R16-A5 (i) |
| W142 (extended) | No NEVER_SUBMIT.md in **exp70g, exp70j, exp70k** (and none in exp70a/b/d/e). exp70j/k are class C and "never resubmitted" under the FREEZE (l.2824-2825) | not started | before any further 27-29 Sep submit | `ls experiments/exp70*` (09:0xZ); `CONTEXT.md` l.2824 |
| W57 / W66 / W31 / W72 (curator CONTEXT records) | Due 26 Sep 12:00 and **still missed**:<br>- `CONTEXT.md` l.22 still says "frozen/duplicated frames with GT still moving" (I39);<br>- `grep -c` finds 0 hits for `out_valid` (I47), `efpost` (I51) and `33.1%` (I77) | overdue | 26 Sep 12:00 (passed) | `CONTEXT.md` l.22; `grep -c` = 0 (09:0xZ) |
| W150 (residue) | **The round prompt is still unfixed** (js last commit 13a27a1): l.37 makes the browser agent run `e10_snapshot.py` first; l.38 is stale ("finals decided = #37 K2 + #38 twin; remaining: the E10 watch ..."). Round 16's 08:31Z snapshot fell after the exp70b event (07:37Z), so no harm this time | overdue, low priority | before round 17 (~11:00Z) | `experiments/workflows/biohub-research-round.js` l.35-38; `round16/scan_browser.notes.md` 08:31Z |
| W136 (residue) | The D2 entry says only "Morning brief sent in chat ~07:45Z"; **whether a PushNotification went out is not logged** | partly done | with R16-A5 (ii) | `CONTEXT.md` l.2877; `round16/report.json` R16-A5 (ii) |
| W03 | The friend A card is stale (`PROMPT_FRIEND_A.md` l.7-9; last change b41ec05) | partly done, low priority | not urgent | `git log -1 -- PROMPT_FRIEND_A.md` |
| W02 | Friend A's "Task 0" reply | overdue and moot | 25 Sep 18:00 | `research/wf_ideas_v3/TASK_FRIEND_A.md` l.17-22 |

## NEXT 24 H (27 Sep 09:10 -> 28 Sep 09:10 UTC)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| **W158** (new; = R16-A1) | **now; hard before the first poll.log header showing 56598763 or 56598765 terminal (ERROR can come any time; earliest COMPLETE ~12:10Z); practical edge 11:45Z** | **PROBES 43/44 READ ADDENDUM**, one CONTEXT entry (text ready), quoting the last poll.log header with both refs PENDING:<br>(1) COMPOSITION: INS = #37 by default, exp70b only on the user's letter; (b) partner = #37 unless the letter names exp70b; E10 "#37" = INS only for a no-insertion port;<br>(2) RE-TICK order;<br>(3) READ TRIGGER with a timeout: first header with both terminal, or the first header at/after 14:28:22Z; 14:40Z ListSubmissions fallback; a non-terminal ref is UNSCORED;<br>(4) LETTER WINDOW = an event, not 12:00Z;<br>(5) ANSWER PARSING: a blanket yes never authorises the exp71 push.<br>Commit + push as the user with round16/ (no trailer) | not started (`grep -c "READ ADDENDUM" CONTEXT.md` = 0) | `round16/report.json` R16-A1, plan_issues (PC16-02/04, R16AP-1/8) |
| **W159** (new; = R16-A0) | with W158 | Save `report_md_ru` of `round16/report.json` as `round16/REPORT.md`; commit with W158 | not started | `round16/report.notes.md` 08:57Z |
| **W160** (new; = R16-A2) | **once, right after W158 is pushed; no later than 11:00Z** | **One merged user message** (Russian chat text + <= 180-char push, both ready): defaults if no answer; neutral exp70b facts ("the 0.955 bar was ours, not yours"); only the better final counts; #38 is a narrow hedge; class-C letter only before the first 43/44 terminal header; exp72 has no deadline before 28 Sep ~08:00Z. Ask point by point: E10 v2, exp70b, class C (a)/(b)/(c) + (b) partner, Q1/Q2/Q3 separately. Log "R16-A2 message sent (chat + push: sent / not-sent)" | not started (`grep -c R16-A2` = 0) | `round16/report.json` R16-A2 |
| **W154** (class-C letter) | **before the first poll.log header with 43 or 44 terminal** (earliest ~12:10Z; ERROR earlier) | The user's (a)/(b)/(c) letter counts as pre-registered only if logged verbatim with `date -u` while the last header shows BOTH refs PENDING (quote it). Later = USER DECISION AFTER SCORE. No answer = (a) | awaiting user (no letter logged after the 07:45Z brief) | `CONTEXT.md` l.2834-2836; `round16/report.json` R16-A1 (4) |
| W165a (new; = R16-A8 (iii)) | **before 12:00:00Z** and before any trigger | E10 v2 yes counts only then; scope = ref + version first seen after the OK (baseline = the newest e10_watch snapshot before the OK). amanatar V6 and the mtoshidesu kernel stay under v1 | awaiting user | `round16/report.json` R16-A8 (iii) |
| **W161** (new; = R16-A3; replaces W157) | **12:00:00Z** (`date -u`) | **R8 CUTOFF PASSED; E10 v2 LAPSED** line (text ready) unless an E10 v2 OK was logged before; a later v2 yes = USER OVERRIDE, forward-only; exp71/exp72 only on an explicit named yes. Commit with the next commit | not started | `round16/report.json` R16-A3; `CONTEXT.md` l.1671-1672 (R8) |
| W98 (residue: I69 caveat) | **12:00Z** | `LESSONS_draft.md` l.7 still says "public LB (one embryo, ~29% of the hidden test)" as fact | partly done | `research/wf_ideas_v4/round9/LESSONS_draft.md` l.7 |
| W76 | **round 17 ~11:00-11:30Z**; **round 18 ~13:00-15:00Z** | R17: audit W158 (logged with a quoted PENDING header, pushed before any terminal header), W160 sent once, any user letter vs the first terminal header, the 12:00Z W161 line. R18: audit the 43/44 read, the post-read E10 P1, the ROUND 16 RECORD, the new RESUME POINT. **After that research is closed: monitoring and hygiene only** | round 16 done (untracked) | `round16/report.json` next_focus |
| **W156** (= R15-A5 + **R16-A4**) | **~12:10-13:10Z expected; hard trigger = first header at/after 14:28:22Z; 14:40Z ListSubmissions fallback** | Read 43/44 mechanically (R15-A1 (3)/(4) + W158): displays, ledger L ranges with the insertion-gate text, V*_C yes/no, letter timing, resulting pair. Push one line (with exact untick/tick text if a letter makes a re-tick due). Record L6/L7. **No resubmit, no rung (FREEZE)** | not started (PENDING at 08:50:47Z) | `round16/report.json` R16-A4; `ledger.md` l.20-21 |
| **W163** (new; = R16-A6) | **after the 43/44 read, by ~15:00Z** (or at 12:00Z if the read is late) | **New RESUME POINT** in CONTEXT (finals + last SELECTED, ladder 39-44, D1/D2, 43/44 read, deviation record + FREEZE, W158 addendum, pending letters with expiry, E10 status, slots, live timers, poller, W6, 30 Sep read list). Then repoint the memory resume line (it still says "latest 26 Sep 22:46 UTC") | not started | `CONTEXT.md` l.2599 (last RESUME POINT); `memory/MEMORY.md` resume line; `round16/report.json` R16-A6, plan_issues (PC16-06) |
| **W162** (new; = R16-A5) | **today, after W158; ideally in the 12:00Z commit** | **ROUND 16 RECORD** (text ready: D2 audit PASS, E10 08:31Z not met, intel #255, forecast premise, rechecks, exp72 path, nothing reaches R8) + round-15 hygiene: (i) ROUND 15 RECORD verbatim; (ii) push-status line; (iii) fix `v6_2026-09-27/NOTES.md` item 4 and git-add the v6 folder, `e10_watch/20260927T0831Z.txt`, ledger.md, poll.log; (iv) slots line | not started (`grep -c "ROUND 16 RECORD"` = 0) | `round16/report.json` R16-A5; `experiments/ext_optimized-biohub-max-score/v6_2026-09-27/NOTES.md` l.5 |
| **W164** (new; = R16-A7; continues W149) | next P1 **after the 43/44 read (~12:30-13:30Z)** rather than exactly 12:04Z; then every 3 h to **29 Sep 00:00Z** | E10 P1. amanatar V6 stays post-deadline whatever it scores (fails P3); mtoshidesu kernel notify-only. Timer 2e87e414 fires at hh:04 (12:04Z would precede the read) | in progress (08:31Z not met) | `round16/report.json` R16-A7; `experiments/e10_watch/20260927T0831Z.txt`; CronList 2e87e414 |
| W135 / W128 / W106 (= R16-A8 (iv)) | **last yes with ERROR room ~28 Sep 08:00Z; last yes at all ~28 Sep 18:30Z** | exp71/exp72: only a **named** Q1 + Q2 yes triggers the push (a blanket yes does not). Score ~T+11.7-15.2 h. Recommendation: no (0/5 model swaps on the LB; P(eligible final) ~0.01-0.03) | blocked (awaiting user) | `round16/report.json` R16-A8 (iv), rejected (R16AP-4); `CONTEXT.md` l.2722-2746 |
| W165b (new; = R16-A8 (i)) | any time up to **29 Sep 20:00Z (practically 18:00Z)** | exp70b-as-final letter: log as USER DECISION AFTER SCORE; re-tick at once (untick 56563521, tick 56592350, keep 56563534) unless a class-C (b)/(c) letter is pending, then one re-tick after the 43/44 read; re-read SELECTED | awaiting user | `round16/report.json` R16-A8 (i), R16-A1 (2) |
| W156a / FREEZE | standing until 29 Sep 23:59 unless the user says otherwise in chat | No DC rung, no DC / fm45 / lp30 combo on a DC base, no other ladder submit, no exp70m, never resubmit a class-C file. Slot order: E10 port > unchanged resubmit of an ERRORed finals-relevant file > exp72 (yes only) > empty | **standing** | `CONTEXT.md` l.2821-2826, l.2871 |
| W19 / W73 | until **29 Sep 20:00** | ONE poller. Before any submit, the last successful header must be < 15 min old and not a 429 | in progress | `experiments/lb_poll/ledger.md` l.6; `poll.log` l.12891 |
| W102 / W93 | standing | Protect the finals' inputs. Never push or submit exp65 / exp66, exp70g, exp71, exp70j/k again, or the dry-run kernel | standing | `CONTEXT.md` l.2223-2226, l.2249-2252, l.2824 |
| T77 (new) | **11:00Z** | Latest send time for W160 | - | `round16/report.json` R16-A2 deadline |
| T71 -> T78 (new) | **~11:00-11:30Z** | Round 17 (files only) | - | `round16/report.json` next_focus |
| T72 | **11:45Z** | Practical hard edge for W158 (and W159) | - | `round16/report.json` R16-A1 deadline |
| T03 | **12:00:00Z** | R8 cutoff; E10 v2 lapse (W161); W98 | - | `CONTEXT.md` l.1671; `round16/report.json` R16-A3 |
| T73 | **~12:10Z earliest** (ERROR any time); ~12:10-13:10Z expected | 43/44 terminal; the class-C letter window closes at that header | - | `round16/report.json` R16-A1 (4), new_facts |
| T79 (new) | **14:28:13Z / 14:28:22Z** | 9.0 h clocks of 43/44; the first header at/after 14:28:22Z is the read trigger if either is still PENDING | - | `CONTEXT.md` l.2837; `round16/report.json` R16-A1 (3) |
| T80 (new) | **14:40Z** | ListSubmissions fallback read if poll.log has no header | - | `round16/report.json` R16-A1 (3) |
| T74 -> T81 (new) | **~13:00-15:00Z** | Round 18 (audit the read, E10, ROUND 16 RECORD, RESUME POINT) | - | `round16/report.json` next_focus |
| T82 (new) | **~15:00Z** | W163 RESUME POINT due | - | `round16/report.json` R16-A6 |
| T66 | from **12:00Z** | Curator edits W147 / W166 and the W148 hindsight commit may start | - | `round14/report.json` next_focus |
| T32 / T39 | 27 Sep 12:04, 15:04, 18:04, 21:04 | E10 P1 checks (timer 2e87e414); prefer the post-read run (W164) | timer alive | CronList |
| T18 / T42 | **28 Sep 00:00** | Slot reset: 5 slots for 28 Sep, reserved for an E10 v1 port or an unchanged ERROR resubmit (none pending) | - | `round16/report.json` R16-A3 |
| T83 (new) | **28 Sep ~08:00Z** | Last exp72 yes with room for an ERROR resubmit | - | `round16/report.json` R16-A8 (iv) |
| T67 | standing | **All timers are session-only.** If the session restarts, recreate 2e87e414, 012fa6dd, 328f7392, 18ff4796, bb224de9. The one-shot liveness timers 5b23a3ed / 54a8f20d / cdd738f1 are past and moot (watcher stopped 07:37Z) but still listed | - | CronList ~09:03Z; `CONTEXT.md` l.2876 |

## LATER (28 Sep 09:10 -> 29 Sep 23:59 UTC, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T59 | **28 Sep 02:00** | Former hard edge for a combo (moot: BASE none). Q6 asked 29 Sep 02:00Z vs 11:00Z | `CONTEXT.md` l.2793; `round16/report.json` R16-A8 (v) |
| T32 / T39 (cont.) | 28 Sep 00:04 ... 21:04 every 3 h; the last useful one 29 Sep 00:04 | E10 P1 checks | `CONTEXT.md` l.2530-2531; `round16/report.json` R16-A7 |
| T46 | **28 Sep 12:00** | F1 consolidation under R8 | `CONTEXT.md` l.1671, l.2708-2709 |
| T28 | 28 Sep | S14: an x138 successor on a late trigger (P7) | `CONTEXT.md` l.1616 |
| T84 (new) | **28 Sep ~18:30Z** | Last exp72 yes at all | `round16/report.json` R16-A8 (iv) |
| T19 / W77 + **W166 (e)** | **28 Sep 17:57** (timer 012fa6dd) | API SELECTED + the first logged page read of the ticks; record N954, N955 and team count as **plain numbers** (no decision mapping, no MC) | CronList; `round16/report.json` R16-A9 (e) |
| T35 | 28 Sep 22:00 | Final admission table = L9 eligibility for every ladder variant + class-C rows (43/44) + exp72 if Q3 = yes | `research/wf_ideas_v3/FINAL_REPORT.md` l.178; `CONTEXT.md` l.2833 |
| T20 | **29 Sep 00:00** | Last slot reset; last useful E10 trigger; E10 v1 ends | `CONTEXT.md` l.2355, l.2708; `round16/report.json` R16-A3 |
| T29 / T47 / T85 (new) | **29 Sep 02:00** | Last E10 port submit and the default last submit (no-answer cap). An 11:00Z answer applies only to an ERROR resubmit and exp72, never to ports | `CONTEXT.md` l.2521-2524; `round16/report.json` R16-A8 (v) |
| T60 (= W135 G2) | **29 Sep 12:00** | G2 must have landed for exp72 to be finals-eligible (Q3 = yes only) | `CONTEXT.md` l.2736 |
| T09 / W77 | **29 Sep 11:57** (328f7392) / **17:57** (18ff4796) | Remind the user to check or re-tick; API SELECTED; plain N954/N955 numbers (W166 (e)). The brief asked the user to set their own alarms (I159) | CronList; `round15/report.json` R15-A2 §6 |
| T86 (new) | **29 Sep ~18:00Z** | Practical expiry of the exp70b letter (W165b) | `round16/report.json` R16-A8 (i) |
| T48 (= W131) | **29 Sep ~19:00** | L9 read (+ the class-C table if the user allowed (b)/(c), + W158 composition). Never two byte-identical files; never a non-COMPLETE file. Tell the user the exact two refs | `CONTEXT.md` l.2510-2518, l.2833-2853 |
| T10 | **29 Sep 20:00** | Ticks final: exactly 2 files; without a re-tick {#37, #38} stays. **Stop the poller** | `CONTEXT.md` l.2515-2516, l.2620 |
| **W148** (= R14-A8) | **before 29 Sep 23:00Z** | Hindsight guard: ONE text-only commit as the user, pushed | `round14/report.json` R14-A8 |
| T49 | **29 Sep 23:00-23:45** (timer bb224de9 at 23:27) | Final public LB snapshot to `experiments/private_read/` | `CONTEXT.md` l.2580-2588; CronList |
| T11 | 29 Sep 23:59 | Competition deadline. A submit must **finish** before it to count (participant comment only) | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 |
| T30 / T50 | **30 Sep from 00:15Z, hourly** | Private read per v2 (d) + L1-L7 + DC-DOSE read + **W166 (d): X = private score of our exact-x138 submission and its private rank** vs the modelled 415-700 | `CONTEXT.md` l.2570-2598, l.2863-2868; `round16/report.json` R16-A9 (d) |
| **W147 + W166** (= R14-A7 + R13-A6 + R12-A10 + R15-A8 + **R16-A9**) | s3 item 11 **before the first private score**; the rest **by 30 Sep** | Curator edits: IDEAS I-106, I-063, I-069, I-297/I-298 (+ **c16 note: the twin #38 matters only in a beta < 0 world**), I-252, "division knobs invisible on public" is WRONG for DC, I-018 DC band; **forkblob ins35 numbers + p* = J/(1+J) replaces "FP:TP >= 7.7"**; post-deadline removal-gate curve | `round15/report.json` R15-A8; `round16/report.json` R16-A9 (a)-(c) |
| W29 | after 29 Sep | Post-deadline list (rounds 10-16, DC sensitivity per embryo, removal-gate curve over J in [0.13, 0.36], amanatar V6) | `round16/report.json` R16-A9 (c), R16-A7 |

**Done, superseded or moot since 06:10Z (for the record):**
- W151 (R15-A1): `CONTEXT.md` l.2814-2871, commit 4161226, pushed 06:19Z before any 43/44 terminal header (`round16/scan_plancheck.notes.md` 08:45Z).
- W152 (R15-A0): `research/wf_ideas_v4/round15/REPORT.md` tracked in 4161226.
- W141 D2 (R15-A4): `CONTEXT.md` l.2872-2876; D2 audit PASS (`round16/scan_plancheck.notes.md`).
- W153 (R15-A3): SELECTED 2/2 [56563534, 56563521] at 07:41:28Z (l.2876-2877).
- W136 (R15-A2): brief sent in chat ~07:45Z (l.2877); push status still open (see OVERDUE).
- W145 / T68 / T70 / T56: watcher STOP 07:37:07Z (l.2876); the liveness checks are moot.
- W140 / T65: quiet window ended 06:45Z.
- W157 -> W161 (R16-A3). T58 (09:00Z exp71 edge) moot (`round16/report.json` rejected, R16AP-4/10).
- W149 E10 P1: 08:31Z not met (`experiments/e10_watch/20260927T0831Z.txt`); continues as W164.
- Earlier records: `_curation/15/watch.json`, `_curation/14/watch.json`.

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I161** (new) | "KEY DIAGNOSTIC: private rank of a file just above X ... overfit median 415 ... mid 524 ... central 602; hard 707 => X's own private rank is modelled at or below the bronze line (~#400) in every field; the 16:54Z premise 'bronze falls inside the x138 block, P(above block) ~ P(medal)' no longer holds once the >= 0.954 public group (358 at 07:37Z) grows to ~520-690" | `round16/scan_hyp_forecast_update.notes.md` | It overturns the reasoning behind keeping #38. It reaches CONTEXT only via R16-A5 (4) and IDEAS only via R16-A9 (a) by 30 Sep; **it should be in front of the user at the 29 Sep ~19:00Z L9 read** (illustrative only, I-092) |
| **I162** (new) | "Runtime: every candidate is COMPLETE ... and the private score is computed in the same scored run, so no option carries a hidden-rerun runtime risk ... The runtime family is irrelevant to the pair choice" | `round16/scan_hyp_forecast_update.notes.md` | Removes a recurring objection to swapping #37 for exp70b or a V*_C; not stated in CONTEXT |
| **I163** (new) | "User 20:33Z words: 'one final aimed at PUBLIC (the best public-scoring variant)'; L9's display >= 0.955 bar is the session's own (20:49Z). exp70b is now provably the best public file (UP)" | `round16/scan_plancheck.notes.md`; `CONTEXT.md` l.2388, l.2407 | The user's literal instruction points at exp70b; our own bar keeps it out. It is only in the unsent R16-A2 point 1. If W160 is not sent, the user decides without this fact |
| **I164** (new) | "pre-reg v3 user refusal (7) l.1582 'no detector/edge/head retraining before 29.09'; brief template does not name R9/refusal (7)" | `round16/scan_plancheck.notes.md`; `CONTEXT.md` l.1582 | exp71 is head-only FT: a yes to Q1 overrides the user's own refusal (7). R16-A1 (5) / R16-A3 name it; the 07:45Z brief did not |
| **I165** (new) | "Reproduction: scratchpad r16rcb/fb_ins35.py ... copy it into experiments/exp60_trainlab/ if it is to survive the session"; forecast scripts `<scratchpad>/r16/forecast_mc*.py` are "session-only" | `round16/report.json` R16-A9 (b); `round16/scan_hyp_forecast_update.notes.md` | The forkblob +0.00019 ins35 measurement and the rank model vanish with the session unless copied (text-only copy, no build) |
| **I166** (new) | "ERROR is terminal at any latency, so the window can close before 12:00Z" | `round16/report.json` R16-A1 (4) | The class-C letter window is an event, not the 12:00Z clock the brief implied |
| **I167** (new) | "exp70a NEU at D1 was structural (B0 = P36 already had lp30): no public evidence on lp30's sign either way"; "P36 > #35 is latency-confounded" | `round16/report.json` new_facts, R16-A5 (5); `round16/scan_recheck.notes.md` | Guards against reading D1 as "lp30 neutral". L1 = exp70a - #37 stays the only clean lp30 contrast on 30 Sep |
| **I168** (new) | "Medal lines (Kaggle 1000+ teams: gold 10+0.2%N, silver 5%, bronze 10%): N_final ~3,990-4,030 -> bronze ~#399-403, silver ~#200, gold ~#18"; "teams >= 0.954 293 -> 358 in 15.3 h (~4.25/h)" | `round16/scan_hyp_forecast_update.notes.md`; `round16/report.json` new_facts | Updates I158 (bronze ~#394). Plain numbers for the W166 (e) tick checks |
| **I169** (new) | mtoshidesu/testbiohub-lf-dctta020-sectta1: "sjlee stack + DC 0.20 + DET 0.965, 0.947 V2; not x138 family ... not pulled" | `round16/scan_browser.notes.md`; https://www.kaggle.com/code/mtoshidesu/testbiohub-lf-dctta020-sectta1 | A DC 0.20 public kernel appeared while our DC 0.20 probe is pending; it is the known I-018 line, notify only. Do not mistake it for an E10 trigger |
| **I170** (new) | "(b) never worse than (a) by > ~0.01" from the MC table was **rejected** ("false: -0.042..+0.050 depending on the DC prior"); r16fc-4 "#38 worth only ~0.01-0.06 P(bronze)" rejected as a bound ("under beta < 0 it is worth up to ~0.1-0.16") | `round16/report.json` rejected | The scan notes still contain the MC tables (`scan_hyp_forecast_update.notes.md`). Never quote them to the user as numbers (I-092) |
| **I171** (new) | "The (b) partner is set to #37 (the literal R15-A1 (4)(b) text, since 42 is not the L9 V*) unless the user names exp70b" | `round16/report.json` R16-A1 why; `CONTEXT.md` l.2842 | Until W158 is logged, (b) has two readings (#37 or exp70b). A letter "(b)" alone must be read as {V*_C, #37} |
| I149 (still at risk; strengthened by I161) | "#38 = X + eps, and eps may be exactly 0 on private ... With eps > 0, #38 hedges an insertion failure; with eps <= 0 it does not" | `CONTEXT.md` l.2846-2851 (now logged) | Now in CONTEXT as REASON text, but the ticked pair still carries #38; weigh at the 29 Sep ~19:00Z read |
| I150 | "E[score] favours a DC-diverse F2 ... But block-step utility P(max > X138): ~0.94 vs ~0.89 => keep #38" | `round15/scan_recheck.notes.md` | The utility choice (expected score vs clearing the block) is still never stated in CONTEXT; I161 changes the block-step premise |
| I151 | Lab "TP cluster sits in [0.30,0.35)"; SHIFT(-0.05) | `round15/scan_hyp_div_sensitivity.notes.md` | Partly in CONTEXT l.2857-2862 (NARROW/BROAD); the lab-cluster fact is not. Post-deadline W29 |
| I153 | Watcher exits after exp70b | `round15/scan_plancheck.notes.md` | **Materialised** 07:37:07Z (`CONTEXT.md` l.2876) |
| I154 | probe.json "rule" boilerplate "above exp56 adopt" in all exp70* | `round15/scan_plancheck.notes.md` | Still unfixed (W126) |
| I155 / I156 / I157 / I160 | Insertion knobs inert; D prior-driven (scale is a MODEL ESTIMATE); safe divisions run before insertion; sjlee DC plateau | `round15/*.notes.md` | I156 and I160 are now in CONTEXT l.2830-2832, l.2852-2856; I155 / I157 are not |
| I158 | LB block positions | `round15/scan_browser.notes.md` | Superseded by I168 |
| I159 | Session-only timers; one-shot liveness timers still listed after their times | CronList ~09:03Z | The 07:30Z push timer was deleted by hand (l.2877), so the firing question is unresolved; the user's own alarms for 29 Sep 12:00Z / 18:00Z remain the backstop |
| I142 | "+0.006 is the exp60 IN-SAMPLE number ... honest ... +0.0019 ... P(<0) 0.10-0.20" | `round14/report.json` new_facts (12) | Still not in CONTEXT (W146 overdue) |
| I143 | FT weights on public stacks "0/4 on the LB"; now "0 of 5" | `round14/report.json` new_facts (13); `round16/report.json` R16-A2 point 5 | The honest prior for Q1-Q3 |
| I136 | FOCUS_NOTE reaches only the plancheck scan; the browser scan runs `e10_snapshot.py` first | `experiments/workflows/biohub-research-round.js` l.35-38 | W150 |
| I144 | amanatar lineage failed P3/P4b; V6 still unscored at 08:40Z ("Best Score 0.953 V4") | `round16/scan_browser.notes.md` | V6 NOTES item 4 is wrong about R8 (W162 (iii)) |
| I145 | "It has to finish before the deadline to count" (participant, no host answer) | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 | Matters for an 11:00Z 29 Sep cap |
| I114 | "x138 cell 1 = configuration guard: BIOHUB_DET_THRESHOLD must equal 0.965 ... else RuntimeError" | `reach0955/v_intel.notes.md` | Not in CONTEXT; matters for any E10 port of a DET-changed fork |
| I116 | Agents label local (UTC+3) times as "Z"; cron hours are local | `reach0955/discussions_2026-09-26.notes.md` | CronList "57 14 29 9" = 29 Sep 11:57Z |
| I72 | The harness asks for a Co-Authored-By trailer; the user's rule forbids it | `memory/feedback-git-no-coauthor.md` | Keep for W158 / W162 / W148 (4161226 and 0bd1408 carry none) |
| I95 | The harness has refused the round-report Write 9 rounds running (8-16) | `round16/report.notes.md` | W159 |
| I130, I131/I132, I110/I111, I148, I96-I106, I88/I89, I69, I77-I83, I47, I51, I39, I44, I01-I76 | Older insights, unchanged | `_curation/15/watch.json`, `_curation/14/watch.json`, `_curation/11/watch.json` | See the W57 family, W98 |

**Resolved since 06:10Z (now in CONTEXT):**
- I152 (E10 not bound by R8): `round16/report.json` R16-A3 / R16-A7 carry it; CONTEXT gets it via W161 (the v6 NOTES fix is W162 (iii)).
- I156 (scale is a MODEL ESTIMATE): `CONTEXT.md` l.2830-2832.
- I160 (sjlee DC plateau): `CONTEXT.md` l.2852-2856.
- I149 REASON text: `CONTEXT.md` l.2846-2851.
- Details: `_curation/15/watch.json`.
