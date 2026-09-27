# round20 report notes

- 2026-09-27T20:31:47Z start; no report.json existed. Inputs: findings+verdicts from harness; files in round20/.
- 20:33Z judge checks: poll.log header 20:25:10Z shows 56611472 (46) PENDING. kaggle kernels status (read-only): exp78b COMPLETE, exp79d COMPLETE, exp77 RUNNING, exp79a 404 (never pushed). _dl exp78b dummy: 121,252 nodes / 117,092 edges / 95 forks, kernel_elapsed ~1,368 s, divinsert added 8/0/12/12 (orphan 5/0/11/6, steal 3/0/1/6) vs cap6 6/0/6/6 (steal 2/0/1/2) -> the cap12fc2 increment = 14 insertions, 5 of them steals. exp78a 86 forks, exp76e 80 forks recount OK.
- 20:36Z verified: last RESUME POINT still l.2599 (26 Sep 22:46Z); no 'R8 coverage' line; MEMORY project-lb-probe-approval.md modified 25 Sep, says 'E10 v1 in force' (PC20-05 confirmed, 5th round).
- tools/runtime_ledger.py EXP_RULES ends at exp70[a-z]* (l.76-77); no safetail_ci family (PC20-04 confirmed). tests/test_runtime_ledger.py exists.
- e10_watch_loop.py l.28 docstring + l.78 LOOK text say '>= 0.955'; runbook.notes.md l.57-66 computes OUR from poll.log (live 0.956 -> SC > 0.956); runbook l.206 SI K uses DIVINS_CAP=4 (PC20-06 confirmed).
- CONTEXT 20:30Z (after round 20 launch): user 'я спать - работай в автономном режиме'; session plan = W1 00:05Z 3 submits (exp78a, exp78b, exp76e or 46-informed), 2 slots kept for ~08:00Z (N2/CI/SEC stacks). This plan predates the round-20 findings; judge merges: exp76e -> CI exp79a; 2nd of the 2 later slots waits for E10 to 12:00Z (v2 (4)).
- 26 Sep 2026 = Saturday (weekly GPU quota reset 26 Sep 00:00Z; last reading 07:55/30 h at ~21:56Z 26 Sep; next reset 3 Oct).
- exp79a probe.json: exp70g + coordinject a0.5 (cap 6, fc 1, thr 0.4, lowrefine, safetail), kernel id vitaliineibauer/biohub-exp79a-k2cap6-coordinject (404 = never pushed).
- Judge W1 choice: design A (3 in W1 + W2a after DIV reads + W2b 12:00Z E10-held) over design B (4+1): keeps exp80a as the W2 DIV step (R20ID-3 fix) and matches the 20:30Z 3+2 plan; SEC read moves to W2 (R20ID-4 fix); N2 GPU0 = the one SEC recipe if its dummy passes (judge amendment of PC20-07, since v2 (6) bans N2 in W3/W4).
