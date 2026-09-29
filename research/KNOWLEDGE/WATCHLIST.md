# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-29 ~18:45 UTC (21:45 MSK), curation 45. This updates the curation-44 build of ~17:45Z (structured copy in `research/KNOWLEDGE/_curation/44/watch.json`). Older predecessors run from `_curation/43/watch.json` down to `_curation/18/watch.json` (there was no curation 42). Rows not repeated here are unchanged there.

**Sources read for this update:**
- **`CONTEXT.md`:** 4,741 lines; `## 9. Literature` starts at l.4721. Three new entries since curation 44:
  - l.4698-4712 (17:54Z): **ROUND 44 APPLIED** (read-time block R44-A2; round 45 = NO-OP R44-A1; rank line R44-A3; feed stopped R44-A4; "Laptop on battery again from 17:43Z ... push not delivered - Remote Control inactive"). Committed in **1ae6716**.
  - l.4713-4716 (18:13Z): **ROUND 45 LAUNCHED AT THE USER'S REQUEST**; R44-A1 is overridden by the user; 0 Kaggle calls by agents.
  - l.4717-4720 (18:37Z): **18:37Z FINALS CARD**: exp89t still PENDING at 18:35:24Z (L_lo 9.59 h); API SELECTED 18:37:20Z = П3, case a; card `card_1837_PENDING.txt` sha8 **2e46a239**. Committed in **2361191**.
- **`research/wf_ideas_v4/round45/report.json`** (18:39Z, untracked, **not yet applied**): **R45-A1..A6**, new_facts (1)-(8), plan_issues (1)-(8), rejected. `report.notes.md` and the scan notes (`scan_plancheck`, `scan_hyp_lasthours45`, `scan_recheck`, `scan_browser`) were read too.
- **`experiments/lb_poll/poll.log`:** newest header **18:35:24Z** (l.33083); exp89t 56669888 **PENDING**; `ledger.md` l.20: "> 9.58 (pending)".
- **`git status`** (session start): `??` `_lb/e10_20260929T1141Z/`, `_night_subs.*`, **`research/wf_ideas_v4/round45/`**.
- **Census 18:41Z** (this curation; Win32_Process, read-only, 0 Kaggle calls):
  - **Alive:** poller 37016; old watcher 29636->30864; manual_admit 29032/13708 + 3028; **watchdog 16220 (wrapper 9596, started 17:43:52Z)**; waiter 9016->29828; t7 34124->6344 + 16748; **reader 1364->19012**; timers 20960 (19:43Z), 24260 (21:05Z), 21232 (00:07Z); orphan sleep 27876.
  - **Gone:** timer 29184/30288 (18:37Z, fired), 30820 (18:13Z, fired), **watchdog v2 30176/16728**.
- **Battery 18:41Z** (this curation, Win32_Battery): **59%, BatteryStatus 1** (on battery). Round 45 measured 69% at 18:14:58Z and 62% at 18:35:00Z, about 21%/h (`round45/report.notes.md`).

