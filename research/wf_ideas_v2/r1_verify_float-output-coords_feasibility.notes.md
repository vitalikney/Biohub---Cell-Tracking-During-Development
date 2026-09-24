# feasibility verify float-output-coords (started)
- exp48 nb cell 8 L1688-1748: write_test_submission int(round()) is the LAST op; DaughterNet insertion, leaf prune, linefit all run before -> no downstream conflict.
- replay.py write_geff L625-634 rounds; tail npz stores float post-linefit zyx (L1436) -> lab flag trivial.
- x138 DIFF.md L52 confirms x138 CSV writer still rounds.
- LB scores recorded to 3 decimals only -> +0.0015 may show as 0/+0.001/+0.002.
- truncation risk: 6bba-like -0.0047 but 44b6-like +0.0002 -> if public embryo behaves 44b6-like, truncation indistinguishable from 'server rounds' on public; private could lose. Policy must be: keep floats ONLY if public rises.
- final JSON written (not refuted; fix = keep-only-if-public-rises rule)
