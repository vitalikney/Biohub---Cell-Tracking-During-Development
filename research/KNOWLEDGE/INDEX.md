# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 5: state as of 2026-09-26 ~04:05 UTC, git HEAD f05389e (pushed 01:20:05Z) plus the untracked `research/wf_ideas_v4/round5/`. Previous: curation 4 (~01:20 UTC, b2cb928). All times UTC; every line cites its source.
Deadline 29 Sep 23:59; the user ticks finals MANUALLY by 29 Sep 20:00. Sources: `CONTEXT.md` §1; PRE-REG v3 §f l.1707-1736; AMENDMENT f2 l.1887-1895; RESUME POINT l.2006-2025; 01:20 entries l.2026-2038.

## STATE IN 10 LINES

1. **Best public 0.954** (P35 exp57b, R5 UNPROVEN; P36 exp57, diagnostic): neither is a final. **Rank #160 of 3,922 at 03:16Z**, 36 ranks above the silver line. Sources: `experiments/lb_poll/ledger.md` (03:53:35Z); `FACTS.md` F-LB-02/03, F-LB-09; `research/wf_ideas_v4/round5/report.json` new_facts.
2. **Base x138** (P34 exp56 = 0.953, ADMIT, L <= 6.46 h). Sources: `experiments/lb_poll/ledger.md`; `DECISIONS.md` §1.
3. **Running:** #37 K2 exp58 (ref 56563521, 00:02:12Z) and #38 twin exp58n (56563534, 00:02:18Z), both **PENDING at 03:53:33Z** (L > 3.85 h). ETA: twin ~06:15-07:40Z, K2 ~07:50-09:30Z. Poller PID 20052 must stay up. Sources: `experiments/lb_poll/poll.log` l.2397-2402; `FACTS.md` C-35, F-RUN-16.
4. **Default finals:** the pair {#37, #38}, read by the READ TABLE (`CONTEXT.md` l.1978-2005) + CLARIFICATION v2 C1-C6 (l.2026-2032, **now in CONTEXT**, f05389e, pushed before any score). Sources: `DECISIONS.md` §2, §2b, §2c.
5. **CLARIFICATION v3 (V1-V7) is NOT in CONTEXT.** It fixes #34 in C3/row 4 (pairs, not labels -> {twin, exp52}), replaces row 5's queue reading with bound B, and makes K2'' = exp58d the only runtime-trigger offer. It must be pushed before the first #37/#38 result. Sources: `DECISIONS.md` §2d; `FACTS.md` C-37..C-39; round5 `report.json` R5-A2.
6. **Finals ticked: 0 of 2** (auto-select would pick P36 + #35). The provisional tick rule and the 29 Sep checklist are in CONTEXT l.2034-2038; the ticks and durable reminders do not exist yet. Sources: `FACTS.md` F-RUL-12; `WATCHLIST.md` W54, W50.
7. **All riders are closed**, and round 5 closed more: fork-removal 0 for 5 (already-divided -0.00068 on x138), D4 and N1 dropped, AdaBN blocked. The largest known remaining defect (post-freeze transitions, lab ceiling +0.0063) is post-deadline only. Sources: `CONTEXT.md` l.2021-2022, l.2033; `FACTS.md` F-TRN-21..23; `DECISIONS.md` G16-G19.
8. **Next decision points (26 Sep):** v3 push + OK request before ~06:00; background clean-proof polls 07:57:30/08:00:45/08:01:45Z (8.0 h mark 08:02:12Z); score read with bound B once both are terminal; provisional tick ~09:30-10:00; round-5 records into CONTEXT by 12:00; M6 lapses 18:00. Sources: `WATCHLIST.md` W56, W45, W55, W47, W54, W57, T12-T16.
9. **Cutoffs:** R8 (no new mechanisms) 27 Sep 12:00; admission table 28 Sep 22:00; reminders by 28 Sep evening; finals tick 29 Sep 20:00 (reminders 12:00 + 18:00). Sources: `CONTEXT.md` l.1614-1615, l.2034-2038; `WATCHLIST.md` T17-T20.
10. **Ideas ledger:** 243 ideas: lb-tested 38, lab-tested 20, refuted 139, deferred 20, in-plan 25, open-untested 1. Strict orphan I-233; at risk I-226, I-228, I-232, I-235, I-236, I-243. Source: `IDEAS.md` l.9, l.11, ORPHANS l.374.

## WHERE THINGS ARE

Knowledge base (`research/KNOWLEDGE/`, written only by the curator workflow `experiments/workflows/biohub-curator.js`):
- `research/KNOWLEDGE/INDEX.md`: this page.
- `research/KNOWLEDGE/IDEAS.md` + `research/KNOWLEDGE/ideas.json`: I-001..I-243 in 12 clusters with status and sources. Delta at l.11, ORPHANS at l.374, per-ID change log in `ideas.json` meta.curations.
- `research/KNOWLEDGE/FACTS.md`: verified facts §1 metric .. §7 lab-to-LB transfer; CONTRADICTIONS at l.159 (open: C-33, C-35..C-42).
- `research/KNOWLEDGE/DECISIONS.md`: probes P01..P38 (§1), lab gates G01-G19 (§1b), finals (§2), READ TABLE (§2b), CLARIFICATION v2 (§2c, in CONTEXT), proposed v3 (§2d l.214), R1-R10 (§3 l.236).
- `research/KNOWLEDGE/WATCHLIST.md`: OVERDUE l.34, NEXT 24 H l.48, LATER l.76, INSIGHTS AT RISK l.102 (W, T, I IDs).
- `research/KNOWLEDGE/CHANGES.md`: delta per curation. Curator logs: `research/KNOWLEDGE/_curation/{v4,2,3,4,5}/`.

Key sources (repo root):
- `CONTEXT.md`: single source of truth; newest entries end at l.2038, just above "## 9. Literature" (l.2039). PRE-REG v3 l.1576-1736; AMENDMENT f2 l.1887-1895; READ TABLE l.1978-2005; RESUME POINT 00:02 l.2006-2025; CLARIFICATION v2 l.2026-2032; round-4 records l.2033; tick rule + checklist l.2034-2038.
- `experiments/RESULTS.md` (every LB probe; P37/P38 at l.70-71). `experiments/lb_poll/poll.log` (10-min poll). `experiments/lb_poll/ledger.md` (latency bounds, R5, A5 watch; some texts stale, C-40).
- Kernels: `experiments/exp58_x138_safe_lowref/` (K2), `experiments/exp58n_x138_safe_lowref/` (twin), `experiments/exp58t_x138_safe/` (K1); `experiments/*/probe.json` says what each changed.
- `experiments/exp60_trainlab/results.md` (x138 lab verdicts); `experiments/runtime_step0/` (hidden-N bound, F(K2) = 7.87 h).
- `tools/runtime_ledger.py` (`--print`), `tools/build_probe_kernel.py` (l.2016-2029 refuse deadline moves, F-MOD-18), `tools/dummy_gates.py`, `tools/trainlab.py`.
- `research/wf_ideas_v4/round5/report.json` (untracked): R5-A1..A8 in `actionable`, verbatim v3 block in `plan_issues`, `ok_message_ru`, `report_md_ru` (no REPORT.md yet). Rounds 3-4 have REPORT.md; round 2 does not.
- `research/wf_ideas_v3/FINAL_REPORT.md` (pre-reg source); `PROMPT_FRIEND_A.md` (stale), `PROMPT_FRIEND_C.md`, `TEAM.md`; intel in `research/browser_research_2026-09-24*.md`, `research/discussions_summary.md`, `research/survey_*.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-001 / I-090 | K2 exp58 (#37) / no-insertion twin exp58n (#38) | in-plan: SUBMITTED, PENDING; read as a pair by the table | `IDEAS.md` l.42, l.79 |
| I-236 | READ TABLE CLARIFICATION v3 (V1-V7) | at risk: not in CONTEXT; commit + push before any result | `IDEAS.md` l.93; `DECISIONS.md` §2d |
| I-228 | Consolidated pre-score OK request, now 7 items | at risk: unposted; post `ok_message_ru` now | `IDEAS.md` l.90; round5 R5-A3 |
| I-226 | Background clean-proof polls 07:57:30/08:00:45/08:01:45Z | at risk: job not started; start before 07:45Z | `IDEAS.md` l.59; round5 R5-A1 |
| I-235 / I-237 | K2'' = exp58d (37800/32400) as the only trigger offer; runtime bound B | in-plan; builder change not prepared; build only on trigger + OK | `IDEAS.md` l.61-62; round5 R5-A4 |
| I-227 / I-229 | Provisional tick (exactly 2, by ref); 29 Sep checklist | in CONTEXT; tick after the read, reminders by 28 Sep | `IDEAS.md` l.89, l.91 |
| I-011 / I-219 / I-225 | K1 contingency; twin floor 0.952; K2 resubmit on "Kaggle Error" | in-plan; each needs the OK (part of I-228) | `IDEAS.md` l.52, l.87, l.58 |
| I-243 / I-232 / I-233 | ledger text fix; round REPORT.md files; poller error_description | after ~09:40Z / quiet window / close or implement | `IDEAS.md` l.66, l.359, l.60 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/5/{ideas,facts,watch}.json`)

1. [now] **CLARIFICATION v3 not in CONTEXT.** Append the verbatim block from round5 `report.json` plan_issues, point l.2023 at the OK REQUEST, commit as the user and push before the first #37/#38 result (hard limit ~06:00Z). It also resolves the #34 contradiction (C3/row 4 vs the Never line). Sources: `WATCHLIST.md` W56; `FACTS.md` C-37; `DECISIONS.md` §2d.
2. [now] **OK request unposted.** Post the 7-item Russian text (R5-A3) in chat + PushNotification; log "OK REQUEST posted <UTC>" and the answer time against the first result times (OKs after a visible score are post-hoc). Sources: `WATCHLIST.md` W45; `FACTS.md` C-33.
3. [now] **Clean-proof job not running.** Poller polls ~07:54Z and ~08:04Z straddle 08:02:12Z. Start the R5-A1 background script (stamps after the call) well before 07:45Z; never import `lb_poll.py`, never restart PID 20052. Sources: `WATCHLIST.md` W55; `FACTS.md` F-RUN-16/17.
4. [today] **Runtime trigger cannot be built as written** (builder refuses deadline moves; D4 has no code; DIVINS alone is harmful). Prepare K2'' tests outside 07:45-08:35Z, keep K2 sha unchanged. Sources: `FACTS.md` F-MOD-18, C-39; `WATCHLIST.md` W58.
5. [today] **Poller stop rule:** keep PID 20052 until both refs are terminal and at least to the first poll after 09:32:18Z (not ~09:30Z). No builds, pushes or submits inside 07:45-08:35Z. Sources: `WATCHLIST.md` T16; round5 R5-A5.
6. [today] **Score read + provisional tick:** mechanical read with bound B (C-38), then recommend the tick as a pair with refs (default 56563521 + 56563534); verify 2/2. Sources: `WATCHLIST.md` W47, W54; `FACTS.md` F-RUL-12.
7. [today] **Stale ledger texts** (A6 K3 rebase, D4 ask, "Forecast F not supplied"): neutralise via v3 V6 now; code fix only after ~09:40Z. Sources: `FACTS.md` C-40; `WATCHLIST.md` W59.
8. [today] **Round-5 folder untracked, no round5/round2 REPORT.md**; `experiments/ext_*` uncommitted; friend A card stale. Save `report_md_ru` with the v3 commit. Sources: `WATCHLIST.md` W60, W05, W02-W03.
9. [before-finals] **Round-5 records into CONTEXT by 12:00:** #160 intel, R5H facts, post-freeze defect (+ fix CONTEXT l.22, C-36), fork-removal 0 for 5, AdaBN blocker, W44 done; plus curation-3 closures (W31). Sources: `WATCHLIST.md` W57; `FACTS.md` C-36, C-41.
10. [before-finals] **Durable 29 Sep reminders** (12:00, 18:00) and the admission table do not exist yet. Sources: `WATCHLIST.md` W50, W04, T19.
11. [info] I-233 is the only strict orphan; LB "Entries" is one short of our 39 (C-42); memory residue lists closed riders. Sources: `IDEAS.md` ORPHANS; `FACTS.md` C-42; `WATCHLIST.md` W34.

## HOW TO USE

- "Score of probe N, what it changed, why dropped?" -> `DECISIONS.md` §1, then `experiments/RESULTS.md` and `experiments/<exp>/probe.json`.
- "How do we read K2/twin and pick the pair?" -> `DECISIONS.md` §2b + §2c + §2d, then `CONTEXT.md` l.1978-2038 and round5 `report.json` plan_issues.
- "Which lab gate closed a rider?" -> `DECISIONS.md` §1b, then `experiments/exp60_trainlab/results.md`.
- "Which rule decides this?" -> `DECISIONS.md` §3; rule text `CONTEXT.md` l.1576-1736; latency bounds `experiments/lb_poll/ledger.md`.
- "Was idea X tried?" -> search the alias in `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md` and its CONTRADICTIONS.
- "What is next / overdue / at risk?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`. Anything newer than 04:05Z 26 Sep -> tail of `CONTEXT.md` §14 and `experiments/lb_poll/poll.log`.
