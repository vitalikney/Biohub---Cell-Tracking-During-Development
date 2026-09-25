# schedule skeptic notes: log-shoulder-hypotheses (2026-09-25T11:13:39Z)
- started; no prior json. Read BRIEF.md.
- 2026-09-25 11:15Z read sibling verdicts: _value.json (refuted, central +0.0002 public), byte-lowscore-extension_schedule.json (H1: lab needs new x138-on-train harness 4-5 agent-h, lab on vitalii 26 Sep 00:05 or ~06:00Z, 54 videos ~5-6 GPU-h, P(scored) ~0.2-0.25 unconditional).
- Verified: predict_unet_transformer.py l.256-295 strict 3x3x3 local max of logits; x138 downsample (1,4,4) -> 1.625 um iso grid (cell 4 l.61); lowdet patch in cell 4 l.487 ('lowdet peaks' anchor = det_logits[f_idx][0] on GPU, sigmoid>0.3, dumped as low_coords/low_score int16 full-res); V1284 patch shares the same anchor (cell 4 l.502-509: x122 silent failure) -> a 3rd patch on that anchor is a known failure mode.
- Gap filler consumes low_coords (cell 5 l.1200-1204, score>=0.5): appending shoulder peaks INTO low_coords changes the control arm -> must be a separate npz key.
- r2_critic.notes.md l.16 (a_never GT->Ultrack 2.3 um, 25/63 clips), l.18 (repulsion +0.55..+1.0 um), fn_anatomy_exp39.md l.9 (a_never 1907 = 167 44b6 + 1740 6bba) all check out.
- Dummy clips = 44b6_0113de3b, 44b6_0b24845f, 6bba_05b6850b, 6bba_05db0fb1 (holdout_split.json) -> ~30 a_never GT expected (1740/128*2 + 167/71*2), too few for a 5% kill test but a coarse diagnostic.
- Container: no ~/.kaggle key, no torch (pip CPU wheel possible for synthetic tests).
- Toy 3D (scipy, 1.625 um grid, 180 configs of 2 anisotropic Gaussians sep 4.9-8.1 um in z): 60 configs have no raw peak within 3 um of nucleus 2; -LoG(sigma=1 vox) + 3.5 um exclusion rescues 12/60 (20%), 0 spurious. Mechanism implementable but modest; idealised.
- Verdict: refuted on schedule lens: P(scored LB probe containing it by 29 Sep 10:00) ~0.05 (gated) / ~0.25 (ungated rider), << 0.7.
