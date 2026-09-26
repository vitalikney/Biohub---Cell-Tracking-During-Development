# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-26 17:40 UTC (curation 11). This is an incremental update of the curation-10 build from 15:51 UTC (`research/KNOWLEDGE/_curation/10/watch.json`).

Sources read for this update:
- `CONTEXT.md` at main HEAD **df6996e** (17:00:28Z; 2,362 lines). Eight entries are new since curation 10 (l.2230-2341). `## 9. Literature` is at l.2342:
  - ROUND 10 RECORD 16:04 (l.2230);
  - E10 PORT RULE P4c 16:04 (l.2257);
  - P1 SNAPSHOTS + post-R8 check times 16:04 (l.2280);
  - PRIVATE-READ PREDICTIONS 16:04 (l.2288);
  - PORT GATE BUILT + P4c(3) wording fix 16:30 (l.2301);
  - USER ANSWER "full rounds" 16:49 (l.2318);
  - PRIVATE RANK FORECAST 16:54 (l.2324);
  - USER OK to the successor-scenario PLAN 17:00 (l.2335).
- `git log`: there are seven commits since 6064d85: 848e07a (16:04Z), a79775f (16:22Z), bea9d99 (16:30Z), 8a3cf31 (16:49Z), 99b127a (16:50Z), a94626a (16:54Z) and df6996e (17:00Z).
- `research/wf_ideas_v4/round11/`, which is **untracked**. The round ran ~17:01-17:31Z. `report.json` has R11-A0..A9, new_facts (1)-(7), plan_issues (1)-(10) and next_focus. `report.notes.md` is there, `REPORT.md` is **not**. `scan_plancheck.json` has PC11-01..14.
- `experiments/e10_watch/`: `20260926T1620Z.txt` is tracked; `20260926T1701Z.txt` and `20260926T1701Z-2.txt` are untracked. Also read: `tools/e10_snapshot.py` l.52 and l.510, and `experiments/workflows/biohub-research-round.js` l.20, l.36-38.
- `experiments/lb_poll/poll.log`: the last header is `=== 2026-09-26T17:26:11Z`, and `tasklist` shows python PID 20052 alive.
- `research/wf_ideas_v4/round9/LESSONS_draft.md` (l.5, l.7, l.41-42), `PROMPT_FRIEND_A.md`, `research/KNOWLEDGE/IDEAS.md`, and `~/.claude/projects/.../memory/MEMORY.md` (disk mtime 13:35Z).

All times are UTC. IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, cancelled, moot.

