# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 25: state as of 2026-09-28 ~11:10 UTC. Git HEAD 74caff9 ('Schedule restored ...') = origin/main. Untracked: `research/wf_ideas_v4/round25/` (no REPORT.md), `research/KNOWLEDGE/_curation/25/`, `experiments/discussions/digest_20260928T1106Z.md` (`git status`). The previous curation was 24 (~07:45Z, 19c24b5). All times are UTC unless marked MSK (= UTC+3), and every line cites its source.
Deadline: 29 Sep 23:59. The user ticks the finals MANUALLY by 20:00 UTC = 23:00 MSK on 29 Sep (`CONTEXT.md` l.3680-3687). `CONTEXT.md` gained 16 entries at l.3539-3716; `## 9. Literature` is now at l.3717. Anchors:
- Rules: PRE-REG v3 l.1576-1736; E10 PORT RULE l.2138-2147; LADDER + L9 l.2407-2424; RESUME POINT 01:48 l.3398; FINALS CARD 04:31 l.3417-3430.
- Since c24: **R24 pre-score 1/3-3/3 + LIFT SPLIT** 07:43 l.3539-3597; **exp87a/b/i builds + ledger** 07:44 l.3598; **user answers** 07:47 l.3607; **P49 read, S1 fires** 07:54 l.3615; **KNOB ARMS** 09:07 l.3625; **P48 read = 0.957 C+** 09:35 l.3639; **W2b AMENDMENT A** 09:35 l.3649; **dummy gates** 10:16 l.3659; **private hedge proposal** 10:16 l.3669; **user 3+2 + tick 20:00 UTC** 10:19 l.3680; **teammate GPU + datasets** 10:45 l.3688; **morning CI = YES** 10:47 l.3704; **cron restored** 10:52 l.3709.

## STATE IN 10 LINES

1. **Finals TICKED 2/2 (unchanged):** #37 K2 exp58 (56563521) = 0.954 + #38 exp58n (56563534) = 0.953; both below V_pub. No fallback if the user does not tick (`DECISIONS.md` §2 [c25] l.769-771; `FACTS.md` F-RUL-20).
2. **Team best: P48 exp79a (exp70g + coordinject ALPHA 0.5, CI file, 56623105) = 0.957, C+, UP 33 teams = V_pub.** Rank #153 of 3,968 (`CONTEXT.md` l.3639-3648; `experiments/lb_poll/_lb/S1_0934Z`).
3. **Cap direction closed:** P47 exp78b (cap 12) = 0.955 '-', P49 exp78a (cap 8) = 0.955 '-'; S1 fired, cap 6 is the optimum, BASE stays exp70g (0.956) (`CONTEXT.md` l.3530, l.3615-3624; `FACTS.md` F-LB-22).
4. **PENDING:** P50 exp85a = exp70g + ILP_DIVISION_WEIGHT 0.4 + READMIT 0.94 (56629533, sent 05:02:30Z; L > 6.01 h) at the 11:03:26Z header; terminal possible from ~11:54Z (`experiments/lb_poll/poll.log` l.22041; `experiments/lb_poll/ledger.md` 11:03:28Z).
5. **Logged W2b rule (AMENDMENT A, 09:35):** at 50's terminal header, latest 14:00Z: R+ (>= 0.957) -> exp87a (K + CI), else exp83c (SEC + CI). Round 25 wants exp75 instead of exp83c, latest 13:00Z, but that is NOT logged (`CONTEXT.md` l.3649-3658; `research/wf_ideas_v4/round25/report.json` R25-A1; `FACTS.md` C-202).
6. **Budget:** 28 Sep: 4 slots used, 1 left (P51). GPU ~5 h left (user) vs ~4.5 h (round 25) (`CONTEXT.md` l.3688-3691; `FACTS.md` C-206).
7. **Built/gated:** exp87a, exp83c, exp88a (DIS 2.25), exp88b (TAU 0.7) PASS 10:16; exp88c (DIS 1.75) COMPLETE on Kaggle 10:46Z, gate unlogged; exp86c 84 forks, needs the R25-A3 (b) waiver; exp75 built 27 Sep (ab621c13), on the NO-GO list; no exp89/exp90 folder (`CONTEXT.md` l.3659-3668; `DECISIONS.md` §1 [c25] l.454-459; `FACTS.md` F-MOD-44/45).
8. **29 Sep plan (user YES):** 3 night files (00:05-01:45Z) + 2 morning files; morning CI allowed, cutoff 09:30Z logged vs 08:45Z proposed; non-CI by 11:30Z; W4 freeze 23:30Z (`CONTEXT.md` l.3680-3687, l.3704-3708; `FACTS.md` C-204).
9. **Next decision points:** now: log R25-A1/A2/A4 + exp88c gate, then wake-ups 11:50/12:20/12:50/13:00Z; P50 read -> P51 submit; 12:47Z round 26; ~21:45-22:30Z P51 read; 23:30Z freeze; 00:04Z night batch; 07:23Z morning prep; 29 Sep 12:03Z finals card v3; 18:37Z final proposal; 20:00Z tick (`CONTEXT.md` l.3709-3716; `WATCHLIST.md` l.69-137).
10. **Ideas ledger:** 477 ideas (lb-tested 59, lab-tested 25, in-plan 117, refuted 227, deferred 47, open 2); strict orphan I-233; 15 at risk (`IDEAS.md` CHANGES (25) l.153-163, ORPHANS l.764).

