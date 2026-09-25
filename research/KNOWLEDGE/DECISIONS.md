# DECISIONS - LB probes, finals candidates, pre-registered rules (curator: facts; curation 2)

State as of **2026-09-25 20:45 UTC** (curation 2; git HEAD da154cb; last LB poll `experiments/lb_poll/poll.log`
20:42:40Z; ledger `experiments/lb_poll/ledger.md` 20:42:42Z). Baseline = curation v4 (18:25 UTC); lines marked **[c2]**
changed in curation 2. Probe IDs
P01..P36 = the team's probe numbers; keep them stable. Main sources: `experiments/RESULTS.md` (probe rows l.33-69),
`CONTEXT.md` §11 (l.232-318), §11a (l.320-349), §14 (dated entries), PRE-REGISTRATION v3 (CONTEXT 25 Sep 13:38, l.1576-1736
= `research/wf_ideas_v3/FINAL_REPORT.md` §e/§f), ADDENDUM L + AMENDMENT f2 (CONTEXT 25 Sep 18:20, l.1850-1895).
Dates are UTC unless marked MSK (= UTC+3). Latency = submit -> scored, when known.

## 1. All LB probes (chronological)

Rule shorthand: **1-chg** = §11a "one change per probe, < 0.002 = noise" (06 Sep); **NF3** = noise floor +-0.003 (§11a,
08 Sep; later superseded, FACTS C-06); **band** = per-probe rule written in probe.json / CONTEXT before scoring (e.g. >= 0.950
adopt, 0.945-0.949 tie, <= 0.944 drop); **R1..R10** = PRE-REGISTRATION v3.

