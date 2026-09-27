# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-27 ~18:40 UTC (curation 19). Updates the curation-18 build of 15:55 UTC (`research/KNOWLEDGE/_curation/18/watch.json`); rows not repeated here are unchanged there.

Sources read for this update:
- `CONTEXT.md` at HEAD 22840c5 (3,095 lines; `## 9. Literature` at l.3075). New entries since curation 18:
  - 16:08 ROUND 18 PRE-SCORE CARD (l.3011-3056);
  - 16:08 REBASE FOR 28 SEP (l.3057-3062);
  - 16:33 exp76d DUMMY CLEAN (l.3063-3064);
  - 17:21 exp75 DUMMY COMPLETE (l.3065-3069);
  - 18:19:11 USER YES TO N2 (l.3070-3074).
- `git log`: 12d9271, 77e7810, ffe74d6, 22840c5. Git dates are local (UTC+3).
- `git status` (18:33Z):
  - untracked: `research/wf_ideas_v4/round19/`, `experiments/exp77_secft_n2/` (now with `exp77-secft-n2.ipynb` + `kernel-metadata.json` + `build.py`), `experiments/ds_secw_corwin_v1/weights/`, `e10_watch/20260927T1731Z.txt`, `e10_watch/20260927T1743Z.txt`.
- `research/wf_ideas_v4/round19/`: `REPORT.md` + `report.json` (complete, written_utc 18:28:35Z; actions R19-A1..A12) and all `scan_*.notes.md`.
- `experiments/lb_poll/ledger.md` (ledger time 18:24:50Z); `poll.log` (last header 18:24:48Z, l.16368).
- `experiments/e10_watch/watch_loop.log` (RUN 6 at 17:45:37Z).

All times are UTC. IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, superseded, moot, blocked, awaiting user.

**State in one line (18:40Z 27 Sep):**
- **Finals are unchanged**: #37 56563521 + #38 56563534 (`CONTEXT.md` l.3027-3035; `round19/REPORT.md` §1 (1)).
- **Probes 45 and 46 are PENDING** at the last header 18:34:50Z (`poll.log` l.16429; header 18:24:48Z l.16368-16373; `ledger.md` rows 56606948 L > 7.15 h, 56611472 L > 3.79 h).
  - 45 can score any minute (window ~18:37-19:00Z; 8.0 h mark 19:15:12Z).
  - 46 is expected ~22:00-22:40Z.
- **Round 19 is complete (18:28Z)**. **None of R19-A1..A12 is in CONTEXT yet**: the last CONTEXT entry is the 18:19Z N2 line (l.3070).
- **New since 15:55Z:**
  - the user said **yes to N2** (exp77, second fine-tune, ~3 GPU-h tonight; l.3070-3074);
  - the exp77 notebook was built at ~18:33Z and is **not pushed per CONTEXT**;
  - the round-19 report was written without knowing this: it still lists N2 as closed (I198).
- **Kaggle state:**
  - exp76a dummy: QUEUED since 16:33Z (18:19Z check, `round19/report.notes.md`);
  - exp75 and exp76d dummies: clean (l.3063, l.3065);
  - exp76c/e/g: not built (`ls experiments`, 18:33Z).
- **E10 v3 loop:** 6 runs, 0 signals (`watch_loop.log`).

**Changes since 15:55Z (curation 18):**
- **Done:**
  - W184: pre-score card logged 16:08Z, before 45 was terminal (l.3011);
  - W193: `round18/` committed (12d9271);
  - W194 (round 19 part): the round ran and its report is complete;
  - W186 (partly): exp76a/exp76d built and committed (12d9271); exp76d dummy PASS logged (l.3063); exp75 dummy clean (l.3065).
- **Superseded:**
  - W187 (R18-A4 "drop CI at 19:00Z / re-push exp76a") is WITHDRAWN by R19-A1 (4);
  - W191 (R18-A8 ladder-watcher restart) -> manual LB download per terminal header (R19-A2 (4));
  - W190 -> **W203** (R19-A11 W1 order 00:05 CI / 00:10 SEC / 00:50 DIV);
  - W189 -> **W199** (R19-A7 message after 45) + **W196** (R19-A2); W189 Q2 (exp74) is dropped (`round19/report.json` rejected);
  - W185 -> **W185 = R19-A5** (still overdue, now with the missing 46 waiter);
  - W188 -> **R19-A6** (same ID);
  - T101, T102, T104: passed or withdrawn.
