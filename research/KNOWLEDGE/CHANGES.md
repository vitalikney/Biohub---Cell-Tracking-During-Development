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
