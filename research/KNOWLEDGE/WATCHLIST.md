# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-25 20:50 UTC (curation 2; incremental update of the 18:30 UTC v4 build). Sources: `CONTEXT.md` §14 up to
the 20:35 UTC entry (git HEAD da154cb), `experiments/exp60_trainlab/results.md`, `results_forkblob.md`,
`experiments/lb_poll/ledger.md` + `poll.log` (last poll 20:42:40Z), `experiments/RESULTS.md`,
`research/wf_ideas_v4/round2/report.json` + `report.notes.md` (round 2, finished 20:42 UTC; its REPORT.md was never
written, see W30), `research/wf_ideas_v3/FINAL_REPORT.md`, `TASK_LOCAL_SESSION.md`, `TASK_CLOUD_SESSION.md`,
`TASK_FRIEND_A.md`, `TASK_FRIEND_C.md`, `NEXT_RESEARCH.md`, `research/wf_ideas_v4/FINAL_REPORT_v4.md`, and `tools/`.
All times are UTC. The IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done / in
progress / overdue / not started / cancelled.

State in one line: exp60 lab read at 20:35. It gives NO K3 (forkmid fails its power clause), NO K3b (t* = 0.30 >
0.25), forkblob CLOSED (20:05), and K4/tempfuse DROPPED by default. So **F1 = K2 (exp58)**, and it goes at 00:01 on 26
Sep (pre-approved, 18/18 gates). The live levers are the F2 twin exp58n (its dummy was pushed ~20:35 and needs the
user's OK on f2) and an optional floatout rider (needs an OK). P36 is PENDING and is info-only
(`CONTEXT.md` 19:05 (b), 20:05, 20:35; `research/wf_ideas_v4/round2/report.json` plan_issues "STRATEGIC CONSEQUENCE").

Changes since 18:30: W01, W08, W09 and W11 are done; W13, W24, W27 and T01 are cancelled; I10 and I13 are resolved.
New: W30-W37 and I15-I20.

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| W30 | **ADDENDUM M was never recorded, and round 2 is untracked.** Round 2 wanted ADDENDUM M (M1-M6) committed to CONTEXT "BEFORE anyone opens the DeepCenter section of the exp60 T9 results". The T9 results were opened and committed at 20:35 (da154cb), 7 min BEFORE round 2 finished (report.json 20:42). The M text is not in CONTEXT, `research/wf_ideas_v4/round2/` is untracked, and its REPORT.md was blocked by the harness. What to do now: record M in CONTEXT as a **post-T9** entry, saying so honestly. M1/M2 are tightenings and do not change the verdict (t* = 0.30 means no build under every reading). M3-M6 (ANTIPAR one-shot FAIL, DNVETO closed, the 7.7:1 break-even, dummies = plumbing only, the K4 reopen clause) stay valid. Then commit round2/ and save the RU REPORT.md text from report.json | overdue | was "<= 21:15 UTC 25 Sep" | `round2/report.json` actionable R2-A1, R2-A2; `round2/report.notes.md` 20:40; `git log` da154cb 23:35 +0300 = 20:35 UTC; `grep "ADDENDUM M" CONTEXT.md` finds nothing; `git status` `?? research/wf_ideas_v4/round2/` |
| W02 | Friend A "Task 0" reply (available 26-28 Sep? 5070 Ti free? sasyami GPU hours? can he run shard B?) | overdue (still awaited; no commit or CONTEXT note) | 25 Sep 18:00 | `research/wf_ideas_v3/TASK_FRIEND_A.md` l.17-22; `git log -- PROMPT_FRIEND_A.md` (last 16:41 +0300 fea74ea) |
| W03 | **The friend A card is now fully stale.** Task 2 (exp60 shard B on sasyami, "не позже 08:00 UTC 26.09", path `experiments/exp60_x138_trainlab/sasyami_b`, branch `claude/practical-meitner-31k9ye`) is obsolete: both shards finished at 20:05. Task 3 (tempfuse LOEO by 06:00 27 Sep) is dead because K4 was dropped. Add a top block to `PROMPT_FRIEND_A.md` like the friend C one ("ШАГ 0 C08 ОТМЕНЁН", 14c339e), so he does not burn sasyami quota | overdue (his "беру шард B" coordination deadline was 23:00 25 Sep) | now | `TASK_FRIEND_A.md` l.31-53, 55-65; `CONTEXT.md` 20:05 (both shards COMPLETE), 19:05 (f) (K4 dropped); `PROMPT_FRIEND_A.md` top block is still the 14:30 one |
| W04 | Admission table in CONTEXT (file, public, latency, R5, riders, F1/F2 candidate), updated after EVERY new score | overdue (#34/#35 scored and no table; `experiments/lb_poll/ledger.md` covers the latency/R5 columns only) | after each score; final table 28 Sep 22:00 | `TASK_CLOUD_SESSION.md` T13; `FINAL_REPORT.md` §d; `grep -i "admission" CONTEXT.md` finds nothing; `ledger.md` |
| W05 | Commit `experiments/ext_corwin-biocel-aux/` and `experiments/ext_y3uanm-secondary-ft/` (cited by FINAL_REPORT_v4 §2). Leave out `__pycache__` | overdue (still untracked) | 25 Sep | `git status` 20:50 UTC |
| W06 | Record the quota evidence. Hidden reruns do not consume the GPU quota (18:56 -> 21:13 used while the #35/#36 reruns ran). CONTEXT l.1746 still says "unverified". Fold this into the 00:05 quota check (W15) | overdue | with W15 at the latest | `CONTEXT.md` l.1744-1746; `research/wf_ideas_v4/lens_redteam-plan.json` RT1; `round2/report.json` R2-A5 |
| W07 | forkmid dose output files (`experiments/forkmid_dose/`) | overdue (minor; the numbers are in `CONTEXT.md` 14:29, and forkmid is now closed) | - | `TASK_LOCAL_SESSION.md` §7; the folder is absent |
| W34 | Memory index pointer is stale. `MEMORY.md` still lists "LB probe approval: 25 Sep batch approved: exp52, exp53, exp54". The file body was updated 13:38 to PRE-REGISTRATION v3, but it does not mention ADDENDUM L, ADDENDUM M or f2, and it says K2 at "~00:55 UTC" while CONTEXT says 00:01. Main session only | overdue | 25 Sep | `round2/report.json` R2-A12 (PC2-16); memory `project-lb-probe-approval.md` |

## NEXT 24 H (25 Sep 20:50 -> 26 Sep 20:50 UTC)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W12 / W17 | **~21:20-21:40 (twin dummy returns)** | Read the exp58n twin dummy with the f2 gates: (a) node rows (id stripped) == the K2 dummy; (b) edges differ from K2 only at K2's DIVINS inserted/steal forks; (c) LOWDET and LOWREFINE lines == K2; (d) no DIVINS lines; (e) no DEADLINE / REPAIR FAILED / LOWREFINE FAILED; (f) kernel time <= the K2 dummy. **`tools/dummy_gates.py` has no `--twin` mode** (args l.72-78: ref56/ref57b/k2/k1/fd/ff/insertion). Write it before the output is read. Log the verdict in CONTEXT | dummy in progress (pushed ~20:35); gate code not started | `CONTEXT.md` 18:20 f2, 20:35; `round2/report.json` R2-A3 (PC2-01); `tools/dummy_gates.py` l.71-78 |
| W10 | ~22:15, ~00:45, ~03:15, ~05:45 | Research rounds 3-6. Round 3's focus in round 2's next_focus (1) is already overtaken: T9 has been read. Replace it with the twin read, the K2 checklist, the morning OK list and the browser delta | round 2 done 20:42; round 3 pending | `CONTEXT.md` 17:55; `round2/report.json` next_focus |
| W14 | ~23:48 (7.5 h mark) | P36 = exp57 v1 (submitted 16:18:09, PENDING at 20:42:40Z, L > 4.40 h). **INFO ONLY** (rule of 19:05 (b)): no leaf-prune rider whatever the delta. Log the score, latency and delta vs #35 in RESULTS.md l.69 + CONTEXT | in progress | `experiments/lb_poll/ledger.md`; `CONTEXT.md` l.1905-1907; `experiments/RESULTS.md` l.69 |
| W15 | 00:00 26 Sep, check ~00:05 | Daily slots reset (5/day). GPU quota reset expected but UNCONFIRMED. Check Settings and record in CONTEXT (with W06). With no reset (~5 GPU-h left): the twin dummy has priority, and nothing else needs GPU now (K3/K3b/L6 are gone) | pending | `CONTEXT.md` l.1545, 1816; `round2/report.json` R2-A5 |
| W16 | **00:00:30-00:05 26 Sep** | Submit K2 = `vitaliineibauer/biohub-exp58-x138-safe-lowref` **v1** (the dummy-gated version; do not re-push). **The -m must START with `probe 37: exp58 ...`**: the runtime ledger takes the family from the first exp token, and "exp56"/"exp57b" first would misclass K2 as x138 (7.5 h). Then run `python tools/runtime_ledger.py --k2 <ref> --family <ref>=safetail` and check that ledger.md shows "safetail (9.5 h)". Log the submit time. No scheduled-submit script exists, so the local session must be awake | pending | `CONTEXT.md` 13:38 (decision 3), 17:55; `round2/report.json` R2-A4 (PC2-10); `ledger.md` A5 WATCH "K2 (exp58) not in the poll log yet" |
| W18 | before any rider dummy (no rider is pending now) | Forecast F (A5-F): `runtime_ledger.py` exists (597eec3), but `--forecast-h` is never supplied, because `dummy_gates.py` has no per-dataset repair timing output. Needed only if a rider dummy appears. Low priority now | partial (ledger done; forecast not wired) | `ledger.md` "INFO A5-F"; `round2/report.json` R2-A11 (PC2-12); `FINAL_REPORT_v4.md` §3 item 5 |
| W19 | **~06:30-08:01 26 Sep** | Keep the poller alive. K2 COMPLETE seen by **08:01** (= 00:01 + 28,800 s) proves the insertion gate did not fire. L(K2) <= 9.5 h (by 09:31) proves R5(a). If the poller died, R5(b) (step-0 forecast 7.8 h) still admits K2 (I11) | poller running (20:42:40Z) | `ledger.md`; `CONTEXT.md` 13:38 R5; `round2/report.json` new_facts (4) (others' latency 2-8 h) |
| W20 | when K2 scores (~06:30-10:00) | Read K2 by R3 against #35 = 0.954: accept at >= 0.953, drop the rider at <= 0.952. Record its in-block rank as a proxy for the unrounded score vs #35. If K2 errors: K1 (exp58t v1) in the next slot, with the morning OK | pending | `CONTEXT.md` 13:38 R3/R5; `round2/report.json` R2-A10; `FINAL_REPORT_v4.md` §3 item 6 |
| W21 | ~05:00-09:00 26 Sep (user wakes) | **Morning OK list, revised.** (1) f2: F2 = exp58n, and its S3 submit (07:00-09:00) with the twin dummy verdict attached. (2) Optional floatout on x138 as an R3 coordinate rider, riding only in S12 (W33). (3) K1 fallback if K2 errors. **Drop from the list:** L3 and forkblob (both closed), the L1/L2 OK (moot: t* = 0.30 is > 0.25, so no build under any reading), and the time trigger (not fired). Say plainly that F1 = K2 is very likely final and S4-S7 stay empty by design | not started | `round2/report.json` R2-A8; `experiments/exp60_trainlab/results.md` l.77-80; `CONTEXT.md` 20:35 |
| W22 | ~09:00 26 Sep | Rank line. Latest: #157/3,908 at 19:46; 0.954 block = 139-201; the silver line (~195) is INSIDE the 0.954 block, 38 ranks below us, and drifts ~6 ranks per 1.6 h. The 19:46 line is not yet in CONTEXT | partial (round 2 intel only) | `round2/report.json` new_facts (1)-(2), R2-A10 |
| W23 | every ~6 h (next ~01:45) until 29 Sep 07:00 | x138 successor watch (E10): a public notebook >= 0.956, or a spike of >= 10 teams at one score >= 0.956 -> `experiments/ext_<slug>`. Last check 19:46: nothing (no public notebook > 0.953, x138 still v1) | in progress | `round2/report.json` new_facts (5); `TASK_LOCAL_SESSION.md` §9 |
| W25 | 26 Sep | Slots: S2 = K2; S3 = twin only with the f2 OK; **S4 (K3) empty, S5 (K3b) empty** (T9 FAIL); S6 empty (K4 dropped; K1 only in branches C/D). Do not fill the slots with knob variants | resolved by T9; S3 pending the OK | `CONTEXT.md` 20:35 "CONSEQUENCE"; `round2/report.json` plan_issues |
| W31 | **by 26 Sep 12:00** | Closures to CONTEXT (curator mirror): ANTIPAR one-shot FAIL (div_J 0.1290 -> 0.1250, TP 1 / FP 4), DNVETO closed without a run, I-072 closed (x138 safe-division gates already run on float coords; do NOT write "TP-hostile by GT geometry"), I-066/067/077/078 re-checked and still closed, K4/tempfuse DROPPED with the M6 reopen clause (tempfuse=0 byte-identity + honest LOEO-44b6 >= +0.003 by 26 Sep 18:00), R2S-6 info-only, the corrected dummy wording (M5) | not started | `round2/report.json` R2-A7, rejected; `CONTEXT.md` 19:05 (f) (K4 default drop "unless ... before 26 Sep 12:00") |
| W26 | 26 Sep ~09:30 | Day-2 cloud research (`NEXT_RESEARCH.md`, budget ~$10-12). It is effectively superseded by the night rounds, but nobody has recorded that. Decide and log it | not started (no CONTEXT mention) | `research/wf_ideas_v3/NEXT_RESEARCH.md`; `grep -i day2 CONTEXT.md` finds nothing |
| W35 | 26 Sep (with W31) | RESULTS.md has no exp60 lab row (forkmid / DeepCenter / forkblob / insertion verdicts), only probe rows. Add a one-line lab note, or point to `experiments/exp60_trainlab/results.md` | not started | `experiments/RESULTS.md` l.67-69 |

## LATER (26 Sep 20:50 -> 29 Sep 23:59 UTC)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T02 | 27 Sep ~09:00 | LB snapshot + rank line | `FINAL_REPORT_v4.md` §3 item 8 |
| W33 | code by **27 Sep 12:00** (R8), only after the user's OK | floatout on x138. Port `--patch floatout` to `cells_src[CELL['post']]` (not the hard-coded 7). **Make FLOATOUT_CHECK fail-soft**: the bare assert at `tools/build_probe_kernel.py` l.1315-1362 would kill a hidden rerun (R7). Add a FORCE_FAIL test with the restored sha == mode 0. F1 line only, rides only in S12, never the twin. Write "public tie expected" in CONTEXT before the score | `round2/report.json` R2-A9, new_facts (12) |
| T03 | **27 Sep 12:00** | **R8: no new mechanisms after this.** S7 (a leaf-prune rider is no longer possible: P36 is info-only), S8 (x138 successor only on E10), S9 (F2 candidate), S10-S11 reserve (K1 if K2 failed) | `CONTEXT.md` 13:38 R8 + slot table, l.1905-1907 |
| T04 | **28 Sep 12:00** | S12 consolidation of F1-final, only if accepted riders sit in different files (likely only K2 + optional floatout). Gate = union of the dummy gates (+ "FLOATOUT CHECK PASSED", floor == integers on 100% of rows). The consolidated file JOINS the candidates; do NOT rebuild the twin | `CONTEXT.md` 13:38 S12, 18:20 f2; `round2/report.json` R2-A9 |
| T05 | 28 Sep 16:00 | S13: repeat of S12 on error | `CONTEXT.md` 13:38 |
| T06 | 28 Sep 22:00 | Final admission table (W04) | `FINAL_REPORT.md` §d; `TASK_CLOUD_SESSION.md` T13 |
| T07 | 28-29 Sep | Risk: queue latency > 10 h. If so, R5(b) (step-0 forecast) decides | `FINAL_REPORT.md` §g item 6 |
| T08 | 29 Sep 02:00 (hard edge 10:00) | After 02:00 only S17 (an emergency repeat of F1-final) | `CONTEXT.md` 13:38 R8, S17 |
| T09 | 29 Sep ~11:30 / **12:00** | Draft (11:30), then remind the user (12:00) to tick F1/F2 manually | `TASK_CLOUD_SESSION.md` T13; memory `project-lb-probe-approval.md` |
| T10 | **29 Sep 20:00** | The USER ticks the finals. F1 = the fullest accepted x138-family K build (today: K2, or S12 if built and admitted). F2 = exp58n if f2 got the OK and it scored >= 0.953, else exp52 (#34 last resort before exp52). Never tick exp56, two identical-component files, or auto-select | `CONTEXT.md` 13:38 §f, 18:20 f2; `round2/report.json` new_facts (3) |
| T11 | 29 Sep 23:59 | Competition deadline | `CONTEXT.md` §1 |
| W28 | idle only | T12 / C09 head-shift scale check | `TASK_CLOUD_SESSION.md` T12 |
| W29 | after 29 Sep | E14: friend A's honest out-of-embryo A/B; the error anatomy I06 feeds it | `TASK_FRIEND_A.md` "Задача 4" |

**Done / cancelled since 18:30 (for the record):**
- W01 done: ADDENDUM L gates are in `tools/trainlab.py` (314b82e; `CONTEXT.md` 19:05).
- W08 done: exp60 dumps downloaded, 56 clips, missing [], failed_hooks 0 (`CONTEXT.md` 20:05).
- W09 done: T9 read (`CONTEXT.md` 20:35; `experiments/exp60_trainlab/results.md`).
- W11 done then closed: forkblob code in 28c3256; lab FAIL at 20:05.
- W13 cancelled: no K3/K3b is left to gate.
- W24 cancelled: L6 needed a passing K3b bed.
- W27 and T01 cancelled: K4 dropped (`CONTEXT.md` 19:05 (f); `round2/report.json` M6).
- Earlier items done: pre-registration v3, T1-T6, step 0, the K2/K1/FD/FF dummy gates, ADDENDUM L + f2 recorded before the exp60 output, exp58n built, the RESULTS.md probe 25 fix, the P36 reading rule, and the kaggle_lab.py closure (`CONTEXT.md` 13:38-20:35).

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| I01 | "Of x138's forks, 24% (15/62 on the dummies) are one-blob duplicates at t+1, against 2% of GT divisions." | `research/wf_ideas_v4/lens_literature.json` plan_critique 1-2 | K3b is dead, so this no longer blocks a submission. It stays the main fact for any post-29 Sep division work: all fork-removal riders (forkblob, ANTIPAR, forkmid) failed to exploit it in the lab |
| I02 | "1 of 10 lab gains transferred ... a lab-based slot decision is allowed only for arms whose learned inputs are out-of-sample on the lab clips" | `research/wf_ideas_v4/lens_mine-old.json` plan_critique (4) | The insertion lab +0.0157/+0.0090 (`results.md`) is in-sample (L5). Never cite it as value |
| I03 | Hidden reruns do not consume the GPU quota | `lens_redteam-plan.json` RT1 | Still not in CONTEXT (W06) |
| I04 | "DeepCenter score recorder and the TRAINLAB summary cell are not fail-soft ... 7 of 17 44b6 picks are leak-siblings" | `CONTEXT.md` 14:29 (T5) | 44b6 lab deltas are partly in-sample. The exp60 run reported failed_hooks 0 (`CONTEXT.md` 20:05) |
| I05 | "K2 forecast <= 7.86 h ... The insertion gate at 8.0 h is only +0.14 h above that ... Do NOT move it later on its own" | `lens_headroom.json` critique (2) | Now matters only for floatout/S12. K2 must show COMPLETE by 08:01 (W19) |
| I06 | K2 dummy vs train GT: "FN 82 of 2,127 GT edges. 50% are swaps, 23% one-free-end fragments, 6% end-anchored node misses" | `lens_mine-old.json` critique (3) | Not in CONTEXT. It is the error anatomy for the post-deadline 0.97 path |
| I07 | "lowrefine is not a coordinate-only rider ... +33 final nodes, +29 edges and +1 fork" | `lens_redteam-plan.json` RT2 | The K2 vs #35 read mixes lowrefine and safetail. Only the twin (F2) partly isolates it |
| I08 | Kernel time is not a hidden-test budget signal; use the per-dataset `[ds] repair` lines | `research/wf_ideas_v3/FINAL_REPORT.md` §j item 19 | Twin gate (f) "kernel time <= K2 dummy" (`round2/report.json` R2-A3): compare the repair lines, not the total, because shard launch jitters 258-700 s |
| I09 | "Блок 0.953 на private останется единым" is untested | `FINAL_REPORT.md` §g item 13 | Round 2 found 10 late risers at the END of the 0.953 block (ranks 438-469), consistent with byte-copies tied by submission time. That supports "never tick exp56" (`round2/report.json` new_facts (3)) |
| I11 | "R5(b) ... admits K2 even if the overnight poller fails" | `lens_redteam-plan.json` RT2 (4) | Use it if the poller dies (W19) |
| I12 | "The bronze line (~390) will probably sit ABOVE X (raw x138) by 29 Sep" | `research/wf_ideas_v4/final.notes.md` 18:10 | Updated by I18 |
| I14 | Stale operational text: `TASK_LOCAL_SESSION.md` names branch `claude/practical-meitner-31k9ye`, while the work lands on `main` | `TASK_LOCAL_SESSION.md` "Кто ты"; `TASK_FRIEND_A.md` l.52 | Same risk as W03 |
| I15 | "Lab control division TP/FP/FN = 16/25/83, div_J 0.129. A fork veto therefore breaks even only at FP:TP >= 1/J = 7.7 ... not the public ~3:1. Only ~5% of vetoed forks are evaluable." And: "the public read over-rewards fork REMOVALS whose precision lies between the private break-even (0.11-0.20) and 0.265" | `round2/report.json` new_facts (7), plan_issues "Structural (R2-RC-B)" | Only in the untracked round2 JSON (W30). It is the quantitative reason the whole fork-removal family failed, and the reason any future removal rule needs a 0-TP (or FP >= 3*TP) clause |
| I16 | "Dummy twins (test == train zarr) have GT divisions 0/0/0/3 ... Every exp56/K2/exp57b dummy fork (62/75/74) is metric-ignored, so dummies are plumbing evidence only" | `round2/report.json` new_facts (11), M5 | Not in CONTEXT. Nobody should read a twin/K2 dummy score as value or safety evidence |
| I17 | "FLOATOUT_CHECK (build_probe_kernel.py l.1315-1362) is a bare-assert cell, not fail-soft" | `round2/report.json` new_facts (12) | exp52 (the F2 fallback) was built with floatout and scored fine, but any NEW floatout build without the W33 fix violates R7 |
| I18 | "The silver line (~rank 195 = 5%) now falls INSIDE the 0.954 block; we are 38 ranks above it. It drifts ~6 ranks per 1.6 h" | `round2/report.json` new_facts (2) | At that drift, ~38 ranks is lost in ~10 h if late-scored teams keep entering above us. K2's unrounded score within the block matters (W20, W22) |
| I19 | **DeepCenter t* = 0.30 is the lab optimum** (a HIGHER threshold, the removal direction). 6bba div TP/FP/FN 15/11/73 vs control 15/17/73 (score +0.0010) and 44b6 1/6/10 vs 1/8/10 (score -0.0006): 8 evaluable FP removed, 0 TP lost. But it is not node-preserving (nodes -79 on 6bba, -49 on 44b6; forks -131/-98), and "t* > 0.25: no build" was pre-registered | `experiments/exp60_trainlab/results.md` l.13-18, l.61-66; `CONTEXT.md` l.1858 | Recorded nowhere in CONTEXT (20:35 says only "t* = 0.30 ... NO K3b"). It is a post-hoc idea, too late (R8) and not node-preserving: do NOT act before 29 Sep. Keep it for after 29 Sep, together with I01 |
| I20 | Round 2 claims were overtaken within minutes. "The T9 main score is still running ... nobody has read DeepCenter numbers yet" (20:36) vs the T9 read committed at 20:35. Round 2 R2-A6 (confirm forkmid) and R2-A8 item (2) (ask for L1+L2) are moot | `round2/report.notes.md` 20:36; `git log` da154cb | Round 3 and later must re-read CONTEXT before acting on round 2 actions (see W10, W21) |

Resolved since 18:30: **I10** (the P36 L35 contradiction) is resolved by the rule "P36 is INFO ONLY" (`CONTEXT.md`
l.1905-1907). **I13** (`tools/kaggle_lab.py` orphan) is closed explicitly (`CONTEXT.md` 19:05 (e)).
