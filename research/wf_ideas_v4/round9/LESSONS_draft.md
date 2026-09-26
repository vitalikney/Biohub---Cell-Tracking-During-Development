# Lessons draft (round 9, 26 Sep), to be finalised into CONTEXT section 11 after 29 Sep

LESSONS DRAFT for CONTEXT section 11 (full text below, Markdown). Core numbers: insertion +0.001 on the LB twice (lab +0.006, ratio ~1/6); x138 head +0.002 on our base vs +0.007 on x138's own base; edge filter lab +0.016 -> LB 0/-0.001; float output lab +0.002 -> two ties; leaf prune lab +0.0006/+0.0008 -> two ties; head retrain killed by an embryo-held-out test (+12% worse 6bba->44b6); fork removers 0 for 5; runtime by poller latency bounds with a concurrent twin as control (insertion <= 0.85 h); pre-registration made the finals read mechanical. FULL TEXT:

# LESSONS (draft for CONTEXT section 11; round 9, 26 Sep ~13:10 UTC; round-10 fixes R10-A5/A6 applied 26 Sep ~16:05 UTC; finalise after the private LB on 29 Sep)

Scope: what moved from our lab (in-sample train clips, official metric) to the public LB (one embryo, ~29% of the hidden test), and what did not. Public steps between our kernels are real on the public embryo, because the kernels are deterministic (curator, 25 Sep 19:05Z). Transfer to private (~71%, other embryos) stays unknown until 29 Sep; fill in section 5 then.

## 1. Transfer table (lab -> public LB)

