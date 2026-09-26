# R11-RC-C notes (x138 byte copy as final) - 2026-09-26T17:17:46Z
- start: no prior json; checking CONTEXT l.1550/1637/1739, v_private json, e10_watch 17:01Z
- 2026-09-26 ~20:25Z checked: CONTEXT l.1797-1798 (#34 submitted 08:09:00Z 25 Sep, 0.953, L34 (6.29,6.46] h); l.1550 (241 at 0.953 at 25 Sep 11:27Z -> all scored by 11:27, so submitted before ~05:00Z given >=6.3 h latency, i.e. BEFORE #34); l.1739 (Never tick exp56); l.1798-ff rules §3.7.b tie = earlier submission (https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/rules); l.1849 public in-block order = unrounded score; l.2033 late copies sit at block end; l.796 kernels deterministic run-to-run.
- e10_watch 20260926T1701Z histogram: 0.953 block 354 (ranks 296-649), 0.954 97 (199-295), >=0.955 198; we #210. LastSubmissionDate is not the scoring sub's time (147 inversions) - cannot count copies before 08:09 from CSV directly.
- l.2324 forecast: 250-400 teams above us given >X; bronze ~395.
- Own world check: {#37,#34} vs {#37,#38} differs only when I<0. #34 > twin only if L<0 (or L==0 exactly, since twin sub 26 Sep 00:02 is later than #34). #34 medals only if <= ~155 teams beat X on private AND I<0 AND L<=0: P ~<1%. Twin wins world I<0,L>0 (P ~0.07-0.1) with rank ~250-400. Dominance holds; 'every world' slightly overstated (small-field world).
- Nuance for RC-A: a successor published 27-28 Sep gets far fewer copies by deadline than x138's 350 -> bottom-of-block penalty smaller; supports RC-A only qualitatively.
- 2026-09-26T17:19:17Z final JSON written (refuted=false)
