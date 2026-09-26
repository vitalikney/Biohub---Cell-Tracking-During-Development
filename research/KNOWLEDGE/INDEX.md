# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 12: state as of 2026-09-26 ~21:30 UTC, git HEAD 9beb9f0, plus the untracked `research/wf_ideas_v4/round12/` (report.json 21:01Z, R12-A0..A10 NOT yet applied). Previous: curation 11 (~17:50 UTC, df6996e). Hashes from before 26 Sep 10:15 are pre-rewrite: `experiments/git_rewrite_map_2026-09-26.txt`. All times UTC; every line cites its source.
Deadline 29 Sep 23:59; finals ticked MANUALLY by 29 Sep 20:00. `CONTEXT.md` anchors (at 9beb9f0): PRE-REG v3 l.1576-1736 (R7-R9 l.1665-1673); E10 PORT RULE l.2138-2147 + P4c l.2257-2317; RESUME POINT 13:27 l.2205-2212 (STALE); ROUND 11 RECORD l.2342-2351; E10 v2 PROPOSED l.2352-2361; TIMERS l.2362-2367; COMBO-ORACLE l.2368-2379; USER 20:30/20:33/20:34 l.2380-2396; DRY RUN l.2397-2406; LADDER + L9 l.2407-2424; INTEL l.2425-2444; PROBES 39/40 l.2445-2453; REACH0955 PLAN 21:21 l.2454-2474; `## 9. Literature` l.2475.

## STATE IN 10 LINES