## WHERE THINGS ARE

Knowledge base `research/KNOWLEDGE/` (written only by `experiments/workflows/biohub-curator.js`):
- `INDEX.md` = this page. `CHANGES.md` = per-curation deltas (v4, 2-25). Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,25}/`.
- `IDEAS.md` + `ideas.json` (I-001..I-477): CHANGES (25) l.153, FINALS l.184, LADDER l.252, BASE l.327, RUN l.368, LOC l.424, DIV l.460, MODEL l.530, NODES l.582, INFER l.618, EF l.640, LINK l.660, VALID l.696, TESTSET l.746, ORPHANS l.764; per-ID log `ideas.json` meta.curations[n=25].
- `FACTS.md`: §1 metric l.179, §2 data l.196, §3 LB l.217 (F-LB-22..24 l.242-244), §4 runtime l.246 (F-RUN-39/40 l.288-289), §5 rules l.291 (F-RUL-20/21 l.314-315), §6 models l.317 (F-MOD-44..46 l.364-366), §7 lab-to-LB l.368 (F-TRN-57 l.428), CONTRADICTIONS l.430 (C-201..C-209 l.634-642).
- `DECISIONS.md`: probes §1 l.131 (P47-P51 l.185-189; [c25] builds l.448-459); gates §1b l.466; finals §2 l.531 ([c25] l.769, snapshot l.771); E10 §2f l.910; ladder/cards §2h l.1082 ([c25] rows l.1179-1211); R1-R10 §3 l.1213 ([c25] rows l.1257-1285).
- `WATCHLIST.md` (curated ~11:00Z): OVERDUE l.69 (W248-W253, W258), NEXT 24 H l.88 (T145-T156), LATER l.112, INSIGHTS l.138 (I287-I302 l.142-157).

Key sources (repo root):
- `CONTEXT.md` (anchors above). LB: `experiments/RESULTS.md` (rows to P46 only); `experiments/lb_poll/poll.log`, `ledger.md`, `_lb/S1_0934Z`, `dataset_baseline/`; `experiments/e10_watch/watch_loop.log`; `experiments/discussions/feed_loop.log` + `digest_*.md`.
- Kernels (each has `probe.json`): finals `experiments/exp58_x138_safe_lowref/` (#37), `exp58n_x138_safe_lowref/` (#38); best `exp79a_k2cap6_coordinject/`; base `exp70g_k2_cap6/`; P50 `exp85a_k2cap6_div04_ra094/`; P51 candidates `exp87a_k2cap6_div04_ra094_ci/`, `exp75_k2_coordinject/` (exp83c = Kaggle e8f5a8a6); knob arms `exp88a_k2cap6_dis225/`, `exp88b_k2cap6_tau07/`, `exp88c_k2cap6_dis175/`; `exp86c_k2cap6_div04_ra092/`, `exp87b_k2cap8_div04_ra094_ci/`, `exp87i_k2cap8_div04_ra092/`.
- Tools: `tools/build_probe_kernel.py`, `tools/coordinject_patch.py`, `tools/runtime_ledger.py` (no exp89/exp90 rule yet), `tools/dummy_gates.py`, `tools/e10_port_gate.py`, `tools/kaggle_feed.py` (--our-best 0.957); `experiments/lb_poll/e10_watch_loop.py`. Missing: `tools/uptest.py`, `tools/gate_dummy.py` (scratchpad only).
- Rounds: `research/wf_ideas_v4/round25/report.json` (R25-A1..A9), `report.notes.md`, 5 `scan_*.json`, 18 `v_*.json`; `research/wf_ideas_v4/knobarms_28sep/` (13 arms, v_0..v_12); `round24/` (no REPORT.md); older `round23/`..`round8/`. Background: `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v3/FINAL_REPORT.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md` ORPHANS l.764 ff.)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-463 | W2b AMENDMENT A2 + P50/P51 read rule: R+ -> exp87a, else exp75; latest 13:00Z; new code '0u' | Log pre-score NOW, quoting the last PENDING header | `IDEAS.md` ORPHANS; `round25/report.json` R25-A1 |
| I-464 | W4 AMEND 4: night list fixed by P50 alone (R+: exp86c/exp75/exp89e; else exp88c/exp89a/exp88b); M1 CI, M2 non-CI | Log with I-463; settle the CI cutoff | `IDEAS.md` ORPHANS; R25-A2 |
| I-465 | exp75 (#37 + CI) as the private hedge: lift NO-GO, grandfather its 2,288 s dummy, submit v1 as is | Log R25-A4 before any submit | `IDEAS.md` ORPHANS; R25-A4 |
| I-451 | exp88c (ILP_DISAPPEARANCE 1.75) night arm | Log gate before downloading the output | `IDEAS.md` ORPHANS; R25-A3 (a) |
| I-460 / I-383 | exp89a/b/o CI arms on exp79a + ledger rule exp89 -> safetail_ci | Add the rule + test; build the realised-branch member at 50's read | `IDEAS.md` ORPHANS; R25-A5 |
| I-477 / I-468 | Russian user message (MSK first): drop answered Q2; ask the tick fallback and Q3 | Send with the P50 read; log answers | `IDEAS.md` ORPHANS; R25-A6 |
| I-467 / I-426 | Finals card v3: neutral A/B/C table + CI caveat, MSK times | Draft today; send 29 Sep 12:00Z (15:00 MSK) | `IDEAS.md` ORPHANS; R25-A7 |
| I-473 | Copy uptest.py into `tools/` (UP test for '0u') | Before the P50 read | `IDEAS.md` ORPHANS; R25-A8 (b) |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/25/{ideas,facts,watch}.json`)

