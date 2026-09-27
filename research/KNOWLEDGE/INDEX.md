# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 20: state as of 2026-09-27 ~21:00 UTC. Git HEAD 771a608 ('User: autonomous night 27-28 Sep; W1 plan') = origin/main (`git status -sb`). Untracked: `research/wf_ideas_v4/round20/`, `research/KNOWLEDGE/_curation/20/`, `experiments/e10_watch/20260927T2043Z.txt`, `experiments/ds_secw_corwin_v1/weights/`. The previous curation was 19 (~18:50 UTC, 22840c5). All times are UTC, and every line cites its source.
Deadline: 29 Sep 23:59. The user ticks the finals MANUALLY and picks them on 29 Sep after all variants are scored; our buffer is 20:00 (`CONTEXT.md` l.3211-3213). `CONTEXT.md` gained 8 entries since curation 19, at l.3075-3221; `## 9. Literature` is now at l.3222. Anchors:
- Rules: PRE-REG v3 l.1576-1736; E10 PORT RULE l.2138-2147; LADDER + L9 l.2407-2424; RULE RECONCILIATION l.2502-2529; user letters (E10 v3, class-C (b), FREEZE lifted, aggressive mode) l.2917-2951.
- Since c19: R19-A1 amendment 18:50 l.3075; READ TABLE v2 18:50 l.3112; **PROBE 45 READ 0.956** 18:56 l.3196; cap rungs 19:01 l.3201; exp76a clean + exp77 pushed + exp79a/d built 19:05 l.3206; **USER: finals on 29 Sep** 19:10:58 l.3211; exp78a/exp76e clean 20:02 l.3214; **USER: autonomous night** 20:30 l.3217.
- Not yet logged: all of round 20 (R20-A1..A14), including READ TABLE v3 (R20-A2), the RESUME POINT (R20-A3; the newest is still l.2599, 26 Sep 22:46) and the N2 pre-registration (R20-A6) (`research/wf_ideas_v4/round20/report.json`).

## STATE IN 10 LINES

1. **Finals TICKED 2/2 (unchanged):** #37 K2 exp58 (56563521) = 0.954 and #38 twin exp58n (56563534) = 0.953. The user does not re-tick now; they pick on 29 Sep. The rule path is letter (b) {exp70g, #37} (`CONTEXT.md` l.3211-3213; `DECISIONS.md` §2 [c20] snapshot l.584; `FACTS.md` C-160 l.558).
2. **New team best: P45 exp70g (K2 + insertion cap 6, 56606948) = 0.956**, code P6. It was #162 at 18:55Z and #163 of ~3,956 at 20:43Z, 10th of 53 in the 0.956 block, SubmissionCount 47. Info only; the private LB (~71%) decides (`CONTEXT.md` l.3196-3200; `experiments/e10_watch/20260927T2043Z.txt` l.981).
3. **Base** = K2 (x138 + safetail + lowrefine + gated DaughterNet insertion), now on cap 6 (exp70g). 28 Sep files move off the exp70b base onto the cap direction and the cap-6 base (`FACTS.md` F-MOD-39 l.336; `DECISIONS.md` §1 [c20] table l.358).
4. **Pending:** P46 exp70q (cap 6 + thr 0.3 + fm 4.5, 56611472, submitted 14:36:59Z, 8.0 h mark 22:36:59Z) was still PENDING at the 20:55:15Z header. A 46 waiter exists (`experiments/lb_poll/poll.log` l.17283-17287; `CONTEXT.md` l.3216).
5. **Kernels:** exp77 N2 training has been RUNNING since 19:04Z. Clean dummies: exp76a (CI), exp78a (cap 8), exp76e, and exp78b (cap 12 + fc2; COMPLETE per the judge). exp79d (cap 6 + SEC) is COMPLETE with no logged gate. **exp79a (cap 6 + CI) was never pushed** (404 at 20:33Z) (`CONTEXT.md` l.3206-3216; `research/wf_ideas_v4/round20/report.notes.md` l.4).
6. **User mode:** asleep since 20:30Z; the session runs autonomously. The aggressive mode and E10 v3 remain in force. #37 + #38 stay ticked (`CONTEXT.md` l.3217-3221, l.2917-2951).
7. **28 Sep plan (round 20, NOT in CONTEXT):** W1 = 00:05Z exp78b, CI exp79a on its dummy PASS (<= 03:00Z), 00:50Z exp78a; W2a 08:45-10:00Z (exp80a or the N2 SEC file); W2b 12:00Z (held for E10). It conflicts with the 20:30Z CONTEXT default exp78a, exp78b, exp76e (`research/wf_ideas_v4/round20/report.json` R20-A2; `FACTS.md` C-161 l.559).
8. **Watchers:** the E10 v3 loop has done 9 runs with 0 signals (RUN 9 20:43:55Z; next 21:43:42Z). The LB poller runs every ~10 min (`experiments/e10_watch/watch_loop.log`; `experiments/lb_poll/poll.log`).
9. **Next decision points:** now: exp79a push, R20-A2 (before 46 is terminal), R20-A3, R20-A6 (before exp77 finishes ~22:00Z). 22:00-22:40Z 46 read; 22:30Z round 21; 23:45Z W1 dummies PASS. 28 Sep: 00:05Z W1; 07:30-11:00Z W1 reads; 08:00-09:30Z morning message (02:00Z-cap question); 12:00Z W2b. 29 Sep: 00:05-01:45Z W4; finals proposals 12:00Z/18:00Z; tick buffer 20:00Z (`WATCHLIST.md` NEXT 24 H l.72, LATER l.103).
10. **Ideas ledger:** 412 ideas (lb-tested 54, lab-tested 22, refuted 204, deferred 44, in-plan 86, open 2). The strict orphan is still I-233 (`IDEAS.md` CHANGES (20) l.103-113, ORPHANS l.649).