1. **Finals TICKED 2/2**: #37 K2 exp58 (56563521) = **0.954**, #38 twin exp58n (56563534) = **0.953**; API SELECTED checked 20:04:35Z. Sources: `experiments/RESULTS.md` l.70-71; `research/wf_ideas_v4/round12/report.json` R12-A2 (3); `DECISIONS.md` §2 l.320.
2. **Rank #217 of 3,935** at 20:01Z (info only; private ~71% decides). Sources: `experiments/e10_watch/20260926T2001Z.txt`; `FACTS.md` F-LB-02.
3. **User 20:30-20:34Z:** reach 0.955+, public knob-ladder ban lifted (CONTEXT says "R7"; in PRE-REG v3 it is R9's ladder clause, C-84), finals = one for public + one for private, then asleep / autonomous. Sources: `CONTEXT.md` l.2380-2396; `FACTS.md` C-84; `IDEAS.md` I-295 (l.105).
4. **Base** = x138 + safetail + lowrefine + gated DaughterNet insertion (K2), rebuild sha 1f1ddb6d. Sources: `CONTEXT.md` l.2407-2409; `IDEAS.md` I-001.
5. **Ladder (NEW):** exp70a lp30, exp70d dc0.30, exp70e both, exp70b fm45, exp70g cap6 built. **Probe 39 = exp70e** (56589025, 21:15:23Z) and **probe 40 = exp70a** (56589065, 21:17:47Z) PENDING at poll 21:18:31Z; exp70d = last 26 Sep slot (hard 23:50Z); first scores ~04-08Z. Sources: `CONTEXT.md` l.2407-2453; `experiments/lb_poll/poll.log` l.8682-8687; `IDEAS.md` I-302..I-307 (l.120-125).
6. **Finals rule L9** (kept at 21:21): an eligible V* (display >= 0.955, L_hi <= 9.0 h, knobs >= 0.954) -> pair {V*, #38}; else {#37, #38}. Round 12's insertion-hedge table (I-297) and rule reconciliation (I-301) are NOT in CONTEXT. Sources: `CONTEXT.md` l.2419-2423, l.2461-2466; `DECISIONS.md` §2h l.589; `IDEAS.md` l.106-107, l.474.
7. **Retrain line started** 21:21 on the main session's reading of the user's words (one run exp71 + one probe exp72, R8 lifted for it); round 12 and the plan agent say R9 needs an explicit yes. Prep only so far. Sources: `CONTEXT.md` l.2466-2472; `research/wf_ideas_v4/reach0955/plan.notes.md`; `IDEAS.md` I-119 (l.324).
8. **E10:** v1 (>= 0.956) in force, not met at 20:01Z; v2 (>= 0.954) PROPOSED, lapses without an OK by 27 Sep 12:00; HF v3 dry run PASS (~45-60 min trigger-to-ready). No public code behind any 0.955-0.966 team. Sources: `CONTEXT.md` l.2352-2361, l.2397-2406, l.2437-2444; `IDEAS.md` I-026, I-286 (l.159), I-262 (l.153).
9. **Next decisions:** R12-A3 reconciliation NOW; round 13 ~22:30Z (ins_cap6 arm, I-311/I-312); exp70d by 23:50Z; S4 00:05Z exp70g vs exp70b; ladder reads ~04-08Z; morning message 07:30Z; **R8 + E10 v2 OK 27 Sep 12:00**; F1 consolidation 28 Sep 12:00; last ladder/port submit 29 Sep 02:00 (R8; L9 says 11:00, C-86); L9 read 29 Sep ~19:00; ticks 20:00. Sources: `WATCHLIST.md` NEXT 24 H l.71, LATER l.107; `round12/report.json` R12-A3..A7.
10. **Ideas ledger:** 326 ideas (lb-tested 41, lab-tested 21, refuted 172, deferred 31, in-plan 56, open 5). Strict orphan I-233. Source: `IDEAS.md` l.11, ORPHANS l.498.

## WHERE THINGS ARE

Knowledge base `research/KNOWLEDGE/` (written only by `experiments/workflows/biohub-curator.js`):
- `INDEX.md` (this page); `CHANGES.md` (per-curation deltas v4, 2-12).
- `IDEAS.md` + `ideas.json`: I-001..I-326 in 13 clusters (FINALS l.69, **LADDER l.113**, BASE l.134, RUN l.169, LOC l.208, DIV l.239, MODEL l.296, NODES l.339, INFER l.371, EF l.391, LINK l.411, VALID l.442, TESTSET l.480, ORPHANS l.498); delta l.13; per-ID changes `ideas.json` meta.curations[n=12].
- `FACTS.md`: §1 metric l.83 ... §7 lab-to-LB l.226; CONTRADICTIONS l.272 (C-84..C-95 new, l.359-370).
- `DECISIONS.md`: probes §1 l.60; lab gates G01-G40 §1b l.199; finals §2 l.261 (c12 snapshot l.330); READ TABLE §2b-§2e; E10 §2f l.471; OC §2g l.558; **ladder + L9 §2h l.589**; R1-R10 §3 l.607.
- `WATCHLIST.md`: OVERDUE l.60, NEXT 24 H l.71 (W113-W129), LATER l.107 (T40-T49), INSIGHTS l.144 (I107-I124).
- Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,12}/`.

Key sources (repo root):
- `CONTEXT.md`: single source of truth; newest §14 entry l.2454-2474 (21:21Z), above `## 9. Literature` l.2475.
- LB: `experiments/RESULTS.md` (probes to 38); `experiments/lb_poll/poll.log`, `experiments/lb_poll/ledger.md` (probes 39/40); `experiments/e10_watch/20260926T{1620,1701,2001}Z.txt`.
- Finals kernels: `experiments/exp58_x138_safe_lowref/` (#37), `experiments/exp58n_x138_safe_lowref/` (#38). Ladder: `experiments/exp70{a_k2_lp30,d_k2_dc030,e_k2_lp30_dc030,b_k2_fm45,g_k2_cap6}/probe.json`.
- Tools: `tools/build_probe_kernel.py` (uncommitted edit; secswap patch in prep), `tools/runtime_ledger.py` (exp70* -> safetail l.76, 34fdf40), `tools/e10_port_gate.py`, `tools/e10_snapshot.py`, `tools/dummy_gates.py`.
- Reach-0.955 work: `research/wf_ideas_v4/reach0955/` (r_/v_ ladder, retrain, intel; `plan.notes.md`; `discussions_2026-09-26.json`; `intel_0960_0966.json`).
- Rounds: `research/wf_ideas_v4/round12/` (untracked: `report.json` R12-A0..A10, `scan_*.json`, `v_*.json`); `round11/`..`round8/`; prompt `experiments/workflows/biohub-research-round.js` (stale l.37, l.40).
- Background: `research/wf_ideas_v3/FINAL_REPORT.md`, `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `PROMPT_FRIEND_A.md` (stale), `PROMPT_FRIEND_C.md`, `TEAM.md`, `research/discussions_summary.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-297 / I-301 | Insertion-hedge pair table + rule reconciliation (what was lifted, R8 02:00Z cap, per-submit checks) | In-plan, at risk. Log R12-A3 before exp70d; note probes 39/40 went out first | `IDEAS.md` l.107, l.474 |
| I-302..I-307 | K2 knob ladder (39 exp70e, 40 exp70a pending; exp70d next; L5 combos ~08:00Z only from positive singles) | In-plan; read each rung in poll.log | `IDEAS.md` l.120-125 |
| I-326 / I-306 | S4 at 00:05Z: exp70g cap6 (needs ins_cap6 arm + L9 class-B amendment) vs exp70b (skeptic NO-GO blind) | Decide before 00:05Z | `IDEAS.md` l.131, l.124 |
| I-119 | Distilled-secondary FT exp71 -> probe exp72 | Started on session reading; prep only until the user confirms; exp72 pair row open | `IDEAS.md` l.324 |
| I-286 / I-315 | E10 v2 PORT-ONLY; 07:30Z morning message (E10 v2, pair row, R8 lift, retrain, ticks) | Needs user OK by 27 Sep 12:00 | `IDEAS.md` l.159, l.110 |
| I-311 / I-312 | Justin PP-only 0.953 -> 0.956; "LB tracks node count" | Open; round 13: map to knobs (<= 2 rungs) or close | `IDEAS.md` l.129-130 |
| I-323 / I-324 | Corwin secondary (EV <= 0); yuki0731 coord-inject (unproven, runtime risk) | Open; take or close by R8 27 Sep 12:00 | `IDEAS.md` l.336, l.236 |
| I-283 / I-229 | Private-read pre-registration v2; 29 Sep tick checklist (L9 read 19:00Z) | In-plan; commit before any private score | `IDEAS.md` l.472, l.91 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/12/{ideas,facts,watch}.json`)

1. [now] **Log the R12-A3 RULE RECONCILIATION** with `date -u` before exp70d: lifted = R9 ladder clause (R7 hygiene + R9 retrain bar still hold); insertion-hedge table (L9 {V*, #38} vs {V*, #37} vs P6 {PORT, #37}); last submit 29 Sep 02:00Z (R8), not L9's 11:00Z; record that probes 39/40 went out before it but passed W6 and dummy checks. Sources: `round12/report.json` R12-A3, plan_issues (1)-(3); `FACTS.md` C-84, C-85, C-86; `WATCHLIST.md` W116.
2. [now] **Retrain consent:** the 21:21 "yes" reading conflicts with the plan agent's 21:15Z revision, v_retrain and R12-A3 (a). Push no training kernel until the user confirms; the morning message must say the line was started on the session's reading. Rename any retrain kernels away from exp70a/b. Sources: `CONTEXT.md` l.2466-2472; `research/wf_ideas_v4/reach0955/v_retrain.json` corrections; `WATCHLIST.md` W128, I108.
3. [now] **Pair rule for exp72:** 21:21 says retrain pairs with #37 (insertion in both finals); the hedge table has exp72 compete with V* while #38 stays. Settle before exp72 can score; ask the user. Sources: `CONTEXT.md` l.2465-2466; `round12/report.json` R12-A3 (b); `IDEAS.md` I-297.
4. [now] **S4 00:05Z:** exp70b is skeptic NO-GO as a blind rung; exp70g is outside L9's knob set (class C, never a final) unless an L9 class-B amendment is logged before it scores. Sources: `research/wf_ideas_v4/reach0955/v_ladder.json` no_go_items; `CONTEXT.md` l.2419-2420, l.2473-2474; `FACTS.md` C-95; `WATCHLIST.md` W125.
5. [now] **API budget:** 429s at 20:36:50Z; one poller only (two python PIDs seen 21:05Z); re-check W6 (header < 15 min) before every submit; x138 crashes on DET_THRESHOLD != 0.965 and ignores --set SECONDARY_*. Sources: `experiments/lb_poll/poll.log` l.8497; `round12/report.json` R12-A5; `WATCHLIST.md` W118, I114; `FACTS.md` C-90.
6. [today] **Hygiene (R12-A0/A1/A2/A8):** save round12/REPORT.md from R12-A0; ROUND 12 RECORD; `rm -rf experiments/_pytest_oc_k2` (never push); commit as the user, no trailer; new RESUME POINT (13:27 is stale) + MEMORY line; fix round prompt l.37/l.40. Sources: `round12/report.json` R12-A0..A2, R12-A8; `WATCHLIST.md` W113-W115, W121.
7. [today] **Timers + morning message:** create the 07:30Z push and replace 2bd08ad3 (R12-A6), log ids; send R12-A7 (E10 v2, pair row, R8 lift, retrain, ticks) and log answers. Sources: `round12/report.json` R12-A6, R12-A7; `WATCHLIST.md` W119, W120.
8. [today] **K2 dummy node reference:** 122,252 (CONTEXT) vs 121,252 (v_retrain/v_intel); recount once before the exp72 node gate. Sources: `CONTEXT.md` l.2446, l.2451; `research/wf_ideas_v4/reach0955/v_retrain.json` RT-4.
9. [before-finals] **PRIVATE-READ PRE-REG v2** (I-283) and transfer table (I-316) committed before the first private score (latest 29 Sep 23:00Z); ladder files are post-hoc. Sources: `round12/report.json` R12-A9; `WATCHLIST.md` W122.
10. [info] y3uanm's 0.956 is not tied to the FT recipe (quick saves); discussion notes label UTC+3 as "Z"; close I-233 with one line. RESOLVED since the watch pass: runtime ledger exp70* -> safetail (34fdf40, `tools/runtime_ledger.py` l.76). Sources: `FACTS.md` C-88, C-94; `WATCHLIST.md` I116, W127.

## HOW TO USE

- "Score of probe N, what changed?" -> `DECISIONS.md` §1, `experiments/RESULTS.md`, `experiments/lb_poll/poll.log` (39+), `experiments/<exp>/probe.json`.
- "Which files are the finals / what if a ladder rung hits 0.955?" -> `DECISIONS.md` §2 (l.330) + §2h, `CONTEXT.md` l.2407-2424, l.2461-2466, `IDEAS.md` LADDER + FINALS.
- "What if a public successor appears?" -> `DECISIONS.md` §2f, `CONTEXT.md` l.2138-2147, l.2257-2317, l.2352-2361, `IDEAS.md` I-286/I-314.
- "Which rule decides this?" -> `DECISIONS.md` §3; `FACTS.md` §5 + C-84..C-86; `CONTEXT.md` l.1576-1736.
- "Was idea X tried?" -> search its mechanism in `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md` + CONTRADICTIONS. "Which gate closed it?" -> `DECISIONS.md` §1b.
- "What is next / overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`. Old hash -> `experiments/git_rewrite_map_2026-09-26.txt`.
- Anything newer than ~21:30Z 26 Sep -> tail of `CONTEXT.md` §14 (above `## 9.`), `experiments/lb_poll/poll.log`, newest `research/wf_ideas_v4/round*/` and `reach0955/`.
