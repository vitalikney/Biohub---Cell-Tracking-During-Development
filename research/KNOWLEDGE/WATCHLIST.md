# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-29 ~16:45 UTC (19:45 MSK), curation 43. This updates the curation-41 build of ~14:50Z (committed in 55ec8ab; structured copy in `research/KNOWLEDGE/_curation/41/watch.json`). There was no curation 42 (round 42 was lost to a network drop, `CONTEXT.md` l.4668-4677). Older predecessors run from `_curation/40/watch.json` down to `_curation/18/watch.json`. Rows not repeated here are unchanged there.

**Sources read for this update:**
- **`CONTEXT.md`:** 4,698 lines; `## 9. Literature` starts at l.4678. Two new entries since curation 41:
  - l.4643-4667 (14:59Z): **ROUND 41 APPLIED** (R41-A1..A4, A6). pre_exp89t killed ~14:48Z (A1); T7 + manual-admit texts under decision B (A2); `mk_card_1837.py` patched to sha8 **a19e1bd6** (A3); input rules (A4).
  - l.4668-4677 (15:59Z): **ROUND 42 LOST TO A NETWORK DROP; SESSION RESTART; JOBS RE-ARMED.** Laptop on battery 15:08Z, network lost, all 9 round-42 agents failed; the Claude session restarted and re-armed the local-only jobs; the jobs that call Kaggle were kept (poller w37016, manual_admit w3028, old watcher w30864, feed loop + stop job).
  - **Nothing is logged after 15:59Z** (checked 16:42Z).
- **`git log`:** 55ec8ab (14:59Z, round 41 + curation 41) and **369b065** (15:59Z, ops). **`git status` (16:42Z):** `M` ledger.md, poll.log; `??` `_lb/e10_20260929T1141Z/` (**still untracked**), `_night_subs.*`, **`research/wf_ideas_v4/round42/`** (scan notes only), **`research/wf_ideas_v4/round43/`**.
- **`research/wf_ideas_v4/round43/report.json`** (written 16:36Z, untracked, **not yet applied**): **R43-A1..A8**, new_facts (1)-(10), plan_issues (1)-(11), rejected (1)-(7); the Russian report text is embedded in `next_focus` (no REPORT.md). Also `round43/report.notes.md`, `scan_plancheck.notes.md`, `scan_hyp_ops43.notes.md`, `scan_recheck.notes.md`, `v_*.notes.md`.
- **`experiments/lb_poll/poll.log`:** newest header **16:34:55Z** (l.32351); exp89t 56669888 **PENDING**; `ledger.md` (16:34:57Z) gives L > 7.57 h.
- **`experiments/discussions/feed_loop.log`:** last run **15:59:14Z** (0 new topics, 1 new comment on 744250, E10 FLAG none). Next and last run ~17:29:14Z.
- **Round prompt `experiments/workflows/biohub-research-round.js`** (last changed in 55ec8ab): l.20 now has #151, "pre_exp89t.sh killed", a19e1bd6, R41-A2; it **still says** "polls every 5 min", "S0 tags pre_exp89t (17:40Z)" and "T7 trigger ~19:20Z". l.37 still lists pre_exp89t among the allowed callers and keeps the "FIRST run `python tools/e10_snapshot.py`" fallback.
- **`experiments/RESULTS.md`:** 163 lines; probe rows still end at probe 46 (l.79).
- **Process census ~16:40Z (this curation, Win32_Process, read-only, 0 Kaggle calls):**
  - Alive: poller 37016; feed loop 10924/20892; orphans of the dead claude 15852: old exp89t watcher 29636->30864, manual_admit 29032->13708 + 3028, feed stop 24584->32220; new session (claude 12724): exp89t waiter 9016->29828, t7_trigger 34124->6344 + 16748, timers 32396 (17:13Z), 30820 (18:13Z), 29184 (18:37Z), 20960 (19:43Z), 24260 (21:05Z), 21232 (00:07Z), feed-signal waiter 13072->8364, **the blind watchdog 22680->5024 (still the old version, so R43-A1 is not applied)**.
  - **No R43-A2 manual-admit reader** is running.
  - Gone: pre_exp89t 36816 (R41-A1 done).
  - Scratchpad `mk_card_1837.py` sha8 **a19e1bd6** (backup `.59c54168.bak`); no `card_1837_*.txt` file exists.
  - The three orphan task outputs `tasks/bud7lhxmi.output`, `b2rmui3gc.output` and `b8b41p9da.output` are all 0 bytes.
  - Battery: BatteryStatus 2 (AC), 79%.

