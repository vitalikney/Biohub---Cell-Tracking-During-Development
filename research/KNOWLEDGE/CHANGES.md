# CHANGES - delta per curation (newest section at the end)

Each curation appends one dated section. IDs (I-, F-, C-, P, W, T, I) are stable across curations; see `research/KNOWLEDGE/INDEX.md`.

## v4 - 2026-09-25 ~18:30 UTC (first curation; baseline, git HEAD 14c339e)

Previous curation: none. `research/KNOWLEDGE/` did not exist before commit 5ea53f9, so everything below is NEW (baseline),
not a delta. Inputs: `CONTEXT.md` up to the 18:20 UTC entries, `experiments/RESULTS.md`, `experiments/lb_poll/poll.log`
(last poll 18:28:59Z), `research/wf_ideas_v2/`, `research/wf_ideas_v3/`, `research/wf_ideas_v4/FINAL_REPORT_v4.md`
(no `research/wf_ideas_v4/round*/` yet). Curator logs: `research/KNOWLEDGE/_curation/v4/`.

Files created:
- `research/KNOWLEDGE/IDEAS.md` + `ideas.json`: 211 ideas I-001..I-211 in 12 clusters (RUN, BASE, LOC, DIV, FINALS, MODEL,
  NODES, INFER, EF, LINK, VALID, TESTSET). Status: refuted 111, lb-tested 37, in-plan 21, deferred-after-deadline 19,
  lab-tested 18, open-untested 5 - `research/KNOWLEDGE/_curation/v4/ideas.json`.
- `research/KNOWLEDGE/FACTS.md`: 7 fact tables + contradictions C-01..C-18 - `research/KNOWLEDGE/_curation/v4/facts.json`.
- `research/KNOWLEDGE/DECISIONS.md`: probes P01..P36, finals table, R1-R10 status - same source.
- `research/KNOWLEDGE/WATCHLIST.md`: W01-W29, T01-T11, I01-I14 - `research/KNOWLEDGE/_curation/v4/watch.json`.
- `research/KNOWLEDGE/INDEX.md`, `research/KNOWLEDGE/CHANGES.md` (this file).

State recorded at baseline (for the next delta):
- Best public 0.954 (P35 exp57b), base x138 (P34 = 0.953), branch A; R1, R2, R5, R6 applied; R3, R4 pending - `DECISIONS.md` §1, §3.
- P36 (exp57 v1) PENDING; K2 = exp58 scheduled 00:01 26 Sep; exp58n twin built, not submitted - `DECISIONS.md` §1 footer, §2.
- F1 candidate K2; F2 = exp52 until AMENDMENT f2 is OK'd - `DECISIONS.md` §2; `CONTEXT.md` l.1887-1895.
- Orphans: strict I-072, I-081, I-204, I-205, I-207; at-risk I-035, I-158 - `IDEAS.md` ORPHANS.

Alerts opened (13 after dedup; full list in `INDEX.md` TOP ALERTS):
- now: ADDENDUM L code missing in `tools/trainlab.py` (W01); P36 L35 reading undecidable (I10); K2 00:01 submit + poller (W16, W19);
  forkblob patch not built (W11).
- today: morning OK package (W21); twin/K3 dummy-gate code (W12, W13); admission table (W04); untracked ext folders (W05);
  friend A card stale (W02, W03); tempfuse build-or-drop (I-158).
- before-finals: R7 vs exp52 DIVINS_DUMP=1 (C-16); K3b one-blob share (I01); close orphans; manual finals, never exp56 (T10).
- info: stale `experiments/RESULTS.md` l.58 (P25 = 0.946, C-17), `CONTEXT.md` §4 weighting (C-01), §11a noise floor (C-06),
  quota "unverified" (W06), `TEAM.md` 0.97 target (C-04).

Alerts resolved: none (first curation).

## 2 - 2026-09-25 ~20:55 UTC (curation 2; git HEAD da154cb + untracked `research/wf_ideas_v4/round2/`)

Previous curation: v4 (~18:30 UTC, 14c339e). New inputs: `CONTEXT.md` l.1896-1937 (entries 18:40-20:35), commits 9545e91..da154cb,
`experiments/exp60_trainlab/results.md` + `results_forkblob.md`, `experiments/lb_poll/ledger.md` (20:42:42Z),
`research/wf_ideas_v4/round2/report.json` + scan/v_*.json (finished 20:42). Curator logs: `research/KNOWLEDGE/_curation/2/`.

State change in one line: the exp60 T9 lab read closed every fork rider (no K3, no K3b, forkblob FAIL, K4 dropped), so
F1 = K2 (exp58) is very likely final; the live levers are the f2 twin, an optional floatout rider and the K1 fallback -
`CONTEXT.md` l.1918-1937; `DECISIONS.md` §1b.

Ideas (`IDEAS.md` "CHANGES IN THIS CURATION (2)"; full list `ideas.json` meta.curations[n=2], 33 records changed):
- New (5): I-212 ANTIPAR (refuted, one-shot lab FAIL), I-213 GT-geometry fork flags (refuted), I-214 K3 bundle (refuted),
  I-215 floatout on x138 (in-plan, needs OK), I-216 ADDENDUM M (at risk, not in CONTEXT).
- To refuted/closed: I-071 forkmid, I-073 forkblob, I-074 DeepCenter K3b, I-075 6bba extension, I-183 linefit w0.7,
  I-072 float-coord divgates, I-081 DNVETO, I-158 tempfuse K4 (DROPPED), I-205 kaggle_lab, I-207 stage-resume.
- To lab-tested: I-201 exp60, I-204 density quartiles (info only); I-062 insertion gets its in-sample lab (+0.0157 / +0.0090).
- Updated: I-001 (K2 submit mechanics), I-010 (A5 ledger built), I-090 (twin dummy pushed), I-136 (P36 info only).
- Counts v4 -> 2: 211 -> 216 ideas; refuted 111 -> 124, lab-tested 18 -> 20, in-plan 21 -> 16, open-untested 5 -> 0,
  lb-tested 37 and deferred 19 unchanged. Strict orphans 5 -> 0; at risk: I-035, I-216 (I-158 left the list).

Facts and decisions (`FACTS.md`, `DECISIONS.md`, lines marked [c2]; `_curation/2/facts.json`):
- New facts: lab fork-veto break-even FP:TP >= 7.7 (public 0.265 vs lab 0.114), dummy clips' GT divisions 0/0/0/3
  (dummies prove plumbing only), GT vs predicted sister geometry, other teams' latency 2-8 h, how the ledger picks a
  family, K2/twin checksums, exp60 outcomes, floatout +0.0023 lab / ~+0.0001 private, rank #157/3,908 at 19:46.
- Contradictions resolved: C-01 (edge-J weighting), C-06 (LB noise), C-16 (R7 applies to new builds), C-17 (RESULTS P25 = 0.946).
- Contradictions new: C-19 (19:05 stamps written ~18:40), C-20 (P36 info only), C-21 (ADDENDUM M not recorded before T9),
  C-22 (break-even differs by bed), C-23 (L2 both tightening and loosening).
- `DECISIONS.md`: new §1b lab-gate decisions G01-G06; finals table: K2 very likely F1, K3/K3b/K4 none; P36 row info only.

Watchlist (`WATCHLIST.md`; `_curation/2/watch.json`):
- Done: W01 (ADDENDUM L code), W08, W09, W11 (forkblob built and closed). Cancelled: W13 (K3/K3b dummy gates), W24, W27, T01.
- Resolved insights: I10 (P36 reading written before it scored), I13 (kaggle_lab.py closed).
- New: W30-W37 (ADDENDUM M/round 2 untracked, closures, floatout fail-soft, memory pointer, RESULTS lab row) and I15-I20.

Alerts (`INDEX.md` TOP ALERTS, 12 after dedup):
- Resolved since v4: ADDENDUM L code missing (W01, merged 19:05 entry l.1896); P36 reading undecidable (rule recorded
  l.1904-1906); forkblob not built (built and FAILED, l.1918-1923); tempfuse build-or-drop (DROPPED, l.1912-1914);
  K3b one-blob share (moot, no K3b); R7 vs exp52 DIVINS_DUMP (C-16 resolved); stale RESULTS P25, CONTEXT §4 weighting
  and §11a noise (C-17, C-01, C-06); orphans I-204/I-205/I-207 closed.
- Still open from v4: twin dummy-gate code (now `--twin` only), admission table, untracked ext_* folders, friend A card
  (now fully stale), quota evidence, never tick exp56, TEAM.md 0.97 target.
- New: ADDENDUM M not recorded and T9 read first (C-21, W30); round 2 closures only in untracked files (W31); K2 `-m`
  message + `--k2/--family` ledger call (W16); morning OK list in `FINAL_REPORT_v4.md` §5 stale (W21); FLOATOUT_CHECK
  bare assert (I17, W33); stale memory pointer (W34); rank line in CONTEXT stale (W22); DeepCenter t* = 0.30 post-hoc (I19).
- Curator disagreement settled here: the ideas curator kept "L1+L2 K3b re-read (P ~0.1)" on the morning OK list; the
  facts and watch curators say no K3b under any reading (`experiments/exp60_trainlab/results.md` l.76-80). INDEX follows the latter.

## 3 - 2026-09-25 ~23:15 UTC (curation 3; git HEAD 1ca747b + untracked `research/wf_ideas_v4/round3/`)

