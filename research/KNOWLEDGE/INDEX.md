# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 13: state as of 2026-09-27 ~01:45 UTC, git HEAD 5e57346 (round 13 committed in 3d48d35, timers in 5e57346); probes 39-42 all PENDING at the 01:39:32Z poll. Previous curation: 12 (~21:30 UTC 26 Sep, 9beb9f0). Hashes older than 26 Sep 10:15 are pre-rewrite (`experiments/git_rewrite_map_2026-09-26.txt`). All times are UTC; every line cites its source.
Deadline 29 Sep 23:59; the user ticks finals MANUALLY by 29 Sep 20:00. `CONTEXT.md` anchors at 5e57346:
- Rules: PRE-REG v3 l.1576-1736 (R7-R9 l.1665-1673); E10 PORT RULE l.2138-2147, P4c l.2257-2317; E10 v2 PROPOSED l.2352-2361; LADDER + L9 l.2407-2424.
- 26 Sep evening: ROUND 12 RECORD l.2475; RULE RECONCILIATION l.2502-2529; RETRAIN PAUSED l.2539; CAP-6 l.2545; E10 HARDENING l.2550; PRIVATE-READ v2 l.2570; RESUME POINT 22:46 l.2599-2622 (partly stale, alert 5).
- 27 Sep: probe 42 l.2623; ROUND 13 RECORD l.2626-2663; LADDER PRE-SCORE REGISTRATION l.2664-2721; EXP71/EXP72 GOVERNANCE l.2722-2746; TIMERS l.2747-2749; `## 9. Literature` l.2750.

## STATE IN 10 LINES

