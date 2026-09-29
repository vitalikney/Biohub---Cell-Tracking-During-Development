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

## 13 - 2026-09-27 ~01:45 UTC (curation 13; git HEAD 5e57346; round 13 committed in 3d48d35)

**Operations:**
- **Commits since curation 12** (`git log --oneline 9beb9f0..5e57346`):
  - 0bc0da4: ROUND 12 RECORD + RULE RECONCILIATION (insertion hedge, R8 02:00Z cap) (`CONTEXT.md` l.2475-2529).
  - ea5637e: builder `--patch secswap` (finals + ladder rebuild byte-identical).
  - d3a2c0d: timers 2f0d1fa1 / c7cd2e6b / bb224de9 (l.2530).
  - ed0c638: **probe 41 = exp70d** (56589423, 21:38:33Z) + node-count correction to K2 121,252 (l.2534-2538).
  - 9014772: exp71 READY, push BLOCKED pending the user's yes (l.2539-2544).
  - 86e96f2: CAP-6 lab arm -0.00057, exp70g dropped (l.2545-2549).
  - bf07763: E10 hardening, PRIVATE-READ v2, RESUME POINT 22:46Z (l.2550-2622).
  - fc2536c: **probe 42 = exp70b** (56592350, 00:05:50Z) (l.2623-2625).
  - 3d48d35: ROUND 13 RECORD, LADDER PRE-SCORE REGISTRATION (L5v2, attribution, A-only extension), EXP71/EXP72 GOVERNANCE (l.2626-2746), plus `research/wf_ideas_v4/round13/` incl. REPORT.md and `experiments/e10_watch/20260926T2246Z.txt`.
  - 5e57346: TIMERS 65b1b746 (07:30Z push) and 2e87e414 (E10 P1, defers in the 04:10-06:45Z quiet window) (l.2747-2749).
- **LB:** 4 ladder probes out, all PENDING at 01:39:32Z (`experiments/lb_poll/poll.log`); finals unchanged, SELECTED last read 20:04:35Z. E10 P1 at 22:46Z not met. We are #229 of 3,935 (`CONTEXT.md` l.2626-2641).
- **Round 13** ran ~22:45Z-01:28Z (node count, division PP, gated fusion, ladder next, recheck, plancheck, browser). Nothing reaches R8 (`CONTEXT.md` l.2652-2660).