| Mechanism | Lab (in-sample unless noted) | Public LB | Transfer |
|---|---|---|---|
| DaughterNet fork insertion (steal, cap 4, thr 0.4) | exp60 ins35: 44b6 +0.0058 (17 clips), 6bba +0.0065 (39 clips) | +0.001 twice (P27 0.947 -> P28 0.948; P34 0.953 -> P35 0.954), and K2 0.954 vs twin 0.953 | YES, at ~1/6 of the lab size (0..0.3 given 3-decimal rounding) |
| x138 V1284 coordinate head | retrained head: leak-group OOF distance -18.9% | +0.002 on our base (P28 0.948 -> P31 0.950); +0.007 on x138's own base (0.946 -> 0.953) | YES, but the size depends on the base: the head pays most where later stages consume positions (flow relink, readmit, gap filler) |
| x138 verbatim | author 0.953 | 0.953 (P34) | YES (takaito verbatim did NOT: author 0.951 -> ours 0.944, P24) |
| Edge filter (trusts the ILP/edge net) | +0.0162 / +0.0095 | 0.947 / 0.946 vs 0.947 (P29/P30) | NO (0 or negative): the edge net had seen the lab clips |
| Float output coordinates | +0.0019..+0.0025 (CI90 +0.001..+0.004) | ties twice (P32 = P31 0.950; P33 = P28 0.948) | NO visible gain (true public gain < ~0.0005) |
| Leaf prune 0.3 | +0.0006 (exp39 laptop), +0.0008 (x138 lp30, 51/56 clips up) | ties twice (P27 vs P20; P36 = P35 0.954, unrounded slightly above) | same sign, but below the display step |
| DivNet parent veto | +0.0023 in-sample (53 FP : 1 TP removed) | tie (P20 0.947 = P14) | NO: at best ~1 net FP removed on the public embryo |
| Relink off / bonus 2.5 / gshift | friend B +0.0053 on 12 videos (relink off) | 0.945 x3 vs 0.947 | NO (-0.002) |
| TTA / weight changes on a tuned stack | leaky local gains (z-flip +0.010) | z-flip 0.941/0.938, axis-flip 0.946, primary swap 0.944, fine-tuned secondary 0.937, soup 0.943 (base 0.947) | NO, all negative |
| Head retrain on 199 | leak-group OOF -18.9% | not submitted: kill test FAILED (embryo-held-out 6bba->44b6 +12.0% worse; it learns 6bba's z offset) | the kill test did its job |
| Lowrefine (V1284 refine of the lowdet pool) | node-neutral by design (+28 readmits on the 4-clip dummies (1,337 -> 1,365; 121,252 dummy nodes); no lab or hidden count) | d1 = K2 - #35 = 0; d2 = twin - #34 = 0 | harmless and invisible, as designed (R3 rider) |
| Overlap-consensus splice | exp64 K2 stack -0.00143 (in-sample, post-stop info; exp39 proxy -0.00047) | not submitted (G-A FAIL 43/62) | stopped by its own gate |

Rule of thumb that held: an in-sample lab gain transfers at somewhere between 0 and ~1/6 of its size. It transfers at all only when the mechanism adds evidence the base lacked (a separate division network, better localisation). Mechanisms that trust more of the same in-sample model (edge filter, DivNet veto, ILP over relink) transferred at 0. To see +0.002 on the public LB we needed about +0.012 in the lab. Apart from the insertion, nothing on x138 came within 5x of that; the next best were the z shift (+0.0016) and leaf prune (+0.0008).

## 2. Where the score was

- The gap to the top (0.975) is detection and localisation. 83% of missing GT nodes are absent upstream, and about half of FN edges are node misses (rounds 3 and 7). The linker tail's total ceiling was about +0.014 (ideas v2). The top teams retrained models. We froze ours on 24 Sep (R9) after our own retrains lost (0.920 all-199 scratch secondary, 0.937 fine-tuned secondary).
- Divisions: the 0.911 no-division diagnostic (P26) puts our public division Jaccard at ~0.36 on the exp29 base (P26: 0.947 - 0.911 = 0.036 = 0.1 x J), not x138 (score = 0.1 x div_J). On the x138 lab it is 0.129. On a low-J embryo, break-evens are 2-3x stricter for removing forks and looser for adding them. Fork-removal riders went 0 for 5 (forkmid, forkblob, ANTIPAR, already-divided, DNVETO); the only fork ADDER transferred.
- Sparse annotation: x138's readmitted and synthetic nodes match GT only ~1% of the time (73/13,284; 58/5,647). Most node-removal rules therefore act on unannotated cells, and the lab measures them with very low power.

## 3. Process lessons

1. Reproduce first. Spend one probe on a verbatim copy before building on a public notebook (x138 reproduced exactly; takaito lost 0.007).
2. Pre-register before the score. The READ TABLE (written 25 Sep 23:12Z, clarified in v2-v4, all before #37/#38 scored) made the 07:35Z finals read mechanical: row 3, no OK needed. Rules written after a number (ADDENDUM M, round 2) were labelled post-hoc and changed nothing.
3. Kill tests and power clauses stopped ideas that looked cheap (head retrain, forkmid, forkblob, ANTIPAR, K3b). Every LB read of the same classes was a tie or a loss. Not one closed idea has since shown an LB gain.
4. Sha-identity dummies (K1 dummy == exp57b; FF CSV == exp56; twin = K2 minus 12 fork edges) made every "off" path provably byte-identical. Fail-soft stages (safetail) made the runtime risk measurable.
5. Runtime is a first-class risk. Our only runtime evidence is latency from our own 10-min poller: L = (last PENDING poll, first COMPLETE poll], widened when a CLI call failed. Paired submissions ran concurrently, so the twin doubled as a runtime control: the insertion costs <= L(K2)_hi - L(twin)_lo = 0.85 h on the hidden run. Hidden reruns did not count against our GPU quota. Latencies against the 12 h limit: x138 <= 6.46 h, x138 + insertion (6.72, 7.73], K2 (7.36, 7.54], twin (6.69, 6.87] h.
6. LB mechanics: scores show 3 decimals, so the ~345 teams at 0.953 (15:16Z) are ordered by unrounded score, and ties go to the earlier submission. Late copies land at the bottom of their block. Our public rank drifted from #155 to #210 (15:16Z 26 Sep) at the same 0.954; that is not a signal.
7. Stop the mechanism search earlier. After the 25 Sep freeze, ten research rounds produced rule clarifications, closures and one stopped candidate (overlap consensus: G-A 43/62 < 60), but no score. They were useful for finals hygiene; a smaller budget would have found the same.
8. Check the rules text before setting policy. Two things we treated as "not allowed" (overlap consensus, an in-kernel sweep) were our own caution. The only TEST-DATA prohibition is hand labelling (3.4.b); private sharing of code or data is banned (3.5.d, 3.6.a), and original work (3.14.a) and no unfair practices (3.8.d) also bind. Check the rules early, then decide on method grounds.
9. Leaked material (cached private CSVs in public datasets) is neither usable nor allowed. A static CSV cannot score in a code-competition rerun, and the rules require original work (3.14.a, 3.8.d).
10. 'Keep more/shorter components' rules win in the lab through node count and do not transfer: round-3 boundary rescue, MIN_TRACK_LEN L4 (probe 6 = -0.002), I-146 on x138 (round 10: +0.00033, W/L 7/47, carried by 3 tiny clips).

## 4. Post-deadline list (with two more weeks)

All items: leak-free embryo-held-out bed with leak groups from day 1; bar = lab >= 6x the target public gain (insertion transfer ~1/6).

1. GPU retention-guard counterfactual (I-222): the guard switches 44b6 33.1% / 6bba 3.9% of frames from the 0.80-weight blend to primary-only. Arms guard-off / floor 0.8 / weight 0.475 on 44b6_9be80b04, e28840c6, eb2880fc, d2f34f90, c771cb04 + 6bba_ab78413d; ~1-2 GPU-h; sign unknown. Gate = same sign on both embryos, which is weak because the 6bba side is effectively one clip (ab78413d at 93%). Shake-up analysis only.
2. Axial localisation of z-elongated nuclei in 6bba: 477/668 missing GT nodes (71%; 436 in 6bba) have a final node at 7-10 um; misses are z-dominant 41% vs 25-28% in the control. Gate = embryo-held-out coordhead-v2 (train 6bba -> test 44b6 and the reverse), distance improves in BOTH directions (the head retrain failed exactly this: +12.0%).
3. Learned per-node/per-video z correction inside that coordhead-v2: a constant +0.1 vox gave +0.0016 in-sample (6bba +0.0015); transfer ~+0.0003 because the bias depends on the embryo (0.15 vs 0.45 um). Same gate.
4. Post-freeze-transition re-solve with geometric/flow cost only (never ILP or edge-net trust): x138 post-freeze excess ~0.0068 per 6bba GT; CPU-replayable on the exp60 presafe dump. Gate = held-out 6bba clips, plus a check that frozen frames exist on another embryo (freezes: 30/39 6bba clips, 0/17 44b6; they may be a 6bba acquisition/annotation artefact, so the hidden embryos may have none).
5. OOF linker evidence with a PRE-RELINK dump hook: exp60 dumps are post-relink (tools/trainlab.py l.243), so no relink-family arm can be replayed. Add the hook and a leak-group OOF edge net first. Gate = the lab reproduces the sign of the P21-P23 -0.002 public reads; those were on the exp29 base, so the lab check must use exp29 or be re-read on x138.
6. Far-daughter 8-12 um slot as an extension of the insertion (I-079): 62/99 GT divisions detected but unforked, far daughter median 9.9 um, 33/62 at 8-12 um. The evidence is 6bba-dominated (88/99 divisions). Bar: lab >= +0.012 (1/6 transfer -> +0.002 public).
7. Overlap consensus only with a NEW splice design (the owner rule hurt: exp64 K2 stack -0.00143, exp39 proxy -0.00047) and a new G-A whose floors are fixed on a held-out subset of pairs, never on the same 199 videos (58/62 is not a floor).
8. Joint detector + edge fine-tune on dense pseudo-labels that include teacher EDGES, on the leak-free bed (Canh: head-only -0.003, encoder-only -0.038).

## 5. PRIVATE column (fill in on 30 Sep)

| File | Public | Private | Rank |
|---|---|---|---|
| #37 K2 (x138 + safetail + lowrefine + insertion) | 0.954 | | |
| #38 twin (no insertion) | 0.953 | | |
| #34 x138 verbatim 56545267 (not ticked; reference) | 0.953 | | |
| #35 x138 + insertion 56545786 (not ticked; reference) | 0.954 | | |
| P36 x138 + leaf prune + insertion 56555189 (diagnostic; not ticked) | 0.954 | | |

Pre-registered contrasts (CONTEXT, 26 Sep round-10 entry "PRIVATE-READ PREDICTIONS"; calibration only, never a finals input), in thousandths of the DISPLAYED 3-decimal private scores, priors P(<0) / P(=0) / P(>0):
- C1 insertion on plain x138 = #35 - #34: 0.10-0.15 / ~0.30 / 0.55-0.60.
- C2 insertion on the K2 stack = #37 - #38: 0.10-0.15 / ~0.30 / 0.55-0.60.
- C3 lowrefine + safetail = #38 - #34: ~0.10 / ~0.80 / ~0.10.
- C4 leaf prune = P36 - #35: ~0.15 / ~0.70 / ~0.15 (lab +0.0008, public 0).
Reading: C1 and C2 with the same non-zero sign = the insertion transfers to the private embryos. One embryo split can only fail to contradict the ~1/6 lab->LB rule, never confirm it. Our private result = max(#37, #38). No rank-vs-0.953-block reading (rivals' private = max of their own two files).

PRIVATE-READ PRE-REGISTRATION v2 (26 Sep, round 12; see CONTEXT): (a) CONFOUND (R12P-1): #35 has L in (6.72, 7.73] h, so it may have crossed x138's own 7.5 h deadline, which can only LOWER #35. That biases C1 down and C4 up. C1 > 0 and C4 <= 0 are clean reads; C1 <= 0 and C4 > 0 are ambiguous. The C1 prior P(<0) becomes 0.12-0.18. (b) OUTCOME TABLE, first match wins, over displayed contrasts in thousandths. (i) C2<0 & C1>0: stack interaction (lowrefine suspect). (ii) C2<0: the insertion is embryo-specific on the finals stack; demote item 6. (iii) C1>0 & C2>0: promote item 6. (iv) C2>0 & C1<=0: clean on K2, C1 unresolved. (v) C1>0 & C2=0: weak, no promotion. (vi) C1<0 & C2=0: #35 degrade or harm, not separable. (vii) C1=C2=0: uninformative. Ordering C1 against C2 needs |C2-C1| >= 2. C3 promotes or demotes only at |C3| >= 2. C4 <= 0 closes leaf prune; C4 > 0 is ambiguous. SCOPE: only #34, #35, P36, #37 and #38 are pre-registered. Every file submitted after 26 Sep 20:33Z (the ladder, new finals) is outside the table and post-hoc. (c) RANK CALIBRATION (R12P-3 amended): our result = the max over the pair actually SELECTED at 29 Sep 20:00Z, each file with its own submit time. If that pair is not {#37, #38}, re-issue a dated forecast before 29 Sep 23:59Z or label the read 'forecast was for a different pair'. Tie read, three cases: above every earlier exact copy -> max > X; between the earlier and the later copies -> = X; below the whole run -> < X. The margin read is replaced by the unrounded-order read: the fraction of public-0.955-0.957 teams ranked above the X copy run, plus their median rank change. One draw, no rule. (d) PROCEDURE (R12P-4 amended): F = API SELECTED after 20:00Z. Read list: #34 56545267, #35 56545786, P36 56555189, #37 56563521, #38 56563534, plus every probe from 26 Sep 20:33Z on. Take a public LB snapshot on 29 Sep ~23:00-23:45Z with `python -m kaggle competitions leaderboard biohub-cell-tracking-during-development -d -p experiments/private_read/`, rename it with a timestamp, and allow 3 retries with 60-120 s backoff. From 30 Sep 00:15Z, hourly: call competition_submissions(..., page_size=100), fail loudly on a missing ref, and cross-check with the CLI using --page-size 100. Board check: our Score == max over F AND the top-50 differs from the 23:30Z snapshot; otherwise use the Private tab, read-only. Compute the medal lines from N, then C1-C5 and I. Report both reads: at first publication and after cleanup. (e) WHOLE-HISTORY TRANSFER TABLE (r12p-3 corrected): E = {P27->P28, P34->P35 (degrade flag), P38->P37, P28->P31}; T = {P20->P29, P20->P30, P14->P20, P11->P12, P14->P16, P14->P19, P14->P21/22/23}; N = {P31->P32, P28->P33, P35->P36 (flag)}. Only non-zero displays count. H-E: at least 2 non-zero E > 0 and none < 0. H-T: negatives outnumber positives among the non-zero T; not read with fewer than 3 non-zero. Report r as the interval [(S-k)/D, (S+k)/D], with and without P34->P35. Bar: 0.002/lower end (floor 0.004) if the lower end > 1/6; +0.02 or learning only if the upper end < 1/6 or S <= 0; otherwise 1/6. Never divide by S <= 0. Calibration only. (f) One conditional late-sub arm (R12P-5 merged): K1 exp58t v1, no rebuild, only if C1 <= 0 and C2 > 0 at 3 dp. It needs its own user OK on 30 Sep.

Questions for 30 Sep: did the insertion transfer to private (C1, C2)? Did the 0.955-0.957 public risers hold their places?


Evidence: experiments/lb_poll/poll.log (probes 10-38); CONTEXT.md l.1446-1525, l.2072-2082, l.2118-2140; experiments/exp60_trainlab/results.md; research/wf_ideas_v4/round6 R6H-7 (earlier 10-item lessons, merged here); round7 r7h-3; draft copy in this agent's scratchpad lessons.md
