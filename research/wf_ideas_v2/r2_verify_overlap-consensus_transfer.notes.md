# r2 verify overlap-consensus (transfer lens) notes
- started 2026-09-24; no prior json
- read r2_research notes + r2_critic notes + oc_sim.py. Hidden test ~100-130 videos (CONTEXT l.14); public ~29% => ~30-38 clips for the public embryo vs 71 in 44b6 train. Pair count ~N^2 -> if a 44b6-type public embryo has ~35 clips, multi-copy share roughly halves (22% -> ~11%) => ceiling ~+0.002 not +0.004 (assumption: same recording size / crop sampler).
- plan: stratify owner-chooser accuracy by border distance (border-driven vs phase/context-driven discordance) -> transfer robustness.
- MEASURED oc_xfer.py (scratchpad; exp39+ef 44b6 match files, 3 s): 202 non-owner copy instances on discordant GT edges, owner rule net +89 (fixed 144 / broken 55, acc 0.72) = reproduces oc_sim.
  by non-owner score: [0,3) n121 net +64 acc .77; [3,6) +11 .67; [6,10) +9 .62; [10,15) +5 .73; NO discordant case with non-owner score >=15.
  by score gap owner-nonowner: [0,1) -1 (acc .44), [1,3) 0 (.50), [3,6) +28 (.76), [6,12) +38 (.81), >=12 +24 (.74) -> gap<3 is a coin flip; rule gap>=3 & nonowner<8: net +78 acc .77 (n147).
  excluding leak group 0: net +22 (acc .70). limiting dim of failing copy: z +31, xy +20, t +38.
- MEASURED oc_xfer2/3.py: copies fail NEARLY INDEPENDENTLY in-sample: multi-copy edges discordant 9.1% vs all-copies-FN 1.1% (independence with p~5.5% would give 10.4% / 0.3%). => in-sample errors are mostly context/phase-driven noise (memorised interior), not input-determined.
  Border effect lives only in the first ~3 um/frames: single-copy FN z[0,3) 8.3% vs 4.7% interior; t[0,3) 6.8% vs 4.9%; xy[0,3) 4.7% (none); 3-15 um bins ~= baseline. Multi-copy: z[0,3) 10.4%, t[0,3) 10.5%, xy[0,3) 8.1% vs ~5%.
  => transfer: the chooser's real signal is the <3 um/<3 frame border truncation (architecture, should transfer). The claim 'test headroom probably larger' is unsupported: out of sample more errors are input-determined (both copies fail -> unfixable) and extra context-noise discordance is chooser coin-flip -> more splice volume, not more net gain.
- final JSON written (valid)
