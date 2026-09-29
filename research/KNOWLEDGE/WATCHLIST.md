# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-29 ~14:50 UTC (17:50 MSK), curation 41. This updates the curation-40 build of ~13:50Z, which is committed in 2fcbedd with a structured copy in `research/KNOWLEDGE/_curation/40/watch.json`. Older predecessors run from `_curation/39/watch.json` down to `_curation/18/watch.json`. Rows not repeated here are unchanged there.

**Sources read for this update:**
- **`CONTEXT.md`:** 4,663 lines; `## 9. Literature` starts at l.4643. One new entry since curation 40:
  - l.4618-4642 (13:58Z): **ROUND 40 APPLIED**. It covers:
    - (A1) RESERVE-SLOT EDGES;
    - (A3) `mk_card_1837.py` installed and patched for B, sha8 **59c54168**, with the new code T3KEEP;
    - (A4) the MESSAGE SET with T3KEEP;
    - (A6) the round prompt refresh;
    - (A5) the feed stop at ~17:29Z;
    - the LB at #148.
  - **Nothing is logged after 13:58Z** (checked 14:46Z).
- **`git log`:** **2fcbedd** (13:59Z) commits round 40, curation 40 and the prompt refresh. **`git status`:**
  - `M` feed_loop.log, state.json, ledger.md, poll.log;
  - `?? experiments/discussions/744357.md` and `digest_20260929T1428Z.md`;
  - `?? experiments/lb_poll/_lb/e10_20260929T1141Z/`: **still untracked**;
  - `?? _night_subs.*`;
  - `?? research/wf_ideas_v4/round41/`.
- **`research/wf_ideas_v4/round41/report.json`** (written 14:42:57Z, untracked, **not yet applied**) has **R41-A1..A8**, new_facts (1)-(8), plan_issues (1)-(8) and rejected. There is no REPORT.md. The `report.notes.md` l.6-45 holds the R41-A3 patch program between the `<<<PATCHR41` and `PATCHR41>>>` markers.
- **Round 41 scans:** `scan_plancheck.notes.md`, `scan_hyp_evedry41.notes.md` (the evening dry run), `scan_recheck.notes.md` and `scan_browser.notes.md`.
- **`experiments/lb_poll/poll.log`:** newest header **14:39:33Z** (l.31857). exp89t 56669888 is **PENDING**. `ledger.md` (14:39:35Z) gives L > 5.65 h.
- **`experiments/discussions/feed_loop.log`:** last run **14:29:04Z**. It found 1 new topic, 744357 "Farewell and Thanks" (no content), and E10 FLAG none. The digest is `digest_20260929T1428Z.md`.
- **Round prompt `experiments/workflows/biohub-research-round.js`:**
  - l.20 KEY FACTS was refreshed (R40-A6): #148, П3, decision B, the EVENING CHAIN;
  - PLAN CHECK was refreshed;
  - "currently ticked" no longer appears (grep count 0).
- **`experiments/RESULTS.md`:** 163 lines; probe rows still end at probe 46 (l.79).
- **Process census, ~14:45Z (this curation, `ps -W`, read-only, 0 Kaggle calls).**
  - Alive:
    - **`pre_exp89t.sh` w36816 / cyg 12542: STILL ALIVE**;
    - manual_admit w3028, t7 w29648, the watcher w30864, the watchdog w22236;
    - the poller w37016;
    - the feed loop w20892 (sleeping since 14:29:04Z);
    - **the feed stop job w32220**;
    - the FEED SIGNAL waiter **w24700 / w11836** (re-armed 14:30:11Z);
    - timers 18:37Z w33156, 19:43Z w30648, 21:05Z w31720 and 00:07Z w19388.
  - Gone: the e10 waiter w20284 and the old feed waiter w24352.
  - Scratchpad `mk_card_1837.py` sha256 starts **59c54168** (the R41-A3 patch is **not** applied).