**Ideas** (`IDEAS.md` l.13-47; `ideas.json` meta.curations[n=13], 65 records; `_curation/13/ideas.json`):
- **New (I-327..I-335):**
  - In-plan: I-327 attribution protocol + read-only watcher (not written); I-328 A-only 0.954-UP extension {exp70a, #38}; I-330 G2 held-out finals veto for exp72.
  - Refuted: I-329 PC13-06 insertion-hole rule (the gate is per clip).
  - Deferred-after-deadline: I-331 start-leaf prune; I-332 component prune; I-333 divergence-2.5 rung; I-334 density-aware tau; I-335 detection band gate.
- **Status changes:**
  - Ladder: I-304 exp70d and I-306 exp70b submitted; I-326 exp70g refuted (-0.00057); I-307 rewritten as L5v2; I-302 gets the stop rule and slot priority.
  - Closed or refuted: I-311 Justin PP-only closed for the window; I-126 refuted (already in x138); I-222 max-union guard refuted; I-309 edge-gate knobs are no-ops.
  - I-312 measured; it closes when probe 40 reads.
  - Recorded: I-297 / I-301 / I-300 at 21:31Z; I-314, I-283, I-316, I-317, I-257, I-282, I-232.
  - I-119: exp71 push blocked, "R8 lifted" suspended, exp72 class C unless Q3 = yes.
  - Other updates: I-105/I-108 node-attribution fix; I-051 x138 division knobs; I-304/I-074 44b6 reads in-sample.
  - I-323 / I-324 moved to deferred via the general R8 sentence, not closed by name.
- **Counts c12 -> c13:** 326 -> 335:
  - refuted 172 -> 176
  - deferred 31 -> 37
  - in-plan 56 -> 59
  - open 5 -> 1
  - lb-tested 41 and lab-tested 21 unchanged
- **Orphans:** strict orphan I-233. At risk: I-119, I-229, I-252, I-286, I-299, I-315, I-327. Dropped off the at-risk list: I-232, I-257, I-282, I-283, I-297, I-301, I-306, I-314, I-326; I-323/I-324 moved to deferred.

**Facts and decisions** (`FACTS.md`, `DECISIONS.md`, rows marked [c13]; `_curation/13/facts.json`):
- **New facts:**
  - F-LB-15: the LB row counts only scored submissions (the freshness key).
  - F-RUN-26: ladder dummies, corrected node counts, W6 audit.
  - F-MOD-30: gated fusion is already in x138.
  - F-TRN-42: cap-6 lab arm.
  - F-TRN-43: round-13 node/division lab.
  - [c13] notes on 31 rows. F-TRN-41 now carries the +0.62% correction (the '+3.9%' included the primary's +3.2%; the ideas-curator alert on it is resolved).
- **Contradictions:** new C-96..C-103 (dummy node counts, display needed to move finals, exp72 node gate, when 39-42 score, ...). Resolved: C-84, C-85, C-86, C-95 (by 21:31/21:56 entries). C-93 superseded by R13-A3.
- **DECISIONS.md:**
  - §1: rows P39-P42 + planned combo table (exp70c/h/f).
  - §1b: gates G41-G43.
  - §2: [c13] finals snapshot (l.374).
  - §2f: P1 22:46Z not met.
  - §2h: L5v2, attribution, A-only extension, stop/slot, quiet-window rows.
  - §3: R4/R5/R7/R8/R9/§f/L9 statuses + 3 rule rows.

**Watchlist** (`WATCHLIST.md`; `_curation/13/watch.json`):
- **Done:** W113-W117, W119, W121, W122, W124, W125, W127, W129. After the watch pass also: W132/W133/W135/W136/W139 (3d48d35, 5e57346). W128 is now blocked.
- **New:** W132-W142 (R13-A0..A9, W142 exp70g NEVER_SUBMIT); reminders T51-T61; insights I125-I135.
- **Still overdue:** W57 family (CONTEXT l.22, out_valid, efpost, 33.1%); W71/W118/W140 round prompt l.38/l.40 + quiet window; W98 LESSONS l.7.

**Alerts** (`INDEX.md` TOP ALERTS, 10 after dedup):
- **Resolved since curation 12:** rule reconciliation logged (21:31Z); round-12 record + REPORT.md; RESUME POINT + MEMORY (22:46Z); timers replaced; K2 dummy node count corrected (121,252); S4 decided (exp70b; exp70g dropped); private-read v2; retrain consent (push blocked, governance logged); exp72 pair row (class C unless Q3); pre-score registration and round-13 commit (3d48d35); morning timer and quiet-window deferral (5e57346).
- **Carried over:** E10 v2 OK before 12:00Z (07:30Z push); I-233; W57 / LESSONS l.7 hygiene; stale round prompt; stale MEMORY index line.
- **New:** ladder watcher by 04:10Z; API quiet window; SELECTED re-read + I-312 closure at D1; RESULTS rows 39-42; RESUME POINT partly stale; exp70g NEVER_SUBMIT; G2 cost if Q3 = yes; re-tick; closures of I-323/I-324 by name at R8; 0.953-block order caveat.
- **Curator disagreements settled here:**
  - Watcher: [now] by all three.
  - Pre-score registration and commit: [now] (watch) -> resolved by 3d48d35 before this index.
  - exp72 / G2: [today] (ideas, watch) vs [info] (facts) -> [today], since a yes is needed by ~09:00Z.
  - Timer 2f0d1fa1 in the quiet window: [today] (watch) -> resolved by 2e87e414.
  - SELECTED re-read: [today] (ideas, facts) -> [today], at D1.

## 14 - 2026-09-27 ~02:25 UTC (curation 14; git HEAD f24ff72 + untracked `research/wf_ideas_v4/round14/` and `experiments/e10_watch/20260927T0147Z.txt`)

**Operations:**
- **Commits since curation 13** (`git log --oneline 5e57346..f24ff72`): f2f843e curation 13 + round 13 files; f24ff72 read-only ladder watcher `experiments/lb_poll/ladder_watch.py` (35 tests, dry run OK, pushed 01:54:14Z) with poller-phase and restart fixes.
- **CONTEXT.md and RESULTS.md are unchanged since 5e57346** (last entry TIMERS UPDATED l.2747-2749). Everything new comes from round 14 (`research/wf_ideas_v4/round14/report.json`, 02:11:57Z, R14-A0..A9; REPORT.md not saved), the 01:47Z E10 snapshot and the polls.
- **LB:** probes 39-42 all PENDING at 02:19:40Z (`experiments/lb_poll/poll.log`); finals unchanged (TICKED 2/2, SELECTED last read 20:04:35Z). Rank #242 of 3,937 at 01:47:50Z (was #229); 226 teams >= 0.955 (`experiments/e10_watch/20260927T0147Z.txt`; `FACTS.md` F-LB-15 [c14]).
- **Watcher not launched:** `experiments/lb_poll/ladder_watch/` and `run_ladder_watch.sh` absent at 02:24Z (`FACTS.md` F-RUN-27).

**Ideas** (`IDEAS.md` CHANGES (14) l.61; `ideas.json` meta.curations[n=14], 30 records; `_curation/14/ideas.json`):
- **New (I-336..I-340):** I-336 HINDSIGHT GUARD (in-plan, at risk; R14-A8); I-337 route-robustness read (refuted -> descriptive B arm); I-338 rule-register template (in-plan; R14L-9); I-339 / I-340 rejected watcher variants PC14-05 / PC14-06 (refuted).
- **Status changes:** I-063 DaughterNet v2 refuted -> deferred-after-deadline (gap at noise level; R14-RC-B); I-106 exp23 secondary with the public primary refuted -> open-untested (never run; exp72 is its class; R14-RC-A).
- **Updated rows:** I-302/I-307/I-328/I-229 (READ SHEET v1, literal readings); I-327 (restart loop, S0 = 0147Z, hard cap 11:30Z, liveness); I-258 (SELECTED after 06:45Z); I-315 (push variants P-A/P-B/P-C + corrected brief); I-297/I-062/I-069/I-283 (insertion '+0.006' in-sample, OOF +0.0019, C2 P(<0) 0.10-0.20); I-119/I-317 (0/4 FT swaps; R14L-8); I-252 (R14L-1..5); intel I-026/I-025/I-282/I-094; ops I-232/I-257/I-265.
- **Counts c13 -> c14:** 335 -> 340; refuted 176 -> 177, deferred 37 -> 38, in-plan 59 -> 61, open 1 -> 2; lb-tested 41 and lab-tested 21 unchanged. Orphans: strict I-233; at risk I-119, I-229, I-252, I-286, I-299, I-315, I-327, I-336.

**Facts and decisions** (`FACTS.md`, `DECISIONS.md`, rows marked [c14]; `_curation/14/facts.json`):
- **New facts:** F-RUN-27 (watcher: 35 tests, not fail-soft, NOT running; default HARD_CAP 09:40Z at `ladder_watch.py` l.66); F-RUL-18 (discussion 743765: 'a submit must finish before the deadline', participant only); F-TRN-44 (insertion prior: +0.006 in-sample vs +0.0019 OOF; I-063 unresolved). [c14] notes on F-LB-01..15, F-RUN-26 (latency scaling, L_hi clocks), F-RUL-12, F-MOD-28 (combo shas re-verified), F-TRN-41 (0/4), C-75, C-103.
- **Contradictions:** new C-104..C-110 (`FACTS.md` l.413-419): S0 snapshot never existed; +0.006 vs +0.0019; SELECTED timing (D1 -> after 06:45Z); 0/5 vs 0/4; hard cap 09:40Z vs exp70b; D1-1 priors; I-063/I-106 status.
- **DECISIONS.md:** P39-P42 [c14] (latency bounds, ETAs, 8.0 h clocks e 05:15:23Z, a 05:17:47Z, d 05:38:33Z, b 08:05:50Z); §2 [c14] paragraph + snapshot (l.400); §2f 01:47Z P1 not met (l.637); §2h four rows (S0 + launch, pre-score notes, READ SHEET v1, liveness; l.696-699); §3 [c14] notes on R5/R8/R9/L9 + two rule rows (round-14 pre-score notes, hindsight guard).

**Watchlist** (`WATCHLIST.md`; `_curation/14/watch.json`):
- **Done:** W132, W133, W135, W137, W139. Partly done: W134 (code done, launch pending), W136 (timer 65b1b746), W140 (timer 2e87e414 defers in the quiet window).
- **New:** W143-W150 (R14-A0..A6; W150 round-prompt defect), reminders T62-T67, insights I136-I148. W71 / W118 merged into W150; W138 / W123 into W147.
- **Still overdue:** W57 family (CONTEXT l.22, out_valid, efpost, 33.1%); W98 LESSONS l.7; W142 exp70g NEVER_SUBMIT.md; W126 RESULTS rows 39-42 (await scores).

**Alerts** (`INDEX.md` TOP ALERTS, 9 after dedup):
- **Resolved since curation 13:** watcher code written and pushed (f24ff72); curation-13 files committed (f2f843e); pre-score registration pushed before any score (3d48d35); timers with quiet-window deferral (5e57346).
- **Carried over:** watcher launch by 04:10Z (now: restart loop, S0 = 0147Z, cap 11:30Z); 07:30Z push (E10 v2, Q1-Q3, R8 cap); re-tick; exp70g NEVER_SUBMIT; W57 / LESSONS l.7; I-233; stale MEMORY line (C-75).
- **New:** R14-A2 pre-score notes committed and pushed by 04:25Z (+ REPORT.md, round14/, 0147Z snapshot); round-15 browser scan would call the API in the quiet window (W150); liveness checks without an owner (W145); READ SHEET v1 at D1; SELECTED read moved to ~07:30Z; corrected brief lines (in-sample +0.006, 0/4); ROUND 14 RECORD before 07:30Z; HINDSIGHT GUARD before 29 Sep 23:00Z; I-063 / I-106 status corrections; timers session-only.
- **Curator disagreements settled here:** SELECTED read: c13 'at D1' vs c14 'after 06:45Z' -> after 06:45Z (R14 plan_issues (4)). I-063/I-106: facts curator 'queued, info' vs ideas curator 'applied' -> applied in `IDEAS.md`, CONTEXT wording via R14-A6/A7. W150 raised only by the watch curator -> kept as [now].

## 15 - 2026-09-27 ~06:15 UTC (curation 15; git HEAD da9766e = origin/main + untracked `research/wf_ideas_v4/round15/`, `experiments/e10_watch/20260927T0531Z.txt`, `experiments/ext_optimized-biohub-max-score/v6_2026-09-27/`)

**Operations:**
- **Commits since curation 14** (`git log --oneline f24ff72..da9766e`): 8155321 R14 pre-score notes + READ SHEET v1 + `run_ladder_watch.sh` + round14/REPORT.md (pushed 02:29:01Z, before any score); a129e5f watch timers; 862869f LADDER READ D1; 477a3bb exp70j/exp70k built; da9766e probes 43/44 submitted.
- **CONTEXT.md:** six new entries l.2750-2813 (R14 PRE-SCORE NOTES, READ SHEET v1, WATCH TIMERS, LADDER READ D1 04:58, POST-D1 RUNGS 04:59, SUBMIT 43/44 05:28); `## 9. Literature` now l.2814. `experiments/RESULTS.md` unchanged (last row P38, l.71).
- **LB:** P39 exp70e 0.949, P40 exp70a 0.954 (no UP), P41 exp70d 0.949; P42 exp70b, P43 exp70j (DC 0.20, 56598763), P44 exp70k (DC 0.225, 56598765) PENDING at 06:11:39Z (`experiments/lb_poll/ladder_watch/calls.jsonl`). Rank #256 of 3,938 at 05:32Z; 239 teams >= 0.955 (`experiments/e10_watch/20260927T0531Z.txt`). Finals unchanged (TICKED #37 + #38; D1 row D1-3, `CONTEXT.md` l.2789-2799).
- **Watcher** ran from 03:35Z (PID 10088), 3 fresh events, UP test FAIL at all three (`CONTEXT.md` l.2791-2793).
- **Round 15** judged at 06:00Z (`research/wf_ideas_v4/round15/report.json` R15-A0..A8); none of its actions is done yet.

**Ideas** (`IDEAS.md` CHANGES (15) l.68; `ideas.json` meta.curations[n=15], 55 records; `_curation/15/ideas.json`):
- **New (I-341..I-353):** I-341 exp70j / I-342 exp70k (in-plan, submitted); I-344 class-C finals table and I-345 deviation record + FREEZE (in-plan, at risk); I-346 NARROW/BROAD note, I-347 event-unit scale, I-348 per-embryo DC study (post-deadline); I-352 / I-353 amanatar V6 blend and lookahead (post-deadline); rejected I-343 exp70m, I-349 further DC variants, I-350 twin + DC 0.20, I-351 exp70d as private-aimed final.
- **Status changes:** lb-tested I-303 (P40), I-304 (P41), I-305 (P39), I-312 (closed by exposure), I-074 (dc0.30 = -0.005 public); refuted I-307 (BASE none) and I-328 (A-only did not fire); I-327 no longer at risk.
- **Counts c14 -> c15:** 340 -> 353; lb-tested 41 -> 46, refuted 177 -> 182, deferred 38 -> 41; lab-tested 21, in-plan 61, open 2 unchanged. Orphans: strict I-233; at risk I-119, I-229, I-252, I-286, I-299, I-315, I-336, I-344, I-345 (I-327 dropped off).

**Facts and decisions** (`FACTS.md`, `DECISIONS.md`, rows marked [c15]; `_curation/15/facts.json`):
- **New facts:** F-TRN-45 (DC 0.25 -> 0.30 = -0.005 public vs lab +0.0013; lab sign wrong); F-TRN-46 (lp30 on K2 = 0.954, no UP); F-MOD-31 (DeepCenter threshold semantics); F-RUN-28 (43/44 dummy re-verification). [c15] notes on ~20 rows (F-LB, F-RUN-26/27, F-RUL-12/18, F-MOD-28, F-TRN-43, C-75, C-101).
- **Contradictions:** new C-111..C-120 (`FACTS.md` l.438-447): 43/44 breach R13-A1/L9 (C-111); 'watcher paused' false (C-112); 04:59 prior inflated (C-113); V6 R8 reason wrong (C-114); probe.json 'above exp56 adopt' (C-115); exp70d COMPLETE time (C-116); dc0.30 sign-flip mechanism (C-117); RESULTS.md stale (C-118); 'division knobs invisible on public' (C-119); class-C pair shape (C-120). Resolved: C-104, C-106, C-108.
- **DECISIONS.md:** §1 P39-P42 [c15] + new P43/P44 (l.139-140); §2 [c15] paragraph l.412 + snapshot l.421; §2f E10 05:31Z l.665; §2h post-D1 rows (l.728); §3 R1-R10/L9 [c15] notes + one rule row.

**Watchlist** (`WATCHLIST.md`; `_curation/15/watch.json`):
- **Done:** W134 (watcher launched), W143/W144 (pre-score notes + REPORT.md, 8155321), W137 absorbed into W153; W141 D1 half done.
- **New:** W151-W157 (R15-A1 entry, R15-A0 REPORT.md, SELECTED read, class-C letter, ROUND 15 RECORD, 43/44 read, 12:00Z lapse line); reminders T68-T74; insights I149-I159.
- **Still overdue:** W126 RESULTS rows 39-41; W142 NEVER_SUBMIT (now exp70g/j/k); W146 ROUND 14 RECORD; W57 family; W98 LESSONS l.7; W150 round prompt l.37/l.38.

**Alerts** (`INDEX.md` TOP ALERTS, 9 after dedup):
- **Resolved since curation 14:** watcher launch (03:35Z); R14-A2 pre-score notes pushed before any score (8155321); timers logged (a129e5f); D1 read applied mechanically (862869f); SELECTED timing settled at 07:30Z; liveness timers set (no result logged yet).
- **Materialised:** the W150 quiet-window API call (round-15 browser E10 snapshot 05:31Z; no 429, no harm).
- **Carried over:** 07:30Z push (now the R15-A2 form); exp70g NEVER_SUBMIT (extended to j/k); ROUND 14 RECORD; round prompt l.37; re-tick; hindsight guard; W57 / LESSONS l.7; I-233; stale MEMORY line (C-75).
- **New:** R15-A1 pre-score entry for 43/44 (hard 11:45Z); breach disclosure + FREEZE; E10 pair rows missing from the brief (I-299); D2 read of P42; RESULTS rows 39-44; 12:00Z lapse line with I-323/I-324 closures; public DC chase risk; I149/I150 for the L9 read; session timers 5b23a3ed/54a8f20d still listed.
- **Curator disagreements settled here:** 43/44 breach: [now] (facts, watch) vs [today] (ideas) -> [now], because the disclosure goes into the 07:30Z brief. Risk of the public DC chase: [info] (ideas) vs [today] (facts) -> [info] as a standing caution, with the read itself under alert 4/R15-A5 timing. R15-A1: [now] by all three.

## 16 - 2026-09-27 ~09:15 UTC (curation 16; git HEAD 0bd1408 = origin/main + untracked `research/wf_ideas_v4/round16/`, `experiments/e10_watch/20260927T0831Z.txt`, `experiments/ext_optimized-biohub-max-score/v6_2026-09-27/`)

**Operations:**
- **Commits since curation 15** (`git log --oneline da9766e..0bd1408`): 4161226 probes 43/44 PRE-SCORE ENTRY + `round15/REPORT.md` (06:19Z, before any 43/44 score); 0bd1408 LADDER READ D2 (07:41Z).
- **CONTEXT.md:** two new entries, l.2814-2871 (deviation record, FREEZE, descriptive read, CLASS-C FINALS TABLE, priors, NARROW/BROAD note, L6/L7 + DC-DOSE, watcher correction, main-session note) and l.2872-2879 (D2); `## 9. Literature` is now at l.2880. `experiments/RESULTS.md` is unchanged (last row P38, l.71).
- **LB:** P42 exp70b (K2 + forkmid 4.5) = 0.954 with an attributable UP (U4, fm45 POS; L (7.41, 7.58] h). It is not V*, so the pair {#37 56563521, #38 56563534} stays and API SELECTED was 2/2 at 07:41:28Z (`CONTEXT.md` l.2872-2879). P43/P44 were PENDING at the 09:10:50Z header (`experiments/lb_poll/poll.log` l.13013). Rank #255 of 3,943, 8th of 113 in the 0.954 block (`experiments/e10_watch/20260927T0831Z.txt` l.911).
- **Watcher** stopped at 07:37:07Z (64 calls, 0 x 429). The morning brief went out in chat at ~07:45Z; its push status is not logged (`CONTEXT.md` l.2876-2879).
- **Round 16** judged at 08:57Z (`research/wf_ideas_v4/round16/report.json` R16-A0..A9). None of its actions was done by ~09:15Z.

**Ideas** (`IDEAS.md` CHANGES (16) l.71; `ideas.json` meta.curations[n=16], 49 records; `_curation/16/ideas.json`):
- **New (I-354..I-359):** I-354 exp70b as the public-aimed final (in-plan, user letter only); I-355 answer-parsing rule (in-plan, part of R16-A1); I-356 unified slot table, I-357 N954 deadline observable and I-358 the mtoshidesu DC 0.20 kernel (all refuted); I-359 post-deadline removal-gate method (deferred).
- **Status changes:**
  - lb-tested: I-306 (P42 0.954) and I-071 forkmid (refuted -> lb-tested; its lab closure for private stands).
  - Now logged in CONTEXT: I-345 FREEZE / deviation record and I-344 class-C table.
  - Folded into existing rows: I-303 (exp70a NEU was structural), I-073 (forkblob on the ins35 bed +0.00019, closure upheld), I-094/I-297 (forecast premise corrected), I-026/I-286 (E10 cadence, v2 lapse).
- **Counts c15 -> c16:** 353 -> 359. lb-tested 46 -> 48, refuted 182 -> 184, deferred 41 -> 42, in-plan 61 -> 62; lab-tested 21 and open 2 unchanged. The strict orphan is still I-233; I-336 is still not in CONTEXT.

**Facts and decisions** (`FACTS.md`, `DECISIONS.md`, rows marked [c16]; `_curation/16/facts.json`):
- **New facts:**
  - F-RUN-29: 43/44 read timing, with 9.0 h clocks at 14:28:13Z / 14:28:22Z.
  - F-TRN-47: fm45 on K2 = 0.954 with an attributable UP.
  - [c16] notes on F-LB-01/02/03/04/10/11/15, F-RUN-03/27, F-RUL-12, F-MOD-27 and F-TRN-12/46.
- **Contradictions:**
  - New C-121..C-131 (`FACTS.md` l.464-474), including: the class-C (b) partner and exp70b composition (C-121); public block ranks used for private rank (C-124, C-127); exp70a NEU structural (C-125); the manufactured 09:00Z exp72 edge (C-128); exp70b vs #37 (C-129); 43/44 timing (C-131).
  - Resolved in CONTEXT: C-106, C-111, C-112, C-113.
  - Updated: C-26 (stale RESUME POINT), C-114, C-118, C-120.
- **DECISIONS.md:**
  - §1: P42 scored; P43/P44 updated (l.152-154).
  - §2: [c16] paragraph l.435 and a new snapshot at l.445 (replaces c15).
  - §2f: E10 08:31Z at l.695.
  - §2h: D2 applied, plus three round-16 rows (l.761-763).
  - §3: R1-R10 rows updated, plus proposed rows R16-A1 and R16-A3.

**Watchlist** (`WATCHLIST.md`; `_curation/16/watch.json`):
- **Done:** W151 (R15-A1, 4161226), W152 (round15/REPORT.md), W141 D2, W153 (SELECTED 07:41:28Z), W136 (brief in chat; push status still open), W145 (watcher stopped). W149 E10 P1 at 08:31Z was not met and continues as W164. W157 became W161.
- **New:** W158-W167 (= R16-A0..A9 plus hygiene), reminders T77-T86, insights I161-I171.
- **Still overdue:** W126 (RESULTS rows 39-42), W142 (NEVER_SUBMIT for exp70g/j/k), W146/W155 (ROUND 14/15 RECORDs), W57 family, W98 (LESSONS l.7), W150 (round prompt l.35-38).

**Alerts** (`INDEX.md` TOP ALERTS, 8 after dedup):
- **Resolved since curation 15:**
  - R15-A1 pre-score entry logged and pushed before any 43/44 score.
  - Breach disclosed (CONTEXT (9) and the brief).
  - D2 read applied mechanically.
  - 07:30Z SELECTED read (done at 07:41Z).
  - Round-16 prompt risk moot (the watcher had stopped).
- **Moot:** the 09:00Z exp71/exp72 yes edge (C-128).
- **Carried over:** ROUND 14/15 RECORDs, RESULTS rows, NEVER_SUBMIT markers, the 12:00Z lapse line (now R16-A3), the round prompt, the HINDSIGHT GUARD, I-233, and the stale RESUME POINT / MEMORY line (C-26).
- **New:**
  - R16-A1 addendum (practical edge 11:45Z).
  - R16-A2 single message by 11:00Z, carrying the exp70b and refusal-(7) facts.
  - 43/44 read triggers (14:28:22Z / 14:40Z).
  - exp70b-as-final letter (I-354).
  - fb_ins35.py only exists in a scratchpad.
  - Corrected readings C-124/C-125/C-127/C-128.
- **Curator disagreements settled here:**
  - exp70b risk: [info] (facts) vs [before-finals] (ideas) -> [before-finals], because the letter has a practical expiry of 29 Sep ~18:00Z.
  - RESULTS rows: [before-finals] (facts) vs [today] (ideas, watch) -> [today], folded into the R16-A5 commit.
  - R16-A2: [now] (facts, watch); ideas nested it inside its R16-A1 alert -> a separate [now] alert.

## 17 - 2026-09-27 ~12:05 UTC (curation 17; git HEAD a6ffbc9 = origin/main + untracked `research/wf_ideas_v4/round17/`, `research/wf_ideas_v4/bigger_levers/`, `research/wf_ideas_v4/e10v3/`, `experiments/exp73a..exp73v/`, `experiments/exp74_k2_secw_corwin/`, `experiments/ds_secw_corwin_v1/`, `experiments/e10_watch/20260927T1101Z.txt`)

**Operations:**
- **Commits since curation 16** (`git log --oneline 0bd1408..a6ffbc9`):
  - 289bd52 R16-A1 read addendum + round-16 report; 06f1a02 R16-A2 message + forecast.
  - 61e0737 USER E10 v3; 659cef3 USER class-C letter (b), pre-score; 5bce47f USER Q1/Q2 yes; d1ccc85 exp71 pushed.
  - 9cdc047 aggressive mode, P45 exp70g submitted, exp70q/exp70r built.
  - a6ffbc9 12:00 UTC line, which also commits `experiments/lb_poll/e10_watch_loop.py` and `run_e10_watch_loop.sh`.
- **CONTEXT.md:** nine new entries at l.2880-2954; `## 9. Literature` is now at l.2955. `experiments/RESULTS.md` is unchanged (last row P38).
- **User decisions 11:08-11:16Z** (`CONTEXT.md` l.2917-2951):
  - E10 v3: trigger = a public notebook >= 0.955; (A) verbatim copy, (B) copy + SI, (C) port into K2; autonomous submit.
  - Class-C letter (b), pre-registered at 11:09:39Z with both refs PENDING: V*_C -> {V*_C, #37}.
  - Q1/Q2 yes: exp71 pushed 11:11:50Z; exp72 set for 28 Sep 00:05Z; Q3 is open.
  - FREEZE lifted 11:14Z.
  - Aggressive mode 11:16Z: P45 = exp70g (K2 + cap 6, 56606948) submitted 11:15:12Z. The last 27 Sep slot goes to exp70r if P43 >= 0.955 by ~13:00Z, else exp70q.
- **LB:**
  - Rank #260 of 3,945, 6th of 115 in the 0.954 block (`experiments/e10_watch/20260927T1101Z.txt` l.930).
  - E10 P1 was not met at 11:01Z. amanatar V6 now shows 0.901 (`FACTS.md` F-LB-04 [c17]).
  - P43/P44/P45 were PENDING at the 12:01:34Z header (`experiments/lb_poll/poll.log` l.14050). Finals are unchanged: #37 + #38.
- **Round 17** was judged at 11:28-11:40Z (`research/wf_ideas_v4/round17/report.json` R17-A0..A11). Only R17-A1 is (partly) done: a6ffbc9 at `CONTEXT.md` l.2952-2954.
- **Built but untracked:**
  - 20 exp73 division rungs (`research/wf_ideas_v4/bigger_levers/prep_div_combos.json`).
  - exp74 K2 + Corwin's secondary (`prep_corwin_secondary.json`; the dataset upload is not done).
  - exp75 coord-inject prep (`prep_coord_refiner.notes.md`, `tools/coordinject_patch.py`).
  - E10 v3 tooling (`research/wf_ideas_v4/e10v3/`). `tools/e10_snapshot.py` (`take_snapshot`) is still uncommitted, and the loop is not running.

**Ideas** (`IDEAS.md` CHANGES (17) l.80-89; `ideas.json` meta.curations[n=17], 74 records; `_curation/17/ideas.json`):
- **New (I-360..I-372):**
  - Rungs: I-360 exp70n (thr 0.3), I-361 exp70q, I-362 exp70r, I-363 exp73 ladder.
  - I-364 E10 v3.
  - Round 17: I-365 pre-score card, I-366 slot-collision default (needs the user's OK), I-367 override-budget lesson, I-368 post-deadline division-transfer bed.
  - Rejected: I-369..I-372 (2-3x OOF bar; private_read.py before the deadline; 'FINALS FROZEN' at 20:05Z; 'slots = E10 v1 insurance only').
- **Status changes:**
  - E10 v2 I-286 -> refuted/superseded.
  - Revived to in-plan: SI I-287, {X, #37} pair I-298, P45 exp70g I-326.
  - Deferred -> in-plan: exp74 Corwin's secondary I-323, exp75 coord-inject I-324.
  - FREEZE I-345: in-plan -> refuted/closed.
  - Updated: I-344 (letter (b) logged), I-119/I-330 (Q1/Q2 yes, Q3 open), I-354 (still open; the letter did not name exp70b).
- **Counts c16 -> c17:** 359 -> 372. in-plan 62 -> 73, refuted 184 -> 186; lb-tested 48, lab-tested 21, deferred 42 and open 2 are unchanged. The strict orphan is still I-233.

**Facts and decisions** (`FACTS.md`, `DECISIONS.md`, rows marked [c17]; `_curation/17/facts.json`):
- **New facts:**
  - F-RUN-30: GPU lanes and the exp71 run.
  - F-MOD-32: Corwin's CC0 secondary.
  - F-MOD-33: insertion-cap anatomy. The cap binds on 3 of 4 dummy clips, so thr 0.3 is near-inert.
  - F-TRN-48: public evidence on 'more divisions'.
  - [c17] notes on F-LB-01/02/03/04/10/11/15, F-RUN-03/29, F-RUL-12, F-MOD-27, F-TRN-42 and F-DAT-05.
- **Contradictions:**
  - New C-132..C-143 (`FACTS.md` l.497-508), including: FREEZE vs new rungs (C-132); which E10 rule is in force (C-134); the 12:00Z line content (C-135); the partner #37 vs #38 (C-137); 'more divisions' (C-138); thr 0.3 inert (C-139); slots left (C-140); Corwin's secondary (C-142).
  - Resolved: C-121..C-123.
  - Updated: C-05, C-26, C-111, C-114, C-118, C-120, C-128, C-129.
- **DECISIONS.md:**
  - §1: new P45 row (l.167) and the built/planned table (l.292: exp70n/q/r, exp72, E10 v3 copies, exp73a..v, exp74, exp75).
  - §2: [c17] paragraph l.475 and a new snapshot at l.482 (replaces c16).
  - §2f: E10 v3 at l.736.
  - §2h: 7 appends and 5 new rows.
  - §3: R1-R10 and others updated, plus 6 new rows (e.g. R17-A1 corrected line, R17-A4 default, read cards R17-A2/A5).

**Watchlist** (`WATCHLIST.md`; `_curation/17/watch.json`):
- **Done:** W158 (R16-A1, 289bd52), W159 (round16/REPORT.md), W160 (R16-A2 sent; push status open), W154 (letter (b)), W135/W128/W106 (Q1/Q2 yes, exp71 pushed), W156a (FREEZE lifted).
- **Superseded:** W161 -> W169 (R17-A1), W165a E10 v2 -> v3, W164 -> W174, W163 -> W175.
- **New:** W168-W182, reminders T87-T98, insights I172-I186.
- **Still overdue:** W176 (ROUND 14-17 RECORDs), W126 (RESULTS rows 39-42), W182 (NEVER_SUBMIT for exp70j/k), the W57 family, W150 (round prompt), and the R16-A2 push status.

**Alerts** (`INDEX.md` TOP ALERTS, 8 after dedup):
- **Resolved since curation 16:**
  - R16-A1 logged and pushed pre-score.
  - R16-A2 sent.
  - Class-C letter received and pre-registered.
  - E10 v2 question superseded by the user.
  - exp71 yes/push.
  - The exp70b/(b)-partner ambiguity for 43/44: #37, per the letter.
- **Partly resolved after the curators ran:** the 12:00Z line is logged (a6ffbc9, `CONTEXT.md` l.2952-2954) with the corrected wording. It still lacks the slot count, bracket check, push status and deviation record, so the alert was downgraded from 'log it' to 'complete it'.
- **Carried over:** 43/44 read (now R17-A2 with the (b) re-tick text), RESUME POINT/MEMORY (C-26), ROUND RECORDs, RESULTS rows, NEVER_SUBMIT, HINDSIGHT GUARD, `fb_ins35.py`, round prompt, I-233.
- **New:**
  - R17-A3 last-slot line before the first 43/44 header.
  - No dummy for exp70q/r.
  - E10 v3 tooling uncommitted and the loop not running.
  - Untracked 28 Sep levers (exp73/74/75).
  - Pre-score card R17-A5 by 17:50Z.
  - R17-A4 slot-collision ask.
  - GPU quota not re-read.
  - 20:00Z is our buffer, not a Kaggle freeze.
  - exp70n name reuse.
- **Curator disagreements settled here:**
  - 12:00Z line: all three curators said [now] 'log R17-A1' -> [now] 'complete it', because a6ffbc9 landed after they ran.
  - Aggressive-rung evidence: [info] (facts) vs [now] (watch) -> folded into the [now] R17-A3 alert.
  - Untracked levers: [before-finals] (facts) vs [today] (ideas, watch) -> [today], because 28 Sep slots start at 00:00Z and exp72 keeps 00:05Z.

## 18 - 2026-09-27 ~16:05 UTC (curation 18; git HEAD b853642 = origin/main + untracked `research/wf_ideas_v4/round18/`, `experiments/e10_watch/20260927T1343Z..1543Z.txt`, `experiments/ds_secw_corwin_v1/weights/`)

**Sources since curation 17:**
- `CONTEXT.md` l.2952-3010, 7 entries: 12:00 line; R8 FULL RECORD 12:12; last-slot pre-score line 12:12; bigger levers 12:49; P43/P44 READ 13:14; exp71 done + exp72 built 13:27; P46 exp70q submitted 14:37.
- Commits ac08c5e, c86fd5a, f28d5f5, 0408ab1, 2981590, b853642 (`git log`).
- Round 18: `research/wf_ideas_v4/round18/REPORT.md`, `report.json` R18-A0..A10.
- Polls and LB: `experiments/lb_poll/poll.log` 16:03:10Z (P45/P46 PENDING); `experiments/e10_watch/watch_loop.log` (4 runs, 0 signals); `experiments/e10_watch/20260927T1543Z.txt` (rank 283 / 3,952).

**Ideas** (`IDEAS.md` CHANGES (18) l.88-99; `ideas.json` meta.curations[n=18]; `_curation/18/ideas.json`):
- **New:**
  - I-373..I-377, I-379: exp70b rebase and the exp76a/d/c/g/h/e/i/f builds.
  - I-380: R18S-3 waves, rejected.
  - I-381..I-383: slot budget, CI no-op/queue-stall guard, ledger families.
  - Post-deadline or rejected: I-378 (exp76b), I-384..I-387.
  - I-388: fixed round timer, only if the user asks.
- **Status changes:**
  - lb-tested: I-341, I-342 (0.954/0.954) and I-344 (letter (b) did not fire).
  - refuted: I-362 (exp70r), I-360 (exp70n), I-366 (27 Sep collision moot).
  - Other: I-361 submitted as P46; I-324 exp75 downgraded to a sign probe; I-119 exp72 dummy clean.
- **Counts c17 -> c18:** 372 -> 388. lb-tested 48 -> 51, refuted 186 -> 192, deferred 42 -> 45, in-plan 73 -> 76, open 2 -> 3; lab-tested 21 is unchanged. The strict orphan is still I-233.

**Facts and decisions** (`FACTS.md`, `DECISIONS.md`, rows marked [c18]; `_curation/18/facts.json`):
- **New facts:**
  - F-RUN-31: latency drift; P45/P46 windows (l.264).
  - F-RUN-32: coordinject runtime budget; no ledger family (l.265).
  - F-RUN-33: round cadence, mean 2.72 h, median 2.52 h, range 1.73-4.25 h (l.266).
  - F-MOD-34: exp75/exp76 CI line (l.328).
  - F-MOD-35: primary-logit roles (l.329).
  - F-TRN-49: display-edge arithmetic (l.383).
- **Contradictions:** new C-144..C-149, e.g. C-144 'exp75 best chance' vs sign probe and C-148 cadence (l.532-537); 14 contradictions updated.
- **DECISIONS.md:**
  - §1: P46 row (l.177) and the new built/planned table (l.319).
  - §2: snapshot l.523 (#37 + #38 TICKED; CI and secFT files public-only).
  - §2f: E10 v3 loop live (l.786).
  - §2h: rows for the R8 record, the last-slot line, the 43/44 read, the round-18 card and the 28 Sep slot budget (l.861-866).
  - §3: the R8 cutoff is logged; the 02:00Z cap question is open.

**Watchlist** (`WATCHLIST.md`; `_curation/18/watch.json`):
- **Done:** 12:00/12:12 records, the last-slot line, the 43/44 read, E10 v3 committed and live, round 17 committed, exp71/exp72, P46 submitted.
- **Superseded:** W173 -> W184, W175 -> W185, W172 -> W189, W180 submit step -> W190.
- **New:** W183-W194, reminders T100-T108, insights I187-I197.
- **Still overdue:** W126 (RESULTS rows P39-P46), W176 (ROUND RECORDs), W182 (NEVER_SUBMIT for exp70j/k), H1, `fb_ins35.py`.

**Alerts** (`INDEX.md` TOP ALERTS, 8 after dedup):
- **Resolved since curation 17:**
  - The 12:00Z line was completed by the 12:12 full record (`CONTEXT.md` l.2955-2971).
  - The R17-A3 line was logged before any 43/44 score (l.2972-2982).
  - The exp70q dummy ran and P46 was submitted (l.3007-3010).
  - E10 v3 tooling was committed (c86fd5a) and the loop is live.
  - The untracked 28 Sep levers were committed and logged (l.2983-2994).
  - The 43/44 read happened (l.2995-3000).
- **Carried over, re-keyed to round 18:**
  - Pre-score card: R17-A5 -> R18-A1.
  - RESUME POINT/MEMORY/timers: R17-A7 -> R18-A2.
  - RESULTS rows, ROUND RECORDs, NEVER_SUBMIT, HINDSIGHT GUARD, `fb_ins35.py`, I-233.
- **New:**
  - User cadence answer and the three plan corrections (R18-A0).
  - Build and push exp76a/d.
  - exp75 queue stall and the CI risk for W1 (19:00Z decision).
  - runtime_ledger families.
  - exp72 gate values not logged; probe.json boilerplate.
  - The 'v' suffix for L_hi > 8.0 h.
  - The 02:00Z cap and exp74 questions.
  - sha and MSYS path traps.
  - The exp73 SI-name collision.
- **Curator disagreements settled here:**
  - Pre-score card: [now] (ideas, facts) vs [today] (watch) -> [now], because the 17:50Z deadline is <2 h away.
  - RESUME POINT/timers: [now] (ideas, watch) vs [today] (facts) -> [now], because the 45 read timer must exist before ~17:56Z.
  - The cadence answer was marked stale/contradiction/risk by the three curators -> one [now] alert that carries the plan corrections.

## 19 - 2026-09-27 ~18:50 UTC (curation 19; git HEAD 22840c5 = origin/main + untracked `research/wf_ideas_v4/round19/`, `experiments/exp77_secft_n2/`, `experiments/e10_watch/20260927T1731Z.txt`, `20260927T1743Z.txt`, `experiments/ds_secw_corwin_v1/weights/`)

**Sources since curation 18:**
- `CONTEXT.md` l.3011-3074, 5 entries: round-18 PRE-SCORE CARD 16:08; REBASE onto exp70b 16:08; exp76d dummy clean 16:33; exp75 dummy complete 17:21; USER YES TO N2 18:19:11. `## 9. Literature` moved to l.3075.
- Commits 12d9271, 77e7810, ffe74d6, 22840c5 (`git log`).
- Round 19: `research/wf_ideas_v4/round19/REPORT.md`, `report.json` R19-A1..A12 (report complete 18:28:35Z), `scan_plancheck.json`, `scan_recheck.json`, `scan_hyp_reads_table.json`, `scan_hyp_n1_prep.json`.
- Polls and LB: `experiments/lb_poll/poll.log` 18:44:52Z (P45/P46 still PENDING); `experiments/e10_watch/watch_loop.log` (RUN 5-7, 0 signals); `experiments/e10_watch/20260927T1843Z.txt` (#289, SubmissionCount 46).

**Ideas** (`IDEAS.md` CHANGES (19) l.94-104; `ideas.json` meta.curations[n=19], 48 records; `_curation/19/ideas.json`):
- **New:** I-389 (LSD S1 proof, refuted); I-390 (46-PENDING row); I-391 (per-mechanism fallbacks); I-392 (28 SEP READ TABLE v2); I-393 (V_pub finals rule, I-354 folded in); I-394 (W2 stacks exp76j/k); I-395 (tau 0.75 coin rung, needs a user yes); I-396 (N2 output rungs, user-approved, no slot yet).
- **Status changes:** I-385 N2 deferred -> in-plan (user yes 18:19:11Z, `CONTEXT.md` l.3070-3074); I-365 stays in-plan (card logged; R19-A1 amendment due).
- **Updated rows:** I-327 (count-rule UP test), I-381 (W1 00:05/00:10/00:50Z), I-382 (CI queue, exp76a gate), I-383 (ledger rules, CI latency 9.8-10.45 h), I-375 / I-324 (exp76d and exp75 dummies clean). The R19-A10 curator items were applied to I-051/I-334, I-333, I-025/I-053/I-352, I-304 and I-384.
- **Counts c18 -> c19:** 388 -> 396. in-plan 76 -> 83, refuted 192 -> 193, deferred 45 -> 44, open 3 -> 4; lb-tested 51 and lab-tested 21 are unchanged. The strict orphan is still I-233.

**Facts and decisions** (`FACTS.md`, `DECISIONS.md`, rows marked [c19]; `_curation/19/facts.json`):
- **New facts:**
  - F-RUN-34: CI kernels queue for hours on Kaggle (l.268).
  - F-MOD-36: dummy gate values for exp72, exp76d, exp70b, K2 and exp75 (l.332).
  - F-MOD-37: the exp77 N2 trainer, with recipes n2a and n2b (l.333).
  - F-MOD-38: N1 x2/x3/x1.5 weights, kept local only (l.334).
  - F-TRN-50: division lab on the exp70b bed (l.389). Tau 0.75 is a coin flip by embryo, divergence 2.5 has sign <= 0, and the DC band [0.25, 0.30) has 0 lab TP.
- **[c19] notes** on 11 facts (F-MET-10, F-LB-01/02/10, F-RUN-30/31/32, F-RUL-05/10, F-MOD-34, F-TRN-48).
- **Contradictions:** new C-150..C-158 (l.544-552). They cover:
  - N2/N1 terminology and the user's yes vs the closures;
  - CI runtime;
  - W1 fallbacks;
  - the exp77 name clash;
  - W1 times;
  - coordinject lab numbers;
  - the UP-test S0;
  - the R18-A4 withdrawal;
  - the ladder watcher.

  8 contradictions were updated.
- **DECISIONS.md:**
  - §1: P45/P46 rows updated; new [c19] built/planned table (l.339).
  - §2: snapshot replaced (l.544).
  - §2f: E10 note (l.815).
  - §2h: rows for the rebase, the N2 yes, R19-A1, READ TABLE v2, the R19-A7 message and the tau rung (l.891-896).
  - §3: R9 overridden again by the N2 yes; the R8 02:00Z cap still binds; R19-A1/A2/A6/A8 proposed (l.930-932).

**Watchlist** (`WATCHLIST.md`; `_curation/19/watch.json`):
- **New:** W195-W207, T109-T115, I198-I213.
- **Superseded:** W187 (CI drop/re-push withdrawn), W191 (ladder watcher -> manual LB download per terminal header), W190 -> W203, W189 -> W199 + W196.
- **Still overdue:** W185 RESUME POINT, W207 (no 46 waiter), W202 (b) (exp72 gates), W126 (RESULTS rows P39-P46), W176 (ROUND RECORDs), W182 (NEVER_SUBMIT for exp70j/k), H1.

**Alerts** (`INDEX.md` TOP ALERTS, 9 after dedup):
- **Resolved since curation 18:**
  - Pre-score card R18-A1 logged at 16:08, before any 45/46 score (l.3011-3056; 12d9271).
  - exp76a/exp76d built and rebased onto exp70b (l.3057-3062).
  - exp76d dummy clean (l.3063-3064).
  - exp75 queue stall over, dummy clean (l.3065-3069). R18-A4 is withdrawn.
  - Round 18 committed (12d9271).
- **Carried over, re-keyed to round 19:**
  - Pre-score amendment: R18-A1 -> R19-A1.
  - RESUME POINT/MEMORY: R18-A2 -> R19-A5.
  - Ledger families: R18-A5 -> R19-A6.
  - The 02:00Z cap question: R18-A6 -> R19-A7.
  - Records (RESULTS rows, ROUND RECORDs, NEVER_SUBMIT, H1, probe.json 'compare with exp56').
- **New:**
  - The N2 yes vs the three written closures, plus the N2 rung placement.
  - N2 weights must go only to NEW datasets (sha hard-fail).
  - No 46 waiter; stale 00:05Z waiter echo.
  - exp76c must be pushed by ~19:30Z.
  - GPU quota not re-read (~8-9 GPU-h planned).
  - exp77 name clash with the tau rung / R19-A6 rule.
  - S0 must be chosen by SubmissionCount.
  - R19-A7 message with 3 yes/no questions.
  - R19-A10 corrections (V6, exp72 gates, CI latency 9.8-10.45 h, +0.00215).
  - Do not upload N1 weights.
- **Curator disagreements settled here:**
  - N2 contradiction: [now] (ideas, watch) vs [today] (facts) -> [now], because it must precede any N2 dummy and the exp76d read.
  - GPU quota: [now] (watch) vs [today] (ideas, facts) -> [now], because the exp77 push is imminent.
  - runtime_ledger: [today] (ideas) vs [before-finals] (facts) -> [today], because it is due before 00:05Z 28 Sep.

## 20 - 2026-09-27 ~21:00 UTC (curation 20; git HEAD 771a608 = origin/main + untracked `research/wf_ideas_v4/round20/`, `experiments/e10_watch/20260927T2043Z.txt`, `experiments/ds_secw_corwin_v1/weights/`)

**Sources since curation 19:**
- `CONTEXT.md` l.3075-3221, 8 entries: R19-A1 amendment 18:50; READ TABLE v2 18:50; PROBE 45 READ 0.956 18:56; cap rungs 19:01; exp76a clean + exp77 pushed + exp79a/d built 19:05; USER finals-on-29-Sep 19:10:58; exp78a/exp76e clean 20:02; USER autonomous night 20:30. `## 9. Literature` moved to l.3222.
- Commits a2e0696, ca663c1, 7cd6a0e, bd7d7a4, cdeeb2d, 32eeedd, 771a608 (`git log`).
- Round 20: `research/wf_ideas_v4/round20/report.json` R20-A1..A14 (complete 20:45:36Z; no REPORT.md), `scan_plancheck.json`, `scan_hyp_insertion_direction.json`, `scan_hyp_private_view.json`, `scan_recheck.json`, `v_*.json`.
- Polls and LB: `experiments/lb_poll/poll.log` 20:55:15Z (P45 COMPLETE 0.956, P46 PENDING); `experiments/e10_watch/watch_loop.log` RUN 7-9 (0 signals); `experiments/e10_watch/20260927T2043Z.txt` l.981 (#163, count 47).

**Ideas** (`IDEAS.md` CHANGES (20) l.103-113; `ideas.json` meta.curations[n=20], 72 records; `_curation/20/ideas.json`):
- **New:** I-397 exp78a cap 8; I-398 exp78b cap 12 + fc2; I-399 exp80a cap 24 + fc2 (W2-conditional); I-400 cap 48 (refuted as a W2 step); I-401 exp79a cap 6 + CI; I-402 exp79d cap 6 + SEC; I-403 READ TABLE v3 + W1/W2 v3; I-404 exp78b + CI stack; I-405 GPU quota reading; I-406 29 Sep finals card lines; I-407 private-read addendum; I-408 extended cap lab (NULL); I-409 frame cap >= 3 and I-410 steal_frac/ALPHA (closed); I-411 thr-0.3 base switch and I-412 John Taylor port (rejected).
- **Status changes:** I-326, I-066, I-067 -> lb-tested (P45 = 0.956, public only; the lab was blind). I-363, I-373, I-376, I-390, I-391, I-394, I-375, I-395 -> refuted (superseded after the 0.956 and v3). I-388 -> in-plan (~2.5 h round cadence). I-365 and I-392 are now logged.
- **Counts c19 -> c20:** 396 -> 412. lb-tested 51 -> 54, lab-tested 21 -> 22, in-plan 83 -> 86, refuted 193 -> 204, deferred 44, open 4 -> 2. The strict orphan is still I-233.

**Facts and decisions** (`FACTS.md`, `DECISIONS.md`, rows marked [c20]; `_curation/20/facts.json`):
- **New facts:** F-MOD-39, the 28 Sep cap-direction and cap-6 builds (l.336); F-TRN-51, the extended cap lab, where all gain at cap >= 8 comes from 6bba (l.392); F-TRN-52, private-view models for the cap line (l.393).
- **[c20] appends:** 16 facts (F-LB-01/02/03/10/12, F-RUN-31/34, F-RUL-05/10/12, F-MOD-33/36/37, F-TRN-42/48) and 11 contradictions.
- **New contradictions C-159..C-166** (l.557-564):
  - the P45 S0 deviation (127, not 113);
  - exp70g class B vs C;
  - the W1 plan conflict;
  - B-relative codes;
  - the E10 trigger level;
  - finals timing;
  - the 02:00Z cap;
  - exp79a status.
- **DECISIONS.md:**
  - P45/P46 rows (l.178-179) and the §1 [c20] table (l.358);
  - the §2 [c20] snapshot (l.584; exp70g = current V_pub; proposal {exp70g, #37});
  - §2f E10 (l.852);
  - §2h rows (l.934-943);
  - §3 R20 rows (l.981-984).

**Watchlist** (`WATCHLIST.md`; `_curation/20/watch.json`):
- **New:** W208-W215, T116-T121, I214-I230.
- **Done:** W195, W196, W198, W202 (b), W205 (push), W207 (46 waiter, `CONTEXT.md` l.3216).
- **Superseded:** W197, W200, W201.
- **Still overdue:** W185 RESUME POINT (5th round), W188 ledger families (4th), W126 RESULTS rows, W176, W177, W182.

**Alerts** (`INDEX.md` TOP ALERTS, 10 after dedup):
- **Resolved since curation 19:**
  - R19-A1 and READ TABLE v2 were logged pre-score (a2e0696 18:50:11Z vs the 18:54:54Z header).
  - 45 was read.
  - exp76a, exp78a, exp76e and exp78b dummies are clean.
  - exp77 was pushed.
  - The 46 waiter is set.
  - round 19 was committed.
  - The N2-vs-closures conflict is handled by the proposed R20-A6.
  - The GPU-quota and ledger alerts carry over, re-keyed to R20-A7 and R20-A4.
- **New:**
  - exp79a is unpushed (404) and the CI-latency arithmetic applies to it (W208, I229).
  - R20-A2 v3 codes + W1 v3 must land before 46 is terminal; they conflict with the 20:30Z CONTEXT plan.
  - The R20-A3 (B) correction of the 18:56Z read.
  - R20-A6 one-file N2 + the exp79d gate.
  - The 46 read with count 47/48.
  - E10 v3 texts are stale (>= 0.957, SI cap 6).
  - R20-A9 finals card lines + the R20-A12 morning message.
  - round20/REPORT.md is missing and round20/ is untracked.
- **Curator disagreements settled here:**
  - RESUME POINT [now] vs [today] -> [now].
  - N2 [today] vs [now] -> [now].
  - The W1 plan conflict is merged into the R20-A2 alert.

## 21 - 2026-09-27 ~23:56 UTC (curation 21; git HEAD 4ac7126 = origin/main + untracked `research/wf_ideas_v4/round21/`, `experiments/ext_succskip/`, `experiments/e10_watch/20260927T2143Z..2343Z.txt`, `experiments/ds_secw_corwin_v1/weights/`)

**Sources since curation 20:**
- `CONTEXT.md` l.3222-3310, 5 entries: READ TABLE v3 codes + W1/W2 v3 21:05 (logged while 46 was PENDING); N2 PRE-REGISTRATION 21:06; LEDGER + BUILD 21:06; N2 DONE + GATES 21:26; PROBE 46 READ 22:27. `## 9. Literature` moved to l.3311.
- Commits 9d0820c (round 20 + REPORT.md), 9e81f06, cc17974, 4ac7126 (`git log`).
- Round 21: `research/wf_ideas_v4/round21/report.json` R21-A1..A13 (complete 23:43:24Z; no REPORT.md), 5 `scan_*.json`, 15 `v_*.json`. New probe.json: `experiments/exp80a_k2_cap24_fc2/`, `experiments/exp81_k2cap6_secn2a/`.
- Polls and LB: `experiments/lb_poll/poll.log` to 23:55:50Z (P46 COMPLETE 0.956; no 28 Sep submit); `experiments/e10_watch/watch_loop.log` RUN 10-12 (0 signals); `experiments/e10_watch/20260927T2343Z.txt` l.307 (#167 of 3,960, count 48).

**Ideas** (`IDEAS.md` CHANGES (21) l.109-117; `ideas.json` meta.curations[n=21], 50 records; `_curation/21/ideas.json`):
- **New:** I-413 CI-RAN GATE; I-414 W2 TABLE v4 + DIV STOP RULES S1-S6; I-415 W4 AMEND 2 + E10 copy after 02:00Z 29 Sep; I-416 BASE-lookup stack builds (exp82*/exp83*, scratch only); I-417 holder rule for the SEC file (refuted); I-418 ERROR / dataset-freeze rules + NO-GO list; I-419 exp60 replay is DC-blind for pre-DC gate relaxations.
- **Status changes:** I-361 (exp70q) in-plan -> lb-tested (P46 = 0.956, code 0); I-385 (N2) -> lab-tested (n2a 7029fe69, proxy 0.998/1.010); I-400 (cap 48) refuted -> in-plan (exp84a, only under S3); I-374 (exp76a) and I-402 (exp79d) -> refuted (superseded); I-084, I-190, I-051 stay closed after the round-21 rechecks. Logged since c20: I-403, I-381, I-392 (v3), I-383 (safetail_ci), I-398/I-401 (dummy PASS), I-399/I-396 (exp80a/exp81 built).
- **Counts c20 -> c21:** 412 -> 419. lb-tested 54 -> 55, lab-tested 22 -> 24, in-plan 86 -> 88, refuted 204 -> 206, deferred 44, open 2. The strict orphan is still I-233; 16 at-risk orphans (I-324, I-413, I-414, I-415, I-406, I-383, I-257, ...).

**Facts and decisions** (`FACTS.md`, `DECISIONS.md`, rows marked [c21]; `_curation/21/facts.json`):
- **New facts:** F-LB-16 P46 read (l.232); F-RUN-35 CI hidden-run model + CI-RAN gate (l.272); F-MOD-40 dummy gate values for the W1/W2 files (l.340); F-TRN-53 round-21 rechecks (l.398).
- **[c21] appends:** F-LB-01/02/03/10/15, F-RUN-03/11/31/34, F-RUL-05/12, F-MOD-37/39, F-TRN-52; C-26/118/159/163/164/165.
- **Resolved contradictions:** C-161, C-162 (v3 logged pre-46), C-166 (exp79a pushed and PASSED).
- **New contradictions C-167..C-174** (l.570-577): P46 stale S0; W2b duplicate (exp79a); CI queue premise; stack names; exp83 ledger family; GPU quota estimates; E10 after 02:00Z; N2 proxy band.
- **DECISIONS.md:** P45/P46 rows (l.179-180); §1 [c21] 12-row build/plan table (l.375); §2 [c21] snapshot (l.620; V_pub = exp70g, exp70q not V_pub); §2f E10 (l.890); §2h rows (l.982-989); §3 R21 rows.

**Watchlist** (`WATCHLIST.md`; `_curation/21/watch.json`):
- **New:** W216-W223, T122-T128, I231-I248.
- **Done:** W188 (ledger family), W204, W205, W206 (N2 pre-reg), W208 (exp79a push), W209 (v3), W211, W213 (46 read), T111, T112. **Moot:** T116, I229 (CI queue premise).
- **Still overdue:** W185 RESUME POINT (6th round), W126 RESULTS rows P39-P46, W212 GPU quota.

**Alerts** (`INDEX.md` TOP ALERTS, 10 after dedup):
- **Resolved since curation 20:** R20-A2 v3 logged pre-46 (9d0820c; `CONTEXT.md` l.3222); R20-A6 N2 pre-registration logged before exp77 finished (l.3286); R20-A4 ledger family (l.3296); exp79a pushed + PASS (l.3304); 46 read (l.3307); round 20 committed with REPORT.md; round-20 alert 2 (CI queue) refuted (`FACTS.md` C-169).
- **New:** R8 COVERAGE line before exp79a (R21-A1); W1 submit procedure (R21-A2); exp83 ledger rule + exp83a/b dummies (R21-A5/A6); R21-A3 CONTEXT write (PASS lines, CI-RAN GATE, 46 S0 addendum, ERROR rules, NO-GO); W2 TABLE v4 / W4 AMEND 2 / finals card before ~07:30Z (R21-A7..A9); E10 after 02:00Z question (R21-A10); scratch-only builds; latency-drift and sub-display reading caveats (R21-A12).
- **Carried over:** RESUME POINT (R20-A3 -> R21-A4), GPU quota (R20-A7 -> R21-A11), E10 stale texts (R20-A10 (5) -> R21-A9 (v)), finals card (R20-A9 -> R21-A9), records (RESULTS, REPORT.md -> R21-A13).
- **Curator disagreements settled here:** exp83 ledger rule [now] vs [today] -> [now]; finals card [today] vs [before-finals] -> [today]; RESULTS rows [info] vs [before-finals] -> [before-finals].

## 22 - 2026-09-28 ~01:48 UTC (curation 22; git HEAD acbea01 = origin/main + untracked `research/wf_ideas_v4/round22/`, `experiments/ext_succskip/`, `experiments/ext_corwin-biocel-aux/_booster/`, `experiments/e10_watch/20260928T0043Z..0143Z.txt`, `experiments/ds_secw_corwin_v1/weights/`)

**Sources since curation 21:**
- `CONTEXT.md` l.3311-3377, 7 entries: R8 COVERAGE 00:00 (l.3311); R21-A3 gates 00:00 (l.3316-3337); W1 SUBMITS 00:06 (l.3338) and 00:50 (l.3342); R21-A5/A6 exp83 rule + builds 01:02 (l.3344); W2 TABLE v4 + S1-S6 01:02 (l.3347); W4 AMEND 2 01:02 (l.3366). `## 9. Literature` moved to l.3378.
- Commits d36a4b2 (round 21 + REPORT.md), b0bac2e, 978124d, ad5cbaf, bb3c299, acbea01 (`git log`).
- Round 22: `research/wf_ideas_v4/round22/report.json` + `REPORT.md` R22-A1..A11 (01:32:58Z), 5 `scan_*.json`, 13 `v_*.json`. New probe.json: `experiments/exp83a_k2cap12fc2_ci/`, `experiments/exp83b_k2cap8_ci/`.
- Polls and LB: `experiments/lb_poll/poll.log` to 01:36:09Z (P47/P48/P49 PENDING); `experiments/e10_watch/watch_loop.log` RUN 13-14 (0 signals); `experiments/e10_watch/20260928T0143Z.txt` l.1013 (#169, 10th of 59 in the 0.956 block).

**Ideas** (`IDEAS.md` CHANGES (22) l.117-125; `ideas.json` meta.curations[n=22], 53 records; `_curation/22/ideas.json`):
- **New:** I-420 CI-STACK DUMMY GATE; I-421 PRE-SCORE CLARIFICATIONS (CI-? SCOPE etc.); I-422 fc2 at cap 6 (refuted, banned knob rung); I-423 DaughterNet fold subset (refuted by construction); I-424 post-deadline theft-aware ranker for claimed daughters (32/99 missed GT divisions); I-425 28 Sep morning brief.
- **Status changes:** W1 submitted, no score yet: I-398 (P47), I-401 + I-324 (P48, first CI on the LB), I-397 (P49), I-381. Logged in CONTEXT: I-324, I-396, I-399, I-413, I-414, I-415, I-418, I-383, I-404, I-327. I-410 ALPHA -> refuted/dominated (lab); I-082 MITO3 refuted -> deferred-after-deadline (pluggable edges-only, probmat features NaN in the ship path); I-259 task template -> in-plan. Wording/evidence updates: I-046 (failure-class record, not CI transfer), I-080, I-059, I-060, I-064, I-408, I-412, I-049, I-139.
- **Counts c21 -> c22:** 419 -> 425. lb-tested 55, lab-tested 24, in-plan 88 -> 91, refuted 206 -> 207, deferred 44 -> 46, open 2. The strict orphan is still I-233; at risk: I-252, I-257, I-259, I-330, I-336, I-405, I-406, I-407, I-416, I-420, I-421, I-425.

**Facts and decisions** (`FACTS.md`, `DECISIONS.md`, rows marked [c22]; `_curation/22/facts.json`):
- **New facts:** F-LB-17 W1 record (l.234); F-LB-18 competitor intel, John Taylor knobs (l.235); F-RUN-36 W1 timing, safetail floor 6.69 h (l.276); F-MOD-41 exp83a/b builds + undefined CI gate, 9 stacks missing (l.345); F-TRN-54 round-22 lab rechecks (l.404).
- **[c22] appends:** F-LB-01/02/03/10/15/16, F-RUN-11/34/35, F-RUL-01/05/12, F-MOD-40; C-26/118/159/163/164/165/169/170/172/173.
- **Resolved contradictions:** C-167, C-168, C-171.
- **New contradictions C-175..C-181** (l.584-590): CI stack after a CI '?'; 12:00Z consolidation not superseded; earliest 47 terminal; undefined CI-stack PASS; MITO3 probmat NaN; one-sided CI caveat; W2a with an unread DIV ref.
- **DECISIONS.md:** P47/P48/P49 rows (l.182-184); §1 [c22] 11-row build table (l.396); §2 [c22] finals paragraph + snapshot (l.654-656; V_pub = exp70g); §2f E10 paragraph (l.929); §2h rows (l.1029-1037); §3 11 appends + 5 R22 rows.

**Watchlist** (`WATCHLIST.md`; `_curation/22/watch.json`):
- **New:** W224-W229 (R22-A1/A3/A6/A7/A10/A11), T129-T133, I249-I261.
- **Done:** W216 (R8 COVERAGE), W203 (W1 submits), W217 (R21-A3), W218, W219 (1) (exp83 rule + dummies), W220 (W2 v4), W221 (W4 AMEND 2), W223 (round 21 committed), T113, T18.
- **Re-keyed:** W185 -> R22-A2 (7th round), W214 -> R22-A4 (2nd), W212 -> R22-A5 (3rd), W222 -> R22-A8, W202 -> R22-A9.
- **Still overdue:** W126 RESULTS rows P39-P46, E10 loop text '>= 0.955' (`experiments/lb_poll/e10_watch_loop.py` l.28, l.78), W176/W177/W182.

**Alerts** (`INDEX.md` TOP ALERTS, 10 after dedup):
- **Resolved since curation 21:** R21-A1 R8 COVERAGE (l.3311, d36a4b2); R21-A2 W1 submits (l.3338, l.3342); R21-A3 gates (l.3316); R21-A5/A6 exp83 rule + exp83a/b dummies (l.3344; `tools/runtime_ledger.py` l.80); R21-A7/A8 W2 TABLE v4 / W4 AMEND 2 pre-score (l.3347, l.3366); R21-A13 round 21 committed with REPORT.md (d36a4b2).
- **New:** R22-A1 CI-STACK DUMMY GATE before the exp83a/b outputs are read; R22-A3 CI-? SCOPE contradiction + W2a/consolidation gaps; W1 read window starts ~06:58Z (hard stop 06:45Z for pre-score lines); 9 missing stack builds (R22-A6/A11); stale task template (R22-A10); round-22 closures only in research files (R22-A9); weak cap-48 lab prior for exp84a.
- **Carried over:** RESUME POINT (R21-A4 -> R22-A2), finals card + E10 NOW line (R21-A9 -> R22-A4), GPU quota (R21-A11 -> R22-A5, estimate raised to ~20.6-22 h / 25-26.5 h at 2x), morning message (R21-A10 -> R22-A8), RESULTS rows.
- **Curator disagreements settled here:** R22-A3 [now]/[today] -> [now]; R22-A4 [now]/[today] -> [now]; task template [today]/[now] -> [now]; RESULTS rows [info]/[before-finals] -> [info] with the FINALS READ as deadline.

## 23 - 2026-09-28 ~04:50 UTC (curation 23, re-run after the round-23 curator agents failed on the weekly limit; git HEAD 08ceca1 = origin/main + untracked `experiments/exp82a-c`, `exp83c-g`, `exp84a`, `experiments/e10_watch/20260928T0443Z.txt`, `experiments/ext_succskip/`, `experiments/ext_corwin-biocel-aux/_booster/`, `experiments/ds_secw_corwin_v1/weights/`)

**Sources since curation 22:**
- `CONTEXT.md` l.3378-3447, 10 entries: CI-STACK DUMMY GATE 01:48 (l.3378); PRE-SCORE CLARIFICATIONS 01:48 (l.3387); RESUME POINT 01:48 (l.3398); P45 CORRECTION (l.3409); CI-STACK GATE READ PASS 01:50 (l.3411); E10 SIGNAL CHECKED 02:46 (l.3414); FINALS CARD + E10 v3 NOW + S7 + SEC-STACK GATE 04:31 (l.3417-3430); USER limit reset 04:32 (l.3431); DISCUSSION 743929 knobs + exp85a/b/c + W2 AMENDMENT 04:38 (l.3433-3441); PROCESS FIX 04:39 (l.3442-3447). `## 9. Literature` moved to l.3448.
- Commits dc6198b, e46b7ea, d251648, 95276ad, db8ba02 (round 23 report), 46c18a2, d14e9a3 (exp85a/b/c), 08ceca1 (`git log`).
- Round 23: `research/wf_ideas_v4/round23/report.json` + `REPORT.md` R23-A1..A12, 5 `scan_*.json`, 16 `v_*.json`. New probe.json files: `experiments/exp85a_k2cap6_div04_ra094/`, `exp85b_k2cap6_div04/`, `exp85c_k2cap6_ra094/`; nine untracked stack folders `experiments/exp82a_k2cap8_secn2a/` ... `exp84a_k2_cap48_fc2/`.
- Polls and LB: `experiments/lb_poll/poll.log` to 04:36:39Z (l.20089; P47/P48/P49 PENDING, no new score); `experiments/e10_watch/watch_loop.log` RUN 15-17 (one non-trigger signal at RUN 15); `experiments/e10_watch/20260928T0443Z.txt` l.313, l.1035 (#173, 10th of 58 in the 0.956 block).

**Ideas** (`IDEAS.md` CHANGES (23) l.128-137; `ideas.json` meta.curations[n=23], 44 records; `_curation/23/ideas.json`):
- **New:** I-426 29 Sep finals proposal message (in-plan, at risk); I-427 absence-insurance pre-tick (refuted); I-428 SEC-STACK DUMMY GATE (in-plan, logged); I-429 'push the SEC dummies now' (refuted); I-430 'low-score premise is an in-sample artifact' (refuted); I-431 exp85a/b/c = John Taylor's knobs on exp70g, exp85a = W2a at dummy PASS (in-plan).
- **Status changes:** I-412 refuted -> in-plan (via I-431). Logged, no longer at risk: I-406 finals card, I-257 RESUME POINT, I-421 clarifications, I-420 CI gate (+ PASS: I-404, I-398, I-397). Updated: I-364/I-287 (E10 NOW; SI runbook defect), I-414/I-399/I-396 (S7; exp80a/exp81 -> W3/W4), I-416 (nine stacks built), I-405 (quota 4th deferral), I-139/I-049 (READMIT re-refuted on the lowrefine coupling, then overridden by the 04:39 fix; ILP 0.4 has no direct output channel).
- **Counts c22 -> c23:** 425 -> 431. lb-tested 55, lab-tested 24, in-plan 91 -> 95, refuted 207 -> 209, deferred 46, open 2. Strict orphan I-233; at risk I-252, I-259, I-330, I-336, I-405, I-407, I-425, I-426.

**Facts and decisions** (`FACTS.md`, `DECISIONS.md` rows marked [c23]; `_curation/23/facts.json`; state as of 04:40Z, before the 04:38/04:39 entries):
- **New facts:** F-LB-19 competitor intel (l.237); F-RUN-37 research-round availability (l.279); F-MOD-42 stack builds, SEC gate, SI rehearsal (l.349); F-TRN-55 round-23 lab rechecks + mc23 model (l.409).
- **[c23] appends:** F-LB-01/02/10/15/17, F-RUN-33/36, F-RUL-01/05/10/12, F-MOD-40/41.
- **Resolved contradictions:** C-26, C-159, C-164, C-170, C-175..C-178, C-181. **Updated:** C-118/163/165/172/173/180.
- **New contradictions C-182..C-189** (l.596-603): S3 vs W2 v4 (resolved by S7); runbook SI recipe; condensed card; snapshot tracking; limit note vs reset; report timestamp; #38 rationale; stale template.
- **DECISIONS.md:** P47-P49 status appends (l.183-185); §1 [c23] build table (l.409-424); §2 [c23] card paragraph + snapshot (l.690-692; V_pub = exp70g, proposal {V_pub, #37}); §2f E10 (l.967); §2h rows (l.1076-1091); §3 R23 rows (l.1144-1150).
- **Gap:** exp85a/b/c are not yet in FACTS/DECISIONS/WATCHLIST (`grep -c exp85` = 0); only `IDEAS.md` I-431 covers them.

**Watchlist** (`WATCHLIST.md`; `_curation/23/watch.json`):
- **New:** W230-W234, T135-T138, I262-I273.
- **Done/resolved:** T122 (exp83a/b PASS, l.3411), I258 (CI-? SCOPE), I216 (P45 correction), I249 (CI gate used), I261, I239/I223 (card logged).
- **Re-mapped:** W212 -> R23-A5; W226/W229 -> R23-A7; W202 -> R23-A8; W199 + W222 -> R23-A9; W228 -> R23-A11; W227 -> R23-A12.
- **Still overdue:** W228 template, W232 runbook SI, W212 quota, W229 builds commit, W126 RESULTS rows, W202 info line, E10 loop '>= 0.955' text.

**Alerts** (`INDEX.md` TOP ALERTS, 10 after dedup):
- **Resolved since curation 22:** R22-A1 CI gate + PASS (l.3378, l.3411); R22-A2 RESUME POINT + P45 correction + MEMORY (l.3398, l.3409); R22-A3 clarifications (l.3387); R22-A4 card + E10 NOW pre-score (l.3417-3425, condensed); R22-A6 stacks rebuilt (F-MOD-42); round 23 committed with REPORT.md (db8ba02); limit outage ended (l.3431).
- **New:** exp85a READMIT/lowrefine coupling + ILP 0.4 no-output-channel, record node growth before submit (R23-RC-A/B); E10 runbook SI cap 4 / REF exp58 (R23-A4); SEC gate lacks sibling CSVs and clauses (R23-A3, A6); W2 plan churn + unlogged '04:5x amendment'; finals draft R23-A10 defects; R23-A8/R20-A13 CONTEXT lines.
- **Carried over:** task template (R22-A10 -> R23-A11), GPU quota (R22-A5 -> R23-A5, 4th), morning brief (R22-A8 -> R23-A9), W1 read procedure (R22-A7 -> R23-A12), stack log/commit (R22-A11 -> R23-A7), RESULTS rows, E10 loop text.
- **Curator disagreements settled here:** template [today]/[now] -> [now]; stack log/commit [now]/[today] -> [today]; finals draft [before-finals] (all); RESULTS rows [info], due before the FINALS READ.

## 24 - 2026-09-28 ~07:45 UTC (curation 24; git HEAD 19c24b5 = origin/main + untracked `research/wf_ideas_v4/round24/` (no REPORT.md), `experiments/e10_watch/20260928T0639Z.txt`, `20260928T0722Z.txt`, `experiments/discussions/digest_20260928T0704Z.md`, `0735Z.md`, new `experiments/ext_*` folders, `experiments/ds_secw_corwin_v1/weights/`)

**Sources since curation 23:**
- `CONTEXT.md` l.3448-3538, 7 entries: CURATION 23 ACTED ON + exp85a PRE-SUBMIT LINE 04:53 (l.3448); PROBE 50 SUBMITTED + GPU QUOTA READ 05:03 (l.3465); exp85b/c GATES + OPS RESTART 06:26 (l.3479); kaggle_feed + first API discussions read 06:35 (l.3495); exp86a/b/c BUILT 06:37 (l.3515); exp86a/b/c GATES PASS 07:28 (l.3522); P47 READ 07:32 (l.3530-3538). `## 9. Literature` moved to l.3539.
- Commits d14e9a3, d015291, 59e14e2, 048c518, a240ba1, ebadfa3, af035e7, f40d44b, 19c24b5 (`git log`).
- Round 24: `research/wf_ideas_v4/round24/report.json` R24-A1..A11 (07:18Z), 6 `scan_*.json`, 23 `v_*.json`; no REPORT.md. New kernels: `experiments/exp86a_k2cap8_div04_ra094/`, `exp86b_k2cap12fc2_div04_ra094/`, `exp86c_k2cap6_div04_ra092/`.
- LB and feeds: `experiments/lb_poll/poll.log` to 07:32:48Z (l.20760); `ledger.md` 07:32:50Z (gap 05:06:44Z -> 06:22:29Z); `experiments/lb_poll/_lb/S0_0729Z`; `experiments/e10_watch/watch_loop.log` RUN 18-19 (0 signals); `experiments/discussions/feed_loop.log` (E10 FLAG none to 07:35:25Z).

**New LB results:** P47 exp78b (cap 12 + FRAME_CAP 2) = **0.955, code '-', no UP**. S5 closes the cap direction above 8. P50 = exp85a (exp70g + ILP 0.4 + READMIT 0.94) was submitted 05:02:30Z. P48, P49 and P50 are PENDING (`CONTEXT.md` l.3465-3474, l.3530-3538). Best display is unchanged at 0.956 (exp70g = V_pub). Rank #181/3,966 at 07:29Z.

**Ideas** (`IDEAS.md` CHANGES (24) l.135-144; `ideas.json` meta.curations[n=24], 64 records; `_curation/24/ideas.json`; curated at 07:31Z, before the P47 read):
- **New I-432..I-448:**
  - I-432 kaggle_feed.
  - I-433 detached loops + live-session plan.
  - I-434 GAP RULE.
  - I-435 exp86a/b/c.
  - I-436 TABLE v5 + K LEVER.
  - I-437 W4 AMEND 3 + (4) EXCEPTION.
  - I-438 exp87 builds.
  - I-439 RA98 (refuted).
  - I-440 coordinject ALPHA 1.0 (refuted).
  - I-441 ILP-fork restore (refuted).
  - I-442 exp87m V6 filler.
  - I-443 SYN-DN (deferred).
  - I-444 'V_pub + one-lever parent' (refuted).
  - I-445 node-row hash gate + runtime rule v2.
  - I-446 watch thresholds.
  - I-447 T1-T5 push schedule.
  - I-448 builder weight-path hardening.
- **Status changes:**
  - I-139 moves refuted -> in-plan: READMIT 0.94 is on the LB inside P50, and the lowrefine-coupling reason is withdrawn (R24-RC-A).
  - I-405 (quota read) and I-259 (template refreshed) leave the at-risk list.
  - I-287 is fixed but gets a K-base SI rule.
- **Pending for curation 25:** I-398 (exp78b) and the cap-direction ideas still need the P47 '-' read.
- **Counts c23 -> c24:** 431 -> 448. In-plan 95 -> 108, refuted 209 -> 212, deferred 46 -> 47, others unchanged. Strict orphan: I-233. At risk: I-252, I-330, I-336, I-407, I-425, I-426, I-434, I-436, I-437, I-448.

**Facts and decisions** (`FACTS.md`, `DECISIONS.md` rows marked [c24]; `_curation/24/facts.json`; state 07:35Z, includes P47):
- **New facts:**
  - F-LB-20: LB movers (l.239).
  - F-LB-21: discussion intel via the API; no public notebook above 0.953 (l.240).
  - F-RUN-38: dummy runtimes (l.283).
  - F-RUL-19: disclosed-knob rule + P50 guard (l.307).
  - F-MOD-43: exp85/exp86 builds and gates (l.355).
  - F-TRN-56: K-knob decomposition, where READMIT carries the change and ILP 0.4 adds +3 safe divisions (l.416).
- **[c24] appends:** F-LB-01/02/04/10/15/17/18, F-RUN-33/36/37, F-RUL-01/05/12/15, F-MOD-40/42/43, F-TRN-51/55/56, F-DAT-02.
- **Contradictions:**
  - Resolved: C-170, C-172, C-183, C-189.
  - Updated: C-118, C-163, C-165, C-184.
  - New C-190..C-200 (l.611-621): knob status; W2b text; ILP inertness; lowrefine coupling; synthetic author (José Freitas, not hengck23); runtime criterion; GT division count (304 vs 149); finals partner advice; READMIT 0.92 ban; P47 L bound; exp86c gate.
- **DECISIONS.md:**
  - §1: P47 read and a new P50 row (l.184-187), plus the [c24] build table (l.427-429).
  - §2: [c24] paragraph + snapshot (l.730-732). V_pub = exp70g; the proposal is still {V_pub, #37}.
  - §2f: E10 (l.1009).
  - §2h: [c24] rows (l.1134-1147).
  - §3: [c24] rows (l.1211-1218).

**Watchlist** (`WATCHLIST.md`; `_curation/24/watch.json`; curated at 07:25Z, before the P47 read):
- **New:** W235-W247, T139-T144, I274-I286.
- **Done:**
  - W228 template.
  - W232 runbook SI.
  - W212 quota.
  - W229 stacks commit.
  - W126 part 1 (RESULTS 39-46).
  - W174 loop text.
  - W231 (c) sibling CSVs.
  - W233 push-by-BASE principle.
- **Superseded:** T117 (W2a taken by P50), and W199/W222 (morning brief -> W241).
- **Superseded after the watch curator ran:** W238's 'exp86c has no output' and I282 (gates logged 07:28, `CONTEXT.md` l.3522); T139 (47 read, l.3530).

**Alerts** (`INDEX.md` TOP ALERTS, 10 after dedup):
- **Resolved since curation 23:**
  - R23-A4, R23-A11, R23-A5, R23-A7.
  - RESULTS rows 39-46.
  - E10 loop text.
  - Sibling CSVs.
  - exp85a pre-submit line.
  - The c23 'READMIT/lowrefine coupling' alert (benign, R24-RC-A).
  - The c23 'ILP 0.4 does nothing' premise, now refuted: +3 safe divisions.
  - exp86 gates logged.
- **New:**
  - R24-A1..A3 pre-score blocks missed the P47 deadline.
  - R24-A7 user message due by 08:00Z.
  - The exp86c stricter gate (84 forks) + the READMIT 0.92 ban.
  - Dead cap > 8 files after P47; build only exp87a/b/i.
  - The W2b live-session need, timers lost at 05:07Z, the 429 risk.
  - Three runtime criteria.
  - The exp87m V6 0.901 omission.
  - The synthetic-author correction.
- **Carried over:**
  - Finals draft R23-A10 (+ knob-file caveat).
  - W230 CI caveat.
  - W231 residue.
  - Missing CONTEXT lines R22-A9 / R23-A8 / R20-A13 (+ R24-A10).
  - RESULTS rows (now P47-P50).
  - Round REPORT.md + commit.
  - Orphan I-233.
- **Curator disagreements settled here:**
  - exp86c: [now] (watch) vs [today] -> [today].
  - User message: [now] vs [today] -> [now].
  - Pre-score blocks: [now] in all three.

## 25 - 2026-09-28 ~11:10 UTC (curation 25; git HEAD 74caff9 = origin/main + untracked `research/wf_ideas_v4/round25/` (no REPORT.md), `research/KNOWLEDGE/_curation/25/`, `experiments/discussions/digest_20260928T1106Z.md`)

**Sources since curation 24:**
- `CONTEXT.md` l.3539-3716, 16 entries: R24 PRE-SCORE 1/3-3/3 + W4 LIFT SPLIT 07:43 (l.3539-3597); R24-A5 BUILDS + LEDGER 07:44 (l.3598); USER ANSWERS 07:47 (l.3607); P49 READ + S1 07:54 (l.3615); KNOB ARMS 09:07 (l.3625); P48 READ 09:35 (l.3639); W2b AMENDMENT A 09:35 (l.3649); DUMMY GATES 10:16 (l.3659); PRIVATE HEDGE PROPOSAL 10:16 (l.3669); USER 3+2 + TICK 20:00 UTC 10:19 (l.3680); TEAMMATE GPU + DATASETS 10:45 (l.3688); MORNING CI YES 10:47 (l.3704); SCHEDULE RESTORED 10:52 (l.3709). `## 9. Literature` moved to l.3717.
- Commits f40d44b..74caff9 (13; incl. a599958 gates, b618f7b 3+2, 1b5e912/7f50382 datasets, ce23262 CI mornings, a256dcb logs + curation 24) (`git log`).
- Round 25: `research/wf_ideas_v4/round25/report.json` R25-A1..A9 (10:52Z), 5 `scan_*.json`, 18 `v_*.json`, `ci_zshift_out.json`; knob arms `research/wf_ideas_v4/knobarms_28sep/` (13 arms, v_0..v_12). New kernels: `experiments/exp87a_k2cap6_div04_ra094_ci/`, `exp87b_k2cap8_div04_ra094_ci/`, `exp87i_k2cap8_div04_ra092/`, `exp88a_k2cap6_dis225/`, `exp88b_k2cap6_tau07/`, `exp88c_k2cap6_dis175/`; `experiments/lb_poll/dataset_baseline/`.
- LB: `experiments/lb_poll/poll.log` to the 11:03:26Z header (l.22041); `ledger.md` 11:03:28Z; `experiments/lb_poll/_lb/S1_0753Z`, `S1_0934Z`.

**New LB results:** P49 exp78a (cap 8) = **0.955 '-'**, S1 fires: DIV volume closed, cap 6 optimum, BASE stays exp70g (`CONTEXT.md` l.3615-3624). P48 exp79a (exp70g + coordinject ALPHA 0.5) = **0.957 C+, UP 33 teams = NEW BEST and V_pub**, rank #153/3,968, L (9.27, 9.45] h (l.3639-3648; `ledger.md`). P50 exp85a still PENDING (L > 6.01 h). `experiments/RESULTS.md` still ends at P46.

**Ideas** (`IDEAS.md` CHANGES (25) l.153-163; `ideas.json` meta.curations[n=25], 85 records; `_curation/25/ideas.json`):
- **New I-449..I-477:** knob-arm workflow I-449; exp88a/c/b I-450/I-451/I-452; spares I-453/I-454 (unbuilt); refuted knobs I-455..I-458; knob inventory I-459; exp89 R0 CI arms I-460; R+ K-base arms I-461; deeper stacks refuted I-462; AMENDMENT A2 + '0u' I-463; W4 AMEND 4 I-464; exp75 private hedge I-465; 'B by default' refuted I-466; card v3 I-467; tick fallback I-468; 3+2 schedule I-469; teammate GPU I-470; dataset pre-push rule I-471; session cron I-472; tools/uptest.py I-473; spare exp90a I-474; 0.956-crowd attribution refuted I-475; '#38 + CI' / SEC hedge refuted I-476; R25-A6 user message I-477.
- **Status changes:** I-397/I-398/I-401/I-324 in-plan -> lb-tested; I-399/I-400/I-404/I-414/I-421/I-442 -> refuted (moot or dropped); I-300 refuted -> in-plan (user lift 07:47). Knob refutations added to I-175/I-309/I-333/I-349/I-439; z shift after CI refuted (I-029/I-041).
- **Counts c24 -> c25:** 448 -> 477; lb-tested 55 -> 59, lab-tested 24 -> 25, in-plan 108 -> 117, refuted 212 -> 227, deferred 47, open 2. Strict orphan I-233. At risk: I-425/I-434/I-436/I-437 leave; new I-451, I-460, I-463, I-464, I-465, I-468, I-473, I-474, I-477 join I-252, I-330, I-336, I-407, I-426, I-448.

**Facts and decisions** (`FACTS.md`, `DECISIONS.md` rows marked [c25]; `_curation/25/facts.json`; state 10:55Z):
- **New facts:** F-LB-22 cap curve (l.242); F-LB-23 P48 CI read (l.243); F-LB-24 LB 10:17Z (l.244); F-RUN-39 W1 latencies, CI adds 1.60-2.18 h (l.288); F-RUN-40 29 Sep submit-by arithmetic (l.289); F-RUL-20 user answers 07:47/10:19/10:47 (l.314); F-RUL-21 teammate/credential rules + pre-push check (l.315); F-MOD-44 knob arms (l.364); F-MOD-45 exp75 + exp89 plan, no ledger rule (l.365); F-MOD-46 dataset baseline (l.366); F-TRN-57 lab vs LB for cap and CI (l.428).
- **Contradictions:** resolved C-165, C-192, C-193, C-195, C-198; updated C-118, C-163, C-184, C-191, C-197, C-200; new C-201..C-209 (l.634-642): P49 latency bound; last-slot file exp83c vs exp75; exp75 NO-GO status; CI cutoff 09:30Z vs 08:45Z; exp83c runtime limit; GPU hours left; P50 '+' definition; private-hedge pair; LB team count.
- **DECISIONS.md:** §1 rows 47-50 updated + planned P51 (l.185-189), [c25] build table (l.448-459); §2 [c25] paragraph + snapshot (l.769-781; V_pub = exp79a, ticks still #37 + #38); §2h 20 new rows (l.1179-1211; logged 07:43-10:52 lines + R25 proposals marked PROPOSED); §3 7 new rule rows (l.1257-1285).

**Watchlist** (`WATCHLIST.md`; `_curation/25/watch.json`; curated ~11:00Z):
- **New:** W248-W261, T145-T156, I287-I302.
- **Done:** W235-W237 (pre-score blocks), W239 (builds), W241 (user message + answers), W238 gate lines, W243 (2) E10 trigger, W231 (b), W247 main part (cron).
- **Superseded:** W242/T106 -> W248; W234/W230/T120 -> W254 (card v3); W231 (a)/(d), T123 dead after P47/P49.

**Alerts** (`INDEX.md` TOP ALERTS, 10 after dedup):
- **Resolved since curation 24:** R24-A1..A3 pre-score blocks; R24-A7 user message; dead cap > 8 files + exp87a/b/i builds; three runtime criteria -> rule v2; P48 CI-RAN read; E10 trigger >= 0.958; lost session timers (cron restored 10:52).
- **New:** R25-A1/A2 pre-score lines unlogged before P50 terminal (~11:54Z); exp88c gate unlogged after COMPLETE; no P50/P51 wake-ups; Q2 already answered + tick-fallback not asked; CI cutoff 09:30Z vs 08:45Z; no exp89 ledger rule, uptest.py/gate_dummy.py missing, GPU ~4.5-5 h; exp75 NO-GO lift + exp86c waiver; card v3 + CI caveat (R25P-9 draft refuted); CI_lo 2.2 h model stale.
- **Carried over:** RESULTS rows (now 47-49); round REPORT.md (24-25) + commit; finals texts (now card v3); orphan I-233; curator info lines (W202/W244).
- **Curator disagreements settled here:** the user message [now] (watch) vs [today] -> [now]; the CI cutoff [today] vs [before-finals] -> [today] (must be in W4 AMEND 4 before 23:30Z).

## 26 - 2026-09-28 ~14:10 UTC (curation 26; git HEAD 5e5fd1b = origin/main + untracked `research/wf_ideas_v4/round26/` (no REPORT.md), `research/KNOWLEDGE/_curation/26/`, `experiments/discussions/digest_20260928T1338Z.md`, `experiments/e10_watch/20260928T1318Z.txt`, `1322Z.txt`)

**Trigger:** the user asked "ресерчеры активны?". Answer: yes. LB poller header 14:04:10Z (`experiments/lb_poll/poll.log` l.23139), E10 watch RUN 25 13:22Z with 0 signals (`experiments/e10_watch/watch_loop.log`), discussion feed 13:38Z with nothing new (`experiments/discussions/feed_loop.log`), round 26 done 13:50Z (`research/wf_ideas_v4/round26/report.json`); next rounds 15:17 / 17:47 / 20:17Z (18:17 / 20:47 / 23:17 MSK) (R26-A6).

**Sources since curation 25:**
- `CONTEXT.md` l.3717-3923, 15 entries: A2 + P50/P51 read rule and W4 AMEND 4 11:17 (l.3717, l.3753); exp88c gate + exp86c waiver (l.3794); exp75 line (l.3810); exp88c PASS, exp89a/e, ledger, uptest 11:19 (l.3824); Q3 YES 11:26 (l.3834); fallback tick allowed 11:27, blocked 11:28 (l.3842-3855); P50 read + P51 submit 12:16 (l.3856, l.3863); R+ night list 12:17 (l.3871); RISK STACK 12:23 (l.3885); user confirmed night + standing override 12:25 (l.3899); exp89p PASS 12:40 (l.3908); exp89q/r PASS 13:14 (l.3915). `## 9. Literature` moved to l.3924.
- Commits 74caff9..5e5fd1b (12, a04ab40 first) (`git log`). Round 26: `research/wf_ideas_v4/round26/report.json` R26-A1..A7, 5 `scan_*.json`, 13 `v_*.json`. New kernels: `experiments/exp89a_k2cap6_ci_dis225/`, `exp89e_k2cap6_k_dis175/`, `exp89p_k2cap6_k_sec/`, `exp89q_k2cap6_k_sec_dis225/`, `exp89r_k2cap6_k_sec_dis225_ci/`; new tool `tools/uptest.py`; LB snapshot `experiments/lb_poll/_lb/S1_1214Z`.

**New LB results:** P50 exp85a (exp70g + ILP_DIVISION_WEIGHT 0.4 + READMIT 0.94 = K) = **0.958 R+, UP 21 teams, rank 134 of 3,969 = NEW BEST and V_pub (non-CI)**; E10 trigger raised to >= 0.959 (`CONTEXT.md` l.3856-3862; `FACTS.md` F-LB-25). P51 exp87a (K + CI, 56640366) submitted 12:14:57Z, PENDING at 14:04:10Z (l.3863; `poll.log` l.23142). 28 Sep slots 5/5 used. `experiments/RESULTS.md` still ends at P46.

**Ideas** (`IDEAS.md` CHANGES (26) l.169-179; `ideas.json` meta.curations[n=26], 71 records; `_curation/26/ideas.json`):
- **New I-478..I-496:** risk stack exp89q/r I-478; exp89p I-479; R8 coverage extension I-480; MORNING TABLE v1.1 I-481 (v1 refuted I-482); depth-cap supersede I-483; exp89s I-484; exp89l I-485; exp89t on a user yes I-486; exp89u / pair D refuted I-487; user message R26-A6 I-488; freeze-line codes I-489; masking relaxation I-490; night hygiene I-491; finals pool + PENDING branch I-492; V_pub rule v4 refuted I-493; EXP75 PARTNER RULE v2 I-494; card v4 I-495 (supersedes I-467); dummy-clip GT lab I-496.
- **Status changes:** I-431/I-139 in-plan -> lb-tested; I-330/I-435/I-450/I-451/I-452/I-460/I-461/I-467/I-468/I-474 in-plan -> refuted (answered, moot or superseded). Closed: ILP < 0.4 (I-049), READMIT 0.92/0.90 (I-139), TAU 0.7, DIS 1.75, exp86c on M2, 'B recommended at 0.954' (I-466).
- **Counts c25 -> c26:** 477 -> 496; lb-tested 59 -> 61, lab-tested 25 -> 26, in-plan 117 -> 120, refuted 227 -> 240, deferred 47, open 2. Strict orphan I-233. At risk: I-330, I-426, I-451, I-460, I-463, I-464, I-465, I-468, I-473, I-474, I-477 leave; I-480, I-481, I-483, I-484, I-485, I-488..I-492, I-494 join I-252, I-336, I-407, I-448.

**Facts and decisions** (`FACTS.md`, `DECISIONS.md` rows marked [c26]; `_curation/26/facts.json`; state 13:55Z):
- **New facts:** F-LB-25 K read 0.958 (l.246); F-LB-26 LB 13:18Z (l.247); F-RUN-41 dummy runtimes, DIS 2.25 +15-20% (l.293); F-RUL-22 finals ticking is manual only (l.320); F-MOD-47 night builds + gates (l.372); F-MOD-48 round-26 dry-run builds exp89s/t/u/l (l.373); F-TRN-58 levers closed after P50 (l.436). [c26] notes on F-MET-04, F-DAT-06/13, F-LB-01/02/10/17, F-RUN-37/39/40, F-RUL-05/19/20, F-MOD-44/45, F-TRN-57.
- **Contradictions:** resolved C-191, C-200, C-202, C-203, C-204, C-207; updated C-118, C-163, C-184, C-197, C-206, C-208, C-209; new C-210..C-218 (l.651-659): P50 latency bound; depth cap vs exp89r; void morning rule; R8 coverage gap; MASKED overlap; night list re-cut after P50; exp75 partner rule; V_pub tie order; stale KEY FACTS.
- **DECISIONS.md:** §1 P50/P51 updated + planned P52-P54 (l.189-193), [c26] build table (l.472); §2 [c26] paragraph + snapshot (l.809-811; V_pub = exp85a, ticks still #37 + #38); §2f E10 >= 0.959 + standing override (l.1093); §2h 10 appends + 14 rows (l.1256-1269; R26-A1..A7 marked PROPOSED); §3 7 appends + 9 rule rows.

**Watchlist** (`WATCHLIST.md`; `_curation/26/watch.json`; curated ~14:05Z):
- **New:** W262-W270, T157-T164, I303-I314.
- **Done:** W248, W249, W250 (a)(b), W251, W252 (a), W255 (a)(b)(e), W253 (c)(d)(e), W260 (08:45Z cutoff), W258 (moot), T145, T146.
- **Superseded:** R0/R-/R? night branch, exp89e, exp86c night slot, old M1/M2 lists; W256 exp90a moot; W254 card v3 -> W266 (card v4); T154 -> T162 (notify-only); I289 -> I310.

**Alerts** (`INDEX.md` TOP ALERTS, 9 after dedup):
- **Resolved since curation 25:** R25-A1/A2 pre-score lines; exp88c gate; P50/P51 wake-ups (P50 read 12:16); R25-A6 questions (Q2 dropped, Q3 yes, tick fallback answered then blocked); CI cutoff 09:30Z vs 08:45Z (08:45Z adopted); exp89 ledger rule + uptest.py; exp75 NO-GO lift; exp86c waiver (slot then moot).
- **New:** user reply R26-A6 [now]; R8 coverage for exp89p/q/r [now]; exp89s build + GPU read + ledger 't' [now]; depth cap vs exp89r + void morning rule [today]; P51-dependent freeze codes + masking [today]; exp75 partner rule v2 before 00:06Z [today]; missing cron jobs (17:57Z, 19:30Z, final snapshot) [today]; card v4 + single-embryo caveat + 743006 host note [before-finals].
- **Carried over:** RESULTS rows (now 47-50); REPORT.md (rounds 24-26) + round26/ untracked; stale KEY FACTS / e10_watch_loop.py docstring (C-163, C-218); orphan I-233.
- **Curator disagreements settled here:** depth cap [today] (ideas, watch) vs [before-finals] (facts) -> [today], since exp89l may be built at P51's read; R26-A1 coverage [today] (facts) vs [now] (watch) -> [now].

## 27 - 2026-09-28 ~16:40 UTC (curation 27; git HEAD da5ce54 = 756c513 (round 27 committed) + 00e2603 (laptop on AC) + da5ce54 (hedge pair agreed); uncommitted `research/KNOWLEDGE/*` curation-27 edits, `experiments/lb_poll/ledger.md`, `poll.log`)

**Sources since curation 26:**
- `CONTEXT.md` l.3924-4050, 13 entries: R8 COVERAGE night files 14:12 (l.3924); MORNING TABLE v1.1 (l.3931); exp89s built + gate (l.3956); EXP75 PARTNER RULE v2 (l.3965); exp89s PASS 14:40 (l.3974); OPS outage + user defaults 15:43 (l.3979); API LOAD CUT 15:57 (l.3988); standby CORRECTION 16:26 (l.3999); GAP RULE v2 (l.4009); DIS runtime = sibling (l.4021); card v4 stored + R27 facts (l.4029); laptop ON AC 16:30 (l.4035); 743929 comment + user agrees with the hedge pair 16:32 (l.4041). `## 9. Literature` moved to l.4051.
- Commits dba59bd, eea3793, 7faa8cf, 608d950, 756c513, 00e2603, da5ce54 (`git log`). Round 27: `research/wf_ideas_v4/round27/report.json` R27-A1..A9 (16:20Z), `finals_card_v4_ru.md`, 5 `scan_*.json`, 13 `v_*.json` (no REPORT.md; the harness refused the write). New kernel: `experiments/exp89s_k2cap6_k_dis225/`.

**LB:** no new score. P51 exp87a (K + CI, 56640366) PENDING at the 16:32:08Z header (`experiments/lb_poll/poll.log` l.23871-23874); read earliest ~20:50Z. Rank 138 of 3,968 at 15:43Z (was 134), 124 teams >= 0.959; E10 null (`CONTEXT.md` l.4029-4034; `FACTS.md` F-LB-27). `experiments/RESULTS.md` still ends at P46 (l.79).

**Ideas** (`IDEAS.md` CHANGES (27) l.181; `ideas.json` meta.curations[n=27], 55 records; `_curation/27/ideas.json`):
- **New I-497..I-509:** power watchdog I-497; keep-awake question I-498; exp89p 00:07Z question I-499; GAP RULE v2 I-500; RULE v2.1 compute gate I-501; 'DIS dummies +15-20%' refuted I-502; 23:30Z freeze line + LATE rule I-503; 00:04Z checklist + nb_try + backup crons I-504; tight-poll loop refuted I-505; exp89s in exp75's slot refuted I-506; submit at the decision header I-507; Q3 conditional П1 line I-508; MIN_TRACK_LEN as a DIS anchor refuted I-509.
- **Status changes:** I-486 (exp89t) in-plan -> refuted (user default no, `CONTEXT.md` l.3979-3987). Logged (status kept in-plan): I-480, I-481, I-483, I-484 (PASS 14:40Z), I-494, I-497, I-500; I-495 card stored. I-309 DET revisit clause void.
- **Counts c26 -> c27:** 496 -> 509; lb-tested 61, lab-tested 26, in-plan 120 -> 128, refuted 240 -> 245, deferred 47, open 2. Strict orphan I-233. At risk: I-480, I-481, I-483, I-484, I-488, I-489, I-494 leave; I-501, I-503, I-504, I-507, I-508 join I-485, I-490, I-491, I-492, I-252, I-336, I-407, I-448.

**Facts and decisions** (`FACTS.md`, `DECISIONS.md` rows marked [c27]; `_curation/27/facts.json`; state 16:20Z):
- **New facts:** F-LB-27 LB 15:43Z (l.249); F-RUN-42 setup vs compute, DIS runtime = sibling (l.296); F-RUN-43 poll gaps + loop restart (l.297); F-RUN-44 lid standby on battery (l.298); F-RUL-23 ban report + API-load cut (l.326); F-MOD-49 exp89s (l.380); F-MOD-50 night readiness audit, nb_try 'limit' hole (l.381); F-TRN-59 DET closed, RC-A refuted (l.445). F-RUN-41's DIS +15-20% part retracted.
- **Contradictions:** resolved C-211, C-212, C-213, C-216; updated C-118, C-163, C-206, C-209, C-214, C-218; new C-219..C-228 (l.669-678): outage cause; DIS runtime; CI gap rule; exp89p time; Q3 vs card П1; card v4 defects; submit-failure handling; missing late re-check; GPU quota total; morning submit timing. C-219, C-220, C-221 are now closed by `CONTEXT.md` l.3999-4028.
- **DECISIONS.md:** §1 P55-P56 morning row (l.195) + [c27] build table (l.490-492); §2 [c27] paragraph + snapshot (l.842-844); §2f E10 (l.1128); §2h 15 rows (l.1305-1319; R27-A1..A9 marked PROPOSED); §3 7 rule rows (l.1403 ff.). The 16:32Z hedge-pair agreement (`CONTEXT.md` l.4041-4050) landed after the facts curator and is not yet in DECISIONS.

**Watchlist** (`WATCHLIST.md`; `_curation/27/watch.json`; curated ~16:25Z): new W271-W280, T164-T170, I315-I326; I306 ('DIS dummies slower') retired; the 15:17Z round was lost to standby.

**Alerts** (`INDEX.md` TOP ALERTS, 10 after dedup):
- **Resolved since curation 26:** R26-A6 user message (defaults applied); R8 coverage for exp89p/q/r; depth cap + void morning rule (MORNING TABLE v1.1); exp89s build + ledger 't'; exp75 partner rule v2; the outage-cause contradiction; GAP RULE v2 (logged before P51's read); DIS runtime fact; card-v4-stored line; power (on AC 16:29Z, `CONTEXT.md` l.4035-4040); round 27 committed (756c513).
- **New:** RULE v2.1 before exp89l [today]; freeze line + night checklist + backup crons + failed-submit rule [today]; nb_try 'limit' hole [today]; R27-A6 questions [today]; card v4 defects + Q3 П1 + V_pub re-check in 58b6ded3 + decision-header submit + DET line [before-finals]; GPU API vs Settings [info]; no new Kaggle loops [info]; 0.956 wave below P2 threshold [info].
- **Carried over:** MASKED coded '0' (I-490) [today]; RESULTS rows P47-P50; REPORT.md rounds 24-27; KEY FACTS for round 28; missing 17:57Z tick check + 23:00-23:45Z LB snapshot; orphan I-233.
- **Curator disagreements settled here:** power [now] (all three curators, written before 16:29Z) -> [today] watch item, since `CONTEXT.md` l.4035 logs AC; night hardening [before-finals] (facts) vs [today] (ideas, watch) -> [today], since it is due at the 23:30Z freeze.

## 28 - 2026-09-28 ~20:27 UTC (curation 28; git HEAD e42769c = da5ce54 + 266389e, f22bcae, 0fef1f4, e45bef0, 9bcd86f, d150eec, f05e678, e42769c (round 28 committed); uncommitted `research/KNOWLEDGE/*` curation-28 edits, `experiments/lb_poll/ledger.md`, `poll.log`; untracked `research/wf_ideas_v4/round29/` (running), `experiments/e10_watch/20260928T2018Z.txt`)

**Trigger:** the user asked "какой статус" after the chat claimed the 20:47 MSK round was lost to the battery. Answer from the sources: P51 still PENDING (`experiments/lb_poll/poll.log` l.25274, 20:23:04Z); 31 background waiters alive at 20:26Z (22:47Z round .. 30 Sep 00:07Z; Win32_Process read, `_curation/28/index.notes.md`); the round was lost to the cron defect, not the battery (`research/wf_ideas_v4/round28/report.json` R28-A1 (3); `CONTEXT.md` l.4127-4133).

**Sources since curation 27:**
- `CONTEXT.md` l.4051-4133, 8 entries: round-27 remainder 16:38 (l.4051); 744093 float centroids 16:39 (l.4059); travel window + post-wake check 16:43 (l.4066); ideas + discussions sweep 20:00 (l.4073); AUTONOMOUS MODE 20:07 (l.4081); background timers 20:13 (l.4094); RULE v2.1 + exp89l gate + no-freeze fallback + G4 20:18 (l.4104); crons never fire -> waiters 20:18 (l.4127). `## 9. Literature` moved to l.4134.
- Commits 266389e..e42769c (8) (`git log`). Round 28: `research/wf_ideas_v4/round28/REPORT.md` + `report.json` R28-A1..A6 (20:05Z), 4 `scan_*.json`, 8 `v_*.json`. Sweep: `research/wf_ideas_v4/ideas_29sep/` (3 mine files, rank.json, v_0..v_15). No new kernel.

**LB:** no new score. P51 exp87a (K + CI, 56640366) PENDING at 20:23:04Z; expected ~21:31-21:42Z; admit edge 10.75 h = 22:59:57Z. Rank #139 of 3,973 at 19:36Z (was 138); E10 null (best public 0.953) (`FACTS.md` F-LB-28 l.251). `experiments/RESULTS.md` still ends at P46 (l.79).

**Ideas** (`IDEAS.md` CHANGES (28) l.192; `ideas.json` meta.curations[n=28], 62 records; `_curation/28/ideas.json`):
- **New I-510..I-521:** waiters I-510 (logged); no-freeze fallback I-511 (logged); SEC dummy-lab info line I-512; truncation calibration / floatout anchor void I-516; post-wake check I-517; refuted: CI prior cut I-513, SEC swap tonight I-514, G3 false NETWORK I-515, LEARNED_BONUS 0.75 I-518, max_neighbors I-519, dt=2 fork I-520, third-child fork I-521. IB29 re-proposals folded into I-029, I-454, I-183, I-333, I-331, I-384, I-440, I-175, I-222, I-441.
- **Status changes:** I-498 (keep-awake, default no), I-499 (exp89p 00:07Z, default 00:46Z), I-472 (session-cron schedule) in-plan -> refuted. I-501 (RULE v2.1) logged at l.4104.
- **Counts c27 -> c28:** 509 -> 521; lb-tested 61, lab-tested 26 -> 28, in-plan 128, refuted 245 -> 255, deferred 47, open 2. Strict orphan I-233; at risk now includes I-495 (card), I-510, I-511, I-516.

**Facts and decisions** (`FACTS.md`, `DECISIONS.md` rows marked [c28]; `_curation/28/facts.json`; state 20:24Z):
- **New facts:** F-LB-28 LB 19:36Z (l.251); F-RUN-45 crons never fire, timers replace them (l.301); F-RUL-24 autonomous mode (l.330); F-TRN-60 round-28 lab reads + empty sweep (l.450). [c28] notes on F-LB-01/02/10, F-MET-10, F-RUN-39/42/43/44, F-RUL-05/20/22, F-MOD-50, F-TRN-58.
- **Contradictions:** resolved C-219, C-220, C-221, C-226 (and new C-229, C-232, C-233, C-235, C-236 by the 20:13/20:18 entries); updated C-118, C-209, C-214, C-218, C-222..C-225, C-227, C-228; open new: C-230 card v4 lacks edits, C-231/C-237 battery vs cron cause, C-234 admit edge + freeze item (5), C-238 exp89p timer 00:44Z vs T54 (l.684-693).
- **DECISIONS.md:** §1 P51-P56 updated + [c28] build table (l.502-504); §2 [c28] paragraph + snapshot (l.874-876); §2f E10 (l.1162); §2h rows l.1354-1370 (R28-A1..A6: A1, A2 LOGGED, A3-A6 PROPOSED); §3 11 rule rows (l.1461-1471).

**Watchlist** (`WATCHLIST.md`; `_curation/28/watch.json`; curated ~20:15Z): new W281-W288, T171-T174, I327-I337; W270 and the cron parts of W276/W277/T166 superseded by W281; W282 and W288 were written before the 20:18Z entries and are now done (`CONTEXT.md` l.4104-4133).

**Alerts** (`INDEX.md` TOP ALERTS, 9 after dedup):
- **Resolved since curation 27:** RULE v2.1 compute gate (I-501) + exp89l gate + no-freeze fallback + G4, logged pre-score; timers armed for freeze, batch, backups, morning, finals and hourly rounds; R27-A6 questions (defaults: no keep-awake, exp89p 00:46Z); backup crons + V_pub re-check in 64b9bb56; power on AC; 744093 no impact.
- **New:** user correction 'not the battery' + keep VS Code open [now]; exp89p 00:44Z timer vs T54 [today]; waiter fragility + standby on AC [today]; card v4 stated-but-missing edits (C-230) [before-finals]; R28-A6 lines + runbook l.66 [today].
- **Carried over:** freeze text (now R27-A4 + R28-A4, incl. nb_try 'limit' hole, guarded T54, masking) [today]; P51 read + branch + exp89l [today]; RESULTS rows P47-P51; finals still #37 + #38; GPU API vs Settings; orphan I-233. REPORT.md for rounds 24-27 still missing (round 28 has one).
- **Curator disagreements settled here:** waiters [now] (watch, ~20:15Z) -> [today] maintenance, since 31 waiters are alive at 20:26Z; RESULTS rows [before-finals] (watch) vs [today] (ideas, facts) -> [today].

## 29 - 2026-09-28 ~21:10 UTC (curation 29; git HEAD e42769c unchanged; uncommitted `research/KNOWLEDGE/*` curation-28/29 edits, `experiments/lb_poll/ledger.md`, `poll.log`, E10/feed logs; untracked `research/wf_ideas_v4/round29/` (no REPORT.md), `experiments/e10_watch/20260928T2018Z.txt`, `20260928T2041Z.txt`, `experiments/discussions/digest_20260928T2027Z.md`)

**Sources since curation 28:** no new `CONTEXT.md` entry (4,154 lines, last entry 20:18Z l.4127, `## 9. Literature` l.4134) and no commit (`git log`). New: round 29 `research/wf_ideas_v4/round29/report.json` (R29-A1..A8, new_facts, plan_issues, rejected, next_focus, report_md_ru; written 20:52-20:55Z), `report.notes.md` ('R29-A1 exact snippets', mocks 20:47-20:50Z), 5 `scan_*.json`, 13 `v_*.json`, and three stored texts: `night_checklist.md` (075152c4), `freeze_line_template.md` (c675d7c3), `finals_card_v5_ru.md` (aadead83) (sha256 read 21:08Z). REPORT.md was not written (harness blocked; `report.json` report_md_ru_note).

**LB:** no new score. P51 exp87a (56640366) PENDING at the 21:03:12Z header, L > 8.80 h; read expected ~21:31-21:42Z; admit iff first COMPLETE header + 210 s x failed attempts <= 22:59:57Z (`experiments/lb_poll/poll.log` l.25518; `experiments/lb_poll/ledger.md`). Rank #140 of 3,974 at 20:41Z (was #139 of 3,973), 127 teams >= 0.959; E10 RUN 31/32 null, feed digest 20:27Z null (`FACTS.md` F-LB-29; `experiments/e10_watch/watch_loop.log`). `experiments/RESULTS.md` still ends at P46 (l.79).

**Ideas** (`IDEAS.md` CHANGES (29) l.193; `ideas.json` meta.curations[n=29], 45 records; `_curation/29/ideas.json`):
- **New I-522..I-534:** in-plan I-522 fail-closed nb_try/G2/T54 parsers + never-empty T54, I-523 nb_try v3 order, I-524 one stored night text + CONTEXT pointer, I-525 UTC clock rule, I-526 finals card v5, I-527 MORNING TABLE A-M2 precedence, I-528 P UP test + E10 converter, I-529 late-read watchers, I-530 free session overnight, I-531 E10 displacement cost; refuted I-532 (R29-RC-B card line), I-533 (R29-RC-C geometry-hedge text), I-534 (R29-RC-A class table; only the '~1/6 is one lever, not a law' note kept, on I-320).
- **Updated (~30):** I-485/I-445 exp89l built at 51's read with a v2.1-specific gate; I-500/I-511/I-463 admit-slack sign inverted; I-501 RULE v2.1 anchors coincide; I-503/I-504/I-490/I-491/I-479/I-465/I-507/I-508/I-512 now carried by the stored template/checklist; I-510/I-517/I-388 waiter texts stale; I-495 superseded by I-526; I-232 round29 REPORT.md blocked.
- **Counts c28 -> c29:** 521 -> 534; in-plan 128 -> 138, refuted 255 -> 258; others unchanged (lb-tested 61, lab-tested 28, deferred 47, open 2). No old ID changed kind. Strict orphan I-233; at risk +I-522, I-524, I-526, I-527, I-529; I-495, I-492 off (`IDEAS.md` ORPHANS l.861).

**Facts and decisions** (`FACTS.md`, `DECISIONS.md` rows marked [c29]; `_curation/29/facts.json`; state 21:02Z):
- **New facts:** F-LB-29 LB 20:41Z (l.253); F-RUN-46 stale waiter texts + PowerShell 'Get-Date -Format u' = MSK with 'Z' (l.304); F-RUL-25 kaggle 2.2.4 output (stdout version warning, no 'Successfully submitted', 429 text) (l.334); F-TRN-61 '~1/6' is one lever, not a law (l.455). [c29] notes on F-LB-01/02/10, F-MET-10, F-RUN-39/42/43/45, F-RUL-22, F-MOD-50, F-TRN-58.
- **Contradictions:** updated C-118, C-209, C-225, C-230, C-232, C-238; new open C-239 vacuous G4 -F grep, C-240 batch-text pointer (l.4054), C-241 success string, C-242 fail-open parsers, C-243 admit-slack sign, C-244 MORNING TABLE A-M2, C-245 freeze item (9) tie wording, C-246 card v4 pairs vs partner rule v2, C-247 exp89l build time, C-248 gate85.py unsuitable, C-249 01:30Z 'CI only' text (l.699-709).
- **DECISIONS.md:** §1 [c29] appends P51-P56 + build table (l.514-516); §2 [c29] finals snapshot 21:00Z (l.905-907; TICKED #37 + #38, V_pub exp85a); §2f E10 note (l.1195); §2h rows R29-A1..A8, all PROPOSED (l.1404-1411); §3 R5/R8/§f notes + 2 rows (l.1513-1514).

**Watchlist** (`WATCHLIST.md`, curated ~20:58Z; `_curation/29/watch.json`): done W281 (1)(2), W282, W288, W285 content (as card v5); reopened W282 (c) admit sign -> I345/W289, W282 (d) G4 -F -> W290, W281 (3) battery wording -> W297; new W289-W297, T177-T180, I338-I348 (l.50-62, l.68, l.82, l.129).

**Alerts** (`INDEX.md` TOP ALERTS, 10 after dedup):
- **Resolved since curation 28:** the freeze text, night checklist and card fixes now exist as stored files (round 29); I-495/I-492 absorbed by card v5; the waiter set is intact (31 alive, round 29 new_facts 9).
- **New:** fail-open parsers + empty T54 (R29-A1) [now]; no CONTEXT pointer + vacuous G4 (R29-A2) [now]; MORNING TABLE A-M2 contradiction [now]; admit-slack sign inverted + exp89l dummy AT the read, not gate85.py [now]; round 30 must be skipped or short, no round 23:25Z-~00:50Z (R29-A5) [now]; freeze item (9) tie wording + PowerShell UTC trap [today]; round29/REPORT.md missing, late-read watchers, S0/S1 for P [before-finals]; '~1/6' annotation + weak division transfer across lab embryos [info].
- **Carried over:** P51 read; 23:33Z freeze (now from the template, after R29-A1); card v4 stated-but-missing edits (C-230, now also no banner and opened by the 12:03Z waiter); 'not the battery' user message; RESULTS rows P47-P51; runbook l.66; W279 (1) DET_THRESHOLD line; R28-A6 lines; orphan I-233; finals still #37 + #38.
- **Curator disagreements settled here:** A-M2 conflict ideas [now] vs facts [today] -> [now] (rides in the R29-A2 entry); battery correction watch [info] vs ideas [today] -> [today]; card v4 facts [before-finals] vs ideas [today] -> [today]; RESULTS rows [today] (c28 INDEX) -> [before-finals] (all three curators).

## 30 - 2026-09-29 ~02:00 UTC (curation 30; git HEAD afebb5d = e42769c + 6dc7088 (round 29), a9c6d41 (P51 = 0.959), f156067 (exp89l gate PASS), ca8f729, 59b1cf5 (W4 freeze), 775d484, afebb5d (night batch); uncommitted `research/KNOWLEDGE/*` curation-30 edits, `experiments/lb_poll/ledger.md`, `poll.log`, E10/feed logs; untracked `research/wf_ideas_v4/round30/` (no REPORT.md), `experiments/e10_watch/20260929T0113Z.txt`, `20260929T0141Z.txt`, `experiments/discussions/digest_20260929T0057Z.md`)

**Sources since curation 29:** 7 commits (`git log e42769c..afebb5d`); `CONTEXT.md` 4,154 -> 4,293 lines, 7 new entries l.4134-4272 (21:11Z pointer + card v5 + A-M2 precedence; 21:45Z P51 read; 21:45Z exp89l build; 22:16Z exp89l gate PASS; 23:34Z W4 FREEZE; 00:06Z / 00:47Z night batch), `## 9. Literature` l.4273. Round 30 `research/wf_ideas_v4/round30/report.json` (R30-A1..A5, new_facts, plan_issues, rejected, next_focus, report_md_ru; 01:44Z), 4 `scan_*.json`, 9 `v_*.json`. Ledger 01:54:06Z; E10 RUN 33-37 (null); digest 00:57Z (null). `experiments/RESULTS.md` unchanged (ends at P46, l.79).

**LB:** P51 exp87a (K + CI, 56640366) = **0.959 = NEW BEST**, read 21:43:19Z, '+' vs exp85a, UP 12, L (9.30, 9.48] h ADMIT; V_pub = exp87a (CI); branch A; E10 trigger -> >= 0.960 (`CONTEXT.md` l.4153-4160). Night: P52 exp89r 56656147 (00:05:28Z), P53 exp75 56656157 (00:05:34Z), P54 exp89p 56657612 (00:46:36Z), all PENDING at 01:54:04Z; 2 submits left (`CONTEXT.md` l.4254-4272; `experiments/lb_poll/ledger.md`). Rank #132 of 3,979 at 01:42Z (`experiments/e10_watch/20260929T0141Z.txt`).

**Ideas** (`IDEAS.md` CHANGES (30) l.198; `ideas.json` meta.curations[n=30], 57 records; `_curation/30/ideas.json`):
- **New I-535..I-542:** in-plan I-535 running-champion tie order, I-536 A-M1 from exp89p's display alone ('0u' unreachable), I-537 A-M2 SEC/Rr cell -> UNUSED, I-538 07:23Z prep + morning command block (no rebuild), I-539 card v5 info lines, I-540 MSK brief + 'pair by the card' wording; refuted I-541 (disclosure harvest / dataset-watch build trigger, R30-RC-C), I-542 (re-submit a file to win the tie order).
- **Status move:** I-438 in-plan -> lb-tested (P51 = 0.959). Logged/applied since c29: I-522..I-527, I-530 (21:11Z), I-485/I-501/I-445/I-480 (exp89l PASS), I-503/I-490/I-507/I-508/I-512/I-531 (freeze), I-478/I-465/I-479/I-504/I-491 (night batch).
- **Updated:** I-528/I-490/I-473 UP-test protocol (R30-A3); I-497/I-529/I-517 one-shot watchers; I-510 stale timer texts; I-388/I-530 short rounds 31-35; I-232 round29/30 REPORT.md missing; I-364/I-446 E10 trigger 0.960.
- **Counts c29 -> c30:** 534 -> 542; lb-tested 61 -> 62, in-plan 138 -> 143, refuted 258 -> 260; lab-tested 28, deferred 47, open 2 unchanged. At-risk 16 -> 13 (9 off, I-535..I-540 on); strict orphan I-233 (`IDEAS.md` ORPHANS l.875).

**Facts and decisions** (`FACTS.md`, `DECISIONS.md` rows marked [c30]; `_curation/30/facts.json`; state 01:50Z):
- **New facts:** F-LB-30 P51 read + LB (l.255); F-RUN-47 night execution (l.307); F-RUL-26 LB row mechanics, '0u' unreachable (l.338); F-MOD-51 exp89l + code-path audit (l.394); F-TRN-62 CI transfer and deadlines (l.461). [c30] notes on 13 rows.
- **Contradictions:** C-118, C-209, C-225, C-230, C-238..C-249 updated (most RESOLVED or MOOT); new C-250 tie order, C-251 A-M2 SEC/Rr cell, C-252 stale '0u' / 'V_pub stays exp85a', C-253 UP count rule masks exp89r, C-254 'recommended' wording, C-255 card v5 placeholders, C-256 RC-B overclaim, C-257 RC-C refuted, C-258 morning time wording (l.716-724).
- **DECISIONS.md:** §1 P51 SCORED, P52-P54 SUBMITTED, P55-P56 branch A (l.194-198); [c30] build table (l.525-527); §2 finals snapshot 01:50Z (l.940-955); §2f E10 line (l.1232); §2h R29-A1..A8 statuses + rows R30-A1..A5, all PROPOSED (l.1441-1453); §3 [c30] notes + 5 rows.

**Watchlist** (`WATCHLIST.md`, curated ~01:57Z; `_curation/30/watch.json`): done W289, W290 and the P51/freeze/night items (l.44-64); new W298-W303, T181-T186, I349-I357; I338-I343, I345, I346 resolved, I348 moot; still open W126, W279 (1), W286 (2), W296/W303, W297 (l.68-77).

**Alerts** (`INDEX.md` TOP ALERTS, 11 after dedup):
- **Resolved since curation 29:** fail-open parsers + CONTEXT pointer + vacuous G4 (R29-A1/A2, logged 21:11Z); MORNING TABLE A-M2 precedence logged (21:11Z (6)); card v4 banner; P51 read; exp89l dummy PASS; freeze 23:34Z; night batch with no duplicate; 'keep the session free' (night ran).
- **New:** R30-A1 pre-score entry (tie order, '0u' unreachable, A-M2 cell) [now]; E10 runbook l.66 trigger 0.958 -> 0.960 [now]; card v5 stale lines + info lines [today]; 07:23Z prep-only, no rebuild [today]; one-shot watchers, re-arm 06:07Z [today]; UP-test count-rule masking (R30-A3) [today]; 'pair by the card' wording + MSK brief [before-finals]; CI deadline degrade not provable, RC-C refuted [info].
- **Carried over:** RESULTS rows (now P47-P51 + P52-P54); REPORT.md for round 29 and now round 30; W279 (1) DET_THRESHOLD line; W297 battery correction (folded into the R30-A1 entry); orphans I-233, I-336, I-516, I-448, I-252, I-407; finals still #37 + #38.
- **Curator disagreements settled here:** card v5 edits ideas [today] / facts [before-finals] / watch [now, inside W298] -> [today] with the 12:03Z fill as hard limit; RESULTS rows facts [before-finals] vs ideas/watch [today] -> [today]; tie order and A-M2 cell ideas/watch [now] vs facts [today] -> [now] (one entry, hard limit 07:38Z).

## 31 - 2026-09-29 ~02:55 UTC (curation 31; git HEAD d6deab5 = afebb5d + d6deab5 (round 30 committed, 02:02Z entry, card v5 edits); uncommitted `research/KNOWLEDGE/*` curation-31 edits, `experiments/lb_poll/ledger.md`, `poll.log`, E10/feed logs; untracked `research/wf_ideas_v4/round31/` (no REPORT.md), `experiments/e10_watch/20260929T0213Z.txt`, `20260929T0241Z.txt`, `experiments/discussions/digest_20260929T0227Z.md`, `experiments/lb_poll/_night_subs.csv`)

**Sources since curation 30:** 1 commit (`git log afebb5d..d6deab5`); `CONTEXT.md` 4,293 -> 4,314 lines, 1 new entry 02:02Z MORNING/FINALS TEXT RESOLUTIONS l.4273-4293, `## 9. Literature` l.4294; card v5 sha8 aadead83 -> aab8801a (`git diff afebb5d..d6deab5 -- research/wf_ideas_v4/round29/finals_card_v5_ru.md`). Round 31 `research/wf_ideas_v4/round31/report.json` (R31-A1..A5, new_facts, plan_issues, rejected, next_focus; 02:38Z), 4 `scan_*.json`, 7 `v_*.json`. Ledger 02:34Z; E10 0213Z/0241Z (null); digest 02:27Z (null). `experiments/RESULTS.md` unchanged (ends at P46).

**LB:** no new score; P52 exp89r, P53 exp75, P54 exp89p PENDING at the 02:44:13Z header (`experiments/lb_poll/poll.log` l.27644). Rank #132 of 3,979 at 02:14Z / 02:42Z, 17th of 21 in the 0.959 block; medal lines up one block (bronze ~#398 in 0.955, silver ~#199 in 0.957) (`FACTS.md` F-LB-31 l.257).

**Ideas** (`IDEAS.md` CHANGES (31) l.200; `ideas.json` meta.curations[n=31], 37 records; `_curation/31/ideas.json`):
- **New I-543..I-549:** in-plan I-543 A-M2 function (Rr '+' restored), I-544 08:40Z header + manual list, I-545 card pool non-CI L_hi <= 9.0 h, I-546 04:13Z wake push + battery-tolerant watchdog, I-547 read-time latency log, I-548 card fill numbers for V_pub exp87a; refuted I-549 ('не медаль' scenario sentence, R31P-2).
- **Logged since c30 (02:02Z):** I-535 (conservative running champion), I-536 (A-M1 from P's display), I-537 (SEC/Rr -> UNUSED), I-538 (no rebuild), I-540/I-481 wording; card v5 edits (I-526).
- **Updated (30 records):** I-530 round schedule never logged -> at risk; I-045 WEAKENED on public by CI, stays closed (R31-A5); I-526/I-539 card gaps; I-497 battery-tolerant watchdog; I-528, I-529, I-089, I-092, I-494.
- **Counts c30 -> c31:** 542 -> 549; in-plan 143 -> 149, refuted 260 -> 261; lb-tested 62, lab-tested 28, deferred 47, open 2 unchanged. At-risk 13 -> 15 (off I-535..I-538; on I-530, I-543..I-546, I-548); strict orphan I-233 (`IDEAS.md` ORPHANS l.884).

**Facts and decisions** (`FACTS.md`, `DECISIONS.md` rows marked [c31]; `_curation/31/facts.json`; state 02:47Z):
- **New facts:** F-LB-31 LB state (l.257); F-RUN-48 latency families + poller cadence (l.310); F-RUL-27 texts logged 02:02Z (l.342); F-TRN-63 card model re-run for exp87a (l.466). [c31] notes on 11 rows.
- **Contradictions:** C-245, C-247, C-250, C-251, C-252 RESOLVED; C-118, C-209, C-253, C-255, C-258 updated; new C-259 A-M2 bullet drops Rr '+', C-260 card 8.0 h vs rule 9.0 h, C-261 08:40Z header may not exist, C-262 hourly rounds, C-263 stale card numbers, C-264 round-31 partner overclaims, C-265 late-read trigger (l.730-736).
- **DECISIONS.md:** §1 P52-P56 cells (l.196-199); [c31] build update (l.540); §2 finals snapshot 02:47Z (l.963-980); §2f E10 line (l.1256); §2h R30-A1 LOGGED, R30-A2..A5 still proposed, new R31-A1..A5 rows (l.1473-1482); §3 [c31] notes + 3 rows.

**Watchlist** (`WATCHLIST.md`, curated ~02:50Z; `_curation/31/watch.json`): done W298 (R30-A1, 02:02Z); new W304-W308, T187-T191, I358-I365; T185 superseded by T189; still open W126, W279 (1), W286 (2), W296/W303 (now rounds 29-31), W297 (l.61-71).

**Alerts** (`INDEX.md` TOP ALERTS, 8 after dedup):
- **Resolved since curation 30:** R30-A1 pre-score entry (A-M1 trigger, tie reading, A-M2 SEC/Rr cell, '0u' unreachable, no rebuild) logged 02:02Z; card v5 l.21/l.59/l.106 edits.
- **New:** R31-A1 entry (A-M2 function, 08:40Z header, read-only rounds, card pool L + info lines) [now]; 04:13Z wake push + battery-tolerant watchdog [today]; stale card numbers vs moved medal lines [today]; silver favours {exp87a, exp85a} caveat [before-finals]; I-547 / I-045 notes [info].
- **Carried over:** E10 runbook l.66 (still 0.958; the 02:41Z run passed with it) [now]; RESULTS rows P47-P54; REPORT.md rounds 29-31; W279 (1) + W297 (not folded into 02:02Z); R30-A3..A5 unlogged (folded into the R31-A1 alert); finals still #37 + #38.
- **Curator disagreements settled here:** R31-A1 (2) facts [today] vs ideas/watch [now] -> [now] (one entry); card numbers facts [before-finals] vs ideas/watch [today] -> [today] (hard limit 12:03Z); RESULTS rows ideas/facts [before-finals] vs watch [today] -> [today], after the morning decisions and before the 12:03Z card.

## 32 - 2026-09-29 ~03:55 UTC (curation 32; git HEAD a9ac9ee = d6deab5 + a9ac9ee (round 31 committed, 02:53Z entry, card v5 l.17/l.124); uncommitted `research/KNOWLEDGE/*` curation-32 edits, `experiments/lb_poll/ledger.md`, `poll.log`, E10 logs; untracked `research/wf_ideas_v4/round32/` (no REPORT.md), `experiments/e10_watch/20260929T0313Z.txt`, `20260929T0341Z.txt`, `experiments/lb_poll/_night_subs.csv`, `_night_subs.err`)

**Sources since curation 31:** 1 commit (`git log d6deab5..a9ac9ee`); `CONTEXT.md` 4,314 -> 4,333 lines, 1 new entry 02:53Z A-M2 FUNCTION + 08:40Z HEADER + ROUND SCHEDULE + CARD POOL L l.4294-4312, `## 9. Literature` l.4313; card v5 sha8 aab8801a -> a134d5e4 (`git diff d6deab5..a9ac9ee -- research/wf_ideas_v4/round29/finals_card_v5_ru.md`). Round 32 `research/wf_ideas_v4/round32/report.json` (R32-A1..A4, new_facts, plan_issues a-e, rejected, next_focus, report_md_ru; 03:45Z), 4 `scan_*.json`, 7 `v_*.json`. Poll headers 03:34:22Z / 03:44:23Z (`experiments/lb_poll/poll.log` l.28010); E10 RUN 38-39 0313Z/0341Z (null). `experiments/RESULTS.md` unchanged (ends at P46).

**LB:** no new score; P52 exp89r, P53 exp75, P54 exp89p PENDING at 03:44:23Z (L > 3.64 / 3.64 / 2.96 h). Rank #132 of 3,980, 17th of 21 in 0.959; 115 teams >= 0.960; medal lines unchanged (silver ~#199 in 0.957, bronze ~#398 in 0.955) (`FACTS.md` F-LB-32 l.259).

**Ideas** (`IDEAS.md` CHANGES (32) l.202; `ideas.json` meta.curations[n=32], 43 records; `_curation/32/ideas.json`):
- **New I-550..I-556:** in-plan I-552 UP test from e10 snapshots + 'timeout 180' (at risk), I-553 timer texts are pointers (at risk), I-556 restrict the recheck lens; deferred I-550 insert-before-short-filter; refuted I-551 -LoG merged-daughter splitter, I-554 post-wake poller lag, I-555 E10 timing anchored on 20:00Z.
- **Logged since c31 (02:53Z):** I-543 (A-M2 function), I-544 (08:40Z header + manual list), I-545 / I-526 (card pool L, sha8 a134d5e4), I-546 push + I-547 read-time log (logged, but the push has no waiter).
- **Status moves:** I-530 in-plan -> refuted (round pause NOT adopted, 02:53Z (3)); I-121 refuted -> deferred-after-deadline (v2 drop reason void, R32-RC-C). 36 other records updated (I-546, I-539, I-548, I-528, I-424, I-232, I-478/I-465/I-479, ...).
- **Counts c31 -> c32:** 549 -> 556; in-plan 149 -> 151, refuted 261 -> 264, deferred 47 -> 49; lb-tested 62, lab-tested 28, open 2 unchanged. At-risk 15 -> 13 (off I-530, I-543, I-544, I-545; on I-552, I-553); strict orphan I-233 (`IDEAS.md` ORPHANS l.893).

**Facts and decisions** (`FACTS.md`, `DECISIONS.md` rows marked [c32]; `_curation/32/facts.json`; state 03:51Z):
- **New facts:** F-LB-32 LB state (l.259); F-RUN-49 UP tests without API calls + uptest.py timeout gap (l.313); F-RUL-28 texts logged 02:53Z (l.346); F-RUL-29 E10 copy timing restated (l.347); F-TRN-64 lab anatomy of missed divisions (l.472). [c32] notes on 11 F rows.
- **Contradictions:** C-259..C-262 RESOLVED (02:53Z); C-118, C-247, C-255, C-258, C-263 updated; new C-266 push has no waiter, C-267 uptest.py no timeout vs freeze (7), C-268 08:30Z timer text, C-269 12:03Z card v4 + dead cron ids, C-270..C-272 refuted round-32 claims (l.743-749).
- **DECISIONS.md:** §1 P52-P56 (l.197-200), [c32] update (l.543); §2 finals snapshot 03:51Z (l.968-985); §2f E10 (l.1280); §2h R31-A1 LOGGED (R31-A1 (3) not adopted), R31-A4/A5 still proposed, new R32-A1..A4 rows (l.1502-1510); §3 [c32] status on R1-R10 and §f.

**Watchlist** (`WATCHLIST.md`, curated ~03:53Z; `_curation/32/watch.json`): done W304 (R31-A1, 02:53Z); T189 superseded (round pause not adopted); new W309-W313, T192-T194, I366-I373; I358, I359 resolved; still open W126, W279 (1), W286 (2), W296/W303 (now rounds 29-32), W297, W308 (l.61-71).

**Alerts** (`INDEX.md` TOP ALERTS, 9 after dedup):
- **Resolved since curation 31:** R31-A1 pre-score entry logged 02:53Z and committed a9ac9ee; card v5 non-CI pool L 9.0 h (l.17, l.124).
- **New:** R32-A1 push waiter by 04:09Z [now]; timer texts vs logged lines at 07:23Z / 08:30Z / 12:03Z [today]; uptest.py save timeout + 0-call UP test, with the curator correction that E10 runs hourly (~xx:42Z), not every ~30 min [today]; card v5 dead cron ids l.93/138/152 and card v4 l.1 old sha8 [today, at the 12:03Z fill]; R32-A4 post-deadline division order + W313 recheck lens [info].
- **Carried over:** E10 runbook l.66 (still 0.958; fix before 04:41Z) [now]; card v5 numbers l.39 / l.46-47, l.114 '+/0u', I-539 info lines [today]; RESULTS rows P47-P54, REPORT.md rounds 29-32, W279 (1), W297, I-510, I-045 note [today]; finals still #37 + #38, messages 18:37Z / 19:43Z / 20:00Z [before-finals].
- **Curator disagreements settled here:** card stale items facts / watch [before-finals] vs ideas [today] -> [today] (hard limit 12:03Z); RESULTS / REPORT rows ideas / facts [before-finals] vs watch [today] -> [today], after the morning decisions and before the 12:03Z card; R32-A4 [info] everywhere.

## 33 - 2026-09-29 ~04:50 UTC (curation 33; git HEAD dd7cf04 = a9ac9ee + 6bbbdf0 (round 32 committed, 03:56Z entry), dd7cf04 (04:10Z power push sent); uncommitted `research/KNOWLEDGE/*` curation-33 edits, `experiments/lb_poll/ledger.md`, `poll.log`, E10 / feed logs; untracked `research/wf_ideas_v4/round33/` (no REPORT.md), `experiments/e10_watch/20260929T0413Z.txt`, `20260929T0441Z.txt`, `experiments/discussions/digest_20260929T0358Z.md`, `experiments/lb_poll/_night_subs.csv`, `_night_subs.err`)

**Sources since curation 32:** 2 commits (`git log a9ac9ee..dd7cf04`); `CONTEXT.md` 4,333 -> 4,349 lines, 2 new entries: 03:56Z ROUND 32 external delta null + R32-A1..A3 (l.4313-4324) and 04:10Z R31-A2 POWER PUSH SENT (l.4325-4328); `## 9. Literature` l.4329. Round 33 `research/wf_ideas_v4/round33/report.json` (R33-A1..A4, new_facts, plan_issues a-e, rejected, report_md_ru; 04:36Z), 4 `scan_*.json`, 4 `v_*.json`. Poll headers 04:34:31Z / 04:44:33Z (`experiments/lb_poll/poll.log` l.28315, l.28376); E10 RUN 40 0441Z (null); feed digest 0358Z (null). `experiments/RESULTS.md` unchanged (ends at P46).

**LB:** no new score; P52 exp89r, P53 exp75, P54 exp89p PENDING at 04:44:33Z. Rank #132 of 3,981 at 04:13Z -> #133 of 3,982 at 04:41Z, 18th of 22 in the 0.959 block; 115 teams >= 0.960; medal lines unchanged (silver ~#199 in 0.957, bronze ~#398 in 0.955) (`experiments/e10_watch/20260929T0441Z.txt` l.1149; `FACTS.md` F-LB-33 l.261).

**Ideas** (`IDEAS.md` CHANGES (33) l.205; `ideas.json` meta.curations[n=33], 37 records; `_curation/33/ideas.json`):
- **New I-557..I-560:** in-plan I-557 per-ref night read watchers (R33-A1, at risk), I-558 P late threshold 8.0 h non-CI (R33-A2, optional, at risk), I-559 C11 record for probes 54 / 52 (R33-A4 (b), at risk); refuted I-560 finals-pool config sweep-drift risk (E10 pre-pool validator gate kept).
- **Logged / done since c32:** I-546 push SENT 04:10Z; I-552 UP-test procedure and I-553 timer texts are pointers LOGGED 03:56Z (all three off the at-risk list).
- **Updated:** I-529 (R33-A3 immediate 'timeout 180' save; e10 loop ends 12:00Z); I-129 (aka OpenKaggle BH-0005 MIN_TRACK_LEN 4; exp89m NOT recommended); I-087 / I-258 (stale-tick line already in place); I-116 / I-119 (C11 'overturns' refuted as overclaim); I-026 (scans must open decisions/ and kaggle_runs/); external null on I-364, I-412, I-475, I-541, I-320.
- **Counts c32 -> c33:** 556 -> 560; in-plan 151 -> 154, refuted 264 -> 265; lb-tested 62, lab-tested 28, deferred 49, open 2 unchanged. At-risk 13 -> 13 (off I-546, I-552, I-553; on I-557, I-558, I-559); strict orphan I-233 (`IDEAS.md` ORPHANS l.900).

**Facts and decisions** (`FACTS.md`, `DECISIONS.md` rows marked [c33]; `_curation/33/facts.json`; state 04:42Z):
- **New facts:** F-LB-33 LB + external state (l.261); F-RUN-50 one-shot read watcher + 09:13-10:13Z timer gap (l.316); F-RUN-51 e10 loop ends 12:00Z (l.317); F-RUL-30 03:56 / 04:10 logs (l.352); F-RUL-31 P late threshold 8.0 vs 10.2 h (l.353); F-MOD-52 all 10 pool notebooks validator OFF, code default ON (l.410); F-TRN-65 BH-0005 = I-129 + C11 wording (l.480).
- **Contradictions:** C-247, C-266, C-268, C-269 RESOLVED by the logged lines; C-267 partly; C-118, C-255, C-263 still open; new C-273 (P late threshold, open), C-274 (who re-arms the watcher, open), C-275..C-278 resolved by skeptics (l.758-763).
- **DECISIONS.md:** §1 [c33] update (l.546); §2 finals snapshot 04:42Z with exp89m as not a candidate (l.975-988); §2h rows for logged R32-A1..A3 + push, R33-A1..A4 proposals, round-33 rejections (l.1648-1650); §3 [c33] status on R1-R10; changelog (l.1850).

**Watchlist** (`WATCHLIST.md`, curated ~04:45Z; `_curation/33/watch.json`): done W309 (push), W310 (UP-test procedure), W311 (a); W313 replaced by W318 (READS-vs-CARD lens); new W314-W318, T195-T197, I374-I381; still open W126, W279 (1), W286 (2), W296/W303 (now rounds 29-33), W297, W308 (l.58-68).

**Alerts** (`INDEX.md` TOP ALERTS, 10 after dedup):
- **Resolved since curation 32:** the 04:13Z push had no waiter (R32-A1 timer logged, push sent 04:10Z); uptest save timeout (R32-A2 logged); timer texts vs logged lines (R32-A3 logged; texts still stale but no longer govern).
- **New:** W314 / R33-A1 per-ref watchers NOT armed (re-checked ~04:50Z: only 13516 / 16292) [now]; R33-A2 P late threshold before exp89p's first header [today]; R33-A3 morning late-read watchers (e10 ends 12:00Z) [today]; C11 record wording after each decision [today]; BH-0005 = I-129 and the validator-default-ON warning for E10 copies [info]; stress re-ticking away from {#37, #38} over the partner choice (I380) [before-finals].
- **Carried over:** E10 runbook l.66 (still 0.958; now fix before 05:41Z) [now]; card v5 numbers / info lines / l.114 [today, 12:03Z]; RESULTS rows P47-P54, REPORT.md rounds 29-33, round 33 uncommitted, W279 (1), W297, I-510, I-045 note [today]; finals still #37 + #38, messages 18:37Z / 19:43Z / 20:00Z [before-finals].
- **Curator disagreements settled here:** RESULTS / REPORT rows ideas / facts [before-finals] vs watch [today] -> [today], after the morning decisions; card fill facts / ideas [before-finals] -> [today] (hard limit 12:03Z); R33-A2 all [today] (optional, pre-score only).

## 34 - 2026-09-29 ~06:17 UTC (curation 34; git HEAD d9d259e = dd7cf04 + b4848cb (round 33 + curation 33 committed, 04:51Z entries), d9d259e (06:09Z post-wake check, digest 0528Z, `experiments/discussions/744250.md`); uncommitted `research/KNOWLEDGE/*` curation-34 edits; untracked `research/wf_ideas_v4/round34/` (no REPORT.md), `research/KNOWLEDGE/_curation/34/`, `experiments/lb_poll/_night_subs.csv`, `_night_subs.err`)

**Sources since curation 33:** 2 commits (`git log dd7cf04..d9d259e`); `CONTEXT.md` 4,349 -> 4,371 lines, 3 new entries: 04:51Z P LATE THRESHOLD (R33-A2, l.4329-4335), 04:51Z OPS per-ref watchers + morning procedure (R33-A1 / R33-A3, l.4336-4342), 06:09Z POST-WAKE CHECK (l.4343-4350); `## 9. Literature` l.4351. Round 34 `research/wf_ideas_v4/round34/report.json` (R34-A1..A4, new_facts, plan_issues a-d, rejected, next_focus, report_md_ru; 06:05Z), 4 `scan_*.json`, 5 `v_*.json`. Poll headers to 06:07:54Z (`experiments/lb_poll/poll.log` l.28746; 05:34:41Z / 05:46:17Z empty, DNS errors); E10 0513Z (null), RUN 41 0541Z fetched 0 of 8 (`experiments/e10_watch/watch_loop.log`); feed digest 0528Z (new topic 744250). `experiments/RESULTS.md` unchanged (ends at P46).

**LB:** no new score; P52 exp89r, P53 exp75, P54 exp89p PENDING at 06:07:54Z. Rank #133 of 3,984 at 05:14Z, 18th of 22 in the 0.959 block (116-137); 115 teams >= 0.960; medal lines unchanged (silver ~#199 in 0.957, bronze ~#398 in 0.955) (`experiments/e10_watch/20260929T0513Z.txt` l.1149; `FACTS.md` F-LB-34 l.263).

**Ideas** (`IDEAS.md` CHANGES (34) l.208; `ideas.json` meta.curations[n=34], 35 records; `_curation/34/ideas.json`):
- **New I-561..I-563:** in-plan I-561 conditional night-ref LB saves post_exp75 / post_exp89r / post_exp89p (R34-A1, at risk); in-plan I-562 card v5 l.45 neighbour = exp85a in the FILLED copy (R34-A2, at risk); refuted I-563 card l.47 recompute / 'P3 first upheld' (R34-RC-B, refuted CI prior).
- **Logged since c33:** I-557 per-ref watchers, I-558 P late 8.0 h, I-529 morning late-read watcher + save (all 04:51Z; off the at-risk list).
- **Updated:** I-487 (exp89u revival refuted again); I-513 (no mc34_* numbers on the card or in messages); I-494 (standing prior favours P2 {exp87a, exp75} on bronze ~10/13; logged rule (b) kept); I-412 (JT neighbour-pair rejection upheld); I-548 (#133 / 3,984; standing-prior rows); I-353 / I-442 (aka Charannoo/biohub divrelax, R34-A3); I-026 (4 new repos; scans list full repo trees); I-517 / I-497 (outage, no loop restart); ~20 smaller updates.
- **Counts c33 -> c34:** 560 -> 563; in-plan 154 -> 156, refuted 265 -> 266; lb-tested 62, lab-tested 28, deferred 49, open 2 unchanged. At-risk 13 -> 12 (off I-529, I-557, I-558; on I-561, I-562); strict orphan I-233 (`IDEAS.md` ORPHANS l.906).

**Facts and decisions** (`FACTS.md`, `DECISIONS.md` rows marked [c34]; `_curation/34/facts.json`; state 06:15Z):
- **New facts:** F-LB-34 LB + external delta (l.263); F-RUN-52 network outage 05:34-05:47Z and recovery (l.320); F-RUN-53 UP-test masking risk for the night refs (l.321); F-RUL-32 04:51 logs (l.358); F-RUL-33 selection timing at the deadline, topic 744250 (l.359); F-MOD-53 external repos round 34, no build (l.417); F-TRN-66 finals-pair model under the standing CI prior (l.488).
- **Contradictions:** C-273 and C-274 RESOLVED by the 04:51Z logs; new C-279 (card l.45 neighbour, open), C-280 (mc34 used the refuted prior, resolved), C-281 (Charannoo disclosure, resolved), C-282 (UP-test masking, open), C-283 (P2 / P3 order, resolved) (l.772-776); C-118, C-263 still open.
- **DECISIONS.md:** §1 [c34] update (l.549); §2 finals snapshot 06:15Z, exp85a named as exp87a's closest neighbour, exp89u a refuted non-candidate (l.978-980); §2h rows for the 04:51 logs, R34-A1..A4 proposals, round-34 rejections (l.1675-1677); §3 [c34] status on R5-R8, R10, finals rule §f; changelog (l.1879).

**Watchlist** (`WATCHLIST.md`, curated ~06:15Z; `_curation/34/watch.json`): done W314 (per-ref watchers), W315 (P late 8.0 h); new W319 (R34-A1), W320 (R34-A2), W321 (R34-A3), W322 (R34-A4), T198-T200, I382-I390; I374-I376 resolved; still open W126, W279 (1), W286 (2), W296/W303 (now rounds 29-34), W297 (l.39-48).

**Alerts** (`INDEX.md` TOP ALERTS, 10 after dedup):
- **Resolved since curation 33:** W314 / R33-A1 per-ref watchers (logged 04:51Z, 1760 / 17532 alive); R33-A2 P late threshold (logged pre-score); R33-A3 morning procedure (logged); R34-A4 post-wake step (logged 06:09Z: back on AC 06:01Z, loops alive, none restarted; `CONTEXT.md` l.4343-4350).
- **New:** W319 / R34-A1 night-ref LB saves NOT armed (re-checked 06:17Z: no save job) [now]; e10 RUN 42 06:41Z must fetch after RUN 41 0/8 [today]; uptest compare does not enforce the +1 count step [today]; card l.45 neighbour fix (I-562) [today]; no mc34_* numbers (refuted prior) [today]; exp89q v flag if P reads late (PC34-04) [today]; topic 744250 [info].
- **Carried over:** E10 runbook l.66 (still 0.958; fix before 06:41Z) [now]; card v5 fill (I-539, I-548) [today, 12:03Z]; C11 record (I-559), I-510 message, W279 (1), W297 [today]; RESULTS rows P47-P54, REPORT.md rounds 29-34, round 34 untracked [today]; finals still #37 + #38, messages 18:37Z / 19:43Z / 20:00Z [before-finals].
- **Curator disagreements settled here:** battery: ideas 'on battery 72% at 06:00Z' [now] vs facts / watch 'AC at 06:08Z' -> AC (06:09Z entry; Win32_Battery 2, 79% at 06:17Z), the RUN 42 check stays [today]; mc34 numbers facts [before-finals] vs ideas / watch [today] -> [today] (first exposure at the 12:03Z fill); RESULTS / REPORT ideas / facts [before-finals] vs watch [today] -> [today], after the morning decisions (as in c33).

## 35 - 2026-09-29 ~07:45 UTC (curation 35; git HEAD 81884c9 = d9d259e + f2c4711 (round 34 + curation 34 committed, 06:20Z OPS entry), 81884c9 (07:23Z MORNING PREP, e10 0641Z / 0713Z, digest 0658Z); uncommitted `research/KNOWLEDGE/*` curation-35 edits, `experiments/lb_poll/ledger.md`, `poll.log`, e10 logs; untracked `research/wf_ideas_v4/round35/` (no REPORT.md), `research/KNOWLEDGE/_curation/35/`, `experiments/e10_watch/20260929T0741Z.txt`, `experiments/lb_poll/_night_subs.csv`, `_night_subs.err`)

**Sources since curation 34:** 2 commits (`git log d9d259e..81884c9`); `CONTEXT.md` 4,371 -> 4,401 lines, 2 new entries: 06:20Z OPS night-ref LB saves (R34-A1) + R34-A2 card line + R34-A3 'later' (l.4351-4360), 07:23Z MORNING PREP (l.4361-4380); `## 9. Literature` l.4381. Round 35 `research/wf_ideas_v4/round35/report.json` (R35-A1..A5, new_facts (1)-(6), plan_issues (a)-(f), rejected, next_focus, report_md_ru; 07:33Z), 4 `scan_*.json`, 5 `v_*.json`. Poll headers to 07:38:11Z (`experiments/lb_poll/poll.log` l.29295); e10 RUN 42 (06:42Z) and RUN 43 (07:42Z, `20260929T0741Z.txt`) both 8/8, signals 0 (`experiments/e10_watch/watch_loop.log` l.54-55); feed digest 0658Z (0 new). `experiments/RESULTS.md` unchanged (ends at P46).

**LB:** no new score; P52 exp89r, P53 exp75, P54 exp89p PENDING at 07:38:11Z. Rank #136 of 3,986 at 07:14Z, 17th of 20 in the 0.959 block (120-139); 119 teams >= 0.960; the 3 teams that passed us are at 0.960; medal lines unchanged (`FACTS.md` F-LB-35 l.265).

**Ideas** (`IDEAS.md` CHANGES (35) l.212; `ideas.json` meta.curations[n=35], 46 records; `_curation/35/ideas.json`):
- **New I-564..I-567:** in-plan I-564 UP-test log line + one LB-lag re-save (R35-A1, at risk); in-plan I-565 card v5 П1 deletions l.39 / l.48 / l.54 + 'П1 = 0' check (R35-A2, at risk); refuted I-566 PC35-01 as proposed (S0-bias premise false; 'never MASKED on +0'); open-untested I-567 optional CI-dataset guard before A-M1 (PC35-05, strict orphan).
- **Logged since c34:** I-561 night-ref saves and I-562 card l.45 line (06:20Z, off the at-risk list); I-517 post-wake DONE (06:09Z); I-538 / I-547 / I-481 morning prep, L bounds, commands (07:23Z).
- **Upheld closed:** I-172 (probe 8 GAP_CLOSE_UM; GAP_CLOSE_MAX_GAP 2 no-op), I-176 (tight55 rank-neutral), I-133 (B25; R35-A3 side line at the DIS read). Kai-Gowers x138-port reads mapped to I-026, I-431 (K replicated), I-138, I-150, I-001, I-183, I-441, I-129, I-342 (probes 43/44 tie K2, correcting 'below').
- **Updated:** I-544 (08:40Z header ~08:38:23Z), I-553 (timer texts still stale), I-529 / I-504 (CI dataset not in G3), I-528 / I-535 / I-552 (S0 0713Z / 0741Z), I-548 (#136 / 3,986), I-526 (+ I-565), I-556 (R35-A5 lens from round 36), I-364 / I-541 / I-475, I-412, I-559, I-353 and others.
- **Counts c34 -> c35:** 563 -> 567; in-plan 156 -> 158, refuted 266 -> 267, open 2 -> 3; lb-tested 62, lab-tested 28, deferred 49 unchanged. At-risk 12 -> 12 (off I-561, I-562; on I-564, I-565); strict orphans I-233 + I-567 (`IDEAS.md` ORPHANS l.914).

**Facts and decisions** (`FACTS.md`, `DECISIONS.md` rows marked [c35]; `_curation/35/facts.json`; state 07:40Z):
- **New facts:** F-LB-35 LB 07:14Z + movers (l.265); F-RUN-54 morning-prep state, 08:40Z header ~08:38:23Z, G3 gap (l.324); F-RUL-34 06:20 / 07:23 logged texts (l.363); F-RUL-35 uptest compare mechanics, R35-A1 (l.364); F-MOD-54 Kai-Gowers x138-port reads (l.423); F-TRN-67 external K replication, new external negatives, DC tie correction (l.495).
- **Contradictions:** C-279 and C-282 RESOLVED by the 06:20Z log; new C-284 (card П1 lines for a CI V_pub, open), C-285 (PC35-01 S0 bias, resolved), C-286 (DC 0.20 / 0.225 tie vs 'below', resolved), C-287 (citation corrections, resolved) (l.784-787); C-118, C-263 still open.
- **DECISIONS.md:** §1 [c35] update (l.552) and [c35] cells on P52-P56 (l.200-203); §2 finals snapshot 07:40Z, still TICKED #37 + #38, plan {V_pub, #37 / exp75} (l.983-985); §2h R34 row marked A1 / A2 LOGGED + 4 new rows (06:20 saves, 07:23 prep, R35 proposals, R35 rejections) (l.1699-1704); §3 [c35] statuses R5-R8, R10, §f; changelog (l.1908).

**Watchlist** (`WATCHLIST.md`, curated ~07:40Z; `_curation/35/watch.json`): done W319 (saves armed), W322 (post-wake), T198 (RUN 42 8/8), T151 prep + W306 (07:23Z); new W323-W328 (R35-A1..A5, PC35-05), T201-T205, I391-I399; still open W126, W279 (1), W286 (2), W296/W303 (now rounds 29-35), W297.

**Alerts** (`INDEX.md` TOP ALERTS, 11 after dedup):
- **Resolved since curation 34:** W319 / R34-A1 night-ref LB saves armed (jobs 8368 / 17300 / 27192, alive 07:36Z); R34-A2 card l.45 line logged; R34-A4 post-wake logged; e10 RUN 42 / 43 fetched 8/8; 07:23Z morning prep logged; round 34 committed (f2c4711); battery question closed (AC, 79%).
- **New:** exp89p read -> A-M1 due now (P54 PENDING at 07:38:11Z) [now]; R35-A1 UP-test log line + lag re-save not logged [now]; first MSK 'UNUSED by rule' message unsent [now]; card v5 П1 lines l.39 / l.48 / l.54 (R35-A2, C-284) [today]; B25 side line at the DIS read (R35-A3) [today]; CI-dataset guard (PC35-05) [only if A-M1 fires]; Kai-Gowers external reads [info].
- **Carried over:** E10 runbook l.66 [now]; timer texts stale pointers (I-553) [today]; card fill 12:03Z with standing prior only, no mc34_* numbers [today]; C11 line (I-559) [today]; RESULTS rows P47-P54, REPORT.md rounds 29-35, round 35 untracked, four missing CONTEXT lines [today]; finals messages 18:37Z / 19:43Z / 20:00 UTC tick, hindsight guard before 23:00Z [before-finals].
- **Curator disagreements settled here:** UP-test count check: facts [today] vs ideas / watch [now] -> [now] (first use at exp89p's read); CI-dataset guard: ideas [now] / watch [today] / facts [info] -> conditional one call iff A-M1 fires (risk ~0); RESULTS / REPORT: ideas / facts [before-finals] vs watch [today] -> [today] after the morning decisions (as in c33 / c34).

## 36 - 2026-09-29 ~08:50 UTC (curation 36; git HEAD 785be93 = 81884c9 + 332ace7 (round 35 + curation 35 committed, 07:46Z entry), ce88ccf (07:59Z P54 read), 2fdf387 (08:19Z A-M2 rule (a)), 096d533 (08:23Z exp89t built), 6a3f778 (08:27Z user yes), 785be93 (08:28Z slot 2 held); uncommitted `research/KNOWLEDGE/*` curation-36 edits, `experiments/lb_poll/ledger.md`, `poll.log`, e10 / feed logs; untracked `research/wf_ideas_v4/round36/` (with REPORT.md), `research/KNOWLEDGE/_curation/36/`, `experiments/discussions/744273.md`, `744278.md`, `digest_20260929T0828Z.md`, `experiments/e10_watch/20260929T0841Z.txt`, `experiments/lb_poll/_night_subs.csv`, `_night_subs.err`)

**Sources since curation 35:** 6 commits (`git log 81884c9..785be93`); `CONTEXT.md` 4,401 -> 4,461 lines, 6 new entries l.4381-4440 (07:46Z ROUND 35 procedures, 07:59Z READ P54, 08:19Z A-M2 RULE (a), 08:23Z exp89t BUILT, 08:27Z USER yes, 08:28Z SLOT 2 HELD); `## 9. Literature` l.4441. Round 36 `research/wf_ideas_v4/round36/report.json` (R36-A1..A5, 08:33Z; read CONTEXT only to l.4425 per `report.notes.md`), `REPORT.md`, 4 `scan_*.json`, 12 `v_*.json`. Poll headers to 08:38:21Z (`experiments/lb_poll/poll.log` l.29661); e10 RUN 44 08:42Z 8/8, signals 0 (`experiments/e10_watch/watch_loop.log`); feed 08:28Z 2 new topics (744273, 744278 'can we still join', no content). `experiments/RESULTS.md` unchanged (ends at P46).

**LB:** NEW P54 exp89p (K + SEC) = 0.956 (07:58:14Z; L (7.02, 7.20] h) -> P '-', SEC on K ~-0.002; A-M1 UNUSED (`CONTEXT.md` l.4394-4403). P52 exp89r, P53 exp75 PENDING at 08:38:21Z; exp89t not yet submitted. Rank #139 at 08:13Z (of 3,987) and 08:42Z, 16th of 20 in the 0.959 block (124-143); 123 teams >= 0.960 (+4 since 07:14Z) (`FACTS.md` F-LB-36 l.267; `experiments/e10_watch/20260929T0841Z.txt` l.1160).

**Ideas** (`IDEAS.md` CHANGES (36) l.219; `ideas.json` meta.curations[n=36], 51 records; `_curation/36/ideas.json`):
- **New I-568..I-574:** logged I-568 A-M2 rule (a) (supersedes I-543) and I-569 slot-2 hold to 12:00Z; at-risk I-570 CLARIFY + SEC-tie exception (R36-A2), I-571 08:30Z timer line (R36-A3), I-572 read-time logistics (R36-A4; item (1) conflicts with the hold), I-573 card fill delta for exp89t / rule (a) (R36-A5); refuted I-574 gated exp89t option (the user chose ungated).
- **Status moves:** I-479 in-plan -> lb-tested (P54); I-485 exp89l and I-543 in-plan -> refuted; I-567 open -> refuted (moot); I-486 exp89t refuted -> in-plan (revived, user yes 08:27Z).
- **Updated:** I-484 / I-450 / I-483 / I-507 (exp89s under rule (a) + hold; 08:45Z CI cutoff broken with the user told); I-540 (brief overtaken); I-535 / I-508 (-> I-570); I-553 (-> I-571); I-496 / I-512 (dummy-lab sign record); I-161 / I-162 (744273 external null); I-548 (#139 / 3,987); I-526 (+ I-573).
- **Counts c35 -> c36:** 567 -> 574; lb-tested 62 -> 63, refuted 267 -> 270, in-plan 158 -> 162, open 3 -> 2; lab-tested 28, deferred 49 unchanged. At-risk 12 -> 13 (off I-559, I-564, I-565; on I-570..I-573); strict orphans 2 -> 1 (I-233) (`IDEAS.md` ORPHANS l.928).

**Facts and decisions** (`FACTS.md`, `DECISIONS.md` rows marked [c36]; `_curation/36/facts.json`; state 08:35Z + 08:38:21Z header):
- **New facts:** F-LB-36 P54 read + LB 08:13Z (l.267); F-RUN-55 29 Sep latencies / exp89t timing (l.327); F-RUL-36 logged decisions 07:46-08:28 (l.368); F-MOD-55 exp89t = exp87a + DIS 2.25 (l.428); F-TRN-68 SEC n2a on K = -0.002 + dummy-lab sign record (l.501); F-TRN-69 744273 external null + round-36 MC for exp89t (l.502).
- **Contradictions:** C-284 resolved as procedure; new C-288..C-296 (l.795-803): SEC-in-pool sentence, SEC-champion tie, 'champion exp87a' (OPEN, R36-A2); R36-A1 superseded by the user yes; rule (a) auto-send vs the hold; late submits vs R8 / CI cutoff; card v5 vs exp89t (OPEN, R36-A5); exp89t probe.json generic rule; exp89p L bounds. C-118, C-263 still open.
- **DECISIONS.md:** §1 [c36] update (l.556), P52-P55 cells + new P55 exp89t row (l.201-205); §2 finals snapshot 08:35Z, still TICKED #37 + #38 (l.989-991); §2h 6 new rows (P54 read, rule (a), exp89t build + yes, slot-2 hold, R36 proposals, R36 rejections) (l.1730-1735); §3 [c36] R5-R8, R10, §f; changelog (l.1941).

**Watchlist** (`WATCHLIST.md`, curated ~08:40Z; `_curation/36/watch.json`): done A-M1 (unused), W315, W317 (b), round-35 procedures; moot T201, T203, W328, W302 (4), W279 (1); downgraded W286 (2) (live loop already >= 0.960, `experiments/lb_poll/e10_watch_loop.py` l.78); new W329-W337, T206-T212, C1-C6, I400-I408; still open W126, W296/W303 (rounds 29-35).

**Alerts** (`INDEX.md` TOP ALERTS, 11 after dedup):
- **Resolved since curation 35:** exp89p read -> A-M1 UNUSED (07:59Z); R35-A1 UP-test line logged (07:46Z); first MSK brief overtaken by the exp89t yes; E10 runbook l.66 downgraded to info; CI-dataset guard moot; C11 record logged; round 35 committed (332ace7).
- **New:** round 36 stale vs the 08:27Z yes and 08:28Z hold (C1 / C4 / C-291 / C-292) [now]; exp89t submit at dummy PASS with probe-55 -m and watcher [now]; R36-A2 CLARIFY before exp89r's header [now]; R36-A3 08:30Z line overdue [now]; no timer for the ~11:55Z slot-2 ask, 11:10Z timer text stale (watch only) [today]; late windows exp89s ~19:01-19:49Z / exp89t tail, R8 override unrecorded [today]; card fill delta I-573 incl. 'no CI in finals' case [today]; 744273 external edge-filter null [info].
- **Carried over:** night reads exp75 / exp89r (now coding rule (a) only) [today]; RESULTS rows P47-P51 + P54, REPORT.md rounds 29-35, round 36 untracked [today]; finals messages 18:37Z / 19:43Z / 20:00 UTC tick, hindsight guard before 23:00Z [before-finals].
- **Curator disagreements settled here:** RESULTS / REPORT: ideas / facts [before-finals] vs watch [today] -> [today] after the morning decisions (as in c33-c35); R8 override line: watch [info] kept as part of alert 7 [today] because it rides with the late-window watchers; 11:55Z timer gap (watch only) kept [today].

## 37 - 2026-09-29 ~10:00 UTC (curation 37; git HEAD 348b9dc = 785be93 + 7caa068 (round 36 + curation 36 committed, 08:51Z CLARIFY + SEC exception, 08:51Z timer note), 9693f08 (09:00Z P55 exp89t submitted), 782eed2 (09:09Z P53 read), 348b9dc (09:19Z P52 read); uncommitted `research/KNOWLEDGE/*` curation-37 edits, `experiments/lb_poll/ledger.md`, `poll.log`, e10 logs; untracked `research/wf_ideas_v4/round37/` (no REPORT.md), `research/KNOWLEDGE/_curation/37/`, `experiments/e10_watch/20260929T0941Z.txt`, `experiments/lb_poll/_night_subs.csv`, `_night_subs.err`)

**Sources since curation 36:** 4 commits (`git log 785be93..348b9dc`); `CONTEXT.md` 4,461 -> 4,508 lines, 5 new entries l.4441-4487 (08:51Z CLARIFY + ORDER (1) SEC EXCEPTION, 08:51Z 08:30Z TIMER NOTE, 09:00Z PROBE 55 SUBMITTED, 09:09Z READ P53, 09:19Z READ P52); `## 9. Literature` l.4488. Round 37 `research/wf_ideas_v4/round37/report.json` (R37-A1..A8, plan_issues (1)-(7), rejected R37-RC-A/B/C, R37-F1/F6; 09:40Z; REPORT.md write refused, text in 'report_md_ru'), 4 `scan_*.json`, 8 `v_*.json`. Poll headers to 09:48:35Z (`experiments/lb_poll/poll.log` l.30088; exp89t PENDING); e10 RUN 45 09:42Z 8/8, signals 0 (`experiments/e10_watch/watch_loop.log`); feed digest 09:18Z (Satwik + Yassine Alouini in 744273). `experiments/RESULTS.md` unchanged (ends at P46).

**LB:** NEW P53 exp75 (#37 + CI) = 0.955 clean (09:08:28Z; L (8.88, 9.05] h; CI 3/3 '+') and P52 exp89r = 0.957 (09:18:30Z; Rr '-', DIS ~0, rule (a) not met, exp89s not sent) (`CONTEXT.md` l.4471-4487). P55 exp89t submitted 09:00:17Z (56669888), PENDING. V_pub stays exp87a 0.959; rank #140 of 3,989 at 09:41Z, 16th of 20 in the 0.959 block (`experiments/e10_watch/20260929T0941Z.txt` l.1164; `FACTS.md` F-LB-37 l.269). 4 of 5 submits used today.

**Ideas** (`IDEAS.md` CHANGES (37) l.225; `ideas.json` meta.curations[n=37], 50 records; `_curation/37/ideas.json`):
- **New I-575..I-582:** in-plan at-risk I-575 slot-2 closure (R37-A1 + A5), I-576 stale timers 17304 / 33456 (R37-A2), I-577 exp89t S0 (R37-A3), I-578 12:03Z card from `card_fill_1203.txt` (R37-A4), I-579 CONTEXT addendum + count-jump timing (R37-A6), I-580 exp89t read handling (R37-A7), I-581 optional П2/П3 caption (R37-A8); deferred-after-deadline I-582 Satwik 'public embryo division-poor'.
- **Status moves:** I-465 exp75 and I-478 exp89r in-plan -> lb-tested; I-484 exp89s in-plan -> refuted. Closed/upheld: R37-RC-A DIS 1.75 (I-461, I-451), R37-RC-B wording, R37-RC-C blind exp89s, R37-F1 duplicate, R37-F6 rule change for exp89t, E10 / aggressive again.
- **Logged / done since c36 (off at-risk):** I-570 CLARIFY, I-571 timer note (08:51Z), I-572 read logistics (executed), I-573 card delta (pre-applied into I-578).
- **Counts c36 -> c37:** 574 -> 582; lb-tested 63 -> 65, refuted 270 -> 271, deferred 49 -> 50, in-plan 162 -> 166; lab-tested 28, open 2 unchanged. At-risk 13 -> 16; strict orphan I-233 (`IDEAS.md` ORPHANS l.942).

**Facts and decisions** (`FACTS.md`, `DECISIONS.md` rows marked [c37]; `_curation/37/facts.json`; state 09:45Z):
- **New facts:** F-LB-37 P53 / P52 reads + LB 09:13-09:41Z (l.269); F-RUN-56 count-jump completion timing + S0 availability for exp89t (l.330); F-RUL-37 logged decisions 08:51-09:19 (l.372); F-TRN-70 lever record after P52 / P53 (l.507); F-TRN-71 Satwik external division null (l.508).
- **Contradictions:** C-288, C-289, C-290 RESOLVED (08:51Z CLARIFY); new C-297..C-303 (l.810-816): 11:10Z timer text, 12:03Z timer card v4, exp89t read window, exp89t S0, card fill vs reads, slot-2 window 14:15 vs 14:55 MSK, 'П3 first' vs MC. C-118 still open.
- **DECISIONS.md:** P52 / P53 / P55 filled (l.202-206), §1 [c37] update (l.559); §2 finals snapshot 09:45Z, still TICKED #37 + #38 (l.994-996); §2h 5 new rows (CLARIFY, P53 read, P52 read, R37 proposals, R37 rejections) (l.1759-1763); §3 [c37] statuses; changelog (l.1971).

**Watchlist** (`WATCHLIST.md`, curated ~09:45Z; `_curation/37/watch.json`): done W330, W331, W337 (08:51Z logs), exp89t submit, exp75 / exp89r reads; moot W335, T211, I405, I406; contradictions C1, C3, C4 resolved; new W338-W343, W345, T209, T210, T216, C7-C9, I409-I418; still open W126 (RESULTS rows), W296/W303 (REPORT.md rounds 29-35, 37), W336 (R8 override line).

**Alerts** (`INDEX.md` TOP ALERTS, 12 after dedup):
- **Resolved since curation 36:** round 36 vs the user (C1/C4, C-291/C-292); exp89t submit (09:00:17Z); R36-A2 CLARIFY and R36-A3 timer line logged (08:51Z); exp75 / exp89r reads coded; round 36 committed (7caa068); 11:55Z slot-2 timer gap closed (an 11:50Z timer pid 21496 exists, `WATCHLIST.md` T209).
- **New:** stale timers 17304 / 33456 [now]; R37-A1 slot-2 message with the 14:15 MSK cutoff [now]; exp89t count-56 S0 missing, arm 17:40Z pre_exp89t save + 11:45Z mk_s0.py [now]; 11:50Z / 12:00Z UNUSED log [today]; 12:03Z card from scratchpad block with R37-A4 edits (scratchpad-only risk) [today]; round 38 last slot-2 scan [today]; R37-A6 addendum [today]; exp89t read window 17:53-19:54Z + 19:47Z re-read [before-finals]; battery [today]; П2/П3 break-even caption [info]; Satwik I-582 [info].
- **Carried over:** finals tick 20:00Z, SELECTED check, hindsight guard / I-252 / I-407 before 23:00Z [before-finals]; RESULTS rows P47-P55, REPORT.md rounds 29-35 + 37 [info, after the tick].
- **Curator disagreements settled here:** exp89t S0: facts [today] vs ideas / watch [now] -> [now] (the job must be armed while the session is alive); CONTEXT addendum: watch [now] / facts [today] / ideas [info] -> [today] with the next commit; RESULTS / REPORT: ideas / facts [info] vs watch [before-finals] -> after the 20:00Z tick (changed from [today] in c33-c36, since the finals work now takes all remaining pre-tick time).

## 38 - 2026-09-29 ~10:50 UTC (curation 38; git HEAD 135788c = 348b9dc + 66f1eeb (09:57Z ROUND 37 APPLIED, round 37 + curation 37 committed), 135788c (10:00Z feed false positive, 'stacking' excluded); uncommitted `research/KNOWLEDGE/*` curation-38 edits, `experiments/lb_poll/ledger.md`, `poll.log`, e10 logs; untracked `research/wf_ideas_v4/round38/` (no REPORT.md), `research/KNOWLEDGE/_curation/38/`, `experiments/e10_watch/20260929T1013Z.txt`, `20260929T1041Z.txt`, `experiments/lb_poll/_night_subs.csv`, `_night_subs.err`)

**Sources since curation 37:** 2 commits (`git log 348b9dc..135788c`); `CONTEXT.md` 4,508 -> 4,529 lines, 2 new entries l.4488-4508 (09:57Z ROUND 37 APPLIED R37-A1..A5; 10:00Z FEED E10 FLAG = FALSE POSITIVE); `## 9. Literature` l.4509. Round 38 `research/wf_ideas_v4/round38/report.json` (R38-A1..A7, plan_issues (1)-(11), new_facts, rejected R38-RC-A/B, R38T-G5, R38T-H2; 10:38Z; REPORT.md write refused), 4 `scan_*.json`, 17 `v_*.json`. Poll headers to 10:48:46Z (`experiments/lb_poll/poll.log` l.30454; exp89t PENDING); e10 RUN 46 10:42Z 8/8, signals 0 (`experiments/e10_watch/watch_loop.log`; `20260929T1041Z.txt`). `experiments/RESULTS.md` unchanged (ends at P46).

**LB:** no new score. P55 exp89t (56669888) PENDING (L > 1.8 h at 10:48:46Z). V_pub stays exp87a 0.959; rank #141 of 3,991 at 10:42Z, 17th of 21 in the 0.959 block (`experiments/e10_watch/20260929T1041Z.txt` l.1166-1168; `FACTS.md` F-LB-38 l.271). 4 of 5 submits used today.

**Ideas** (`IDEAS.md` CHANGES (38) l.228; `ideas.json` meta.curations[-1], 28 records; `_curation/38/ideas.json`):
- **New I-583..I-587:** in-plan at-risk I-583 card v3 (R38-A1), I-584 E10 after 12:00Z = verify + MSK push (R38-A2 (d)), I-586 19:44:45Z manual-admit list (R38-A6); in-plan conditional I-585 slot-2-yes UP arming (R38-A3); refuted I-587 S1 re-saves (R38T-H2).
- **Status moves:** I-548 mc31v card numbers in-plan -> refuted (R38T-G5). I-576 logged 09:57Z as pointers (kill rejected); I-578 superseded by I-583; I-577 17:40Z job flawed -> R38-A4; I-579 re-carried as R38-A2 (a); I-580 extended to T0-T8 (R38-A5). Rechecks upheld: I-535 running champion unchanged, I-297 #38 stays out, I-490 masking relaxation.
- **Counts c37 -> c38:** 582 -> 587; refuted 271 -> 273, in-plan 166 -> 169; lb-tested 65, lab-tested 28, deferred 50, open 2 unchanged. At-risk 16 -> 16 (off I-548, I-576, I-578; on I-583, I-584, I-586); strict orphan I-233 (`IDEAS.md` ORPHANS l.950).

**Facts and decisions** (`FACTS.md`, `DECISIONS.md` rows marked [c38]; `_curation/38/facts.json`; state 10:45Z):
- **New facts:** F-LB-38 LB at 10:14Z + feed false positive (l.271); F-RUN-57 poller cadence ~602 s, armed jobs, pre_exp89t weak spot (l.333); F-RUL-38 09:57Z / 10:00Z logged decisions (l.376); F-TRN-72 exp89t dummy-lab +0.00089 is not private evidence (l.513); F-TRN-73 #37 beats #38 as partner iff x > 0, P ~0.85 (l.514).
- **Contradictions:** new C-304..C-314 (l.823-833): card v2 Satwik line, stale header/rank, slot-2 clause, 22:45-23:00 MSK band, 17:40Z job, masking conflict, missing R37-A6 addendum, KEY FACTS stale, and others; [c38] notes on C-297..C-301.
- **DECISIONS.md:** P55 cells (l.207), §1 [c38] (l.562); §2 snapshot 10:45Z, still TICKED #37 + #38, П3 recommended (l.999-1001); §3 4 new rows: ROUND 37 APPLIED, feed false positive, R38-A1..A7 PROPOSED, round-38 rejections (l.1787-1790); changelog (l.2000).

**Watchlist** (`WATCHLIST.md`, ~10:45Z; `_curation/38/watch.json`): done W338 (09:19Z slot-2 status), W339 (timers as pointers), round 37 commit, 09:58Z feed run; new W346-W353, C10-C13, T219-T223, I419-I429; still open W126 (RESULTS rows), W296 (REPORT.md rounds 29-35, 37, 38).

**Alerts** (`INDEX.md` TOP ALERTS, 11 after dedup):
- **Resolved since curation 37:** stale timers (handled as log-only pointers, 09:57Z); R37-A1 slot-2 status sent 09:19Z; S0 and card plans logged; round 37 committed (66f1eeb); 0.9812 E10 flag closed (135788c).
- **New:** card v2 flawed -> card v3 [now]; 12:00Z single CONTEXT entry R38-A2 incl. R37-A6 addendum and E10-after-12:00Z policy [today]; 17:40Z pre_exp89t job fragile -> re-arm [today]; exp89t playbook T0-T8 + RECOMMENDED PAIR + 19:44:45Z script [today]; KEY FACTS stale [today]; slot-2 masking conflict [info]; ready #38-partner answer and T7 anomaly check [before-finals]; kaggle_feed not competition-scoped [info].
- **Carried over:** slot-2 11:50Z / 12:00Z UNUSED log [now]; finals tick 20:00Z with 'tick now' line, SELECTED checks, hindsight guard / I-252 / I-407 before 23:00Z [before-finals]; RESULTS rows P47-P55, REPORT.md rounds 29-35, 37, 38 [after the tick].
- **Dropped from the top list:** battery / charger (c37 alert 10) and П2/П3 break-even caption (c37 alert 11): no curator re-raised them in c38; I-581 stays in `IDEAS.md`.
- **Curator disagreements settled here:** exp89t playbook: facts / ideas [today] vs watch [today] + [before-finals] -> [today] (logging due before 17:53Z); RESULTS / REPORT.md: watch [today] vs ideas [today, after the tick] -> after the 20:00Z tick, as in c37.
