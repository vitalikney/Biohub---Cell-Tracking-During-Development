# Ideas workflow v2: final report (24 Sep 2026, ~18:20 UTC)

The workflow started with 9 lenses. Their hypotheses were deduplicated to 14 ideas, each idea was researched and checked by 3 skeptics (transfer, arithmetic and feasibility), and a critic added 2 more ideas in round 2. This page is the synthesis. Machine-readable version: `research/wf_ideas_v2/final.json`. Crash log: `final.notes.md`.

## Bottom line

- **Public 0.97 is out of reach.** Expected public is about 0.955, and even with every idea at its best case the total is about 0.962.
  - Starting point is 0.948 (exp48).
  - The x138 coordinate head (probe 31, pending) should add about +0.005.
  - The six kept ideas add about +0.002 together in expectation.
  - The 0.965-0.975 band needs +0.017 to +0.027. That is more than the sum of all the ceilings (+0.014).
- **The edge filter adds nothing on public.** Probe 29 (full filter) scored 0.947, a tie with exp39. Probe 30 (drop-only) scored 0.946. The lab's +0.016 was an in-sample artefact of the edge network and ILP. The stitch that depended on it is closed too.
- **The plan for the last five days:**
  1. Lock in the x138 head.
  2. Add float output coordinates, using a truncation-safe encoding.
  3. Add the two cheap riders (fork midpoint, overlap splice) only through scored files.
  4. Choose the two finals with a best-of-two rule. F2 carries the edge filter as a private hedge.

## Probe status (24 Sep)

| probe | file | public | reading |
|---|---|---:|---|
| 28 | exp48 = exp39 + leaf prune + DaughterNet insertion | **0.948** | current best |
| 29 | exp39 + edge filter ef_a3_rl_pr (lab +0.0162) | 0.947 | tie: in-sample, closed |
| 30 | exp39 + drop-only filter ef_a0 (lab +0.0095) | 0.946 | does not transfer |
| 31 | exp51 = exp48 + x138 V1284 head | pending | expected ~0.951-0.955 |

## Kept ideas, ranked

| # | idea | public gain (after local-to-LB discount) | probability | effort | ships as |
|---|---|---|---|---|---|
| 1 | Float output coordinates, truncation-safe encoding | +0.001 (0 to +0.002) | no harm 0.97; visible 0.45 | 3 h + 2 kernels | P32/P33 on 25 Sep |
| 2 | Finals rule based on E[max] (best of two) | 0 public; +0.001-0.0015 private | premium always >= 0 | 1 h desk | finals, 29 Sep |
| 3 | Edge filter kept as a finals hedge (F2 only) | 0 public; private upside | 0.3 that it helps private | 1 h + 1 slot | P36 on 25 Sep |
| 4 | Overlap consensus across test clips | ~+0.0005 (0 to +0.002) | overlap 0.5; gate 0.6 | 4 h probe, 1-1.5 d full | bit-probe, then F1' |
| 5 | Fork-midpoint filter (repaired) | +0.0003 to +0.0008 | net positive 0.65 | 3-4 h | rider in F1' |
| 6 | Plain 199-video head retrain (pilot) | ~+0.0003 (0 to +0.002) | visible ~0.05 | ~1 d + 2 GPU h | P39, only if gated in |

### 1. Float output coordinates (all 3 skeptics survived)
- **Why it helps.** The scorer matches each frame with optimal 1/(1+d) assignment and never rounds. Our writer's `int(round())` adds z-quantisation noise (0.47 um RMS), which flips near-tie matches. Floats remove that noise.
- **Already measured on all 199 videos** (exp39 tail, scorer reproduced 199/199):

  | output encoding | gain | CI90 |
  |---|---:|---|
  | plain float | +0.0018 | |
  | safe encoding | +0.0019 | [+0.00115, +0.00271] |
  | plain float on a truncating server | -0.004 | |

  Node count and divisions are identical in every case.
- **Safe encoding.** `w = max(0, r + min(max(round(v - r, 3), 0), 0.499))` with `r = round(v)`, written as `%.3f`. Then `floor(w) == round(v)`, so a server that rounds or int-casts scores exactly as today. A server that keeps Float64 gets the gain.
- **Gate (regression check on e48 tails, Kaggle CPU):**
  - overall >= +0.0010;
  - 6bba CI90 lower bound > 0;
  - 44b6 >= -0.0005;
  - 6bba wins >= 55% among the videos that change;
  - nodes, edges and divisions byte-identical.
- **LB rule.** Keep it if the public score is not lower (the same score is harmless). Revert on a parse error or a drop of 0.002 or more.
- **Implementation.** New `--patch floatout` (`OUTPUT_FLOAT_COORDS=0|safe|float`; 0 is byte-identical to today), plus `out.coords` in `replay.write_geff`.

