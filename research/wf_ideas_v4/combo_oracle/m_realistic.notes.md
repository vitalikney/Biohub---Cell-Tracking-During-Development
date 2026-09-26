# m_realistic notes (2026-09-26T18:10:56Z)
- start: m_realistic.json absent -> fresh run. Read r11_graph_arms.py (orph_mirror/orph_near/oracle_fp), exp60 results.md, antipar_lab.py (ANTIPAR rule), tools/trainlab.forkmid/insert35/official_eval, official metric (edges valid only if an endpoint matches a GT node with edges; non-consecutive edges dropped; outdeg cap 2).
- plan: scratchpad/combo/combo_arms.py. Base = ins35 on exp60 final graphs (56 clips). Pre-declared grids (<=3 per knob):
  F1 forkmid thr {3.5,4.5,5.5} um (safe non-inserted forks, tool rule); F2 ANTIPAR cos {0.0,0.25,0.5}; F3 any-2-child-fork midpoint thr {4.5,6.0,7.5} um (drop flagged/inserted edge else lower edge_prob).
  O mirror orphan attach: sister [5,14] um, dist<=12 um, residual {1.0,1.5,3.0} um, greedy by residual.
  L dangling end u(t) -> free start v(t+1), flow-compensated (median displacement of edges from nodes within 20 um, >=3), radius {3,5,8} um, greedy by distance, one-to-one.
  Combination order F -> L -> O. Oracles: F (drop child edge of every FP fork), L (end->start pairs <=12um that are GT edges), O (1-child parent->start <=12um that are GT edges), and F+L+O oracle together.
- 21:3xZ: scripts moved to scratchpad/combo/m_realistic/ (a sibling agent writes combo_oracle.py/combo_out.json in combo/). 1-clip test (44b6_18ced818, 61 s): GT sparse (90 TP edges/clip), most edits IGN (unannotated).
- finding before scoring: the t+1 end->free-start pool is EMPTY below ~8 um (pool pairs <=12 um: 102 and 52 on two clips, min 9.8 / 7.9 um, median ~11 um; ILP already links everything closer). L_flow R{3,5,8} add ~0. Added (declared before any score) G = gap closing end(t)->free start(t+2), 2x flow, R {5,8} um, with an interpolated node at t+1 (+1 node per link).
- full singles run: COMBO_WORKERS=5 python combo_arms.py singles singles.json (log singles.log).
- 21:5xZ SINGLES DONE (singles.json, singles_agg.json; base reproduces ALL 0.93988, div 25/31/74). Pooled deltas vs ins35:
  F forkmid 3.5/4.5/5.5: -0.00187 / +0.00017 / 0 (removed forks TP/FP/ign 3/3/105, 0/1/39, 0/0/11)
  F antipar 0.0/0.25/0.5: -0.00077 / -0.00012 / -0.00063 (TP/FP removed 2/5, 1/4, 1/1)
  F anymid 4.5/6.0/7.5: -0.00366 / 0 / 0 (4.5 removes 5 TP, 2 FP forks)
  O mirror res 1.0/1.5/3.0: +0.00020 / -0.00054 / -0.01285 (new forks TP/FP 1/4, 2/13, 7/200)
  L flow R 3/5/8: 0 / 0 / +0.00002 (0, 0, 8 edges; 1 TP 0 FP 7 ign)
  G gap R 5/8: -0.000002 / -0.00005 (48/238 edges, 0 TP; +1 node each link hurts adj)
  oracle_F +0.00629; oracle_L (end->free start t+1 GT edges) +0.00014 (6 edges); oracle_O as pure GT-edge add +0.00174 (creates 138 FP forks: wrong kind of oracle); oracle F+L+O(edge) +0.00390.
- pass 2 launched: combos.json (8 realistic combos + oracle Ostrict/Odiv and F+L+O joint oracles) -> combos_out.json
- 22:2xZ COMBOS DONE (combos_out.json/_agg.json, boot_out.json). Best realistic combo F forkmid4.5 -> L R8 -> O res1.0: +0.00039 (44b6 0, 6bba +0.00041, W/L 3/2, boot90 [-0.00076,+0.00197]; 6bba_debd7bfa +0.028 carries it). Pre-declared middle (fm4.5, R5, res1.5): -0.00038 (44b6 -0.0025, W/L 5/9). Pairs F+O +0.00037, F+L +0.00020, L+O +0.00022; ANTIPAR variants +0.00012; +gap closing +0.00034 (W/L 3/29).
- joint oracles: F+L+Odiv (round-11 definitions) +0.01353 (super-additive vs 0.0118); F+L+Ostrict (perfect wide-pool filter, 20 TP forks) +0.02711. Sibling m_joint_oracle.json: +0.0206 with relink swaps. Realistic best captures 2.9% / 1.4% / 1.9% of them.
- answer written: research/wf_ideas_v4/combo_oracle/m_realistic.json (finalize.py)
