# v_recheck R11-RC-B ILP division weight - skeptic notes (2026-09-26 ~18:20 UTC)
- No prior answer file existed.
- x138 weight: experiments/ext_x138/biohub-x138.ipynb cell 0 sets os.environ BIOHUB_ILP_DIVISION_WEIGHT = "1.2" (verified by grep).
- exp12 (RESULTS.md l.28-29): div1.2 raw 36/205/70 -> precision 36/241 = 0.149; div0.6 24/104/82 -> 0.1875 (s_merge quoted 24/103 = 0.19, i.e. weight 0.6). Marginal 0.6->1.2: +12 TP / +101 FP = 0.106.
- CAVEAT (strengthens closure): exp12 sweep.py scores via pilkwang train-repo `evaluate` (committed 2026-09-06, before the 2026-09-11 discovery of the official rule) = PRE-PATCH weakly-connected-component division credit, which over-counts TPs (memory: fork 4 TP vs official 3). So 0.149 is an UPPER bound on official precision. Also model = exp03B pipeline, not x138 weights -> not x138's net anyway.
- Break-even verified from experiments/exp60_trainlab/results.json aggregate ALL: control 6bba 15/17/73 + 44b6 1/8/10 = 16/25/83, J=0.129, q*=J/(1+J)=0.114; ins35 6bba 23/23/65 + 44b6 2/8/9 = 25/31/74, J=25/130=0.192, q*=0.161. Derivation: dJ>0 iff q > T/(D+T) = J/(1+J). Correct.
- Edge bed: _dl/exp60_a/edge_cache/44b6_18ced818.npz edge_src/edge_tgt/edge_prob shape (0,) -> no ILP edges cached, no replay bed. Confirmed.
- No output channel: x138 relink is one-to-one (v3 j-14; probe 3 weight 0.9 neutral 0.941 on public pipeline, consistent).
- Verdict: not refuted; info-only ledger fix, no build, no R8/OK needed. Suggest ledger adds "pre-patch metric, upper bound" and "exp03B pipeline, not x138 net".
