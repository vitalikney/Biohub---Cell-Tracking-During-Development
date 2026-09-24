# transfer verify notes (oof-edge-scorer-full-candidates)
- started; no prior output
- train_unet_transformer.py:56 loss = "BCE on annotated rows and columns (sparse GT, unannotated ignored)" -> network supervised EXACTLY on the pairs that are evaluable in the lab; sub-threshold probs there are in-sample (memorised targets), out of sample they are not.
- CONTEXT ~1207: probe 21 relink-off 0.945, probe 22 relink bonus 2.5 0.945 (both -0.002 vs 0.947); relink-off local +0.0053 -> LB -0.002. Two measured cases where trusting net probs more in relink did not transfer; BONUS 1.5 variant = same direction as probe 22.
- Expected local +0.000..+0.001 (research) < +0.002 gate; in-sample inflated; no out-of-sample check except an LB probe, which research says not to spend -> cannot be validated for private.
- Node multiplier: relink-only, edge_prob kept separate -> node count ~unchanged; not the leak route. 44b6: selection is 6bba only (dense labels), pocket gains concentrate there.
- Verdict: refuted under transfer lens.
