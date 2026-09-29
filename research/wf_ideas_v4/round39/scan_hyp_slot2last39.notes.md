# scan_hyp_slot2last39 notes
- 2026-09-29 11:10Z start; folder created.
- 11:12Z read CONTEXT l.4380-4539 (09:00Z P55 exp89t submit, 09:09Z exp75 0.955, 09:19Z exp89r 0.957 DIS~0, 08:28Z user hold slot 2 to 12:00Z, 10:54Z R38 applied, 11:10Z timer log A-M2 UNUSED).
- 11:14Z external delta since 09:14Z, 0 Kaggle calls (local files only):
  - experiments/discussions/digest_20260929T0918Z.md: 3 comments (744278 fheizz 'nah too late'; 744273 Satwik 09:06Z 'public LB has very few divisions', no values; Yassine 09:13Z no values) -> already covered r37/r38.
  - digest_20260929T0958Z.md: 0 new topics / 0 new comments; E10 flag 0.9812 beraterolelk = other competition (CONTEXT 10:00Z).
  - feed_loop.log last run 09:58:41Z; next ~11:28Z (90-min cadence).
  - experiments/e10_watch/20260929T1110Z.txt: DIFF vs 1041Z: all 5 kernel lists + 2 statuses 'no change'; newest comp kernel still flexonafft lineage-forge 2026-09-28 13:02Z; best genuine public notebook 0.953. LB 11:10:54Z: ours #141, 0.959, count 56, 17th of 22 in 0.959 block; >=0.960 124 (unchanged). Only LB movers (Manish 0.956->0.959 etc.), no disclosures.
  - round38 scan_browser (Chrome 10:13-10:20Z): no new topics/comments, Code tab unchanged.
  => NO disclosed knob / public notebook / finding since 09:14Z.
- Timing arithmetic: non-CI safetail L (7.03, 7.19] h (exp89p) -> latest submit reading by 19:45:17Z = 19:45:17 - 7.19 h = 12:33:53Z; CI (exp75 8.88-9.05 h, exp87a/89r 9.04-9.48 h) -> latest 10:15-10:52Z = already passed. New build not yet dummied needs ~35-45 min (r37: compute ~1,130 s + rglob 203-788 s + queue + gate) -> push by ~11:50Z for a 12:33Z submit, i.e. outside the user's 12:00Z hold.
- Existing gated non-CI candidate exp89s (K + DIS, dummy PASS, CSV 8956f46c6824): DIS ~0 (09:19Z) -> expected display ~0.958; V_pub needs >= 0.960 -> P small (~0.02-0.05); not a partner (carries K + cap 6); excluded by task (do not revive). No finals value.
- No WebSearch done: a paper/GitHub search cannot produce a pre-registered, dummied file by 12:00Z.
- 11:17Z wrote scan_hyp_slot2last39.json (4 findings; verdict: slot 2 UNUSED, nothing reaches R8).