- **New:** actions **W195-W207**, reminders **T109-T115**, insights **I198-I213**.

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W195** (new; = R19-A1) | **PRE-SCORE AMENDMENT for 45/46 and W1**, to paste before 45 is terminal:<br>(1) UP test by **SubmissionCount** (S0 = `e10_watch/20260927T1743Z.txt`, count 46 -> 47; LSD is a cross-check only; 3 re-downloads, else AMBIGUOUS, never N4);<br>(2) 46-PENDING row at the last header before 23:50Z;<br>(3) fallbacks per mechanism (CI: exp76c -> exp76a -> exp75; SEC: exp76g -> exp76d -> exp72; DIV: none);<br>(4) R18-A4 withdrawn;<br>(5) log 45's L next to K2's (7.36, 7.54] h | **overdue**: not in CONTEXT (last entry l.3070); report "NOW" was 18:28Z; 45 can be terminal at any header from ~18:35Z | before 45 is terminal (window to ~19:00Z; 8.0 h mark 19:15:12Z) | `round19/report.json` R19-A1; `CONTEXT.md` l.3070 is the last entry; `poll.log` l.16368 |
| **W185** (= R18-A2 -> R19-A5) | **RESUME POINT**. The last one is 26 Sep 22:46Z (l.2599). MEMORY.md l.8 still says "E10 v1 in force, v2 pending; retrain needs explicit yes" and l.9 says "latest 26 Sep 22:46 UTC". Log every waiter with its kind:<br>- crons 2e87e414, 012fa6dd, 328f7392, 18ff4796, bb224de9;<br>- Bash PIDs: 34616 (the 45 waiter), 18920 (00:05Z; its echo text "exp72, exp75" is stale), the round-20 waiter, 10648 (E10 signal);<br>- mark 5b23a3ed, 54a8f20d and cdd738f1 as expired.<br>**Add the missing 46 waiter** (W207). Add the 18:19Z N2 yes and the exp77 push to the new RESUME POINT | **overdue ~3.5 h** (R18-A2 said "now" at ~15:50Z) | now, before the 45 read | `grep -n "RESUME POINT" CONTEXT.md` -> l.2599 last; `memory/MEMORY.md` l.8-9; `round19/report.json` R19-A5 |
| **W207** (new) | **No waiter for probe 46** (56611472; 8.0 h mark 22:36:59Z; hard edge 00:00Z). A crash or compaction would lose the 46 read and the W1 row choice | not started | now (with W185) | `round19/report.json` R19-A5, plan_issues (7) |
| **W197** (new; = R19-A3) | Build **exp76c** (exp70q + CI), **exp76g** (exp70q + SEC) and **exp76e** (exp70b + cap6) with `MSYS_NO_PATHCONV=1` and the KQ order for the exp70q family. **Push exp76c FIRST, by ~19:30Z**: CI kernels queue ~3.3 h. Then push exp76g and exp73m, and exp76e right after 45 only if 45 is P5/U4. **Never re-push exp76a.** Diff each against its base. Log the shas and push times in one CONTEXT line | not started: no exp76c/e/g folders at 18:33Z | exp76c push ~19:30Z latest; all dummies PASSED by 23:45Z | `round19/report.json` R19-A3; `ls experiments` 18:33Z |
| W176 | No ROUND 14-19 RECORD in CONTEXT (`grep -c "ROUND 1[4-9] RECORD"` = 0) | overdue, low priority | after the 46 read | `CONTEXT.md` grep 18:33Z |
| W126 | **No RESULTS.md rows for probes 39-44**; 45/46 will extend the gap. The last row is probe 38 (l.71); last commit b2be382 (26 Sep 07:35Z) | overdue (D1 04:58Z) | before the finals read | `experiments/RESULTS.md` l.71; `git log -1 -- experiments/RESULTS.md` |
| W177 (= R17-A9) | LESSONS H1. `LESSONS_draft.md` has not changed since bf07763 | overdue | H1 now; H2 29 Sep 23:00Z | `research/wf_ideas_v4/round9/LESSONS_draft.md`; `git log -1` = bf07763 |
| W182 | No `NEVER_SUBMIT.md` in exp70j/exp70k (class C). exp70n has no row in any table (I196) | not started | before any 28 Sep submit | `ls experiments/exp70j_k2_dc020 experiments/exp70k_k2_dc0225` 18:33Z |
| W174 residue | E10 v3 submit edges and runbook v3 are not logged in CONTEXT | overdue | with W185 | `round18/scan_plancheck.notes.md` 15:20Z |
| W202 (b) (new part of R19-A10) | **The exp72 gate values were never logged** (d78093ac, 121,061 nodes / 116,931 edges / 80 forks, Secondary ed8c616b). l.3068 says only "exp72 dummy complete earlier". The same line should carry the exp76d CSV bee0afe9 (121,061 / 116,930 / 79). exp72 is the SEC fallback in W1 | overdue (R18-A3 step 5) | with W196, before 00:05Z | `CONTEXT.md` l.3068; `round19/report.json` R19-A10 (b) |
| W57 / W66 / W31 / W72 | "frozen/duplicated frames" (2 hits); 0 hits for `out_valid` / `efpost` / `33.1%` | overdue, low priority | passed | `_curation/18/watch.json` |
| W150 | Round prompt unchanged (js 13a27a1). Round 19 still produced no ROUND RECORD | overdue, low priority | before round 20 | `git log -1 -- experiments/workflows/biohub-research-round.js` |

