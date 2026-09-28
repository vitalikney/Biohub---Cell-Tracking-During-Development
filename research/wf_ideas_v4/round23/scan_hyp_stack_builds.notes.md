# round23 scan_hyp_stack_builds notes
- 2026-09-28T04:00:51Z start; no prior json
- 2026-09-28 build check. Scratch root = session scratchpad/r23 (copy of tools/ @ c86fd5a (clean), exp56_x138_verbatim, exp39). Env block = round21 scan_hyp_w2_w4_plan.json build_env_git_bash verbatim (MSYS_NO_PATHCONV=1).
  - Refs rebuild byte-identical (nb + kernel-metadata; probe.json 'change' equal): exp58 K2 1f1ddb6d63b47f54, exp58n twin 55038fd6ac009ad9, exp70g 52c182a36a40faf9, exp78a 8d8d9c28, exp78b d54d810c, exp79a 5f9b265d, exp80a da984964, exp81 6a62e321, exp83a 80a0856f, exp83b d9b0834d.
  - New builds, all 9 match plan prefixes; then built in repo experiments/<name>/ and repo == scratch byte-for-byte (nb + meta):
    exp82a ffc00631194affcc | exp82b 7cd1e3ed4a706cbb | exp82c ee4312442a4f3ab8 | exp83c e8f5a8a621222f77 | exp83d 22ccc1dd89c948e3 | exp83e a016cf0f733e53bc | exp83f c8a2fccba8d60596 | exp83g 00f8cb366726663c | exp84a 4cb1e47bbd7840e5
  - Diffs vs siblings: exp82a vs exp81 = header + DIVINS_CAP 6->8 only; exp84a vs exp80a = header + CAP 24->48; exp83c vs exp79a and exp83d vs exp83a = header + 2 SECONDARY env lines + secondary sha line reading env.
  - Metadata: private, T4, GPU on, internet off, docker pin unchanged; SEC files add vitaliineibauer/biohub-secft-n2a-v1, CI files add yuki0731/biohub-coord-inject.
  - Ledger family (tools/runtime_ledger.py EXP_RULES): exp82a-c/84a -> safetail, exp83c-g -> safetail_ci. OK.
  - No push, no submit, no git change to tracked files (git status: only pre-existing M lines + new untracked folders).
- 04:05Z state: poll header 2026-09-28T03:56:32Z -> 47 (56623073), 48 (56623105), 49 (56624341) all PENDING. E10 run 16 03:43Z 0 signals.
- kaggle kernels list --mine (read-only, 04:06Z): newest runs exp83b 01:01:59Z, exp83a 01:01:48Z (both COMPLETE+PASS per CONTEXT 01:50Z) -> both GPU lanes idle since ~01:35Z. No dummy exists for exp82a-c / exp83c-g / exp84a.
- kaggle datasets (read-only): yuki0731/biohub-coord-inject lastUpdated 2026-08-25 09:41:33Z (unchanged; files dated 25 Aug; coordinject_patch.py sha256-checks them anyway, fail-soft). vitaliineibauer/biohub-secft-n2a-v1 files dated 2026-09-27 21:25:39Z incl. ARTIFACT_MANIFEST.json (present).
- Gate gap: CONTEXT has a dummy gate only for exp83a/b (R22-A1, 01:48Z). No pre-registered gate for SEC stacks exp82a-c or SEC+CI stacks exp83c-g. CI is a post-step on submission.csv (coordinject_patch.py docstring: nodes/ids/edges unchanged) and exp83a==exp78b / exp83b==exp78a / exp79a==exp70g topology -> SEC+CI dummy topology must equal its SEC-only sibling dummy (exp81 for 83c, 82b for 83d, 82a for 83e, 82c for 83g; exp80a for 83f).
- Ideas: IDEAS.md curation 22 (425 ideas; open-untested 2). Round 22 already concluded no new mechanism reaches R8; R8 hard line (27 Sep 12:00Z) is past. Nothing new here reaches R8.
- 2026-09-28T04:07:04Z final JSON written (6 findings)