1. **Finals TICKED 2/2**: #37 K2 exp58 (56563521) = **0.954** and #38 twin exp58n (56563534) = **0.953**. API SELECTED was last read at 20:04:35Z, not since probes 39-42. Sources: `experiments/RESULTS.md` l.70-71; `CONTEXT.md` l.2599-2602, l.2646-2648; `DECISIONS.md` §2 l.374.
2. **LB #229 of 3,935** at 22:46Z (214 teams >= 0.955); info only, private (~71%) decides. Our LB row counts only SCORED submissions. Sources: `CONTEXT.md` l.2626-2663 (2); `FACTS.md` F-LB-15.
3. **Base** = x138 + safetail + lowrefine + gated DaughterNet insertion (K2); the 8.0 h insertion gate is per clip. Sources: `CONTEXT.md` l.2407-2409, l.2661-2663 (7); `IDEAS.md` I-001 (l.168).
4. **Ladder 4/4 submitted, none scored:** probes 39 exp70e (56589025), 40 exp70a (56589065) and 41 exp70d (56589423) expected ~04:37-05:11Z; 42 exp70b (56592350) ~07:27-08:30Z. exp70g (cap 6) dropped after its lab arm read -0.00057. 4 slots left on 27 Sep. Sources: `experiments/lb_poll/poll.log` 01:39:32Z; `CONTEXT.md` l.2534, l.2545-2549, l.2623-2625; `IDEAS.md` I-302..I-306 (l.111-115).
5. **Ladder rules registered before any score (01:31Z):** L5v2 = at most ONE combo (POS base + fm45, only if fm45 is POS; P ~0.01-0.03). Attribution = passed-team UP test on fresh LB downloads keyed on SubmissionCount, which needs the read-only watcher (**not written; must run by 04:10Z**). Stop rule; slot priority E10 > error resubmit > combo > exp72 > empty. Sources: `CONTEXT.md` l.2664-2710; `IDEAS.md` I-307, I-327 (l.116, l.123).
6. **Finals rule = insertion hedge (L9 + reconciliation):** no eligible V* -> {#37, #38}; V* displays >= 0.955 -> {V*, #38}; **A-only extension**: exp70a displays 0.954 with an attributable UP and its insertion gate did not fire -> {exp70a, #38} (dropped if the watcher does not run); E10 port without insertion -> {PORT, #37}. Any change needs the user's re-tick by 29 Sep 20:00. Sources: `CONTEXT.md` l.2502-2529, l.2690-2699; `DECISIONS.md` §2 l.374, §2h l.642; `IDEAS.md` I-297, I-328 (l.96, l.100).
7. **Retrain (exp71 -> exp72):** exp71 is READY; its push is blocked until the user's explicit yes (R9), and the "R8 lifted" reading is SUSPENDED. exp72 is class C (public only) unless Q3 = yes, and then a G2 held-out veto must land by 29 Sep 12:00. GPU quota: 07:55 of 30 h used. Sources: `CONTEXT.md` l.2539-2544, l.2722-2746; `IDEAS.md` I-119, I-330 (l.318, l.331).
8. **E10:** v1 (>= 0.956) is in force and not met at 22:46Z; no public notebook is above 0.953. v2 (>= 0.954) is PROPOSED and lapses without an OK by 27 Sep 12:00. Hardening logged 22:46Z. The P1 timer is now 2e87e414; it defers inside the 04:10-06:45Z API quiet window. Sources: `CONTEXT.md` l.2550-2569, l.2626-2632 (1), l.2747-2749; `experiments/e10_watch/20260926T2246Z.txt`; `IDEAS.md` I-286 (l.152).
9. **Next decision points:** 04:10Z watcher + S0; ~04:40-05:15Z D1 read of 39-41 (+ SELECTED re-read, I-312 closure); 07:30Z push 65b1b746 (E10 v2, Q1-Q3, R8 cap, pair rows, laptop); ~07:30-08:30Z D2 read of 42; **12:00Z R8 cutoff + E10 v2 lapse**; 28 Sep 12:00 F1 consolidation; 29 Sep 02:00 last ladder submit, 19:00 L9 read, 20:00 ticks. Sources: `WATCHLIST.md` NEXT 24 H l.47, LATER l.83; `CONTEXT.md` l.2700-2710 (5).
10. **Ideas ledger:** 335 ideas (lb-tested 41, lab-tested 21, refuted 176, deferred 37, in-plan 59, open 1). Round 13 found nothing that reaches the R8 bar. Strict orphan: I-233. Sources: `IDEAS.md` l.11, ORPHANS l.496; `CONTEXT.md` l.2652-2660 (6).

## WHERE THINGS ARE

Knowledge base `research/KNOWLEDGE/` (written only by `experiments/workflows/biohub-curator.js`):
- `INDEX.md` (this page); `CHANGES.md` (per-curation deltas v4, 2-13).
- `IDEAS.md` + `ideas.json`: I-001..I-335 in 13 clusters (FINALS l.58, LADDER l.104, BASE l.127, RUN l.162, LOC l.201, DIV l.232, MODEL l.290, NODES l.334, INFER l.368, EF l.389, LINK l.409, VALID l.440, TESTSET l.478, ORPHANS l.496); delta l.13; per-ID changes in `ideas.json` meta.curations[n=13].
- `FACTS.md`: §1 metric l.100 ... §7 lab-to-LB l.246; CONTRADICTIONS l.294 (new C-96..C-103, l.393-400).
- `DECISIONS.md`: probes §1 l.70 (P39-P42 added); gates G01-G43 §1b l.231; finals §2 l.296 (c13 snapshot l.374); E10 §2f l.518; OC §2g l.611; ladder + L9 + L5v2 §2h l.642; R1-R10 §3 l.665.
- `WATCHLIST.md`: OVERDUE l.36, NEXT 24 H l.47 (W132-W142, T51-T61), LATER l.83, INSIGHTS l.123 (I125-I135). Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,13}/`.

Key sources (repo root):
- `CONTEXT.md`: single source of truth; newest §14 entry l.2747-2749 (01:32Z), just above `## 9. Literature` l.2750.
- LB: `experiments/RESULTS.md` (probes to 38; rows 39-42 not yet added); `experiments/lb_poll/poll.log`, `ledger.md` (39-42); `experiments/lb_poll/ladder_watch/` (to be created by the watcher); `experiments/e10_watch/20260926T{1620,1701,2001,2246}Z.txt`.
- Kernels: finals `experiments/exp58_x138_safe_lowref/` (#37), `experiments/exp58n_x138_safe_lowref/` (#38); ladder `experiments/exp70{a_k2_lp30,d_k2_dc030,e_k2_lp30_dc030,b_k2_fm45,g_k2_cap6}/probe.json`; retrain `experiments/exp71_secft_all/` (NEVER_SUBMIT.md).
- Tools: `tools/build_probe_kernel.py` (per-clip insertion gate l.1415-1422; `--patch secswap` ea5637e), `tools/runtime_ledger.py` (exp70* -> safetail l.76), `tools/e10_port_gate.py`, `tools/e10_snapshot.py`, `tools/dummy_gates.py`.
- Rounds: `research/wf_ideas_v4/round13/` (`REPORT.md`, `report.json` R13-A0..A9, `scan_*.json`, `v_*.json`), `round12/`..`round8/`; `research/wf_ideas_v4/reach0955/` (ladder, retrain, intel, `ins_cap6.json`); prompt `experiments/workflows/biohub-research-round.js` (stale l.38, l.40).
- Background: `research/wf_ideas_v3/FINAL_REPORT.md`, `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `PROMPT_FRIEND_A.md` (stale), `PROMPT_FRIEND_C.md`, `TEAM.md`, `research/discussions_summary.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-327 | Attribution protocol + read-only `experiments/lb_poll/ladder_watch.py` | In-plan, at risk: not written. Dry-run the parser on the 22:46Z CSV; start by 04:10Z, stop at 06:45Z | `IDEAS.md` l.123 |
| I-302 / I-307 | K2 ladder; L5v2 = at most one combo (exp70c/h/f) | D1 (39-41) ~05:15Z, D2 after 42; combo submit by ~09:30Z, else log "ladder ends (5a)" | `IDEAS.md` l.111, l.116 |
| I-328 | A-only 0.954-UP extension -> {exp70a, #38} | Needs the watcher + exp70a's own ledger line 'gate did NOT fire'; the user re-ticks | `IDEAS.md` l.100 |
| I-286 / I-299 / I-315 | E10 v2 (>= 0.954); E10 pair rows; 07:30Z push | User OK before 12:00Z; without it, log 'E10 v2 not in force' | `IDEAS.md` l.152, l.98, l.99 |
| I-119 / I-330 | exp71 FT -> exp72 probe; G2 held-out finals veto | Blocked until the user answers Q1-Q3; a yes by ~09:00Z is needed to score on 27 Sep | `IDEAS.md` l.318, l.331 |
| I-312 / I-258 | "LB tracks node count" closure; API SELECTED re-read | One line each at the first probe read (~04:40-05:00Z) | `IDEAS.md` l.121, l.90 |
| I-229 / I-283 | 29 Sep tick checklist; private-read v2 + ladder addendum L1-L5 | In-plan; L9 read 29 Sep 19:00Z | `IDEAS.md` l.80, l.470 |
| I-323 / I-324 / I-233 | Corwin secondary; coord-inject; poller error_description | Deferred only through a general sentence; close each by name at R8 12:00Z | `IDEAS.md` l.330, l.229, l.186 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/13/{ideas,facts,watch}.json`)

1. [now] **Ladder watcher (R13-A2) not written.** Write `experiments/lb_poll/ladder_watch.py` (read-only, 60 s from lb_poll, 429 backoff), dry-run it on the 22:46Z CSV (#229, SubmissionCount 40) and start it from the repo root by **04:10Z**. S0 = the 03:04Z timer snapshot if its SubmissionCount == 40, else a download at ~04:10Z. Without it the A-only extension is DROPPED and 0.954 cannot count as POS; 39 and 40 will likely co-complete (equal displays -> both NEU). Sources: `CONTEXT.md` l.2676-2699, l.2747-2749; `round13/report.json` R13-A2; `WATCHLIST.md` W134.
2. [now] **API quiet window 04:10-06:45Z** (no agent API calls). The round-14/15 prompts must say so; `experiments/workflows/biohub-research-round.js` l.38/l.40 are still stale ('finals decided... E10 >= 0.956', '~4 h headroom'). The E10 timer already defers (2e87e414). Sources: `round13/report.json` R13-A8; `WATCHLIST.md` W140, W71/W118; `CONTEXT.md` l.2747-2749.
3. [today] **The 07:30Z push (65b1b746)** is the only channel for: E10 v2 (lapses 12:00Z), exp71/exp72 Q1-Q3 (yes by ~09:00Z), the R8 cap for the last ladder submit (default 29 Sep 02:00), the E10 pair rows (I-299), laptop/session to 29 Sep 20:00, and any re-tick. Log 'sent' or the not-sent result, and each answer with `date -u`. Sources: `CONTEXT.md` l.2599-2606, l.2722-2749; `round13/report.json` R13-A4; `IDEAS.md` I-315.
4. [today] **At D1 (~04:40-05:15Z):** log 'API SELECTED 2/2 [56563521, 56563534] at hh:mmZ (after probes 39-42)' (last read 20:04:35Z); log the I-312 closure (R13-A6 wording); log each watcher event (S0/S1, SubmissionCount, verdict; whether an ERROR increments the count); add RESULTS.md rows P39-P42 as they score. Sources: `CONTEXT.md` l.2646-2648, l.2682-2689; `round13/report.json` R13-A5, plan_issues (10); `FACTS.md` F-LB-15; `experiments/RESULTS.md` l.71.
5. [today] **The 22:46Z RESUME POINT is partly stale:** "combos after two rungs" -> L5v2; "exp72 competes with V*" -> class C unless Q3 = yes; timers c7cd2e6b/2f0d1fa1 -> 65b1b746/2e87e414. Write a new RESUME POINT after D1. The MEMORY index line seen by subagents is also stale. Sources: `CONTEXT.md` l.2599-2622 vs l.2664-2749; `FACTS.md` C-75.
6. [today] **exp70g has no NEVER_SUBMIT.md** (exp71 has one), so the R12-A3(d) folder guard would not stop it. Add the file or log 'never submit exp70g'. Sources: `experiments/exp70g_k2_cap6/` (3 files); `WATCHLIST.md` W142.
7. [today] **exp72, if Q3 = yes:** G2 (44b6-only FT + SECFT_PREFIX, K2 tail on 39 held-out 6bba clips) must land by 29 Sep 12:00 with pooled >= -0.0005, which is one more ~4.5 GPU-h run. The node gate is necessary only (the exp23 swap was +0.62% nodes and lost 0.007). Prepare G2 locally only; push nothing before explicit answers. Sources: `CONTEXT.md` l.2722-2746; `FACTS.md` F-TRN-41 [c13], C-102; `IDEAS.md` I-330.
8. [before-finals] **Re-tick:** a ladder pair ({V*, #38} or {exp70a, #38}) is only a recommendation until the user re-ticks by 29 Sep 20:00; otherwise {#37, #38} stays. Timers 012fa6dd / 328f7392 / 18ff4796 verify SELECTED. Sources: `CONTEXT.md` l.2509-2521, l.2693-2699; `DECISIONS.md` §2 l.374.
9. [before-finals] **Closures and hygiene:** at R8 12:00Z close I-323 and I-324 by name (post-deadline) and I-233 in one line. Still missing: the W57 family (CONTEXT l.22, out_valid, efpost, 33.1%) and the fix to `research/wf_ideas_v4/round9/LESSONS_draft.md` l.7 ('~29%' stated as a fact). Sources: `CONTEXT.md` l.2658-2660; `WATCHLIST.md` W57, W98; `IDEAS.md` ORPHANS l.496.
10. [info] Cite only the corrected dummy node counts (K2 121,252; exp70e 120,707; exp70a 120,719). F-TRN-41 now says +0.62% nodes, not +3.9%. Order inside the 0.953 block is not by submission time (caveat for the v2 tie read). Sources: `CONTEXT.md` l.2537-2538; `FACTS.md` C-96, F-TRN-41; `research/wf_ideas_v4/round13/scan_browser.json`.

**RESOLVED since the watch pass (01:35Z):** W133 pre-score registration (`CONTEXT.md` l.2664-2721, 3d48d35); W135 governance (l.2722-2746); W132/W139 commit of round13/REPORT.md, e10_watch 22:46Z, poll.log and ledger (3d48d35); W136 morning timer 65b1b746, and 2f0d1fa1 -> 2e87e414 with quiet-window deferral (5e57346, l.2747-2749).

## HOW TO USE

- "Score of probe N, what changed?" -> `DECISIONS.md` §1, `experiments/RESULTS.md`, `experiments/lb_poll/poll.log` (39+), `experiments/<exp>/probe.json`.
- "Which files are the finals / what if a rung displays 0.954 or 0.955?" -> `DECISIONS.md` §2 (l.374) + §2h, `CONTEXT.md` l.2502-2529 and l.2664-2710, `IDEAS.md` FINALS + LADDER.
- "Can exp72 be submitted or become a final?" -> `CONTEXT.md` l.2722-2746, `IDEAS.md` I-119/I-330, `WATCHLIST.md` W128.
- "What if a public successor appears?" -> `DECISIONS.md` §2f, `CONTEXT.md` l.2138-2147, l.2257-2317, l.2352-2361, l.2550-2569; `IDEAS.md` I-286.
- "Which rule decides this?" -> `DECISIONS.md` §3; `FACTS.md` §5 + CONTRADICTIONS; `CONTEXT.md` l.1576-1736.
- "Was idea X tried?" -> search its mechanism in `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md`. "Which gate closed it?" -> `DECISIONS.md` §1b.
- "What is next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`. Old hash -> `experiments/git_rewrite_map_2026-09-26.txt`.
- Anything newer than ~01:45Z 27 Sep -> the tail of `CONTEXT.md` §14 (above `## 9.`), `experiments/lb_poll/poll.log`, `experiments/lb_poll/ladder_watch/`, newest `research/wf_ideas_v4/round*/`.
