# L6: false-negative anatomy, the end-to-start stitch, and the swap rule (2026-09-24)

Scripts: `fn_anatomy.py` (FN classes, stitch candidates, exact stitch estimates), `swap_anatomy.py` (swap moves and
an exact evaluation of the kernel function). Replay out dir: `.public_local_cache/l2_replay/l6_stitch`. Official metric
throughout. Protocol: design and grid on SELECTION (64 videos, all 6bba), one CONFIRMATION run (135 videos: 71 44b6,
64 6bba). Gate: delta >= +0.002, each embryo >= +0.001, gain on >= 55% of videos per embryo, 90% CI low > 0.

## 1. FN classes of the final exp39 graph (199 videos)

Validation: the FN count equals the official `edge_fn` in every video (6,732 in total), and per-video TP/FP/FN equal
the replay csv. No GT node has more than one match. The same holds for the exp39 + ef_a3_rl_pr graph (6,099 = its
official FN count).

| class | what it means | exp39 all | 44b6 | 6bba | exp39+ef all |
|---|---|---:|---:|---:|---:|
| a_never | no raw ILP node within 7 um of the GT node | 1907 | 167 | 1740 | 1907 |
| a_tail | a ckpt node within 7 um was removed by the tail (short-track filter etc.) | 606 | 81 | 525 | 624 |
| a_linefit | the node survives, but linefit moved it more than 7 um from the GT node | 354 | 28 | 326 | 353 |
| a_taken | a final node within 7 um was assigned to another GT node | 62 | 16 | 46 | 62 |
| b_break | p_u is a track end and p_v a track start | 150 | 5 | 145 | 399 |
| b_v_taken | p_u is an end; p_v is linked from another node | 701 | 150 | 551 | 556 |
| b_u_diverted | p_u is linked elsewhere; p_v is a start | 706 | 156 | 550 | 593 |
| b_swap | both p_u and p_v are linked elsewhere | 2175 | 444 | 1731 | 1528 |
| c_gap_node | a matched end is a synthetic gap node | 57 | 16 | 41 | 57 |
| c_gap_node_off | an unmatched end, where our track passes through a synthetic node | 14 | 0 | 14 | 20 |
| **total** | | **6732** | **1063** | **5669** | **6099** |

- **Detection side (a_\*)**: 2,929 FN (43.5%). There are no GT edges spanning more than one frame.
- **Where the ILP had the edge (b_\*)**:
  - exp39: break 115/150, swap 558/2175, u_diverted 288/706, v_taken 246/701.
  - After the edge filter: swaps with an ILP edge fall to 1 (the filter fixes those).
  - The filter creates new breaks (150 -> 399; 281 of them have an ILP edge).
- **Oracle** (recover every FN of the class, and drop the competing edges): swap +0.0457 (ef graph: +0.0323), u_diverted +0.0095, v_taken +0.0099, break +0.0011 (ef: +0.0030).

## 2. Recoverable class: breaks the ILP had, and the stitch rule

- **Candidate pairs.** On the exp39+ef graph, 6,228 end->start pairs are linker (ILP) edges: 232 TP, 17 FP (precision 0.93).
- **Pairs without an ILP edge.** Mutual-nearest-neighbour pairs of this kind are 17% precise, so they are not usable.
- **Why the pairs are free.** The motion relink drops ILP links it cannot place inside its gates (median 10.6 um). Nothing afterwards restores them.

**Rule** (`stitch_final_graph`, `tools/build_probe_kernel.py --patch stitch`, replay `st.*`), applied after linefit and
after the edge filter:
1. Re-add every linker edge whose source is a track end and whose target is a track start at t+1.
2. Order by p, descending; each node is used once.
3. Knobs: `min_prob`, `max_um`, `min_um`, `min_chain`.

Exact estimates (edge counts exact; division term held fixed):

| graph | added | TP | FP | score delta |
|---|---:|---:|---:|---:|
| exp39 | 1156 | 115 | 5 | +0.0008 |
| exp39+ef | 7182 | 281 | 19 | +0.0020 |

Selection replay (`l6_selection_stitch.md`, control exp39):

| config | score | vs ef_a3_rl_pr |
|---|---:|---:|
| ef_a3_rl_pr | 0.912468 | 0 |
| **ef_st_all** | **0.914252** | **+0.001784** |
| ef_st_c2 | 0.914184 | +0.001716 |
| ef_st_p06 | 0.914167 | +0.001699 |
| ef_st_p07 | 0.914143 | +0.001675 |
| ef_st_p08 | 0.913984 | +0.001516 |
| ef_st_max12 | 0.913886 | +0.001418 |
| st_all / st_p08 (on exp39) | 0.898486 / 0.898511 | +0.00067 / +0.00070 vs exp39 |

