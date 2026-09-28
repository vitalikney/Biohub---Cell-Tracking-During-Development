# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-28 ~16:25 UTC (curation 27). This updates the curation-26 build of 28 Sep ~14:00Z (full text in the git history of this file; structured copy `research/KNOWLEDGE/_curation/26/watch.json`). Older predecessors: `_curation/25/watch.json`, `_curation/24/watch.json`, `_curation/23/watch.json`, `_curation/22/watch.json`, `_curation/21/watch.json`, `_curation/20/watch.json`, `_curation/18/watch.json`. Rows not repeated here are unchanged there. The TASK_LOCAL_SESSION, TASK_CLOUD_SESSION and v3 FINAL_REPORT rows have not changed since `_curation/20/watch.json`.

**Sources read for this update:**
- `CONTEXT.md` has 4,019 lines, and `## 9. Literature` starts at l.3999. These entries are new since curation 26 (l.3924-3998):
  - 14:12Z entries:
    - R8 COVERAGE EXTENDED TO THE NIGHT FILES (l.3924);
    - MORNING TABLE v1.1 (l.3931);
    - exp89s BUILT + GATE (l.3956);
    - EXP75 PARTNER RULE v2 (l.3965).
  - 14:40Z: **exp89s gate PASS** (l.3974).
  - 15:43Z: OPS "network outage", loops restarted, round 27 launched, **user defaults applied** (l.3979).
  - 15:57Z: **KAGGLE BAN REPORT (elsewhere), so the API load was cut** (l.3988).
- `git log`: dba59bd, eea3793, 7faa8cf and 608d950 are new (the last one is 18:57 local = 15:57Z). `git log -15 --format=%b | grep -ci co-author` = 0.
- `git status` 16:18Z: `research/wf_ideas_v4/round27/` untracked; round 26 is now tracked (`git ls-files research/wf_ideas_v4/round26`).
- `research/wf_ideas_v4/round27/report.json` (written 16:16Z) holds **R27-A1..A9** and plan_issues 1-12. Also read:
  - `report.notes.md` and `finals_card_v4_ru.md`;
  - scan notes: `scan_plancheck.notes.md`, `scan_hyp_nightdry.notes.md`, `scan_hyp_card.notes.md`, `scan_recheck.notes.md`, `scan_browser.notes.md`.
- `experiments/lb_poll/poll.log`:
  - newest header **16:12:02Z** (l.23749); 56640366 (probe 51) PENDING (l.23752);
  - the 15:15:31Z header is the NameResolutionError (l.23505).
- Loops:
  - `experiments/e10_watch/watch_loop.log`: RUN 27 15:43:14Z, signals 0.
  - `experiments/discussions/feed_loop.log`: 15:57:02Z, 15 topics, 0 new, E10 FLAG none. The feed now runs every 90 min (l.3993-3996).
- Local read-only check 16:19:43Z: `Win32_Battery` BatteryStatus **1 (on battery), 53%**.
- File checks 16:20Z:
  - `tools/runtime_ledger.py` l.82 now reads `exp89[abcghilmnort]`;
  - `experiments/RESULTS.md` probe rows still end at probe 46 (l.79);
  - `ls research/wf_ideas_v4/round2*/REPORT.md` = rounds 20-23 only;
  - `ls tools | grep gate` = `division_gate_funnel.py`, `dummy_gates.py`, `e10_port_gate.py` (no `gate_dummy.py`);
  - `ls experiments | grep exp89` = a, e, p, q, r, s (no l/t/u);
  - `grep "GAP RULE v2\|RULE v2.1\|Modern Standby\|FINALS CARD v4" CONTEXT.md` = 0 hits.

All times are UTC. The user thinks in MSK (UTC+3) (`CONTEXT.md` l.3683-3687). IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at 16:25Z, 28 Sep:**
- **Best display 0.958:** exp85a (probe 50, 56629533, non-CI). V_pub = exp85a.
- **Rank:** #138 of 3,968 at 15:43Z, 14th of 21 in the 0.958 block, 124 teams >= 0.959 (`round27/report.json` new_facts 2). It was #134 before.
- **Probe 51 exp87a (56640366):**
  - PENDING at 16:12:02Z (`poll.log` l.23752).
  - Earliest read ~20:50Z; expected 21:30-22:15Z.
  - **'?' threshold L_hi 10.2 h = 22:26:57Z** (`round27/report.json` new_facts 1).
