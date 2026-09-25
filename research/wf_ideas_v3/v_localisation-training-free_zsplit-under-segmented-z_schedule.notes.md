# zsplit schedule skeptic notes
- 2026-09-25 ~11:xx UTC: started. Read BRIEF.md, sibling dogrescue schedule verdict (refuted, P(scored)~0.09) and zsplit value verdict (refuted).
- tools/dog_rescue.py does NOT exist (ls). The idea's 1.5 h estimate assumes dogrescue infra (track assembly, insertion, cap) exists; standalone it needs +2-3 h agent.
- build_probe_kernel.py --base x138 supports only divinsert|leafprune (docstring l.13-14) -> new patch needed in x138 cell 5.
- x138 cell 5 already has a full-res frame reader with cache (blosc2 chunk, fallback zarr; cell 5 ~l.120-140, used by refine_synthetic_midpoint) -> in-kernel z-profile is implementable, cheap per node; frame reads ~0.05 s/frame -> ~0.2-0.4 h serial over 10-13k hidden frames if frames not already cached; repair loop is serial, deadline guard REPAIR_DEADLINE_S=27000 checked per dataset at cell 5 l.2116 -> stage must be deadline-gated.
- Evidence check: hole valley 4-5 um <0.85 1.2% / <0.95 4.7% (n=169), 5-6 um 0%/5.3% (n=132) confirmed (wf_ideas_v2/r1_research_hole-fill-sandwich.notes.md). attract3 +0.55..+1.0 um confirmed but on pairs both matched to distinct preds (r2_critic l.18) -> not a merge signature. ::4 stride confirmed (polyphase notes l.11).
- Sibling verdicts: dogrescue schedule refuted P(scored)~0.09; zsplit value refuted (+0.0001 central public).
- Container: no data, no Kaggle; last commits 25 Sep 11:11 UTC (no friend A commits since 24 Sep).
- VERDICT: refuted on schedule; P(scored with honest gate) ~0.05-0.08; blind rider schedulable (~0.75) but below LB noise.
- 2026-09-25T11:14Z final JSON written.
