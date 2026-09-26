# v_hyp_successor R11S-8 notes (2026-09-26)
## 2026-09-26 17:17 UTC (date -u) - skeptic check of R11S-8
- No prior v_hyp_successor_r11s-8.json existed; fresh answer.
- Round-7 rejection text verified: research/wf_ideas_v4/round7/REPORT.md l.95 ("no successor base; new code after R8; unscored stack"). CONTEXT l.2144 P6 last sentence repeats it.
- Public insertion reads verified: #34 0.953 / #35 0.954 (CONTEXT l.1797, l.1801); #37 0.954 / #38 0.953. Lab +0.0058/+0.0065 (CONTEXT forecast 16:54 entry).
- Re-ran scratchpad/transplant_probe.py: amanatar old, amanatar v10, HF v3 -> changed cells [4,5], same_hunks True, same_new_cells True, next line after /divinsert = FINAL print. Objection (1) is mechanically answerable on proxies, but tools/build_probe_kernel.py has NO succ base yet (grep: only BASES l.105; no --base-ipynb). "Answered" = design, not code.
- R8 (CONTEXT l.1671; round-prompt HARD LINE; CONTEXT 16:49 entry) needs an honest LAB GATE + dummy + new OK, submittable by 27 Sep 12:00. SI on an unknown base cannot be submitted by R8 and has no lab gate; R11S-8 itself says (3) "still true", calling it "mitigated". A mitigation is not the gate R8 names -> admissible only as an explicit user amendment of R8/P6 naming a substitute gate ("transfer by construction, not measured on S"), as scan_plancheck PC11-03/PC11-12 say.
- Proxy dummy on HF v3 is a dummy of the tooling, not of the file to be submitted (the real SI dummy happens post-trigger, post-R8).
- Recipe conflict inside round 11: R11S-4/R11S-8 use K2 recipe (lowrefine on); PC11-07 argues K1 (LOWREFINE_ENABLE=0) because tools/dummy_gates.py --k2 hard-codes x138 constants (l.112 raw nodes == 121,777) and lowrefine private prior ~0. Unresolved.
- Missing clause: PC11-11(3)/PC11-12(b) "successor's diff must not touch division stages" (insertion transfer argument depends on it) is absent from R11S-8's mitigation list.
- Value: R11S-2's own MC: early port {port,#37} bronze 0.84 > SI 0.80 at s=0.954; SI wins only when detection is late or for silver (+0.1). x P(trigger) 0.10-0.15 -> incremental SI-over-port ~0 to +0.02 P(bronze), ~+0.01 P(silver). Priors, not measurements; 'second ticket' effect inflates.
- 17:25 UTC: final JSON written (refuted=true, partial).
