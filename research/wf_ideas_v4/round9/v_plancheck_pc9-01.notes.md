# v_plancheck_pc9-01 notes (2026-09-26T12:56:45Z)
- Commit times (git log --date=iso-strict, +03:00 -> UTC):
  - e925955 / 9c85782 09:51:54Z "G-A train run 43/62" (G-A reading fixed here)
  - 9826517 10:27:19Z (wt4) G-A readout 43/62
  - 1986fb9 10:45:32Z (wt6 only) proxy G-B on exp39 tails: 44b6 -0.00047, boot lower -0.00216, FAIL on proxy
  - 24dcdea 10:52:55Z main: commit message itself says "G-A fail (43/62), proxy lab -0.00047"
- CONTEXT 10:52 entry (l.~2178) openly lists the proxy -0.00047 / -0.00216 / 22-37 as "Supporting evidence (info)".
  It does NOT contain the phrase "written before any exp64/G-B number"; only the 11:06 entry does, scoped as
  "no exp64 output was on disk" -> accurate (exp64_a files 12:05-12:32Z, exp64_b dir 12:57Z).
- G-A is a mechanical count (43/62 vs >= 60), fixed 54 min before the proxy existed -> no contamination path.
- The proxy is not G-B as pre-registered (G-B = x138/K2 tails; proxy = exp39 divnet_rerank tails, no insertion).
- No logged user answer to R8-A2 (grep CONTEXT). 11:06 entry already says "Default = STOP"; round prompt 69a35b4 and
  this task text say STOPPED / do not re-propose. So "final close" is redundant; zero score effect.
- Only real wording slip: the R8-A2 question text (round8/report.json) said nobody had seen G-B lab results, while
  the proxy was known (and logged at 10:52). Proxy != G-B, so minor.
- Verdict: honesty-gap core refuted; optional one-line clarification only.
