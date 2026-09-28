# v_hyp_stack_builds r23sb-2 notes
- 2026-09-28T04:14:34Z start; no prior json. Task: skeptic check of r23sb-2 (finals/ladder rebuild byte-identical).
- tools/ diff c86fd5a..HEAD(e46b7ea): only tools/runtime_ledger.py (+7 lines, ledger rules 9e81f06/ad5cbaf); build_probe_kernel.py unchanged -> "copy at c86fd5a" == HEAD builder.
- Repo notebooks (git-clean, last touched 25 Sep f8e9c78/6f79a34): exp58 1f1ddb6d63b47f54, exp58n 55038fd6ac009ad9, exp70g 52c182a3, exp78a 8d8d9c28, exp78b d54d810c, exp79a 5f9b265d, exp80a da984964, exp81 6a62e321, exp83a 80a0856f, exp83b d9b0834d = finding. CONTEXT l.2222/2246/2349/2485/2983 record the same finals shas.
- INDEPENDENT rebuild (my scratch v23sb2, git archive HEAD tools+exp56+exp39, MSYS_NO_PATHCONV=1, CONTEXT l.1773/1780 commands): exp58 -> 1f1ddb6d63b47f54 nb cmp-same + kernel-metadata cmp-same; exp58n -> 55038fd6ac009ad9 nb+meta cmp-same. CONFIRMED.
- Caveat (not a refutation): byte-identical notebooks do not pin Kaggle dataset versions; irrelevant for #37/#38 since they are already scored (code-comp scores public+private in the same run).
- 2026-09-28T04:15:37Z final JSON written (refuted=false)