- **28 Sep slots:** 5 of 5 used. Any submit before 00:00Z fails on the daily limit (`round27/scan_hyp_nightdry.notes.md`).
- **Night, 29 Sep:**
  - 00:05Z: exp89r (branch A) or exp89q (branch B).
  - 00:06Z: exp75.
  - 00:46Z: exp89p.
  - Fallback: exp89p fail -> exp83c.
  - All eight night/fallback kernels are COMPLETE at version 1 with no NEVER_SUBMIT (`round27/report.json` new_facts 7).
- **Morning:** MORNING TABLE v1.1 (`CONTEXT.md` l.3931-3955). **exp89s PASSED** (l.3974-3978). exp89l is built only in branch A, at probe 51's read.
- **User defaults** (the user wrote "продолжи" without answers, l.3984-3986): no exp89t, no exp89u; the depth-cap reading for {K, SEC, DIS 2.25, CI} stands.
- **GPU:** 9,988.9 s of 21,600 s used at 15:44Z, **~3.2 h left**, refresh 3 Oct. Read via kagglesdk `get_accelerator_quota_statistics` (`round27/report.json` new_facts 8). Not yet in CONTEXT (W279 (2)).
- **POWER RISK (new, top priority):**
  - The laptop is on battery: 64% at 15:49Z -> 57% at 16:08Z -> **53% at 16:19:43Z**, ~22%/h, so it can be **empty ~18:40-18:45Z (21:40 MSK)**.
  - The 15:05-15:35Z "network outage" was Modern Standby on battery with the lid closed (`round27/report.json` new_facts 5; `round27/scan_plancheck.notes.md` 15:48Z). The CONTEXT line (l.3979-3983) is wrong.
  - Standby kills the poller, the loops, the probe-51 waiter and every session cron: freeze 5ece5d24, batch 2ab38c73.
- **API load:** cut after a Kaggle ban report elsewhere. Feed every 90 min with 12 topics; kernel waiters every 5 min; no new pollers (l.3988-3997).
- **Finals:** #37 + #38 are ticked. **Only the user ticks, by 20:00Z (23:00 MSK) 29 Sep.** The session never ticks (l.3851-3855).

**Changes since ~14:00Z (curation 26):**
- **Done:**
  - W262 (R8 coverage, l.3924-3930);
  - W263 (MORNING TABLE v1.1, l.3931-3955);
  - W264 (1) exp89s built (l.3956-3964), gate PASS (l.3974-3978);
  - W264 (2) ledger `t` and test (l.3962-3963; `tools/runtime_ledger.py` l.82);
  - W266 (1) partner rule v2 (l.3965-3973);
  - W267: the message was sent; the user said "продолжи", so the defaults apply (l.3984-3986);
  - W269: GPU measured (`round27/report.json` new_facts 8);
  - W261 (checks):
    - dataset baseline at 14:12Z (l.3957-3958);
    - ref/size/lastUpdated at 15:47Z (`round27/report.json` new_facts 7);
  - T157: round 27 ran at 15:44Z instead of 15:17Z (l.3982-3983).
- **Superseded:**
  - W268 -> **W279** (3), the KEY FACTS refresh for round 28.
  - T160 (a separate 19:30Z job) -> **W277** (1), folded into cron 58b6ded3 at 19:43Z.
  - I306 is **RETIRED: WRONG** (R27-A3 (1)): DIS 2.25 adds no runtime.
- **New:**
  - actions **W271-W280**;
  - reminders **T164-T170**;
  - insights **I315-I326**.

---

