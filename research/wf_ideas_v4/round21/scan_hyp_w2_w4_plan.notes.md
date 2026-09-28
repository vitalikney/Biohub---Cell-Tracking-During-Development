# round21 scan_hyp_w2_w4_plan notes
- 2026-09-27T22:30Z started; no prior json.
- 22:40Z scratch ROOT build check (scratchpad/r21root = copy of tools/ + exp56/exp39 bases; repo untouched):
  exp79a 5f9b265d, exp78a 8d8d9c28, exp78b d54d810c, exp80a da984964, exp81 6a62e321 reproduce byte-identically (nb + metadata)
  with B="--base x138 --patch divinsert --patch safetail --patch lowrefine", KB (no CAP) + C<cap> after LOWREFINE, CI, N2 vars.
  exp70g does NOT reproduce with this order (762c16.. vs repo 52c182..): older K-with-CAP=4-then-override order; irrelevant (scored).
- New combo shas (scratch only, not written to repo): exp82a cap8+n2a ffc00631; exp82b cap12fc2+n2a 7cd1e3ed; exp82c cap24fc2+n2a ee431244;
  exp83a cap12fc2+CI 80a0856f; exp83b cap8+CI d9b0834d; exp83c cap6+n2a+CI e8f5a8a6; exp83d cap12fc2+n2a+CI 22ccc1dd;
  exp83e cap8+n2a+CI a016cf0f; exp83f cap24fc2+CI c8a2fccb. exp83a vs exp79a diff = only DIVINS_CAP/FRAME_CAP lines + header comment.
- PLAN ISSUE: tools/runtime_ledger.py EXP_RULES maps exp8\d[a-z]* -> safetail; CI stacks named exp83* would be mis-familied.
  Need (r"exp83[a-z]*", "safetail_ci") BEFORE the exp8\d rule (+ test), or name CI stacks exp79[b-z]... (exp79a rule is exact 'exp79a').
- 22:45Z more scratch builds: exp83g cap24fc2+n2a+CI 00f8cb36; exp84a K2+cap48+fc2 4cb1e47b. Diffs: exp83c = exp79a + secswap only (cell0 env + cell3 sha line);
  exp83c = exp81 + coordinject cell (cell0 +2 env lines, one inserted cell). All new metadata: T4, internet off, ft-weights kept, n2a/coord-inject sources.
- State at 22:30Z (experiments/e10_watch/20260927T2230Z.txt): 3,959 teams; ours #165, 0.956, 9th of 52 in the 0.956 block (ranks 157-208) ->
  holder exp70g unrounded ~0.9565 - 8.5/52e-3 ~ 0.95634 under uniform in-block density (round-18 method); >=0.955 294, 0.954 120, >=0.960 89.
  kaggle kernels status: exp81 (cap6+n2a) dummy COMPLETE, exp80a (cap24 fc2) dummy COMPLETE (gates not yet logged in CONTEXT at 22:30Z).
- MC (scratchpad r21/mc21.py = r20 mc.py + C12 (cap12fc2 marginal: 2.3x cap6 volume, q-0.08, steal edge N(-5e-5,1e-4)), CI N(+2e-4,1e-3), SEC N(-1e-4,1.2e-3)):
  base seed11 P(bronze)/P(silver): A{#37,#38} .51/.11; P1{exp70g,#37} .67/.38; P8{exp78b,#37} .69/.42; P9{cap12+CI,#37} .70/.44; P10{cap12+CI,exp78b} .50/.41;
  P11{cap12+SEC+CI,#37} .69/.44; P12{..,exp78b} .52/.43; P13{cap6+CI,#37} .70/.42; P14{cap6+CI,exp70g} .61/.43. seed7 within +-0.01.
  qpub0 (lab-like private): A .51/.11, P1 .59/.25, P8 .57/.21, P9 .58/.23, P10 .24/.16, P13 .63/.29. qpub_hi: P8 .75/.54, P9 .76/.55.
  overfit field: A .67/.23, P9 .79/.53; central: A .34/.03, P9 .60/.38; inspes: A .41/.09, P9 .63/.41. CI&SEC mean -5e-4: P9 .67/.40, P11 .66/.37 (vs P1 .67/.38).
  => partner choice dominates (#37 vs own parent: -0.17..-0.34 bronze); F1 choice among cap-family stacks moves P by <= ~0.04.
- 22:48Z final JSON written: research/wf_ideas_v4/round21/scan_hyp_w2_w4_plan.json (10 findings r21w-1..10)
