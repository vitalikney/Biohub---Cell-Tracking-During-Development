# scan_hyp_division_pp notes (round 13, started 2026-09-26T22:46Z)
- 22:47Z (date -u 22:46:59Z 26 Sep): output json absent -> fresh run. Read CONTEXT tail (l.2250-2570), reach0955/r_ladder.json, plan.notes.md, ins_cap6.notes.md, experiments/exp60_trainlab/results.md, IDEAS DIV section (I-047..I-085, I-212..I-321).
- Existing exp60 lab division-knob numbers (vs x138 control; score = adj edge J + 0.1 div J): forkmid45 44b6 0.0000 / 6bba +0.0002; ins35_forkmid45 vs ins35 44b6 0 / 6bba +0.0003; dc0.15 -0.0005/-0.0017; dc0.20 0.0000/-0.0008; dc0.30 -0.0006/+0.0010; dc0.35 -0.0074/-0.0036; ins cap5 0/-0.00019, cap6 -0.00079/-0.00052, cap8 -0.00079/+0.00018 (vs ins35). NONE positive on both embryos (lp30 +0.0008 both, but not a division knob).
- Safe-division knobs in x138 cell 0 (env, only cell-0 assignment -> --set works): SAFE_DIV_MAX_UM 9.0, SISTER_MAX_UM 14.0, SISTER_SYMMETRY_TAU 0.6, DIVERGE_UM 2.25, EXISTING_CHILD_MAX_UM 10.0, FRAME_FRAC_CAP 0.0076, GLOBAL_FRAC_CAP 0.00375, REQUIRE_MUTUAL_NN 1, REQUIRE_DIVERGENCE 1, OUTPUT_KEEP_DIVISION_COMPONENTS 1, DC veto 1 thr 0.25. Never swept on the x138 exp60 bed (I-051 sweep was the old sim_safediv base, 11 Sep).
- Plan: scratch CPU sweep (tools/ untouched) replaying the presafe dumps (_dl/exp60_a, _dl/exp60_b) with one knob changed, scored on control bed AND with ins35 applied on top (K2-like bed).
- 23:15Z sweep running (8 workers, started 22:52Z; CPU shared with two other agents' 6-worker jobs). Script scratchpad/divpp/sweep.py: 20 arms (ctl_replay parity, tau 0.4/0.5/0.7, sister 12/16, parent 8/10, child 9/11, diverge 1.75/2.75, gcap 0.0025/0.005, fcap 0.005/0.01, no mutual-NN, no keep-div-components, dc0.30, safe-div off), each scored on control bed and +ins35 bed. Smoke 6bba_55b7eebe parity True.
- 23:39Z SWEEP 1 DONE (scratchpad/divpp/sweep_raw.json, agg sweep_agg.json). Parity: ctl_replay writer digest == kernel final on 56/56 clips; dc0.30 ctl-bed reproduces results.md (44b6 -0.00058, 6bba +0.00099). Deltas (score = adj edge J + 0.1 div J), ctl bed | ins35 bed (~K2 without lowrefine):
  tau0.7  ALL +0.00268 (44b6 -0.000003, 6bba +0.00310; 6bba SEL +0.00323 CONF +0.00298) div 16/25/83 -> 20/29/79; forks +100, nodes +46; W/L 4/11 | ins ALL +0.00237 (44b6 -0.000003, 6bba +0.00271) div 25/31/74 -> 29/35/70
    marginal forks: +4 TP (6bba_3c5691b6, 48816121, 9a41d029, f8ffd5e7) / +4 FP (3fda6b25, 74686d6a, 7d3058ae, ab78413d) / ~92 unannotated. Evaluable precision 4/8 = 0.50; one-sided Wilson80 lower ~0.29 (> public break-even 0.265).
  tau0.5  ALL +0.00053 (44b6 +0.00059, 6bba +0.00038; 6bba SEL +0.0028 CONF -0.0019 -> halves disagree) div FP 25->21 (TP 1 in/1 out) | ins +0.00071 (44b6 +0.00121, 6bba +0.00049)
  tau0.4  -0.00243 (44b6 +0.00133, 6bba -0.00323); div 12/15/87 (loses 4 TP)
  div2.75 +0.00050 (44b6 0.000002, 6bba +0.00064, both halves +; FP -4 no TP lost; W/L 12/0) | ins +0.00068
  par10 +0.00080 (single clip 6bba_5c039895 +1 TP; W/L 1/12) | par8 +0.00013 | fcap0.005 +0.00039 (SEL only, 3 clips) | fcap0.01 -0.00013
  sis12 -0.00071 | sis16 -0.00002 | ch9/ch11/gcap*/nokeepdiv exactly 0 (not binding) | nomnn -0.00055 | div1.75 -0.00167 | safediv_off -0.01328
  dc0.30 ins bed: ALL +0.00128, 44b6 +0.00004 (was -0.00058 without insertion), 6bba +0.00131 -> the exp70d/probe-41 interaction with the insertion is NOT adverse in the lab (in-sample DaughterNet p).
- 44b6 lacks power for any fork-ADD knob: 17 clips, 11 GT divisions; tau0.7 changes 0 evaluable 44b6 forks.
- Old closure I-051 (11 Sep, sim_safediv on 12 exp23 videos, 14 GT div, old pipeline, no DC veto): tau 0.6 best, tau 1.0 +0 TP / +3 FP. Different base; this is the first tau read on the x138 exp60 bed (99 GT div).
- 23:45Z sweep 2 launched: tau 0.65/0.75/0.8/0.9/1.0 plateau + tau0.7+dc0.30 + tau0.7+div2.75 (arms2.json).
- 23:55Z DRY BUILDS (builder imported with ROOT -> scratchpad/divpp/build; nothing under experiments/): K2 rebuild exp58_x138_safe_lowref sha 1f1ddb6d63b47f54 (== repo), exp70d rebuild e0b8fc0cf87660c3 (== repo). New: exp70i_k2_tau07 sha 1120fdfd412a3f0f (diff vs K2 = cell-0 name line + one line os.environ["BIOHUB_SAFE_DIV_SISTER_SYMMETRY_TAU"] = "0.7" appended after x138's own "0.6"; read in cell 2 via os.environ.get; not in the cell-1 drift guard; not re-set in cells 3/4; cell 11 only lists it in the dormant validator PP_SWEEP_KEYS). exp70j_k2_div275 sha aab35c8a2d5c3ee0.
- x138 cell 11 prints 'Post-process base configuration (public 0.939)': the safe-div PP constants date from the 0.939-era base and were never re-tuned for x138 in the notebook (validator off). x138's own dormant sweeper covers exactly these keys -> a plausible (unverified) route for Justin CH123's PP-only 0.953 -> 0.956 over 70 subs.
- 23:56Z SWEEP 2 DONE (sweep2_raw.json). TAU PLATEAU, ctl bed | ins35 bed (ALL; 44b6; 6bba SEL/CONF):
  tau0.65 +0.00107 (44b6 -0.000003; 6bba +0.00129/+0.00115) | +0.00083
  tau0.70 +0.00268 (44b6 -0.000003; 6bba +0.00323/+0.00298) | +0.00237
  tau0.75 +0.00429 (44b6 -0.000003; 6bba +0.00516/+0.00482) div 16/25/83 -> 22/29/77 | +0.00376 (44b6 -0.000003) div 25/31/74 -> 31/36/68
  tau0.80 +0.00413 (44b6 -0.000004; 6bba +0.00479/+0.00481) | +0.00357
  tau0.90 +0.00597 (44b6 +0.00003; 6bba +0.00615/+0.00795) | +0.00445 (44b6 -0.00023: first 44b6 FP fork e35b117d)
  tau1.00 +0.00528 (44b6 +0.00010; 6bba +0.00540/+0.00716) | +0.00362 (44b6 -0.00040)
  tau0.7+dc0.30 +0.00304 (44b6 -0.00058) | +0.00314 (44b6 +0.00003); tau0.7+div2.75 +0.00356 | +0.00350
  Evaluable marginal forks vs tau 0.6: 0.65 +2TP/+4FP; 0.7 +4/+4; 0.75 +6/+4; 0.8 +6/+5; 0.9 +9/+8 (1 FP removed); 1.0 +9/+13.
  tau0.75 checks: dc_miss 0 (DC is evaluated BEFORE the symmetry test, so every lookup is a recorded kernel score -> replay exact); global/frame caps never bind (skipped_cap 0); safe forks 676 -> 837; nodes +83; clip bootstrap 90% [+0.00157, +0.00752], P(<0) 0.004; leave-one-clip-out min +0.0035; 6bba both halves ~+0.005; 44b6 exactly neutral (no evaluable change) on both beds.
- 00:05Z sweep 3 launched: exp64 44b6 lab dumps (_dl/exp64_a|b, 71 clips, x138 + lowrefine + insertion dump; notebook experiments/exp64_overlap_lab/kernel_a) arms tau0.7/0.75/0.8/0.9, dc0.30, tau0.75+dc0.30. Smoke 44b6_0c582fdc parity True (forks 22 -> 31 at tau0.75).
- 00:20Z SWEEP 3 DONE (sweep3_raw.json; exp64 44b6 bed = x138 + lowrefine + safetail, insertion dump; 71 clips, parity 71/71, dc_miss 0; 17 overlap exp60, 54 new). REVERSAL for tau:
  tau0.75: ALL71 ctl -0.00086 / ins -0.00122 (div 4/19/22 -> 4/23/22: 0 TP, +4 FP, +289 forks); NEW54 -0.00169 / -0.00221; leak-group (18 units) bootstrap 90% ctl [-0.00136, -0.00017] P(<0) 0.99; ins [-0.00205, -0.00035].
  tau0.7 -0.00051/-0.00070; tau0.8 -0.00106/-0.00151; tau0.9 -0.00165/-0.00232 (monotone harm on 44b6).
  dc0.30: ALL71 ctl +0.00225 / ins +0.00336 (FP 19 -> 10, 0 TP lost, forks -428); NEW54 +0.00451 / +0.00593; unit bootstrap 90% ctl [+0.00033, +0.00355] P<0 0.01; ins [+0.00062, +0.0053] P<0 0.00. (exp60 44b6-17 was -0.00058 ctl / +0.00004 ins.) Caveat: 44b6 = DeepCenter's TRAINING embryo; leak group 0 holds 5 of the 9 removed FP forks (overlapping crops; handled by the unit bootstrap).
  tau0.75+dc0.30: ALL71 +0.00131 / +0.00199 (unit boot P<0 0.14/0.13).
  => tau is embryo-specific (6bba +0.005, 44b6 -0.001..-0.002): FAILS the both-embryo test. dc0.30 (probe 41 exp70d, already submitted) is now lab-positive on BOTH embryos on the K2-like insertion bed (6bba +0.00131 on 39 clips; 44b6 +0.00336 on 71 clips).
- 6bba exp60 stems are in no multi-clip leak group (no overlapping 6bba crops) -> 6bba clip bootstrap is valid.
- 00:22Z sweep 4 launched on exp64 44b6: div2.75, par8, fcap0.005, tau0.5, dc0.30+div2.75.
- 00:42Z SWEEPS 4/5 DONE. exp64 44b6-71 (ctl | ins; leak-group unit bootstrap 90%):
  div2.75 +0.00050 | +0.00071 (FP 19 -> 17, 0 TP lost; boot [0, +0.0021] | [0, +0.0031]); par8 0 | 0; fcap0.005 +0.00004 | +0.00004; tau0.5 -0.00098 | -0.00030 (loses 1 TP); dc0.30+div2.75 +0.00261 | +0.00388 (FP 19 -> 9; boot ins [+0.0012, +0.0061]).
  exp60 (sweep5): dc0.30+div2.75 44b6-17 -0.00058 | +0.00004; 6bba +0.00152 | +0.00201 (FP 17 -> 8 ctl / 23 -> 14 ins, 0 TP lost; boot ins [+0.0008, +0.0033]). tau0.75+dc0.30 6bba +0.00545 | +0.00512, 44b6-17 -0.00058 | +0.00003.
  => div2.75 is >= 0 on BOTH embryos on BOTH beds (6bba +0.00064/+0.00085, 44b6-17 0/0, 44b6-71 +0.00050/+0.00071), removes only FP forks (6 evaluable FP, 0 TP), no DC miss. Near-additive with dc0.30.
  Independent cross-check: round-13 scan_recheck (r13rc/k2bed_arms.py) measured dc030+ins on exp64 = +0.00336 too (identical number, different script).
- 00:43Z sweeps 6/7 launched (divergence plateau 2.5/3.0/3.5 on exp60 and exp64).
- 01:01Z SWEEPS 6/7 DONE (divergence plateau; ctl | ins):
  exp60: div2.5 44b6 0 | 0; 6bba +0.00064 | +0.00085 (SEL +0.00084, CONF +0.00037; FP 17 -> 13, 0 TP); div3.0 6bba -0.00139 | -0.00107 (loses 2 TP; CONF -0.0035); div3.5 6bba -0.00081, 44b6-17 +0.00057.
  exp64 44b6-71: div2.5 0 | 0 (forks -125, none evaluable); div3.0 -0.00182 | -0.00161 (loses 1 TP); div3.5 -0.00093 | -0.00025.
  => divergence response: 2.25 (x138) 0 -> 2.5 / 2.75 plateau (+0.0006..+0.0009 lab, FP-only) -> CLIFF at 3.0 (TP loss on BOTH embryos). 2.75 sits 0.25 um below the cliff; 2.5 is 0.5 um below and gives the same 6bba gain but 0 on 44b6.
- 01:02Z sweeps 8/9 launched: dc0.30 + div2.5 on exp60 and exp64.
- 01:12Z SWEEPS 8/9 DONE: dc0.30+div2.5 exp60 ctl +0.00132 (44b6 -0.00058, 6bba +0.00152) | ins +0.00184 (44b6 +0.00004, 6bba +0.00200; FP 23 -> 14, 0 TP); exp64 44b6-71 +0.00225 | +0.00336 (== dc0.30 alone; div2.5 inert on 44b6).
- Dry builds (scratchpad/divpp/build/experiments, builder ROOT monkeypatched; K2 rebuild 1f1ddb6d == repo): exp70n_k2_div250 d1379b7d5eb1bd59...; exp70o_k2_dc030_div250 29d62e6414fb69ba...; exp70j_k2_div275 aab35c8a2d5c3ee0...; exp70m_k2_dc030_div275 dc5d535e9f6b6918...; exp70k_k2_tau075 33ec2ee49f4c85f0... (NOT recommended); exp70l_k2_dc030_tau075 7534a871b772d7d7... (NOT recommended). Each diff vs K2 = cell-0 name line + the override line(s) only; all private, internet off, 5 datasets, kernel_sources [].
- 01:15Z writing scan_hyp_division_pp.json.
- 01:13Z final JSON written (6 findings).