Previous curation: 2 (~20:55 UTC, da154cb). New inputs:
- `CONTEXT.md` l.1938-1966 (entries 20:55-22:06) and commits 4f5d325, 1ca747b.
- `experiments/lb_poll/ledger.md` (22:53Z-23:03Z).
- `research/wf_ideas_v4/round3/report.json` + scan/v_*.json (finished 22:59Z).

Curator logs: `research/KNOWLEDGE/_curation/3/`.

**State change in one line.** The user OK'd AMENDMENT f2 at 22:06, so the finals pair is F1 = K2 (exp58) and F2 = the exp58n twin (twin gates PASS at 20:55). Both are submitted at 00:01 26 Sep. Round 3 adds a pre-score READ TABLE and declares the x138 tail saturated - `CONTEXT.md` l.1955-1966; `research/wf_ideas_v4/round3/report.json` R3-A1, R3-A2, new_facts (13).

**Ideas** (`IDEAS.md` "CHANGES IN THIS CURATION (3)"; full list in `ideas.json` meta.curations[n=3], 42 records changed):
- New (7):
  - I-217 READ TABLE: in-plan, at risk (not in CONTEXT).
  - I-218 widened K1 trigger: refuted.
  - I-219 twin floor 0.952: in-plan, needs OK.
  - I-220 density-gated insertion: refuted.
  - I-221 x138 structure repair / dedupe: refuted.
  - I-222 retention-guard hysteresis: refuted.
  - I-223 poller window `[:12]` -> `[:60]`: in-plan, at risk.
