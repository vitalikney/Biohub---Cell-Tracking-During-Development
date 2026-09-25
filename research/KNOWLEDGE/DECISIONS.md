# DECISIONS - LB probes, finals candidates, pre-registered rules (curator: facts; curation 3)

State as of **2026-09-25 23:00 UTC** (curation 3; git HEAD 1ca747b + untracked `research/wf_ideas_v4/round3/`; last LB
poll `experiments/lb_poll/poll.log` 22:53:04Z; ledger `experiments/lb_poll/ledger.md` 22:53:06Z). Baseline = curation v4
(18:25 UTC); lines marked **[c2]** changed in curation 2 (20:45 UTC), **[c3]** in curation 3. Probe IDs
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
| P36 | 25 Sep 16:18:09 (56555189) | exp57 v1 | DIAGNOSTIC (slot S1): x138 + leaf prune 0.3 + ungated insertion | PENDING (**[c3]** poll 22:53:04Z) | > 6.58 h (pending; **[c3]** ledger 22:53:06Z) | **[c2] INFO ONLY** (reading rule recorded before the score, CONTEXT item (b) l.1904-1906): L35 > 7.5 h is unprovable, so P36 cannot trigger a leaf-prune rider even if delta >= +0.002; leaf prune on x138 stays closed. Superseded R4 text: delta = #36 - #35 (>= +0.002 rider; abs <= 0.001 closed; <= -0.002 readmit must stay). Never a final (FACTS C-20) | RESULTS l.69; CONTEXT l.1807-1810, l.1904-1906; `experiments/lb_poll/ledger.md` |
| P37 **[c3]** | scheduled >= 00:01:00 UTC 26 Sep (not in poll.log at 22:53:04Z) | exp58 v1 = K2 | x138 + safetail C01 + lowrefine C05 + DaughterNet insertion (#35 config) | - | forecast 7.87 h (FACTS F-RUN-13) | pre-approved (PRE-REG v3 item (3), night plan 17:55); read by R3/R5/§f (+ proposed READ TABLE, §2b) | CONTEXT 22:06 l.1963-1964; `research/wf_ideas_v4/round3/report.json` R3-A1 |
| P38 **[c3]** | scheduled >= 00:01:00 UTC 26 Sep, right after P37 | exp58n v1 = twin | K2 without the insertion (x138 + C01 + C05) | - | est. ~6.5-6.6 h | approved by the user's f2 OK 22:06 UTC; F2 candidate by f2 (public >= 0.953, R5-admissible, no error) | CONTEXT 22:06 l.1960-1966; git 1ca747b; round3 R3-A1 |

Scheduled (not yet submitted): **S2 = K2 = exp58** (x138 + safetail + lowrefine + #35 insertion) at 00:01 UTC 26 Sep,
pre-approved, dummy gates 18/18 green (CONTEXT 25 Sep 17:20-17:55 l.1817-1836). **[c2]** Submit the dummy-gated
version `-v 1` (no re-push) after 00:00:30 UTC. Its `-m` must start "probe 37: exp58 = K2 ..." so that the runtime
ledger files it under the safetail family (9.5 h); then run `tools/runtime_ledger.py --k2 <ref> --family
<ref>=safetail` (`research/wf_ideas_v4/round2/report.json` R2-A4). Expected score ~06:30-08:00 UTC (FACTS F-RUN-10).
S3 = exp58n twin only after the user's OK on AMENDMENT f2 (FINAL_REPORT_v4 §3 item 2). **[c2]** The twin dummy was
pushed ~20:35 UTC; its gate read is pending (CONTEXT l.1935-1937). **[c2]** S4 (K3) and S5 (K3b) are EMPTY after the
exp60 lab read (§1b). S6 (K4/tempfuse) is DROPPED by default (CONTEXT item (f) l.1913-1914; round2 M6). Total
submissions so far 37 (36 probes + 1 duplicate; FINAL_REPORT_v4 §2); 25 Sep is full (5 submissions).
**[c3] Update.** Twin gates PASS (CONTEXT 20:55 l.1955-1959) and the user OK'd f2 at 22:06 UTC (l.1960-1966), so S3 is
approved: K2 and the twin go together at >= 00:01:00 UTC 26 Sep as P37/P38 (rows above), each `-v 1` (no re-push),
messages starting "probe 37: exp58 = K2 ..." and "probe 38: exp58n = K2 twin ...". Per round 3 the ledger assigns the
families from the message, so the round-2 `--k2/--family` step is superseded (FACTS C-28). After the submits: one
`tools/runtime_ledger.py --print` check, and log in CONTEXT whether P36 was still PENDING (then L(K2) may include queue
time) - `research/wf_ideas_v4/round3/report.json` R3-A1, R3-A6 (e). Round 3 proposes a CONTEXT line "S4-S6 (26 Sep)
carry no rider; unused slots are not burned; exceptions only K1 per the READ TABLE or a deadline-move/D4 build if the
runtime trigger fires, each with an OK" (R3-A3; not in CONTEXT at HEAD 1ca747b).

## 1b. Lab-gate decisions that consumed or freed an LB slot [c2]

These are not LB probes. They are pre-registered lab reads on the exp60 bed (56 clips) that decided whether a rider
gets a slot.

| ID | Time (UTC) | Candidate | Gate / rule | Result | Decision | Source |
|---|---|---|---|---|---|---|
| G01 | 25 Sep 20:05 | forkblob (ADDENDUM L4, R3-class rider) | L4 lab harm gate: pooled div_J(arm) >= control, TP <= 1 with FP >= 3*TP, dose >= 10%, adj_edge >= -0.0002 | vetoed 150 (TP 1, FP 6, ign 143), dose 22%, div_J 0.1290 -> 0.1271 **FAIL** | CLOSED, not in K3; no user OK needed | CONTEXT l.1918-1923; `experiments/exp60_trainlab/results_forkblob.md` |
| G02 | 25 Sep 20:35 | forkmid (K3, S4) | ORIGINAL T9 (0 TP, >= 3 FP with >= 1 on 44b6) and ADDENDUM L3 | removed 40/676, TP 0, evaluable FP 1; score +0.00013 **FAIL / FAIL** | NO K3; S4 empty; no public ladder | CONTEXT l.1926-1929; `experiments/exp60_trainlab/results.md` l.78, l.84-89 |
| G03 | 25 Sep 20:35 | DeepCenter safe-division threshold (K3b, S5) | T9 strict / strict + L2 / L1 + L2 | t* = 0.30: conf, plateau, 44b6 and precision all False **FAIL** under all three readings | NO K3b; S5 empty; L6 extension moot | CONTEXT l.1930-1931; `experiments/exp60_trainlab/results.md` l.79 |
| G04 | 25 Sep 20:35 | insertion (#35 config) | L5: in-sample upper bound, warning only | 44b6 +0.0157, 6bba +0.0090 (nosteal0 0.0000 / +0.0071) | consistent with R2 (insertion stays in K2); nosteal0 closed by L5 | CONTEXT l.1932-1933 |
| G05 | 25 Sep 20:24-20:30 | ANTIPAR fork veto (round-2 idea R2S-2) | one-shot lab, rule frozen in `research/wf_ideas_v4/round2/scan_hypotheses.json` | vetoed 113/676 (TP 1, FP 4), div_J 0.1290 -> 0.1250, score -0.00034 **FAIL** | CLOSED per round 2 (ADDENDUM M4). **[c3]** Recorded in CONTEXT 20:55 as a post-hoc fact: "FAIL, CLOSED (no reruns)" (FACTS C-21 resolved) | `research/wf_ideas_v4/round2/report.json` new_facts (8), R2-A7; CONTEXT 20:55 l.1945-1947 |
| G06 | 25 Sep ~20:40 | DNVETO (DaughterNet parent veto p < 0.057), K4/tempfuse | round 2 skeptic condition "drop if ANTIPAR fails"; K4 default DROPPED (CONTEXT (f)) | not run | DNVETO CLOSED; K4 DROPPED. **[c3]** CONTEXT 20:55 records both; K4 "reopen only with a new honest bed" (the M6 LOEO-44b6 clause is not in CONTEXT) | `research/wf_ideas_v4/round2/report.json` rejected, plan_issues M6; CONTEXT l.1913-1914, 20:55 l.1947-1950 |
| G07 **[c3]** | 25 Sep ~22:45 | swapfix / 2x2 re-assignment on x138 (I-165/I-166, RC-A) | round-3 recheck on exp60 dumps | 0 of 555 both-ends FN are true 2x2 swaps; rule reaches 1 TP (~+0.00002) | stays CLOSED (proposed; not in CONTEXT) | `research/wf_ideas_v4/round3/report.json` rejected, R3-A8 (1); `research/wf_ideas_v4/round3/v_recheck_r3-rc-a-swapfix-on-x138.json` |
| G08 **[c3]** | 25 Sep ~22:45 | clip-boundary short-track rescue b4 (I-145, RC-B) | its own bar: SELECTION >= +0.001, nodes <= +0.4%, boundary FN -25% | SELECTION 0.00000, CONFIRMATION +0.00109, W/L 7/47, nodes +0.48% **FAIL**; R4 would need +0.002 | stays CLOSED; ILP start/end part deferred past the deadline (proposed) | round3 report.json rejected, R3-A8 (2); `research/wf_ideas_v4/round3/v_recheck_r3-rc-b-clip-boundary-short-track-on-x138.json` |
| G09 **[c3]** | 25 Sep ~22:45 | axis-flip TTA on x138 (I-151, RC-C) | R9 (user refusal) + no honest lab | public sign depends on the base (probe 19 -0.001; probe 25 +0.002 bundled) | stays CLOSED (R9) | round3 report.json rejected, R3-A8 (4); `research/wf_ideas_v4/round3/v_recheck_r3-rc-c-axisflip-tta-private-reread.json` |
| G10 **[c3]** | 25 Sep ~22:45 | density-gated insertion / density-scaled DIVINS_CAP (R3S-2) | lab quartiles | cap of 4 binds nearly everywhere; every quartile above break-even except Q2 -0.0005 | CLOSED (proposed) | round3 report.json new_facts (11), rejected; FACTS F-TRN-14 |
| G11 **[c3]** | 25 Sep ~22:45 | deterministic x138 tail-bug fixes (R3S-3), dangling-end relink/gap bridging (R3S-4), retention-guard hysteresis (R3S-5) | lab anatomy | 0 structural defects; 0 mutual-nearest end->start pairs within 7 um; no flicker penalty | all CLOSED (proposed); tail saturated, rest needs retraining (R9) | round3 report.json new_facts (12)-(17), rejected; FACTS F-MOD-15, F-TRN-15, F-TRN-18 |

Consequence (CONTEXT l.1935-1937): **the F1 stack = K2** unless a later mechanism passes. The remaining levers are the
F2 twin (needs the f2 OK) and an optional floatout rider (needs an OK; expected private gain ~+0.0001, FACTS
F-TRN-13). **[c3]** The f2 OK came at 22:06 UTC. Round 3 concludes that the new-mechanism search is over in practice,
before the R8 cutoff (27 Sep 12:00): S4-S11 stay empty except K1 by the READ TABLE and an OK'd S12 floatout
(`research/wf_ideas_v4/round3/report.json` plan_issues "STRATEGIC").

## 2. CURRENT finals candidates

F1/F2 are ticked manually by the user by 29 Sep 20:00 UTC (reminder 12:00). Rule text: CONTEXT l.1707-1736 (§f) and
AMENDMENT f2 l.1887-1895 (f2 needs the user's OK; until then §f applies: F2 = exp52). **[c3]** f2 OK'd by the user at
22:06 UTC 25 Sep (CONTEXT l.1960-1966): F2 = exp58n twin if it scores without error, is R5-admissible and public >= 0.953;
otherwise exp52 per §f.

| File (probe) | Public | Latency | Admissible by R5? | Riders inside | F1/F2 role | Source |
|---|---|---|---|---|---|---|
| K2 = exp58_x138_safe_lowref (P37, **[c3]** submit >= 00:01 UTC 26 Sep) | - | forecast <= ~7.8 h; **[c3]** 7.87 h (FACTS F-RUN-13) | pending: yes once scored without error and L <= 9.5 h (C01 build); **[c3]** R5(b) margin 1.63 h admits it unless it ERRORs | C01 safetail, C05 lowrefine, C03 insertion (#35 config) | **F1 candidate**. **[c2]** Very likely the final F1 stack: K3/K3b failed their lab gates and K4 was dropped (§1b); only an OK'd floatout could still ride in the S12 consolidation. **[c3]** Default world (P ~0.85-0.9 per round 3): F1 = K2 | CONTEXT l.1797-1829; `research/wf_ideas_v4/round3/report.json` R3-A9; `experiments/exp58_x138_safe_lowref/probe.json`; `experiments/runtime_step0/step0.md` |
| exp58n_x138_safe_lowref (twin, P38, **[c3]** submit >= 00:01 UTC 26 Sep) | - | est. ~6.5-6.6 h | pending (C01 build; R5(b) as K2) | C01, C05; no insertion | **F2 candidate under AMENDMENT f2** (if public >= 0.953, R5-admissible, dummy gate `--insertion 0`). **[c2]** Dummy pushed ~20:35 UTC, gate read pending; S3 submit still needs the user's OK. **[c3]** Gates PASS (20:55); f2 OK'd 22:06 -> **F2 candidate** (submit approved) | CONTEXT l.1887-1895, l.1935-1937, l.1955-1966; `experiments/exp58n_x138_safe_lowref/probe.json`; `research/wf_ideas_v4/v_private-finals_noins-twin-f2_feasibility.notes.md`; `research/wf_ideas_v4/round2/report.json` R2-A3 |
| exp58t (K1, dummy only) | - | - | would be (C01) | C01, insertion; lowrefine off | fallback item 2 (§f); v4 item 6: goes in the next slot if K2 errors [needs OK]. **[c3]** Round-3 READ TABLE triggers: K2 ERROR (row 1) or lowrefine removed from the F1 stack (row 4; row 5 with d2 <= -0.002); never at d1 = -0.001; message must start 'probe NN: exp58t' [needs OK] | CONTEXT l.1774, l.1818; FINAL_REPORT_v4 §3 item 6; `research/wf_ideas_v4/round3/report.json` R3-A9 (1) |
| exp57b (P35) | 0.954 | (6.72, 7.73] h | **NO** (ungated insertion; L35 <= 7.5 h not provable) | insertion (ungated), DIVINS_DUMP=1 | fallback item 3 only if L35 <= 7.5 h were proven -> excluded | CONTEXT l.1805-1807; §f l.1713-1716 |
| exp56 (P34) | 0.953 | (6.29, 6.46] h | yes (L34 <= 7.5 h) | none (byte copy of x138) | fallback item 4 only; "never tick exp56" while any admissible non-copy x138-family file exists | §f l.1716, l.1735; f2 l.1893-1894 |
| exp52 (P32) | 0.950 | <= 7.8 h | yes always (no timer) | V1284 head, leaf prune, insertion, DivNet veto, float out (DIVINS_DUMP=1; **[c2]** admissible: R7 applies to new builds only, CONTEXT (d) l.1910-1911) | **F2 by §f default** until f2 is OK'd; fallback 5; F1 in branch D. **[c3]** After the f2 OK: F2 only if the twin errors, is not R5-admissible or scores < 0.953 (0.952 floor needs an OK, R3-A9 (2)) | §f l.1719-1733; `experiments/exp52_coordhead_floatout/probe.json` |
| exp51 (P31) | 0.950 | ~7.5 h | yes always | as exp52 without float | branch-D alternative to exp52 | §e R5 l.1656; §f l.1732 |
| exp48 (P28) / exp53 (P33) | 0.948 | ~7.6 h / <= 7.8 h | no timer (not named in R5) | leaf prune + insertion (+ float) | superseded | CONTEXT l.1497 |
| exp57 v1 (P36) | pending | > 6.58 h (**[c3]** 22:53Z) | never a final | leaf prune + ungated insertion | diagnostic only; **[c2]** info-only read | CONTEXT l.1807-1808, l.1904-1906 |
| K3 / K3b / K4 (exp59 etc.) **[c2]** | - | - | not built | forkmid / DeepCenter threshold / tempfuse | **none**: lab FAIL (G02, G03), K4 dropped (G06) | §1b |

Never tick two files with identical components; objective = P(private > raw x138) first, silver second (f2, l.1894-1895).

## 2b. Proposed K2/twin READ TABLE [c3] (round 3; NOT in CONTEXT at HEAD 1ca747b)

Source: `research/wf_ideas_v4/round3/report.json` plan_issues (verbatim block) and R3-A2. It counts as a pre-score
clarification of R3/R5/§f/f2 only if written into CONTEXT before any K2 or twin score appears in `poll.log` (earliest
~06:00 UTC 26 Sep). Rows tagged [OK] need the user's OK; without it the strict text applies (no K1, floor 0.953, §f order).
Refs: d1 = K2 - #35 (0.954; #35 = scored proxy of K1), d2 = twin - #34 (0.953). "Clean" iff the ledger shows L(K2) upper
bound <= 8.0 h (then the insertion deadline never fired). First matching row wins:

| Row | Condition | F1 | F2 |
|---|---|---|---|
| 1 | K2 ERROR | K1 = exp58t v1 in the next slot [OK], once scored, R5-admissible, >= 0.953 | twin by f2, else exp52 |
| 2 | twin - K2 >= +0.002 (R2 reopens) | twin | K2 if d1 >= -0.001 [OK], else K1 if scored [OK], else exp52 |
| 3 | d1 >= -0.001 (lowrefine kept) | K2 | twin if >= 0.953 (0.952 with floor OK), else exp52 |
| 4 | d1 <= -0.002 and clean | K1 [OK] once scored, R5-admissible, >= 0.953; no K1: twin [OK] [else §f item 4 = #34] | twin if >= 0.953 (no K1: exp52), else exp52 |
| 5 | d1 <= -0.002, not clean | d2 <= -0.002: as row 4; d2 >= -0.001: K2 (raise the runtime trigger to the user after comparing L(twin)) | twin if >= 0.953 (0.952 with OK), else exp52 |

Never: K1 at d1 = -0.001; exp56 while an admissible non-copy x138-family file exists; two files with identical components.
Round 3 rejects paraphrasing f2 as "never exp56/#35": f2 keeps #34 as the last resort before exp52 (FACTS C-26, C-27).

## 3. Status of pre-registered rules R1-R10 (PRE-REGISTRATION v3, user OK 25 Sep ~13:37 UTC)

| Rule | Content (short) | Applied when | Outcome / status | Source |
|---|---|---|---|---|
| R1 base | a = 0.953 and L34 <= 7.5 h -> x138 is the base, #34 non-degraded | 25 Sep 14:37 | a = 0.953, L34 in (6.29, 6.46] -> base = x138; branch D excluded | CONTEXT l.1797-1800 |
| R2 insertion | insertion in F1 if b >= a (tie counts for) | 25 Sep 16:20 | b = 0.954 >= 0.953 -> BRANCH A, K2 WITH insertion; S3 held | CONTEXT l.1801-1805 |
| R3 harmless riders (C01, C05, C04) | accept if dummy gates pass and public >= previous stack - 0.001; <= -0.002 remove | not yet (first read on K2 score, ~26 Sep 06:30-09:00) | pending for C01+C05 inside K2. **[c2]** C04 forkmid: no build (G02). forkblob: CLOSED by its lab gate (G01), so no OK is needed. **[c3]** The reference ("previous stack") is not named: K2 = 0.952 passes vs #34, fails vs #35; round 3 proposes d1 = K2 - #35 for the F1 stack and d2 = twin - #34 for lowrefine alone (§2b; FACTS C-27), to be written before any score. R3's "never try again" bars new builds, not an already scored f2 file | l.1647-1649; ADDENDUM L4 l.1865; `research/wf_ideas_v4/round3/report.json` PC3-01, R3-A2 |
| R4 node/fork changers | delta vs current F1 candidate: >= +0.002 -> F1; 0/+0.001 -> F2 candidate; <= -0.001 closed; never on lab gain alone | P36 (exp57 v1) vs #35; later K3b/K4 | **[c2]** P36 made INFO ONLY before it scored (CONTEXT (b) l.1904-1906), which settles the L35 ambiguity. K3b not built (G03), K4 dropped (G06), so R4 has no pending subject except an OK'd floatout (R2-A9 treats it as an R3 coordinate rider) | l.1650-1652, l.1808-1810 |
| R5 admission by time | scored without error AND (latency <= own REPAIR_DEADLINE_S: 7.5 h x138-type, 9.5 h C01 builds, OR step-0 margin >= 1 h); ungated-insertion files with L > 7.5 h excluded; exp51/52 always admissible | 25 Sep 16:20 (#34 yes, #35 no) | K2/twin pending on their own latency (poll every 10 min). **[c2]** `tools/runtime_ledger.py` automates R5(a) by family in `experiments/lb_poll/ledger.md`; K2 must be tagged with the safetail family (FACTS F-RUN-11). **[c3]** The message token suffices (no flags, C-28). F(K2) = 7.87 h gives a 1.63 h margin to 9.5 h, so R5(b) admits K2 and the twin unless they ERROR; "K2 fails R5" is an empty K1 trigger (F-RUN-13). P36 at 22:53Z: L > 6.58 h (info) | l.1653-1657, l.1806-1807; step0.md; `research/wf_ideas_v4/round3/report.json` new_facts (8)-(9), R3-A6 |
| R6 N1 trigger | build parrepair if L34 > 8.0 h, #35 error/timeout, L35 > 8.5 h with insertion, or F1 forecast > 9.0 h | 25 Sep 16:20 and 16:45 (step 0) | NOT triggered (L34 <= 6.46, L35 <= 7.73, K2 forecast <= ~7.8 h); no N1. **[c3]** Refined F(K2) = 7.87 h < 9.0 h: still not triggered | l.1658-1664, l.1804-1805, l.1811-1814 |
| R7 hygiene | validator/PP sweep off; no DIVINS_DUMP=1 in submissions; every stage fail-soft; first check node-count identity; no choice between near-copies by 0.001 except via R3 | continuously since 25 Sep 13:38 | respected in K2/K1/twin builds (DIVINS_DUMP 0, fail-soft verified by FF dummy). **[c2]** C-16 resolved: R7 applies to new builds (CONTEXT (d) l.1910-1911). Open: the floatout FLOATOUT_CHECK is a bare assert and needs a fail-soft wrapper before any use (round2 R2-A9). **[c3]** Cell 0 of K2 and the twin re-checked: VALIDATOR 0, DIVINS_DUMP 0, no LAB/FORCE_FAIL/TRAINLAB lines; kernels unchanged since their dummies. Round 3: K2's rank inside its score block is info only, never a decision input (R7) | l.1665-1670; probe.json exp58*/exp52; `research/wf_ideas_v4/round3/report.json` new_facts (6), R3-A7 |
| R8 deadlines | new mechanisms by 27 Sep 12:00; F1-final consolidation by 28 Sep 12:00; after 29 Sep 02:00 only emergency repeat (hard edge 10:00) | 25 Sep 18:20: E13/C08 closed on schedule; **[c2]** 20:05-20:35: forkblob, forkmid and DeepCenter decided on the lab before the 27 Sep cutoff | future cutoffs: new mechanisms 27 Sep 12:00, F1-final 28 Sep 12:00, emergency only after 29 Sep 02:00. **[c3]** Round 3: the new-mechanism search is over in practice (tail saturated, every rider gate failed; §1b G07-G11) | l.1671-1672; ADDENDUM L7 l.1883; `research/wf_ideas_v4/round3/report.json` plan_issues STRATEGIC |
| R9 do-not | no N2 size probe, no test-crop overlap consensus, no detector/edge/head retraining before 29 Sep, no knob ladders, no axis-flip on x138 | since 25 Sep 13:38 | in force; used to close the y3uanm secondary fine-tune and M3. **[c2]** Round 2 used it to reject knob ladders to fill the empty S4-S7 slots. **[c3]** Round 3 used it to keep axis-flip on x138 closed (G09) and to name retraining as the only lever left for the saturated tail (F-TRN-15); top movers at 22:16 likely use private retrained/ensembled models (F-LB-06) | l.1673-1676; FINAL_REPORT_v4 §2; `research/wf_ideas_v4/round3/report.json` rejected, new_facts (2) |
| R10 agent-hour priority | E1 > pre-reg > E2 > E4 build > E3 > step 0 > (N1 if R6) > E4/E5 analysis > E7 > E12; E1+E2 in git before moonshot code | 25 Sep 14:05-14:29 | satisfied: T1 safetail (14:05) and T2 lowrefine (14:29) merged first | l.1677-1678; CONTEXT §9 T1 l.1898, 14:29 l.1747-1752 |
| Finals rule §f | F1 = fullest admissible x138-family K build with C01, not a byte copy, riders passed R3/R4; F2 = exp52 (or twin per f2) | 29 Sep by 20:00 UTC (manual tick) | pending. **[c2]** Expected pair: F1 = K2 (if it scores without error and is admissible); F2 = exp58n twin with the f2 OK, else exp52. **[c3]** f2 OK'd 22:06 UTC; default pair F1 = K2, F2 = twin; edge cases by the proposed READ TABLE (§2b) | l.1707-1736; f2 l.1887-1895; 22:06 l.1960-1966 |

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

**[c3] Since 20:45 UTC.** CONTEXT 20:55 (l.1938-1954) records ADDENDUM M as post-hoc NOTES (not a pre-registration; no
verdict changed) and the ANTIPAR/DNVETO/K4/I-072 closures; the twin gates PASS (l.1955-1959); the user OK'd AMENDMENT f2
at 22:06 (l.1960-1966, git 1ca747b). Round 3 (`research/wf_ideas_v4/round3/report.json`, 22:59 UTC) proposes, all
pending in CONTEXT: the READ TABLE (§2b, before any score), an "S4-S6 empty" line plus the workflow-prompt edit
(`experiments/workflows/biohub-research-round.js` l.34, l.54; FACTS C-29), a new 26 Sep 00:1x RESUME POINT (C-26), the
poller window fix (F-RUN-14) and the curator closures (§1b G07-G11). Morning OK list (R3-A9, replaces round 2's R2-A8):
(1) K1 only on READ TABLE rows 1/4/5; (2) twin floor 0.952 while lowrefine is kept; (3) F1 = twin if twin - K2 >= +0.002;
(4) F1 = twin instead of #34 if lowrefine leaves F1 and no K1; (5) optional floatout (S12, fail-soft); (6) deadline move
or D4 only if the runtime trigger fires.