### 2. Finals rule (all 3 survived; desk rule)
Kaggle ranks each team by the better of its two private scores. So the second final should maximise `E[D+] = mu*Phi(mu/s) + s*phi(mu/s)`, where D is its private score minus F1's, with mean mu and spread s. It should not be a near-copy of F1.

- **F1** = the best scored file of the form B + float.
  - B = exp51 if P31 >= 0.951.
  - B = exp48 if P31 < 0.948.
  - If P31 is 0.949-0.950, keep both candidates and take the higher float version.
  - A rider moves into F1 only through a scored file F1' that is not lower than F1.
- **F2** = F1 + edge filter + stitch.
  - Eligible only if its public score is >= F1 - 0.003.
  - Expected premium ~+0.0019 at mu ~0 and s >= 0.0048. A near-copy would give only ~+0.0002.
- **Fallback F2** = the other base, i.e. the same pipeline with coordhead toggled.
- **Never** pick the maximum public score among near-copies (winner's curse ~+0.0013).
- **Tick both finals by hand by 29 Sep 20:00 UTC.**

### 3. Edge filter as a finals hedge (2 of 3 survived; merged into item 2)
- **No `ef_anom` variant.** The edge filter already gates itself: it is neutral on ordinary transitions, and every restriction either equals it or throws away 17-53% of it.
- **Probe reading.** Probes 29 and 30 are flat, so the edge filter goes into exactly one final (F2).
- **Build (P36):** B + float + `--patch edgefilter` (ENABLE=1, ALT=3, RELINK=1, PRUNE=1) + `--patch stitch` (STITCH_ENABLE=1, st_all). This is the lab-confirmed pair.
- **Before submitting,** check that the dummy-clip logs show nonzero drops and stitches. The edge filter has never run on coordhead float coordinates.
- **If F1 changes later,** rebuild F2 as F1' + edge filter + stitch.

### 4. Overlap consensus (round 2; all 3 survived)
- **Mechanism.**
  - The 44b6 videos are overlapping space-time crops of one recording, and the crops are bit-identical where they overlap.
  - 198 GT edges are discordant: TP in one copy and FN in the other.
  - A GT-free owner rule picks the copy farther from its crop border and clip end. It is right 70-72% of the time.
  - Simulated ceiling: +0.006 on a 44b6-type embryo (+89 FN units, +41 FP units).
- **Step A: registration on train** (Kaggle CPU, ~30 min). Match overlaps by exact-content anchor hashing. Gate:
  - >= 60 of the 65 known 44b6 pairs recovered;
  - 0 pairs in 6bba;
  - 0 pairs across embryos.
- **Step B0: bit-probe.** Needs the user's OK and a check of the rules page. A kernel runs registration only on the hidden test clips and raises an error if any overlap exists. An error means build the splice; a valid score means close the line.
- **Step B: splice.** Build rules:
  - Correspondence radius 3.5 um.
  - Agreement is judged at track level.
  - The owner takes over only if its score leads by >= 3 AND the non-owner scores < 8.
  - Components with forks are skipped, and so are the 36 edges seen in three copies.
  - A video reverts if its node count rises by more than 0.5%.
  - If the cell throws, the untouched CSV is kept.

  Gate:
  - 44b6 >= +0.002;
  - sign test over leak groups, >= 7 positive;
  - the result without group 0 is >= 0;
  - 6bba bit-identical;
  - node ratio <= +0.3%;
  - divisions unchanged.
- **Risk.** 75% of the simulated gain sits in one leak group. The test embryo may have fewer clips. It is transductive use of the test clips, so the rules must be checked first.

### 5. Fork-midpoint filter, repaired (3 skeptics refuted it as written; their fixes converge)
- **Change.** Only on safe-division forks, never on DaughterNet-inserted ones: their true-positive midpoint distances are 2.86-5.94 um, and the 4.0 um rule on all forks deletes 6 of 10 inserted TP. Use a 4.5 um threshold, because coordhead positions cannot be re-validated. Run it as the last graph edit. Nodes are never touched.
- **Verification run** (FM45_sd on e48, all 199 videos). Pass criteria:
  - 0 division TP lost on each embryo;
  - division FP down by >= 4;
  - adjusted edge delta >= -0.0001;
  - identical node and inserted-fork counts;
  - 1.36*dTP - 0.36*dFP > 0.
- **Ships** only as a rider in a scored F1'.

### 6. Plain head retrain on train videos (reduced from `gate-aware-refine-head`; conditional long shot)
- **Start only if both hold:** P31 >= 0.951, and the zero-mode control P35 shows that the shift itself carries the gain (exp51 - zero >= 0.002).
- **Pilot capture:** 36 videos, ~1.3-2 GPU h.
- **Training:** 224-32-3 MLP with Huber loss on pairs within 4 um, per-embryo mean offset removed, output bounded to 2 um, embryo-held-out folds.
- **Kill it unless all three hold on both held-out embryos:**
  - the share within 4 um is >= +0.005 over the public head;
  - the 4-7 um zone count drops by >= 3%;
  - the mean shift stays within ±0.2 um of the public head's.
- **LB:** one probe. Adopt only if it scores >= F1 + 0.001.

## Dropped

| idea | why |
|---|---|
| stitch (tie-aware gate) | Its condition, probe 29 >= 0.950, failed. It survives only as a rider inside F2. |
| frozen-frame double step | The geometric part measures ~0. The remaining ILP-first part is the in-sample channel that gave 0/-0.001/-0.002 on the LB. |
| division cap for private J | Beyond cap 4 the marginal is 0 TP / +2 FP. Density scaling is refuted. The looser threshold is already shipped. |
| dorado out-of-sample lab | Nothing is left for it to gate. Stage 1 would finish too late. It is the same embryo as 44b6. |
| out-of-fold edge scorer | A fine-tune from the public weights is not out-of-fold. The plumbing is below the gate; the oracle is +0.0019 at perfect flips. |
| hole fill (sandwich) | The 4-6 um holes are the same imaged blob, so fills become duplicates. The sandwich test passes 40% of random points. |
| refined duplicate collapse | Head-free variants measured -0.002 to -0.013. The oracle is +0.0004/+0.0020, and the head does not make pairs converge. |
| polyphase shift-and-stitch | It removes the same grid error as the head. The dose-response bound is +0.001-0.002. |
| anisotropic RTS smoother | Anisotropy is ~1.08. The re-smooth's value came from the edge filter, which is closed. The 44b6 sign is negative. |
| clip-boundary frames | There is no detector padding. The ILP end effect has a +0.0011 oracle, which the node multiplier cancels. |

## Schedule (UTC)

- **Thu 24 Sep (0 slots left)**
  - Write `--patch floatout`.
  - Build exp52 = exp51 + float and exp53 = exp48 + float.
  - Run the float regression in the CPU lab.
  - Run overlap Step A on train.
  - Write the bit-probe kernel.
  - Ask the user to approve the 25 Sep batch.
- **Fri 25 Sep (5 slots)**
  - P31 scores around 01:00-03:00, which sets the base B.
  - P32 = B + float.
  - P33 = the other base + float.
  - P34 = bit-probe, if approved.
  - P35 = exp51 zero-mode, only if P31 >= 0.951.
  - P36 = F2 hedge (B + float + edge filter + stitch).
  - Lab: fork-midpoint verification.
  - Friend A's DaughterNet-B, lab only. It enters only if added-fork precision is >= 0.45.
- **Sat 26 Sep (GPU quota resets)**
  - Head-retrain pilot and kill test, if the start conditions hold.
  - Overlap splice lab, if the bit-probe raised an error.
  - P37 = F1 + fork-midpoint.
- **Sun 27 Sep (submit by ~12:00)**
  - P38 = F1' + overlap splice, if its gate passed.
  - P39 = F1' + retrained head, if the kill test passed.
  - P40 = F2 rebuilt on the final F1.
- **Mon 28 Sep**
  - Last submission ~06:00-08:00, because scoring takes 8-10 h.
  - Run the desk E[D+] table and record the decision in CONTEXT.md.
- **Tue 29 Sep**
  - No probes.
  - Tick F1 and F2 by 20:00 and verify on the submissions page.

About 9-11 of the 25 remaining slots will be used.

## Honest outlook (arithmetic)

| component | expected | best case |
|---|---:|---:|
| exp48 base | 0.948 | 0.948 |
| x138 head (probe 31) | +0.005 | +0.007 |
| float coords | +0.001 | +0.002 |
| fork-midpoint rider | +0.0005 | +0.001 |
| overlap consensus | +0.0005 | +0.002 |
| head retrain | +0.0003 | +0.002 |
| edge filter / stitch / finals hedge | 0 (public) | 0 (public) |
| **total** | **~0.955** | **~0.962** |

- **Probabilities:** P(>= 0.955) ~0.5; P(>= 0.960) ~0.05; P(>= 0.965) < 0.01.
- **Where we would land.** On the 24 Sep board, 0.955 is about rank 70-80, and that rank will drift down as copies of x138 spread.
- **Why the top teams are out of reach.** They (0.969-0.975) report gains from model retraining. That route cannot be validated and shipped honestly in 5 days with an in-sample lab.
- **What the kept ideas do.** They secure about +0.006-0.008 over today's best with near-zero downside, and they add a private-only hedge through the second final.
