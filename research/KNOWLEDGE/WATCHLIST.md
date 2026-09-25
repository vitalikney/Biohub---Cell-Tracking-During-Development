# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-25 23:05 UTC (curation 3; incremental update of the 20:50 UTC curation-2 build).

Sources:
- `CONTEXT.md` §14 up to the 22:06 UTC entry (git HEAD 1ca747b)
- `experiments/lb_poll/ledger.md` (22:53:06Z) and `poll.log` (last block 22:53:04Z)
- `experiments/RESULTS.md`
- `research/wf_ideas_v4/round2/report.json`, now committed in 4f5d325
- `research/wf_ideas_v4/round3/report.json` and `report.notes.md`: round 3 finished 22:59Z; **untracked**; it wrote no REPORT.md
- `research/wf_ideas_v3/FINAL_REPORT.md`, `TASK_LOCAL_SESSION.md`, `TASK_CLOUD_SESSION.md`, `TASK_FRIEND_A.md`, `NEXT_RESEARCH.md`
- `research/wf_ideas_v4/FINAL_REPORT_v4.md`
- `tools/`, `experiments/lb_poll/lb_poll.py`, `experiments/workflows/biohub-research-round.js`
- the memory files `MEMORY.md` and `project-lb-probe-approval.md`

All times are UTC. The IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, cancelled.

**State in one line.** The user gave the OK on AMENDMENT f2 at 22:06 (`CONTEXT.md` 22:06), and the twin dummy gates PASS (`CONTEXT.md` 20:55). At **00:01 on 26 Sep** two submissions go in:
- K2 = `exp58` v1, as probe 37;
- the twin = `exp58n` v1, as probe 38.

The default finals are F1 = K2 and F2 = twin, with P ~0.85-0.9 (`round3/report.json` R3-A9). Every rider gate has failed. S4-S11 stay empty, except K1 (only through the READ TABLE, with an OK) and an optional S12 floatout (with an OK). P36 is still PENDING and counts as info only.

**Changes since 20:50:**
- Done: W30 (ADDENDUM M was recorded post-hoc at 20:55, and round2/ was committed in 4f5d325), W12/W17 (twin gates pass), W21 item (1) (the f2 OK).
- Partial: W31 (the round-2 closures are in CONTEXT 20:55).
- Superseded by round 3: W06, W15 and W18.
- Resolved: I16, I20.
- New: W36-W43 and I21-I30.

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| W38 | **Round 3 is untracked, and neither round has a REPORT.md.** (1) Commit `research/wf_ideas_v4/round3/`. (2) Save the Russian text from `round3/report.json` key `report_md_ru` (and the round-2 text) as the REPORT.md files. (3) `CONTEXT.md` 20:55 cites `research/wf_ideas_v4/round2/REPORT.md`, but that file does not exist. Fix the citation or create the file | not started | with the RESUME POINT (W40), ~00:15 26 Sep | `git status` 23:00 (`?? research/wf_ideas_v4/round3/`); `ls research/wf_ideas_v4/round2` (no REPORT.md); `round3/report.notes.md` 22:50Z, 22:56Z |
| W02 | Friend A "Task 0" reply: is he available 26-28 Sep, is the 5070 Ti free, how many sasyami GPU hours does he have, can he run shard B? | overdue (still awaited: no commit, no CONTEXT note) | 25 Sep 18:00 | `research/wf_ideas_v3/TASK_FRIEND_A.md` l.17-22; `git log -- PROMPT_FRIEND_A.md` (last fea74ea 16:41 +0300) |
| W03 | **The friend A card is fully stale.** It still tells him to run exp60 shard B on sasyami by 08:00 26 Sep, although both shards finished at 20:05. It also still has tempfuse LOEO by 06:00 27 Sep, and K4 is dropped. Add a top "cancelled" block, as was done for friend C (14c339e) | overdue | now (his coordination deadline was 23:00 25 Sep) | `TASK_FRIEND_A.md` l.31-65; `CONTEXT.md` 20:05, 20:55 (M6); the top block of `PROMPT_FRIEND_A.md` is still the 14:30 one |
| W04 | Admission table in CONTEXT, updated after every score. Columns: file, public, latency, R5, riders, F1/F2 candidate. The READ TABLE (W39) covers the decision logic but not the table itself | overdue | after each score; final version 28 Sep 22:00 | `TASK_CLOUD_SESSION.md` T13; `FINAL_REPORT.md` §d; `grep -i admission CONTEXT.md` finds nothing |
| W05 | Commit `experiments/ext_corwin-biocel-aux/` and `experiments/ext_y3uanm-secondary-ft/` without `__pycache__`. FINAL_REPORT_v4 §2 cites both | overdue (still untracked) | 25 Sep | `git status` 23:00 |
| W06 | Record in CONTEXT that hidden reruns do not consume GPU quota. Round 3 has the numbers: +2.28 h used 13:58-18:12, against ~4.8 h of #34/#35/#36 reruns in that window. CONTEXT l.1746 still says "unverified" | overdue; the round-3 text is ready (R3-A6 (c)) | with the RESUME POINT (W40) | `round3/report.json` R3-A6, new_facts (10); `CONTEXT.md` l.1744-1746 |
| W07 | forkmid dose output files (`experiments/forkmid_dose/`) | overdue, but moot: forkmid is closed (`CONTEXT.md` 20:35). Suggest closing it in CONTEXT | - | `TASK_LOCAL_SESSION.md` §7; the folder is absent |
| W34 | **Memory pointers are stale.** (a) The `MEMORY.md` "Resume point" line says "latest 25 Sep 10:20 UTC ... just above ## 9". That block (CONTEXT l.1519) has a WRONG finals line (see I30). (b) The body of `project-lb-probe-approval.md` says "K2 ... ~00:55 UTC" and "f2 APPROVED ~21:00 UTC", but CONTEXT says 00:01 and 22:06. (c) Round 3 found the index line itself current, so curation 2 was wrong on that point. This is for the main session only | overdue (partial) | right after the 00:01 submits | `round3/report.json` R3-A5, rejected (PC3-07 sub-claim); memory files as read 23:00 |