## NEXT 24 H (27 Sep 18:40 -> 28 Sep 18:40 UTC)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| **W205** (new) | **tonight: push now; training ~3 GPU-h; outputs, datasets and rungs before 23:45Z, or they go to W2** | **N2 = exp77**, user yes 18:19:11Z:<br>- one T4x2 session;<br>- GPU0 continues exp71 (ed8c616b) for epoch 2;<br>- GPU1 trains fresh from pilkwang 9bac2fa0 for 1 epoch at lr 3e-5;<br>- outputs -> **new** private datasets -> exp70b + secswap rungs.<br>The notebook and metadata exist (18:33Z) but nothing is pushed or logged. Log the push time and sha; read the GPU quota first (I210) | in progress (built, not pushed per CONTEXT) | `CONTEXT.md` l.3070-3074; `experiments/exp77_secft_n2/` (untracked) |
| **W206** (new) | **before any N2 rung is dummied or submitted** | **Reconcile N2 with the pre-registered rules.** Three rules exclude it:<br>- card (6): "no N1/N2 build before the deadline" (l.3052);<br>- R19-A2 (6): "Never in W3/W4: ... N1/N2";<br>- round 19's closed list ends "... N2".<br>The user's yes overrides the build ban, but no table says where an N2 rung goes. **Log one amendment BEFORE any SEC score (exp76d ~07:30-08:15Z 28 Sep)** that says:<br>- does an N2 rung replace exp76d in the W1 SEC slot (only if its dummy PASSED by 23:45Z) or go to W2?<br>- which of the 2 recipes;<br>- its gate (new Secondary sha, nodes band);<br>- public-only unless Q3 = yes.<br>W1 never holds two SEC files (R19-A1 (3)) | not started | before 23:45Z (W1) or before the first SEC read (W2) | `CONTEXT.md` l.3052, l.3070-3074; `round19/report.json` rejected, R19-A2 (6), R19-A1 (3) |
| **W196** (new; = R19-A2) | **before 00:05Z** (ideally right after W195 or the 45 read) | **28 SEP READ TABLE v2**. Paste this, NOT R19RT-1. It covers:<br>- rows A/B/C/D + the 46-PENDING row;<br>- codes P5/P6/U/N/MASKED/NEG/BLIND "?";<br>- CI ledger: `safetail_ci` <= 10.75 h, CI_lo 2.2 h, "v" if L_hi > 10.2 h, drop exp76c if 46's L_hi > 9.0 h;<br>- W1 order; W2 max-stack rules; W3/W4; T_last;<br>- finals V_pub with the CI/SEC caveats.<br>Amend it for N2 (W206) | not started | before 00:05Z 28 Sep | `round19/report.json` R19-A2 |
| **W198** (new; = R19-A4) | when the exp76a dummy completes (expected ~20:00-21:30Z) | **exp76a gate**, one PASS/FAIL line:<br>- edges == exp70b (117,076 / 74 forks), **NOT exp75's K2 counts** (75 / 117,077), which would false-FAIL;<br>- node rows == exp75's (z/y/x >= 99.9%);<br>- sha != ed7101bf / d6d9d808;<br>- COORDINJECT SUMMARY videos=4/4, replaced 0.90-0.93, 2 workers on cuda;<br>- 0 Traceback/SKIP/DEADLINE;<br>- FORKMID 4.5.<br>On FAIL, the CI slot goes to exp75 | waiting (QUEUED at 18:19:29Z) | `round19/report.json` R19-A4; `round19/report.notes.md` 18:19Z |
| **W199** (new; = R19-A7; replaces W189 brief) | **right after the 45 read (~19:00-19:30Z)** | ONE short Russian message:<br>- 45's code, display and rank;<br>- the W1 plan (00:05 CI / 00:10 SEC / 00:50 DIV; public-only);<br>- odds: P(>= 0.955 by 29 Sep 19:00Z) ~0.35-0.45, P(>= 0.956) ~0.10-0.15.<br>At most 3 yes/no questions:<br>(1) tau 0.75 rung, default NO, answer by 23:30Z;<br>(2) lift the 29 Sep 02:00Z cap, default NO, by 29 Sep 00:00Z;<br>(3) Q3 (SEC file as final), default NO, by 29 Sep 19:00Z.<br>**Add the N2 plan (where its rungs go, W206).** Log the R8-coverage line: coordinject was never named by the user | not started | ~19:00-19:30Z | `round19/report.json` R19-A7, plan_issues (12) |
| **W188** (= R18-A5 -> R19-A6) | **before 00:05Z** | `tools/runtime_ledger.py` rules:<br>- `safetail_ci` 10.75 h / divins 10.2 h;<br>- exp75*, exp76[abcfhik] -> CI;<br>- exp76[degj], exp77*, exp7[24]* -> safetail;<br>- exp73[w-z] reserved;<br>- plus a test.<br>**Check the exp77 rule against the N2 folder `exp77_secft_n2` (a training kernel, never submitted) and the proposed tau rung `exp77a` (I200).** Until this lands, pass `--family` | not started (EXP_RULES has no exp72-77; verified 18:14Z) | before 00:05Z | `round19/report.json` R19-A6; `round19/report.notes.md` |
| **W200** (new; = R19-A8) | build + dummy after the 45 read if 45 is not NEG; PASS by 23:45Z; submit 00:50Z in row C only | **tau 0.75 coin-flip rung "exp77a"**:<br>- gate: nodes [121,252, 121,313], forks 82-99;<br>- NEVER a final.<br>**Needs a NEW user yes** (W199 q1). **Rename it before building**: exp77 is now the N2 training kernel (I200) | awaiting user | `round19/report.json` R19-A8 (covered_by_existing_approval = false) |
| **W201** (new; = R19-A9) | after the 46 read (~22:40Z); pushed by ~23:30Z | Dummies for the row's W2 stacks, CI stacks first:<br>- exp76f 68e3919e in every row;<br>- row B: exp76i e1dd9646, plus new exp76j / exp76k;<br>- row A: exp76h 3819c1b0.<br>Only if the GPU quota is >= 6 h (I210) | not started | `round19/report.json` R19-A9 |
| **W202** (new; = R19-A10) | with W196 | CONTEXT corrections:<br>(a) **amanatar V6 0.901 is not a division read** (the l.2976-2977 citation is misattributed);<br>(b) exp72/exp76d gate values (see OVERDUE);<br>(c) div 2.5/2.75 stays out;<br>(d) N1 x2/x3 weights are local only (`_dl/secft_x2_ds`, `_dl/secft_x3_ds`), never uploaded.<br>Curator items by 30 Sep | not started | before 00:05Z | `round19/report.json` R19-A10 |
| **W204** (new; = R19-A12) | tonight, with the W195/W196/W185 entries | Commit `round19/`, the CONTEXT entries, `exp77_secft_n2/` (after the push) and later the ledger edit + test.<br>- Stage **named paths only**; no `e10_watch/*`, `ledger.md`/`poll.log` or `ds_secw_corwin_v1/weights/` unless intended;<br>- **no Co-Authored-By trailer** (I72); grep for "claude" before the push | not started (`round19/` untracked) | `round19/report.json` R19-A12; `git status` 18:33Z |
| **W203** (new; = R19-A11; replaces W190) | **28 Sep 00:03Z waiter (PID 18920, stale text); 00:05Z CI, 00:10Z SEC, 00:50Z DIV** | Per file:<br>- no duplicate in `kaggle competitions submissions`;<br>- last poll header < 15 min old and not a 429;<br>- dummy PASS in CONTEXT;<br>- CI dataset check (yuki0731/biohub-coord-inject = 10 files dated 2026-08-25).<br>Log each ref; run the ledger with `--family`. The finals stay untouched | not started | `round19/report.json` R19-A11, R19-A2 (4) |
| W165b / Q3 | Q3 by 29 Sep 19:00Z (W199 q3); exp70b-as-final is now handled by V_pub (R19-A2 (9)) | awaiting user | `round19/report.json` R19-A5, R19-A2 (9) |
| W19 / W73 | until 29 Sep 20:00 | ONE poller. Header < 15 min old and not a 429 before any submit | in progress (last header 18:24:48Z) | `experiments/lb_poll/poll.log` l.16368 |
| W102 / W93 | standing | Never resubmit class C (exp70j/k) or an ERRORed stack. exp65/66 and the dry-run kernel stay never-submit. An ERRORed single gets one unchanged resubmit only per R19-A2 (5) | standing | `round19/report.json` R19-A2 (5) |
| T100 | hourly at **hh:43Z** (next 18:43:42Z) until 29 Sep 12:00Z | E10 v3 watch run. **Its snapshot can already show count 47: never use it as S0 by time** (I203) | live, 0 signals in 6 runs | `experiments/e10_watch/watch_loop.log` |
| T95 (updated) | **now -> ~19:00Z**; 8.0 h mark **19:15:12Z**; hard edge ~20:30Z | **Probe 45 (56606948) read** by the count rule (W195). Log k, the TeamIds passed and L vs K2's | PENDING at 18:24:48Z | `ledger.md`; `round19/report.json` R19-A1 |
| T109 (new) | **~19:30Z** | Latest exp76c push that can still PASS by ~23:30Z (CI queue ~3.3 h) | - | `round19/report.json` R19-A3 (c) |
| T110 (new) | **~19:00-19:30Z** | W199 message; tau answer due 23:30Z | - | `round19/report.json` R19-A7 |
| T96 (updated) | **~22:00-22:40Z**; 8.0 h mark **22:36:59Z**; hard edge 00:00Z | Probe 46 (56611472) read. **The waiter is missing (W207)**. "v" if L_hi > 8.0 h | - | `round19/REPORT.md` §1 (1); `round19/report.json` R19-A5 |
| T111 (new) | **22:30-23:15Z** | Round 20 (round-20 waiter per R19-A5). It checks that W195/W196/W185 were logged BEFORE 45 was terminal | - | `round19/report.json` next_focus |
| T112 (new) | **23:30Z** tau answer; **23:45Z** every W1 dummy PASSED (T103); **23:50Z** last header for the 46-PENDING row | - | - | `round19/report.json` R19-A1 (2), R19-A8 |
| T18 / T42 (updated) | **28 Sep 00:00Z** reset; **00:05Z CI / 00:10Z SEC / 00:50Z DIV** | W203 | - | `round19/report.json` R19-A2 (4) |
| T104 (updated) | **28 Sep ~07:30-11:00Z** | Expected W1 completions:<br>- SEC ~07:30-08:15Z;<br>- DIV ~08:35-09:15Z;<br>- CI ~09:40-11:00Z.<br>One manual `kaggle competitions leaderboard -d` into a new folder at each terminal header. **No ladder-watcher restart**: it hardcodes the 27 Sep refs | - | `round19/report.json` R19-A2 (4), plan_issues (9) |
| T113 (new) | **28 Sep ~08:00-11:00Z** | Round 21: the W1 reads by count; the W2 stack choice | - | `round19/report.json` next_focus |
| T105 (updated) | **28 Sep, after all W1 reads or 12:00Z** | W2 file 1 = max stack of the + levers; file 2 only if all 3 are + | - | `round19/report.json` R19-A2 (5) |
| T106 (updated) | **28 Sep 12:00Z** | Held E10 v3 slot released. A CI ref not terminal by then -> W2 goes on with CI = "?" | - | `round19/report.json` R19-A2 (3)-(4) |
| T67 | standing | Timers are session-only; cron fields are LOCAL (UTC+3). Background Bash waiters die with the session | - | `round19/report.json` R19-A5 |

