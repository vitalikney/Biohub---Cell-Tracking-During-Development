# v_hyp_finals_r26f-2 notes (skeptic, VALUE + FEASIBILITY)
- 2026-09-28 ~16:40 local: no prior v_hyp_finals_r26f-2.json -> fresh.
- Source finding: round26/scan_hyp_finals.json R26F-2 (same agent that built mc26). Model: scratchpad r26/mc26.py (imports r21/mc20.py). exp75 modelled as b + CI, #37 as b; common random numbers per world -> pair differences not seed noise.
- CONTEXT 11:17Z R25-A1 (5): exp75 >= 0.955 -> B on card as trade; <= 0.954/NO-OP/ERROR -> B drops; <= 0.953/ERROR -> CI-risk flag. Origin: 10:16Z session answer to the user ('exp75 >= 0.955 -> {best public, exp75}; <= 0.954 -> keep #37').
- #37 public = 0.954 (CONTEXT l.2074, 3618). So exp75 0.954 = CI display step 0 on the cap-4 base (unrounded delta in (-0.001,+0.001)); prior from probe 48 (exp79a vs exp70g) +0.001 UP 33.
- Re-ran mc26 with other seeds (PARTNERS '#37,exp75', VPUB exp85a):
  CI 0/.0008: seed 23 A .740 B .767; seed 5 A .739 B .761 (seed 11 in grid2: .747/.771) -> B>A robust at mean 0 (+.02-.03 bronze, +.03 silver).
  CI -0.0003/.0008: seed 23 A .740 B .736; seed 5 A .739 B .729 -> A ahead. Crossover with sd .0008 is ~-0.0002, not -0.0004 (that was the sd .001-.0015 runs). So the relaxed floor holds only if the private CI mean is >= ~-0.0002.
- Gap: the amendment ignores the other CI reads that arrive before the card: probe 51 exp87a vs exp85a (~21:30-22:15Z today) and night exp89r vs exp89q (if exp89r is used). The V_pub-non-CI branch is exactly the one where exp87a did NOT read '+', i.e. a '0' or '-' CI read on the K base. A '-' there plus exp75 at 0.954 pulls the CI posterior to ~0 or below -> near/below crossover.
- 'clean' needs to be explicit: COMPLETE, not ERROR, CI-RAN (dL > 0.5 h vs 7.54 h), L_hi <= 10.2 h, no 'ins-tail?' footnote (L_hi in (9.6,10.2]) since a skipped insertion on private tail videos is invisible at a 0.954 display.
- Feasibility: 0 GPU, card text only, pre-score before 00:06Z submit of exp75 (reads ~09:00-09:40Z) -> honest; user still picks finals; the 10:16Z rule was told to the user, so the change must be told too. No R1-R10 conflict found; not a closed line.
- Value: bounded downside (B vs A differ only by CI on the partner); gain = mean-preserving-spread option on a partner below the medal line; model-conditional (+.02-.03 bronze in the branch V_pub non-CI AND exp75 = 0.954 exactly).