## NEXT 24 H (25 Sep 23:05 -> 26 Sep 23:05 UTC)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W36 | **23:15-23:55 tonight**, else after ~09:30 26 Sep; **never 06:00-09:30** | Poller window. `experiments/lb_poll/lb_poll.py` l.28 keeps only `splitlines()[:12]`, which is header + 5 rows. A pending K build drops out of the log after 4 newer submissions, and then its COMPLETE is never seen. Change it to `[:60]` and restart only in a quiet window. Within 1 min, check that a new block with more than 5 rows appears, then run `python tools/runtime_ledger.py --print`. If you cannot check it, leave the poller alone: tonight's 5 rows are enough | not started (`lb_poll.py` l.28 unchanged, last commit 597eec3) | `round3/report.json` R3-A4, new_facts (7) |
| W14 | 23:48 (7.5 h mark) and at the 00:01 submit | P36 = exp57 v1: still PENDING at 22:53Z, L > 6.58 h. It is INFO ONLY and cannot trigger a rider. Record its state at the K2 submit: if P36 is still pending, L(K2) may include queue time. When it scores, log it in RESULTS.md l.69 and in CONTEXT | in progress | `ledger.md` 22:53Z; `CONTEXT.md` 19:05 (b); `round3/report.json` R3-A6 (e) |
| W16 | **00:01:00-00:10 26 Sep** | **Submit K2, then the twin** (5 slots on 26 Sep). First list the submissions; only P36 may be PENDING. Then submit `-k vitaliineibauer/biohub-exp58-x138-safe-lowref -v 1 -m 'probe 37: exp58 = K2 ...'`. Then submit `-k vitaliineibauer/biohub-exp58n-x138-safe-lowref -v 1 -m 'probe 38: exp58n = K2 twin ...'`. The FIRST exp token of each message must be exp58 or exp58n. **Do not re-push either kernel**, because v1 is the gated version. Then run `python tools/runtime_ledger.py --print` and check that it shows K2 = safetail (9.5 h) and twin = safetail_noins. No `--k2/--family` flags are needed (this supersedes R2-A4). Log the refs, the submit times and "pre-approval (3) + f2 OK 22:06" in CONTEXT. The local session must be awake, because there is no scheduled submit | not started (approved) | `CONTEXT.md` 22:06; `round3/report.json` R3-A1; `ledger.md` WATCH A5-L(K2) |
| W39 | right after the submits; **hard limit before the first K2/twin score (~06:00)** | **The K2/TWIN READ TABLE goes into CONTEXT and is committed before any score appears in poll.log.** It sets d1 = K2 - #35 (0.954) and d2 = twin - #34 (0.953). K2 is "clean" iff L(K2) upper bound <= 8.0 h (COMPLETE seen by ~08:01Z). It has 5 first-match rows, and the [OK] rows need the user. Without it the R3 reference is undefined: 0.952 passes against #34 and fails against #35. Copy the text verbatim from the end of `round3/report.json` plan_issues | not started (`grep "READ TABLE" CONTEXT.md` finds nothing) | `round3/report.json` R3-A2, plan_issues |
| W40 | right after the submits; before the ~00:45 round and before any compaction | **RESUME POINT 26 Sep 00:1x.** Make it the last RESUME POINT block: facts and pointers only, the f2 text quoted verbatim, and a pointer to the READ TABLE. Mark the 25 Sep 10:20 block "SUPERSEDED (its finals line is wrong)". Add "STALE (6 Sep)" under §10. Put the S4-S6 empty line here (W37), plus W06 and W41 (a)-(c). Update the memory pointers (W34) | not started | `round3/report.json` R3-A5; `CONTEXT.md` l.1519-1532 (stale finals), l.109 (§10 from 6 Sep) |
| W37 | before round 4 (~00:45) | **Stop the drift in the workflow prompt.** `experiments/workflows/biohub-research-round.js` l.34 (plancheck) still says "K3 = K2 + forkmid and K3b = DeepCenter threshold builds ... slots S4-S6", and l.54 (report) still lists "riders K3 / K3b / K4 / N1" as pre-approved. Every later round will propose the closed riders again. Also add a CONTEXT line saying S4-S6 carry no rider by the T9 read | not started (both lines unchanged at 23:00) | `round3/report.json` R3-A3, plan_issues PC3-03 |
| W10 | ~00:45, ~03:15, ~05:45 | Research rounds 4-6. Round 3 is done (22:59Z). Round 4: confirm that K2 and the twin are PENDING under the right refs, and that W39/W40/W37 are committed; a light browser delta; no new mechanism mining. Rounds 5-6: the score-read procedure, the morning brief and the finals-tick checklist. Consider making them monitoring only | round 3 done; 4-6 pending | `round3/report.json` next_focus |
| W41 | (a)-(c) with W40; (d) when the scores arrive | **Runtime records.** (a) F(K2) = 7.87 h, inside the 818-1179 s start-up noise and just below the 7.9 h A5-F trigger. (b) R5(b) margin to 9.5 h = 1.63 h, so K2 and the twin are admissible unless they ERROR, and "K2 fails R5" is not a K1 trigger. (c) = W06. (d) Record L(K2), L(twin) and L(K2) - L(twin), which bounds the hidden insertion cost. Word it as "L(K2) <= 8.0 h => the insertion deadline never fired", NOT "the insertion ran on every clip" | not started | `round3/report.json` R3-A6, new_facts (9) |
| W15 | ~00:05 26 Sep | GPU quota check: **downgraded to optional**. Nothing consumes it any more: no GPU push tonight, whatever it shows | optional | `round3/report.json` R3-A6 (c), PC3-08; `CONTEXT.md` l.1545, 1816 |
| W18 | - | Forecast F: round 3 computed it by hand (7.87 h), but `--forecast-h` is still not wired into the ledger. It matters only if a rider dummy appears | partial / low | `ledger.md` INFO A5-F; `round3/report.json` new_facts (9) |
| W19 | **~06:00-09:31 26 Sep** | Keep the poller alive. K2 COMPLETE seen by **08:01** means "clean" (the insertion deadline did not fire). L(K2) <= 9.5 h by 09:31 proves R5(a). If the poller died, R5(b) still admits K2 (I11, W41 (b)). Do NOT restart the poller in this window (W36) | poller running (22:53Z, 0 gaps > 15 min) | `ledger.md`; `round3/report.json` R3-A4, new_facts (5) |
| W21 | ~05:00-09:00 26 Sep (user wakes); **before the first score is acted on (~06:30)** | **Morning OK list (R3-A9)**, each item with the READ TABLE row that triggers it. (1) K1 = exp58t v1, only if K2 ERRORs or the table removes lowrefine (row 4, or row 5 with d2 <= -0.002). Never at d1 = -0.001. Its message starts "probe NN: exp58t". (2) A 0.952 twin floor while lowrefine is kept. (3) twin - K2 >= +0.002 means F1 = twin; the user confirms F2 now. (4) If lowrefine leaves F1 and there is no K1: F1 = twin instead of §f item 4 (#34). (5) Optional floatout S12 (W33). (6) A deadline move or D4, only if the runtime trigger fires. Say plainly that the default world is F1 = K2, F2 = twin, S4-S11 empty. The f2 item is DONE (22:06) | not started | `round3/report.json` R3-A9; `CONTEXT.md` 22:06 |
| W20 | when K2 and the twin score (~06:30-10:00) | Read the scores **mechanically, by the READ TABLE** (W39), which supersedes the "accept >= 0.953, drop <= 0.952" wording. Take d1, d2 and "clean" from `ledger.md`. Record K2's rank inside its block against #35 (18th of 65) as INFO ONLY (R7) | pending | `round3/report.json` R3-A2, R3-A7 |
| W22 | with W40; ~09:00 26 Sep | Intel line. Latest (22:16-22:23): **#164/3,914**; 0.954 block = 147-211 (we are its 18th); silver ~196 is inside the block, 32 ranks below us; the 7 ranks lost since 19:46 went to teams rising to >= 0.955. The 19:46 line is in CONTEXT (20:55); the 22:16 line is not | partial | `round3/report.json` R3-A7, new_facts (1)-(2); `CONTEXT.md` 20:55 |
| W23 | every ~6 h (next ~04:30) until 29 Sep 07:00 | x138 successor watch (E10): a public notebook >= 0.956, or a spike of >= 10 teams at one score >= 0.956. Last check 22:16-22:43 found nothing: no notebook run since 09:09, x138 still v1 (260 copies), no new discussions | in progress | `round3/report.json` new_facts (4); `TASK_LOCAL_SESSION.md` §9 |
| W25 | 26 Sep | Slots: S2 = K2 and S3 = twin, both at 00:01. S4-S6 are empty by the T9 read. K1 goes in only through the READ TABLE with an OK. Unused slots are not burned | resolved; the CONTEXT line is W37 | `CONTEXT.md` 20:35, 22:06; `round3/report.json` R3-A3 |
| W31 | **by 26 Sep 12:00** | Closures into CONTEXT/curator. **Done at 20:55:** ANTIPAR, DNVETO, I-072, K4 (M6), M5. **Still open:** (1) the R2S-6 info-only note. (2) Round-3 closures R3-A8: swapfix/I-165/I-166 (0 of 555 true swaps); clip-boundary rescue I-145 (SELECTION 0.00000); the lab calibration rule for node-adding arms (I23); axis-flip I-151 (base-dependent sign, user refusal R9); tail-bug fixes, retention hysteresis and density-gated insertion (all closed); "x138 tail saturated" (I21). (3) The M6 reopen clause lapses at 18:00 today; note that | partial | `CONTEXT.md` 20:55; `round3/report.json` R3-A8, rejected |
| W35 | 26 Sep (with W31) | RESULTS.md: add a one-line exp60 lab note (or a pointer to `experiments/exp60_trainlab/results.md`). Add rows for probe 37 (K2) and probe 38 (twin) at the submit, and fill in probe 36 when it scores | not started | `experiments/RESULTS.md` l.67-69 |
| W26 | 26 Sep ~09:30 | Day-2 cloud research (`NEXT_RESEARCH.md`, ~$10-12 budget). The night rounds have effectively superseded it. Record "superseded / cancelled" in CONTEXT | not started (no CONTEXT mention) | `research/wf_ideas_v3/NEXT_RESEARCH.md`; `grep -i "day-2\|NEXT_RESEARCH" CONTEXT.md` finds nothing |
| T12 | 26 Sep 18:00 | The M6 reopen window for K4/tempfuse closes: it needed tempfuse=0 byte-identity plus an honest LOEO-44b6 >= +0.003. Nobody owns it, so it lapses. Note it in CONTEXT | pending (expected lapse) | `round2/report.json` M6; `CONTEXT.md` 20:55 |

## LATER (26 Sep 23:05 -> 29 Sep 23:59 UTC)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T02 | 27 Sep ~09:00 | LB snapshot + rank line (compare with #164 at 22:16 25 Sep) | `FINAL_REPORT_v4.md` §3 item 8; `round3/report.json` new_facts (1) |
| W33 | code by **27 Sep 12:00** (R8); only with the user's OK (R3-A9 item 5) | floatout on x138: port `--patch floatout` to `cells_src[CELL['post']]`. **Make FLOATOUT_CHECK fail-soft**, because the bare assert at `tools/build_probe_kernel.py` l.1315-1362 would kill a hidden rerun (R7). Add a FORCE_FAIL test. It goes on the F1 line only, rides only in S12, and never on the twin. Write "public tie expected" in CONTEXT before any score | `round2/report.json` R2-A9, new_facts (12); `round3/report.json` R3-A9 |
| T03 | **27 Sep 12:00** | **R8: no new mechanisms after this.** In practice the search is already over: the tail is saturated and every rider gate has failed. S7-S11 stay empty, except K1 per the READ TABLE and S8 for an x138 successor (E10) | `CONTEXT.md` 13:38 R8; `round3/report.json` plan_issues STRATEGIC |
| T04 | **28 Sep 12:00** | S12: consolidate F1-final, only if accepted riders sit in different files (at most K2 + floatout). Gate = the union of the dummy gates, plus "FLOATOUT CHECK PASSED" and floor == integers on 100% of rows. The file JOINS the candidates. Do NOT rebuild the twin | `CONTEXT.md` 13:38 S12, 18:20 f2 |
| T05 | 28 Sep 16:00 | S13: repeat S12 on error | `CONTEXT.md` 13:38 |
| T06 | 28 Sep 22:00 | Final admission table (W04) | `FINAL_REPORT.md` §d; `TASK_CLOUD_SESSION.md` T13 |
| T07 | 28-29 Sep | Risk: queue latency > 10 h. Other teams' reruns took 7-10 h. If it happens, R5(b) decides | `FINAL_REPORT.md` §g item 6; `round3/report.json` new_facts (2) |
| T08 | 29 Sep 02:00 (hard edge 10:00) | After 02:00 only S17 (an emergency repeat of F1-final) | `CONTEXT.md` 13:38 R8, S17 |
| T09 | 29 Sep ~11:30 / **12:00** | Draft the finals-tick checklist at 11:30 (F1/F2 by the READ TABLE rows). Remind the user at 12:00 to tick manually | `TASK_CLOUD_SESSION.md` T13; `round3/report.json` next_focus; memory `project-lb-probe-approval.md` |
| T10 | **29 Sep 20:00** | The USER ticks the finals. Default: F1 = K2 (or the S12 file if built and admitted), F2 = exp58n twin if it scored without error, is R5-admissible and >= 0.953 (f2 OK 22:06). Otherwise use the READ TABLE rows, then exp52. #34 is the last resort before exp52. Never tick exp56 while an admissible non-copy x138-family file exists, never tick two files with identical components, and never auto-select | `CONTEXT.md` 18:20 f2, 22:06; `round3/report.json` plan_issues READ TABLE |
| T11 | 29 Sep 23:59 | Competition deadline | `CONTEXT.md` §1 |
| W28 | idle only | T12 / C09 head-shift scale check | `TASK_CLOUD_SESSION.md` T12 |
| W29 | after 29 Sep | E14: friend A's honest out-of-embryo A/B. It is fed by the error anatomy (I06, I21, I22) and by DeepCenter t* (I19) | `TASK_FRIEND_A.md` "Задача 4" |

**Done or cancelled since 20:50 (for the record):**
- W30 done: ADDENDUM M was recorded as post-hoc NOTES with an honest sequence note (`CONTEXT.md` 20:55), and round2/ was committed (4f5d325). The missing REPORT.md moves to W38.
- W12/W17 done: the twin dummy gates PASS (nodes 121,252 identical; K2 = twin + 12 inserted edges - 5 stolen edges; repair 219 s vs 509 s) (`CONTEXT.md` 20:55).
- W21 (1) done: the user's OK on f2 (`CONTEXT.md` 22:06).
- Earlier: W01, W08, W09 and W11 done; W13, W24, W27 and T01 cancelled (see the curation-2 build, `research/KNOWLEDGE/_curation/2/watch.json`).

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| I01 | "Of x138's forks, 24% (15/62 on the dummies) are one-blob duplicates at t+1, against 2% of GT divisions" | `research/wf_ideas_v4/lens_literature.json` plan_critique 1-2 | The main fact for division work after 29 Sep. Forkblob, ANTIPAR and forkmid all failed to exploit it |
| I02 | "1 of 10 lab gains transferred ... a lab-based slot decision is allowed only for arms whose learned inputs are out-of-sample" | `research/wf_ideas_v4/lens_mine-old.json` plan_critique (4) | The insertion lab +0.0157/+0.0090 is in-sample (L5). Never cite it as value |
| I03 | Hidden reruns do not consume GPU quota | `lens_redteam-plan.json` RT1; `round3/report.json` new_facts (10) | Still not in CONTEXT (W06) |
| I04 | "DeepCenter score recorder and the TRAINLAB summary cell are not fail-soft ... 7 of 17 44b6 picks are leak-siblings" | `CONTEXT.md` 14:29 (T5) | 44b6 lab deltas are partly in-sample |
| I05 | "K2 forecast <= 7.86 h ... the insertion gate at 8.0 h is only +0.14 h above that ... do NOT move it later on its own" | `lens_headroom.json` critique (2); refined to 7.87 h in `round3/report.json` new_facts (9) | This is why "clean" (W39) is not guaranteed. L(twin) is the paired control (W41 (d)) |
| I06 | K2 dummy vs train GT: "FN 82 of 2,127 GT edges. 50% are swaps, 23% one-free-end fragments, 6% end-anchored node misses" | `lens_mine-old.json` critique (3) | Not in CONTEXT. It conflicts with I21/I22, which come from a bigger bed where the "swaps" are really node misses. Reconcile the two before any work after 29 Sep |
| I07 | "lowrefine is not a coordinate-only rider ... +33 final nodes, +29 edges and +1 fork" | `lens_redteam-plan.json` RT2 | The READ TABLE uses d1/d2 to read lowrefine, and this is why d2 exists |
| I08 | Kernel time is not a hidden-test budget signal; use the per-dataset `[ds] repair` lines | `research/wf_ideas_v3/FINAL_REPORT.md` §j item 19 | Start-up noise between identical kernels is 818-1179 s (`round3/report.json` new_facts (9)) |
| I09 | "Блок 0.953 на private останется единым" is untested | `FINAL_REPORT.md` §g item 13 | A third window in a row shows late 0.953 risers at the END of the block: 16 more at ranks 460-486 (`round3/report.json` new_facts (3)). This backs "never tick a verbatim x138 copy" |
| I11 | "R5(b) ... admits K2 even if the overnight poller fails" | `lens_redteam-plan.json` RT2 (4) | The margin is now quantified at 1.63 h (W41 (b)) |
| I12 / I18 | The silver line (~196) sits INSIDE the 0.954 block. We fell from 38 ranks above it (19:46) to 32 above it (22:16) | `round2/report.json` new_facts (2); `round3/report.json` new_facts (1) | At ~2.4 ranks/h (6 ranks in 2.5 h) we reach the line in ~13 h if teams keep rising. Only the 19:46 line is in CONTEXT (W22) |
| I14 | Stale operational text: `TASK_LOCAL_SESSION.md` "Кто ты" and `TASK_FRIEND_A.md` l.52 name branch `claude/practical-meitner-31k9ye`, but the work lands on `main` | those files | Same risk as W03 |
| I15 | "The public read over-rewards fork REMOVALS whose precision lies between the private break-even (0.11-0.20) and 0.265" | `round2/report.json` plan_issues "Structural (R2-RC-B)" | CONTEXT 20:55 records only the lab break-even (7.7:1), not this public/private asymmetry. Any future removal rule needs a private break-even clause |
| I17 | "FLOATOUT_CHECK (build_probe_kernel.py l.1315-1362) is a bare-assert cell, not fail-soft" | `round2/report.json` new_facts (12) | Any NEW floatout build without the W33 fix violates R7 |
| I19 | **DeepCenter t* = 0.30 is the lab optimum** in the removal direction. 6bba div 15/11/73 vs control 15/17/73; 44b6 1/6/10 vs 1/8/10; 8 evaluable FP removed, 0 TP lost. It is NOT node-preserving (nodes -79/-49) | `experiments/exp60_trainlab/results.md` l.13-18, l.61-66 | Still recorded nowhere in CONTEXT (20:35 gives only "t* = 0.30 ... NO K3b"). Do not act before 29 Sep (R8); keep it for later |
| I21 | "The x138 tail is saturated. Edge FN 1,705 of 40,093 = node misses 834 (49%), swaps 730 (43%), dangling ends 141 (8%), with 0 mutual-nearest end->start pairs within 7 um. The remaining error mass needs retraining" | `round3/report.json` new_facts (13), R3-A8 (6) (untracked) | This is the reason to STOP mining post-processing. If it is not recorded (W31), new chats will mine closed classes again |
| I22 | "There are 0 true 2x2 swaps ... our nodes sit 3.9-4.2 um from the GT nuclei ... 6bba holds 485 of the 555" | `round3/report.json` new_facts (14) | "Swap" errors are a detection/localization problem (detector or coordinate-head retraining), not a linking one |
| I23 | "The CONFIRMATION half reads every node-adding arm as positive (L4 +0.00099, L5 +0.00041, rescue +0.00109), while the LB read MIN_TRACK_LEN 4 at -0.002" | `round3/report.json` R3-A8 (3), new_facts (16) | A lab calibration rule: a node-adding arm counts only if SELECTION and CONFIRMATION agree and >= 55% of clips win, and it still takes a ~-0.002 LB discount. Belongs in FACTS/CONTEXT |
| I24 | "Evaluable precision: sparse half 8 TP / 3 FP, dense half 1 TP / 3 FP. 186 of 201 inserted forks are metric-ignored. Private harm needs out-of-fold evaluable precision < ~11% (q* = 0.114)" | `round3/report.json` new_facts (11) | This is the quantitative case for the twin hedge (F2 = no insertion). The dense-half precision (25%) is close to break-even |
| I25 | "The poller logs only the 5 newest submissions per poll (lb_poll.py '[:12]')" | `round3/report.json` new_facts (7) | Silent failure mode: on a busy day a pending K build loses its COMPLETE, so R5(a) and "clean" stay UNPROVEN for good (W36) |
| I26 | "Their last submissions were 12:24-15:33 UTC, so hidden-rerun latency is 7-10 h with no queue problem ... fits private retrained or ensembled models, which R9 bars for us" | `round3/report.json` new_facts (2) | Latency above 8 h is normal elsewhere, which makes "not clean" (READ TABLE row 5) a live branch |
| I27 | The probe.json line "compare with exp56 ... ties recorded" is builder boilerplate, not a rule | `tools/build_probe_kernel.py` l.2310; `round3/report.json` plan_issues READ TABLE | Someone reading `experiments/exp58*/probe.json` could apply the wrong reference (exp56 instead of #35/#34) |
| I28 | "GT node recall before safe divisions -> final: t0 0.959 -> 0.940, t-2 0.966 -> 0.947 ... mid 0.986 -> 0.986; boundary edge TP rate 0.926 vs 0.958" | `round3/report.json` new_facts (15) | Clip-boundary node loss is a real deficit (~2 pp). The cheap rescue failed (I-145), so the ILP start/end part is deferred until after 29 Sep |
| I29 | The retention guard has no flicker penalty: switch pairs 6.05% FN, between blended 3.17% and primary 10.71% | `round3/report.json` new_facts (17) | Closes hysteresis for good. Recording it prevents rework |
| I30 | **Contradiction:** the 25 Sep 10:20 RESUME POINT says "FINALS ...: F1 = best of {exp57b, exp56, exp51/exp52}; F2 = ... exp51 if F1 is x138-based" | `CONTEXT.md` l.1531-1532 | PRE-REG v3 §f and f2 forbid this. The memory "Resume point" line sends every new chat to this block (W34, W40) |

Resolved since 20:50:
- **I16** (dummies are plumbing evidence only; the GT divisions are 0/0/0/3) is now in `CONTEXT.md` 20:55 (M5).
- **I20** (round-2 claims overtaken) is resolved: round 3 re-read CONTEXT up to 22:06 before acting (`round3/report.notes.md` 22:50Z). The lesson carries over to W37: the workflow prompt itself is stale.
- **I10** and **I13** were resolved in curation 2.
