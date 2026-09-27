# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 16: state as of 2026-09-27 ~09:15 UTC. Git HEAD 0bd1408 (= origin/main; ladder D2) plus the untracked `research/wf_ideas_v4/round16/`, `experiments/e10_watch/20260927T0831Z.txt` and `experiments/ext_optimized-biohub-max-score/v6_2026-09-27/`. Previous curation: 15 (~06:15 UTC, da9766e). Hashes older than 26 Sep 10:15 are pre-rewrite (`experiments/git_rewrite_map_2026-09-26.txt`). All times are UTC, and every line cites its source.
Deadline 29 Sep 23:59; the user ticks finals MANUALLY by 29 Sep 20:00. `CONTEXT.md` gained two entries since curation 15: PROBES 43/44 PRE-SCORE ENTRY (06:19) at l.2814-2871 and LADDER READ D2 (07:41) at l.2872-2879, just above `## 9. Literature` at l.2880. Anchors:
- Rules: PRE-REG v3 l.1576-1736 (R7-R9 at l.1665-1673); E10 PORT RULE l.2138-2147; E10 v2 PROPOSED l.2352-2361; LADDER + L9 l.2407-2424; RULE RECONCILIATION l.2502-2529; E10 HARDENING l.2550-2569.
- 27 Sep: ROUND 13 RECORD l.2626-2663; LADDER PRE-SCORE REGISTRATION (R13-A1) l.2664-2721; EXP71/72 GOVERNANCE l.2722-2746; READ SHEET v1 l.2776-2785; LADDER READ D1 l.2789-2799; SUBMIT 43/44 l.2809-2813; 43/44 PRE-SCORE ENTRY (deviation record, FREEZE, class-C table) l.2814-2871; D2 l.2872-2879. Not yet logged: ROUND 14/15/16 RECORDs, R16-A1..A6 (`research/wf_ideas_v4/round16/report.json`). Newest RESUME POINT l.2599 (26 Sep 22:46) is stale.

## STATE IN 10 LINES

