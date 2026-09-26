# Lessons draft (round 9, 26 Sep), to be finalised into CONTEXT section 11 after 29 Sep

LESSONS DRAFT for CONTEXT section 11 (full text below, Markdown). Core numbers: insertion +0.001 on the LB twice (lab +0.006, ratio ~1/6); x138 head +0.002 on our base vs +0.007 on x138's own base; edge filter lab +0.016 -> LB 0/-0.001; float output lab +0.002 -> two ties; leaf prune lab +0.0006/+0.0008 -> two ties; head retrain killed by an embryo-held-out test (+12% worse 6bba->44b6); fork removers 0 for 5; runtime by poller latency bounds with a concurrent twin as control (insertion <= 0.85 h); pre-registration made the finals read mechanical. FULL TEXT:

# LESSONS (draft for CONTEXT section 11; round 9, 26 Sep ~13:10 UTC; finalise after the private LB on 29 Sep)

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
| Lowrefine (V1284 refine of the lowdet pool) | node-neutral by design (+28 readmits of 121,252) | d1 = K2 - #35 = 0; d2 = twin - #34 = 0 | harmless and invisible, as designed (R3 rider) |

Rule of thumb that held: an in-sample lab gain transfers at somewhere between 0 and ~1/6 of its size. It transfers at all only when the mechanism adds evidence the base lacked (a separate division network, better localisation). Mechanisms that trust more of the same in-sample model (edge filter, DivNet veto, ILP over relink) transferred at 0. To see +0.002 on the public LB we needed about +0.012 in the lab. Apart from the insertion, nothing on x138 came within 5x of that; the next best were the z shift (+0.0016) and leaf prune (+0.0008).

## 2. Where the score was

- The gap to the top (0.975) is detection and localisation. 83% of missing GT nodes are absent upstream, and about half of FN edges are node misses (rounds 3 and 7). The linker tail's total ceiling was about +0.014 (ideas v2). The top teams retrained models. We froze ours on 24 Sep (R9) after our own retrains lost (0.920 all-199 scratch secondary, 0.937 fine-tuned secondary).
- Divisions: the 0.911 no-division diagnostic (P26) puts our public division Jaccard at ~0.36 (score = 0.1 x div_J). On the x138 lab it is 0.129. On a low-J embryo, break-evens are 2-3x stricter for removing forks and looser for adding them. Fork-removal riders went 0 for 5 (forkmid, forkblob, ANTIPAR, already-divided, DNVETO); the only fork ADDER transferred.
- Sparse annotation: x138's readmitted and synthetic nodes match GT only ~1% of the time (73/13,284; 58/5,647). Most node-removal rules therefore act on unannotated cells, and the lab measures them with very low power.

## 3. Process lessons

1. Reproduce first. Spend one probe on a verbatim copy before building on a public notebook (x138 reproduced exactly; takaito lost 0.007).
2. Pre-register before the score. The READ TABLE (written 25 Sep 23:12Z, clarified in v2-v4, all before #37/#38 scored) made the 07:35Z finals read mechanical: row 3, no OK needed. Rules written after a number (ADDENDUM M, round 2) were labelled post-hoc and changed nothing.
3. Kill tests and power clauses stopped ideas that looked cheap (head retrain, forkmid, forkblob, ANTIPAR, K3b). Every LB read of the same classes was a tie or a loss. Not one closed idea has since shown an LB gain.
4. Sha-identity dummies (K1 dummy == exp57b; FF CSV == exp56; twin = K2 minus 12 fork edges) made every "off" path provably byte-identical. Fail-soft stages (safetail) made the runtime risk measurable.
5. Runtime is a first-class risk. Our only runtime evidence is latency from our own 10-min poller: L = (last PENDING poll, first COMPLETE poll], widened when a CLI call failed. Paired submissions ran concurrently, so the twin doubled as a runtime control: the insertion costs <= L(K2)_hi - L(twin)_lo = 0.85 h on the hidden run. Hidden reruns did not count against our GPU quota. Latencies against the 12 h limit: x138 <= 6.46 h, x138 + insertion (6.72, 7.73], K2 (7.36, 7.54], twin (6.69, 6.87] h.
6. LB mechanics: scores show 3 decimals, so the ~330 teams at 0.953 are ordered by unrounded score, and ties go to the earlier submission. Late copies land at the bottom of their block. Our public rank drifted from #155 to #204 at the same 0.954; that is not a signal.
7. Stop the mechanism search earlier. After the 25 Sep freeze, nine research rounds produced rule clarifications, closures and one stopped candidate (overlap consensus: G-A 43/62 < 60), but no score. They were useful for finals hygiene; a smaller budget would have found the same.
8. Check the rules text before setting policy. Two things we treated as "not allowed" (overlap consensus, an in-kernel sweep) were our own caution. The Kaggle rules ban only hand labelling of test data and private sharing of code or data (3.4.b, 3.5.d, 3.6.a). Check the rules early, then decide on method grounds.
9. Leaked material (cached private CSVs in public datasets) is neither usable nor allowed. A static CSV cannot score in a code-competition rerun, and the rules require original work (3.14.a, 3.8.d).

## 4. Post-deadline list (with two more weeks)

1. Detector and localisation: a joint fine-tune (detector + edges) with dense pseudo-labels that include teacher EDGES (Canh: head-only fine-tune -0.003, encoder-only -0.038). Axial localisation of z-elongated nuclei in 6bba.
2. A learned per-node or per-video z correction with an embryo-held-out gate. A constant z shift gave +0.0015 on 6bba in-sample, but the bias depends on the embryo (44b6 +0.15 um vs 6bba +0.45 um).
3. A post-freeze re-solve using only geometric/flow cost (never ILP or edge-net trust).
4. Overlap consensus with a new, pre-registered G-A at lower floors (58/62 pairs sit at the exact offset).
5. A leak-free validation bed from day 1: models trained on one embryo and scored on the other, with leak groups.

## 5. PRIVATE column (fill in on 30 Sep)

| File | Public | Private | Rank |
|---|---|---|---|
| #37 K2 (x138 + safetail + lowrefine + insertion) | 0.954 | | |
| #38 twin (no insertion) | 0.953 | | |
| #34 x138 verbatim (not ticked; reference) | 0.953 | | |

Questions for 30 Sep: did the insertion transfer to private (K2 - twin)? Did the 0.955-0.957 public risers hold their places?


Evidence: experiments/lb_poll/poll.log (probes 10-38); CONTEXT.md l.1446-1525, l.2072-2082, l.2118-2140; experiments/exp60_trainlab/results.md; research/wf_ideas_v4/round6 R6H-7 (earlier 10-item lessons, merged here); round7 r7h-3; draft copy in this agent's scratchpad lessons.md
