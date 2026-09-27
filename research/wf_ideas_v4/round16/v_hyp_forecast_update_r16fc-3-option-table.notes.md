# notes r16fc-3-option-table (2026-09-27T08:44:31Z)
- 08:44Z no cached JSON; read scan_hyp_forecast_update.json/.notes.md (model = judgmental 18-world MC, notes call it "illustration, not a decision input per I-092").
- CONTEXT l.2814-2871 R15-A1 (4) class-C table: default (a) recommended; reason qualitative ONLY; "only out-of-public evidence (6bba dc0.20 -0.0008) leans against transfer". D2 07:41Z: exp70b 0.954, pair unchanged.
- IDEAS.md I-092 refuted (MC world counts as finals input); round15 report.json 'rejected': R15FP-1 12-world counts rejected -> qualitative reason only. I-344 in-plan table. R15-A8(1): {V*,#38} dominated for high-variance knob (already known => (c) not recommended is not new).
- poll.log l.12833/12835 (08:45Z): 43/44 still PENDING -> pre-registration window still open.
- Independent check (scratchpad hedge.py, 400k draws; files #37=X+I, #38=X+eps (eps=0 -> tie loses), V=X+I+d; bronze margin t over X in 3 settings; I opt/pess; d lab N(-0.8,1.2)e-3 / harsh N(-3,1.5)e-3 / neutral N(0,2)e-3):
  b-a in [-0.042, +0.178]; lab d: -0.008..+0.050; harsh d: -0.042..+0.001; neutral: +0.033..+0.178. c << a everywhere under lab/harsh (-0.14..-0.57).
  => ordering (c) dominated and (b) >= (a) in most settings holds qualitatively; "never worse than (a) by > ~0.01" and "not worse than no change even if DC transfers adversely" do NOT hold (loss up to ~0.04; finding's own r16fc-4 bound 0.06).
- Verdict: refuted as written (repeats I-092/R15FP-1 world-count framing; overstated safety claim). Salvage: qualitative line with bounded loss.
- 2026-09-27T08:46:49Z final JSON written (refuted=true).
