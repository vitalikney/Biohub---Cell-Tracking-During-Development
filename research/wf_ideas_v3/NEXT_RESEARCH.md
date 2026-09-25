# Research, day 2 (cloud session, 26 Sep 2026 from ~09:30 UTC) — moderate budget

Budget: about $45 left for the whole cloud session. Day 2 target is at most ~$10–12: no workflows, at most 3–4
subagents, short reads (grep, not whole files). Everything goes to `research/wf_ideas_v3/day2_*.md` plus a dated
entry in `CONTEXT.md`; commit and push to `claude/practical-meitner-31k9ye`.

Starting now makes little sense: the new facts arrive tonight and early tomorrow — the #34/#35 scores and latencies,
the local chat's step-0 timings, the K2 dummy runs and its submission, the exp60 lab. Before them, research would only
repeat v3.

## Inputs to pull first (from the local chat, via git)
- `CONTEXT.md`: entries after 25 Sep 14:05 UTC (a, b, L34, L35, branch letter, K2 dummy gates, K2 submission/score,
  R6 trigger).
- `experiments/runtime_step0/*_timing.txt` (dummy per-clip timings).
- exp60 lab output JSON (forkmid audit, DeepCenter threshold arc on 6bba, insertion no-harm, linefit arc), if pushed.
- `research/wf_ideas_v3/browser_intel.md` updates (tie-break rule, submission GPU quota, new notebooks ≥ 0.954).

## Questions, in priority order
1. **Runtime.** From L34/L35 and the step-0 timings: an upper bound on the number of hidden clips N and on each
   build's runtime. Did R6 fire (N1 parrepair needed)? Is REPAIR_DEADLINE_S = 34200 enough, and does
   DIVINS_DEADLINE_S = 28800 leave margin under 12 h?
2. **Branch check.** Is the branch (A–E) the local chat chose consistent with the pre-registered rules R1–R2?
   Flag deviations only; do not rewrite the rules.
3. **exp60 lab.** Sanity-check the gates for K3 (forkmid ≥ 4.5 µm) and K3b (DeepCenter threshold chosen on 6bba):
   sample sizes, per-embryo sign, whether the arc has a plateau or a single-point optimum.
4. **Rank logic.** Evidence on how Kaggle breaks ties on the private LB (earlier submission?) and whether the 0.953
   block will stay together on private. Decides how much F1 must differ from x138.
5. **New public intel.** Any public notebook or post ≥ 0.954 since 25 Sep 11:40 UTC (WebSearch; kaggle.com is blocked
   here, so ask the local chat's browser for specific pages).

Output: a one-page `day2_findings.md` with concrete recommendations for the day's LB slots (S4–S6 on 26 Sep, S7–S11
on 27 Sep). No new mechanisms after 27 Sep 12:00 UTC (rule R8).
