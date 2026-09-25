# v_divisions_divins-x138-lab-retune_value notes
- 2026-09-25T10:51:31Z start; output json did not exist; read BRIEF + h_divisions.notes
- read CONTEXT.md 00:15/00:40/02:00/02:10/03:10 (24 Sep), 11:20 (probe 28 0.948), 25 Sep 08:15/08:40/10:20: numbers cited by the idea check out (lab CONF +0.0019 CI[-0.0007,+0.0050]; LB +0.001; 12 x138 insertions/4 dummy clips, 5 steals, 0 on 44b6_0b24845f; readmit 1,337; J/(1+J)=0.265).
- read wf_ideas_v2/r1_research_div-cap-private-j.json + r1_verify_div-cap-private-j_transfer.json: cap4->6 marginal 0 TP/+2 FP on SELECTION; only ~3% of insertions evaluable (15 of 466 on CONF); DaughterNet OOF folds are within-embryo (not embryo-held-out); 44b6 CONF gain = 1 TP on 1 video.
- r1_hyp_divisions.json: 13->23 missing-second-daughter is on exp39 tails (not x138); ckpt slot touches <= 10/151 GT divs (6.6%).
- own python (metric arithmetic, J_pub 0.36, D~50 GUESS): +0.002 public over #35 needs out-of-sample precision +0.15 (0.27->0.42) on ~5 evaluable public insertions; 0.27->0.35 gives +0.0011. ckpt slot (2.6-3.3 reachable public divs): +0.000..+0.0017 even at precision 0.5 and recall 0.4 among reachable.
- lab resolution: SE of a CONF delta ~0.0017 (from CI [-0.0007,+0.0050]); P(gate +0.001 passes | true 0) = 0.28; 144-config grid on SELECTION -> winner's curse (v1 orphan +0.0044 -> +0.0010; steal +0.0058 -> +0.0019).
- LB: difference of two probes has sd ~0.003 -> a +0.001 change is invisible; lab->LB transfer ~0.5x.
- verdict: REFUTED under value/transfer lens (realistic public +0.000..+0.001 < +0.002 bar). No web research needed (all numbers internal).
