# v_hypotheses R8H-10 skeptic notes (2026-09-26, UTC)
- Checked: no earlier v_hypotheses_r8h-10.json existed.
- research/wf_ideas_v2/r2_research_overlap-consensus.json: option (e) position averaging "optional: v2, on AGREE nodes only (max +0.0005)"; median GT distance 1.34 -> 1.24 um; splice v1 skips any component with a fork.
- CONTEXT.md l.1499/1529: float output closed (invisible on LB, server rounds / gain < 0.0005) -> rounded int coords, so averaging sub-voxel gains mostly vanish.
- experiments/exp60_trainlab/results.md control 44b6/ALL (17 clips): div TP/FP/FN = 1/8/10 -> 11 GT divisions (the finding's "10 GT divisions" is the FN count; nit). ins35 (DaughterNet insertion) already takes 44b6 to 2/8/9.
- CONTEXT 08:58 UTC G-B pre-registered clause: "forks untouched" -> importing divisions would break a pre-registered gate = post-hoc change.
- .claude/worktrees/wf_b39793f6-e79-4/experiments/exp65_overlap_probe/ga_report.json: G-A found 43/62 GT links (splits.json holds 62, not 65) at GT offset, 0 wrong, 16 missing below the pre-registered floor (spatial <5% / frames <5), 3 reachable missed; 0 6bba, 0 cross; gate_verdict G_A_pass = False (found_ge_60 False). By the 08:58 text "FAIL -> stop". Splicing below-floor pairs = lowering the floor after the result -> post-hoc rescue of a failed gate.
- Verdict: finding stands (not refuted). Add: G-A failed as pre-registered, so the whole overlap splice line stops unless the user decides otherwise; division import is post-deadline regardless.