1. [now] **R25-A1/A2 pre-score lines (AMENDMENT A2 + '0u' rule; W4 AMEND 4) are not in CONTEXT**, and P50 can be terminal from ~11:54Z. Until logged, AMENDMENT A (exp83c, latest 14:00Z) governs. Decide exp83c vs exp75; if exp75, log R25-A1 with the R25-A4 lift/grandfather line and quote the PENDING header. Sources: `round25/report.json` R25-A1, R25-A2, R25-A4; `CONTEXT.md` l.3649-3658; `FACTS.md` C-202, C-203; `WATCHLIST.md` W248, W249, W251.
2. [now] **exp88c gate unlogged, kernel COMPLETE at 10:46Z.** Log the gate (nodes +0.4..+1.3% vs 121,252, forks 81 +-5, runtime rule v2) marked 'logged after the kernel completed, before its output was downloaded', then download. Sources: R25-A3 (a); `WATCHLIST.md` W250; `FACTS.md` F-MOD-44.
3. [now] **No wake-ups for the P50 read / P51 submit.** Add 11:50, 12:20, 12:50, 13:00Z; the 12:47Z round-26 cron fires inside the window. Pause feed/watch loops ~10 min before the submit; run pre-submit checks (header < 15 min, 1 submission left, R8 COVERAGE, ledger family) and the dataset pre-push listing. Also missing: 17:57Z tick check, post-tick SELECTED check, 29 Sep ~23:27Z LB snapshot. Sources: `CONTEXT.md` l.3702-3716; `WATCHLIST.md` W258, T145-T147.
4. [now] **User message R25-A6:** Q2 (CI mornings) was answered YES at 10:47Z, so drop it; ask the tick-fallback question (else finals stay #37 + #38) and Q3; MSK first. Sources: R25-A6 (c), (e); `CONTEXT.md` l.3704-3708; `WATCHLIST.md` W253; `IDEAS.md` I-468, I-477.
5. [today] **Morning CI cutoff contradiction:** 09:30Z logged vs 08:45Z (round 25). At the 10.9 h CI tail a 09:30Z file reads ~20:24Z, after the tick; observed CI L is 9.27-9.45 h. Settle it in W4 AMEND 4. Sources: `FACTS.md` C-204, F-RUN-40; `round25/scan_plancheck.json` PC25-03; `WATCHLIST.md` W260.
6. [today] **Tooling gaps:** `tools/runtime_ledger.py` has no exp89/exp90 rule (exp89 CI files would be filed safetail 9.5 h; exp90a 'unknown'); uptest.py and gate85.py are scratchpad-only. GPU ~4.5-5 h: build/push only the realised-branch member. Sources: R25-A5 (a), R25-A8 (b); `FACTS.md` F-MOD-45, C-206; `WATCHLIST.md` W252, W255.
7. [today] **Night batch prerequisites:** exp86c R25-A3 (b) waiver (84 forks) before the 23:30Z freeze; every night file PASS by 23:30Z; P51 read (~21:45-22:30Z) must not block the freeze. Sources: R25-A3 (b); `CONTEXT.md` l.3522-3529; `WATCHLIST.md` W250, NEXT 24 H l.88.
8. [today] **Records:** `experiments/RESULTS.md` lacks rows 47-49 (0.955 / 0.957 / 0.955); REPORT.md not rendered for rounds 24-25 and round25/ untracked; CONTEXT still carries the CI_lo 2.2 h model vs measured dL 1.60-2.18 h (log the 'ins-tail?' footnote). Sources: `FACTS.md` C-118; `WATCHLIST.md` W126, W257, I287; `CONTEXT.md` l.3135.
9. [before-finals] **Finals card v3** as a neutral A/B/C table (A {V_pub, #37}; B {V_pub, exp75} only if exp75 >= 0.955; C {V_pub, exp70g}); R25P-9 draft refuted; CI caveat: exp75 is not an independent CI read, CI lab evidence is in-sample with a z-biased refiner; V_pub is itself a CI file. Sources: R25-A7; `round25/v_hyp_private_r25p-9.json`; `FACTS.md` C-197, C-208; `WATCHLIST.md` W254, I290, I294.
10. [info] Orphan I-233 (close in one line); log one CONTEXT line with the 10 refuted knob arms (`research/wf_ideas_v4/knobarms_28sep/v_*.json`); 0822Z '0.956 crowd' look-signal info line (R25-A8 c); dataset pre-push check before every push (W261); restart the E10 loop (docstring still '>= 0.955'). Sources: `IDEAS.md` ORPHANS; `WATCHLIST.md` I296, W261; `FACTS.md` C-163.

**RESOLVED since curation 24:** R24-A1..A3 pre-score blocks + LIFT SPLIT logged 07:43 (`CONTEXT.md` l.3539-3597); R24-A7 user message answered 07:47 (l.3607); dead cap > 8 files dropped and exp87a/b/i built with ledger rule 07:44 (l.3598); one runtime criterion (rule v2 <= 2,100 s, l.3578-3591); P48 read through the CI-RAN gate (l.3639-3648); E10 trigger raised to >= 0.958 (l.3645-3646); cron restored after the 05:07Z timer loss (l.3709-3716); exp87m dropped (R25-A2, pending log).
**Settled curator disagreements:** R25-A1/A2 and the exp88c gate are [now] in all three curators. The CI cutoff [today] vs [before-finals] -> [today], since it must be in W4 AMEND 4 before 23:30Z. The user message [now] (watch) vs [today] -> [now], to go with the P50 read.

## HOW TO USE

- "Score of probe N, and what changed?" -> `DECISIONS.md` §1; `experiments/RESULTS.md` (to P46); `experiments/lb_poll/ledger.md` / `poll.log` (P47 onward); `experiments/<exp>/probe.json`.
- "P50 scored; which code, and what goes out as P51?" -> `CONTEXT.md` l.3649-3658 (AMENDMENT A, logged); `round25/report.json` R25-A1 (A2 + '0u', proposed); `DECISIONS.md` §1 l.189, §2h [c25].
- "What goes out tonight / tomorrow morning?" -> `CONTEXT.md` l.3680-3716; `round25/report.json` R25-A2, R25-A5; `IDEAS.md` I-464, I-460; `WATCHLIST.md` NEXT 24 H l.88.
- "Which pair do we propose for the finals?" -> `CONTEXT.md` l.3417-3430, l.3669-3679; `DECISIONS.md` §2 [c25] l.769-781; `round25/report.json` R25-A7; `IDEAS.md` I-467, I-465.
- "Did a public notebook beat us (E10 v3, trigger >= 0.958)?" -> `experiments/discussions/feed_loop.log` + digests; `experiments/e10_watch/watch_loop.log`; `DECISIONS.md` §2f.
- "Which rule decides this?" -> `DECISIONS.md` §3; `FACTS.md` §5 and CONTRADICTIONS; `CONTEXT.md` l.1576-1736.
- "Was idea X tried?" -> `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md`. "What is next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~11:10Z 28 Sep, check the tail of `CONTEXT.md` §14 (above `## 9.`), `poll.log`, and the newest `research/wf_ideas_v4/round*/`.