## LATER (28 Sep 18:40 -> 29 Sep 23:59 UTC, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T46 | **28 Sep 12:00** | F1 consolidation (R8 lifted for the named items) | `CONTEXT.md` l.1671; l.2955-2971 |
| T19 / W77 | **28 Sep 17:57** (012fa6dd) | API SELECTED + page read of the ticks | `_curation/18/watch.json` |
| T114 (new) | **28 Sep <= 23:30Z** | W3 (if a slot is left): only + levers that B* lacks; never knob rungs, DC, tau follow-ups or N1/N2. **Amend the N2 part (W206)** | `round19/report.json` R19-A2 (6) |
| T35 | 28 Sep 22:00 | Final admission table: 45, 46, W1/W2/W3 files, E10 v3 copies | `research/wf_ideas_v3/FINAL_REPORT.md` l.178 |
| T20 / T107 (updated) | **29 Sep 00:00Z** reset; **W4 00:05-01:45Z, <= 5 files**; last submit 01:45Z unless the user lifts the cap (W199 q2, by 29 Sep 00:00Z). With the lift: T_last = 18:30Z - (L_ref + 0.25 h), ~10:30Z and never later than 11:00Z; CI files T_last - 2.4 h | `round19/report.json` R19-A2 (6)-(7) |
| T98 | **29 Sep 02:00Z** target for a verbatim E10 copy; the loop ends 29 Sep 12:00Z | `experiments/e10_watch/watch_loop.log` l.1 |
| T60 | **29 Sep 12:00** | G2 must have landed for a SEC file to be finals-eligible (Q3 = yes only) | `CONTEXT.md` l.2736 |
| T09 / W77 | **29 Sep 11:57** (328f7392) / **17:57** (18ff4796) | Tick checks + user reminder | `round19/report.json` R19-A5 |
| T115 (new) | **29 Sep 19:00Z** | Q3 answer deadline (W199 q3). V_pub finals message: non-CI L_hi <= 9.0 h, CI <= 10.75 h; tau stacks are never finals | `round19/report.json` R19-A2 (9), R19-A7 |
| T48 (= W131) | **29 Sep ~19:00** | L9 last read. Never two byte-identical files; never a non-COMPLETE file | `CONTEXT.md` l.2510-2518 |
| T10 | **29 Sep 20:00** | Our buffer, not a Kaggle freeze; re-ticks are allowed until 23:59Z | `round18/report.json` R18-A2 (1) |
| W178 | before 29 Sep 23:00Z; hourly 30 Sep | Private-read addenda; key on a non-empty privateScore (I180). Add 56606948, 56611472 and every 28 Sep ref (card (8)) | `CONTEXT.md` l.3056 |
| T49 | 29 Sep 23:00-23:45 (bb224de9 at 23:27) | Final public LB snapshot | `_curation/18/watch.json` |
| T11 | 29 Sep 23:59 | Deadline. A submit must **finish** before it | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 |
| T30 / T50 | 30 Sep from 00:15Z | Private read v2 + L1-L7 + W178 | `CONTEXT.md` l.2570-2598 |
| W192 + W179 / W147 / W166 + R19-A10 curator items | by 30 Sep | Curator edits:<br>- I-051/I-334 tau re-measure;<br>- I-333;<br>- V6 correction (I-053/I-025/I-352);<br>- I-384 k = 1.5;<br>- DC-band fact;<br>- the R18-A9 items | `round19/report.json` R19-A10; `round18/report.json` R18-A9 |
| W29 | after 29 Sep | Post-deadline list: N1 k = 1.5 (I-384), primary head FT, LOEO DC | `round19/report.json` R19-A2 (8) |

