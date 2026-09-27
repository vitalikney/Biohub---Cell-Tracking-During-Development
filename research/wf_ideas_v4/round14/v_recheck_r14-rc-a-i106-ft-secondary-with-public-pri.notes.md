# v_recheck R14-RC-A (I-106 FT secondary + public primary vs exp72 '0/5' prior) - skeptic notes
2026-09-27T01:59Z start. No prior JSON existed -> fresh run. Desk-only; no Kaggle calls.
- CONTEXT l.175 A26, l.296-318 (11 Sep re-exam (c)) confirmed verbatim: 'exp23 as secondary with the PILKWANG primary is untested'.
- CONTEXT l.2472 (21:21Z entry (3)): '0/5' is in the CAVEATS line of the retrain decision, not literally in the Q1 text.
  Q1 text (CONTEXT R13-A3 01:31Z, ~l.2730): 'push exp71 (~4.5 GPU-h; ~22 h quota left)?' - no '0/5' inside.
- 02:05Z RESULTS.md l.37-47 checked: probes 7 (exp22, exp08 sec) and 10 (exp27, friendA ep21 sec) on exp06 base (public 0.941 + exp03B primary);
  probe 13 exp32 = exp30 (sjlee stack + exp03B primary) + exp23 sec. So '3/3 secondary swaps on an exp03B primary' = TRUE.
- BUT the primary swaps are not irrelevant: probe 15 exp33 (ONE change vs exp29: primary := exp03B, public seed314159 secondary kept) -0.003;
  probe 17 exp35 (ONE change: soup 0.5 pilkwang + 0.5 exp03B) -0.004; probe 11 exp30 -0.003 (confounded w/ tight55). These are our FT
  weights paired with a PUBLIC counterpart model = the 'diverse' pairing the finding says is untested, with roles swapped. 0/3.
- R13-RC-A (round13/scan_recheck.json): soup scored BELOW exp33 despite fewer nodes -> node story fails for primary swaps too; so the
  primary-swap losses are also not pure node-count, i.e. they are evidence that our FT weights lose on the hidden embryo on the public stack.
- 'correlated errors' (CONTEXT l.316-318) was a hypothesis written 11 Sep, never tested. Friend B port (RESULTS l.101): exp32 vs exp30
  ALL 12 LOEO-44b6 0.8760 vs 0.8867 (-0.011), CLEAN6 0.8723 vs 0.8927 (-0.020), while exp30 > exp29 on CLEAN6 (0.8927 vs 0.8843):
  consistent with the correlation story AND with 'exp23 secondary itself worse' - does not separate them. exp29+exp23 never run in the port.
- exp23 recipe (RESULTS l.75): 1200 it, batch 8, lr 5e-5, bce, all layers; exp72/exp71 recipe (r_retrain RT-1): distilled, lr 1e-5,
  last decoder block + heads, BN frozen, 1 epoch. Genuinely different -> shrinks both harm and gain toward 0.
- Q1 text itself (R13-A3) does not contain '0/5'; it sits in the 21:21Z caveats and v_retrain no_go_items. Numbers (v_retrain P(<0.954)
  25-30%, E ~0) do not move. exp72 = class C unless Q3; finals untouched -> private value 0.
- VERDICT 02:10Z: count correction right; headline 'rests on ONE confounded precedent' and replacement text ('the other 0/5 items are
  primary swaps or weaker models') overcorrect by dropping 2 clean one-change FT-primary negatives. refuted=true; fix = balanced text.
- 02:12Z JSON written: v_recheck_r14-rc-a-i106-ft-secondary-with-public-pri.json (refuted=true, balanced-text fix).
