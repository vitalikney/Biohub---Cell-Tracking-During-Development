# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 14: state as of 2026-09-27 ~02:25 UTC. Git HEAD f24ff72 (the read-only ladder watcher, pushed 01:54:14Z) plus the uncommitted `research/wf_ideas_v4/round14/` and `experiments/e10_watch/20260927T0147Z.txt`. Probes 39-42 were all PENDING at the 02:19:40Z poll. Previous curation: 13 (~01:45 UTC, 5e57346). Hashes older than 26 Sep 10:15 are pre-rewrite (`experiments/git_rewrite_map_2026-09-26.txt`). All times are UTC, and every line cites its source.
Deadline 29 Sep 23:59; the user ticks finals MANUALLY by 29 Sep 20:00. `CONTEXT.md` is **unchanged since 5e57346**. Its last entry is TIMERS UPDATED at l.2747-2749 (01:32Z), just above `## 9. Literature` at l.2750. Anchors:
- Rules: PRE-REG v3 l.1576-1736 (R7-R9 at l.1665-1673); E10 PORT RULE l.2138-2147; P4c l.2257-2317; E10 v2 PROPOSED l.2352-2361; LADDER + L9 l.2407-2424.
- 26 Sep evening: RULE RECONCILIATION l.2502-2529; E10 HARDENING l.2550; PRIVATE-READ v2 l.2570; RESUME POINT 22:46 l.2599-2622 (partly stale).
- 27 Sep: ROUND 13 RECORD l.2626-2663; LADDER PRE-SCORE REGISTRATION l.2664-2721; EXP71/EXP72 GOVERNANCE l.2722-2746. No round-14 entry exists yet.

## STATE IN 10 LINES