- To refuted/closed: I-216 ADDENDUM M, now recorded post-hoc in `CONTEXT.md` l.1938-1951.
- Updated:
  - I-090 twin: approved.
  - I-089/I-091: exp52 is now only the f2 fallback.
  - I-001, I-002 (F(K2) = 7.87 h), I-003 (R5(b) margin 1.63 h).
  - I-011: K1 triggers narrowed to READ TABLE rows 1/4/5.
  - I-036, I-062 (insertion by density quartile), I-136 (P36 still pending), I-094 (#164), I-201 (lab calibration rule).
- Re-closed with numbers: I-165/I-166 swapfix, I-145, I-151, I-173.
- Counts, curation 2 -> 3:
  - ideas 216 -> 223;
  - refuted 124 -> 129, in-plan 16 -> 18;
  - lb-tested 37, lab-tested 20, deferred 19 and open-untested 0 are unchanged.
- At risk: {I-035, I-216} -> {I-035, I-217, I-223}.

**Facts and decisions** (`FACTS.md` and `DECISIONS.md`, lines marked [c3]; `_curation/3/facts.json`):
- New facts:
  - F-RUN-13: F(K2) = 7.87 h.
  - F-RUN-14: the poller keeps only 5 rows.
  - F-RUN-15: twin dummy 1,038 s vs K2 1,512 s.
  - F-RUL-05: hidden reruns use no GPU quota.
  - F-RUL-11: the Overview page is unchanged.
  - F-MOD-14/15.
  - F-TRN-14..18: insertion gain by density quartile, x138 tail saturated with 0 true 2x2 swaps, node loss at clip boundaries, the lab over-rewards node-adding arms, no flicker penalty.
  - F-LB: #164/3,914 at 22:16, 18th of 65 in the 0.954 block, silver 32 ranks below us.
- Contradictions resolved: C-21 and C-23 (ADDENDUM M recorded as post-hoc notes, `CONTEXT.md` l.1938-1951).
- Contradictions new:
  - C-24: other teams' latency.
  - C-25: f2 OK time, memory ~21:00 vs CONTEXT 22:06.
  - C-26: stale RESUME POINT.
  - C-27: R3 reference for K2, #34 vs #35.
  - C-28: `--k2/--family` flags superseded.
  - C-29: the workflow prompt still lists closed riders.
- `DECISIONS.md`:
  - P37 (K2) and P38 (twin) are scheduled; P36 is still pending.
  - §1b adds G07-G11 (round-3 closures, proposed).
  - §2: twin = F2 candidate, with K1 triggers.
  - New §2b holds the proposed READ TABLE.

**Watchlist** (`WATCHLIST.md`; `_curation/3/watch.json`):
- Done: W30 (ADDENDUM M recorded, round 2 committed), W12/W17 (twin gates PASS), W21 item (1) (f2 OK).
- Partial: W31.
- Superseded by round 3: W06, W15, W18.
- Resolved insights: I16, I20.
- New:
  - W36: poller window.
  - W37: workflow prompt drift.
  - W38: round 3 untracked, no REPORT.md.
  - W39: READ TABLE.
  - W40: RESUME POINT.
  - W41: runtime records.
  - T12: the M6 window lapses 26 Sep 18:00.
  - I21-I30.

**Alerts** (`INDEX.md` TOP ALERTS, 12 after dedup):
- Resolved since curation 2:
  - ADDENDUM M not recorded (C-21, W30);
  - twin dummy has no `--twin` gate read (gates PASS, `CONTEXT.md` l.1955-1959);
  - round 2 untracked (committed in 4f5d325);
  - f2 needs the user's OK (OK at 22:06);
  - the K2 `--k2/--family` ledger call (the first exp token now sets the family, C-28);
  - quota check at 00:05 (now optional, W15);
  - the round-2 closures ANTIPAR, DNVETO, I-072 and K4 (in CONTEXT at 20:55).
- Still open from curation 2:
  - the K2 submit (now K2 + twin);
  - the morning OK list (now R3-A9);
  - closures into CONTEXT (now round 3 + I-213);
  - quota evidence;
  - friend A card;
  - admission table and untracked ext_* folders;
  - stale memory pointer;
  - I-035;
  - TEAM.md 0.97;
  - DeepCenter t* = 0.30 post-hoc.
- New:
  - READ TABLE not in CONTEXT (I-217, W39);
  - poller window (I-223, W36);
  - workflow prompt drift (W37);
  - stale 10:20 RESUME POINT (W40, C-26);
  - round 3 untracked, and CONTEXT cites a missing `round2/REPORT.md` (W38);
  - P36 still pending at the submit, so L(K2) may include queue time (W14).
- Curator disagreement settled here:
  - The `[:12]` slice is at `experiments/lb_poll/lb_poll.py` l.28 (verified at 1ca747b); `FACTS.md` F-RUN-14 and round 3 say l.27.
  - Poller urgency: the ideas and facts curators say "today", the watch curator says "now". INDEX uses "now", because the first quiet window is 23:15-23:55 tonight.

## 4 - 2026-09-26 ~01:20 UTC (curation 4; git HEAD b2cb928 + untracked `research/wf_ideas_v4/round4/`)

Previous curation: 3 (~23:15 UTC 25 Sep, 1ca747b). New inputs:
- `CONTEXT.md` l.1967-2025: the 23:12 round-3 entry, the READ TABLE, and the 00:02 RESUME POINT.
- Commits 1017c41 and b2cb928.
- `experiments/lb_poll/ledger.md` (01:13:07Z).
- `research/wf_ideas_v4/round4/report.json` + scan/v_*.json (01:15Z).

Curator logs: `research/KNOWLEDGE/_curation/4/`.

**State change in one line.** K2 (#37, ref 56563521) and the twin (#38, ref 56563534) were submitted at 00:02Z and are PENDING. P36 scored 0.954 and is info only. The READ TABLE is now in CONTEXT (1017c41, pushed 23:13:16Z). Round 4 found gaps in the table (CLARIFICATION v2), 0/2 finals ticked, and an unscheduled clean-proof poll. Sources: `CONTEXT.md` l.2006-2025; `experiments/RESULTS.md` l.69-71; `research/wf_ideas_v4/round4/report.json` R4-A1..A9.

**Ideas** (`IDEAS.md` l.11-22; `ideas.json` meta.curations[n=4], 52 records changed):
- New (11):
  - I-224 CLARIFICATION v2, at risk.
  - I-225 resubmit K2 on "Kaggle Error", needs an OK.
  - I-226 extra clean-proof polls, at risk.
  - I-227 provisional tick, at risk.
  - I-228 combined OK request, at risk.
  - I-229 29 Sep tick checklist, in-plan.
  - I-232 save round REPORT.md files, at risk.
  - I-233 poller error_description, open, strict orphan.
  - Refuted: I-230 in-block rank criterion, I-231 lowrefine lab arm, I-234 thedivyanshpant re-uploads.
- Status changes:
  - I-136 P36: in-plan -> **lb-tested** 0.954.
  - I-035 head-shift scale: at risk -> **refuted** (s_opt 0.75-1.0, round4 `scan_recheck.json` R4-RC-A).
  - I-215 floatout on x138 -> **refuted/closed** (`CONTEXT.md` l.2021-2022).
  - I-217 READ TABLE and I-223 poller `[:60]`: now in CONTEXT / APPLIED; no longer at risk.
- Updated:
  - I-001, I-090: submitted as #37 and #38.
  - I-011, I-219.
  - I-087, I-089, I-091.
  - I-094: rank #155/3,919 at 00:47Z.
  - I-135/I-201: exp60 replay lp30 +0.00083.
  - I-043: stays closed.
  - I-020, I-026, I-119: x138 renamed; y3uanm has no public weights.
  - I-062.
  - I-002 to I-004, I-008, I-010.
- Counts, curation 3 -> 4:
  - ideas 223 -> 234;
  - lb-tested 37 -> 38, refuted 129 -> 134, in-plan 18 -> 22, open-untested 0 -> 1;
  - lab-tested 20 and deferred 19 are unchanged.
- At risk: {I-035, I-217, I-223} -> {I-224, I-226, I-227, I-228, I-232}. The strict orphan is I-233.

**Facts and decisions** (`FACTS.md` and `DECISIONS.md`, lines marked [c4]; `_curation/4/facts.json`):
- New facts:
  - F-LB-09: the LB shows only our best entry, and P36's unrounded score is above #35's.
  - F-RUN-16: refs, the 08:02:12Z clean mark, and ETAs.
  - F-RUN-17: +210 s per failed poll attempt.
  - F-RUL-12: 0/2 ticked, so auto-select would pick P36 and #35.
  - F-MOD-16: K1 is ready; floatout is not ported.
  - F-MOD-17: head-shift scale and lowrefine duplicates.
  - F-TRN-19: leaf prune gives 0 on the LB and +0.0008 in the lab.
  - F-TRN-20: insertion gain breakdown.
- Updated: F-LB-01..08, F-RUN-03/12/14 (poller `[:60]` resolved), F-RUL-04/09/10, F-TRN-17.
- Contradictions:
  - Resolved: C-25 (f2 OK time), C-26 (stale RESUME POINT), C-27 (R3 reference), C-29 (workflow prompt).
  - Moot: C-20.
  - New:
    - C-30: missing REPORT.md files.
    - C-31: floatout status.
    - C-32: READ TABLE gaps.
    - C-33: incomplete pending-OK list.
    - C-34: dense-half precision 1/3 vs 2/4.
    - C-35: expected score times.
- `DECISIONS.md`:
  - §1: P36 scored; P37 and P38 submitted.
  - §1b: G12-G15 (head-shift, duplicate collapse, leaf prune on x138, floatout).
  - §2: 0/2 ticked.
  - §2b: now in CONTEXT.
  - New §2c: proposed CLARIFICATION v2.
  - §3: R3-R9 and §f updated.

**Watchlist** (`WATCHLIST.md`; `_curation/4/watch.json`):
- Done: W06, W14, W16, W36, W37, W39, W40, W41 (a-c).
- Cancelled or closed: W07 forkmid, W28 head-shift. W20/W21 are replaced by W47/W45.
- New:
  - W44-W52 (from R4-A1..A9);
  - T13-T20;
  - I31-I38 (auto-select default, best-entry-only LB row, error_description only via the API, insertion gain resting on 1 TP, the lp30 calibration point, the +210 s arithmetic, the x138 rename, the lowrefine and head-shift closures).
- Still overdue: W02/W03 friend A card, W04 admission table, W05 the ext_* commit.

**Alerts** (`INDEX.md` TOP ALERTS, 11 after dedup):
- Resolved since curation 3:
  - K2 + twin submit (#37/#38 at 00:02Z);
  - READ TABLE not in CONTEXT (1017c41);
  - stale 10:20 RESUME POINT (00:02 block l.2006);
  - workflow prompt drift;
  - poller window `[:60]`;
  - runtime records and quota evidence into CONTEXT;
  - P36 pending at the submit (it scored 23:42:50Z, before the submit);
  - I-035 (closed by measurement).
- Still open from curation 3:
  - closures into CONTEXT (now rounds 2-4);
  - untracked round folder and missing REPORT.md (now round 4, C-30);
  - friend A card;
  - admission table and ext_* folders;
  - `TEAM.md` 0.97.
- Morning OK list: carried over as the combined OK request (I-228).
- New:
  - CLARIFICATION v2;
  - combined OK request;
  - extra clean-proof polls;
  - mechanical score read;
  - 0/2 finals ticked, so a provisional tick is needed;
  - keep the poller session alive to 08:32:12Z;
  - floatout contradiction C-31;
  - 29 Sep checklist and durable reminders;
  - the thin lab evidence for the insertion (C-34).
- Curator disagreement settled here:
  - Floatout alert: the ideas curator dropped it because DECISIONS G15 already carries it; the facts and watch curators kept it. INDEX keeps it as [today], to be confirmed in the OK message.
  - Round-4 commit / REPORT.md urgency: "info" (ideas), "before-finals" (facts), "today" (watch). INDEX uses "today", because the commit is quiet-window work.

## 5 - 2026-09-26 ~04:05 UTC (curation 5; git HEAD f05389e + untracked `research/wf_ideas_v4/round5/`)

**Operations:** no score yet. #37 K2 (56563521) and #38 twin (56563534) are PENDING at 03:53:33Z (L > 3.85 h); nothing submitted since 00:02Z (`experiments/lb_poll/poll.log` l.2397-2402; `experiments/lb_poll/ledger.md` 03:53:35Z). Commit f05389e (01:20:05Z, pushed before any score) put CLARIFICATION v2, the round-4 records, the provisional tick rule and the 29 Sep checklist in CONTEXT (`CONTEXT.md` l.2026-2038). Intel: #160 of 3,922 at 03:16Z (`research/wf_ideas_v4/round5/report.json` new_facts).

**Ideas** (`IDEAS.md` l.11; `ideas.json` meta.curations[n=5], 42 records; `_curation/5/ideas.json`):
- New: I-235 K2'' = exp58d (in-plan, at risk), I-236 CLARIFICATION v3 (in-plan, at risk), I-237 bound B, I-243 ledger text fix (at risk), I-242 post-freeze re-solve (deferred-after-deadline); refuted I-238 (loosen trigger), I-239 (CPU replay of K2 tail), I-240 (fail-soft guards), I-241 (private-only crash hunt).
- Status: I-004 N1 in-plan -> refuted (superseded by I-235); I-009 D4 dropped; I-007/I-008 reframed around K2''; I-054, I-157, I-168, I-192 got round-5 recheck numbers.
- No longer at risk (in CONTEXT): I-224, I-227, I-229. At risk now: I-226, I-228, I-232, I-235, I-236, I-243. Strict orphan still I-233.
- Counts c4 -> c5: 234 -> 243; refuted 134 -> 139, deferred 19 -> 20, in-plan 22 -> 25; lb-tested 38, lab-tested 20, open-untested 1 unchanged.

**Facts and decisions** (`FACTS.md`, `DECISIONS.md`, lines marked [c5]; `_curation/5/facts.json`):
- New facts: F-RUN-18 (concurrent runs; bound B), F-RUN-19 (one hidden run covers public + private), F-MOD-18 (builder refuses deadline moves; D4 has no code), F-MOD-19 (K2 failure behaviour), F-TRN-21 (post-freeze transitions, ceiling +0.0063), F-TRN-22 (already-divided -0.00068 on x138; fork removal 0 for 5), F-TRN-23 (AdaBN blocker).
- Updated: F-DAT-11, F-LB-01/02/03/04/06/08, F-RUN-12/16/17, F-RUL-04/10/12, F-MOD-16; table rows F-LB-04/06 repaired.
- Contradictions: C-31, C-32 resolved; C-30 partly resolved (round3/4 REPORT.md saved); C-33 still open; C-35 updated with round-5 ETAs. New: C-36 (GT on frozen frames vs CONTEXT l.22), C-37 (#34 fallback vs the Never line), C-38 (row-5 queue reading), C-39 (unbuildable runtime remedy), C-40 (stale ledger texts), C-41 (W44 status), C-42 (submission count off by one).
- `DECISIONS.md`: §1 P37/P38 still PENDING; §1b G16-G19 (already-divided, post-freeze re-solve, AdaBN, runtime-trigger builds); §2 K2'' proposed row and pairs-not-labels; §2c marked in CONTEXT; new §2d proposed CLARIFICATION v3 + OK request.

**Watchlist** (`WATCHLIST.md`; `_curation/5/watch.json`):
- Done: W44 (v2 in CONTEXT), W48 rule text, W49 round-4 records, W50 checklist text, round3/4 REPORT.md; W33 floatout closed. W46 superseded by W55.
- New: W55-W60 (R5-A1..A8), T21-T23, I39-I46. Resolved insights: I31-I33, I35, I37, I38.
- Still overdue: W02/W03 friend A card, W04 admission table, W05 ext_* commit, W34 memory residue.

**Alerts** (`INDEX.md` TOP ALERTS, 11 after dedup):
- Resolved since curation 4: CLARIFICATION v2 not in CONTEXT; provisional tick rule / checklist not in CONTEXT; floatout contradiction C-31; round-4 closures into CONTEXT; round3/4 REPORT.md.
- Carried over: OK request (now 7 items, R5-A3); clean-proof polls (now a background job, R5-A1); mechanical score read + provisional tick; poller uptime (stop rule moved to after 09:32:18Z); durable 29 Sep reminders; admission table / ext_* / friend A card; I-233 orphan.
- New: CLARIFICATION v3 (V1-V7); unbuildable runtime trigger (K2'' prep); #34 pairs-not-labels contradiction; stale ledger texts; round-5 records incl. CONTEXT l.22 correction; round5/round2 REPORT.md missing; LB entry count C-42.
- Dropped from INDEX: the thin insertion lab evidence (C-34) and `TEAM.md` "0.97" (C-04); both stay in `FACTS.md`.
- Curator disagreement settled here: #34 contradiction is [today] (ideas) vs [now] (watch); INDEX folds it into alert 1 (v3, [now]). Stale ledger texts: [today] (ideas) vs [info] (facts); INDEX uses [today], neutralised by v3 V6. Clean-proof job: [today] (ideas) vs [now] (facts, watch); INDEX uses [now], since the job must be started well before 07:45Z.

## 6 - 2026-09-26 ~06:30 UTC (curation 6; git HEAD 2f6ec9d + untracked `research/wf_ideas_v4/round6/`)

**Operations:** no score yet. #37 K2 (56563521) and #38 twin (56563534) are PENDING at 06:24:02Z (L > 6.36 h, 0 gaps; `experiments/lb_poll/poll.log` l.3312-3317; `experiments/lb_poll/ledger.md` 06:24:03Z). Since curation 5, all pre-score: fc51b75 (04:04:45Z) put CLARIFICATION v3 V1-V7, the round-5 records and "OK REQUEST posted" in CONTEXT (`CONTEXT.md` l.2039-2051); 801de5a/2f6ec9d (04:11-04:12Z) merged the K2'' builder change (l.2052-2057; not built). Clean-proof job PID 13436 runs beside poller PID 20052 (V7, l.2046). No user reply to the OK request is recorded. Round 6 ran at 06:17Z (`research/wf_ideas_v4/round6/report.json`, untracked, no REPORT.md). Intel: #162 of 3,922 at 05:46Z (`FACTS.md` F-LB-02 [c6]).

**Ideas** (`IDEAS.md` l.11; `ideas.json` meta.curations[n=6], 51 records; `_curation/6/ideas.json`):
- New in-plan: I-244 CLARIFICATION v4 (at risk), I-245 W1 OK timing vs T0 (at risk), I-246 R5 basis F' = 8.27 h, I-247 V3b K2'' gate, I-248 W6 poller scope (at risk), I-249 morning brief (at risk), I-250 score-read cheat sheet. New deferred: I-252 lab->LB lessons. New refuted: I-251 K4 = K2 + efpost (kept as a FACT), I-253 tick before scores, I-254 F2 swap at k >= 0.955, I-255 "K1 shares both timers".
- No longer at risk (in CONTEXT pre-score): I-236 v3, I-228 OK request, I-226 clean-proof job, I-235 builder change. I-237 gains B'. Rechecks on x138: I-164 stitch closed, I-184/I-183 linefit null, I-161/I-162 closure kept with neutral wording, I-196 official edge FP rule.
- At risk now: I-229, I-232, I-243, I-244, I-245, I-248, I-249. Strict orphan still I-233.
- Counts c5 -> c6: 243 -> 255; refuted 139 -> 143, deferred 20 -> 21, in-plan 25 -> 32; lb-tested 38, lab-tested 20, open-untested 1 unchanged.

**Facts and decisions** (`FACTS.md`, `DECISIONS.md`, lines marked [c6]; `_curation/6/facts.json`):
- New facts: F-RUN-20 (15.4% run-to-run spread, per-clip insertion cost), F-MOD-20 (V3 sha-only K2'' gate cannot catch a mis-build), F-TRN-24 (stitch closed), F-TRN-25 (linefit: no detectable effect), F-TRN-26 (efpost, neutral: 6bba +0.00174, 44b6 0), F-TRN-27 (lessons for after 29 Sep).
- Updated: F-MET-03 (exact official edge FP rule, `tools/official/src/tracking_cellmot/metrics.py` l.157-195), F-DAT-11, F-LB-01..08, F-RUN-10/12/13/16-19, F-RUL-10/11/12, F-MOD-16/18 (builder accepts (37800, 32400)), F-TRN-02.
- Contradictions: C-37, C-38, C-39, C-41 resolved by v3; C-40 resolved except the A5-F text; C-30, C-33, C-35, C-36, C-42 updated. New: C-43 (B vs B'), C-44 (R5 blanket vs F' = 8.27 h), C-45 (poller stop time), C-46 (reading the edge filter's LB zero), C-47 (no rule on when a late OK counts).
- `DECISIONS.md`: P37/P38 rows + [c6] slot paragraph; G11, G16-G19 status; new G20-G22 (stitch, linefit, K4/efpost); §2d marked in CONTEXT; new §2e proposed v4 + cheat sheet; §3 R3-R10 and §f updated.

**Watchlist** (`WATCHLIST.md`; `_curation/6/watch.json`):
- Done: W56 (v3), W45 (OK request posted), W58 (builder), W57 (round-5 records listed), W60 for round 5 (REPORT.md committed). W55 running (PID 13436).
- New: W61-W67, T24-T27, I47-I55. Resolved insights: I36, I40-I43, I45.
- Still open: W03 friend A card, W04 admission table, W05 ext_* commit, W26, W31, W34 memory residue, W35 RESULTS.md rows, W50 reminders.

**Alerts** (`INDEX.md` TOP ALERTS, 10 after dedup):
- Resolved since curation 5: CLARIFICATION v3 not in CONTEXT; OK request unposted; clean-proof job not running; runtime trigger unbuildable (builder merged); stale A6/D4 ledger texts (gone for now); round-5 REPORT.md.
- Carried over: score read + provisional tick (now with cheat sheet, B'); poller stop rule (now also later 26 Sep submissions, C-45); round records into CONTEXT by 12:00 (now round 6 + l.22 + B5 l.196); durable 29 Sep reminders; admission table / ext_* / friend A card / memory residue; I-233 orphan.
- New: CLARIFICATION v4 (W1-W8, B', F', V3b); late-OK rule vs T0; morning brief unsent; K2'' as likeliest decision; clean-proof window hygiene (T24); R5 blanket contradiction (C-44, folded into alert 1); edge-filter wording warning (C-46, folded into alert 8).
- Curator disagreement settled here: finals reminders are [deadline/today] (ideas, facts) vs [before-finals] (watch); INDEX uses [before-finals] for the reminders themselves and asks for them today in the brief (alert 3). Round-6 REPORT.md: [today] (ideas) vs [info] (facts) vs [now] (watch); INDEX folds it into alert 1 ([now], same commit as v4).

## 7 - 2026-09-26 ~09:05 UTC (curation 7; git HEAD 42d1a55 + untracked `research/wf_ideas_v4/round7/`)

**Operations:** both finals scored. #37 K2 exp58 (56563521) = 0.954, clean, L in (7.36, 7.54] h; #38 twin exp58n (56563534) = 0.953, L in (6.69, 6.87] h; READ TABLE row 3 -> finals #37 + #38 (`CONTEXT.md` l.2070-2081; `experiments/RESULTS.md` l.70-71; `experiments/lb_poll/poll.log` headers 06:54:06Z twin, 07:34:12Z K2). CLARIFICATION v4 was committed pre-score (64f0551 06:31:36Z, `CONTEXT.md` l.2058-2069); no OK was given, strict text only. Clean-proof job stopped (moot). Commits since curation 6: 64f0551, b4144e9 (score read), 7107b6d (option b, l.2082), 4d0c477 (wave check, l.2083-2095), 4790f1f (rules check, l.2096-2109), 539ea8b + 42d1a55 (overlap-consensus line and its PAUSE, l.2110-2129; after the three curators' reads). Finals NOT ticked: API SELECTED = 0 at 08:37:15Z (`research/wf_ideas_v4/round7/report.json` new_facts 4). Rank #183 at 08:22Z, #185 at 08:38Z (`CONTEXT.md` l.2086; round7 `report.json` new_facts 1). Round 7 ran 08:45Z (untracked, no REPORT.md).

**Ideas** (`IDEAS.md` l.11; `ideas.json` meta.curations[n=7], 61 records; `_curation/7/ideas.json`):
- lb-tested: I-001 safetail/K2 (P37), I-090 twin (P38), I-036 lowrefine (d1 = d2 = 0); I-062 insertion gains its 2nd (P37) LB transfer.
- Applied / no longer at risk: I-244 v4, I-245, I-246, I-248, I-217, I-224, I-236, I-250, I-226, I-228, I-003, I-010; I-249 superseded.
- Moot -> refuted: I-011 K1, I-225, I-219 twin floor, I-235 K2'', I-237 B/B', I-247 V3b, I-091 exp52 fallback.
- New (I-256..I-265): in-plan I-256 E10 PORT RULE, I-257 RESUME POINT, I-258 API tick check, I-259 round focus text, I-262 E10 dry run, I-265 cadence (option b); refuted I-260 forkmid 6bba replication, I-263 wave-source hunt, I-264 leaked CSVs; deferred I-261 axial localisation.
- Rechecks on x138: I-186/I-141 gap LAP + sandwich closed (TP 5 / FP 458), I-042 z-split closed, I-038/I-144/I-156 closed on value/LB/R8, I-071 forkmid the one power-limited closure.
- Counts c6 -> c7: 255 -> 265; lb-tested 38 -> 41, refuted 143 -> 153, deferred 21 -> 22, in-plan 32 -> 28; lab-tested 20, open-untested 1 unchanged. Strict orphan I-233; at risk I-229, I-232, I-243, I-256, I-257, I-259, I-262.
- Not yet in the ledger (INDEX flag): I-208 overlap consensus still "refuted by R9" (`IDEAS.md` l.391) although `CONTEXT.md` l.2110-2129 makes it a paused candidate line (K6).

**Facts and decisions** (`FACTS.md`, `DECISIONS.md`, lines marked [c7]; `_curation/7/facts.json`):
- New facts: F-LB-10 (E10 definition/horizon), F-RUN-21 (headroom moot), F-RUL-13 (API reads ticks), F-RUL-14 (rules check: leaked CSVs not allowed; sweep and test-structure use not prohibited -> R7/R9 team policy), F-MOD-21 (verbatim port cannot carry C01), F-TRN-28 (gap LAP closed), F-TRN-29 (node-miss anatomy, z-offset excess).
- ~30 rows updated (ranks, 0.954 block, insertion 3rd LB transfer, insertion cost <= 0.85 h, 0/2 ticked, K1/K2''/V3b moot); F-RUL-08 relabelled team policy.
- Contradictions resolved/moot: C-33, C-35, C-43, C-44, C-45, C-47; updated C-02, C-30, C-36, C-40, C-42; new C-48..C-57 (E10 horizon, P(trigger), poller horizon, insertion cost, API ticks, headroom reason, power-limited closures, port vs §f(iii), live RESUME POINT, R9 rule vs policy).
- `DECISIONS.md`: P37/P38 results + row-3 decision; slot note (26 Sep slots empty); G23-G26; §2 DECIDED (0/2 ticked) with an E10-port row; §2b/§2e marked applied/in CONTEXT; new §2f proposed E10 PORT RULE P1-P8; §3 R3/R5 applied, R6 never triggered, R7/R9 team policy.

**Watchlist** (`WATCHLIST.md`; `_curation/7/watch.json`):
- Done: W47, W61, W64, W35; K2'' and runtime reminders cancelled; resolved insights I48-I50, I55, I05, I26.
- New: W69-W75 (E10 rule, RESUME POINT, round prompt, records, poller horizon, user message, REPORT.md), I56-I63.
- Still open: W03 friend A card, W05 ext_* untracked, W26 NEXT_RESEARCH, W50 reminders, W54 tick.

**Alerts** (`INDEX.md` TOP ALERTS, 10 after dedup):
- Resolved since curation 6: CLARIFICATION v4 not in CONTEXT; late-OK rule (no OK given); morning brief (superseded); clean-proof window; score read; K2'' decision (moot, K2 clean); poller K2-only stop text (superseded by the 29 Sep 20:00 horizon).
- Carried over: finals tick (now the top alert, 0/2 by API); round records into CONTEXT by 12:00 (now rounds 5-7); durable 29 Sep reminders; poller uptime; friend A card / ext_* / I-233.
- New: overlap-consensus line paused for this report (from CONTEXT after the curators; I-208 stale); plan-table correction (E10 to 29 Sep 00:00, P ~5-10%, rank #185); E10 PORT RULE + conditional yes; stale RESUME POINT / MEMORY.md; round prompt text; insertion cost C-51 (info).
- Curator disagreement settled here: plan-table correction is [today] (ideas, facts) vs [now] (watch); INDEX uses [now], sent with the tick request. Round records are [today] (ideas) vs [before-finals] (facts) vs [now] (watch); INDEX uses [today, by 12:00]. Poller horizon [info] (ideas, watch) vs [info] forgotten (facts): kept [info].

## 8 - 2026-09-26 ~11:10 UTC (curation 8; git HEAD 24dcdea on the REWRITTEN main + untracked `research/wf_ideas_v4/round8/`)

**Operations:**
- **Finals ticked 2/2** = [56563521, 56563534] (#37 K2 + #38 twin). API-verified 09:10:07Z, still 2/2 at 10:45Z. Sources: `CONTEXT.md` l.2154-2156; `research/wf_ideas_v4/round8/report.notes.md`.
- **E10 PORT RULE in CONTEXT** (09:03, l.2138-2147) and **in force** since the user's conditional yes at 09:10 (l.2157-2158). Not triggered at 10:17-10:23Z.
- **Overlap-consensus line:** gates at 08:58 (l.2110-2128), paused, resumed at 09:10 (l.2159-2160). **STOPPED at 10:52 by G-A FAIL**: 43 of 62 pairs vs >= 60; proxy lab -0.00047 (l.2177-2186). No G-P and no K6 submission. The exp64 lab finishes as INFO only.
- **Git history rewritten:** cloud branch at 10:09, main at 10:15 (l.2161-2176). Old hashes map via `experiments/git_rewrite_map_2026-09-26.txt`. Old-history worktree branches come in by cherry-pick only.
- **LB:** no new submission; #188 at 10:17Z; silver margin 13 -> 7-8 ranks (`research/wf_ideas_v4/round8/scan_browser.json`).
- **Round 8** ran 10:16-10:46Z. It is untracked and has only `report.notes.md` (no report.json or REPORT.md).
- Commits since curation 7 (new hashes, `git log --oneline`): 3992fd0 (E10 rule), d3ca495 (ticks 2/2, E10 in force, OC resumed), 1953f18 (exp64 lab kernels), 86a2f75 (round prompt), da645e8 + 4e760fb (cloud day 2), fd23e0a + b41ec05 (rewrites), 24dcdea (OC stop).

**Ideas** (`IDEAS.md` l.11; `ideas.json` meta.curations[n=8], 31 records; `_curation/8/ideas.json`):
- **Applied:** I-227 and I-258 (ticks), I-256 (E10 rule in force), I-259 (round prompt, 86a2f75). I-257 is only partly applied.
- **I-208 overlap consensus:** reopened by the rules check and user decision, then closed by G-A (ledger row updated; no longer "refused by R9").
- **New I-266..I-276:**
  - OC sub-ideas I-266 (G-P bit-probe and its variants), I-267 (K6 and hardening), I-268 (K6 finals rule), I-269 (dt-uniqueness), I-271 (position averaging) and I-273 (post-hoc G-A rescue) are refuted or moot.
  - I-270 (exp64 G-B lab, INFO read) is in-plan.
  - Deferred: I-272 (cross-copy division import) and I-276 (GT-noise mimicry).
  - New ops items: I-274 (R9 amendment line, at risk) and I-275 (post-rewrite git hygiene).
- **Round-8 rechecks:**
  - I-029 constant z shift: corrected (+0.0016 in-sample, ~+0.0003 expected on new embryos) and deferred; I-041 cross-referenced.
  - I-079 split-aware relink: deferred (reach <= 7/62).
  - I-058 DivNet veto stays closed.
- **Counts c7 -> c8:** 265 -> 276 ideas; refuted 153 -> 157; deferred 22 -> 26; in-plan 28 -> 31; lb-tested 41, lab-tested 20 and open-untested 1 unchanged. Strict orphan I-233. At risk: I-229, I-232, I-243, I-257, I-262, I-274 (I-256 and I-259 left the list; I-274 joined).

**Facts and decisions** (`FACTS.md`, `DECISIONS.md`, lines marked [c8]; `_curation/8/facts.json`):
- **New facts:**
  - F-RUN-22: overlap registration runtime.
  - F-MOD-22: OC artefacts, all outside main.
  - F-TRN-30: proxy G-B -0.00047.
  - F-TRN-31: z shift +0.0016 in the lab; not a finals candidate.
  - F-TRN-32: DivNet veto and split-aware relink stay closed.
  - About 20 rows updated (ticks, ranks, E10 in force); new header note on the rewritten hashes.
- **Contradictions:**
  - Resolved: C-48 (E10 horizon), C-50 (poller horizon), C-55 (port vs §f(iii), rule now in force), C-56 (live RESUME POINT).
  - New C-58..C-67: R9 vs the user's OC decision; G-A 65 vs 62 pairs; G-LB vs R4/f2; the E10 pair had K6 been adopted; resume hygiene; old hashes; entries below `## 9.`; z-shift value; splice harm; "official metric" in G-B.
- **`DECISIONS.md`:**
  - P37/P38 marked ticked; G27-G30 added in §1b; §2 gains the tick paragraph plus K6 and E10 rows.
  - §2f marked in force; new §2g holds the OC gates table.
  - R1-R10 and the finals rule each get a [c8] status line.

**Watchlist** (`WATCHLIST.md`; `_curation/8/watch.json`):
- **Done:** W54 (tick), W69 (E10 rule), W74 (user message), W60/W75 (round-7 report and records), W26 (cloud day-2 check-in).
- **Partly done:** W70 (RESUME POINT), W71 (round prompt).
- **New:**
  - W76 (rounds), W79 (sync local main), W80 (resume hygiene), W81 (records), W82 (exp64 INFO read), W83 (save OC evidence by cherry-pick);
  - T26 (silver margin), T27 (~22:00Z line);
  - insights I64-I73.
- **Still open:** W03 friend A card, W05 ext_* untracked, W50 reminders.
- **Note from INDEX:** local main equals origin/main 24dcdea at ~11:08Z (`git status -sb`), so the git part of W79 is resolved. `experiments/lb_poll/ledger.md` shows M from the live poller.

**Alerts** (`INDEX.md` TOP ALERTS, 10 after dedup):
- **Resolved since curation 7:** finals not ticked; E10 rule not in CONTEXT; plan-table correction sent; OC line waiting on the user (stopped by G-A); round 7 records (round 7 done; the rest carried over); I-208 ledger stale (fixed by the ideas curator).
- **Carried over:** records into CONTEXT by 12:00 (remaining items); stale RESUME POINT / MEMORY.md; round prompt text (now "OC listed as active" plus l.36 headroom); durable 29 Sep reminders; poller uptime; friend A card, ext_* and I-233.
- **New:**
  - git after the rewrite: cherry-pick only, friend A reset, no Co-Authored-By trailer despite the harness reminder;
  - exp64 G-B as INFO only;
  - round 8 untracked, with the OC evidence only on worktree branches;
  - R9 amendment line;
  - E10 dry run skipped in round 8;
  - "public = one embryo" is a guess;
  - z shift post-deadline; old hashes; silver margin 7-8 (info).
- **Curator disagreements settled here:**
  - Git merge risk: [now] (facts, watch) vs [today] (ideas, I-275). INDEX uses [now].
  - Records: [now] (watch). INDEX uses [now, by 12:00].
  - R9 amendment: [today] (ideas) vs [info] (facts). INDEX folds it into resume hygiene [today].
  - Local-main sync W79 [now]: resolved by the time of INDEX.

## 9 - 2026-09-26 ~13:25 UTC (curation 9; git HEAD 69d6be2 = origin/main + untracked `research/wf_ideas_v4/round9/` and `experiments/exp64_overlap_lab/results_info_post_stop.md`)

**Operations:**
- **Finals still ticked 2/2**, [56563521, 56563534]. A third API SELECTED check ran at 13:00:41Z. The "11:42" check in a task text is in no log (C-71). Sources: `CONTEXT.md` l.2154-2156; `research/wf_ideas_v4/round9/report.notes.md`.
- **Overlap consensus closed for good.** The R9 amendment was recorded at 11:06 (`CONTEXT.md` l.2187-2197). The post-stop exp64 G-B on the K2 stack is -0.00143, bootstrap lower -0.00200 (`CONTEXT.md` l.2198-2204; `experiments/exp64_overlap_lab/results_info_post_stop.md`). The round prompt now lists E10 as the only active line (69a35b4).
- **E10:** not triggered at 12:47Z or 13:00:51Z. `experiments/ext_robust-3d-cell-tracking/` is a CPU classical baseline scoring 0.432, so it is irrelevant (`research/wf_ideas_v4/round9/scan_browser.json` r9-e10-not-triggered-public-unchanged).
- **LB:** no new submission. We are #204 of 3,928 at 12:46Z, 8 ranks below the ~196 silver line (was 7-8 above it). The 0.953 block is ~330 teams (`research/wf_ideas_v4/round9/scan_browser.json` r9-lb-delta-1246).
- **Round 9** ran 12:46-13:10Z. It is untracked, has `report.json` R9-A0..A9 and no REPORT.md; round 8 also has no REPORT.md.
- **Commits since curation 8** (`git log --oneline 24dcdea..69d6be2`): 957d8bf + 66a18e4 (R9 amendment record, round-8 report.json), 69a35b4 (round prompt), 69d6be2 (exp64 post-stop info).

**Ideas** (`IDEAS.md` l.11; `ideas.json` meta.curations[n=9], 36 records; `_curation/9/ideas.json`):
- **Status changes:** I-270 in-plan -> lab-tested (G-B -0.00143); I-276 deferred -> refuted (reach 1/83 FN, 1/25 FP); I-222 refuted -> deferred (embryo-dependent fallback, GPU counterfactual after 29 Sep).
- **Applied:** I-274 (R9 amendment in CONTEXT 11:06).
- **New:** I-277 DeepCenter readmit veto (refuted; a leaf prune in disguise), I-278 F2 -> P36/#34 (refuted), and I-279 E10 PORT RULE P4b (in-plan, at risk).
- **Notes and aliases:**
  - I-177/179/180/181: probes 21-23 are real -0.002 reads.
  - I-102: secondary weight 0.80.
  - I-062: ~1/6 lab-to-public transfer.
  - I-066: OOF insertion threshold.
  - I-029: z shift + insertion.
  - Ops notes updated on I-208, I-229, I-232, I-243, I-257, I-258, I-259, I-262, I-265, I-275 and others.
- **Counts c8 -> c9:** 276 -> 279 ideas. Refuted 157 -> 159, lab-tested 20 -> 21. Unchanged: lb-tested 41, deferred 26, in-plan 31, open 1. Strict orphan: I-233. At risk: I-229, I-232, I-243, I-257, I-262, I-275, I-279 (I-274 left the list; I-275 and I-279 joined).

**Facts and decisions** (`FACTS.md`, `DECISIONS.md`, rows marked [c9]; `_curation/9/facts.json`):
- **New facts:** F-TRN-33 (division-loss anatomy), F-TRN-34 (link family: real -0.002 reads), F-TRN-35 (exp64 bed fully in-sample). About 30 rows updated (ticks, rank #204, E10 checks).
- **Contradictions:**
  - Resolved: C-58 (R9 amendment recorded) and C-59 (the splice hurts on the real stack).
  - Corrected: C-26 (MEMORY "Resume point" line was already right).
  - New: C-68 (secondary weight 0.80 vs the 0.475 label), C-69 ("public = one embryo" is an inference), C-70 (OC stop sequence; the PC9-01 honesty gap is refuted), C-71 (the unlogged "11:42" check).
- **DECISIONS.md:** new lab gates G31-G33 in §1b (G-B post-stop; round-9 rechecks; last-window ideas). §2 gains a still-2/2 paragraph. §2f adds the proposed P4b and the ledger fix. §2g is marked CLOSED. R1-R10 and the finals rule get [c9] lines.

**Watchlist** (`WATCHLIST.md`; `_curation/9/watch.json`):
- **Done:** W79 (local main in sync), W81 (I-208 row), W82 (exp64 INFO read), rounds 8 and 9, R8-A1/A3.
- **Overdue:**
  - W80 (resume hygiene, = R9-A1).
  - W86 (both REPORT.md files).
  - W57/W66/W31/W72 (curator records missed at 12:00).
  - W71 (round prompt l.20, l.36).
  - W03 (friend A card).
  - W05 (untracked items).
- **New:** W87 (P4b), W88 (ledger exp63), W89 (OC sequence note), W90 (records), W91 (lessons draft), W92 (user message; absorbs W50), W93 (never push exp65/exp66); T30 (30 Sep private column); insights I74-I84.

**Alerts** (`INDEX.md` TOP ALERTS, 9 after dedup):
- **Resolved since curation 8:**
  - The exp64 G-B INFO read (done, -0.00143).
  - The R9 amendment line (in CONTEXT 11:06).
  - The round prompt listing OC as active (69a35b4).
  - The local-main sync.
  - Round-8 report.json (committed in 66a18e4; REPORT.md still missing).
- **Carried over:**
  - Resume hygiene (now [now]).
  - Git cherry-pick of the OC evidence (commit list grew to 6).
  - Records (deadline missed).
  - Round prompt l.20/l.36.
  - 29 Sep reminders (now part of the user message).
  - Tick re-checks and poller.
  - "Public = one embryo".
  - Friend A card, ext_* and I-233.
- **New:**
  - E10 port traps: P4b metadata, exp63 ledger rule.
  - Round-9 artefacts unsaved.
  - Lessons draft only in a scan file.
  - Light-mode question.
  - Weight 0.80 vs 0.475.
  - Stale MEMORY copy injected into subagents.
  - Unlogged "11:42" check.
- **Curator disagreements settled here:**
  - Resume hygiene: [now] (facts, watch) vs [today] (ideas). INDEX uses [now].
  - E10 traps: [now] (watch) vs [today] (ideas, facts). INDEX uses [now, before ~15:30Z].
  - OC cherry-pick: [today] everywhere.
  - User message: [now] (watch) vs [today] (ideas, facts). INDEX uses [today].

## 10 - 2026-09-26 ~15:55 UTC (curation 10; git HEAD 6064d85 = origin/main + untracked `research/wf_ideas_v4/round10/` and the amanatar v10 pull `experiments/ext_optimized-biohub-max-score/v10_2026-09-26/`)

**Operations:**
- **Commits since curation 9** (`git log --oneline 69d6be2..6064d85`):
  - d6a0c73: round 9 records. This covers the 13:27 RESUME POINT, INTEL, the OC SEQUENCE NOTE, E10 P4b, the POINTER (`CONTEXT.md` l.2205-2219), the exp63 -> x138 ledger rule with a test, `research/wf_ideas_v4/round9/REPORT.md` and `LESSONS_draft.md`.
  - 4a44a83: curation 9 and the intel pulls.
  - 3d6a704..a782fa1: the 6 OC commits, cherry-picked.
  - 6064d85: R9-A5 DONE. The finals rebuild is byte-identical, 184 tests pass, and exp65/exp66 hold NEVER_PUSH (`CONTEXT.md` l.2220-2229).
- **Finals still ticked 2/2**, [56563521, 56563534]. The API showed SELECTED at 15:23:10Z and 15:24:58Z (`research/wf_ideas_v4/round10/report.notes.md`; `IDEAS.md` I-258).
- **E10 not met** at ~15:24Z. amanatar v10 was running and unscored, with validator ON, a 45-key train-stem sweep and a 30600 s override. It fails P3/P4b, so it is info only (`experiments/ext_optimized-biohub-max-score/v10_2026-09-26/NOTES.md`; `IDEAS.md` I-025). x138's slug is now `anvithpothula/biohub-0-953-lb-original`; the old slug returns 404 (`FACTS.md` F-LB-05, C-73).
- **LB:** #210 of 3,930 at 15:16:37Z, 14 ranks below public silver (8 at 12:46Z). No new submission (`FACTS.md` F-LB-02 [c10]).
- **Round 10** ran 15:16-15:43Z. It is untracked, has `report.json` R10-A0..A9 and no REPORT.md; the harness refused the write again. round8/REPORT.md is also still missing (`research/wf_ideas_v4/round10/report.json` R10-A0).

**Ideas** (`IDEAS.md` l.11; `ideas.json` meta.curations[n=10], 38 records; `_curation/10/ideas.json`):
- **Applied:**
  - I-257 (RESUME POINT l.2205-2212);
  - I-279 (P4b l.2217);
  - I-243 (ledger exp63 -> x138 + test);
  - I-275 (OC cherry-pick, l.2220-2229);
  - I-259 (round prompt block count).
- **Status changes:**
  - I-146: refuted by measurement. x138's dormant rescue forced on gives +0.00033, W/L 7/47.
  - I-097/I-107: structurally blocked on x138 (V1284 head coupling).
  - I-209: now closed on reach rather than policy.
  Sources: `research/wf_ideas_v4/round10/scan_recheck.json`; `DECISIONS.md` G34, G35.
- **New:**
  - I-280 P4c, I-281 `tools/e10_port_gate.py`, I-282 e10_watch snapshots and the wake mechanism, I-283 PRIVATE-READ PREDICTIONS C1-C4. All four are in-plan and at risk.
  - I-284 protect the finals' inputs (in-plan).
  - I-285 pre-relink dump hook (deferred).
  - The r10h-8 post-deadline list is linked from I-222, I-261, I-029, I-242, I-285, I-079, I-208 and I-110.
- **Counts c9 -> c10:** 279 -> 285 ideas. Deferred 26 -> 27, in-plan 31 -> 36. Unchanged: lb-tested 41, lab-tested 21, refuted 159, open 1. Strict orphan: I-233. At risk: I-229, I-232, I-280, I-281, I-282, I-283 (I-243, I-257, I-262, I-275 and I-279 left the list).

**Facts and decisions** (`FACTS.md`, `DECISIONS.md`, rows marked [c10]; `_curation/10/facts.json`):
- **New facts:** F-RUN-23 (ops at 15:25-15:46Z: poller alive, 0 gaps, no pending reboot), F-MOD-23 (dormant ADAPTIVE_SHORT_TRACK_RESCUE in x138 and both finals) and F-TRN-36. 26 rows were updated.
- **Contradictions:**
  - Resolved: C-26, C-56, C-62, C-63, C-70, C-71.
  - Updated: C-05, C-30, C-64, C-68, C-69.
  - New:
    - C-72: amanatar v10 REPAIR 27000 at the first hit, overridden to 30600 at l.6583.
    - C-73: x138 slug.
    - C-74: the validator scope in P3.
    - C-75: stale MEMORY index injected into sessions.
    - C-76: skeptic check time.
    - C-77: LESSONS_draft numbers.
    - C-78: 29 Sep slot use (no conflict).
- **DECISIONS.md:** new gates G34/G35 in §1b; §2 CURRENT snapshot table; §2f (P4b in force, v10 no port, P4c proposed); §2g archived; [c10] lines on R1-R10.

**Watchlist** (`WATCHLIST.md`; `_curation/10/watch.json`):
- **Done:** W80 (resume hygiene), W87 (P4b), W88 (ledger exp63), W83 (cherry-picks), W89 (OC sequence note), rounds 9 and 10.
- **Overdue:**
  - W86 residue: round8 and round10 REPORT.md.
  - W90/W71: records due 12:00 (CONTEXT l.22, l.196, out_valid, efpost), plus round prompt l.36.
  - W03: friend A card.
- **New:**
  - W94: ROUND 10 RECORD and hygiene commit.
  - W95: P4c.
  - W96: gate script.
  - W97: e10_watch and the post-R8 schedule.
  - W98: lessons fixes.
  - W99: private-read predictions.
  - W100: curator records.
  - W101: user message; absorbs W92.
  - W102: finals-input protection.
  - Insights I85-I95.

**Alerts** (`INDEX.md` TOP ALERTS, 9 after dedup):
- **Resolved since curation 9:**
  - Resume hygiene: the RESUME POINT and POINTER were written; MEMORY.md was updated on disk.
  - P4b is in CONTEXT, and the exp63 ledger rule is in place.
  - The OC cherry-pick is done.
  - round9 REPORT.md and LESSONS_draft are saved.
  - The round prompt '~330' is fixed.
- **Carried over:**
  - The user message, which now has 3 questions (the wake mechanism is new).
  - round8 REPORT.md.
  - Missed records and prompt l.36.
  - Friend A card.
  - Tick re-checks and poller.
  - "Public = one embryo" caveat.
  - Stale MEMORY copy.
  - I-233.
- **New:**
  - P4c and the gate script before the next P1 check.
  - x138 slug rename and e10_watch snapshots.
  - Finals-input protection.
  - Private-read predictions before 29 Sep 23:59.
  - Six LESSONS_draft errors.
  - Uncommitted poll.log/ledger.md, a duplicate v10 folder and `bash.exe.stackdump`.
  - Dormant rescue in the finals (info).
- **Curator disagreements settled here:**
  - User message: [now] (facts, watch) vs [today] (ideas). INDEX uses [now].
  - Hygiene commit: [now] (watch) vs [today] (ideas, facts). INDEX uses [now, before round 11].
  - Private-read predictions: [today] (watch) vs [before-finals] (ideas, facts). INDEX uses [before-finals] with the hard limit stated.
  - LESSONS fixes: [before-finals] (ideas) vs [info] (facts). INDEX uses [before-finals, by 27 Sep 12:00].

## 11 - 2026-09-26 ~17:50 UTC (curation 11; git HEAD df6996e + untracked `research/wf_ideas_v4/round11/` and `experiments/e10_watch/20260926T1701Z*.txt`)

**Operations:**
- **Commits since curation 10** (`git log --oneline 6064d85..df6996e`):
  - 848e07a: ROUND 10 RECORD, finals-input protection, E10 P4c, post-R8 check times, PRIVATE-READ PREDICTIONS (`CONTEXT.md` l.2230-2300); round8/round10 REPORT.md.
  - a79775f: `tools/e10_snapshot.py` + first snapshots (`experiments/e10_watch/20260926T1620Z.txt`).
  - bea9d99: `tools/e10_port_gate.py` (72 tests, 275 total; x138 + exp56 PASS, amanatar v10 FAIL) and the P4c(3) wording fix (`CONTEXT.md` l.2301-2317).
  - 8a3cf31: USER ANSWER, full research rounds until R8 (`CONTEXT.md` l.2318-2323).
  - 99b127a: round workflow hypothesis lenses + "search IDEAS.md by mechanism" rule (`experiments/workflows/biohub-research-round.js`).
  - a94626a: PRIVATE RANK FORECAST 16:54 (`CONTEXT.md` l.2324-2334).
  - df6996e: USER OK to the successor-scenario PLAN only, 17:00 (`CONTEXT.md` l.2335-2341).
- **Finals still 2/2** by API at 17:09Z (`IDEAS.md` I-258). **E10 not met** at 16:20Z / 17:01Z (`experiments/e10_watch/`; `IDEAS.md` I-026). **LB** #210 of 3,929 at 17:01Z (`FACTS.md` F-LB-02, C-79).
- **Round 11** ran ~17:05-17:31Z (scans: browser, successor, detect, graph, outside, recheck, plancheck); untracked, REPORT.md refused again (text in `research/wf_ideas_v4/round11/report.json` R11-A0; `WATCHLIST.md` I95).

**Ideas** (`IDEAS.md` l.13; `ideas.json` meta.curations[n=11], 42 records; `_curation/11/ideas.json`):
- **Landed:** I-280 P4c, I-281 gate, I-283 predictions, I-284 protection (all RECORDED/BUILT); I-282 partly (snapshots, times; timers and wake still missing); I-232 (rounds 8/10); I-252 (LESSONS fixes); I-265 DECIDED (full rounds).
- **New (I-286..I-294):**
  - In-plan: I-286 E10 v2 PORT-ONLY (>= 0.954, pair {PORT, #37}, <= 2 ports, 3-hourly checks; needs one OK before 27 Sep 12:00); I-290 precedence P6 > f2 > R4.
  - Refuted: I-287 SI as default (opt-in only by ~09:00 27 Sep), I-288 scoreDescending flag, I-289 P2_MIN 0.954, I-291 29 Sep 10:00 last submit, I-292 gate-failing successors (anhadmahajan06 0.946, amanatar v10 ERROR), I-293 raw-maxima recall arm (ceiling +0.0059), I-294 division-wave prior.
- **Status/reason changes:** I-047 refuted by measurement (-0.0129/-0.0273); I-049 (0.149 < q* 0.161); I-079/I-062 q* = 0.161; I-122 (Trackastra has a pretrained 3D 'ctc' model); I-278 (#34 rank ~450-640); I-113/I-261/I-139 notes; I-262 now = HF v3 dry run (R11-A6).
- **Counts c10 -> c11:** 285 -> 294. Refuted 159 -> 166, in-plan 36 -> 38; lb-tested 41, lab-tested 21, deferred 27, open 1 unchanged. Strict orphan I-233. At risk: I-229, I-232, I-262, I-282, I-286, I-290 (I-280, I-281, I-283 left the list).

**Facts and decisions** (`FACTS.md`, `DECISIONS.md`, rows marked [c11]; `_curation/11/facts.json`):
- **New facts:** F-DAT-07 (division timing in train GT), F-LB-11 (private-rank and crowd-model priors, info only), F-MOD-24 (K2 patch applies to successors mechanically), F-MOD-25 (Trackastra pretrained model), F-TRN-37 (round-11 lens ceilings).
- **Contradictions:** new C-79 (team count 3,930/3,929/3,932), C-80 (which rule reads a 0.954-0.955 successor), C-81 (SI vs verbatim port), C-82 (post-R8 check cadence), C-83 (last port submit); resolved C-30, C-72, C-73, C-74, C-77.
- **DECISIONS.md:** gates G36/G37 (§1b l.213-214); [c11] CURRENT finals snapshot (§2 l.289, SI row "not a candidate"); §2f P4c + gate tools in force and the E10 v2 V1-V8 table PROPOSED (l.484); [c11] status on R1-R10 and the finals rule.

**Watchlist** (`WATCHLIST.md`; `_curation/11/watch.json`):
- **Done:** W94 (round-10 record), W95 (P4c), W96 (gate), W97 (snapshots + times, partly), W98 (LESSONS a-g), W99 (predictions), W101 (a) (full rounds), W102 (protection in CONTEXT); amanatar v10 reminder moot (ERROR).
- **New:** W103-W112 (R11-A0..A9) and reminders T36-T39 (23:00 P1 check, 27 Sep 06:00 dry run, ~09:00 SI opt-in, 3-hourly post-R8 checks); insights I96-I106 (I96: nothing flags a 0.954-0.955 successor automatically).
- **Still overdue:** CONTEXT l.22, l.196, out_valid, efpost, 33.1%; round prompt '~4 h headroom'; LESSONS l.7 I69 caveat; friend A card.

**Alerts** (`INDEX.md` TOP ALERTS, 9 after dedup):
- **Resolved since curation 10:** P4c and gate script built before the P1 check; x138 slug + e10_watch snapshots started; finals-input protection and private-read predictions in CONTEXT; LESSONS errors fixed; round8/round10 REPORT.md; the "full vs light rounds" question answered.
- **Carried over:** wake mechanism and user's 29 Sep reminders (asked twice); hygiene commit (now round 11); curator records and friend A card; I69 caveat; stale MEMORY copy; I-233.
- **New:** E10 v2 OK before 27 Sep 12:00; SI claim correction; I96 detection gap; session timers; HF v3 dry run; precedence line; 23:00 P1 check and prompt fix; DaughterNet load outside fail-soft (keep W102); forecast calibration-only.
- **Curator disagreements settled here:** hygiene commit [today] (ideas, facts) vs [now] (watch) -> [now, before round 12]; timers [now] (ideas, watch) vs [today] (facts) -> [now]; SI correction [now] (facts) vs [before-finals] (ideas) -> [now], since it rides in the R11-A9 message.

## 12 - 2026-09-26 ~21:30 UTC (curation 12; git HEAD 9beb9f0 + untracked `research/wf_ideas_v4/round12/`, `research/wf_ideas_v4/reach0955/` committed in da6c699)

**Operations:**
- **Commits since curation 11** (`git log --oneline df6996e..9beb9f0`):
  - 96ccff7: ROUND 11 RECORD, E10 v2 PROPOSED (`CONTEXT.md` l.2342-2361); 13a27a1: SESSION TIMERS (l.2362-2367).
  - 52410cf: COMBO-ORACLE 19:13 (`CONTEXT.md` l.2368-2379); f00b337: user directive "reach 0.955+" (l.2380-2387); 620f718: USER DECISION ladder lift + one public / one private final 20:33 (l.2388-2394); 9ead9df: autonomous night 20:34 (l.2395-2396).
  - cc0d57c: E10 dry run on HF v3, full gate PASS, ~45-60 min trigger-to-ready (l.2397-2406).
  - a6a9ff4: K2 ladder exp70a/d/e/b + finals rule L9, logged before any ladder submit (l.2407-2424).
  - 4d0e967: discussion intel (l.2425-2436); da6c699: intel 0.960-0.966 band, reach0955 files, 20:01Z snapshot (l.2437-2444).
  - 34fdf40 / a9fa8eb: **probe 39 = exp70e** (56589025, 21:15:23Z), **probe 40 = exp70a** (56589065, 21:17:47Z), both PENDING; `tools/runtime_ledger.py` l.76 exp70* -> safetail (+ test) (l.2445-2453).
  - 9beb9f0: reach0955 plan decisions: L9 kept, retrain line started (exp71 run + exp72 probe), exp70g built (l.2454-2474).
- **First LB submits since 00:02:18Z** (probes 39/40); finals still 2/2 by API at 20:04:35Z (`research/wf_ideas_v4/round12/report.json` R12-A2 (3)). LB #217 of 3,935 at 20:01Z (`experiments/e10_watch/20260926T2001Z.txt`). E10 v1 not met at 20:01Z (`IDEAS.md` I-026).
- **Round 12** ran ~20:10-21:01Z (browser, recheck, plancheck, fresh-eyes, post-deadline, private-read, red-team E10); untracked, REPORT.md refused again (text in `round12/report.json` R12-A0; `IDEAS.md` I-232).

**Ideas** (`IDEAS.md` l.13-47; `ideas.json` meta.curations[n=12], 77 records; `_curation/12/ideas.json`):
- **New cluster LADDER** (#2, `IDEAS.md` l.113): I-302 ladder; I-303 exp70a (probe 40), I-305 exp70e (probe 39), I-304 exp70d next, I-306 exp70b (S4 fallback, skeptic NO-GO), I-307 informed combos, I-326 exp70g cap6 (gated by round-13 ins_cap6 arm). Refuted: I-300 (11:00Z last submit, R8), I-308 tighter insertion, I-309 --set SECONDARY_*/DET_THRESHOLD, I-310 threshold neighbours. Open: I-311 Justin PP-only, I-312 "LB tracks node count".
- **New FINALS rows:** I-295 one public + one private; I-296 L9 (kept); I-297 insertion-hedge table and I-301 rule reconciliation (not in CONTEXT); I-298 {V*, #37} refuted; I-299 E10 insertion-family rows (need OK); I-315 07:30Z morning message.
- **New elsewhere:** I-313 API budget, I-314 E10 procedure hardening, I-316 transfer table, I-317 late-sub bed, I-318 D0, I-319 G0 gate, I-320 combo oracle (refuted: +0.0143 oracle only), I-321 daughter localisation (moot), I-322 test cleanup, I-323 Corwin secondary (EV <= 0), I-324 coord-inject (LOC), I-325 Bio-Pirates learned ends (not usable).
- **Status/reason changes:** I-119 retrain STARTED on the session's reading (at risk); I-286 RECORDED as PROPOSED; I-262 dry run DONE; I-290 recorded; I-259 applied; I-034 reason inverted -> deferred post-deadline; I-147/I-148 negative on x138 (I-148 closed); I-033 reason fixed; I-222 bound ~+0.005; post-deadline ranks on I-113, I-242, I-079, I-261, I-029, I-110, I-122, I-285, I-208.
- **Counts c11 -> c12:** 294 -> 326. Refuted 166 -> 172, in-plan 38 -> 56, deferred 27 -> 31, open 1 -> 5; lb-tested 41, lab-tested 21 unchanged. Strict orphan I-233. At risk: I-119, I-229, I-232, I-252, I-257, I-282, I-283, I-286, I-297, I-299, I-301, I-306, I-314, I-315, I-323, I-324, I-326 (I-262, I-290 left the list).

**Facts and decisions** (`FACTS.md`, `DECISIONS.md`, rows marked [c12]; `_curation/12/facts.json`):
- **New facts:** F-DAT-16, F-LB-12/13/14 (discussion + band intel), F-RUN-24/25, F-RUL-15/16/17 (API 429s, x138 config guard), F-MOD-26..29, F-TRN-38..41 (combo oracle, 0/5 model-swap record). Curation-11 duplicate F-DAT-07 renumbered F-DAT-15.
- **Contradictions:** new C-84..C-95 (R7 vs R9 lift, private-aimed slot, L9 11:00Z vs R8 02:00Z, ladder odds, y3uanm source, node-count claim, poll gap, Justin inference, exp70 name clash, FT timing vs R8, UTC+3 labelled Z, exp70b blind slot) (`FACTS.md` l.359-370); resolved C-78, C-80, C-82, C-83.
- **DECISIONS.md:** §1 planned ladder table; gates G38-G40 (§1b l.243-245); §2 c12 finals snapshot (l.330); §2f c12 paragraph; **new §2h ladder + L9** (l.589); §3 c12 status incl. an L9 row.

**Watchlist** (`WATCHLIST.md`; `_curation/12/watch.json`):
- **Done:** W110 (curation 11), W111 (20:01Z P1 check + prompt edit 13a27a1), round-11 record, E10 v2 text, timers, dry run; W112 superseded by W120.
- **New:** W113-W129 (R12-A0..A10, ladder, runtime ledger, S4, retrain, reach0955 commit), reminders T40-T49 (23:50Z hard stop, round 13, 02:00Z P1, ladder reads 04-08Z, 07:30Z push, L5 combos, 28 Sep 12:00 consolidation, 29 Sep ~19:00 L9 read, 23:00 pre-reg), insights I107-I124.
- **Still overdue:** CONTEXT l.22, out_valid, efpost, 33.1%; LESSONS l.7; friend A card; round prompt l.37/l.40.

**Alerts** (`INDEX.md` TOP ALERTS, 10 after dedup):
- **Resolved since curation 11:** E10 v2 text in CONTEXT (as PROPOSED); session timers created; HF v3 dry run done; 20:01Z P1 check done; round-11 record committed; SI correction moot under the new strategy; runtime ledger exp70* -> safetail (34fdf40; watch alert W127 was written at 4d0e967, before the fix).
- **Carried over:** E10 v2 OK before 27 Sep 12:00 (now in the 07:30Z message); hygiene commit (now round 12 + `_pytest_oc_k2`); stale RESUME POINT / MEMORY; LESSONS + curator records; I-233.
- **New:** R12-A3 reconciliation before exp70d (probes 39/40 already out); retrain consent; exp72 pair row; S4 exp70g vs exp70b and L9 class; API budget / one poller / x138 config guard; K2 dummy node reference 122,252 vs 121,252; private-read pre-reg v2; I-311/I-312/I-323/I-324 owners; y3uanm not evidence; UTC+3 labelled Z.
- **Curator disagreements settled here:** reconciliation [deadline, now] (ideas, watch) vs [contradiction, now] (facts) -> one [now] alert; retrain [risk, now] (ideas) vs [risk, today] (facts, watch) -> [now], since prep is already running; S4 [now] (ideas) vs [today] (watch) -> [now], due 00:05Z; hygiene [today] (ideas, facts) vs [now] (watch) -> [today], after the reconciliation.