1. **Finals TICKED 2/2:** #37 K2 exp58 (56563521) = **0.954** and #38 twin exp58n (56563534) = **0.953**. D1 and D2 left the pair unchanged; API SELECTED 2/2 [56563534, 56563521] read at 07:41:28Z. Sources: `CONTEXT.md` l.2872-2879; `DECISIONS.md` §2 [c16] l.435, snapshot l.445.
2. **LB #255 of 3,943** at 0.954 (08:31Z; was #256), 8th of 113 in the 0.954 block (ranks 248-360). Info only; private (~71%) decides. Sources: `experiments/e10_watch/20260927T0831Z.txt` l.911; `FACTS.md` F-LB-01 [c16].
3. **Base** = x138 + safetail + lowrefine + gated DaughterNet insertion (K2). Insertion '+0.006' is in-sample; honest OOF +0.0019. Sources: `CONTEXT.md` l.2407-2409; `FACTS.md` F-TRN-44.
4. **Ladder 39-42 done:** P39 exp70e 0.949, P40 exp70a 0.954 (no UP; its NEU was structural, C-125), P41 exp70d 0.949, **P42 exp70b (K2 + forkmid 4.5) 0.954 with an attributable UP** (U4, fm45 POS; L (7.41, 7.58] h, insertion gate did not fire). Not V* (< 0.955), BASE none -> no combo, no re-tick. Sources: `CONTEXT.md` l.2789-2799, l.2872-2879; `FACTS.md` F-TRN-46, F-TRN-47.
5. **Running now:** P43 exp70j DC 0.20 (56598763) and P44 exp70k DC 0.225 (56598765) PENDING at the 09:10:50Z header; expected ~12:10-13:10Z; 9.0 h clocks 14:28:13Z / 14:28:22Z. The watcher stopped at 07:37Z, so the poller is the only record. Sources: `experiments/lb_poll/poll.log` l.13013; `FACTS.md` F-RUN-29; `DECISIONS.md` §1 l.153-154.
6. **43/44 are class C:** the deviation record, FREEZE (no further DC rung/combo/ladder submit; never resubmit a class-C file), descriptive read and class-C finals table (default (a) no change) are logged before any score (4161226). Priors P(>= 0.955) ~0.08-0.20 per rung. Sources: `CONTEXT.md` l.2814-2871; `IDEAS.md` I-344, I-345.
7. **Open decision:** exp70b is now our best public file (unrounded) but fails our own 0.955 bar; only a user letter can make {exp70b, #38} the pair (I-354). No user answer has been logged since the ~07:45Z brief. Sources: `CONTEXT.md` l.2877-2879; `IDEAS.md` I-354; `research/wf_ideas_v4/round16/report.json` R16-A8 (i).
8. **E10:** v1 (>= 0.956) is in force; P1 at 08:31Z was NOT met. v2 (>= 0.954) lapses at 12:00:00Z together with the R8 new-mechanism cutoff, and nothing reaches R8. Sources: `DECISIONS.md` §2f l.695; `research/wf_ideas_v4/round16/report.json` R16-A3.
9. **Next decision points:** now (practical edge 11:45Z) log and push R16-A1 + R16-A0; send R16-A2 once by 11:00Z; 12:00Z R16-A3 lapse line; 43/44 read ~12:10-14:40Z (R16-A4); RESUME POINT ~15:00Z; 28 Sep ~08:00Z / ~18:30Z last exp72 yes; 29 Sep 02:00 last port submit; ~18:00 exp70b letter; ~19:00 L9 read; 20:00 ticks final. Sources: `WATCHLIST.md` NEXT 24 H l.48, LATER l.84.
10. **Ideas ledger:** 359 ideas (lb-tested 48, lab-tested 21, refuted 184, deferred 42, in-plan 62, open 2). Strict orphan: I-233. Sources: `IDEAS.md` l.69, CHANGES (16) l.71, ORPHANS l.566.

## WHERE THINGS ARE

Knowledge base `research/KNOWLEDGE/` (written only by `experiments/workflows/biohub-curator.js`):
- `INDEX.md` this page; `CHANGES.md` per-curation deltas (v4, 2-16).
- `IDEAS.md` + `ideas.json`: I-001..I-359 in 13 clusters: FINALS l.104, LADDER l.157, BASE l.187, RUN l.223, LOC l.262, DIV l.293, MODEL l.355, NODES l.399, INFER l.433, EF l.455, LINK l.475, VALID l.506, TESTSET l.548, ORPHANS l.566. Per-ID log: `ideas.json` meta.curations[n=16].
- `FACTS.md`: §1 metric l.137, §3 LB l.175, §4 runtime l.195, §5 rules l.229, §6 models l.252, §7 lab-to-LB l.288, CONTRADICTIONS l.340 (C-121..C-131 at l.464-474).
- `DECISIONS.md`: probes §1 l.103 (P42-P44 l.152-154); gates §1b l.273; finals §2 l.338 (c16 snapshot l.445); E10 §2f l.590; OC §2g l.701; ladder/L9 §2h l.732 (round-16 rows l.761-763); R1-R10 §3 l.765.
- `WATCHLIST.md`: OVERDUE l.35, NEXT 24 H l.48, LATER l.84, INSIGHTS l.121 (I161-I171). Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,16}/`.

Key sources (repo root): `CONTEXT.md` (source of truth, anchors above). LB: `experiments/RESULTS.md` (rows to P38 only), `experiments/lb_poll/poll.log` + `ledger.md` (39+), `experiments/lb_poll/ladder_watch/` (stopped 07:37Z; never open `state.json`), `experiments/e10_watch/20260927T0831Z.txt` (newest E10/LB snapshot). Kernels: finals `experiments/exp58_x138_safe_lowref/` (#37), `experiments/exp58n_x138_safe_lowref/` (#38); ladder `experiments/exp70{a_k2_lp30,d_k2_dc030,e_k2_lp30_dc030,b_k2_fm45,g_k2_cap6,j_k2_dc020,k_k2_dc0225}/probe.json`; retrain `experiments/exp71_secft_all/` (NEVER_SUBMIT.md). Tools: `tools/build_probe_kernel.py`, `tools/runtime_ledger.py`, `tools/e10_port_gate.py`, `tools/e10_snapshot.py`. Rounds: `research/wf_ideas_v4/round16/` (UNTRACKED; `report.json` R16-A0..A9, `scan_*.json`, `v_*.json`, no REPORT.md yet), `round15/`..`round8/`, `reach0955/`; round prompt `experiments/workflows/biohub-research-round.js` (l.35-38 unfixed). Background: `research/wf_ideas_v3/FINAL_REPORT.md`, `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v4/round9/LESSONS_draft.md`, `PROMPT_FRIEND_C.md`, `TEAM.md`, `research/discussions_summary.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-355 / I-344 / I-299 | R16-A1 read addendum: INS = #37 unless the letter names exp70b; (b) = {V*_C, #37}; insertion-family E10 port never paired mechanically; answer parsing | In-plan, NOT in CONTEXT; log + push while both 43/44 refs are PENDING (practical 11:45Z) | `IDEAS.md` l.152, l.148, l.144 |
| I-354 | exp70b as the public-aimed final ({exp70b, #38}) | User letter only; neutral facts in R16-A2 point 1; practical expiry 29 Sep ~18:00Z | `IDEAS.md` l.151 |
| I-341 / I-342 / I-345 | Read exp70j / exp70k; FREEZE | Mechanical read at the first both-terminal header or at/after 14:28:22Z (14:40Z fallback); no new submit whatever they show | `IDEAS.md` l.180-181, l.183 |
| I-286 | E10 v2 (>= 0.954 trigger) | Unanswered; lapses 12:00:00Z; a later yes is a forward-only override | `IDEAS.md` l.212 |
| I-119 / I-330 | exp71 -> exp72 FT secondary; G2 veto | Only a named Q1 + Q2 yes; would override the user's refusal (7); last yes 28 Sep ~08:00Z (with ERROR room) / ~18:30Z | `IDEAS.md` l.383, l.396 |
| I-229 / I-283 | Tick checklist; private-read v2 + L6/L7 + DC-DOSE | L9 read 29 Sep ~19:00Z; L6/L7 logged at `CONTEXT.md` l.2863-2868 | `IDEAS.md` l.126, l.536 |
| I-336 / I-252 | HINDSIGHT GUARD; LESSONS edits | Guard pushed before 29 Sep 23:00Z (grep 0 in CONTEXT); R16-A9 text fixes by 30 Sep | `IDEAS.md` l.542, l.531 |
| I-359 / I-233 | Removal-gate study on the shipped stack; poller error_description | Post-deadline (fb_ins35.py only in a session scratchpad); close I-233 with one CONTEXT line | `IDEAS.md` l.545, l.247 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/16/{ideas,facts,watch}.json`)

1. [now] **Log R16-A1 in CONTEXT** (date -u, quoting a poll.log header with 56598763 and 56598765 both PENDING): composition, re-tick order, read timeout (14:28:22Z, fallback 14:40Z), letter window, answer parsing. Save `round16/REPORT.md` from `report_md_ru` (R16-A0). Commit as the user (no trailer), push, and log the hash. An ERROR can close the window at any time; practical edge 11:45Z. Sources: `research/wf_ideas_v4/round16/report.json` R16-A0, R16-A1; `WATCHLIST.md` W158, W159; `FACTS.md` C-121..C-123.
2. [now] **Send R16-A2 once, by 11:00Z** (chat + push <= 180 chars): defaults, neutral exp70b facts (the user's own 'best public' wording points at exp70b; the 0.955 bar was ours), class-C window, E10 v2, Q1-Q3; note that exp71 would override refusal (7). Log any letter verbatim with date -u and the header; parse under R16-A1 (5); a blanket yes never authorises the exp71 push. Sources: `report.json` R16-A2, R16-A8; `WATCHLIST.md` W154, W160, I163/I164; `IDEAS.md` I-355.
3. [today] **12:00:00Z R16-A3 line** 'R8 CUTOFF PASSED; E10 v2 LAPSED' (or the user's answer verbatim); fix the `research/wf_ideas_v4/round9/LESSONS_draft.md` l.7 caveat (W98). Sources: `report.json` R16-A3; `DECISIONS.md` §3; `WATCHLIST.md` W161.
4. [today] **Read 43/44 mechanically** (R16-A4): displays, ledger L + insertion-gate text, V*_C, letter timing, resulting pair; one CONTEXT line + one user line; re-tick text only under an existing letter. FREEZE holds. Sources: `CONTEXT.md` l.2821-2853; `report.json` R16-A4; `WATCHLIST.md` W156.
5. [today] **Records:** RESUME POINT l.2599 is stale and MEMORY.md points to it (R16-A6 by ~15:00Z, then repoint); ROUND 14/15/16 RECORDs missing; RESULTS.md has no rows for P39-P42 (0.949 / 0.954 / 0.949 / 0.954); exp70g/j/k lack NEVER_SUBMIT.md; v6 NOTES item 4 gives the wrong R8 reason; the brief's push status is not logged; round16/, v6 and the 0831Z snapshot are untracked. Do it as one R16-A5 commit. Sources: `report.json` R16-A5, R16-A6; `FACTS.md` C-26, C-114, C-118; `WATCHLIST.md` W126, W142, W146/W155/W162, W163.
6. [before-finals] **exp70b-as-final** (I-354) is the one live finals question that no rule decides. Present neutral facts only; round 16 rejected 'weakly dominates, recommend yes' (P(delta < 0) 0.08-0.15). On a yes: untick 56563521, tick 56592350, keep 56563534, re-read SELECTED. Sources: `IDEAS.md` I-354; `FACTS.md` F-TRN-47, C-129; `report.json` R16-A8 (i).
7. [before-finals] **Push the HINDSIGHT GUARD** (I-336) before 29 Sep 23:00Z. Copy `fb_ins35.py` into `experiments/exp60_trainlab/` or log that the forkblob +0.00019 is unreproducible. Timers are session-only (recreate 2e87e414, 012fa6dd, 328f7392, 18ff4796, bb224de9 on restart). Sources: `IDEAS.md` I-336, I-073, I-359; `report.json` R16-A9 (b); `WATCHLIST.md` T67.
8. [info] **Corrected readings, do not reuse:** exp70a's NEU does not show that lp30 is neutral (C-125); public block ranks were used for the x138 copy's private rank, so the #38 hedge premise is weaker (C-124, C-127; I161); the '09:00Z exp72 edge' was manufactured (C-128). The round prompt l.35-38 is still unfixed (W150). Sources: `FACTS.md` CONTRADICTIONS l.464-474; `WATCHLIST.md` I161, W150.

**RESOLVED since curation 15:** R15-A1 pre-score entry logged and pushed at 06:19Z before any 43/44 score (4161226, with `round15/REPORT.md`); D2 read applied mechanically (0bd1408); API SELECTED read 07:41:28Z; brief sent in chat ~07:45Z; watcher stopped 07:37Z (64 calls, 0 x 429); E10 P1 08:31Z checked (not met); the 09:00Z exp71 edge is moot (`CONTEXT.md` l.2814-2879; `WATCHLIST.md` 'Done, superseded or moot').

## HOW TO USE

- "Score of probe N, what changed?" -> `DECISIONS.md` §1, `experiments/RESULTS.md` (to P38), `experiments/lb_poll/poll.log` / `ledger.md` (39+), `experiments/<exp>/probe.json`.
- "Probe 43/44 scored, what are the finals?" -> `CONTEXT.md` l.2814-2871 ((3) read, (4) class-C table), R16-A1 in `research/wf_ideas_v4/round16/report.json` (until logged), `DECISIONS.md` §2 l.445, L9 `CONTEXT.md` l.2407-2424.
- "Did the user answer? Does a letter count?" -> tail of `CONTEXT.md` §14; `experiments/lb_poll/poll.log` headers; `IDEAS.md` I-355; `WATCHLIST.md` W154.
- "Can exp72 be submitted?" -> `CONTEXT.md` l.2722-2746; `IDEAS.md` I-119/I-330. "Public successor appeared?" -> `DECISIONS.md` §2f, `CONTEXT.md` l.2138-2147, l.2550-2569; `IDEAS.md` I-286; newest `experiments/e10_watch/` snapshot.
- "Which rule decides this?" -> `DECISIONS.md` §3; `FACTS.md` §5 and CONTRADICTIONS; `CONTEXT.md` l.1576-1736, l.2664-2721, l.2814-2871.
- "Was idea X tried?" -> search its mechanism in `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md`. "What is next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~09:15Z 27 Sep: tail of `CONTEXT.md` §14 (above `## 9.`), `poll.log`, newest `research/wf_ideas_v4/round*/`.