## OVERDUE / DUE NOW

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W271** (new; = **R27-A1**) | **POWER.** **(a)** ONE Russian message, MSK first, with the R27-A6 questions (W272). Wording is in `round27/report.json` R27-A1. Fill in the current % (53% at 16:19:43Z by a local read). Ask for: the charger now and until 23:00 MSK 29 Sep, the lid open, and an optional LIDACTION command that the user runs. **(b)** A CONTEXT line correcting the 15:43Z OPS entry: Modern Standby on battery with the lid closed (Kernel-Power 14:59:00Z enter Lid; 15:15:31Z brief wake; 15:39:48Z exit Lid), not DNS. **(c)** A notify-only watchdog every 30 min until 29 Sep 20:00Z: Win32_Battery plus the age of the newest poll.log header. It pushes (PushNotification) if still on battery after 16:45Z, below 40%, below 20%, or if the header is > 25 min old. **(d)** A BatteryStatus = 2 check at 23:25Z and 00:03Z. The session never changes power settings itself | **not started** (`grep "Modern Standby" CONTEXT.md` = 0; newest entry 15:57Z) | **NOW**; the message must go before ~18:00Z (21:00 MSK) | `round27/report.json` R27-A1, new_facts 5, plan_issues 1; `round27/scan_plancheck.notes.md` 15:48Z-16:02Z |
| **W272** (new; = **R27-A6**; covered_by_existing_approval **false**) | In the same message: **(i)** run a "не засыпать" process (SetThreadExecutionState) until 23:00 MSK 29 Sep? Default NO; it does not help against a closed lid. **(ii)** In branch A, send exp89p at 03:07 MSK (00:07Z) instead of 03:46? Default 03:46. Do NOT ask PC27-07 (exp89s instead of exp75) or about SEC in П1 | not started | ask now; answers needed before 23:30Z (02:30 MSK); no answer = defaults | `round27/report.json` R27-A6, plan_issues 11 |
| **W273** (new; = **R27-A2**) | **PRE-SCORE "GAP RULE v2"**, quoting the newest poll header with 56640366 PENDING. '+'/'0u' with L_hi > 10.2 h -> UNPROVEN-ins (a normal read; ins-tail? if L_lo > 9.6 h). '0'/'-' with L_hi > 10.2 h -> '?' (no C51 '-', no CI-risk flag). While 51 is UNPROVEN-ins it is not a morning comparator. Tighten L_hi from the hourly e10 snapshots (SubmissionCount 52 -> 53). Same asymmetry for exp89r, exp75 (the B >= 0.955 row) and exp89l. Operational: no 3-min tight-poll loop; no poller restart 21:00-22:30Z unless the header is > 15 min old | not started (`grep "GAP RULE v2"` = 0) | **before 51 can turn terminal: earliest ~20:50Z** (23:50 MSK) | `round27/report.json` R27-A2, plan_issues 2 |
| **W274** (new; = **R27-A3**) | **(1)** A CONTEXT fact correction: round-26 fact 6 ("DIS 2.25 dummies +15-20%") is WRONG. The excess is the pre-GPU rglob I/O phase (203-788 s on any config). Compute after 'GPU shard 0' is equal (89q/89p 1,057/1,059 s; 89s/85a 1,130/1,126 s; 89r/87a 1,473/1,569 s). So exp89q L ~ exp85a L and exp89r L ~ exp87a L. Do not patch the rglob in gated files. (WATCHLIST I306 retired here.) **(2)** PRE-SCORE **"RULE v2.1"** before the exp89l dummy push: compute = last log time - 'GPU shard 0'; PASS if whole-kernel <= 2,100 s OR compute <= 1.10 x the nearest same-CI-family dummy (CI: exp89r 1,473 s -> <= 1,620 s); log setup and compute separately | not started (`grep "RULE v2.1"` = 0) | (1) next CONTEXT log; (2) before any exp89l push (branch A, earliest ~20:50Z) | `round27/report.json` R27-A3, new_facts 6, plan_issues 3 |
| **W279** (new; = **R27-A9**) | **(1)** Before 07:23Z: log RC-C: "DET_THRESHOLD stays closed for 29 Sep and is never a morning filler". **(2)** A round-27 facts line: rank 138; E10 null; no knob disclosed; GPU 9,988.9 of 21,600 s at 15:44Z; 51 expected ~20:50-22:15Z. **(3)** Refresh KEY FACTS in the round-28 task text: rank 138; battery/lid risk and charger status; GAP RULE v2; RULE v2.1; the API-load cut; DIS runtime = sibling; exp89t/exp89u default no. (This curation task text is also stale: it still names the passed R8 27 Sep and 28 Sep 12:00 examples.) | not started | (2)(3) **before round 28 at 17:47Z**; (1) before 07:23Z 29 Sep | `round27/report.json` R27-A9 |
| **W278** (1) (new; = **R27-A8**, first sentence) | Log "FINALS CARD v4 stored (research/wf_ideas_v4/round27/finals_card_v4_ru.md), fill at 12:03Z / 18:37Z by its table" | not started (`grep "FINALS CARD v4"` = 0) | now | `round27/report.json` R27-A8 |
| **W280** (new; extends W246/W257) | Write `research/wf_ideas_v4/round27/REPORT.md` from `report_md_ru` (the harness refused the subagent's write). Rounds 24-26 REPORT.md are also still missing. Commit round 27 with named paths only, as the user, with no Co-Authored-By; never `git add -A` | not started (REPORT.md exists for rounds 20-23 only; round27 untracked) | with the next CONTEXT commit | `round27/report.json` plan_issues 12; `round27/report.notes.md` 16:14:42Z; `memory/feedback-git-no-coauthor.md` |
| W126 (part 2) | RESULTS.md rows for probes **47 (0.955), 48 (0.957), 49 (0.955), 50 (0.958)**; later 51 and the night probes | **overdue** (probe rows end at 46, `experiments/RESULTS.md` l.79) | before the finals card (29 Sep 12:03Z) | `CONTEXT.md` l.3530, l.3615, l.3639, l.3856 |
| W238 (residue) | `tools/gate_dummy.py` is still missing (gate scripts live in the scratchpad). The scratchpad script still flags at the old 1,900 s threshold; RULE v2.1 (W274 (2)) needs a compute split | in progress, low | before the exp89l gate | `CONTEXT.md` l.3920; `ls tools` 16:20Z |
| W202 + W244 | Info/curator lines R22-A9 (a)-(h); R24-A10 (a)-(f) (incl. I278 at l.3510) | not started | today, low | `_curation/26/watch.json` |
| W176 / W177 / W182 | ROUND 14-27 RECORD; LESSONS H1; no `NEVER_SUBMIT.md` in exp70j/exp70k | overdue, low | H1 now; H2 29 Sep 23:00Z | `_curation/24/watch.json` |
| I208 / W57 / W66 / W31 / W72 / W150 | Old low-priority text fixes | overdue, low | passed | `_curation/20/watch.json` |

## NEXT 24 H (28 Sep 16:25Z -> 29 Sep 16:25Z)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W271, W272, W273, W274 (1), W278 (1), W279 (2) | **now** | Power message + questions, OPS correction, watchdog, GAP RULE v2, DIS fact correction, card-stored line, facts line | not started | R27-A1, A2, A3, A6, A8, A9 |
| **T168** (new) | **~18:40-18:45Z** (21:40 MSK) worst case; Windows estimate ~23:40Z | **Battery empty** at ~22%/h (53% at 16:19:43Z). That is before 51's read and before the 00:04Z batch. Watchdog pushes: < 40% (~17:00Z), < 20% (~17:50Z) | live risk | `round27/report.notes.md` 16:08:47Z; local Win32_Battery read 16:19:43Z |
| **T164** (new) | **17:47Z** (20:47 MSK) | **Round 28 checks:** BatteryStatus = 2, and did the watchdog push; poll header age; W273 and W274 (2) logged pre-score with a PENDING header; the DIS fact corrected; the user's answers to W272; E10/feed only if the newest digest is > 100 min old | scheduled (session cron; lost if in standby) | `round27/report.json` next_focus |
| T19 / W77 | 17:57Z | Tick check: API SELECTED still #37 + #38. Not in the 15:50Z cron list | at risk (W270) | `CONTEXT.md` l.2365; `round27/scan_plancheck.notes.md` 15:50Z |
| **T165** (new) | **~20:50Z earliest; 21:30-22:15Z expected** (00:30-01:15 MSK); **'?' threshold 22:26:57Z** | **Read probe 51** under R25-A1 + GAP RULE v2 (W273): '+' >= 0.959 or '0u' -> branch A (exp89r at 00:05Z), and build exp89l (cad1d47f) + dummy under RULE v2.1 (T158, W274 (2)); '0' = NON-ADDITIVE; '-' -> branch B (exp89q) + CI-risk flags; not terminal by the freeze -> exp89q. UP test S0/S1 with e10 snapshots as backup. Update RESULTS (W126). Replaces T148's timing | pending (PENDING 16:12:02Z) | `round27/report.json` new_facts 1, R27-A2; `CONTEXT.md` l.3863-3870, l.3899-3904 |
| T158 | at 51's read, branch A only | exp89l build + coverage line (secFT + coordinject, V_pub only); STOP unless sha8 = cad1d47f; gate vs the exp89r dummy under RULE v2.1 (not rule v2). exp89t/exp89u are off (user defaults) | pending | `CONTEXT.md` l.3945-3947, l.3963-3964, l.3984-3986; `round27/report.json` R27-A3 (2) |
| **T166** (new) | **20:17Z** round 29; **22:47Z** round 30 | Round 29: the 51 read + branch; round 30: the freeze bundle (W275-W278). There is **no 01:17Z round** in the cron; the 01:30Z backup cron replaces it (W276) | scheduled | `round27/report.json` next_focus, plan_issues 6; `round27/scan_plancheck.notes.md` 15:50Z |
| T100 | E10 hourly at hh:41Z until 29 Sep 12:00Z; feed **every 90 min** (was 30) until 29 Sep 23:59Z | E10 v3 watch, trigger **>= 0.959**. Standing override: build + dummy at once and propose the swap; after 02:00Z an E10 copy needs the user's yes | live (RUN 27 15:43Z; feed 15:57Z) | `CONTEXT.md` l.3904-3907, l.3993-3996; `experiments/e10_watch/watch_loop.log` |
| **T143** + W265 + **W275** (new; = **R27-A4**) + **W277** (2) + **W278** (Q3 line) | **23:30Z** (02:30 MSK; freeze cron 5ece5d24 at 23:33Z) | **W4 FREEZE LINE** = R27N-2's text (`round27/scan_hyp_nightdry.json` id R27N-2) with its <> fields filled, plus: item (1) GAP RULE v2; item (4) exp89p 00:46Z both branches unless W272 (ii) = yes; "under C51 '-', exp75 is still submitted at 00:06Z"; item (7) (a) no freeze line -> code 51 from headers <= 23:30Z only, no COMPLETE -> exp89q, a later read never changes the variant, (b)-(e) LATE rules; item (8) AC power + GPU via the API; the fact "exp89q L = exp85a L, exp89r L = exp87a L". R26-A4 (a)-(e) still applies. **W277 (2):** morning files are submitted at their decision header, not at the cutoff. **W278:** the Q3 conditional line ("If V_nonCI carries SEC and is not V_pub, П1 uses the best SEC-free non-CI file (exp85a or exp89s)") | pending | `round27/report.json` R27-A4, R27-A7 (2), R27-A8; `round26/report.json` R26-A4 |
| **W276** (new; = **R27-A5**) + **T167** (new) | at the freeze (23:30Z); batch **00:04Z**; backups **00:20Z, 00:50Z, 01:30Z** (MSK '20 3 29 9', '50 3 29 9', '30 4 29 9') | Replace cron 2ab38c73's prompt with R27N-3's checklist G0-G5 (`round27/scan_hyp_nightdry.json` id R27N-3). G3 dataset diff on ref,size,lastUpdated only; empty = NETWORK, not STOP. Every submit goes through R27N-4's `nb_try`; **limit/allowance/daily output -> exit 3 = STOP, push, never the exp83c fallback**. After 20 min without success push the Russian text and retry every 10 min until LATE. Create the three backup one-shot crons. At 00:03Z check AC power + `nslookup api.kaggle.com` | not started | `round27/report.json` R27-A5, plan_issues 5-7 |
| T126 | 29 Sep 00:00Z | Slot reset (5 new slots) | - | `CONTEXT.md` l.3367 |
| T20 / T107 | **29 Sep 00:04Z cron; 00:05 / 00:06 / 00:46Z** (00:07Z for exp89p only on W272 (ii) yes) | **Night batch:** stack exp89r or exp89q; exp75 (v1, never re-push); exp89p; fallback exp83c only on an exp89p file-specific failure. -m starts with the file token | pending | `CONTEXT.md` l.3899-3907; `round27/report.json` R27-A4, R27-A5 |
| T159 | 29 Sep: exp89q **~07:02-07:45Z**; exp89p **07:38-08:35Z** (00:46Z) or 07:00-07:56Z (00:07Z); exp75 **~09:04-09:49Z**; exp89r **09:21-09:32Z** (tail 11:00Z) | **Night reads**, coded per MORNING TABLE v1.1 (1) and R26-A4 (a); UP tests per R26-A4 (b). DIS files use parent-family windows (R27-A3 (1)) | pending | `round27/scan_hyp_card.notes.md` (PENDING arithmetic); `round27/scan_hyp_nightdry.notes.md` |
| T151 + W277 (2) | 29 Sep **07:23Z** prep. Latest times: A-M1 CI 08:45Z (decide by the 08:40Z header); B-M1 decide by the 10:30Z header, submit by 10:50Z; M2 by 11:30Z | **Morning batch (<= 2 files)** from MORNING TABLE v1.1 (l.3931-3955). **Submit at the decision header**, not the cutoff. Expected reads: A-M1 ~16:55-17:57Z, A-M2 ~16:20-17:15Z, B-M1 ~15:25-16:15Z. UNUSED is the default. Only PASSED dummies (exp89s PASSED l.3974; exp89q PASSED l.3915) | pending | `CONTEXT.md` l.3931-3955; `round27/report.json` R27-A7 (2) |
| W279 (1) | before **07:23Z** | Log the DET_THRESHOLD-closed line (RC-C) | not started | `round27/report.json` R27-A9 (1) |
| W266 (2) + **W278** (2) | edits before **12:03Z** (15:03 MSK); send at 12:03Z | **FINALS CARD v4** (`research/wf_ideas_v4/round27/finals_card_v4_ru.md`, 15:55Z draft). R27-A8 edits: (1) conditional l.31 opener; (2) l.40 П3 silver '~0.39–0.63 (база 0.51)'; (3) token keys on file names ('exp89r = ' ...), not 'probe NN:', plus an E10-copy token; (4) 'exp83c = 3' in the lever list; (5) pool rule l.113 follows GAP RULE v2 (UNPROVEN-ins); (6) PENDING windows for DIS files = parent family; (7) optional DIS footnote at l.58. Send only the ===== block; never tick | draft stored, edits not started | `round27/report.json` R27-A8; `round27/report.notes.md` (card defects l.31/l.40/l.101/l.113/l.58) |
| W19 / W73 / W102 / W93 / W165b | standing | ONE poller; header < 15 min old; never resubmit class C or ERRORed files; a SEC file may be a final only as V_pub (Q3 yes, l.3834) | standing | `CONTEXT.md` l.3331-3335, l.3480-3484, l.3834-3836 |
| W261 | before every push and right before the batch | **Dataset pre-push rule:** ft-weights lastUpdated 2026-09-23 23:54:03; n2a 2026-09-27 21:25:35. **Compare ref,size,lastUpdated only** (downloadCount moves with teammates' downloads) | standing (last checked 15:47Z) | `CONTEXT.md` l.3692-3703; `round27/report.json` new_facts 7, R27-A5 G3 |
| **T169** (new) | until 29 Sep 00:00Z | 28 Sep slots are 5/5 used: **no submit is possible before 00:00Z**. A "limit" error is expected, not a file failure | standing | `round27/scan_hyp_nightdry.notes.md` (last line) |

## LATER (29 Sep ~12:00Z -> 23:59Z, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| W266 (2) / T60 | **12:03Z** (15:03 MSK) | Send card v4 (with the W278 edits). SEC files may appear only as V_pub (Q3 yes) | `CONTEXT.md` l.3713, l.3834 |
| T152 | **18:37Z** (21:37 MSK) | FINAL proposal. Show any still-PENDING file with its pre-agreed swap | `CONTEXT.md` l.3714; `round26/report.json` R26-A4 (d) |
| **W277** (1) (new; supersedes T160) | any time before 19:43Z, best now | Fold the notify-only V_pub re-check into cron **58b6ded3** ('43 22 29 9' MSK = 19:43Z). Its prompt re-reads poll.log and pushes one line if V_pub changed or a PENDING file turned terminal since 18:37Z. Say so in CONTEXT | `round27/report.json` R27-A7 (1), plan_issues 6 |
| T161 | **19:43Z** (22:43 MSK) | Notify-only reminder + the W277 (1) re-check | `CONTEXT.md` l.3849, l.3854-3855 |
| T10 | **20:00Z (23:00 MSK)** | **The user ticks the finals.** The session never ticks by any route. The watchdog (W271 (c)) runs until then | `CONTEXT.md` l.3683-3685, l.3851-3855 |
| T153 | ~20:00-20:30Z | Verify API SELECTED = the user's pair (no cron; W270) | `CONTEXT.md` l.3474 |
| T162 | **21:05Z** (00:05 MSK 30 Sep) | Notify-only job: read SELECTED read-only; if it is not the proposed pair, push the exact pair | `CONTEXT.md` l.3851-3855; `round27/scan_plancheck.notes.md` 15:50Z (cron "last-call") |
| W177 H2 | 23:00Z | LESSONS H2 | `_curation/20/watch.json` |
| T49 | 23:00-23:45Z | Final public LB snapshot (not in the cron; W270) | `CONTEXT.md` l.2619 |
| T11 / T163 | **29 Sep 23:59Z** (02:59 MSK 30 Sep) | Deadline: a submit must **finish** before it; re-ticks allowed until then | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765; `CONTEXT.md` l.3848, l.3855 |
| T155 | 30 Sep 00:07Z cron | POST-DEADLINE job: private read v2 + L1-L7 | `CONTEXT.md` l.3714-3715, l.2570-2598 |
| T133 / **T170** (new) | **3 Oct** | GPU quota refresh (the API reports refresh 2026-10-03) | `round27/scan_hyp_nightdry.notes.md` (GPU quota line) |
| W29 / curator | after 29 Sep | Post-deadline list, plus z-shift +0.1 after CI; MAX_UM 2.0 note | `round25/report.json` R25-A8 (d) |
| W270 (updated) | before 17:57Z | Session cron (15:50Z CronList): rounds, freeze 23:33Z, batch 00:04Z, morning 07:23Z, finals 12:03Z/18:37Z, reminder 19:43Z, last-call 21:05Z, post 00:07Z 30 Sep. **Missing:** the 01:17Z round (-> W276 backups), the 17:57Z tick check (T19), the 23:00-23:45Z LB snapshot (T49). The 19:30Z job is no longer needed (W277 (1)). All crons are session-only, and **a cron that falls inside a standby is lost, not deferred** (the 15:17Z round was swallowed) | `round27/scan_plancheck.notes.md` 15:50Z; `CONTEXT.md` l.3981-3983 |

**Passed or finished time-bound items:**
- R8 new-mechanism cutoff (27 Sep 12:00Z) passed; the 28 Sep 12:00Z consolidation is superseded (T46; l.3392-3394).
- The 13:00Z slot deadline was met (probe 51 submitted 12:14:57Z).
- The 15:17Z research round was lost to standby; round 27 ran 15:44-16:20Z instead (l.3981-3983; `round27/report.json` written_utc).
- Friend replies: none awaited (last friend instruction 26 Sep, l.2175-2176). Teammates are a GPU reserve only (l.3688-3698).
- T156: the tick deadline is 20:00 UTC = 23:00 MSK; never write "20:00" without "UTC" (l.3683-3687).

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I315** (new) | "powercfg: STANDBYIDLE AC 0 / DC 0, VIDEOIDLE AC 300 s / DC 300 s (display-off idle -> Modern Standby entry 'Idle Timeout')"; "AC connected standby is OK, DC/lid standby kills network + crons" | `round27/scan_plancheck.notes.md` 15:48Z-15:49Z | Only in a scan note. On battery, **the display turning off after 300 s can enter standby even with the lid open**, so "don't close the lid" is not enough. The charger is the only real fix. A watchdog loop dies in the same standby, so its silence is itself a signal. |
| **I316** (new) | "RETRY_SLACK_S = 210 # lb_poll.py: one failed attempt = <= 180 s timeout + 30 s sleep"; "RETRY_SLACK_S 210 per failed attempt inflates L_hi" | `tools/runtime_ledger.py` l.42; `round27/scan_hyp_nightdry.notes.md` | A network blip or standby wake near 22:17-22:27Z adds 210 s per failed attempt and can push 51 over the 10.2 h threshold (22:26:57Z). GAP RULE v2 (W273) must be logged before then. |
| **I317** (new) | Our API load today: "~86 ListSubmissions polls ... ~18 discussion-feed runs x ~50 calls (~900, the largest share)"; another account was banned for 'Resource abuse' | `CONTEXT.md` l.3988-3997 | Any new loop (tight poll, extra waiters) raises ban risk the day before the deadline. The tight-poll idea R27N-6 was rejected partly on this basis (`round27/report.json` rejected). |
| **I318** (new) | "nb_try's own HARD-FAIL regex matches 'limit', so a daily-allowance error would send exp83c in exp89p's place" | `round27/report.json` plan_issues 5; `round27/report.notes.md` | Silent slot waste plus a wrong file in the night. The fix (exit 3 = STOP) exists only in R27-A5 text until the batch prompt is replaced (W276). |
| **I319** (new) | "exp89p at 00:46Z reads 07:38-08:35Z vs the A-M1 decision header 'latest 08:40Z' (thin); at 00:07Z it reads 07:00-07:56Z" | `round27/scan_hyp_nightdry.notes.md` | The reason for W272 (ii). With the default (00:46Z), a late exp89p read can force A-M1 = UNUSED ('?'). |
| **I320** (new) | "A-M1 (exp89l CI) submitted at 08:45Z with the 10.9 h CI tail reads 19:39Z > 19:30Z card cutoff"; A-M2 at 11:30Z reads 18:22-19:10Z | `round27/scan_hyp_nightdry.notes.md`; `round27/scan_hyp_card.notes.md` | Morning files sent at the cutoff read after the 18:37Z proposal (W277 (2)). |
| **I321** (new) | "Teammates' downloads change downloadCount, so a full-row diff would give a false STOP" | `round27/report.json` R27-A5 why; `round27/scan_hyp_nightdry.notes.md` | Earlier dataset-check wording (W261, l.3692-3703) did not restrict the columns. |
| **I322** (new) | "The 15:17Z round cron fell inside the 15:15-15:39Z standby -> swallowed"; the cron list "lacks 01:17Z 29 Sep" | `round27/scan_plancheck.notes.md` 15:50Z | Standby-lost crons do not fire later. This is why W276 adds backup crons; the freeze cron 23:33Z has no backup. |
| **I323** (new) | Other teams' "LastSubmissionDate all 05-09Z -> scoring lag ~6-9 h"; "7 teams <=0.953 -> 0.956 ... per single snapshot window = 4 (<5)" | `round27/scan_browser.notes.md` | A public-source P2 signal is near its threshold. The next wave could trip it without any public notebook. |
| **I324** (new) | "exp75 1645 [s] with pred 10.69 min = slower GPU"; setup phase 203-788 s on any config | `round27/scan_recheck.notes.md` (PICK B) | GPU and I/O speed vary per run. Runtime gates must use the compute split (RULE v2.1), and hidden-runtime reads must use parent families. |
| **I325** (new) | "J_adj = J*(1 - 0.1*(N_pred-N_total)/N_total), linear, no kink ... gross bonus per 1% nodes ~ +0.0009"; non-division size-6-7 components = 2.71% of exp85a nodes | `round27/scan_recheck.notes.md` (PICK A) | Useful for the DIS footnote on the card (W278 (7)). The RC-A inference itself was refuted; do not reopen MIN_TRACK_LEN. |
| **I326** (new) | "Q3 ambiguity found: card row {V_nonCI, exp75} can put a SEC file (exp89p/exp89q) in the 'основной' role while a CI file is V_pub" | `round27/scan_hyp_card.notes.md` | The Q3 conditional line must be logged pre-score with the freeze line, before the first night read ~07:00Z (W278). |
| I306 | **RETIRED: WRONG.** "DIS 2.25 dummies +15-20%" was pre-GPU setup noise. DIS files have their parent family's hidden L | `round27/report.json` new_facts 6, R27-A3 (1) | Do not use it in the freeze line or the card. |
| I303 | In branch A, exp89r - exp89p = DIS + CI; DIS is readable only as dd with abs(dd) >= 0.002 | `round26/scan_recheck.notes.md`; `CONTEXT.md` l.3937-3941 | Now logged in v1.1 (l.3937-3941). Kept for the card wording. |
| I304 | UP '0' = "not higher by more than ~0.0001", never "lower" | `round26/scan_hyp_finals.notes.md` | Finals pool rule (R26-A4 (d)). |
| I305 | Dummy-clip GT lab: "only as a gate sanity check, never as a sign read" | `round26/report.json` new_facts 7 | Unchanged. |
| I307 | K's READMIT +0.84% nodes costs ~-0.0008 on any embryo | `round26/report.json` new_facts 10 | Card v4 risk column. |
| I308 | Georgy Mamarin (743006): "a public-best improvement also beat the replaced submission on private ~8/10" | `round26/scan_hyp_finals.notes.md` | Still only in a scan note. |
| I309 | "{exp85a, exp75} is FIRST on bronze in all 16 exp85a runs with CI mean >= -0.0003" | `round26/scan_hyp_finals.notes.md` | Model-conditional (partner rule v2, l.3972-3973). |
| I310 | "The user's own tick is the ONLY path." If the user does nothing, #37 + #38 stay | `CONTEXT.md` l.3851-3855 | Every proposal and notify job must say so. |
| I311 | Old exp12/exp13 raw ILP dirs are empty; DIS priors rest on logged numbers | `round26/scan_recheck.notes.md` | Unchanged. |
| I313 | SEC caveat: "weight swaps were 0/5 on our LB" (not 7) | `round26/report.notes.md`; `round27/scan_hyp_card.notes.md` | Card v4 uses '0 из 5'; re-check at the fill. |
| I287 / I290 / I294 / I297 / I301 / I302 / I278 / I72 / I116 / I145 | Unchanged (CI dL 1.60-2.18 h; exp75 = exp79a positions + #37 edges; CI z-bias; MASKING; no sha pin on ft-weights; 5/day per team; José Freitas not hengck23; no Co-Authored-By; crons die with the session; a submit must finish before the deadline) | `_curation/26/watch.json` | Last 15 commit bodies: 0 Co-Authored-By hits. |

**Resolved since ~14:00Z (curation 26):**
- I312 (ledger `exp89t` mis-mapped): fixed (`tools/runtime_ledger.py` l.82; `CONTEXT.md` l.3962-3963).
- I314 (morning reads after an early tick): now handled by W277 (2) (submit at the decision header).
- I295 (GPU unmeasured): measured, ~3.2 h left at 15:44Z (`round27/report.json` new_facts 8).