## WHERE THINGS ARE

The knowledge base `research/KNOWLEDGE/` is written only by `experiments/workflows/biohub-curator.js`:
- `INDEX.md` is this page. `CHANGES.md` holds the per-curation deltas (v4, 2-20).
- `IDEAS.md` + `ideas.json`: I-001..I-412 in 13 clusters. Sections: FINALS l.134, LADDER l.192, BASE l.245, RUN l.283, LOC l.325, DIV l.359, MODEL l.425, NODES l.476, INFER l.510, EF l.532, LINK l.552, VALID l.583, TESTSET l.631, ORPHANS l.649. The per-ID log is in `ideas.json` meta.curations[n=20].
- `FACTS.md`: §1 metric l.174, §3 LB l.212, §4 runtime l.232, §5 rules l.271, §6 models l.294 (F-MOD-39 l.336), §7 lab-to-LB l.338 (F-TRN-51/52 l.392-393), CONTRADICTIONS l.395 (C-159..C-166 l.557-564).
- `DECISIONS.md`: probes §1 l.126 (P45/P46 l.178-179; [c20] table l.358); gates §1b l.372; finals §2 l.437 ([c20] snapshot l.584); E10 §2f l.723 ([c20] l.852); ladder/cards §2h l.885 ([c20] rows l.934-943); R1-R10 §3 l.945 (R20 rows l.981-984).
- `WATCHLIST.md`: OVERDUE l.56 (W208-W209 first), NEXT 24 H l.72, LATER l.103, INSIGHTS l.129 (I214-I230). Curator logs are in `research/KNOWLEDGE/_curation/{v4,2,...,20}/`.