All times are UTC. The user thinks in MSK = UTC+3 (`CONTEXT.md` l.3683-3687). IDs are stable: W = action, T = time-bound reminder, I = insight, C = contradiction. Status values: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at ~18:41Z, 29 Sep:**
- **Best display 0.959**, exp87a 56640366 = V_pub.
- **SELECTED = П3 {exp87a 56640366, #37 56563521}**, re-read at 18:37:20Z (`CONTEXT.md` l.4717-4720).
- **Decision B:** exp89t promotes only at **>= 0.960** (l.4607-4617).
- **exp89t 56669888 PENDING** at 18:35:24Z, L 9.585 h. That is past the observed CI band edge of 9.48 h (`round45/report.json` new_facts (1)).
  - Next headers: **~18:45:27Z, ~18:55:29Z**. From 18:55Z on, L_lo > 9.6 h, so a T1 read carries the ins-tail note.
  - **T7:** first clean header >= 19:12:17Z (~19:15:3xZ).
  - **Admit edge:** 19:45:17Z; manual-admit 19:44:45Z.
- **Slot 2:** CLOSED UNUSED (l.4689-4690).
- **Rank** (Chrome 18:16Z, `round45/report.json` new_facts (2)): **#154 of 4,007**. The 0.959 block is #144-#159 and we are 6th from its bottom.
- **Pushes are not delivered** (Remote Control inactive since 17:43Z, l.4711-4712): **the chat is the only channel.**

**Changes since ~17:45Z (curation 44):**
- **Done:**
  - W392's intent is superseded by the user's override (C36).
  - **W394** (rank line) and **T152** (18:37Z card) are done (l.4717-4720, 2361191).
  - **W395 / W397:** round 44 is applied and logged (l.4698-4712, 1ae6716).
- **Partly done:** **W393**: the card event used the block; the read push is still pending.
- **Stale:** R44-A5 (1)'s watchdog PIDs (C38).
- **New:**
  - actions **W398-W404** (= R45-A1..A6, plus bookkeeping);
  - reminders **T244-T248**;
  - contradictions **C36-C40**;
  - insights **I485-I496**.

---

## OVERDUE / DUE NOW

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W398** (new; = **R45-A1**) | **R45 PER-EVENT RULE**, one CONTEXT line (amends R44-A2 "send every pushtext44 line"). <br>**(1)** Send pushtext44 only at: <br>- (i) the **first** event that sees exp89t terminal; <br>- (ii) T7 (PENDING at the first clean header >= 19:12:17Z); <br>- (iii) the admit edge. <br>**(2)** At later events (reader after a read, 19:43Z, 21:05Z), act **only on the `SELECTED case=` line**: <br>- a / b: log only; <br>- a_old / b_old: re-send line 1 only; after 20:00Z, replace its tail by hand with "отметка ещё не сменена — смените до закрытия в 02:59 МСК (23:59 UTC)"; <br>- d: untick/tick steps to П3 {V_pub, #37}; <br>- selok=0: "Не смог проверить" only. <br>**Never send msg44's "SELECTED is neither…" line.** <br>**(3)** Admit edge still PENDING -> **`ADMIT_PENDING=1 pushtext44`** once (for a poller header, replace "ручная проверка" with "поллер" by hand); a later terminal header gets T8; T7 is not re-sent. <br>**(4)** A header with "[ERROR" is an error block; if the T7 header is one, apply T7 at the next clean header. <br>No edits to msg44.py, readtime.sh or mk_card_1837.py | **not started** (CONTEXT has no "PER-EVENT" / "ADMIT_PENDING" text at 18:41Z) | **now**; at the latest before T7 (19:12Z / 22:12 MSK) | `round45/report.json` R45-A1, plan_issues (1)-(3); `round45/scan_plancheck.notes.md` DEFECT 1-3 |
| **W399** (new; = **R45-A2**) | **Battery message in the chat, MSK first.** Re-measure first (skip if back on AC). Text per R45-A2: <br>- charge at time T; <br>- ~21%/h; <br>- hibernate at 2%, **~23:40-00:25 MSK**; <br>- "Подключите зарядку до 23:00 МСК и не закрывайте крышку"; <br>- the 00:05 MSK check may fail and the 03:07 MSK save will not run; the ticked П3 is unaffected; <br>- the exp89t read line comes to the chat. <br>Optional: one local one-shot alert at <= 25% (~20:20Z / 23:20 MSK). **Fresh numbers: 59% at 18:41Z** (this curation), which projects 2% at ~21:25Z (00:25 MSK) | not logged in CONTEXT (not known whether it was sent) | **now** (21:40-21:50 MSK) | `round45/report.json` R45-A2, plan_issues (4); Win32_Battery 18:41Z |
| **W400** (new; = **R45-A3**) | **(a)** If watchdog 16220 prints BACK ON AC before ~19:50Z, re-arm watchdog v2 (battery OR > 25 min without a clean header), local only. **(b)** Amend R44-A5 (1) in CONTEXT: at 00:07Z stop the **current** watchdog **16220/9596** (or its re-arm PID) first, by exact PID; 30176/16728 are gone | (a) conditional; **(b) not started** | (a) on an AC alert before 19:50Z; (b) now | `round45/report.json` R45-A3; census 18:41Z |
| **W401** (new; = **R45-A4**) | CONTEXT line **PRIVATE READ (R45)** (0 calls tonight). After 00:07Z no Kaggle job runs. A read happens only on request or at a morning check: <br>- 1x `competitions submissions ... -v --page-size 100`; **FLIP = privateScore non-empty** for 56640366 or 56563521. <br>- On a flip: 1x `uptest.py save private_<HHMM>Z` + 1x `read_private.py` (a copy of read_selected.py made after 23:59Z). <br>- Drop test vs final_0007Z or the full post_exp75 (N 3,991), **never** e10 lb.csv. <br>- Medal lines 10+floor(0.002N) / floor(0.05N) / floor(0.10N). <br>- Pre-registered private sign pairs (CI, DIS, SEC, stack, anchor). <br>- Flip message template (MSK first) | **not started** | CONTEXT line tonight; reads after 00:07Z on request | `round45/report.json` R45-A4 |
| **W404** (new; bookkeeping) | Log "ROUND 45 APPLIED (R45-A1..A6)" in CONTEXT. `research/wf_ideas_v4/round45/` is untracked; the REPORT_RU text is in `next_focus` (no REPORT.md) | not started | with W398 | `git status`; `CONTEXT.md` l.4713-4720 |
| W385 (moot) | Prompt `biohub-research-round.js` l.20 / l.37 refresh | Prompt still unchanged since 55ec8ab. Round 45 ran on CONTEXT facts. Refresh only if round 46 runs (T248) | before any further round | `round44/scan_plancheck.notes.md`; `CONTEXT.md` l.4698-4712 |
| W126 (part 2) | RESULTS.md rows for probes 47-54 (47: 0.955; 48: 0.957; 49: 0.955; 50: exp85a 0.958; 51: exp87a 0.959; 52: exp89r 0.957; 53: exp75 0.955; 54: exp89p 0.956), then probe 55 (exp89t) | **overdue** (rows end at 46, l.79); the values are in `ledger.md` | low; post-deadline OK | `experiments/RESULTS.md` l.79; `experiments/lb_poll/ledger.md` l.20-26 |
| W336 | One line saying that the user's 08:27Z / 08:28Z instructions override R8's 10:00Z edge (l.1671) | not started; moot | low | `CONTEXT.md` l.1671 |
| W286 / W297 / W202 + W244 / W176 / W177 / W182 / I208 / W57 / W66 / W31 / W72 / W150 / W308 | Older text and cleanup items | overdue, low | post-deadline OK | `_curation/36/watch.json`, `_curation/26/watch.json` |

## CONTRADICTIONS TO RESOLVE BEFORE THEY FIRE

| ID | Conflict | Which text wins | Evidence |
|---|---|---|---|
| **C36** (new) | R44-A1 (round 45 = NO-OP at 18:13Z, l.4699-4701) vs the user's "да сейчас запусти" | **The user.** Round 45 ran 18:13-18:39Z (l.4713-4716). Resolved. W392 is superseded | `CONTEXT.md` l.4713 |
| **C37** (new) | R44-A2 / CONTEXT l.4703-4704 "Send every pushtext44 line except CONTEXT FIRST" at every event vs R45-A1 (push only at first read / T7 / admit edge; later events act on `case=` only). Also, msg44.py hard-codes the exp87a pairs, so a correct re-tick to exp89t prints "SELECTED is neither…" while readtime says case=a | **R45-A1** (W398) once it is logged. Until then the session must apply it from `round45/report.json` by hand; readtime.sh `case=` is authoritative | `round45/report.json` R45-A1; `round45/scan_plancheck.notes.md` DEFECT 1-2 |
| **C38** (new) | R44-A5 (1) / curation 44 W396: "Stop watchdog v2 (30176/16728) FIRST" vs census: 30176/16728 gone; live watchdog = **16220/9596** (17:43:52Z, battery mode; breaks on BACK ON AC or > 25 min without a clean header; no percent alert) | **R45-A3 (b)** (W400): stop 16220/9596 (or its re-arm PID) first | census 18:41Z; `round45/report.json` R45-A3 |
| **C39** (new) | The post-deadline private read: R45-PC-06 (on request, no loop) vs R45-LH-3 (hourly LB download with a zip-name / drop-test trigger) | **R45-A4 default** (on request; privateScore is the trigger); the hourly loop (R45-A5) runs **only on the user's yes** | `round45/report.json` R45-A4, R45-A5, rejected |
| **C40** (new) | `e10_20260929T1141Z/lb.csv` is labelled 3,994 teams (card `--teams 3994`) but holds only **1,006 rows** (top rows, down to 0.953) | Fine for the card (explicit `--teams`); **never** a baseline for N or the private drop test (use final_0007Z or post_exp75, N 3,991) | `round45/scan_hyp_lasthours45.notes.md`; `round45/report.json` plan_issues (6) |
| C32 (updated) | Rank-line denominator | The card used "#154 из 4 005" (R44-A3, l.4710-4711). **In later messages:** "Chrome 21:16 МСК: #154 из 4 007, 6-е снизу в блоке 0.959 (блок до #159)" | `round45/report.json` new_facts (2), rejected (last) |
| C33 (open) | Edge keying: header vs L_hi | Header-keyed (R41-A3); if F >= 1 on the terminal header, also log L_hi (l.4706-4707) | `CONTEXT.md` l.4706-4707 |
| C31 / C34 / C35 | - | **Resolved:** <br>- C31: default `--lb` e10 (l.4705-4706); <br>- C34: Deotte is a participant (`round45/report.json` new_facts (3)); <br>- C35: the 18:13Z timer is superseded by C36 | `CONTEXT.md` l.4698-4716 |
| C30 (partly open) | l.3750 "L_hi in (9.6, 10.2]" vs l.4014 / l.4688 "L_lo > 9.6 h" | **L_lo** (R43-A4). This becomes live from the ~18:55Z header (L_lo > 9.6 h) | `round45/report.json` new_facts (1) |
| C22 / C24 / C25 | Prompt l.20 / l.37 stale | Moot unless a round runs (W385) | `biohub-research-round.js` |
| C15 | Timer texts 19:43Z / 21:05Z say "SELECTED read (read_selected.py)" and push "if not the recommended pair" | **readtime.sh selread** (R44-A2) + R45-A1 (2) | `round45/scan_plancheck.notes.md` |

## NEXT 24 H (29 Sep ~18:45Z -> 23:59Z)

| ID | When (UTC / MSK) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W398 + W399 + W400 (b) + W401 + W404 | **now** (21:45 MSK) | Apply round 45: the per-event rule, the battery message, the stop order, the private-read line, "ROUND 45 APPLIED" | not started | see OVERDUE |
| **T244** (new; replaces T213's AC premise) | now -> 00:07Z | **Laptop is ON BATTERY:** 59% at 18:41Z, ~21%/h, 2% hibernate ~21:25Z (00:25 MSK). <br>- At risk: the 21:05Z (00:05 MSK) check (coin flip) and the 00:07Z (03:07 MSK) save / stop / commit (sure miss). <br>- The watchdog does not alert on percent. <br>- Ask the user to plug in before 23:00 MSK (W399) | **open risk** | `round45/report.json` R45-A2; Win32_Battery 18:41Z |
| W393 (in progress) + W398 + T208 + W344 + W386 + W389 | **each header ~18:45:27, 18:55:29, 19:05:3x Z** ... up to 19:45:17Z | **exp89t read:** <br>- one Bash call per event, `timeout: 600000`; <br>- source readtime.sh on its own line; <br>- HOLD guard (COMPLETE with no score); <br>- **push at the first terminal read only** (R45-A1 (1)). <br>Codes: **>= 0.960 T1** (T2 if header > 19:12:17Z; ins-tail note if L_lo > 9.6 h, i.e. from ~18:55Z); **0.959 T3KEEP**; **<= 0.958 T5**; ERROR T6. Expected: **T3KEEP** (I452). The push goes to the **chat** (pushes are not delivered) | pending | `CONTEXT.md` l.4698-4712; `round45/report.json` new_facts (1) |
| **T245** (new) | ~18:55:29Z (21:55 MSK) | First header with L_lo > 9.6 h: a T1 read then needs the R43-A4 ins-tail note (C30) | info | `round45/report.json` new_facts (1) |
| T227 + W398 (4) | **first clean header >= 19:12:17Z** (~19:15:3xZ / 22:15 MSK), t7_trigger 16748 | T7 if still PENDING: 1 SELECTED read (retry rule) + the R41-A2 T7 text (case a). **An "[ERROR" header is not clean**: wait for the next clean one | armed (16748 alive 18:41Z) | `CONTEXT.md` l.4648-4655; R45-A1 (4) |
| T161 + T221 + W384 + **W398 (3)** | **19:43Z** timer 20960; **19:44:45Z** manual_admit 3028; reader 1364/19012 by **~19:47Z** (22:47 MSK) | 19:43Z: act on `case=` only (W398 (2)). Admit edge: still PENDING -> **`ADMIT_PENDING=1 pushtext44`** ("не прочитан к 22:45"), **not** the T7 text. A terminal read first seen after 19:45:17Z -> T8 | armed (reader alive 18:41Z) | `round45/report.json` R45-A1 (3); `round45/report.notes.md` PC-02 dry run |
| W400 (a) | until ~19:50Z | Watchdog 16220 prints BACK ON AC -> re-arm watchdog v2 (battery OR > 25 min without a clean header) | conditional | R45-A3 (a) |
| T10 | **20:00Z (23:00 MSK)** | Finals tick. **П3 is ticked** (API 18:37:20Z). Re-tick only after exp89t >= 0.960 read by 19:45:17Z. The session never ticks. The user's own "2 of 2 selected" check is the last line of defence (I471) | done unless >= 0.960 | `CONTEXT.md` l.4717-4720, l.4617 |
| **T246** (new) + T242 | after the 23:00 MSK tick is confirmed, once | Tell the user in MSK: <br>- the private result is **one call on request** (W401); <br>- **ask** whether to run the optional hourly private-flip check (**W402** = R45-A5). <br>T242: the laptop may sleep after the tick; watchdog 16220 will alert on battery or AC changes (expected) | not started | `round45/report.json` R45-A4, R45-A5 |
| T222 / T153 / T162 + W398 (2) | **21:05Z** (00:05 MSK) timer 24260 | Last comparator check: act on `case=` only. a_old / b_old -> line 1 with the tail replaced by "смените до закрытия в 02:59 МСК". **At risk if the battery dies** (T244) | armed (24260 alive) | `CONTEXT.md` l.4549-4568; R45-A1 (2) |
| **T248** (new) | optional, before 19:50Z | If round 46 runs (the user allowed rounds): local files + Chrome only, 0 API calls. <br>- (a) check the read push and the card against poll.log; <br>- (b) build the post-deadline helper in the scratchpad (read_private.py only after 23:59Z); <br>- (c) one Chrome look at 744250 before 19:50Z; <br>- (d) battery. <br>**It must not block the 19:12-19:50Z events** | optional | `round45/report.json` next_focus |
| T239 | any time before 23:59Z | 744250: Selina Wu's lock question and kostopr4v's private-release question are still unanswered; Deotte is a participant. Quote any host answer verbatim | watch | `round45/report.json` new_facts (3) |
| W382 | only if the user asks, before 20:00Z | Corrected answer lines (decision B cost ≈ 0, etc.). **Add (R45-A6 (d)):** say "last API SELECTED read 18:37:20Z", not "confirmed" | conditional | `round41/report.json` R41-A8; `round45/report.json` R45-A6 (d) |
| W177 H2 / T49 | 23:00Z / 23:00-23:45Z | LESSONS H2; the final public LB snapshot (at most 1 call) | pending | `_curation/20/watch.json`; `CONTEXT.md` l.2619 |
| T11 / T163 | **29 Sep 23:59Z** (02:59 MSK 30 Sep) | Deadline. Files must FINISH scoring by then | - | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744250 |
| W19 / W73 / W102 / W93 / W165b / W261 / T196 / T228 | standing | ONE poller; no resubmit; SEC only as V_pub; a timeout on every Kaggle call; light polling; quiet window 17:30-20:00Z (agents make 0 API calls) | standing | `CONTEXT.md` l.3331-3335, l.3692-3703, l.4715; `memory/feedback-kaggle-api-load.md` |

## LATER (after 29 Sep 23:59Z)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T155 + W376 + W390 + W396 + **W400 (b)** | 30 Sep **00:07Z** (03:07 MSK), timer 21232 (alive 18:41Z) | **POST-DEADLINE:** <br>- **(1)** `PYTHONIOENCODING=utf-8 timeout 180 python tools/uptest.py save final_0007Z`; log public vs private. <br>- **(2)** 1 read_selected call + 1 submissions list (**`--page-size 100`**, I488). <br>- **(3)** Stop, each by exact PID: <br>&nbsp;&nbsp;- **watchdog 16220/9596 FIRST** (not 30176/16728, C38); <br>&nbsp;&nbsp;- then poller 37016; <br>&nbsp;&nbsp;- old watcher 29636/30864; <br>&nbsp;&nbsp;- manual_admit 3028 (+29032/13708); <br>&nbsp;&nbsp;- waiter 9016/29828; <br>&nbsp;&nbsp;- t7 16748 (+34124/6344); <br>&nbsp;&nbsp;- reader 1364/19012. <br>- **(4)** git add CONTEXT, poll.log, ledger, `_lb/e10_20260929T1141Z/`, `_lb/final_0007Z`, `experiments/discussions/`, `research/wf_ideas_v4/round44/` + **`round45/`**, `_night_subs.*`. <br>- **(5)** Commit as Vitaly Neybauer, **no Co-Authored-By** (the memory rule beats the harness reminder); push. <br>**Needs AC power** (T244) | `round44/report.json` R44-A5; `round45/report.json` R45-A3; `memory/feedback-git-no-coauthor.md` |
| **W401** (reads) + **W402** (new; = R45-A5, **awaiting user**) | after 00:07Z | Private read on request (W401). Optional hourly flip check **only on the user's yes**: at :07 each hour until 06:07Z, then every 3 h until 30 Sep 18:07Z; <= ~12 calls; stop at the first flip | `round45/report.json` R45-A4, R45-A5 |
| **T247** (new) | 30 Sep, on the first flip | Record the pre-registered private sign pairs; \|Δ\| < 0.001 = unresolved: <br>- **CI** = exp75 56656157 vs #37 56563521; <br>- **DIS** = exp89t 56669888 vs exp87a 56640366; <br>- **SEC** = exp89r 56656147 vs exp89t; <br>- **stack** = exp87a vs #37; <br>- **anchor** = x138 probe 34 56545267. <br>Compare with the 13:21Z risk-audit MC | `round45/report.json` R45-A4 |
| **W403** (new; = R45-A6) + T243 | post-deadline write-up | Wording: <br>- **(a)** DIS private sign unknown, about −0.003..+0.0007 (in-sample depletion); not a structural lever; <br>- **(b)** I-384: the IB29-06 sub-form is CLOSED by probe 54; the original N1 is "trigger did not fire"; <br>- **(c)** FLOW_Z_WEIGHT: 0.6 / 1.5 refuted, 0.85 untested but predicted inert; <br>- **(d)** "last API SELECTED read", not "confirmed". <br>Plus the T243 RC-A/B/C lines | `round45/report.json` R45-A6; `round44/report.json` R44-A5 (3) |
| W372 | post-deadline, optional | RESULTS.md l.20 "keep steal off" annotation | `round40/report.json` R40-A9 |
| T216 / T223 / T229 / T233 / T236 / T240 | post-deadline | Lesson checks (I413 / I423, I419 / I420, MC П2 vs П3, audit claim, the 0.963 cluster, medal lines: N ~4,005 -> 18 / 200 / 400) | `round43/report.json` new_facts (10); `round45/scan_hyp_lasthours45.notes.md` |
| W317 / W321 / W326 / W312 / W295 / W29 | post-deadline | Older research follow-ups | `_curation/38/watch.json` |
| T133 / T170 | 3 Oct | GPU quota refresh | `CONTEXT.md` l.4239-4241 |

**Passed or finished time-bound items:**
- **Earlier deadlines:** the R8 cutoff (27 Sep 12:00Z), consolidation (28 Sep 12:00Z) and the R8 edge (29 Sep 10:00Z) all passed.
- **Today:**
  - tick 12:37Z; decision B 13:34Z; round 43 applied 16:43Z; slot 2 closed ~16:50Z; round 44 17:13-17:37Z;
  - **round 44 applied 17:54Z** (1ae6716);
  - **the 18:13Z timer fired; round 45 ran 18:13-18:39Z** at the user's request;
  - **18:37Z card sent: PENDING, case a**, sha8 2e46a239 (2361191).
- **Friend replies:** none awaited (`CONTEXT.md` l.2175-2176).
- **Standing notes:**
  - **T156:** 20:00 UTC = 23:00 MSK.
  - **T204:** poller step ~10:02.
  - **T205:** LB `LastSubmissionDate` = the max submit time among SCORED files.

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I485** (new) | "msg44.py l.16-17, 25-31: A/B pair sets are hard-coded to exp87a ... After a T1/T2 promotion AND a correct user re-tick ... pushtext44 prints 'SELECTED is neither…' while readtime.sh prints 'SELECTED case=a'" | `round45/scan_plancheck.notes.md` DEFECT 1 | A false "wrong pair" alarm after a correct re-tick is the worst possible message at 22:43-23:00 MSK. Only W398 (2) prevents it; not in CONTEXT yet |
| **I486** (new) | "'ADMIT_PENDING' appears nowhere in CONTEXT.md or round44/report.json"; without it, at 19:44:45Z "msg44 prints the T7 text 'основным станет, только если ... прочитается до 22:45 МСК' at 22:44-22:45 MSK (contradictory after the edge)" | `round45/scan_plancheck.notes.md` DEFECT 2-3; `round45/report.notes.md` PC-02 dry run | The flag lives only in round notes. It does not persist between Bash calls (`report.notes.md`: "flag does not persist after the call") |
| **I487** (new) | "readtime keys on the FIRST terminal header, so pushtext44 re-emits the same read push (e.g. T3KEEP ...) -> duplicate messages" | `round45/scan_plancheck.notes.md` DEFECT 2 | Repeated "ничего менять не нужно" pushes at 19:43Z / 19:47Z / 21:05Z; W398 (1)-(2) |
| **I488** (new) | "CLI -h: --page-size default 20, max 200"; "the poll block reaches back only to probe 27" | `round45/report.notes.md`; `round45/report.json` new_facts (7) | The post-deadline full submissions read needs `--page-size 100` or it misses every probe older than probe 27 (T247 sign pairs themselves are all within the default page) |
| **I489** (new) | "all saved zips say 'publicleaderboard'; kagglesdk ApiDownloadLeaderboardRequest has no public/private switch"; "the download may keep serving the public board; privateScore is the trigger" | `round45/report.json` R45-A4, rejected | A post-deadline LB download can look "final" while still public; never announce a private rank from it without the privateScore flip or the drop test |
| **I490** (new) | "_lb/e10_20260929T1141Z/lb.csv has 1 006 rows (top 1006, ends at 0.953), not 3 994" | `round45/scan_hyp_lasthours45.notes.md` | C40: never use it as a baseline for N, medal lines or the drop test |
| **I491** (new) | "ILP forks are NOT output (motion relink replaces raw edges ...); output forks come from safe divisions l.2017 + DaughterNet insertion"; "Fork-vs-new-start margin = T-S = Div-A (0.4, DIS-invariant)" | `round45/scan_recheck.notes.md` | This explains why ILP division knobs move the score only through the node set and the readmit. Useful for the write-up (W403); not in CONTEXT |
| **I492** (new) | "DIS-removed 1,812 -> 4 near GT vs 28.3 expected ... ~7x depletion", refuted on value as "an in-sample selection effect (detector trained on these clips)"; private range "-0.003..+0.0007" | `round45/scan_recheck.notes.md`; `round45/report.json` rejected, R45-A6 (a) | Do not quote the 7x depletion as evidence that DIS helps on private |
| **I493** (new) | "push not delivered - Remote Control inactive" (17:43Z); "Chat is the only channel (pushes not delivered since 17:43Z)" | `CONTEXT.md` l.4711-4712; `round45/report.json` R45-A2 | Every read / T7 / admit message must be written in the chat; the user must look at the chat before 23:00 MSK |
| **I494** (new) | "Watchdog 16220 ... loop: break on BatteryStatus != 1 (BACK ON AC) or clean-poll age > 25 min; no percent check" | `round45/report.notes.md` | A dying battery gives no alert; hibernation silently kills the 00:05 / 03:07 MSK jobs (T244) |
| **I495** (new) | "Orphan sleep.exe 27876 (sleep 5400, created 17:29:24Z, parent 24672 GONE) = leftover of the stopped feed loop; ends ~18:59Z with no parent -> no Kaggle call. Harmless." | `round45/scan_plancheck.notes.md` | Do not kill it or mistake it for a live feed loop (alive at 18:41Z census) |
| **I496** (new) | "PENDING card text 'обычно 9,3–9,5 ч' is already past its range at 18:37Z"; L 9.585 h is "past the observed CI band edge 9.48 h" | `round45/report.json` plan_issues (8), new_facts (1) | exp89t is in the tail. A read after 19:12:17Z is T2 (re-tick in < 50 min) and after 19:45:17Z T8. Raises the chance of the late paths |
| I474 (open) | HOLD guard: COMPLETE with an empty score -> no push; the awk still picks the scoreless row | `round44/report.notes.md` | Still needed at every read (W393) |
| I475 / I477 / I478 (open) | No `msg` function; no pipe around `source`; tool `timeout: 600000`; `timeout 90` on selread | `round44/*` | Rules of the read-time block (CONTEXT l.4702-4705) |
| I471 (open) | "the user's own «2 of 2 selected» check before 23:00 MSK remains the last line of defence" | `round43/report.json` plan_issues (11) | Say it with any read push before 20:00Z |
| I452 (open) | "exp87a unrounded ~0.95875 -> exp89t needs DIS_pub >= ~+0.00075 to display 0.960" | `round41/scan_recheck.notes.md` | **T3KEEP is the most likely read** |
| I448 (open) | `_lb/e10_20260929T1141Z/` is still **untracked** | `git status` 18:40Z | Commit at 00:07Z (W396) |
| I410 / I411 (open) | read_selected.py, t7_trigger.sh, manual_admit.sh, mk_card_1837.py, `r44dry/readtime.sh`, `msg44.py`, `cardfix44.py` live **only in the session scratchpad**; the sha8s match at 18:35Z (befef6fb, 233e5ba5, af903431, a19e1bd6) | `round45/report.notes.md`; `CONTEXT.md` l.4702-4703 | After a restart, re-arm from CONTEXT l.4643-4720 and `round45/report.json` |
| I481 (open) | The Chrome MCP tab group is churned by another client (seen in r44 and r45) | `round45/report.json` new_facts (8) | Do not rely on an MCP tab persisting (T49, T248 (c)) |
| I476 / I479 / I480 / I482 / I483 / I484 | pushtext44 line rules; the F=2 window; Deotte is a participant; the watchdog stop order; CI near pairs; LB movers | `round44/*` | **Superseded or refined** by I485-I487 (W398), C38 (stop order), C32 (4,007) |
| I424 / I420 / I423 / I468 / I470 / I472 / I473 | Post-deadline lessons | `round38/report.json`, `round43/report.json` | T216 / T223 / T240 |
| I430-I467 and older | Resolved, in CONTEXT, or moot | `_curation/44/watch.json` ... `_curation/27/watch.json` | - |