All times are UTC. The user thinks in MSK = UTC+3 (`CONTEXT.md` l.3683-3687). IDs are stable: W = action, T = time-bound reminder, I = insight, C = contradiction. Status values: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at ~16:45Z, 29 Sep:**
- **Best display 0.959**, exp87a 56640366 = V_pub.
- **SELECTED = П3 {exp87a 56640366, #37 56563521}** (API 12:37:31Z, `CONTEXT.md` l.4579-4581).
- **Decision B:** exp89t promotes only at **>= 0.960** (l.4607-4617); the code enforces it (`round43/v_hyp_ops43_r43-ops-card.notes.md`).
- **exp89t 56669888 is PENDING** (T0 09:00:17Z; L_lo 7.57 h at 16:34:55Z). Projected clean headers (`round43/report.json` new_facts (6)):
  - typical read 18:15:20, 18:25:22, 18:35:25Z (21:15-21:35 MSK);
  - UNPROVEN-ins after 19:12:17Z; **T7 at ~19:15:35Z** (22:15 MSK);
  - **last admissible header ~19:35:40Z**; the next ~19:45:42Z is after the 19:45:17Z admit edge, so manual-admit 19:44:45Z is the only record in between.
- **Slot 2:** the absolute last dummy start is **16:50Z** (19:50 MSK, `CONTEXT.md` l.4619-4627). After that it is "closed unused" (not "expired", `round43/report.json` rejected (6)).
- **Rank:** **#154 of 4,003**, 5th from the bottom of the 0.959 block (block ends at #158; Chrome 16:15Z, `round43/report.json` new_facts (1)).

**Changes since ~14:50Z (curation 41):**
- **Done:**
  - **W373 / C17** (= R41-A1): pre_exp89t killed ~14:48Z (`CONTEXT.md` l.4644-4648; census 16:40Z);
  - **W375 / C21** (= R41-A2): T7 + manual-admit texts under decision B (l.4648-4657);
  - **W377 / C23** (= R41-A3): builder patched, sha8 a19e1bd6 (l.4657-4662; verified 16:40Z);
  - **W378** (= R41-A4): input rules logged (l.4662-4667). They are applied in the evening;
  - **W381**: round 41 logged (l.4643) and committed (55ec8ab).
- **Partly done:** **W380** (= R41-A6): l.20 refreshed but three stale phrases remain (now C24 / C25), and C22 (l.37) is still open.
- **Superseded:** W379 (R41-A5 census) by **W388** (R43-A6), because its PID list died at the 15:59Z re-arm; W376 is extended by **W390** (R43-A8); T235 header times by the new phase (above); W364 (2) is moot (slot 2 closes 16:50Z).
- **New:**
  - actions **W383-W390** (= R43-A1..A8) and **W391** (round 42/43 bookkeeping);
  - reminders **T237-T240**;
  - contradictions **C24-C30**;
  - insights **I462-I473**.

---

## OVERDUE / DUE NOW

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W383** (new; = **R43-A1**) | **Replace the blind watchdog** (0 Kaggle calls). <br>- TaskStop the watchdog task (wrapper w22680), then `Get-Process -Id 5024,22680` must return nothing; if 5024 survives, `Stop-Process -Id 5024 -Force` (R41-A1 lesson). <br>- Re-arm the v2 loop from R43-A1 (2). It checks the clean-header age (drops `[empty stdout` and `[ERROR` headers with `grep -vF`) and battery status every 120 s, and alerts at > 25 min without a clean poll or on battery. <br>- On any alert, read the waiter / t7 / timer outputs, then re-arm. <br>- Tell the user once, in MSK, to stay on AC with the lid open and a stable network until 23:00 MSK (the text is in R43-A1 (4)). <br>- One CONTEXT OPS line with the new PIDs | **overdue in effect.** "Now" per the report; at 16:40Z 22680->5024 (the old version) is still alive | **before the first possible read header ~18:15Z** (21:15 MSK) | `round43/report.json` R43-A1, plan_issues (1); `round43/scan_plancheck.notes.md` l.4; census 16:40Z |
| **W384** (new; = **R43-A2 (a)**) | **Arm the manual-admit reader.** manual_admit 3028 is an orphan: its stdout `tasks/b2rmui3gc.output` reaches no session, and the 19:43Z timer fires 1 min 45 s before it. The reader polls that file (every 15 s, until 19:47:00Z), then prints it, the last `[manual-admit]` block and the awk first-terminal header. The command is in R43-A2 (a) | not started (no such process at 16:40Z) | **arm now; must be armed before 19:40Z**; it fires by 19:47Z (22:47 MSK) | `round43/report.json` R43-A2, plan_issues (2) |
| **W385** (new; = **R43-A7**) | **CONTEXT line "SLOT 2 CLOSED UNUSED"** in the R43-A7 wording, and a **KEY FACTS refresh** (`biohub-research-round.js` l.20): <br>- polls every ~10 min, not 5; <br>- projected headers 18:15:20 / 18:25:22 / 18:35:25Z; T7 ~19:15:35Z; last admissible ~19:35:40Z; <br>- rank "Chrome 19:15 MSK: #154 of 4 003, block ends #158, 5th from bottom"; <br>- 3 poll.log error blocks (15:19:43, 15:31:24, 15:43:04Z). <br>Also remove "S0 tags pre_exp89t (17:40Z)" and "T7 trigger ~19:20Z" from l.20 and "pre_exp89t" from l.37 (C22, C24) | not started | **at or after 16:50Z** (19:50 MSK), with the next CONTEXT write; before the 17:13Z round | `round43/report.json` R43-A7, plan_issues (8), (10); `biohub-research-round.js` l.20, l.37 (grep 16:41Z) |
| **W391** (new; bookkeeping) | Log "ROUND 43 APPLIED (R43-A1..A8)" in CONTEXT. `round42/` and `round43/` are untracked | not started (CONTEXT newest 15:59Z) | at the next CONTEXT write | `git status` 16:42Z; `CONTEXT.md` l.4668 |
| W126 (part 2) | Add RESULTS.md rows for probes 47-54: <br>- 47: 0.955; 48: 0.957; 49: 0.955; 50: exp85a 0.958; <br>- 51: exp87a 0.959; 52: exp89r 0.957; 53: exp75 0.955; 54: exp89p 0.956. <br>Then probe 55 (exp89t) when it reads | **overdue** (rows end at 46, l.79). The values are in `ledger.md` | low; post-deadline OK | `experiments/RESULTS.md` l.79; `experiments/lb_poll/ledger.md` |
| W336 | One line saying that the user's 08:27Z / 08:28Z instructions override R8's 10:00Z edge (l.1671) | not started; moot in practice | low | `CONTEXT.md` l.1671 |
| W286 / W297 / W202 + W244 / W176 / W177 / W182 / I208 / W57 / W66 / W31 / W72 / W150 / W308 | Older text and cleanup items | overdue, low | H2 29 Sep 23:00Z; post-deadline OK | `_curation/36/watch.json`, `_curation/26/watch.json` |

## CONTRADICTIONS TO RESOLVE BEFORE THEY FIRE

| ID | Conflict | Which text wins | Evidence |
|---|---|---|---|
| **C24** (new) | **Header phase.** <br>- Prompt l.20 says "T7 trigger ~19:20Z"; CONTEXT l.4564 says "expected ~19:20Z (22:20 MSK)"; curation 41 T235 said the last admissible header was ~19:40:4xZ. <br>- After the outage the phase is **18:15:20 ... 19:15:35Z (T7) ... 19:35:40Z (last admissible), then 19:45:42Z (after the edge)** | **`round43/report.json` new_facts (6)** (measured cadence 16:04:47 -> 16:14:50 -> 16:24:52Z). A retry shifts the phase later. Fix with W385 | `round43/report.notes.md` "Cadence check" |
| **C25** (new) | Prompt l.20 "status polls every 5 min" vs the real cadence ~10 min 2-3 s (sleep 600 + call) | **Real cadence** (`round43/scan_plancheck.notes.md` l.2). Fix with W385 | `biohub-research-round.js` l.20; R43-A7 |
| **C26** (new) | The CONTEXT 15:59Z entry lists 2 poll.log error blocks (15:31:24Z, 15:43:04Z); there are **3** (15:19:43Z too) | **poll.log** (each has 3 `[empty stdout` notes and no rows). Fix with W385 | `CONTEXT.md` l.4670; `round43/scan_hyp_ops43.notes.md` (6) |
| **C27** (new) | R41-A4 (2) (`CONTEXT.md` l.4663-4664): "SELECTED must be exactly 2 refs (else R39-A4 push first)". `read_selected.py` has no retry, so a network blip (no "SELECTED at" line) would send a false "wrong pair" alarm | **R43-A3 (W386):** a read with no "SELECTED at HH:MM:SSZ: N ->" line is a FAILED READ. Retry once after 60 s. If it fails again, no wrong-pair push; ask the user to check "2 of 2 selected" | `round43/report.json` R43-A3, plan_issues (5) |
| **C28** (new) | The R41-A5 census list (w29648, w22236, w33156, w30648, w31720, w19388, w24700) is dead after the 15:59Z re-arm; using it would report false deaths and could cause duplicate re-arms (extra Kaggle calls in the quiet window) | **The R43-A6 list (W388)** | `round43/scan_plancheck.notes.md` l.3 |
| **C29** (new) | The card's default rank line is "#141 из 3 994 (14:45 МСК)" (the 11:41Z e10 snapshot labelled with the folder mtime) vs Chrome 16:15Z "#154 из 4 003". R41-A4 (6) made the replacement optional | **R43-A5 (W387):** overwrite the line after the build and grep-check it | `round43/v_plancheck_pc43-06.notes.md`; R43-A5 |
| **C30** (new) | The pre-registered T1 footnote "ins-tail? if L_lo > 9.6 h" (`CONTEXT.md` l.4014, R38-A5) is missing from `mk_card_1837.py` a19e1bd6 and from the round-40 T1 push text. **Also:** CONTEXT l.3750 phrases the trigger as "L_hi in (9.6, 10.2]", while l.4014 and R43-A4 use L_lo > 9.6 h | **R43-A4 (2):** add the footnote by hand on T1 with L_lo > 9.6 h (a ~1-2% case). Do not patch the script. The l.3750 / l.4014 wording difference is unresolved; R43-A4 follows l.4014 | `round43/report.notes.md` "R43-PI-1 verified"; `round43/scan_recheck.notes.md` "RC-A card check" |
| C22 (open, partly) | Round prompt l.37: "0 Kaggle CLI/API calls after 12:00Z", then "If the browser tools are unavailable, use the Kaggle CLI ... FIRST run `python tools/e10_snapshot.py`"; also lists "pre_exp89t" among the allowed callers | **R39-A6 (0 Kaggle calls after 12:00Z; Chrome only).** Round 42's browser scan (Chrome disconnected at 15:14Z) followed R39-A6 and made 0 calls (`round42/scan_browser.notes.md`). Fix the text with W385 | `biohub-research-round.js` l.37 |
| C15 | The 18:37Z / 19:43Z / 21:05Z timer texts push "if not the recommended pair" | **The R39-A4 comparator plus R43-A3.** No push while SELECTED = П3 | `CONTEXT.md` l.4565-4568 |
| C11 | mid_<token> scope | **CONTEXT 11:54Z** | `_curation/40/watch.json` |
| C17 / C21 / C23 | - | **Resolved** by R41-A1 / A2 / A3 (`CONTEXT.md` l.4643-4662) | census 16:40Z; sha8 a19e1bd6 |

## NEXT 24 H (29 Sep ~16:45Z -> 23:59Z)

| ID | When (UTC / MSK) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W383 | **now; before ~18:15Z** | Watchdog v2 + ask the user to stay on AC | **overdue in effect** | see OVERDUE |
| W384 | **now; before 19:40Z** | manual-admit reader | not started | see OVERDUE |
| W364 edges + W385 | **16:50Z** (19:50 MSK) | The absolute last dummy start passes. Then log "SLOT 2 CLOSED UNUSED" and refresh KEY FACTS. From then on no round proposes a submit or a build for scoring | pending (default: unused) | `CONTEXT.md` l.4619-4627; R43-A7 |
| **T237** (new; = round 44; replaces T230) | **17:13Z** (20:13 MSK), timer w32396 | Round 44: the R43-A6 census; **one Chrome rank read before 17:30Z** for the card (R43-A5); one Chrome look at 744250 for a host answer on when selection locks (quote it verbatim; the 23:00 MSK tick plan does not change); skip the recheck lens (11 null rounds) | pending | `round43/report.json` next_focus, R43-A6 |
| **W388** (new; = **R43-A6**; replaces W379) | **17:13Z** round; feed-stop check **after 17:36Z** (20:36 MSK) | **Census against the new list:** <br>- poller 37016; <br>- orphans: old watcher 29636->30864, manual_admit 3028 (29032->13708), feed stop 24584->32220 (ends ~17:35Z); <br>- feed loop 10924/20892 (last run ~17:29Z, then killed); <br>- exp89t waiter 9016->29828; t7_trigger 16748 (34124->6344); <br>- timers 30820 (18:13Z), 29184 (18:37Z), 20960 (19:43Z), 24260 (21:05Z), 21232 (00:07Z); 32396 has fired by then; <br>- feed-signal waiter 13072->8364 (harmless); <br>- the W383 watchdog (5024/22680 gone) and the W384 reader. <br>Expect t7 x1, manual_admit x1, timer.sh x5. Confirm the feed stop with `Get-Process -Id 10924,20892` (must be empty) and `b8b41p9da.output`, **not** with the stop job's own `run_feed_loop` count (I467). Log one line | pending | `round43/report.json` R43-A6, R43-A2 (c) |
| **T234** (updated) | feed **~17:29:14Z (the last run)** | E10 v3 trigger ≥ 0.960 is **report-only**: slot 2 has closed (16:50Z) and no new file can finish. The best public notebook is 0.953 (Chrome 16:15Z) | live, info only | `round43/report.json` new_facts (3), R43-A7 |
| T228 | **17:30-20:00Z** (20:30-23:00 MSK) | Quiet window. Only the poller, the old watcher's save, manual_admit and the SELECTED reads call Kaggle. pre_exp89t is gone | standing | `biohub-research-round.js` l.37; `CONTEXT.md` l.4644-4648 |
| T213 | all evening | **Laptop on AC with the lid open and a stable network.** The 15:08Z battery switch took the network down for 45 min and killed round 42. AC at 16:14Z (65%) and 16:40Z (79%) | watch | `CONTEXT.md` l.4668-4677; census 16:40Z |
| T226 | **18:13Z** (21:13 MSK), timer w30820 | Round 45: READS-vs-CARD from local files only, 0 Kaggle calls | pending | `round43/report.json` next_focus |
| T208 + W344 + **W389** (new; = **R43-A4**) | typical **18:15-18:35Z**; any time up to **19:45:17Z** | **exp89t read under decision B:** <br>- **≥ 0.960:** T1 (T2 if the read header is > 19:12:17Z). <br>- **0.959:** T3KEEP (the pair is unchanged). <br>- **≤ 0.958:** T5. **ERROR:** T6 (pass `--lhi`). <br>- **Take `--hdr` from the awk first-terminal one-liner** (R43-A4 (1)), not from the waiter's echo; if they differ, recompute `--lhi` (+210 s per failed attempt) and log both. <br>- **T1 with L_lo > 9.6 h:** add the "ins-tail?" footnote by hand (R43-A4 (2), C30). <br>1 fresh SELECTED read before each message. **The expected outcome is T3KEEP** (I452) | pending | `CONTEXT.md` l.4607-4617, l.4648-4667; `round43/report.json` R43-A4 |
| **W386** (new; = **R43-A3**) | every SELECTED read: **18:37Z, 19:43Z, 21:05Z**, and before any exp89t push | Failed-read rule (C27): no "SELECTED at" line → retry once after 60 s (at most 2 read-only calls); still failing → no wrong-pair push, ask the user to check "2 of 2 selected" and build the card with `--sel/--seltime` from the last good read (12:37:31Z), stating its time | pending | `round43/report.json` R43-A3 |
| T152 + W378 + **W387** (new; = **R43-A5**) + W384 (b) | **18:37Z** (21:37 MSK), timer w29184 | **FINAL card** via `mk_card_1837.py` a19e1bd6. <br>- Before it: `cat tasks/bud7lhxmi.output`; pass `--lb post_exp89t` only if it has "post_exp89t: rank" with SubmissionCount 57, else `--lb e10_20260929T1141Z --teams 3994` explicitly (R41-A4 (1), R43-A2 (b)). <br>- 1 fresh SELECTED read (W386). `PYTHONIOENCODING=utf-8` on every call. <br>- After the build, **overwrite the "Мы на ЛБ (" line** with the newest pre-17:30Z Chrome read (R43-A5 template; for T1/T2 add ", до чтения exp89t"); check `grep -c '^Мы на ЛБ (Chrome'` = 1 and `grep -cE '#141\|3 994\|14:45 МСК\|#148\|17 из 22'` = 0; log the card's sha8. <br>- Never send a pre-existing `card_1837_*` file (I461) | pending | `CONTEXT.md` l.4657-4667; `round43/report.json` R43-A2 (b), R43-A5 |
| **T238** (new; replaces T235) | poller headers **~19:05:32Z, ~19:15:35Z (T7), ~19:25:37Z, ~19:35:40Z, ~19:45:42Z** | Cadence ~602 s. **The last admissible header before 19:45:17Z is ~19:35:40Z.** manual-admit at 19:44:45Z is the only record in between; a result first seen at ~19:45:42Z is T8 (not a final) | info | `round43/report.json` new_facts (6) |
| T227 | **~19:15:35Z** (22:15 MSK), t7_trigger 16748 | T7 trigger (first header ≥ 19:12:17Z). If exp89t is still PENDING: 1 SELECTED read (W386), then send the **R41-A2 T7 text** (a, П3 ticked) | armed | `CONTEXT.md` l.4648-4655 |
| T161 + T221 + W384 | **19:43Z** timer w20960; **19:44:45Z** manual-admit w3028 (orphan); reader fires by **19:47Z** | Comparator check (R39-A4 + W386). The manual-admit result reaches the session only through the W384 reader: first terminal header ≤ 19:45:17Z → code per R41-A2 (≥ 0.960 T2; 0.959 T3KEEP "(после 22:12 МСК)"; ≤ 0.958 T5 late) after 1 SELECTED read; still PENDING or "call FAILED" → one log line, T8 path | armed (reader not armed) | `CONTEXT.md` l.4655-4657; `round43/report.json` R43-A2 |
| T10 | **20:00Z (23:00 MSK)** | Finals tick. **Done: П3** (12:37Z). Re-tick only after exp89t ≥ 0.960. The session never ticks. The user's own "2 of 2 selected" check is the last line of defence (I471) | done unless ≥ 0.960 | `CONTEXT.md` l.4579-4581, l.4617; `round43/report.json` plan_issues (11) |
| T232 | ≥ 20:05Z, optional | One manual kaggle_feed run | optional | `round40/report.json` R40-A5 |
| T222 / T153 / T162 | 20:00-23:59Z; **21:05Z** timer w24260 | Re-selection is allowed until 02:59 MSK. Comparator check (+W386); last-call notify on a mismatch. No submit without the user's yes | armed | `CONTEXT.md` l.4524, l.4549-4558, l.4565-4568 |
| **T239** (new) | any time before 23:59Z | **744250 host answer.** Two open participant questions: "Are private results going to be immediately released at 02:00 UTC?" and "when does submission selection lock? does it also lock at Sep 29, 23:59 UTC?". The only host statement is still Deotte 12:57Z: "It must finish before 23:59 UTC, otherwise it is not eligible nor can we select it." Quote any answer verbatim; the 23:00 MSK tick plan does not change | watch | `round43/report.json` new_facts (2), R43-A6 |
| W382 | only if the user asks, before 20:00Z | The corrected answer lines (decision B cost ≈ 0; never "в лучшем случае ~0.0005"; the harsh K is not a "floor"). **New:** do not cite exp11 LOEO to the user as private-transfer evidence for cap 6 / K / DIS / CI (it validated the score level only), and there is no detector-side hedge partner (public detector-side record 1 up / 8 down) | conditional | `round41/report.json` R41-A8; `round43/report.json` rejected (2), (3) |
| W370 (a) | moot | Arm the mid_<token> save on a slot-2 submit. Slot 2 closes 16:50Z | moot after 16:50Z | `round40/report.json` R40-A7; R43-A7 |
| W177 H2 / T49 | 23:00Z / 23:00-23:45Z | LESSONS H2; the final public LB snapshot (at most 1 call) | pending | `_curation/20/watch.json`; `CONTEXT.md` l.2619 |
| T11 / T163 | **29 Sep 23:59Z** (02:59 MSK 30 Sep) | Deadline. Files must FINISH scoring by then | - | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744250 |
| W19 / W73 / W102 / W93 / W165b / W261 / T196 | standing | ONE poller (header < 15 min); no resubmit of class-C or ERRORed files; SEC only as V_pub; a timeout on every Kaggle call; light polling | standing | `CONTEXT.md` l.3331-3335, l.3692-3703; `memory/feedback-kaggle-api-load.md` |

## LATER (after 29 Sep 23:59Z)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T155 + W376 + **W390** (new; = **R43-A8**) | 30 Sep **00:07Z** (03:07 MSK), timer w21232 | **POST-DEADLINE:** <br>- **(1)** `PYTHONIOENCODING=utf-8 timeout 180 python tools/uptest.py save final_0007Z`; log whether the LB is public or private. <br>- **(2)** 1 read_selected call + 1 submissions list. <br>- **(3)** Stop, if alive, and verify with Get-Process: **37016** (poller; loops forever), orphans 30864, 3028, 32220, waiter 29828, t7 16748, feed-signal 8364, the W384 reader and the W383 watchdog. <br>- **(4)** git add CONTEXT.md, poll.log, ledger.md, **`_lb/e10_20260929T1141Z/`**, `_lb/post_exp89t` / `final_0007Z` if present, `experiments/discussions/`, **`research/wf_ideas_v4/round4*/`**, **`experiments/lb_poll/_admit_subs.*`** if present, `_night_subs.*` (as evidence). <br>- **(5)** Commit as Vitaly Neybauer with **no Co-Authored-By** (the memory rule beats the harness reminder), then push | `round41/report.json` R41-A7; `round43/report.json` R43-A8; `memory/feedback-git-no-coauthor.md` |
| W372 | post-deadline, optional | RESULTS.md l.20 "keep steal off" annotation | `round40/report.json` R40-A9 |
| T216 / T223 / T229 / T233 / T236 + **T240** (new) | post-deadline | Lesson checks: I413 / I423, I419 / I420, T229 (MC П2 vs П3), T233 (audit claim), T236 (the 0.963 cluster). **T240:** did we keep a medal? Silver #199 fell in the 0.957 block and bronze #399 in the 0.955 block at 11:41Z (I468) | `round43/report.json` new_facts (10) |
| W317 / W321 / W326 / W312 / W295 / W29 | post-deadline | Older research follow-ups | `_curation/38/watch.json` |
| T133 / T170 | 3 Oct | GPU quota refresh | `CONTEXT.md` l.4239-4241 |

**Passed or finished time-bound items:**
- **Earlier deadlines:** the R8 new-mechanism cutoff (27 Sep 12:00Z), the 28 Sep 12:00Z consolidation (superseded) and the R8 29 Sep 10:00Z edge all passed.
- **Today:**
  - the tick 12:37Z; decision B 13:34Z; round 40 applied 13:58Z;
  - the default reserve-slot dummy edge 14:10Z;
  - **pre_exp89t killed ~14:48Z; round 41 applied 14:59Z** (l.4643);
  - **15:08-15:54Z network loss; round 42 lost; session restart and re-arm 15:59Z** (l.4668);
  - feed run 15:59:14Z (1 new comment on 744250);
  - round 43 report 16:36Z (not yet applied).
- **Friend replies:** none awaited (`CONTEXT.md` l.2175-2176).
- **Standing notes:**
  - **T156:** 20:00 UTC = 23:00 MSK. Always write the zone.
  - **T204 (corrected):** poller cadence ~602 s (sleep 600 + call), not 5 min.
  - **T205:** LB `LastSubmissionDate` = the max submit time among SCORED files.

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I462** (new) | "watchdog 5024 age check uses newest '===' header INCLUDING '[empty stdout' error headers -> a pure network loss (like 15:19-15:43Z) never trips 'POLL STALE'. It is also one-shot (breaks after first alert; the 15:08Z battery alert ended it before the drop)" | `round43/scan_plancheck.notes.md` l.4 | This is how round 42 died unnoticed. The same blind watchdog is still armed at 16:40Z (W383). |
| **I463** (new) | "Old claude parent 15852 dead -> old jobs' outputs are orphan files ... No notification reaches the new session from them"; "The 19:43Z timer fires 1 min 45 s before manual-admit" | `round43/scan_plancheck.notes.md` l.2; `round43/report.json` R43-A2 | The only record between 19:35:40Z and the edge would go unread (W384). |
| **I464** (new) | "poller header ts is taken BEFORE poll(); a block may have '[empty stdout' in the header AND data from a retry; lastok/t7 skip such blocks -> the waiter may report a LATER header than the first terminal one" (3 of 9 historical error headers carried data) | `round43/scan_plancheck.notes.md` l.5; `round43/report.notes.md` "PC43-03 verified" | A ~10 min late `--hdr` can flip T1↔T2 near 19:12:17Z or into T8 near 19:45:17Z (W389). |
| **I465** (new) | "read_selected.py (<SP>, 14 lines): calls list_submissions directly, no retry (kaggle_feed._retry exists but unused) -> an SSL EOF gives a traceback and no 'SELECTED at' line" | `round43/report.notes.md` "NEW (this report)" | A network blip becomes a false "your pair is wrong" alarm in the last hours (C27, W386). |
| **I466** (new) | "mk_card_1837.py (sha8 a19e1bd6) has no 'ins-tail'/'9.6' string ... round40 ... T1 push text also lacks the footnote"; CONTEXT l.3750 "A CI read with L_hi in (9.6, 10.2] h gets the footnote" vs l.4014 "ins-tail? if L_lo > 9.6 h" | `round43/report.notes.md` "R43-PI-1 verified"; `CONTEXT.md` l.3750, l.4014 | This pre-registered caveat would be silently dropped. Its trigger is written two ways (C30). |
| **I467** (new) | "do not trust the stop job's own 'run_feed_loop' count (it matches its own command line and prints >= 2 even after a clean kill)" | `round43/report.json` R43-A2 (c) | A wrong count could lead to a second kill or a re-arm in the quiet window. Verify by PID (W388). |
| **I468** (new) | "LB snapshot 11:41Z (3 994 teams): silver #199 falls in the 0.957 block (168-234), bronze #399 in the 0.955 block (385-484)"; we are #154 of 4 003, 5th from the bottom of the 0.959 block | `round43/report.json` new_facts (1), (10); `round43/scan_recheck.notes.md` | This is medal context for the post-deadline lesson check (T240). It is not a finals signal. |
| **I469** (new) | 744250: "when does submission selection lock? does it also lock at Sep 29, 23:59 UTC?" is unanswered; host: "It must finish before 23:59 UTC, otherwise it is not eligible nor can we select it." | `round43/report.json` new_facts (2) | A host answer could shorten the re-selection window assumed in T222 ("allowed until 02:59 MSK") (T239). |
| **I470** (new) | CI costs "1.68-2.20 h inside the kernel on same-batch 29 Sep pairs"; exp11 LOEO "validated the score LEVEL (0.906 vs LB probe 1 0.899) and structural stages, not cap 6/K/DIS/CI transfer"; detector-side public record "1 up / 8 down" | `round43/report.json` new_facts (9), rejected (2)-(4); `round43/scan_recheck.notes.md` | Keeps the 9.6 / 10.2 / 10.75 h marks. It stops a wrong argument to the user about private transfer (W382). |
| **I471** (new) | "Residual accepted risk: during a real outage this session is offline too, so no fix gives a live warning; the user's own «2 of 2 selected» check before 23:00 MSK remains the last line of defence." | `round43/report.json` plan_issues (11) | The user should hear this explicitly with the W383 AC request. |
| **I472** (new) | "'slot 2 expired' before 23:59Z (use 'closed unused')"; "'exp87a insertion provably ran (9.48 - 1.68 = 7.80 h)' (say: ran, by the same-base non-CI sibling exp85a L <= 7.19 h ...)" | `round43/report.json` rejected (6) | Wording rules for the W385 CONTEXT line and any user answer. |
| **I473** (new) | "Power: STANDBYIDLE AC/DC 0 (never), HIBERNATEIDLE AC 0" (the laptop does not sleep), yet the 15:08Z switch to battery still cut the network for 45 min | `round43/scan_plancheck.notes.md` l.7; `CONTEXT.md` l.4668-4671 | The risk is the network on battery, not sleep. That is why the ask is AC plus a stable network (T213). |
| I461 (**reconfirmed**) | Test runs leave ready-looking cards: round 43 also "wrote <SP>/card_1837_T3KEEP.txt (simulated hdr 18:20Z) - DELETED by this agent at ~16:16Z" | `round43/scan_hyp_ops43.notes.md` (1) | At 18:37Z build fresh and check the timestamp. No `card_1837_*` file exists at 16:40Z. |
| I453 (**superseded**) | The old header phase (~19:20:37Z T7, ~19:40:4xZ last admissible) | `round41/scan_hyp_evedry41.notes.md` | Replaced by T238 / C24 (19:15:35Z T7, 19:35:40Z last). |
| I452 (open) | "exp87a unrounded ... ~0.95875 -> exp89t needs DIS_pub >= ~+0.00075 ... to display 0.960" | `round41/scan_recheck.notes.md` | **T3KEEP is the most likely read.** |
| I454 / I455 / I456 / I458 (open) | lastok skips error-tagged blocks; a timed-out save leaves a partial `post_exp89t`; cp1251 crashes on Russian prints; lb_poll.py loops forever | `round41/scan_hyp_evedry41.notes.md` | Now covered by R41-A4 (logged l.4662-4667), W389, W390. |
| I448 (open) | `_lb/e10_20260929T1141Z/lb.csv` is still **untracked** | `git status` 16:42Z | It is the only S0 and the card's default `--lb`. Commit it at 00:07Z (W390). |
| I410 / I411 (open) | read_selected.py, t7_trigger.sh, manual_admit.sh, mk_card_1837.py (+ `.59c54168.bak`) live **only in the session scratchpad** | `CONTEXT.md` l.4657-4662, l.4668-4677 | They survived the 15:59Z restart (same session folder). After another restart, re-arm from CONTEXT l.4643-4677 and `round43/report.json`. |
| I459 / I460 / I457 | The 0.963 cluster; "do not log 'floor'"; the stale rank label (now #154, see C29) | `round41/report.json` | See `_curation/41/watch.json`. |
| I450 / I451 | Resolved by R41-A2 / R41-A3 (`CONTEXT.md` l.4648-4662) | - | - |
| I424 / I420 / I423 | "#38 лучше #37 только если ... (P ~0.1–0.2)"; the lab CI sign was wrong; the public division evidence is 1-2 fork events | `round38/report.json` | Post-deadline lessons (T216 / T223). |
| I430-I449 and older | Resolved, in CONTEXT, or moot | `_curation/41/watch.json` ... `_curation/27/watch.json` | - |
