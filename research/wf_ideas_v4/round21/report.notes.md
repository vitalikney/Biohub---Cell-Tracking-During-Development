# round21 report notes

- 2026-09-27T23:34:45Z: started report writer; report.json absent.
- 23:37Z checks: CONTEXT last dated entry 22:27Z (probe 46 read); grep 'R8 COVERAGE' / 'CORRECTION to the 18:56' / 'W2 TABLE v4' / 'CI-RAN GATE' / 'FINALS CARD LINES' -> none; last RESUME POINT l.2599 (26 Sep 22:46Z). MEMORY l.8/9 still 'E10 v1 in force' / 'latest 26 Sep 22:46'.
- tools/runtime_ledger.py EXP_RULES l.70-84: exp79a exact -> safetail_ci; exp8\d -> safetail (so exp83* would be mis-familied). No exp83 rule yet.
- poll.log last header 2026-09-27T23:25:46Z: newest ref still 56611472 (46); no 28 Sep submit yet.
- E10 loop RUN 11 22:44Z CHANGES=5 signals 0; next 23:43Z.
- Naming conflict: PC21-04 proposes exp82c/exp82d = CI stacks; r21w-1 (verified shas) uses exp82a/b/c = SEC stacks (exp82c = cap24fc2+n2a) and exp83* = CI stacks. Adopt r21w-1 names + r21w-2 rule; reject PC21-04 names.
- 23:42Z R8 origin: 02:00Z cap = R8/P7 (CONTEXT l.2145, 2351, 2522); E10 v3 (l.2917-2925) "lifts R8 for this item" -> an E10 copy after 02:00Z is arguably already allowed; ask anyway (PC21-05) with default yes.
- Judge decisions: adopt PC21-03 (v) (W2b -> W3 <= 23:30Z when BASE = exp70g) instead of r21w-5's exp83c-in-W2b (stacks unread SEC). Keep v3 names (W3 = 28 Sep <= 23:30Z, W4 = 29 Sep 00:05-01:45Z); reject r21w-7 renaming. Use BASE (v3 (5)) not 'holder'. SEC file stays exp81 (r21w-4 refuted).
- Dummy plan: tonight exp83a + exp83b (W2b CI candidates, 2 lanes); exp83c optional; SEC/SEC+CI stacks on BASE after the DIV reads (~08:40Z); exp80a-base stacks after its read; exp84a only under S3.
- 23:39Z Write of REPORT.md blocked by the harness (as in r20); Russian report goes into report.json report_md_ru for the main session to write.
- 23:43Z report.json written (13 actionable R21-A1..A13; report_md_ru embedded).
