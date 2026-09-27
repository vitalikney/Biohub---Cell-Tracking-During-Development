# round20 scan_recheck notes (2026-09-27T20:02:17Z)
- 20:1xZ 27 Sep: no prior scan_recheck.json in round20 -> fresh run. Read round2-19 scan_recheck ids (no repeats allowed).
- KEY NEW FACT (CONTEXT 27 Sep 18:56Z): probe 45 exp70g (K2 + DIVINS_CAP 6; steal cap 2->3 follows) = 0.956, #268 -> #162.
  Lab said NO: research/wf_ideas_v4/reach0955/ins_cap6.json pooled -0.00057 (44b6 -0.00079, 6bba -0.00052), 85 extra insertions 0 TP/4 FP/81 unannotated.
  R15-RC-A (round15/scan_recheck.json) upheld the cap closure: 'upper bound <= +0.0009 public, central ~0'. FALSIFIED by +0.001..+0.003 true delta.
- Second lab-vs-public sign flip on a division knob: probe 41 exp70d DC 0.30 lab +0.0013 (6bba) -> public 0.949 (-0.005). Both flips same direction: lab undervalues forks.
- Controls: 43/44 DC 0.20/0.225 (more SAFE divisions, 96/88 dummy forks) = 0.954 tie -> extra safe-div forks do NOT pay publicly; extra INSERTION forks do.
- Dummy anatomy (_dl/biohub-exp*/run_stats.csv; clips 44b6_0113de3b / 44b6_0b24845f / 6bba_05b6850b / 6bba_05db0fb1):
  eligible @thr0.4 = 14/0/33/142; added cap4 (exp70b) 4/0/4/4 (steal 2/0/1/2); cap6 (exp70g) 6/0/6/6 (steal 2/0/1/2);
  cap8 (exp78a) 7/0/8/8 (steal 2/0/1/4; 44b6_0113 exhausted: skipped_used 6, cap_video 0); skipped_steal_cap = 0 everywhere.
  => cap 4->6 increment is 100% ORPHAN insertions; the steal-cap rise 2->3 never binds (no confound).
  exp70q (cap6 thr0.3): eligible 59/2/42/391 -> thr opens clips where cap does not bind (44b6_0b24845f 0 -> 2 added).
  divins_nodes_scored identical across caps/thr (3869/6988/661/20770) -> DaughterNet cost is cap/thr-independent.
- Ledger: probe 45 L in (7.49, 7.67] h, insertion gate 8.0 h did NOT fire (experiments/lb_poll/ledger.md row 56606948).
- Old verdict texts: research/wf_ideas_v3/v_metric-math_div-budget-ladder-x138_value.json ('|delta| <= 0.0015 public, LB cannot see');
  research/wf_ideas_v3/v_divisions_divins-x138-lab-retune_value.json ('precision falls with rank', 'LB cannot see it');
  research/wf_ideas_v2/r1_research_div-cap-private-j.json (cap4->6 0 TP/+2 FP on SELECTION; public embryo 'division-easier', J_pub 0.36);
  research/wf_ideas_v4/round15/scan_recheck.json R15-RC-A (upheld closure, 'upper bound <= +0.0009, central ~0').
  IDEAS I-067 curation 18: round 18 threw exp73s/c out (lab 0/4/81 + amanatar V6). V6 was mis-attributed (R19-RC-C); lab veto falsified by 45.
- exp60 lab (experiments/exp60_trainlab/results.md): ins35 44b6 +0.0058 (1 TP) / 6bba +0.0065; nosteal0 44b6 0.0000 / 6bba +0.0046 -> lab's 44b6 TP came from a steal.
  DC 0.20 lab 44b6 0 / 6bba -0.0008 vs public tie; DC 0.30 lab +0.0010 6bba vs public -0.005.
- DaughterNet v2 weights NOT local (weights_dataset/vitalii_daughternet has only v1 fold_0..4.pt); v2 SELECTION 'inside noise' (CONTEXT l.1321-1327).
- Finals E[max] algebra (x = private effect cap0->4, y = cap4->6): max(F1,#37)-max(F1,#38) = -y if x>0>y (x+y>0), x if x>0, x+y<0; x or x+y (<0) if x<0; 0 if x,y>0.
  #37 wins iff y<0<x; #38 wins iff x<0. P(x<0) 0.10-0.20 (R14-RC-C), P(y<0) ~0.35-0.5 (lab in-sample -0.0006 both embryos vs public +). At cap 6 a wash (~1e-4); as F1's cap rises |y| grows -> #37 dominates.
- 20:16Z: wrote scan_recheck.json (3 rechecks A/B/C + 1 new fact).
