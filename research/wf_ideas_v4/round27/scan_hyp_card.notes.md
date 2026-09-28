# scan_hyp_card notes (round 27)
- 2026-09-28T15:43Z started; round27 folder was missing -> created; no prior scan_hyp_card.json.
- Sources: research/wf_ideas_v4/round26/report.json R26-A5 (2) spec; round26/v_hyp_finals_r26f-8.json (draft + 4 defects); round26/scan_hyp_finals.json R26F-1..9.

- 15:50Z poll.log header 2026-09-28T15:41:53Z: 56640366 (probe 51 exp87a) still PENDING (poll.log l.23569). 15:15Z header was a DNS error (NameResolutionError), gap 14:54->15:41Z (ledger 'Poll health').
- Feed digest experiments/discussions/digest_20260928T1541Z.md: 44 topics, 0 new topics, 0 new comments; best public notebook 0.953; E10 FLAG none. Aggressive mode: nothing disclosed -> no file.
- Refs for the card (experiments/lb_poll/ledger.md): #37 exp58 56563521 0.954 L(7.36,7.54]; #38 exp58n 56563534 0.953; exp70g 56606948 0.956 L(7.49,7.67]; exp79a 56623105 0.957 CI L(9.27,9.45]; exp78a 56624341 0.955; exp78b 56623073 0.955; exp85a 56629533 0.958 L(7.01,7.19]; exp87a 56640366 PENDING. Night/morning refs unknown -> placeholders filled by the -m token ('probe 52: exp89r|exp89q = ', 'probe 53: exp75 = ', 'probe 54: exp89p = ', R26-A4 (c)).
- SEC swap count: IDEAS.md curation note says the R26F-8 draft's '7 swaps' is corrected to 'weight swaps 0/5 on our LB' -> card uses '0 из 5'.
- Q3 time: user 'да' 11:26Z = 14:26 MSK. 743006 g john rao comment 3529517 at 12:27:30Z = 15:27 MSK.
- NEW FACT (runtime): pulled dummy logs with 'kaggle kernels output <slug> --file-pattern .log' into scratchpad r27/{a,s,p,q,g,b}; script r27/t.py. Stage split (total / setup before 'GPU shard 0' / prediction min / ILP sum / repair sum):
  exp85a 1388/262/9.03/128.5/565.2 (DIS 2.0); exp89s 1566/436/9.73/129.5/525.7 (DIS 2.25);
  exp89p 1313/253/9.17/122.7/491.6 (DIS 2.0); exp89q 1576/519/9.10/122.7/493.3 (DIS 2.25);
  exp88b 1654/501/9.77/135.4/547.2 (DIS 2.0); exp88a 1894/788/9.35/142.7/525.6 (DIS 2.25).
  Total minus setup: exp85a 1126 vs exp89s 1130; exp89p 1060 vs exp89q 1057; exp88b 1153 vs exp88a 1106. => the '+15-20% DIS runtime' (round26 new_facts 6, R26-A3 expectation) is setup/I-O noise (253-788 s before the GPU shards), not DIS compute. Hidden L for DIS files = parent family (non-CI K2 ~7.0-7.7 h, CI ~9.3-9.5 h, tail ~10.9 h).
- PENDING arithmetic (L from ledger: non-CI K2 family 6.87-7.67 h; CI 9.27-9.45 h, tail 10.9 h):
  night: exp89q 00:05Z -> 07:02-07:45Z; exp89r 00:05Z -> 09:21-09:32Z (tail 11:00Z); exp75 00:06Z -> ~09:06-09:36Z (#37 7.36-7.54 + dL 1.6-2.18 -> 8.96-9.72 h => 09:04-09:49Z); exp89p 00:46Z -> 07:38-08:26Z.
  morning at the CUTOFF: A-M1 CI 08:45Z -> 18:01-18:12Z (tail 19:39Z); A-M2 non-CI 11:30Z -> 18:22-19:10Z (=> PENDING at 18:37Z in most cases); B-M1 non-CI 10:50Z -> 17:42-18:30Z.
  morning at the DECISION header: A-M1 decided at exp89p terminal (~07:40-08:30Z) -> read ~17:0x-18:0x; A-M2 decided at exp89r terminal (~09:25-09:35Z) -> read ~16:20-17:15Z; B-M1 decided at max(exp89q, exp89p) terminal (~08:30Z) -> read ~15:25-16:15Z.
- Q3 ambiguity found: card row {V_nonCI, exp75} can put a SEC file (exp89p/exp89q) in the 'основной' role while a CI file is V_pub -> SEC would be a final without being V_pub (Q3 says only V_pub).
- 15:55Z wrote finals_card_v4_ru.md (card + fill procedure + JSON placeholder table; JSON parses; no 'рекомендую' in the sent block).
- 15:58Z wrote scan_hyp_card.json (5 findings R27C-1..5); JSON validated.
