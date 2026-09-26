# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 4: state as of 2026-09-26 ~01:20 UTC, git HEAD b2cb928, plus the untracked `research/wf_ideas_v4/round4/`. The previous curation was 3 (23:15 UTC 25 Sep, 1ca747b). All times are UTC, and every line cites its source.
Deadline: 29 Sep 23:59. The user ticks the finals MANUALLY by 29 Sep 20:00. Sources: `CONTEXT.md` §1; PRE-REG v3 §f l.1707-1736; AMENDMENT f2 l.1887-1895; RESUME POINT l.2006-2025.

## STATE IN 10 LINES

1. **Best public score: 0.954**, held by P35 exp57b and by P36 exp57 (scored 23:42:50Z, info only; its unrounded score is above #35's). Neither is a final: P35 is R5(a) UNPROVEN, and P36 is a diagnostic. Sources: `experiments/lb_poll/ledger.md` (01:13:07Z); `experiments/RESULTS.md` l.69; `FACTS.md` F-LB-09.
2. **Base: x138** (P34 exp56 = 0.953, ADMIT, L34 <= 6.46 h), on branch A. **Rank #155 of 3,919 at 00:47Z**: 6th of 73 teams in the 0.954 block, with the silver line 41 ranks below us. Sources: `CONTEXT.md` l.2006-2017; `FACTS.md` F-LB-02; `research/wf_ideas_v4/round4/report.json` new_facts.
3. **Running now:** #37 K2 exp58 (ref 56563521, submitted 00:02:12Z) and #38 twin exp58n (ref 56563534, 00:02:18Z). Both were PENDING at the 01:13:05Z poll. The LB poller and runtime ledger are live, and the poller session must stay up until 08:32:12Z. Sources: `experiments/lb_poll/poll.log` l.1421-1426; `experiments/lb_poll/ledger.md` A5-L(K2).
4. **Default finals:** F1 = K2 and F2 = twin, read ONLY by the K2/TWIN READ TABLE (in CONTEXT l.1978-2005, commit 1017c41, pushed 23:13:16Z, before any score). Sources: `CONTEXT.md` l.2015-2017; `DECISIONS.md` §2, §2b.
5. **Gaps in the READ TABLE** (C-32) are filled by **CLARIFICATION v2 (C1-C6)**. It is NOT in CONTEXT yet, and it must be committed and pushed before the first score (the twin can score from ~06:15Z). Sources: `DECISIONS.md` §2c; `research/wf_ideas_v4/round4/report.json` R4-A1.
6. **Finals ticked: 0 of 2.** With fewer than 2 ticked, Kaggle auto-selects the best public files, which today are P36 and #35, both wrong. The provisional-tick rule (I-227) is not in CONTEXT. Sources: `FACTS.md` F-RUL-12; round4 `scan_plancheck.json` PC4-01.
7. **All riders are closed:** forkmid, K3b, forkblob, K4, ANTIPAR/DNVETO, leaf prune on x138, floatout, head-shift scale and duplicate collapse. S4-S6 carry no rider. Sources: `CONTEXT.md` l.2021-2022; `DECISIONS.md` §1b G01-G15.
8. **Decision points on 26 Sep:**
   - one combined OK request, before the first score (~06:00);
   - extra K2 "clean" polls at ~07:57:30Z and ~08:00:45Z (8.0 h mark 08:02:12Z);
   - read the scores by the READ TABLE (+ v2) once both are terminal (~06:20-08:30);
   - provisional tick;
   - closures into CONTEXT by 12:00;
   - the M6 window lapses at 18:00.
   Sources: `WATCHLIST.md` W44-W49, T12-T13.
9. **Cutoffs:**
   - R8 (no new mechanisms): 27 Sep 12:00;
   - S12: 28 Sep 12:00 (moot, since there is no rider);
   - admission table: 28 Sep 22:00;
   - finals tick by 29 Sep 20:00 (reminders at 12:00 and 18:00; checklist I-229 not in CONTEXT).
   Sources: `CONTEXT.md` l.1614-1615, l.2019-2023; `WATCHLIST.md` T03-T20, W50.
10. **Ideas ledger:** 234 ideas: lb-tested 38, lab-tested 20, refuted 134, deferred 19, in-plan 22, open-untested 1. The strict orphan is I-233; at risk are I-224, I-226, I-227, I-228 and I-232. Source: `IDEAS.md` l.9, ORPHANS l.366.

## WHERE THINGS ARE

Knowledge base (`research/KNOWLEDGE/`, written only by the curator workflow `experiments/workflows/biohub-curator.js`):
- `research/KNOWLEDGE/INDEX.md`: this page (state, map, top ideas, top alerts).
- `research/KNOWLEDGE/IDEAS.md` + `research/KNOWLEDGE/ideas.json`: ideas I-001..I-234 in 12 clusters, each with status and sources. The delta is at l.11 and ORPHANS at l.366. `meta.curations` in `ideas.json` logs every status change.
- `research/KNOWLEDGE/FACTS.md`: verified facts in §1 (metric) to §7 (lab-to-LB transfer), plus CONTRADICTIONS C-01..C-35 (l.150; the open ones are C-30..C-35).
- `research/KNOWLEDGE/DECISIONS.md`: probes P01..P38 (§1), lab-gate decisions G01-G15 (§1b), finals (§2), READ TABLE (§2b), proposed CLARIFICATION v2 (§2c), and R1-R10 status (§3).
- `research/KNOWLEDGE/WATCHLIST.md`: OVERDUE (l.35), NEXT 24 H (l.49), LATER (l.77) and INSIGHTS AT RISK (l.110), with W, T and I IDs.
- `research/KNOWLEDGE/CHANGES.md`: the delta for each curation. Curator logs are in `research/KNOWLEDGE/_curation/{v4,2,3,4}/`.

Key sources (repo root):
- `CONTEXT.md`: the single source of truth. The newest entries sit at the end of §14, above "## 9. Literature" (l.2026). Key locations: PRE-REG v3 l.1576-1736; AMENDMENT f2 l.1887-1895; round 3 and closures l.1967-1977; READ TABLE l.1978-2005; **live RESUME POINT 00:02 at l.2006-2025**.
- `experiments/RESULTS.md` (every LB probe; P36-P38 at l.69-71). `experiments/lb_poll/poll.log` (10-min poll, 60 rows, `experiments/lb_poll/lb_poll.py` l.28). `experiments/lb_poll/ledger.md` (latency bounds, R5, A5 watch).
- `experiments/*/probe.json`: what each kernel changed. The kernels are `experiments/exp58_x138_safe_lowref/` (K2), `experiments/exp58n_x138_safe_lowref/` (twin) and `experiments/exp58t_x138_safe/` (K1 fallback).
- `experiments/exp60_trainlab/results.md`: x138 train lab and T9 verdicts. `experiments/runtime_step0/`: hidden-N bound and F(K2) = 7.87 h.
- `tools/runtime_ledger.py` (run `--print`; +210 s per failed poll attempt), `tools/dummy_gates.py`, `tools/trainlab.py`, `tools/build_probe_kernel.py`.
- `research/wf_ideas_v4/round4/report.json`: night round 4, untracked. It holds R4-A1..A9, the verbatim CLARIFICATION v2 in plan_issues, and new_facts. Its scans are `scan_plancheck.json`, `scan_hypotheses.json`, `scan_recheck.json` and `scan_browser.json`. Rounds 2 and 3 are `research/wf_ideas_v4/round{2,3}/report.json`. **No round has a REPORT.md** (C-30).
- `research/wf_ideas_v3/FINAL_REPORT.md` (pre-reg source). `PROMPT_FRIEND_A.md` (stale), `PROMPT_FRIEND_C.md` and `TEAM.md` (l.9 still says "0.97") hold the roles. External intel is in `research/browser_research_2026-09-24*.md`, `research/discussions_summary.md` and `research/survey_*.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-001 | K2 = exp58: x138 + safetail + lowrefine + insertion | in-plan: SUBMITTED as #37 and PENDING. Read by the READ TABLE vs #35 | `IDEAS.md` l.43; `experiments/RESULTS.md` l.70 |
| I-090 | F2 = no-insertion twin exp58n (AMENDMENT f2) | in-plan: SUBMITTED as #38 and PENDING. Read vs #34 | `IDEAS.md` l.74; `experiments/RESULTS.md` l.71 |
| I-224 | READ TABLE CLARIFICATION v2 (C1-C6) | at risk: NOT in CONTEXT. Commit and push it verbatim before any score | `IDEAS.md` l.83; `DECISIONS.md` §2c |
| I-228 | One combined pre-score OK request, items (a)-(f) plus closing floatout and dropping L1/L2 | at risk. Post it in Russian before ~06:00 | `IDEAS.md` l.85; round4 R4-A2 |
| I-227 | Provisional finals tick (exactly 2 files, by ref) | at risk. Tick as soon as the table resolves; 0/2 selected now | `IDEAS.md` l.84; `FACTS.md` F-RUL-12 |
| I-226 | Extra clean-proof polls at ~07:57:30Z and ~08:00:45Z | at risk. Schedule before 07:45Z; run only if #37 is still PENDING | `IDEAS.md` l.60; round4 R4-A3 |
| I-011 / I-219 / I-225 | K1 contingency; twin floor 0.952; resubmit K2 on "Kaggle Error" | in-plan; each needs the user's OK (part of I-228) | `IDEAS.md` l.53, l.82, l.59 |
| I-229 / I-232 / I-233 | 29 Sep tick checklist; save round REPORT.md files; poller error_description | checklist into CONTEXT today; REPORT.md in a quiet window; I-233 after 09:30Z or close it | `IDEAS.md` l.86, l.352, l.61 |

## TOP ALERTS (deduplicated from the three curators, `research/KNOWLEDGE/_curation/4/{ideas,facts,watch}.json`)

1. [now] **CLARIFICATION v2 (C1-C6) is not in CONTEXT.** Without it, the row-2 hole drops F2 to exp52, and a twin ERROR in row 5 matches no row. Append the verbatim block, fix the pending-OK line l.2023, then commit and push before any #37/#38 score. Sources: `DECISIONS.md` §2c; `FACTS.md` C-32; `WATCHLIST.md` W44.
2. [now] **The combined OK request has not been sent.** It covers K1, twin floor 0.952, row-2 F2 = K2 or K1, F1 = twin instead of #34, resubmitting K2 on "Kaggle Error", the runtime trigger, closing floatout and the provisional tick. Log the OK time against the first result times; an OK given after a score is visible is post-hoc. Sources: `FACTS.md` C-33; `WATCHLIST.md` W45; round4 R4-A2.
3. [now] **Keep the poller up.** Keep its session (PID 20052) and AC power up until 08:32:12Z. No builds, pushes or submits tonight, and never restart the poller between 06:00 and 09:30Z. Sources: round4 R4-A9; `experiments/lb_poll/ledger.md` A5-L(K2).
4. [today] **Extra clean-proof polls.** Schedule them before 07:45Z. The regular polls are expected at ~07:54Z and ~08:04Z, which straddles the 08:02:12Z mark. A poll with a failed attempt proves "clean" only if its header is <= 07:58:42Z. Sources: `WATCHLIST.md` W46; `FACTS.md` F-RUN-16/17.
5. [today] **Mechanical score read.** Do it once both are terminal, using scores from `poll.log` only. Log k, w, d1, d2, tk, clean, L(K2), L(twin), the table row and the commit/push times, then update `experiments/RESULTS.md` l.70-71. Sources: `WATCHLIST.md` W47; round4 R4-A4.
6. [today] **Provisional tick.** Put the PROVISIONAL TICK rule in CONTEXT now. The user ticks exactly two files (default #37 56563521 + #38 56563534), never #34, #35 or P36. Sources: `WATCHLIST.md` W48; `DECISIONS.md` §2.
7. [today] **Closures missing from CONTEXT** (one grouped line by 12:00):
   - Round 4: I-035, I-043, leaf prune lp30 +0.00083, I-230, I-231, I-234, the #155 intel, the x138 rename, and y3uanm having no public weights.
   - Round 3: I-151, I-173, I-218, I-220 to I-222 and the I-201 rule.
   - Round 2: I-213.
   Sources: `IDEAS.md` ORPHANS; `WATCHLIST.md` W49.
8. [today] **Floatout contradiction** (C-31). CONTEXT l.2022 says CLOSED, while the older KNOWLEDGE text allowed S12. DECISIONS G15 now recommends closing it; confirm the close in the OK message. Source: `DECISIONS.md` §1b G15.
9. [today] **Round-4 folder untracked, REPORT.md files missing.** Rounds 2-4 have no REPORT.md, although CONTEXT l.1938, l.1967 and l.2025 cite them (C-30). Save `report_md_ru` as the REPORT.md files and commit. The friend A card (`PROMPT_FRIEND_A.md`) is still stale. Sources: `WATCHLIST.md` W38, W02-W03.
10. [before-finals] **29 Sep FINALS-TICK CHECKLIST** (I-229). Put it in CONTEXT, and set reminders by 28 Sep that outlive this session. Also start the admission table and commit the `experiments/ext_*` folders. Sources: `WATCHLIST.md` W50, W04, W05.
11. [info] **Weak lab evidence for the insertion.** The +0.0157 rests on 1 TP, and the dense half has 1/3 or 2/4 TP/FP depending on the round (C-34). A dense private embryo may favour the twin, which supports twin = F2. I-233 is still an orphan. `TEAM.md` l.9 still says "0.97" (C-04). Sources: `FACTS.md` C-34, F-TRN-20.

## HOW TO USE

- "What is the score, what did probe N change, or why was it dropped?" -> `DECISIONS.md` §1, then `experiments/RESULTS.md` and `experiments/<exp>/probe.json`.
- "How do we read the K2/twin scores and pick F1/F2?" -> `DECISIONS.md` §2b (READ TABLE) + §2c (CLARIFICATION v2) + §2, then `CONTEXT.md` l.1978-2025.
- "Which lab gate closed a rider?" -> `DECISIONS.md` §1b, then `experiments/exp60_trainlab/results.md`.
- "Which rule decides this?" -> `DECISIONS.md` §3; the rule text is in `CONTEXT.md` l.1576-1736, and latency bounds are in `experiments/lb_poll/ledger.md`.
- "Was idea X tried?" -> search the alias in `IDEAS.md` or `ideas.json`. "Is claim X true?" -> `FACTS.md`, then its CONTRADICTIONS section.
- "What is next, overdue, or at risk?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`. Anything newer than 01:20Z 26 Sep -> the tail of `CONTEXT.md` §14 and `experiments/lb_poll/ledger.md`.