Key sources (repo root):
- `CONTEXT.md` (anchors above).
- LB: `experiments/RESULTS.md` (rows up to P38 only); `experiments/lb_poll/poll.log` and `ledger.md` (P39 on); `experiments/e10_watch/20260927T2043Z.txt` (newest snapshot) and `watch_loop.log`.
- Kernels: finals `experiments/exp58_x138_safe_lowref/` (#37) and `experiments/exp58n_x138_safe_lowref/` (#38); best `experiments/exp70g_k2_cap6/`; 28 Sep builds `experiments/exp78a_k2_cap8/`, `experiments/exp78b_k2_cap12_fc2/`, `experiments/exp79a_k2cap6_coordinject/`, `experiments/exp79d_k2cap6_secft/`, `experiments/exp76a_k2fm_coordinject/`, `experiments/exp76e_k2_fm_cap6/` (each has a `probe.json`); trainer `experiments/exp77_secft_n2/` (N2, NEVER_SUBMIT.md).
- Tools: `tools/build_probe_kernel.py`, `tools/coordinject_patch.py`, `tools/runtime_ledger.py` (no exp72-80 family yet), `tools/e10_port_gate.py`, `experiments/lb_poll/e10_watch_loop.py`.
- Rounds: `research/wf_ideas_v4/round20/report.json` (R20-A1..A14; there is no REPORT.md, since the harness blocked the write), plus `scan_plancheck.json`, `scan_hyp_insertion_direction.json`, `scan_hyp_private_view.json`, `scan_recheck.json` and `v_*.json`. Older rounds: `round19/`..`round8/`.
- Background: `research/wf_ideas_v3/FINAL_REPORT.md`, `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v4/round9/LESSONS_draft.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-403 / I-361 | READ TABLE v3: own-base codes + the W1/W2 v3 plan; then the P46 exp70q read | Log it before 56611472 is terminal (~22:00Z); read 46 with the v3 codes | `IDEAS.md` l.240, l.221 |
| I-401 / I-382 | exp79a = exp70g + coordinject: the on-base CI file | Push the dummy now and never re-push it. Gate: 121,252 nodes, 81 forks, COORDINJECT 4/4 | `IDEAS.md` l.356, l.320 |
| I-398 / I-397 | exp78b (cap 12 + fc2) at W1 00:05Z; exp78a (cap 8) at 00:50Z | Dummies clean; submit per v3 once it is logged | `IDEAS.md` l.237, l.236 |
| I-385 / I-396 / I-402 | N2: one file only (exp70g + the GPU0 epoch-2 student) in W2a; exp79d is the fallback | Log R20-A6 before exp77 completes; use NEW datasets + SHA | `IDEAS.md` l.470, l.472, l.473 |
| I-399 / I-404 / I-405 | exp80a (cap 24 + fc2, only if W2a qualifies); exp78b + CI stack; GPU quota reading | Read the quota first; priority exp79a > N2 dummy > exp80a > stack | `IDEAS.md` l.238, l.241, l.322 |
| I-383 | runtime_ledger families for exp72-80 (safetail_ci / safetail) | Land it with a test before 00:05Z 28 Sep; until then pass `--family` | `IDEAS.md` l.321 |
| I-406 / I-393 / I-407 / I-229 | 29 Sep finals card lines; V_pub rule; private-read addendum; tick checklist | Log before the first W1 terminal header (~07:30Z 28 Sep) | `IDEAS.md` l.189, l.188, l.628, l.156 |
| I-257 / I-324 / I-336 | RESUME POINT + MEMORY + R8 coverage line; HINDSIGHT GUARD | R20-A3 is the next CONTEXT write; push the guard before 29 Sep 23:00Z | `IDEAS.md` l.165, l.353, l.619 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/20/{ideas,facts,watch}.json`)