| # | Date (submit) | Kernel | Change | Public | Latency | Decision (rule) | Source |
|---|---|---|---|---|---|---|---|
| P01 | 06 Sep 06:30 MSK (id 56044199) | exp10 v2 (config v2.1) | clean pipeline: exp03B + ILP div 0.6 + gap5 + direct8 | 0.899 | - | clean pipeline abandoned; base = public 0.941 pipeline (user-approved revised plan §11) | RESULTS l.33; CONTEXT §11 l.233-251 |
| P02 | 06 Sep 07:06 MSK (56049333) | exp06 | public 0.941 pipeline + PRIMARY := exp03B | **0.945** | ~6 h | ADOPTED as base (1-chg; +0.004) | RESULTS l.34; CONTEXT l.255 |
| P03 | 06 Sep (56049863) | exp18 | public pipeline, ILP division weight 0.9 | 0.941 | ~6 h | dropped, neutral (1-chg); later "test invalid, no reopen" (FACTS C-15) | RESULTS l.35 |
| P04 | 06 Sep 17:10 MSK (56056939) | exp19 | public pipeline, det threshold 0.95 | 0.940 | ~5.5 h | dropped, det stays 0.965 (1-chg) | RESULTS l.36; CONTEXT l.257 |
| P05 | 06 Sep 17:57 MSK (56057989) | exp20 | exp06 + SECONDARY_DETECTION_WEIGHT 0.5 | 0.943 | ~6 h | dropped (1-chg, -0.002) | RESULTS l.37; CONTEXT l.259 |
| P06 | 07 Sep 03:08 MSK (56065251) | exp21 | exp06 + OUTPUT_MIN_TRACK_LEN 4 | 0.943 | ~7 h | dropped; try 8 (1-chg) | RESULTS l.38 |
| P07 | 07 Sep 03:08 MSK (56065255) | exp22 | exp06 + SECONDARY := exp08 | 0.929 | ~6 h | dropped, strongly negative | RESULTS l.39; CONTEXT l.275-278 |
| P08 | 07 Sep 10:12 MSK (56071497) | exp24 | exp06 + GAP_CLOSE_UM 6.5 | 0.944 | ~6 h | dropped, noise | RESULTS l.40 |
| P09 | 07 Sep 11:07 MSK (56072510) | exp25 | exp06 + OUTPUT_MIN_TRACK_LEN 8 | 0.944 | ~6.5 h | dropped; post-proc knob probes CLOSED | RESULTS l.41; CONTEXT l.265-266 |
| P10 | 07 Sep 23:58 MSK (56084358) | exp27 | exp06 + SECONDARY := friend_a_full199_ep21 | 0.920 | ~5.5 h | dropped; rule: a secondary must first beat pilkwang raw on 6bba->44b6 | RESULTS l.42; CONTEXT l.267-274 |
| P11 | 10 Sep 16:28 MSK (56145113) | exp30 | sjlee 0.947 TTA stack + PRIMARY := exp03B (sweep off) | 0.944 | ~30 min kernel; scored 11 Sep ~02:00 MSK | no gain; confounded -> deconfound P15 | RESULTS l.44; CONTEXT l.279-282 |
| P12 | 10 Sep 17:08 MSK (56145851) | exp31 | exp30 + Z-flip views in edge-feature TTA | 0.941 | same night | tie by NF3 (re-tested as P16) | RESULTS l.45; CONTEXT l.283-286 |
| P13 | 10 Sep 17:34 MSK (56146281) | exp32 | exp30 + SECONDARY := exp23 | 0.937 | same night | dropped (3rd negative secondary swap) | RESULTS l.46 |
| P14 | 10 Sep 17:49 MSK (56146538) | exp29 | sjlee101/biohub-lf-dctta-v020 verbatim (sweep picked tight55) | **0.947** | ~2 h kernel; same night | NEW BASE; final candidate 1 (until 24-25 Sep) | RESULTS l.43; CONTEXT l.289-290 |
| P15 | 11 Sep 09:35 MSK (56160334) | exp33 | exp29 config + PRIMARY := exp03B | 0.944 | overnight (scored 12 Sep) | fine-tuned primary closed (band: >= 0.949 compose) | RESULTS l.47; CONTEXT l.296-298 |
| P16 | 11 Sep 09:40 MSK | exp34 | exp29 config + Z-flip TTA (12 views) | 0.938 | overnight | Z-flip closed for good (band) | RESULTS l.48; CONTEXT l.291-295 |
| P17 | 11 Sep 09:55 MSK | exp35 | exp29 config + PRIMARY := soup03B_50 | 0.943 | overnight | closed | RESULTS l.49; CONTEXT l.299-300 |
| P18 | 15 Sep evening (56252420; dup 56252506 = 0.946) | exp36 | exp29 + already-divided fork filter + sister floor 5 um | 0.946 | ~35 min kernel; scored 16 Sep | NOT adopted (band: >= 0.947 adopt, <= 0.944 drop -> tie); +0.001-class local gains do not earn probes | RESULTS l.51, l.103; CONTEXT l.965-972 |
| P19 | 15 Sep (56256938) | exp37 | exp29 + 8 axis-flip TTA group | 0.946 | scored 16 Sep | tie; local +0.021 did not transfer; axis-flip closed (band >= 0.950 adopt) | RESULTS l.52; CONTEXT l.972-978 |
| P20 | 21 Sep 20:50 (56440312) | exp39 | exp29 + DivNet parent veto p >= 0.5 | 0.947 | ~100 min kernel; scored 22 Sep | tie; became FINAL 2 recommendation (band: >= 0.948 final 2; tie -> prefer exp39 over exp37) | RESULTS l.53; CONTEXT l.1130-1140 |
| P21 | 22 Sep (headed 24 Sep, see FACTS C-18) (56459135) | exp40 | exp29 + motion relink OFF | 0.945 | - | relink stays; Friend B local +0.0053 did not transfer | RESULTS l.54; CONTEXT l.1208-1210 |
| P22 | 22 Sep (56459139) | exp41 | exp29 + MOTION_RELINK_LEARNED_BONUS 2.5 | 0.945 | - | dropped | RESULTS l.55 |
| P23 | 22 Sep | exp42 | exp29 + takaito gshift in relink | 0.945 | - | dropped; "relink stage at local optimum" | RESULTS l.56; CONTEXT l.1213-1217 |
| P24 | 22 Sep ~20:45 | exp43 | takaito/biohub-a951-gshift verbatim | 0.944 | scored 23 Sep 18:40 | not a base (author 0.948) | RESULTS l.57; CONTEXT l.1226-1230 |
| P25 | 22 Sep ~20:45 | exp44 v2 | exp43 + axis-flip TTA + division hygiene (bundle) | 0.946 | scored 23 Sep 18:40 | "no more probes of public-notebook variants"; finals unchanged exp29 + exp39 | CONTEXT l.1230-1233; `experiments/RESULTS.md` l.58 (fixed to 0.946, FACTS C-17) |
| P26 | 23 Sep (scored 24 Sep 02:00) | exp45 | DIAGNOSTIC: exp29 with safe divisions OFF | 0.911 | ~40 min kernel | J_pub ~0.36, P_min 0.31, break-even 0.265 (never a final) | RESULTS l.59; CONTEXT l.1319-1321 |
| P27 | 24 Sep ~03:10-04:00 (56510844) | exp47 | exp39 + weak-leaf prune 0.3 | 0.947 | scored by 10:50 | tie; below +0.002 gate | RESULTS l.60; CONTEXT l.1343 |
| P28 | 24 Sep ~03:45 (56510845) | exp48 | exp47 + DaughterNet v1 insertion with steal | **0.948** | ~7.6 h (03:45 -> 11:20) | replaces exp29 as finals candidate | RESULTS l.61; CONTEXT l.1365-1367; `research/wf_ideas_v3/h_ensembles-and-private.notes.md` l.4 |
| P29 | 24 Sep (56518035) | exp49 | exp39 + edge filter ef_a3_rl_pr (lab +0.0162) | 0.947 | scored 16:55 | EDGE-FILTER LINE CLOSED (decision tree 10:50: both <= 0.947 -> close) | RESULTS l.62; CONTEXT l.1348-1350, l.1441-1445 |
| P30 | 24 Sep (56518039) | exp50 | exp39 + drop-only edge filter ef_a0 | 0.946 | scored 16:40 | does not transfer; closed | RESULTS l.63; CONTEXT l.1435-1440 |
| P31 | 24 Sep 17:09 (56527239) | exp51 | exp48 + x138 V1284 head (--patch coordhead) | **0.950** | ~7.5 h (-> 25 Sep 00:39) | NEW BEST then; F1 candidate (exp48 fallback); exp54 not needed (== exp48 bytes) | RESULTS l.64; CONTEXT l.1495-1497, l.1483-1485 |
| P32 | 25 Sep 00:02:05 (56534391) | exp52 | exp51 + float output coords (safe) | 0.950 | <= 7.8 h | tie; float harmless but invisible; later §f default F2 | RESULTS l.65; CONTEXT l.1498-1499 |
| P33 | 25 Sep 00:02:10 (56534401) | exp53 | exp48 + float output coords (safe) | 0.948 | <= 7.8 h | tie | RESULTS l.66 |
| P34 | 25 Sep 08:09:00 (56545267) | exp56 | anvithpothula/biohub-x138 VERBATIM | 0.953 | (6.29, 6.46] h | **R1**: x138 = base, #34 non-degraded (branch A/B side) | RESULTS l.67; CONTEXT l.1797-1800 |
| P35 | 25 Sep 08:33:25 (56545786) | exp57b | x138 + DaughterNet v1 insertion (#35 config), no leaf prune | **0.954** (best) | (6.72, 7.73] h | **BRANCH A**; **R2**: insertion in F1 stack; **R6** not triggered; **R5**: #35 itself NOT a finals candidate (L35 <= 7.5 h unproven) | RESULTS l.68; CONTEXT l.1801-1810 |
| P36 | 25 Sep 16:18:09 (56555189) | exp57 v1 | DIAGNOSTIC (slot S1): x138 + leaf prune 0.3 + ungated insertion | PENDING (**[c2]** poll 20:42:40Z) | > 4.40 h (pending) | **[c2] INFO ONLY** (reading rule recorded before the score, CONTEXT item (b) l.1904-1906): L35 > 7.5 h is unprovable, so P36 cannot trigger a leaf-prune rider even if delta >= +0.002; leaf prune on x138 stays closed. Superseded R4 text: delta = #36 - #35 (>= +0.002 rider; abs <= 0.001 closed; <= -0.002 readmit must stay). Never a final (FACTS C-20) | RESULTS l.69; CONTEXT l.1807-1810, l.1904-1906; `experiments/lb_poll/ledger.md` |

Scheduled (not yet submitted): **S2 = K2 = exp58** (x138 + safetail + lowrefine + #35 insertion) at 00:01 UTC 26 Sep,
pre-approved, dummy gates 18/18 green (CONTEXT 25 Sep 17:20-17:55 l.1817-1836). **[c2]** Submit the dummy-gated
version `-v 1` (no re-push) after 00:00:30 UTC. Its `-m` must start "probe 37: exp58 = K2 ..." so that the runtime
ledger files it under the safetail family (9.5 h); then run `tools/runtime_ledger.py --k2 <ref> --family
<ref>=safetail` (`research/wf_ideas_v4/round2/report.json` R2-A4). Expected score ~06:30-08:00 UTC (FACTS F-RUN-10).
S3 = exp58n twin only after the user's OK on AMENDMENT f2 (FINAL_REPORT_v4 §3 item 2). **[c2]** The twin dummy was
pushed ~20:35 UTC; its gate read is pending (CONTEXT l.1935-1937). **[c2]** S4 (K3) and S5 (K3b) are EMPTY after the
exp60 lab read (§1b). S6 (K4/tempfuse) is DROPPED by default (CONTEXT item (f) l.1913-1914; round2 M6). Total
submissions so far 37 (36 probes + 1 duplicate; FINAL_REPORT_v4 §2); 25 Sep is full (5 submissions).

## 1b. Lab-gate decisions that consumed or freed an LB slot [c2]

These are not LB probes. They are pre-registered lab reads on the exp60 bed (56 clips) that decided whether a rider
gets a slot.

| ID | Time (UTC) | Candidate | Gate / rule | Result | Decision | Source |
|---|---|---|---|---|---|---|
| G01 | 25 Sep 20:05 | forkblob (ADDENDUM L4, R3-class rider) | L4 lab harm gate: pooled div_J(arm) >= control, TP <= 1 with FP >= 3*TP, dose >= 10%, adj_edge >= -0.0002 | vetoed 150 (TP 1, FP 6, ign 143), dose 22%, div_J 0.1290 -> 0.1271 **FAIL** | CLOSED, not in K3; no user OK needed | CONTEXT l.1918-1923; `experiments/exp60_trainlab/results_forkblob.md` |
| G02 | 25 Sep 20:35 | forkmid (K3, S4) | ORIGINAL T9 (0 TP, >= 3 FP with >= 1 on 44b6) and ADDENDUM L3 | removed 40/676, TP 0, evaluable FP 1; score +0.00013 **FAIL / FAIL** | NO K3; S4 empty; no public ladder | CONTEXT l.1926-1929; `experiments/exp60_trainlab/results.md` l.78, l.84-89 |
| G03 | 25 Sep 20:35 | DeepCenter safe-division threshold (K3b, S5) | T9 strict / strict + L2 / L1 + L2 | t* = 0.30: conf, plateau, 44b6 and precision all False **FAIL** under all three readings | NO K3b; S5 empty; L6 extension moot | CONTEXT l.1930-1931; `experiments/exp60_trainlab/results.md` l.79 |
| G04 | 25 Sep 20:35 | insertion (#35 config) | L5: in-sample upper bound, warning only | 44b6 +0.0157, 6bba +0.0090 (nosteal0 0.0000 / +0.0071) | consistent with R2 (insertion stays in K2); nosteal0 closed by L5 | CONTEXT l.1932-1933 |
| G05 | 25 Sep 20:24-20:30 | ANTIPAR fork veto (round-2 idea R2S-2) | one-shot lab, rule frozen in `research/wf_ideas_v4/round2/scan_hypotheses.json` | vetoed 113/676 (TP 1, FP 4), div_J 0.1290 -> 0.1250, score -0.00034 **FAIL** | CLOSED per round 2 (proposed ADDENDUM M4). Not yet recorded in CONTEXT (FACTS C-21) | `research/wf_ideas_v4/round2/report.json` new_facts (8), R2-A7 |
| G06 | 25 Sep ~20:40 | DNVETO (DaughterNet parent veto p < 0.057), K4/tempfuse | round 2 skeptic condition "drop if ANTIPAR fails"; K4 default DROPPED (CONTEXT (f)) | not run | DNVETO CLOSED; K4 DROPPED (M6 reopen clause only if LOEO-44b6 >= +0.003 by 26 Sep 18:00) | `research/wf_ideas_v4/round2/report.json` rejected, plan_issues M6; CONTEXT l.1913-1914 |

Consequence (CONTEXT l.1935-1937): **the F1 stack = K2** unless a later mechanism passes. The remaining levers are the
F2 twin (needs the f2 OK) and an optional floatout rider (needs an OK; expected private gain ~+0.0001, FACTS
F-TRN-13).

## 2. CURRENT finals candidates

F1/F2 are ticked manually by the user by 29 Sep 20:00 UTC (reminder 12:00). Rule text: CONTEXT l.1707-1736 (§f) and
AMENDMENT f2 l.1887-1895 (f2 needs the user's OK; until then §f applies: F2 = exp52).

| File (probe) | Public | Latency | Admissible by R5? | Riders inside | F1/F2 role | Source |
|---|---|---|---|---|---|---|
| K2 = exp58_x138_safe_lowref (not yet submitted) | - | forecast <= ~7.8 h | pending: yes once scored without error and L <= 9.5 h (C01 build) | C01 safetail, C05 lowrefine, C03 insertion (#35 config) | **F1 candidate**. **[c2]** Very likely the final F1 stack: K3/K3b failed their lab gates and K4 was dropped (§1b); only an OK'd floatout could still ride in the S12 consolidation | CONTEXT l.1797-1829; `experiments/exp58_x138_safe_lowref/probe.json`; `experiments/runtime_step0/step0.md` |
| exp58n_x138_safe_lowref (twin, built, not submitted) | - | est. ~6.5-6.6 h | pending (C01 build) | C01, C05; no insertion | **F2 candidate under AMENDMENT f2** (if public >= 0.953, R5-admissible, dummy gate `--insertion 0`). **[c2]** Dummy pushed ~20:35 UTC, gate read pending; S3 submit still needs the user's OK | CONTEXT l.1887-1895, l.1935-1937; `experiments/exp58n_x138_safe_lowref/probe.json`; `research/wf_ideas_v4/v_private-finals_noins-twin-f2_feasibility.notes.md`; `research/wf_ideas_v4/round2/report.json` R2-A3 |
| exp58t (K1, dummy only) | - | - | would be (C01) | C01, insertion; lowrefine off | fallback item 2 (§f); v4 item 6: goes in the next slot if K2 errors [needs OK] | CONTEXT l.1774, l.1818; FINAL_REPORT_v4 §3 item 6 |
| exp57b (P35) | 0.954 | (6.72, 7.73] h | **NO** (ungated insertion; L35 <= 7.5 h not provable) | insertion (ungated), DIVINS_DUMP=1 | fallback item 3 only if L35 <= 7.5 h were proven -> excluded | CONTEXT l.1805-1807; §f l.1713-1716 |
| exp56 (P34) | 0.953 | (6.29, 6.46] h | yes (L34 <= 7.5 h) | none (byte copy of x138) | fallback item 4 only; "never tick exp56" while any admissible non-copy x138-family file exists | §f l.1716, l.1735; f2 l.1893-1894 |
| exp52 (P32) | 0.950 | <= 7.8 h | yes always (no timer) | V1284 head, leaf prune, insertion, DivNet veto, float out (DIVINS_DUMP=1; **[c2]** admissible: R7 applies to new builds only, CONTEXT (d) l.1910-1911) | **F2 by §f default** until f2 is OK'd; fallback 5; F1 in branch D | §f l.1719-1733; `experiments/exp52_coordhead_floatout/probe.json` |
| exp51 (P31) | 0.950 | ~7.5 h | yes always | as exp52 without float | branch-D alternative to exp52 | §e R5 l.1656; §f l.1732 |
| exp48 (P28) / exp53 (P33) | 0.948 | ~7.6 h / <= 7.8 h | no timer (not named in R5) | leaf prune + insertion (+ float) | superseded | CONTEXT l.1497 |
| exp57 v1 (P36) | pending | > 4.40 h | never a final | leaf prune + ungated insertion | diagnostic only; **[c2]** info-only read | CONTEXT l.1807-1808, l.1904-1906 |
| K3 / K3b / K4 (exp59 etc.) **[c2]** | - | - | not built | forkmid / DeepCenter threshold / tempfuse | **none**: lab FAIL (G02, G03), K4 dropped (G06) | §1b |

Never tick two files with identical components; objective = P(private > raw x138) first, silver second (f2, l.1894-1895).

## 3. Status of pre-registered rules R1-R10 (PRE-REGISTRATION v3, user OK 25 Sep ~13:37 UTC)

| Rule | Content (short) | Applied when | Outcome / status | Source |
|---|---|---|---|---|
| R1 base | a = 0.953 and L34 <= 7.5 h -> x138 is the base, #34 non-degraded | 25 Sep 14:37 | a = 0.953, L34 in (6.29, 6.46] -> base = x138; branch D excluded | CONTEXT l.1797-1800 |
| R2 insertion | insertion in F1 if b >= a (tie counts for) | 25 Sep 16:20 | b = 0.954 >= 0.953 -> BRANCH A, K2 WITH insertion; S3 held | CONTEXT l.1801-1805 |
| R3 harmless riders (C01, C05, C04) | accept if dummy gates pass and public >= previous stack - 0.001; <= -0.002 remove | not yet (first read on K2 score, ~26 Sep 06:30-09:00) | pending for C01+C05 inside K2. **[c2]** C04 forkmid: no build (G02). forkblob: CLOSED by its lab gate (G01), so no OK is needed | l.1647-1649; ADDENDUM L4 l.1865 |
| R4 node/fork changers | delta vs current F1 candidate: >= +0.002 -> F1; 0/+0.001 -> F2 candidate; <= -0.001 closed; never on lab gain alone | P36 (exp57 v1) vs #35; later K3b/K4 | **[c2]** P36 made INFO ONLY before it scored (CONTEXT (b) l.1904-1906), which settles the L35 ambiguity. K3b not built (G03), K4 dropped (G06), so R4 has no pending subject except an OK'd floatout (R2-A9 treats it as an R3 coordinate rider) | l.1650-1652, l.1808-1810 |
| R5 admission by time | scored without error AND (latency <= own REPAIR_DEADLINE_S: 7.5 h x138-type, 9.5 h C01 builds, OR step-0 margin >= 1 h); ungated-insertion files with L > 7.5 h excluded; exp51/52 always admissible | 25 Sep 16:20 (#34 yes, #35 no) | K2/twin pending on their own latency (poll every 10 min). **[c2]** `tools/runtime_ledger.py` automates R5(a) by family in `experiments/lb_poll/ledger.md`; K2 must be tagged with the safetail family (FACTS F-RUN-11) | l.1653-1657, l.1806-1807; step0.md |
| R6 N1 trigger | build parrepair if L34 > 8.0 h, #35 error/timeout, L35 > 8.5 h with insertion, or F1 forecast > 9.0 h | 25 Sep 16:20 and 16:45 (step 0) | NOT triggered (L34 <= 6.46, L35 <= 7.73, K2 forecast <= ~7.8 h); no N1 | l.1658-1664, l.1804-1805, l.1811-1814 |
| R7 hygiene | validator/PP sweep off; no DIVINS_DUMP=1 in submissions; every stage fail-soft; first check node-count identity; no choice between near-copies by 0.001 except via R3 | continuously since 25 Sep 13:38 | respected in K2/K1/twin builds (DIVINS_DUMP 0, fail-soft verified by FF dummy). **[c2]** C-16 resolved: R7 applies to new builds (CONTEXT (d) l.1910-1911). Open: the floatout FLOATOUT_CHECK is a bare assert and needs a fail-soft wrapper before any use (round2 R2-A9) | l.1665-1670; probe.json exp58*/exp52 |
| R8 deadlines | new mechanisms by 27 Sep 12:00; F1-final consolidation by 28 Sep 12:00; after 29 Sep 02:00 only emergency repeat (hard edge 10:00) | 25 Sep 18:20: E13/C08 closed on schedule; **[c2]** 20:05-20:35: forkblob, forkmid and DeepCenter decided on the lab before the 27 Sep cutoff | future cutoffs: new mechanisms 27 Sep 12:00, F1-final 28 Sep 12:00, emergency only after 29 Sep 02:00 | l.1671-1672; ADDENDUM L7 l.1883 |
| R9 do-not | no N2 size probe, no test-crop overlap consensus, no detector/edge/head retraining before 29 Sep, no knob ladders, no axis-flip on x138 | since 25 Sep 13:38 | in force; used to close the y3uanm secondary fine-tune and M3. **[c2]** Round 2 used it to reject knob ladders to fill the empty S4-S7 slots | l.1673-1676; FINAL_REPORT_v4 §2 |
| R10 agent-hour priority | E1 > pre-reg > E2 > E4 build > E3 > step 0 > (N1 if R6) > E4/E5 analysis > E7 > E12; E1+E2 in git before moonshot code | 25 Sep 14:05-14:29 | satisfied: T1 safetail (14:05) and T2 lowrefine (14:29) merged first | l.1677-1678; CONTEXT §9 T1 l.1898, 14:29 l.1747-1752 |
| Finals rule §f | F1 = fullest admissible x138-family K build with C01, not a byte copy, riders passed R3/R4; F2 = exp52 (or twin per f2) | 29 Sep by 20:00 UTC (manual tick) | pending. **[c2]** Expected pair: F1 = K2 (if it scores without error and is admissible); F2 = exp58n twin with the f2 OK, else exp52 | l.1707-1736 |

Amendments recorded 25 Sep 18:20 UTC before any exp60 output (CONTEXT l.1850-1895): ADDENDUM L (L1 DeepCenter plateau
[OK], L2 precision over evaluable forks + Wilson bound (bug fix, in force), L3 forkmid power fix [OK], L4 forkblob frozen
[R3 class needs OK], L5 insertion arms = in-sample upper bound, nosteal0 closed, L6 conditional 6bba extension, L7
closures: RE-AIM, pair-GBM, E13/C08) and AMENDMENT f2 [needs OK]. User asleep; OKs expected 26 Sep morning (before ~09:00
UTC) - `research/wf_ideas_v4/FINAL_REPORT_v4.md` §5.

**[c2] Since 18:25 UTC.** The ADDENDUM L code was merged (CONTEXT "19:05" entry, written ~18:40, l.1896-1903). In force
until the user's OK: forkmid = ORIGINAL T9; K3b = strict plateau AND L2; insertion = L5 warning. The P36 info-only rule
and the R7 clarification are recorded (l.1904-1916). The exp60 reads decided nothing into K2 (§1b). Round 2
(`research/wf_ideas_v4/round2/report.json`, ~20:42 UTC) proposed **ADDENDUM M** (M1 corrected K3b gate, M2 L2 needs
[OK], M3 forkmid, M4 ANTIPAR/DNVETO closed with the lab break-even FP:TP >= 7.7, M5 dummies = plumbing only, M6 K4
dropped). As of HEAD da154cb it is **not in CONTEXT** (FACTS C-21). Morning OK list per round 2 (R2-A8):
(1) f2 + S3 twin submit; (2) L1 + L2 (moot for exp60); (3) do NOT ask for L3/forkblob; (4) optional floatout;
(5) K1 in the next slot if K2 errors.