**State in one line (17:40Z):**
- **Finals are TICKED 2/2** = [56563521 #37 K2 0.954, 56563534 #38 twin 0.953], per the API SELECTED read at **17:09Z** (`round11/report.json` new_facts (2)).
- **E10 is NOT met** at 17:01Z:
  - amanatar v10 ended in **ERROR** with no score.
  - The new anhadmahajan06/biohub-track-your-cells scores 0.946 and fails P4c(2) (`round11/report.json` new_facts (1); `experiments/e10_watch/20260926T1701Z.txt`).
- **The user said "хорошо" (17:00Z) to the successor-scenario PLAN only.** The rule is unchanged (`CONTEXT.md` l.2335-2341).
- Round 11 now proposes **E10 v2 (port-only, threshold 0.954, pair {PORT, #37})**. It needs a **separate OK before 27 Sep 12:00Z**. SI (successor + insertion) is **not** recommended; it is opt-in only, and the user must ask by ~09:00Z 27 Sep (`round11/report.json` R11-A2, R11-A3).
- Public rank is #210, ~13 below silver (info, R7) (`round11/report.json` new_facts (3)).
- Full research rounds continue until **R8 = 27 Sep 12:00Z** (`CONTEXT.md` l.2318-2323).

**Changes since 15:51Z (curation 10):**
- Done:
  - W94: ROUND 10 RECORD, commit 848e07a.
  - W95: P4c.
  - W96: `tools/e10_port_gate.py` with 72 tests.
  - W97 (1)-(2): `tools/e10_snapshot.py`, 19 tests, and the check times.
  - W99: PRIVATE-READ predictions.
  - W100: records in KNOWLEDGE curation 10.
  - W102: now a CONTEXT line.
  - W86 (rounds 8 and 10).
  - Most of W05.
  - W98 (a)-(g).
  - W101 (a) is answered: full rounds.
- Moot:
  - T31: amanatar v10 ended in ERROR.
- New actions: **W103-W112** (from round 11).
- New reminders: **T36-T39**.
- New insights: **I96-I106**.

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| W57 / W66 / W31 / W72 (curator CONTEXT records) | Due 26 Sep 12:00 and **still missed** at 17:38Z:<br>- `CONTEXT.md` l.22 still says "frozen/duplicated frames with GT still moving" (I39).<br>- B5 at l.196 lacks the unadapted-feature blocker (I44).<br>- `grep -c` finds 0 hits for `out_valid` (I47), `efpost` (I51) and `33.1%` (I77).<br>The records live only in `research/KNOWLEDGE` | overdue | 26 Sep 12:00 (passed) | `CONTEXT.md` l.22, l.196; `grep -c` = 0 |
| W71 (residue) | The round prompt `experiments/workflows/biohub-research-round.js` l.40 (the recheck lens) still says "12 h limit with ~4 h headroom". 99b127a edited the prompt and did not fix it | overdue | before round 12 (~19:45Z) | `biohub-research-round.js` l.40 |
| W98 (residue: I69 caveat) | R10-A5 (a)-(g) are applied (`LESSONS_draft.md` l.5 "round-10 fixes R10-A5/A6 applied 26 Sep ~16:05 UTC"; l.41 "#210", "~345"; l.42 "ten"). **l.7 still states "public LB (one embryo, ~29% of the hidden test)" as fact.** No round has asked for the fix | partly done | 27 Sep 12:00Z (lessons due with R8) | `research/wf_ideas_v4/round9/LESSONS_draft.md` l.5, l.7 |
| W03 | **The friend A card is stale.** `PROMPT_FRIEND_A.md` l.1-5 carries the history-rewrite notice, but l.7-9 still say "answer Task 0 first". Add "finals #37 + #38 ticked; nothing to do before 29 Sep" | partly done (last change b41ec05, 10:15Z) | now (not urgent) | `PROMPT_FRIEND_A.md` l.1-9 |
| W02 | Friend A's "Task 0" reply | overdue and moot | 25 Sep 18:00 | `research/wf_ideas_v3/TASK_FRIEND_A.md` l.17-22 |

## NEXT 24 H (26 Sep 17:40 -> 27 Sep 17:40 UTC)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W103 (= R11-A0; W86 successor) | **now, with W104** | Save `round11/report.json` R11-A0 `REPORT_MD_RU` as `research/wf_ideas_v4/round11/REPORT.md`. The harness refused the subagent's Write at 17:27:43Z, the 4th round running (I95) | not started (`ls round11/REPORT.md`: absent) | `round11/report.notes.md` 17:27:43Z; `round11/report.json` R11-A0 |
| W104 (= R11-A1; absorbs the W05 residue) | **now, before round 12 (~19:45-20:15Z)** | **One commit as the user, with no trailer**:<br>(1) Delete `experiments/e10_watch/20260926T1701Z-2.txt` (CHANGES=0 against `20260926T1701Z.txt`).<br>(2) Append the ROUND 11 RECORD above `## 9`: the E10 P1 check at 17:01Z, API 2/2 at 17:09Z, LB intel, the SUCCESSOR FEASIBILITY FACT, the lens ceilings, the precedence clarification **P6 > f2 > R4**, and the slot line **3/5/5/5 (26-29 Sep)**.<br>(3) Before committing: `python -m pytest -q tests` (275) is green; the finals sha are unchanged (1f1ddb6d / a77bcd6b / 55038fd6); `grep -ci claude` = 0.<br>(4) Commit poll.log, ledger.md, `round11/` (with REPORT.md), the one 17:01Z snapshot and CONTEXT, then push | not started (`grep -c "ROUND 11 RECORD" CONTEXT.md` = 0; `git status`: round11/ and both snapshots untracked) | `round11/report.json` R11-A1, plan_issues (2), (6), (7); `round11/scan_plancheck.json` PC11-05, PC11-14 |
| W105 (= R11-A2) | **ask now** (the user is likely awake until ~20:30Z); the OK must be logged with `date -u` **before 27 Sep 12:00Z AND before any trigger** | **E10 v2 PROPOSED** goes into CONTEXT, then the user is asked for ONE yes:<br>(V1) threshold 0.954, read as the successor's own displayed public score on the pulled LATEST version; for ports it supersedes P6's/§f's "+0.002" and f2's "no displacement of the twin";<br>(V2) all of P3/P4/P4b/P4c apply unchanged, plus the full `tools/e10_port_gate.py` run with 0 FAIL and 0 SKIP before the submit;<br>(V3) checks every 3 h from 27 Sep 12:00 to 29 Sep 00:00Z; the last submit stays 29 Sep 02:00;<br>pair {PORT, #37}, so the twin leaves;<br>supersede: at most 2 ports, and the second only at a strictly higher displayed score;<br>precedence: E10 v2 > E10 v1 > f2 > R4.<br>**On an OK:** write the IN FORCE line and a new RESUME POINT.<br>**Without an OK by 27 Sep 12:00:** record "E10 v2 not in force; 0.954-0.955 risk accepted" and keep the 09:03 rule (>= 0.956).<br>This is a pre-trigger rule: it only counts if it is agreed before any such notebook is seen (user, 17:00Z) | not started (`grep -c "E10 v2" CONTEXT.md` = 1, only the 17:00 plan line l.2340) | `round11/report.json` R11-A2, plan_issues (1), (3); `CONTEXT.md` l.2335-2341 |
| W106 (= R11-A3) | tell the user now (inside W112); **opt-in deadline ~09:00Z 27 Sep**; if the user opts in, everything must be committed before 27 Sep 12:00Z | **SI (successor + insertion) is NOT built.** P6's ban stands. If the user explicitly asks for it, the SI_CONDITIONS apply:<br>(a) a builder `--base succ` with the cell-0 tag handled;<br>(b) the K1 recipe only, token **exp67**;<br>(c) a ledger rule `exp67 -> safetail` plus a test;<br>(d) S-specific dummies D0/D1/D2/DFF;<br>(e) scope S >= 0.955 with 0 division lines added.<br>Otherwise SI is closed for this competition | standing (default: not built) | `round11/report.json` R11-A3, rejected (1); `round11/scan_plancheck.json` PC11-07, PC11-08, PC11-09 |
| W107 (= R11-A4) | **now** | **Create the session timers** (CronCreate) and **log each id and time in CONTEXT**:<br>- E10 P1 checks at 27 Sep 12, 15, 18 and 21; 28 Sep 00, 03, 06, 09, 12, 15, 18 and 21; 29 Sep 00:00Z.<br>- Each check runs `tools/e10_snapshot.py`, reads the diff, confirms Chrome is connected and reads API SELECTED.<br>- Tick checks at 28 Sep 18:00 and 29 Sep 12:00 / 18:00.<br>The 3-hourly cadence is read-only and falls within the 09:10 yes even without E10 v2 | not started (`grep -ci "cron\|timer id" CONTEXT.md` = 0) | `round11/report.json` R11-A4; `round11/scan_plancheck.json` PC11-13 |
| W108 (= R11-A5; W101 (b)/(c) residue) | ask now (inside W112); answer before 27 Sep 12:00Z | **Wake-mechanism question.** It was asked at 16:04 and 16:49 and never answered:<br>(a) keep the laptop and this session running until 29 Sep 20:00Z;<br>(b) allow a Windows Task Scheduler job that runs only `tools/e10_snapshot.py` (it changes the user's machine, so it needs an OK);<br>(c) or the user sets their own alarms for 29 Sep 12:00 / 18:00Z.<br>Default: session timers | open (asked twice, no answer) | `CONTEXT.md` l.2285-2287, l.2321-2323; `round11/report.json` R11-A5 |
| W109 (= R11-A6) | **tonight, before 27 Sep 06:00Z** | **E10 port DRY RUN on HF v3** (never submit):<br>- pull `raunakdey07/biohub-harmonic-fusion-v3`;<br>- sanitise the metadata per P4b(a) with id `vitaliineibauer/biohub-exp63-succ-dryrun-raunakdey07`;<br>- list every source (P4b(b));<br>- run the static gate;<br>- push a private dummy with `NEVER_SUBMIT.md`;<br>- fetch the author's output and run the full gate;<br>- log the wall time of each step and the total trigger-to-submit time.<br>Any FAIL is a gate or procedure finding. That time has never been measured (I-262) | not started | `round11/report.json` R11-A6 |
| W110 (= R11-A7) | next curation, **before 27 Sep 12:00Z** | **Curator records:**<br>- I-047 refuted by measurement (-0.0129 / -0.0273).<br>- I-079: orphan-pool filter oracle +0.0054; q* = 0.161 on K2.<br>- DIV header: fork-removal ceiling +0.0063.<br>- I-113: the 6bba misses are peakless, not dim.<br>- New refuted ideas: raw-image orphan maxima (+0.0059) and a division-wave prior.<br>- The I-139 note.<br>- I-122: the Trackastra alias, premise corrected.<br>- The ILP division-weight reason (0.149 < 0.161).<br>- I-026 / I-256: E10 v2 proposed, SI opt-in only.<br>- I-262: dry run planned.<br>- LESSONS s4: two lines | not started (`IDEAS.md` I-047 l.181 still shows only the old reason; the curation-11 IDEAS/FACTS curators may be running in parallel) | `round11/report.json` R11-A7 |
| W111 (= R11-A8; = W23 cadence) | **next P1 check by <= 23:00Z** (round 12 or a timer); **workflow edit before round 12** | **Next E10 P1 check.** Only the browser agent runs the snapshot, and the plan-check agent reads the newest `e10_watch` file (edit `biohub-research-round.js`; today l.37 and l.38 both mention `e10_snapshot`). Watch the overnight burst: submits made ~23:30-02:00Z show up on the LB at ~07-09Z on 27 Sep. An amanatar re-run is a P2 look only | last check 17:01Z, not met; workflow not yet edited | `round11/report.json` R11-A8; `round11/scan_plancheck.json` PC11-14; `experiments/workflows/biohub-research-round.js` l.37-38 |
| W112 (= R11-A9) | **now**, after W104 and W105 are in CONTEXT | **One user message** (Russian text in R11-A9). It covers:<br>- finals 2/2 at 17:09Z; E10 not met;<br>- a correction: SI is **not** stronger than an early port (this reverses the earlier chat claim);<br>- the E10 v2 five-point yes/no;<br>- the SI opt-in deadline (09:00Z);<br>- the three wake questions (W108).<br>Log every reply with `date -u` | not started | `round11/report.json` R11-A9 |
| W102 | **standing, until the private LB is final** | **Protect the finals' inputs:**<br>- never delete or hide `vitaliineibauer/biohub-ft-weights`, or the kernels `biohub-exp58-x138-safe-lowref` / `-exp58n-`;<br>- never remove files from a biohub-ft-weights version.<br>Note I101: the DaughterNet weight load raises outside the fail-soft | CONTEXT line done (ROUND 10 RECORD (6), l.2249-2252); standing | `CONTEXT.md` l.2249-2252; `round11/scan_plancheck.json` PC11-09 |
| W93 | standing, until 29 Sep 23:59 | **Never push or submit exp65 / exp66**, and never merge `worktree-wf_b39793f6-e79-*` | standing (`NEVER_PUSH.md` in both) | `CONTEXT.md` l.2223-2226 |
| W19 / W73 | until **29 Sep 20:00** | Keep ONE poller (PID 20052). Before any submit, the last `poll.log` header must be < 15 min old. Lid-close and power loss are still not covered (W108 (a)) | in progress (last header 17:26:11Z) | `experiments/lb_poll/poll.log`; `round11/report.json` new_facts (7) |
| W76 | round 12 **~19:45-20:15Z**, then ~22:30, 27 Sep ~01:00, ~03:30, ~06:00, ~08:30 and ~11:00; **ends 27 Sep 12:00** | **Full research rounds**, with new hypotheses (user, 16:49Z). The round-12 focus:<br>(1) verify that R11-A0..A8 landed;<br>(2) log the user's answers (E10 v2, SI, wake);<br>(3) E10 P1 check by the browser agent;<br>(4) read the dry-run result;<br>(5) lenses: red-team the E10 v2 night procedure, private-read calibration, post-deadline agenda.<br>**Do NOT re-run the detection, graph, outside or successor lenses** (saturated by their ceilings) | round 11 done (untracked); round 12 not started | `CONTEXT.md` l.2318-2323; `round11/report.json` next_focus |
| T12 | **26 Sep 18:00** | The M6 reopen window for K4/tempfuse lapses. Log the lapse in the W104 record | pending (expected lapse) | `CONTEXT.md` l.1949 (M6) |
| T26 | info | Public #210 at 17:01Z, 12th of 97 in the 0.954 block, ~13 below silver (196.6). The 0.953 block holds 354 teams (#296-649). Not a trigger (R7) | - | `round11/report.json` new_facts (3) |
| T17 | 26 Sep, until 23:59 | The 3 unused 26 Sep slots stay EMPTY (E10 only) | - | `CONTEXT.md` l.2209 |
| T27 | ~26 Sep 22:00 | From here on no round can yield a final, even in principle | - | `round10/scan_hypotheses.json` r10h-10 |
| T36 (= W111) | **by 23:00** | Next E10 P1 check (W111) | not started | `round11/report.json` R11-A8 |
| T18 | **27 Sep 00:00** | Slot reset: 5 slots for 27 Sep (S8 = E10 port only, by trigger). 27-29 Sep: 5 / 5 / 5 | - | `CONTEXT.md` l.2209; `round11/report.json` plan_issues (6) |
| T37 (= W109) | **27 Sep 06:00** | Deadline for the HF v3 dry run | not started | `round11/report.json` R11-A6 |
| T02 | 27 Sep ~07:00-09:00 | LB snapshot (info only); the overnight burst lands now. Compare with #210 at 17:01Z | - | `round11/report.json` R11-A8 |
| T38 (= W106) | **27 Sep ~09:00** | Last moment for a user SI opt-in. Without one, SI is closed | - | `round11/report.json` R11-A3 |
| T03 | **27 Sep 12:00** | **R8.** No new mechanism after this, and the full rounds end. Also due at R8:<br>- the **E10 v2 OK deadline** (W105);<br>- the wake answer (W108);<br>- lessons (W98);<br>- curator records (W110).<br>An E10 port of a PUBLIC successor stays possible (S8/S14) | - | `CONTEXT.md` l.1671-1672, l.2318-2323 |
| T32 / T39 (= R10-A4, R11-A4) | **27 Sep 12:00, 15:00, 18:00, 21:00** (then LATER) | The first post-R8 E10 P1 checks. They are 3-hourly per R11-A4; `CONTEXT.md` l.2284-2285 still lists the ~6 h times. **The timers must exist first (W107).** Confirm at each check that Claude in Chrome is connected | not started | `CONTEXT.md` l.2280-2287; `round11/report.json` R11-A4 |

## LATER (27 Sep 17:40 -> 29 Sep 23:59 UTC, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T32 / T39 (cont.) | 28 Sep 00, 03, 06, 09, 12, 15, 18 and 21; **29 Sep 00:00** (the last) | Post-R8 E10 P1 checks, each with an e10_watch snapshot. The recorded minimum is 28 Sep 00/06/12/18 | `CONTEXT.md` l.2284-2285; `round11/report.json` R11-A4 |
| T04 / T05 | 28 Sep 12:00 / 16:00 | S12 consolidation / S13. **Empty by rule** | `CONTEXT.md` l.2209; `research/wf_ideas_v3/FINAL_REPORT.md` l.177-178 |
| T28 | 28 Sep | S14: an x138 successor on a late trigger (P7) | `CONTEXT.md` l.1616, l.2209 |
| T19 / W77 | **28 Sep 18:00** (timer per R11-A4; "28 Sep evening" in CONTEXT) | Re-run API SELECTED (it must print `[56563521, 56563534]`, or the E10 pair) and do the FIRST page read of the ticks, which has never been logged | `CONTEXT.md` l.2206, l.2285; `round11/report.json` R11-A4 |
| T35 (plan §d) | **28 Sep 22:00** | The plan's "final admission table in CONTEXT" (`FINAL_REPORT.md` l.178). `grep -ci admission CONTEXT.md` = 0. It is a formality now: one line restating the finals, the tick state and any E10 result | `research/wf_ideas_v3/FINAL_REPORT.md` l.178 |
| T20 | **29 Sep 00:00** | The last slot reset and the **last useful E10 trigger**. Under the strict default (notify and wait), a trigger at 00:00 waits for the user and misses 02:00 (I103) | `CONTEXT.md` l.2139, l.2284-2285; `round11/scan_plancheck.json` PC11-10 |
| T29 | **29 Sep 02:00** | The last E10 (v1 or v2) port submit. R11S-6's "10:00" was rejected (it breaks R8/P7) | `CONTEXT.md` l.1671-1672; `round11/report.json` plan_issues (4) |
| T09 / W77 | 29 Sep **12:00** (backup **18:00**) | API SELECTED plus a page check. Remind the user to CHECK the ticks. The user's own alarms depend on W108 (c) | `CONTEXT.md` l.2206, l.2285; `FINAL_REPORT.md` l.180 |
| T10 | **29 Sep 20:00** | The ticks become final: exactly 2 files. The default is {#37 56563521, #38 56563534}. With an E10 port (v1, or v2 if OK'd), the pair is {port, #37} and the user must re-tick. Never tick #34, #35, P36, or two identical files. **Stop the poller** | `CONTEXT.md` l.2206, l.2209; `round11/report.json` R11-A2 |
| T11 | 29 Sep 23:59 | Competition deadline. W99 is already committed (848e07a), so the "before" proof holds | `CONTEXT.md` l.2288; `git log` 848e07a |
| T30 | **30 Sep** (private LB) | Read C1-C4 from the displayed private scores (`CONTEXT.md` l.2288-2300), fill LESSONS s5, and append to CONTEXT §11. Also check the 16:54 forecast (P(bronze) ~0.65-0.7, central rank ~320) as calibration | `CONTEXT.md` l.2288-2300, l.2324-2334 |
| W102 (cont.) | until the private LB is final | Keep the finals' inputs intact | `CONTEXT.md` l.2249-2252 |
| W29 | after 29 Sep | Post-deadline list: 8 items (R10-A5 (g)), plus the round-11 additions (next_focus (5c)): I-113 (with the 6bba miss facts), I-079, I-122 (the Trackastra ctc model), I-242, I-285, with gates fixed now. The bar is lab >= 6x the target public gain. Also E14 | `round10/report.json` R10-A5 (g); `round11/report.json` R11-A7, next_focus (5) |

**Done, cancelled or moot since 15:51Z (for the record):**
- W94 is done in **848e07a** (16:04Z):
  - the ROUND 10 RECORD is at l.2230-2256, with (4) the x138 slug, (6) FINALS INPUTS PROTECTION and (7) ops;
  - `round8/REPORT.md` and `round10/REPORT.md` are tracked;
  - one v10 copy was kept, and the duplicate folder and `bash.exe.stackdump` were deleted (both absent on disk).
- W95 is done: P4c is at l.2257-2279.
- W96 is done in **bea9d99**: `tools/e10_port_gate.py` plus 72 tests. x138 + exp56 PASS, amanatar v10 FAIL, and pytest shows 275 passed (l.2301-2317).
- W97 (1)-(2) are done in **a79775f**: `tools/e10_snapshot.py` (19 tests), the `20260926T1620Z.txt` baseline and the check times (l.2280-2287). (3), the optional watcher, is now W108 (b).
- W99 is done: PRIVATE-READ PREDICTIONS are at l.2288-2300 and are copied into LESSONS s5.
- W100 is done: curation 10 put the records in KNOWLEDGE. `IDEAS.md` l.16-18 covers I-146, I-097/I-107 and I-209, and FACTS has the x138 slug; CONTEXT has the slug at l.2241-2244.
- W101 is sent. (a) was answered at 16:49Z (full rounds, `CONTEXT.md` l.2318). (b) and (c) moved to W108.
- W102 is done as a CONTEXT line.
- W86: rounds 8 and 10 are done. Round 11 is W103.
- W05: the only residue is W104.
- W23: a P1 check ran at 17:01Z and continues as W111.
- T31 is moot: amanatar v10 ended in ERROR with no score (`round11/report.json` new_facts (1)).
- Earlier records: `_curation/10/watch.json`, `_curation/9/watch.json`, `_curation/8/watch.json`.

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| I96 | **Detection gap for E10 v2:** `tools/e10_snapshot.py` flags P2 only at `P2_MIN = Decimal("0.956")` (l.52), and that P2 look-check counts LB TEAMS moving up (l.510), not notebook scores. R11-A2 says "No tool change is needed ... e10_snapshot.py P2_MIN stays 0.956". Round 11 also rejected lowering it: it "would fire on routine x138-variant entrants". P4c(7) adds: "the kernel API has no score field, so P3's score read needs the browser" | `tools/e10_snapshot.py` l.52, l.510; `round11/report.json` R11-A2, rejected; `CONTEXT.md` l.2278-2279 | Under E10 v2, a 0.954-0.955 successor raises **no automatic flag**. It is caught only if someone opens the page of each new dateRun/scoreDescending kernel in the browser. The R11-A4 timer steps ("snapshot, diff read, Chrome check, API SELECTED") do **not** include a page-score read of new kernels. Add that step to W107 and the W105 procedure, or the night checks can miss exactly the case E10 v2 exists for |
| I97 | "The 0.953 block's median SubmissionCount is 25 (active teams, not one-shot copiers)" | `round11/report.json` new_facts (5) | This weakens the model's picture of "exact x138 copies share one private score X". Many 0.953 teams have submitted 25 times and may not tick a verbatim x138 as a final. It bears on the 16:54 forecast (`CONTEXT.md` l.2324-2334) and on the C1-C4 / rank reading on 30 Sep (I92) |
| I98 | "11th window of late exact x138 copies (10 teams at #625-635, subs 08:41-10:02Z) again at the END of the 0.953 block -> exact ties ordered by submit time". The crowd model's port advantage "assumes exact full-precision ties ordered by submit time; the LB CSV shows 3 decimals only" | `round11/report.json` new_facts (3), plan_issues (9) | This is the whole basis for "port early" under E10 v2. It is inferred from rank order, not stated by Kaggle. I54/I46 are the sibling insights |
| I99 | "The builder's cell-0 header embeds '--base {a.base}', so a 'succ' build of exp56 cannot be byte-identical to exp58 without handling that line"; "write_test_submission normalised sha12: x138 = HF v3 = 56a7f948b762, amanatar old = v10 = c6114b2c75d4" | `round11/report.json` new_facts (4); R11-A3 (a) | This only matters if SI is opted in (W106). The naive byte test fails, and amanatar-family bases are EXPECTED REFUSED |
| I100 | "HF v3 = x138 with comments stripped (a clone, not evidence about transplant robustness)" | `round11/report.json` new_facts (4), R11-A6 | The dry run (W109) tests the port procedure only, never the SI transplant. A PASS there must not be read as "SI works on successors" |
| I101 | "The DaughterNet weight load raises at cell level, outside the fail-soft, so an S with a different docker image or datasets is caught only by a dummy" (DIVINS_GLUE in `tools/build_probe_kernel.py`) | `round11/scan_plancheck.json` PC11-09; `round11/report.json` plan_issues (8) | This also applies to **#37 itself**: if `biohub-ft-weights` becomes unreadable at a rerun or rescore, #37 errors instead of degrading. That strengthens W102 / I91 |
| I102 | "Overnight burst: submits ~23:30-02:00 UTC appear on the LB ~07-09 UTC 27 Sep" | `round11/report.json` R11-A8 | A night check can only see notebooks, not LB movers. LB signals from the night show up at ~07-09Z (T02) |
| I103 | "Under the strict default ('notify and wait'), a trigger at the 29 Sep 00:00Z check waits for the user (~06:00Z) and misses 02:00. Build plus 4 dummies takes ~1.5 h, so the 00:00Z check barely fits" | `round11/scan_plancheck.json` PC11-10 | The last two post-R8 checks (28 Sep 21:00, 29 Sep 00:00) are useful only with night autonomy (P8) and a connected Chrome (P4c(7)). The user should know this when answering W105/W108 |
| I104 | "P(a clean actionable successor >= 0.954 by 29 Sep 00:00) ~5-15%; nothing above 0.953 has appeared publicly in 5 days; recent near-top public notebooks (amanatar, anhadmahajan06) fail P4c" | `round11/report.json` plan_issues (10) | This is the honest scale for W105. The quoted bronze gains (+0.02..+0.26) are model priors, not measurements |
| I105 | "metric: node-drop bonus ~4.5e-6 vs expected cost ~9.5e-5 per node"; "metric has no unexploited lever for x138 (node bonus pays only at P(annotated) < ~0.2%)" | `round11/report.json` new_facts (6), R11-A7 | This closes the node-count-bonus question (`memory/project-metric-insights.md`) numerically. It goes to LESSONS s4 (W110) |
| I106 | "6bba misses mostly not dim (72% vs 87% above threshold) but peakless (31% vs 70% local max within 5 um) ... crowding/merge suspected -> test separability before nnPU"; "Trackastra ships a pretrained 2D+3D 'ctc' model" | `round11/report.json` new_facts (6), R11-A7; https://raw.githubusercontent.com/weigertlab/trackastra/main/trackastra/model/pretrained.json | These redirect two post-deadline items (I-113 nnPU, I-122 Trackastra) before anyone restarts them on the old premise |
| I85 | "x138's slug changed ... live slug is anvithpothula/biohub-0-953-lb-original ... the old slug 404 must not be read as 'x138 deleted'" | `CONTEXT.md` l.2241-2244 (now recorded) | It is recorded now. Keep it for the night timers, which must use the new slug (`tools/e10_snapshot.py`) |
| I86 / I87 | The validator defaults ON when the line is missing; the first-hit grep would wrongly pass amanatar's deadline override; `validate_csv` overwrites duplicate rows silently | `CONTEXT.md` l.2264-2272, l.2301-2317 | Both are **resolved** in P4c(3) and the gate; kept as pointers |
| I88 | x138 and both finals carry a dormant ADAPTIVE_SHORT_TRACK_RESCUE that fires only when MIN_TRACK_LEN removes >= 10% of a clip's nodes (0/56 lab clips) | `research/KNOWLEDGE/IDEAS.md` l.293; `round10/report.json` R10-A7 (1) | Recorded in KNOWLEDGE, **not in CONTEXT** (`grep` = 0). This hidden-embryo switch is shared by both finals and may fire on private embryos; a candidate note for the 30 Sep read |
| I89 | A primary swap under x138 fails SILENTLY (bounded() caps shifts at 2 um) | `research/KNOWLEDGE/IDEAS.md` l.235, l.245 | In KNOWLEDGE only; post-deadline detector work needs a head retrain |
| I90 | "A bare `pytest` at the repo root errors on ... test_adversarial.py; not a regression. Test command = `python -m pytest -q tests`" | `CONTEXT.md` l.2245-2248 (ROUND 10 RECORD (5)) | Recorded now. The count to expect is **275** since bea9d99 |
| I92 | "One embryo split can only fail to contradict the ~1/6 rule ... No rank-vs-0.953-block reading" | `CONTEXT.md` l.2288-2300 | Recorded now. It conflicts in spirit with the 16:54 rank forecast (l.2324-2334), which models the block as copies sharing X. Label the forecast "calibration only" on 30 Sep (see I97) |
| I93 | amanatar v10's five default-OFF sweep-gated levers: a >= 0.956 score would be public evidence that sweep-selected levers help | `experiments/ext_optimized-biohub-max-score/v10_2026-09-26/NOTES.md` items 1-4 | **Moot for now**: v10 ended in ERROR (`round11/report.json` new_facts (1)). Re-open only if amanatar re-runs and scores |
| I94 | Windows Update NoAutoReboot=1, no pending reboot; the remaining risks are lid-close and power loss | `round10/scan_plancheck.json` PC10-06 | Now tied to W108 (a) |
| I95 | **The harness has refused the round-report Write four rounds running** (8, 9, 10, 11 at 17:27:43Z) | `round11/report.notes.md` 17:27:43Z | Structural. Each REPORT.md exists only if the main session extracts it (W103). The workflow (99b127a) still has the subagent write it |
| I69 | **"R8H-1 rests on the assumption that 'public = one embryo'. That is a participants' guess, not a host fact."** Still no host answer | `round8/v_hypotheses_r8h-1.json`; `research/discussions_summary.md` l.4-6; `round9/LESSONS_draft.md` l.7 | l.7 of the lessons still states it as fact, and the round-11 crowd model and the 16:54 forecast lean on it too. W98 residue |
| I82 | The MEMORY index **injected into this curator's system context** (curation 11, 17:34Z) still reads "finals #37 + #38 decided 26 Sep; no standing submit OK except items the user OKs later (E10 port rule proposed; overlap-consensus line paused)". The disk copy (mtime 13:35Z) says "ticked ... only the E10 port rule ... is pre-approved" | `~/.claude/projects/.../memory/MEMORY.md` l.8 (disk) vs this curator's context | Workflow subagents still see a stale approval line. If E10 v2 is OK'd (W105), MEMORY l.8 must change too (threshold 0.954, pair {PORT, #37}) |
| I72 | "The harness reminder asks for a Co-Authored-By trailer, which conflicts with the user's standing rule; the user's rule wins" | `round8/scan_plancheck.json` PC8-08; `memory/feedback-git-no-coauthor.md` | Still live in curation 11: the harness again asks for a "Claude Opus 5.5" trailer. W104 must pass `grep -ci claude` = 0 |
| I76 | "The insertion moved public by ~1/6 of its lab size, so R4's +0.002 needs ~+0.012 in the lab" | `round9/LESSONS_draft.md` l.3; `CONTEXT.md` l.2321 | Now partly in CONTEXT (l.2321, "~+0.012 lab by the ~1/6 transfer rule") |
| I77 | "x138, #37 and #38 switch per frame between an 80%-secondary blend and primary-only ... 44b6 33.1% of frames ... 6bba 3.9%" | `round9/report.json` R9-A6 (3) | `grep -c 33.1% CONTEXT.md` = 0. A public/private shake-up source for BOTH finals (W57 family) |
| I78 | "31/83 FN with no fork within +-4 frames; 46/83 with the nearest fork >= 12 um away ... 15/25 FP with no GT divider" | `round9/report.json` R9-A6 (1) | Division work, post-deadline |
| I79 | exp64 post-stop: "a delta that vanishes without the node multiplier comes from deleted nodes, not from fixed edges" | `experiments/exp64_overlap_lab/results_info_post_stop.md` | Backs "a new splice design" (post-deadline item 7) |
| I83 | "DeepCenter was trained on 44b6 ONLY" (exp64 is not out-of-sample) | `round9/scan_hypotheses.json` r9h-3 | The DeepCenter reason is not in CONTEXT |
| I64 / I66 / I67 | equal_fracs 1.0 pairs; z-shift plateau +0.0015..+0.0018; "99 GT divisions = steal 35 + orphan 27 + ..." | `round8/v_hypotheses_r8h-9.json`; `round8/v_recheck_r8-rc-a-*.json`; `round8/v_recheck_r8-rc-c-*.json` | Post-deadline items 3, 6 and 7 |
| I73 / I68 / I71 | Bit-probe lesson; FP:TP break-even 1/J (J 0.36 is the exp29 base); MAX_S could make K6 == K2 | `round8/*.json` | §11 lessons and any OC rerun |
| I47 / I51 / I39 / I44 | Official edge-FP rule (out-degree/in-degree); efpost 6bba +0.00174; CONTEXT l.22 is wrong about frozen frames; unadapted 224-d features | `round6/report.json`; `round5/report.json` | Still not in CONTEXT (W57 family) |
| I53 / I52 / I54 / I46 / I34 | Gains came from detection, not the linker tail; stitch CLOSED; late copies at the block end (now 11 windows, I98); 44b6 "+0.0157" is one TP | `round6/report.json`; `round4/report.json`; `CONTEXT.md` l.1932 | §11 lessons |
| I01-I09, I14, I15-I29 | Older lens and round insights (fork blobs, 1-of-10 transfer, leak siblings, kernel time is not a budget signal, the stale branch name in the friend cards, the public read over-rewards fork removals, q* 0.114 -> **0.161 on K2** (round 11), DeepCenter t* not node-preserving, FN anatomy) | `research/wf_ideas_v4/lens_*.json`; `FINAL_REPORT.md` §g/§j; `round2`-`round3/report.json`; `experiments/exp60_trainlab/results.md` l.13-18 | Post-deadline and lessons; unchanged since curation 10 |

**Resolved since 15:51Z:**
- I74 / I75 / I80 / I81 / I84 / I65: already resolved in curation 10.
- I86 and I87 are resolved by P4c(3), P4c(5) and `tools/e10_port_gate.py` (`CONTEXT.md` l.2266-2317).
- I85, I90 and I92 are recorded in CONTEXT (l.2241-2244, l.2245-2248, l.2288-2300).
- I93 is moot (v10 ERROR).
- I81 continues as W107/W108.
- Earlier resolutions: `_curation/10/watch.json`, `_curation/9/watch.json`.