Confirmation, run once (`l6_confirmation_vs_ef.md`, control ef_a3_rl_pr):

| config | delta | 90% CI | 44b6 | 6bba | win rate 44b6 / 6bba | div TP/FP/FN |
|---|---:|---|---:|---:|---|---|
| ef_st_all | **+0.002114** | [+0.00161, +0.00262] | +0.001167 | +0.002474 | **15.5%** / 71.9% | 16/28/71 (unchanged) |

**Gate: FAIL.** Delta, both embryo deltas and the CI pass; only the 44b6 win rate fails.
- 59 of 71 44b6 videos are unchanged (ties). 11 of the 12 changed videos gain, 1 loses.
- A stricter variant cannot pass either, because it touches fewer videos. Exact 44b6 confirmation win rates: p>=0.7 14%, p>=0.8 11%.
- Replay config: `ef_st_all=exp39,ef.alt=3,ef.relink=1,ef.prune=1,st.enable=1`.
- Kernel: `python tools/build_probe_kernel.py <name> --patch edgefilter --patch stitch --set EDGEFILTER_ENABLE=1 --set EDGEFILTER_ALT=3 --set EDGEFILTER_RELINK=1 --set EDGEFILTER_PRUNE=1 --set STITCH_ENABLE=1`
  (build tested; the test build was deleted; not pushed).

## 3. Swaps, u_diverted and v_taken are localisation misses, not linking errors

These numbers are for SELECTION, exp39+ef graph, 717 swap FN:
- **The GT link is normal.** Median 2.6 um (the video's GT step median is 1.7 um).
- **Its matched predicted nodes are far apart.** Median 9.4 um.
- **Our competing links are short and smooth.** 1.5 um and 1.4 um, p ~0.76, constant-velocity error 0.85 um. The motion model prefers our link in 98.6% of swaps.
- **The matches are loose.** Match distance GT->predicted at swap endpoints is 4.4 / 4.7 um, against 1.8 um at TP endpoints; 90% have one end more than 3 um off.
- **Our continuations are free.** They are unmatched in 96-99% of cases. The complementary GT link x->y exists in 0%.
- **u_diverted and v_taken** show the same pattern at one end (loose end 3.9 / 4.4 um).

So the annotated nucleus lies between two of our tracks, about 9 um apart. The 7 um assignment takes track A at t and
track B at t+1. The fix is a node at the right position (detection or localisation), not a relink. The +0.03 oracle
cannot be reached by relinking.

**Rule tested anyway** (the coordinator's request): `swapfix_final_graph` (`--patch swapfix`, replay `sw.*`).
- The move is a local 2x2 re-assignment a->b + c->d => a->d + c->b.
- It fires when the sum of second differences (constant velocity) drops by >= `min_gain_um` with >= `min_terms` context terms.
- Moves are node-disjoint and applied greedily by gain.

The exact evaluation (`l6b_swap_eval_selection.json`) and the replay agree:

| config | swaps | selection vs ef | confirmation vs ef |
|---|---:|---:|---|
| ef_sw_t4_g3 | 34 | 0.000000 | not run |
| ef_sw_t3_g4 (picked) | 64 (79 on conf) | 0.000000 | -0.000038 [-0.00011, 0]; 44b6 0, 6bba -0.000052 |
| ef_sw_t2_g2 | 128 | -0.000048 | not run |

**Gate: FAIL**, with no signal. Single re-points (one end moved to a free start) are also net harmful on selection
(-157 TP / +264 FP).

## 4. Other findings worth a follow-up

- **a_linefit** (354 FN): linefit (weight 0.8, window 2) moves a node that was within 7 um of the GT to beyond 7 um.
  - Possible GT-free fix: cap the linefit displacement.
  - This is a tail knob, so it changes the replay base key (a new tail).
- **a_tail** (606 FN): only ~115 are ILP-attachable to a free end or start. A stitch placed before the short-track filter is worth little.
- **Break gap bridges**: 58 detection-side FN are 1-frame gaps (end at t, start at t+2). This is small.

## 5. Files and caveats

- **Code**
  - `tools/build_probe_kernel.py`: `--patch stitch` and `--patch swapfix` (both ENABLE=0 by default = exact no-op). The
    tail call order is always linefit -> edgefilter -> swapfix -> stitch -> divinsert, in any patch order (build-tested).
  - `replay.py`: keys `st.*` and `sw.*`; `write_geff` retries the Windows rename lock. Existing config fingerprints are unchanged.
- **Unverified**
  - No Kaggle kernel run (build test only).
  - The exact estimates hold the division term fixed; the replay shows divisions unchanged.
  - The L5 control rows for confirmation (same fingerprints) were reused, not recomputed.
