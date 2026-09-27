# v_plancheck_pc19-04 notes (skeptic, value + feasibility)
- 2026-09-27 18:13Z: no prior v_plancheck_pc19-04.json. Sources: CONTEXT.md l.3037-3069 (16:08Z card (4), 16:08Z rebase, 16:33Z exp76d dummy, 17:21Z exp75 dummy), round19/scan_plancheck.json PC19-04, round18/REPORT.md l.84 (R18-A7 chain exp76a -> exp72 -> exp75), l.99 (exp75/exp72 as fallbacks).
- Contradiction confirmed: card (4) 'exp76a -> exp72 (as built) -> exp75'; 17:21Z 'For 00:05Z: exp76a if its dummy passes, else exp75'.
- Duplicate risk real: exp76d dummy 121,061 nodes/116,930 edges/79 forks (sha bee0afe9); exp72 121,061/116,931/80 (d78093ac). Same secondary ed8c616b; differ only by forkmid 4.5 base. Default rows (N4/N4, either NEG, 46 N4|MASKED) all hold exp76a + exp76d -> exp76a failure under card chain = {exp76d, exp72}, no CI read.
- Live risk: exp76a dummy pushed 16:33Z, no _dl output yet (only exp72/exp75/exp76d in _dl); exp75 dummy sat ~4 h queued (13:19->17:20Z) -> exp76a may miss 23:45Z.
- Timing: poll.log header 18:04:40Z shows 45 (56606948) and 46 (56611472) PENDING; 45 8.0 h mark 19:15:12Z. Amendment before then = pre-score.
- Extra gap found: card row 1 '46 in {P5,U4} -> exp76c, exp76g, and exp73m if 45 not NEG, else exp76a' -> with 45 NEG gives exp76c + exp76a = two CI files; also overlaps row 'Either NEG'. Same mechanism rule should resolve it (Either NEG row wins; slot 3 held).
- Row 1 needs its own per-slot chain: CI exp76c -> exp76a -> exp75; secFT exp76g -> exp76d -> exp72; division exp73m/exp76e -> held for W2.
- Value: all these files are public-only (card (2)), so no direct private gain; saves one of three W1 slots from a near-duplicate and keeps the CI read. Not a new mechanism, no R8 issue, reads a dummy event not a score.