**Done, superseded or moot since 15:55Z (for the record):**
- W184: card logged 16:08Z (l.3011-3056), before either score.
- W193: `round18/` committed (12d9271).
- W186:
  - exp76a/exp76d built (shas 98a9e647 / 89d71960, l.3057-3062);
  - exp76d PASS (l.3063);
  - exp75 dummy clean 17:20Z (l.3065).
- W187 withdrawn: exp75 ran after ~3.3-4 h in the queue, and a re-push restarts the queue (R19-A1 (4)).
- W191 superseded: `ladder_watch.py` hardcodes WATCHED / BASE_COUNT 40 / the 27 Sep caps, so a restart needs a code change (`round19/scan_plancheck.notes.md`).
- W189 Q2 (exp74) dropped: "not worth a question slot" (`round19/report.json` rejected).
- W183 (cadence answer to the user): nothing in the repo shows whether it was sent. Moot now that round 19 ran and round 20 has a waiter (R19-A5).
- T101 (17:50Z) met; T102 withdrawn; T103 -> T112.

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I198** (new) | Round 19's closed list ends "... knob ladders, **N2**, synthetic pretraining", and its read table says "Never in W3/W4: ... N1/N2". But at 18:19:11Z the user said "да, N2" | `round19/report.json` rejected + R19-A2 (6) (written 18:28:35Z; writer started 18:17Z); `CONTEXT.md` l.3070 | Pasting R19-A2 verbatim would silently forbid the rungs the user just approved. Round 20 would not re-propose N2. See W206 |
| **I199** (new) | "exp76d/exp72 secondary loader is HARD-fail on sha mismatch (RuntimeError, not fail-soft): a dataset re-version ... cannot silently change exp76d, but a missing file -> ERROR" | `round19/scan_plancheck.notes.md` | N2 outputs must go to **new** datasets. Re-versioning `biohub-secft-all-v1` (which exp72, exp76d and exp76g attach) without ed8c616b would ERROR the 00:10Z SEC file |
| **I200** (new) | "the knob is an env-driven cell-0 constant in exp70b; **exp77 is unused**" -> tau rung named `exp77a_k2fm_tau075`; R19-A6 rule `exp77[a-z]* -> safetail`. But `experiments/exp77_secft_n2/` is now the N2 training kernel. An earlier collision: "exp70k_k2_tau075 ... that folder name is now taken by DC 0.225" | `round19/report.json` R19-A8, R19-A6; `round19/scan_recheck.notes.md` | This is the 3rd naming collision (after I190 exp73). Rename the tau rung and the N2 rungs before building, or ledger and CONTEXT tokens mix them |
| **I201** (new; updates I193) | CI per video 77.5-238 s -> hidden "2.2-2.85 h, not 2.1 h. L(exp76a) ~ 7.58 + (2.2..2.85) = 9.8-10.45 h"; CONTEXT l.3067 still says "L ~9.6-9.8 h" | `round19/scan_plancheck.notes.md`; `CONTEXT.md` l.3067 | That leaves 0.05-0.7 h under the 10.5 h COORDINJECT guard, so the CI stage can be partly a no-op. The insertion gate must subtract CI_lo, and exp76c is dropped if 46's L_hi > 9.0 h (R19-A2 (3)). CONTEXT has the stale number |
| **I202** (new) | Both CI kernels queued for hours: exp75 13:18Z -> start ~16:40Z; exp76a 16:33Z -> still QUEUED at 18:19Z. The "only metadata difference" is dataset `yuki0731/biohub-coord-inject`. "If CI scoring reruns queue like the CI dummies, the CI reads land after 11:00Z" | `round19/report.notes.md` 18:22Z; `round19/report.json` plan_issues (15) | The CI submission rerun may also queue, which would push the 28 Sep CI read past 12:00Z and 29 Sep T_last - 2.4 h. The ledger L for CI files then includes queue time |
| **I203** (new) | "Our row's SubmissionCount counts SCORED files only ... LastSubmissionDate (LSD) is the max submit time over our scored files"; "The hourly E10 snapshot at 18:43Z or 19:43Z may already show count 47 and would code a false N4" | `round19/report.json` R19-A1 (1), plan_issues (1) | The UP test in the 16:08Z card (l.3013-3014, "previous snapshot") is wrong until W195 is pasted |
| **I204** (new) | "5 teams sit between exp70b (~0.95445) and the 0.9545 edge (~5e-5) ... For CI ... P(U4) ~1% ... So for CI/SEC the read is effectively P5/N4/NEG" | `round19/scan_hyp_reads_table.notes.md` | "N4 closes the lever" for CI/SEC rests on this. An N4 on a SEC file closes N2 as well |
| **I205** (new) | "That rule's flagship pick dc0.30 (both-embryo positive, bootstrap P(<0)=0.00, 0 TP lost) then read -0.005 public (probe 41). => the closure rule is falsified for the public direction"; lab DC [0.25,0.30) = 0 TP, yet public is TP-rich | `round19/scan_recheck.notes.md` | Lab-gate reasoning ("lab sign >= 0 on both embryos") fails on the public embryo. It is recorded only as a curator item (R19-A10). The same doubt applies to every lab-only argument for CI (lab in-sample +0.0022) |
| **I206** (new) | "tools/dummy_gates.py: no coordinject/secswap mode (grep 0)" | `round19/scan_plancheck.notes.md` | Every CI/SEC/N2 gate is a manual check. A copied gate (exp75's) would false-FAIL exp76a (W198) |
| **I207** (new) | "Latency order inversion: exp70e submitted 21:15:23 completed 04:40:05; exp70a submitted 21:17:47 completed 04:20:02"; "43/44 submitted 9 s apart completed in the same header" | `round19/scan_hyp_reads_table.notes.md` | Basis of the >= 40-min stagger in W1 (00:10 SEC -> 00:50 DIV). Do not compress it to fit an N2 rung |
| **I208** (new; updates I177) | amanatar V6 "tau NOT changed; changes DET 0.960, max-consensus detection blend ... -0.052 exceeds the whole division term ... V6 is NOT a read on division gates" | `round19/scan_recheck.notes.md`; `experiments/ext_optimized-biohub-max-score/v6_2026-09-27/NOTES.md` | `CONTEXT.md` l.2976-2977 still cites V6 against division rungs. The correction is only in W202 (a) |
| **I209** (new) | N1 staging: `_dl/secft_x2_ds` (30f7eec3), `_dl/secft_x3_ds` (a852ed11) with "dataset-metadata ids vitaliineibauer/biohub-secft-x2-v1 / -x3-v1"; "k3 drops a GT centre even IN-SAMPLE" | `round19/scan_hyp_n1_prep.notes.md` | Ready-to-upload folders sit next to tonight's N2 upload work. Uploading the wrong folder is easy; N1 is post-deadline only (R19-A2 (8)) |
| **I210** (new; updates I185) | "Quota: ~22 h left at Q1 (CONTEXT l.2729); since then exp71 ~2.3 h + ~6 dummies -> ~16 h" (an arithmetic estimate, not a read) | `round19/v_plancheck_pc19-03.notes.md` l.9 | Tonight's asks: N2 ~3 h, R19-A3 ~2-2.5 h, R19-A9 ~2-3 h (gated on >= 6 h), exp77a ~0.5 h, N2 rung dummies. That is ~8-9 h of an unread ~16 h. Read the Kaggle Settings page before the N2 push |
| **I211** (new) | "R17-A1 deviation record (12:12Z) names exp71 + rungs 45/exp70q/exp70r, not coordinject (exp75/76a) nor exp76d" | `round19/scan_plancheck.notes.md` | CI has no named user OK. R19-A7 must disclose it before 00:05Z (W199) |
| **I212** (new) | The only W1 plan written in CONTEXT is stale: l.3068-3069 "For 00:05Z: exp76a ... else exp75", and the card (4) fallback "exp76a -> exp72 -> exp75" can pair two SEC files. The 00:05Z waiter echoes "exp72, exp75" | `CONTEXT.md` l.3043, l.3068; `round19/report.json` R19-A5, plan_issues (3) | If W195/W196 are not pasted, a resumed session follows the stale chain |
| **I213** (new) | exp71 changed 10 keys; "detect_head.bias 49.8%"; BN frozen; x138 re-aligns secondary logits per frame, so a global bias shift cancels (I189) | `round19/scan_hyp_n1_prep.notes.md`; `round18/scan_hyp_new_levers.notes.md` | N2 GPU0 = epoch 2 of the same recipe, likely a larger step in the same, mostly cancelled direction. Expect N2 rungs ~= exp76d unless the node delta grows. Log the dummy node delta vs exp76d's -0.16% |
| I187 (updated) | Waiters now exist as Bash PIDs (45: 34616; 00:05Z: 18920; round 20; E10: 10648), but **no 46 waiter** | `round19/report.json` R19-A5 | W207 |
| I188 | exp71 used one GPU of the T4x2 | `round18/scan_hyp_new_levers.notes.md` | exp77 uses both GPUs (l.3071). Check both are busy in its log |
| I190 | E10 SI copies named exp73[x] collide with the division rungs | `round18/scan_plancheck.notes.md` | R19-A6 reserves exp73[w-z]; see I200 |
| I191 | KQ knob order (exp70q sha 33ab04d1 vs 95cf730f); `MSYS_NO_PATHCONV=1` | `round18/scan_hyp_slots_28sep.notes.md` | Now required for exp76c/g (W197) |
| I192 | Latencies rising: K2 7.36-7.54 -> 43/44 7.56-7.74 h | `ledger.md` | 45 at L > 7.15 h at 18:24Z. Log it vs K2 (R19-A1 (5)) |
| I194 | In-bin position 6/114-115 in the 0.954 block; ~2.8 teams/h pass us | `round19/REPORT.md` §2 | U4 window shrinking (I204) |
| I196 | exp70n dummy COMPLETE, no row in any table | `CONTEXT.md` l.2992 | Still orphan; W182 |
| I72 | Harness trailer vs the user's no-co-author rule | `memory/feedback-git-no-coauthor.md` | For W204 |
| I116 | Agents label local times as "Z"; cron fields are local | `round18/report.json` R18-A2 (2) | For the 46 waiter |
| I145 | A submit must finish before the deadline | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 | T107 / T11 |
| I154 / I165 / I174 / I175 / I180 / I181 / I182 and older | Unchanged | `_curation/18/watch.json` | I182 (Q3) now sits in W199 q3 |

**Resolved since 15:55Z:**
- I195: exp75 ran and is clean, so the CI slot is covered.
- I197: the watcher is replaced by manual downloads and the count rule.
- I193: superseded by I201.