All times are UTC. The user thinks in MSK = UTC+3 (`CONTEXT.md` l.3683-3687). IDs are stable: W = action, T = time-bound reminder, I = insight, C = contradiction. Status values: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at ~14:50Z, 29 Sep:**
- **Best display 0.959**, exp87a 56640366 = V_pub.
- **SELECTED = П3 {exp87a 56640366, #37 56563521}** (API 12:37:31Z, `CONTEXT.md` l.4579-4581, l.4617).
- **Decision B:** exp89t promotes only at **>= 0.960** (l.4607-4617).
- **exp89t 56669888 is PENDING** (T0 09:00:17Z). Edges:
  - typical read 18:17-18:29Z (21:17-21:29 MSK);
  - UNPROVEN-ins after 19:12:17Z;
  - admit edge 19:45:17Z (22:45 MSK).
- **Slot 2:** reserve effectively closed. The default dummy-start edge was 14:10Z and has passed. The absolute last is 16:50Z (`CONTEXT.md` l.4619-4627). It expires unused by default.
- **Rank:** **#151 of 3,999, 18th of 23** in the 0.959 block; 133 teams above 0.959 (Chrome 14:19Z, `round41/report.json` new_facts (1)).

**Changes since ~13:50Z (curation 40):**
- **Done:**
  - W364 (1): reserve-slot edges logged at l.4619-4627;
  - W366: builder installed and B-patched at l.4627-4633;
  - W367: MESSAGE SET logged at l.4633-4639;
  - W369: prompt refresh at l.4640 (verified in `biohub-research-round.js` l.20);
  - **W374** (round 40 committed in 2fcbedd). Its S0 CSV part moves to W381;
  - **C18** (the T3KEEP patch) and **C19** (the "currently ticked" line is gone): resolved.
- **Still open:**
  - **W373 / C17:** pre_exp89t is still alive. It becomes **R41-A1**;
  - W364 (2): the user info line is not evidenced in CONTEXT.
- **New:**
  - actions **W375-W381** (= R41-A2..A8);
  - reminders **T234-T236**;
  - contradictions **C21-C23**;
  - insights **I450-I461**.

---

## OVERDUE / DUE NOW

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W373** + **C17** (**= R41-A1**) | **Kill `pre_exp89t.sh`: win 36816 / cyg 12542.** Use `Stop-Process -Id 36816 -Force`. Verify with `Get-Process -Id 36816` (must return nothing) and `Get-Process -Id 3028` (must still be alive). **Do not verify with a Win32_Process CommandLine -match** filter, because it matches the checking process itself. Leave manual_admit w3028 (started in the same second), t7 w29648, the watcher w30864, the poller w37016, the watchdog w22236 and the feed stop job w32220 alone. Add the one CONTEXT OPS line in the R41-A1 wording | **overdue.** Flagged at 13:44Z (curation 40) and 14:15Z / 14:32Z (round 41); **still alive at 14:45Z** | **now; hard edge 17:40:00Z** (20:40 MSK). Otherwise it makes 1-2 LB downloads in the quiet window and creates `_lb/pre_exp89t`, the builder's default `--lb` | `round41/report.json` R41-A1; `CONTEXT.md` l.4614; `round41/scan_hyp_evedry41.notes.md` "!! pre_exp89t.sh STILL RUNNING" |
| **W380** (new; = **R41-A6**) | **Round-prompt KEY FACTS refresh 2** (`biohub-research-round.js` l.20): <br>- rank "#151 of 3 999, 18th of 23 (Chrome 14:19Z); 133 teams above 0.959"; <br>- date the OPS times as 28 Sep events, plus "on battery 29 Sep 05:27-06:01Z and from 08:50Z; on AC at 14:28Z / 14:35Z"; <br>- the 0.963 cluster = 7 teams; <br>- pre_exp89t killed; <br>- builder sha8 a19e1bd6; <br>- T7 / manual-admit = R41-A2; <br>- feed "runs left ~15:59Z, ~17:29Z (last)". <br>Also remove "S0 tags pre_exp89t (17:40Z)" from l.20 and "pre_exp89t" from the l.37 allowed-callers list (C22) | not started (l.20 still says "#148 ... 17th of 22" and "S0 tags pre_exp89t (17:40Z)"; verified 14:46Z) | **before the 15:13Z round** (18:13 MSK) | `round41/report.json` R41-A6, plan_issues (6) |
| W364 (2) | One info line to the user: the reserve slot is effectively closed and П3 stays. The text is in R40-A1 (2) | not evidenced (no CONTEXT line); low value now that П3 is ticked | only if useful; before 16:50Z | `round40/report.json` R40-A1; `CONTEXT.md` l.4619-4627 |
| W126 (part 2) | Add RESULTS.md rows for probes 47-54: <br>- 47: 0.955; 48: 0.957; 49: 0.955; 50: exp85a 0.958; <br>- 51: exp87a 0.959; 52: exp89r 0.957; 53: exp75 0.955; 54: exp89p 0.956. <br>Then probe 55 (exp89t) when it reads | **overdue** (rows end at 46, l.79) | low; post-deadline OK | `experiments/RESULTS.md` l.79; `poll.log` l.31857-31870 |
| W336 | One line saying that the user's 08:27Z / 08:28Z instructions override R8's 10:00Z edge (l.1671) | not started; moot in practice | low | `CONTEXT.md` l.1671 |
| W286 / W297 / W202 + W244 / W176 / W177 / W182 / I208 / W57 / W66 / W31 / W72 / W150 / W308 | Older text and cleanup items | overdue, low | H2 29 Sep 23:00Z; post-deadline OK | `_curation/36/watch.json`, `_curation/26/watch.json` |

## CONTRADICTIONS TO RESOLVE BEFORE THEY FIRE

| ID | Conflict | Which text wins | Evidence |
|---|---|---|---|
| **C21** (new) | **Decision B has not reached T7 or manual-admit.** <br>- The T7 texts (case a П3 and case b П2) in `round40/scan_hyp_exp89tmsg40.json` and R38-A5 (6) still say "≥ 0.960 или 0.959 с UP". <br>- `manual_admit_COMPLETE` still maps to "T2 / T3 (UNPROVEN-ins) / T4_question / T5_late". <br>- CONTEXT R39-A3 (l.4563-4564) points T7 at R38-A5 (6). <br>T7 fires ~19:20Z, about 40 min before the tick, and would promise a promotion at 0.959 | **Decision B** (`CONTEXT.md` l.4607-4617). Log the R41-A2 texts (**W375**): <br>- manual-admit: ≥ 0.960 → T2; 0.959 → T3KEEP "(после 22:12 МСК)"; ≤ 0.958 → T5_late; <br>- T3_interim / T3_promotion / T4_* are never sent | `round41/report.json` R41-A2, plan_issues (2); `round41/scan_hyp_evedry41.notes.md` "Decision B leak" |
| **C23** (new; the residue of C18) | The installed builder (sha8 59c54168) still has **`PROMO = {"T1","T2","T3"}`** and the default **`--lb pre_exp89t`**. It has no code / display / edge guard. It builds a promotion card for "T1 --disp 0.959", for the obsolete "T3", and for T2 after 19:45:17Z | **Decision B + the logged admit edge.** Apply the R41-A3 patch (**W377**) → sha8 a19e1bd6. If the patch is not applied, use the manual rule: T1/T2 only at ≥ 0.960, T3KEEP at 0.959, T5 at ≤ 0.958, never T3/T4/UPWAIT, and always pass `--lb` explicitly | `round41/scan_plancheck.notes.md` l.3-4; `round40/scan_hyp_exp89tmsg40.notes.md` l.26; scratchpad sha verified 14:45Z |
| **C22** (new) | Round prompt `biohub-research-round.js`: <br>- l.37 says "after 12:00Z do NOT run tools/e10_snapshot.py and make 0 Kaggle CLI/API calls", then in the same paragraph "If the browser tools are unavailable, use the Kaggle CLI only ... FIRST run `python tools/e10_snapshot.py`"; <br>- l.37 also lists "pre_exp89t" among the allowed 17:30-20:00Z callers; <br>- l.20 says "S0 tags pre_exp89t (17:40Z)" | **R39-A6 (0 Kaggle calls after 12:00Z; Chrome only) and decision B** (pre_exp89t cancelled). Fix with W380. If Chrome fails in a round, the browser scan should report "unavailable" and make no CLI call | `biohub-research-round.js` l.20, l.37; `CONTEXT.md` l.4614 |
| C17 (open) | CONTEXT l.4614 says the job was "CANCELLED", but w36816 is still alive at 14:45Z | **CONTEXT.** Fix with W373 | census 14:45Z |
| C15 | The 18:37Z / 19:43Z / 21:05Z timer texts push "if not the recommended pair" | **The R39-A4 comparator.** Today no push, because SELECTED = П3. Push only after exp89t ≥ 0.960 | `CONTEXT.md` l.4565-4568 |
| C11 | mid_<token> scope | **CONTEXT 11:54Z** | `_curation/40/watch.json` |
| C18 / C19 / C20 / C14 / C16 | - | **Resolved:** <br>- C18 by the T3KEEP patch (l.4627-4633); the residue is C23; <br>- C19: the "currently ticked" line is gone; <br>- C20 by the l.4619 RESERVE-SLOT EDGES | `CONTEXT.md` l.4618-4642 |

## NEXT 24 H (29 Sep ~14:50Z -> 23:59Z)

| ID | When (UTC / MSK) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W373 | **now; before 17:40Z** | Kill pre_exp89t (R41-A1) | **overdue** | see OVERDUE |
| W380 | **before 15:13Z** (18:13 MSK) | KEY FACTS refresh 2 (R41-A6) | not started | see OVERDUE |
| **W381** (new; the round-41 bookkeeping) | at the next CONTEXT write | Log "ROUND 41 APPLIED (R41-A1..A8)". The main session has logged nothing since 13:58Z, and `round41/` is untracked | not started | `git status` 14:46Z; `CONTEXT.md` l.4618 is the newest entry |
| **T230** (updated) | **15:13Z, 16:13Z** rounds 42-43; **17:13Z** round 44; **18:13Z** round 45 | Ops / READS-vs-CARD lens, Chrome only, 0 Kaggle API calls, no builds, no slot work | pending | `CONTEXT.md` l.4085, l.4099 (hourly to 18:13Z); `biohub-research-round.js` l.37 |
| **T234** (new; replaces T231) | feed **~15:59:12Z** and **~17:29:20Z (the last run)** | E10 v3 trigger ≥ 0.960. **Info only after 14:10Z** unless the user names the notebook. **After 16:50Z it cannot finish.** 744357 is a farewell, and the best public notebook is 0.953 | live | `round41/scan_plancheck.notes.md` "Feed loop sleep pid 37148"; `round41/report.json` new_facts (3) |
| W364 edges | **16:50Z** (19:50 MSK) | The absolute last dummy start, only on the user's explicit yes. After that, "cannot finish by 23:59Z" | pending (default: unused) | `CONTEXT.md` l.4619-4627 |
| **W375** (new; = **R41-A2**) | log **before 18:00Z** (21:00 MSK) | **CONTEXT line: exp89t T7 + MANUAL-ADMIT UNDER DECISION B.** Take the exact T7 (a) / (b) texts and the manual-admit mapping from R41-A2. This fixes C21 | not started | `round41/report.json` R41-A2 |
| **W377** (new; = **R41-A3**) | **before 17:40Z** (20:40 MSK); used at 18:37Z | **Patch `mk_card_1837.py`.** <br>- Save `round41/report.notes.md` l.7-44 (between the markers) as `<SP>/patch_mk_card_r41.py`. <br>- Run it: it must print `patched sha8 a19e1bd6`, and it refuses unless the source is 59c54168. <br>- Run it again with `--write`, which keeps a `.59c54168.bak`. <br>- Then `PYTHONIOENCODING=utf-8 python <SP>/mk_card_1837.py --dry-all` must give **35 ok**. <br>- Log the CONTEXT line. This fixes C23 | not started (sha 59c54168 at 14:45Z) | `round41/report.json` R41-A3; `round41/report.notes.md` l.5-45 |
| **W379** (new; = **R41-A5**; merges T225 / W361 / W368) | **17:13Z** round → kill check **17:29-17:35Z** | **Liveness census** with the new PID list. Expected alive: <br>- poller 37016, watcher 30864, watchdog 22236 (re-arm after any alert); <br>- manual_admit 3028, t7 29648; <br>- feed stop job 32220, FEED SIGNAL waiter **24700 / 11836**; <br>- timers 33156 / 30648 / 31720 / 19388. <br>**Expected gone: 36816.** After the ~17:29:20Z feed run, the stop job kills 20892 / 10924. Log one line | pending | `round41/report.json` R41-A5 |
| T228 | **17:30-20:00Z** (20:30-23:00 MSK) | Quiet window. Only the poller, the watcher save, manual_admit, t7 and the SELECTED reads call Kaggle. **pre_exp89t must be dead by then** (W373) | standing | `biohub-research-round.js` l.37; `CONTEXT.md` l.4614 |
| T213 | all evening | Laptop on AC with the lid open. It was on AC at the 14:28Z / 14:35Z checks, 78% | watch | `round41/report.notes.md` 14:35Z |
| T208 + W344 | early **~17:53Z**; typical **18:17-18:29Z** | **exp89t read under decision B:** <br>- **≥ 0.960:** T1 (T2 if the read header is > 19:12:17Z). RECOMMENDED PAIR line first, then "снимите exp87a 56640366, отметьте exp89t 56669888 (#37 оставьте)". <br>- **0.959:** T3KEEP (the pair is unchanged). <br>- **≤ 0.958:** T5. <br>- **ERROR:** T6 (pass `--lhi`). <br>1 fresh SELECTED read before each message. **The expected outcome is T3KEEP** (I452) | pending | `CONTEXT.md` l.4607-4617, l.4633-4639 |
| **W378** (new; = **R41-A4**) | 18:37Z card; T7 ~19:20Z; manual-admit 19:44:45Z | **Input rules:** <br>- **(1)** `--lb post_exp89t` only if the watcher printed "post_exp89t: rank" with SubmissionCount 57; otherwise `--lb e10_20260929T1141Z --teams 3994`. <br>- **(2)** If read_selected returns ≠ 2 refs, send the R39-A4 push first. <br>- **(3)** Prefix every Russian-printing call with `PYTHONIOENCODING=utf-8`. <br>- **(4)** T6 needs `--lhi`. <br>- **(5)** If a header shows no SubmissionStatus, read the newest poll.log block that has a `^ref,` line by hand. <br>- **(6)** Rank line: correct the label to 14:41 МСК, or replace it with the latest Chrome read made before 17:30Z. **Never quote "#148" or "17 из 22" after 14:19Z** | pending | `round41/report.json` R41-A4 |
| T226 | **18:13Z** (21:13 MSK) | READS-vs-CARD round from local files only. Do not skip it | pending | `round39/report.json` R39-A6 (3) |
| T152 | **18:37Z** (21:37 MSK), timer w33156 | FINAL card via `mk_card_1837.py`, a19e1bd6 if W377 is done. Make 1 fresh SELECTED read first. Before sending, check that no stale `card_1837_*.txt` test file exists (I461) | pending | `CONTEXT.md` l.4627-4633 |
| **T235** (new) | poller headers **~19:10:3xZ, ~19:20:3xZ (T7), ~19:40:4xZ, ~19:50:4xZ** | Cadence ~602 s. **The last admissible header before 19:45:17Z is ~19:40:4xZ.** manual-admit runs at 19:44:45Z on that header. A result first seen at ~19:50Z is T8 (not a final) | info | `round41/report.json` new_facts (6); `round41/scan_hyp_evedry41.notes.md` |
| T227 | **~19:20Z** (22:20 MSK) | T7 trigger w29648. If exp89t is still PENDING: 1 SELECTED read, then send the **R41-A2 T7 text (not the round-40 text)** | armed | `CONTEXT.md` l.4563-4565; C21 |
| T161 + T221 | **19:43Z** timer w30648; **19:44:45Z** manual-admit w3028 | Comparator check. The manual list is mapped with the R41-A2 table; if not terminal, T8 | armed | `CONTEXT.md` l.4535-4537; `round41/report.json` R41-A2 |
| T10 | **20:00Z (23:00 MSK)** | Finals tick. **Done: П3** (12:37Z). Re-tick only after exp89t ≥ 0.960. The session never ticks | done unless ≥ 0.960 | `CONTEXT.md` l.4579-4581, l.4617 |
| T232 | ≥ 20:05Z, optional | One manual kaggle_feed run | optional | `round40/report.json` R40-A5 |
| T222 / T153 / T162 | 20:00-23:59Z; **21:05Z** timer w31720 | Re-selection is allowed until 02:59 MSK. Comparator check; last-call notify on a mismatch. No submit without the user's yes | armed | `CONTEXT.md` l.4549-4558, l.4565-4568 |
| **W382** (new; = **R41-A8**; merges W371 / W362) | only if the user asks, before 20:00Z | The answer lines, corrected by the skeptics: <br>- "decision B cost?" ≈ 0 (±0.0007). **Never "в лучшем случае ~0.0005".** A 0.960 promotion is worth ~+0.0002..+0.0006; <br>- K: mostly READMIT, ~+0.001 on private with a wide spread. **Never call the harsh K a "floor"**; <br>- insertion: +0.0019 from the old config; P(+) ~0.9-0.97 | conditional | `round41/report.json` R41-A8, rejected |
| W370 (a) | only on a slot-2 submit | Arm the mid_<token> save | conditional | `round40/report.json` R40-A7 |
| W177 H2 / T49 | 23:00Z / 23:00-23:45Z | LESSONS H2; the final public LB snapshot (at most 1 call) | pending | `_curation/20/watch.json`; `CONTEXT.md` l.2619 |
| T11 / T163 | **29 Sep 23:59Z** (02:59 MSK 30 Sep) | Deadline. Files must FINISH scoring by then. Slot 2 expires unused by default | - | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744250 |
| W19 / W73 / W102 / W93 / W165b / W261 / T196 | standing | ONE poller (header < 15 min); no resubmit of class-C or ERRORed files; SEC only as V_pub; a timeout on every Kaggle call; light polling | standing | `CONTEXT.md` l.3331-3335, l.3692-3703; `memory/feedback-kaggle-api-load.md` |

## LATER (after 29 Sep 23:59Z)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T155 + **W376** (new; = **R41-A7**; merges W370 (b) and the rest of W374) | 30 Sep **00:07Z** (03:07 MSK), timer w19388 | **POST-DEADLINE:** <br>- **(1)** `PYTHONIOENCODING=utf-8 timeout 180 python tools/uptest.py save final_0007Z`; log whether the LB is public or private. <br>- **(2)** 1 read_selected call + 1 submissions list. <br>- **(3)** **Stop lb_poll.py w37016** (it loops forever), the watchdog 22236 and any leftover waiters. <br>- **(4)** git add CONTEXT.md, poll.log, ledger.md, **`_lb/e10_20260929T1141Z/`**, `_lb/post_exp89t` / `final_0007Z` if present, `experiments/discussions/` (744357.md, digests, state.json), `research/wf_ideas_v4/round41/`, `_night_subs.*` (as evidence). <br>- **(5)** Commit as Vitaly Neybauer with **no Co-Authored-By** (the memory rule beats the harness reminder), then push | `round41/report.json` R41-A7; `memory/feedback-git-no-coauthor.md` |
| W372 | post-deadline, optional | RESULTS.md l.20 "keep steal off" annotation | `round40/report.json` R40-A9 |
| T216 / T223 / T229 / T233 + **T236** (new) | post-deadline | Lesson checks: <br>- I413 / I423, I419 / I420, T229 (MC П2 vs П3); <br>- T233: the audit's "≥ 4 thousandths public-only" claim vs the private exp87a / exp75 / #37; <br>- **T236:** did the 7-team 0.963 cluster survive the private reveal? (I459) | `CONTEXT.md` l.4596-4604; `round41/report.json` new_facts (2) |
| W317 / W321 / W326 / W312 / W295 / W29 | post-deadline | Older research follow-ups | `_curation/38/watch.json` |
| T133 / T170 | 3 Oct | GPU quota refresh | `CONTEXT.md` l.4239-4241 |

**Passed or finished time-bound items:**
- **Earlier deadlines:** the R8 new-mechanism cutoff (27 Sep 12:00Z), the 28 Sep 12:00Z consolidation (superseded) and the R8 29 Sep 10:00Z edge all passed.
- **Today:**
  - the S0 fallback 11:45Z, the slot-2 decision 11:54Z, the card 12:04Z;
  - **the tick 12:37Z**;
  - feed 12:58Z, the audit 13:21Z, decision B 13:34Z;
  - **round 40 applied 13:58Z** (l.4618);
  - the feed run 14:29:04Z;
  - **the default reserve-slot dummy edge, 14:10Z (passed).**
- **Friend replies:** none awaited (`CONTEXT.md` l.2175-2176).
- **Standing notes:**
  - **T156:** 20:00 UTC = 23:00 MSK. Always write the zone.
  - **T204:** poller cadence ~602 s.
  - **T205:** LB `LastSubmissionDate` = the max submit time among SCORED files.

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I450** (new) | "T7 text ... still says '>= 0.960 или 0.959 с UP'; manual_admit_COMPLETE says 'T2 / T3 / T4_question / T5_late' -> contradict decision B" | `round41/scan_plancheck.notes.md` l.5 | T7 is the last message before the tick. If the round-40 text is sent, it promises a promotion that B withdrew (C21, W375). |
| **I451** (new) | "mk_card accepts inconsistent inputs ... T1 at 0.959 -> promotion card (breaks decision B); T2 with hdr 19:50Z/lhi 10.84 -> promotion card past the 19:45:17Z edge ... obsolete T3 accepted (in PROMO). T1/T2 without --llo -> TypeError" | `round41/scan_plancheck.notes.md` l.4 | The code is typed by hand at ~21:20-21:37 MSK, and one slip builds a wrong-direction card (C23, W377). |
| **I452** (new) | "exp87a unrounded (uniform-in-block, 17th of 22): ~0.95875 -> exp89t needs DIS_pub >= ~+0.00075 (range +0.0000..+0.0010) to display 0.960"; DIS old lab "-0.0007" at 2.25 | `round41/scan_recheck.notes.md` ("exp87a unrounded", "DIS old lab") | **0.959 → T3KEEP is the most likely read.** Prepare the T3KEEP message as the default and do not expect a re-tick. |
| **I453** (new) | Headers land at "~19:10:35Z, ~19:20:37Z (T7 fires ~19:20:40Z), ~19:40:42Z, ~19:50:44Z (manual-admit fires at 19:44:45Z)" | `round41/scan_hyp_evedry41.notes.md`; `round41/report.json` new_facts (6) | The effective admit edge is the ~19:40:4xZ header, not 19:45:17Z. A read first seen at ~19:50Z is T8 (T235). |
| **I454** (new) | "lastok awk: '[ERROR ...]' poller headers ... count as OK -> empty block wins; '[empty stdout' notes + valid body (3 of 571 blocks) ... are skipped" | `round41/scan_hyp_evedry41.notes.md` | t7 and manual-admit can see an empty block (~0.5% per poll). Read the newest `^ref,` block by hand (R41-A4 (5)). The fix was rejected so that no armed job is restarted. |
| **I455** (new) | "uptest.save mkdirs before download; a timeout-180 kill leaves an empty/partial post_exp89t -> load() IndexError/BadZipFile" | `round41/scan_hyp_evedry41.notes.md` | Use `--lb post_exp89t` only if the watcher printed "post_exp89t: rank" with count 57 (R41-A4 (1)). |
| **I456** (new) | "--show under cp1251 -> UnicodeEncodeError on '≤' (sys.stdout.encoding cp1251)" | `round41/scan_hyp_evedry41.notes.md` | Any Russian print crashes without `PYTHONIOENCODING=utf-8`. This curation hit it too (14:44Z). |
| **I457** (new) | "Card rank label = lb folder mtime (14:45 MSK build) not snapshot 14:41 MSK; rank 7 h old"; the latest Chrome read is "#151 из 3 999, 18 из 23"; "Never quote '#148' or '17 из 22' after 14:19Z" | `round41/scan_hyp_evedry41.notes.md`; `round41/report.json` R41-A4 (6) | The card's rank line is the most visible stale number in front of the user. |
| **I458** (new) | "00:07Z: lb_poll.py loops forever (no end time) -> must be stopped post-deadline"; the save has no internal timeout | `round41/scan_hyp_evedry41.notes.md`; R41-A7 | The API-load rule (`memory/feedback-kaggle-api-load.md`). An unattended poller keeps calling Kaggle after the deadline. |
| **I459** (new) | "the exact-0.963 cluster is now 7 teams ... generated-looking handles ... likely a multi-account ring ... If Kaggle removes it, our private rank could rise by up to ~7 places (not counted on)" | `round41/report.json` new_facts (2); `round41/scan_browser.notes.md` | This is a post-deadline check (T236). It is not a finals signal. |
| **I460** (new) | "Do not log 'floor'" (the harsh K = -0.001 is a labelled stress case; its cost scales with the readmit band, ~-0.0003..-0.0023); "'в лучшем случае ~0.0005': wrong phrase (the spread is symmetric)" | `round41/report.json` rejected; R41-A8 | Keep any answer to the user consistent (W382). |
| **I461** (new) | "my in-memory mk_card guard test ... wrote scratchpad card_1837_{PENDING,T1,T3KEEP,T5,T6}.txt at 14:33:14Z (test inputs, --now 18:37Z). Removed at 14:33:37Z" | `round41/report.notes.md` l.4 | Test runs can leave ready-looking cards. At 18:37Z build fresh and check the timestamp, never send a pre-existing `card_1837_*` file (T152). |
| I442 (**updated**) | The e10 fallback CSV has 1,006 rows; pass `--teams 3994` | `round40/report.json` R40-A3 (6) | After R41-A3 this is the builder default. Without the patch it must still be passed by hand. |
| I443 (**updated**) | The feed loop's ~18:59Z run would fall inside the quiet window | `round40/scan_plancheck.notes.md` | Now covered by the feed stop job w32220 (17:20-17:35Z, `round41/scan_plancheck.notes.md`). Confirm it at W379. |
| I448 (open) | `_lb/e10_20260929T1141Z/lb.csv` is still **untracked** | `git status` 14:46Z | It is the only S0. Commit it at 00:07Z (W376 (4)). |
| I410 / I411 (open) | read_selected.py, t7_trigger.sh, manual_admit.sh, mk_card_1837.py and soon patch_mk_card_r41.py live **only in the session scratchpad** | `CONTEXT.md` l.4563-4565, l.4627-4633 | After a restart, re-arm from CONTEXT l.4559-4642 and the round39-round41 texts. |
| I441 / I444 / I445 / I446 / I447 | See `_curation/40/watch.json` | - | I446 is updated by I457 (the rank is now #151). |
| I424 / I420 / I423 | "#38 лучше #37 только если ... (P ~0.1–0.2)"; the lab CI sign was wrong; the public division evidence is 1-2 fork events | `round38/report.json` | Post-deadline lessons (T216 / T223). |
| I440, I449 | Resolved: the T3KEEP patch (l.4627-4633). The residue is C23 | `CONTEXT.md` l.4627-4633 | - |
| I430-I439 and older | Resolved, in CONTEXT, or moot | `_curation/40/watch.json` ... `_curation/27/watch.json` | - |