1. [now] **R20-A2 into CONTEXT before 46 is terminal** (earliest ~22:00Z; 8.0 h mark 22:36:59Z). Quote the last poll header that still shows 56611472 PENDING (20:55:15Z at the time of writing). It must also supersede the 19:05Z list and the 20:30Z default W1 order, otherwise a resumed session follows exp78a, exp78b, exp76e. Sources: `report.json` R20-A2; `FACTS.md` C-161, C-162; `WATCHLIST.md` W209.
2. [now] **Push the exp79a CI dummy.** It was never pushed (404 at 20:33Z), and CI kernels queue 2-3.3 h. The CI slot needs a PASS by 03:00Z. A CI file submitted after ~01:30Z finishes after the 12:00Z W2b decision. Sources: `report.json` R20-A1; `FACTS.md` C-166, F-RUN-34; `WATCHLIST.md` W208, I229.
3. [now] **R20-A3: the RESUME POINT, the MEMORY rewrite and the P45 correction.** The last RESUME POINT is 26 Sep 22:46Z (l.2599), and this is the 5th round flagging it. MEMORY still says 'E10 v1 in force', and the R8 coverage line for coordinject/secFT is missing. Correction line: the pre-registered S0 gives 127 TeamIds passed, not 113, and exp70g is class C, so the rule path is (b) {exp70g, #37}. Sources: `FACTS.md` C-26, C-159, C-160; `WATCHLIST.md` W185.
4. [now] **R20-A6 N2 pre-registration before exp77 finishes (~22:00Z).** It pre-registers ONE SEC file (exp70g + the GPU0 epoch-2 student) for W2a; exp79d is the fallback and GPU1 is never submitted. Outputs go to NEW private datasets with an SHA line. Also log the exp79d gate (R20-A5 (b)). Sources: `report.json` R20-A6, R20-A5; `WATCHLIST.md` W206.
5. [today] **P46 read at ~22:00-22:40Z with the v3 codes.** S0 = the newest download with count 47; S1 = the first download with count 48. Do one manual `kaggle competitions leaderboard -d` within ~10 min of the terminal header. Sources: `report.json` R20-A8; `WATCHLIST.md` W213.
6. [today] **GPU quota** is unread since 07:55/30 h (26 Sep); the estimate is 19-25 h used, and it resets on 3 Oct. Read it before exp80a and apply the cut-offs at 24/26/28 h. Sources: `report.json` R20-A7; `FACTS.md` F-RUL-05; `WATCHLIST.md` W212.
7. [today] **Ledger families (R20-A4, 4th flag).** Every 28 Sep ref prints 'family unknown', so there is no R5(a) admission, no 'v' suffix and no L_hi finals clause. Sources: `tools/runtime_ledger.py` l.76; `DECISIONS.md` §3 l.984; `WATCHLIST.md` W188.
8. [today] **E10 v3 texts are stale.** The trigger is now >= 0.957, not >= 0.955 (`experiments/lb_poll/e10_watch_loop.py` l.28, l.78). The runbook's SI (B) uses DIVINS_CAP=4, while our best uses cap 6. Log the R20-A10 (5) line; no code change is needed. Sources: `FACTS.md` C-163; `WATCHLIST.md` W174.
9. [before-finals] **R20-A9 finals card lines** go in before the first W1 terminal header (~07:30Z 28 Sep): V_pub among cap-family files, the winner's-curse tie rule, partner always #37, and the DIV caveat. Also send the R20-A12 morning message (08:00-09:30Z) with one question: lift the 29 Sep 02:00Z cap? Ticks are due by 20:00Z 29 Sep, and the session never re-ticks. Sources: `report.json` R20-A9, R20-A12; `FACTS.md` C-164, C-165; `WATCHLIST.md` W214, W199.
10. [info] **Records:** RESULTS.md ends at P38 (add P39-P46); probe.json 'compare with exp56' is boilerplate; write `research/wf_ideas_v4/round20/REPORT.md` from report_md_ru and commit round 20 by named paths (no `_dl/`, no Corwin weights), as the user with no Co-Authored-By trailer; add the R20-A10/A13 info lines. Lab: the only robust result is fc <= 2, and all gain at cap >= 8 comes from 2 clips of 6bba, so never quote it as private support. Old: ROUND RECORDs, NEVER_SUBMIT exp70j/k, LESSONS H1, V6 misattribution. Sources: `FACTS.md` C-118, F-TRN-51; `WATCHLIST.md` W126, W204, W176, W177, W182.

**RESOLVED since curation 19:** R19-A1 + READ TABLE v2 logged at 18:50, before 45 was terminal (a2e0696 18:50:11Z vs the 18:54:54Z header; `CONTEXT.md` l.3075, l.3112); 45 read 0.956 (l.3196); exp76a clean, exp77 pushed 19:04Z (l.3206-3210); exp78a/exp76e clean and the 46 waiter set (l.3214-3216); the N2-vs-closures conflict is addressed by R20-A6 (unlogged); exp76c/g, exp76j/k, the tau rung and exp73m are superseded (`IDEAS.md` CHANGES (20) l.103-113).

**Settled curator disagreements:** RESUME POINT [now] vs [today] (facts) -> [now], because the user is asleep; N2 [today] (ideas) vs [now] (watch) -> [now], because exp77 finishes ~22:00Z; W1 plan conflict [today] vs [now] -> merged into alert 1.

## HOW TO USE

- "Score of probe N, what changed?" -> `DECISIONS.md` §1; `experiments/RESULTS.md` (up to P38); `experiments/lb_poll/poll.log` / `ledger.md` (P39 on); `experiments/<exp>/probe.json`.
- "46 scored, what now?" -> R20-A2 (in CONTEXT once logged; else `research/wf_ideas_v4/round20/report.json`); `DECISIONS.md` §2h l.938.
- "What goes out on 28 Sep, and where does N2 go?" -> `report.json` R20-A2, R20-A6; `DECISIONS.md` §1 [c20] table l.358; `IDEAS.md` I-403, I-385.
- "Which pair do we propose for the finals?" -> `DECISIONS.md` §2 [c20] l.584; `report.json` R20-A9; `FACTS.md` F-TRN-52, C-160.
- "Did a public notebook beat us (E10 v3)?" -> `CONTEXT.md` l.2917-2926 (trigger now >= 0.957); `DECISIONS.md` §2f l.852; `experiments/e10_watch/watch_loop.log`.
- "Which rule decides this?" -> `DECISIONS.md` §3; `FACTS.md` §5 and CONTRADICTIONS; `CONTEXT.md` l.1576-1736.
- "Was idea X tried?" -> `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md`. "What is next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~21:00Z 27 Sep, check the tail of `CONTEXT.md` §14 (above `## 9.`), `poll.log`, and the newest `research/wf_ideas_v4/round*/`.