1. **Finals are TICKED 2/2:** #37 K2 exp58 (56563521) = **0.954** and #38 twin exp58n (56563534) = **0.953**. API SELECTED was last read at 20:04:35Z. The next read is the first API touch after 06:45Z (~07:30Z), no longer at D1. Sources: `experiments/RESULTS.md` l.70-71; `DECISIONS.md` §2 [c14] snapshot l.400; `FACTS.md` F-RUL-12, C-106.
2. **LB rank #242 of 3,937** at 01:47:50Z (was #229). We are 16th of 97 in the 0.954 block, and 226 teams are >= 0.955. This is info only; the private LB (~71%) decides. Sources: `experiments/e10_watch/20260927T0147Z.txt`; `research/wf_ideas_v4/round14/scan_browser.json`; `FACTS.md` F-LB-15 [c14].
3. **Base** = x138 + safetail + lowrefine + gated DaughterNet insertion (K2). The hedge's '+0.006' for insertion is IN-SAMPLE; the honest OOF figure is +0.0019, with P(<0 private) 0.10-0.20. Sources: `CONTEXT.md` l.2407-2409; `research/wf_ideas_v4/round14/report.json` R14-A6 (5); `FACTS.md` F-TRN-44, C-105.
4. **Ladder: 4 of 4 submitted, none scored.** Probes 39 exp70e (56589025), 40 exp70a (56589065) and 41 exp70d (56589423) are expected ~04:33-05:00Z. Probe 42 exp70b (56592350) is expected ~07:45-08:30Z. The 8.0 h L_hi marks are e 05:15:23Z, a 05:17:47Z, d 05:38:33Z and b 08:05:50Z. Sources: `experiments/lb_poll/poll.log` 02:19:40Z; `DECISIONS.md` §1 P39-P42 [c14] l.125-128; `report.json` R14-A3.
5. **Ladder watcher: written, NOT running.** The code (`experiments/lb_poll/ladder_watch.py`, 35 tests) is not fail-soft. `experiments/lb_poll/ladder_watch/` and `run_ladder_watch.sh` do not exist yet. S0 = the 0147Z snapshot; the registered '03:04Z snapshot' never existed. The hard cap must be passed as 11:30Z; the code default is 09:40Z. If the watcher is not live by 04:10Z, the A-only extension is DROPPED. Sources: `FACTS.md` F-RUN-27, C-104, C-108; `report.json` R14-A1; `WATCHLIST.md` W134.
6. **Finals rule = insertion hedge + L9, applied mechanically by READ SHEET v1 (R14-A3; codes NEG/N4/U4/P5/ERR):** No eligible V*: keep {#37, #38}. V* displays >= 0.955: {V*, #38}. A-only case (exp70a displays 0.954, has an attributable UP, and its ledger says the gate 'did NOT fire'): {exp70a, #38}. E10 port: {PORT, #37}. Every change needs the user's re-tick. Sources: `CONTEXT.md` l.2502-2529, l.2690-2699; `DECISIONS.md` §2h l.674 (rows l.696-699); `IDEAS.md` I-302, I-328.
7. **Retrain (exp71 -> exp72):** exp71 is READY but its push is blocked until the user explicitly says yes (R9). exp72 is class C unless Q3 = yes. The evidence line is now **0/4** FT-weight swaps on public stacks, and the exact exp72 setup is untested. Sources: `CONTEXT.md` l.2722-2746; `report.json` R14-A4; `FACTS.md` F-TRN-41 [c14]; `IDEAS.md` I-119, I-106.
8. **E10:** v1 (>= 0.956) is in force. P1 at 01:47Z was NOT met (largest P2 group 3). amanatar is RUNNING a renumbered 'Version 1 of 6'; a score there is a look signal only. v2 (>= 0.954) is PROPOSED and lapses at 12:00Z without an OK. Timer 2e87e414 takes the next P1 at >= 06:45Z. Sources: `experiments/e10_watch/20260927T0147Z.txt`; `DECISIONS.md` §2f [c14] l.637; `report.json` R14-A9.
9. **Next decision points:** 03:30-03:45Z (hard 04:10Z): launch the watcher. Hard 04:25Z: pre-score notes committed and pushed. 04:10-06:45Z: API quiet window. Liveness checks at 04:20, 05:20 and 06:30Z. D1 at ~04:45-05:40Z. 07:30Z: push 65b1b746 and the SELECTED read. D2 at ~07:45-08:30Z. **12:00Z: R8 cutoff and E10 v2 lapse.** 28 Sep 12:00 F1 consolidation; 29 Sep 02:00 last ladder submit; 29 Sep 20:00 ticks. Sources: `WATCHLIST.md` NEXT 24 H l.56, LATER l.99.
10. **Ideas ledger:** 340 ideas (lb-tested 41, lab-tested 21, refuted 177, deferred 38, in-plan 61, open 2). Nothing reaches the R8 bar. The only strict orphan is I-233. Sources: `IDEAS.md` l.59, CHANGES (14) l.61, ORPHANS l.556.

## WHERE THINGS ARE

The knowledge base lives in `research/KNOWLEDGE/` and is written only by `experiments/workflows/biohub-curator.js`:
- `INDEX.md` is this page. `CHANGES.md` holds the per-curation deltas (v4, then 2-14).
- `IDEAS.md` + `ideas.json`: ideas I-001..I-340 in 13 clusters. Cluster starts: FINALS l.113, LADDER l.159, BASE l.184, RUN l.219, LOC l.258, DIV l.289, MODEL l.347, NODES l.391, INFER l.425, EF l.446, LINK l.466, VALID l.497, TESTSET l.538, ORPHANS l.556. Per-ID changes are in `ideas.json` meta.curations[n=14].
- `FACTS.md`: §1 metric l.109, §3 LB l.147, §4 runtime l.167, §5 rules l.199, §6 models l.222, §7 lab-to-LB l.257. CONTRADICTIONS start at l.306 (C-104..C-110 at l.413-419).
- `DECISIONS.md`: probes §1 l.79; gates §1b l.247; finals §2 l.312 (c14 snapshot l.400); E10 §2f l.544; OC §2g l.643; ladder/L9 §2h l.674; R1-R10 §3 l.701.
- `WATCHLIST.md`: OVERDUE l.45, NEXT 24 H l.56 (W134, W141, W143-W150), LATER l.99, INSIGHTS l.136 (I136-I148). Curator logs are in `research/KNOWLEDGE/_curation/{v4,2,...,14}/`.

Key sources (paths from the repo root):
- `CONTEXT.md`: the single source of truth (see the anchors above).
- LB records: `experiments/RESULTS.md` (rows up to P38; rows 39-42 not added yet). `experiments/lb_poll/poll.log` and `ledger.md`: probes 39-42. `experiments/lb_poll/ladder_watch.py`: the watcher. Its output goes to `ladder_watch/` (`watch.log`, `calls.jsonl`); read those files and never open its `state.json`. `experiments/e10_watch/20260927T0147Z.txt`: the newest E10 snapshot, which is also S0.
- Kernels: finals `experiments/exp58_x138_safe_lowref/` (#37) and `experiments/exp58n_x138_safe_lowref/` (#38); ladder `experiments/exp70{a_k2_lp30,d_k2_dc030,e_k2_lp30_dc030,b_k2_fm45,g_k2_cap6}/probe.json`; retrain `experiments/exp71_secft_all/` (NEVER_SUBMIT.md).
- Tools: `tools/build_probe_kernel.py`, `tools/runtime_ledger.py`, `tools/e10_port_gate.py`, `tools/e10_snapshot.py`.
- Rounds: `research/wf_ideas_v4/round14/` (UNTRACKED): `report.json` R14-A0..A9 and `scan_*.json`; there is no REPORT.md yet. `round13/`..`round8/`, and `research/wf_ideas_v4/reach0955/`. The round prompt is `experiments/workflows/biohub-research-round.js`. Its l.37 would make the browser agent call the API.
- Background: `research/wf_ideas_v3/FINAL_REPORT.md`, `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v4/round9/LESSONS_draft.md`, `PROMPT_FRIEND_C.md`, `TEAM.md`, `research/discussions_summary.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-327 | Attribution protocol + read-only ladder watcher | In-plan, at risk: written (f24ff72) but not launched. Launch it as a restart loop, S0 = 0147Z, cap 11:30Z | `IDEAS.md` l.178 |
| I-302 / I-307 | K2 ladder; L5v2 = at most one combo | D1 and D2 by READ SHEET v1. The combo needs a POS base and fm45 POS; submit by ~09:30Z (hard 28 Sep 02:00) | `IDEAS.md` l.166, l.171 |
| I-328 | A-only 0.954-UP extension -> {exp70a, #38} | Needs the live watcher and the ledger text 'did NOT fire'. An UNPROVEN L_hi counts as a miss by rule | `IDEAS.md` l.155 |
| I-315 / I-286 / I-299 | 07:30Z push (variants P-A/P-B/P-C); E10 v2; E10 pair rows | The push carries the corrected hedge and 0/4 lines. E10 v2 needs an OK before 12:00Z | `IDEAS.md` l.154, l.209, l.153 |
| I-119 / I-330 / I-106 | exp71 -> exp72 FT secondary; G2 veto; exp23-with-public-primary (reopened, untested) | Blocked until Q1-Q3; a yes is needed by ~09:00Z | `IDEAS.md` l.375, l.388, l.362 |
| I-258 / I-312 | API SELECTED re-read; closure of 'LB tracks node count' | SELECTED at ~07:30Z (after 06:45Z); I-312 closes after probe 40 reads | `IDEAS.md` l.145, l.176 |
| I-336 / I-338 / I-252 | HINDSIGHT GUARD commit; rule-register template; LESSONS R14L-1..5 | Apply after 12:00Z. The guard must be PUSHED before the first private score (29 Sep < 23:00Z) | `IDEAS.md` l.533, l.535, l.522 |
| I-229 / I-283 / I-233 | Tick checklist; private-read v2; poller error_description | L9 read on 29 Sep 19:00Z; close I-233 in one line at R8 | `IDEAS.md` l.135, l.527, l.243 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/14/{ideas,facts,watch}.json`)

1. [now] **Launch the ladder watcher** at 03:30-03:45Z (hard 04:10Z). It must run detached with a restart loop via `experiments/lb_poll/run_ladder_watch.sh`, with `--s0 experiments/e10_watch/20260927T0147Z.txt --hard-cap 2026-09-27T11:30Z`. Within 5 minutes, check that `watch.log` shows the S0 line (rank 242, count 40), `calls.jsonl` has one line, and there is no Traceback. Without it, every 0.954 reads N4 and the A-only extension is dropped. Sources: `report.json` R14-A1; `FACTS.md` F-RUN-27; `WATCHLIST.md` W134.
2. [now] **Log the R14-A2 PRE-SCORE NOTES in CONTEXT, then commit (as the user, no trailer) and PUSH** before the first poll.log header with a ladder ref COMPLETE (hard 04:25Z). Content: S0, literal readings (1)-(6), V* tie order a > d > b > e, fm45 POS reading, SELECTED after 06:45Z, and never opening state.json. The same commit carries `round14/REPORT.md` (R14-A0), `round14/` and the 0147Z snapshot. It also replaces the stale S0 at `CONTEXT.md` l.2679. Sources: `report.json` R14-A0, R14-A2; `WATCHLIST.md` W143, W144.
3. [now] **Round 15 would break the 04:10-06:45Z quiet window.** Line l.37 of the round prompt tells the browser agent to run `tools/e10_snapshot.py` first and fall back to the CLI. FOCUS_NOTE (l.35) reaches only the plancheck agent. Fix l.37, or run round 15 without the browser scan or after 06:45Z. Sources: `experiments/workflows/biohub-research-round.js` l.35-38; `WATCHLIST.md` W150, I136.
4. [today] **Watcher liveness checks at ~04:20, 05:20 and 06:30Z** (file-only). No owner and no timer exist for them. Sources: `report.json` R14-A5; `WATCHLIST.md` W145.
5. [today] **D1 (~04:45-05:40Z): apply READ SHEET v1 mechanically.** Log the D1 line with `date -u`. Close I-312 with the R13-A6 wording. Add a RESULTS.md row and the probe.json score for each probe as it scores. D2 comes after probe 42. A-only miss by UNPROVEN L_hi is a miss by rule; do not reopen it (PC14-05 was rejected). Sources: `report.json` R14-A3; `DECISIONS.md` §2h l.698; `WATCHLIST.md` W141, W126.
6. [today] **07:30Z push (65b1b746): send ONE RU variant (P-A/P-B/P-C) matching the D1 row, with the two corrected brief lines** (the insertion hedge is in-sample, and the FT evidence is 0/4, not 0/5). The push carries: E10 v2 (lapses 12:00Z), Q1-Q3 (a yes is needed by ~09:00Z), the R8 cap, and any re-tick line. Read SELECTED then. Log the ROUND 14 RECORD (R14-A6) before the push. Sources: `report.json` R14-A4, R14-A6; `FACTS.md` C-105, C-107; `WATCHLIST.md` W136, W146.
7. [today] **exp70g still has no NEVER_SUBMIT.md**; add it with the next commit. `LESSONS_draft.md` l.7 still states '~29%' as a fact (fix by 12:00Z). Sources: `experiments/exp70g_k2_cap6/`; `WATCHLIST.md` W142, W98.
8. [before-finals] **Any ladder pair is only a recommendation until the user re-ticks by 29 Sep 20:00.** Re-tick once after D2 (~08:30Z), and a second time only if a combo becomes V*. Push the HINDSIGHT GUARD (I-336) before 29 Sep 23:00Z. The W57 family is still overdue (the CONTEXT l.22 error; the out_valid, efpost and 33.1% records). Sources: `report.json` R14-A3, R14-A8; `DECISIONS.md` §2 [c14]; `WATCHLIST.md` W57.
9. [info] **Two status corrections.** I-063 (DaughterNet v2) moves refuted -> deferred, because the gap is at noise level. I-106 moves refuted -> open-untested; it was never run. Also, all six timers are session-only, and the MEMORY index line seen by subagents is stale (read the 22:46 RESUME POINT and later entries). Sources: `research/wf_ideas_v4/round14/scan_recheck.json` R14-RC-A/B; `FACTS.md` C-110, C-75.

**RESOLVED since curation 13:**
- Watcher code written, tested and pushed (f24ff72, 01:54:14Z).
- Curation 13 and round 13 files committed (f2f843e).
- Pre-score registration pushed before any ladder score (3d48d35).
- Timers 65b1b746 and 2e87e414 set, with the quiet-window deferral (5e57346).

## HOW TO USE

- "Score of probe N, what changed?" -> `DECISIONS.md` §1, `experiments/RESULTS.md`, `experiments/lb_poll/poll.log` (39+), `experiments/<exp>/probe.json`.
- "Rung displays 0.954 or 0.955, what are the finals?" -> READ SHEET v1 (`report.json` R14-A3; `DECISIONS.md` §2h l.698), `DECISIONS.md` §2 l.400, `CONTEXT.md` l.2502-2529 and l.2664-2710.
- "Is the watcher alive? Who passed us?" -> `experiments/lb_poll/ladder_watch/watch.log` and `calls.jsonl` (never open state.json); `WATCHLIST.md` W145.
- "Can exp72 be submitted or become a final?" -> `CONTEXT.md` l.2722-2746, `IDEAS.md` I-119/I-330/I-106.
- "What if a public successor appears?" -> `DECISIONS.md` §2f, `CONTEXT.md` l.2138-2147, l.2257-2317, l.2550-2569; `IDEAS.md` I-286.
- "Which rule decides this?" -> `DECISIONS.md` §3; `FACTS.md` §5 and CONTRADICTIONS; `CONTEXT.md` l.1576-1736.
- "Was idea X tried?" -> search for its mechanism in `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md`. "What is next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~02:25Z 27 Sep, read the tail of `CONTEXT.md` §14 (above `## 9.`), `poll.log`, `ladder_watch/`, and the newest `research/wf_ideas_v4/round*/`.
