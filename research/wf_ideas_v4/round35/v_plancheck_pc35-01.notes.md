- 07:24Z start; no prior v_plancheck_pc35-01.json. Read tools/uptest.py, CONTEXT 4260-4380.
- 07:27Z extracted leaderboard_rows (R32-A2 awk) from e10_watch 20260929T0513Z / 0641Z / 0713Z. Columns Rank,TeamId,TeamName,LSD,Score,Count.
  Ours: #133 / #134 / #136, 0.959, count 53 in all three. >=0.960 teams: 116 / 118 / 120; 0.959 block 22 / 21 / 20.
- Teams above us at 0713Z but not at 0513Z (comm): exactly 3, ALL now at 0.960: Miz 16758945 (#138 0.958 -> #114 0.960),
  Boopathi Raja 16775607 (#134 0.959 -> #102 0.960), Asan Ashirov 16887065 (#305 0.956 -> #101 0.960).
  -> No team entered the 0.959 block above us 05:13-07:13Z. A display-0.959 exp89p cannot pass a 0.960 team, so S0=0513Z
  and S0=0713Z give the SAME compare() result for any 0.959 exp89p. The finding's core evidence ("these are exactly the teams a
  marginally higher exp89p would pass") is false.
- Newer-S0-is-weakly-more-sensitive is true in principle (superset), and R32-A2 (03:56Z) already says S0 = the NEWEST count-53
  snapshot; R34-A1's "e.g. 0513Z" is only an example. Residual exposure = a team inserting between us and #135 Amin after 07:13Z
  AND exp89p landing in that gap: negligible.
- LB lag (+0 count at S1): not observed (finding admits; 21:42Z, 12:14Z counts up at header). Poll header 07:18:07Z; _lb has no
  post_* saves yet. A one-shot re-save on +0 is harmless (1 call, contingent), but "never MASKED on +0" rewrites R34-A1 wording.
- Verdict: refuted (premise false, zero effect on current data); keep only a 1-line log note.
