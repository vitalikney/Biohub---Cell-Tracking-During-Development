# r22mb-3 skeptic notes (2026-09-28 ~01:25Z)
- No prior v_hyp_morning_brief_r22mb-3.json existed; fresh run.
- grep 'FINALS CARD|R20-A9|R21-A9|V_pub' CONTEXT.md (3398 lines) at 01:23Z: 0 hits for card/R20-A9/R21-A9; only the older v2 (9) V_pub lines (l.3178-3194). Finding confirmed.
- CONTEXT tail: 01:02Z entries = W2 TABLE v4 + W4 AMEND 2 (R21-A7/A8, commits bb3c299/acbea01). R21-A9 not appended.
- round21/report.json R21-A9: covered_by_existing_approval=true; deadline "before first W1 terminal header (~07:30Z)"; (iv) Russian message is for 29 Sep 12:00Z (refresh 18:00Z), NOT the morning brief (R21-A10 ~08:00-09:30Z).
- round20/report.json R20-A9 (c) ranges (+0.06..+0.21 bronze) differ from R21-A9 (iii) (~+0.1-0.2; pair ranges .55-.8/.2-.55 vs .35-.65/.03-.23) -> must say (iii) supersedes (c), else two range sets in CONTEXT.
- experiments/lb_poll/ledger.md (01:16:07Z): 56623073 exp78b sub 00:06:09Z PENDING; 56623105 exp79a 00:06:33Z PENDING; 56624341 exp78a 00:50:37Z PENDING. Last poll header 2026-09-28T01:16:05Z.
- Safetail latency floor in ledger: exp58n (6.69, 6.87]; exp70a (6.87, 7.04]; exp70d (7.19,7.36]. 00:06:09Z + 6.87 h = 06:58Z -> a terminal header for 47 is possible at ~07:00-07:06Z, so '~07:25Z' deadline is too late; append now, hard stop ~06:45Z.
- No R8 issue: text only, no build/submit; the user ticks; session never re-ticks.
