# prep_div_combos notes (aggressive division-side rungs for 28 Sep)
- 2026-09-27 11:21Z start. Context: CONTEXT 11:14-11:16Z (user: rise on the table, take risks). Pending public reads:
  43 exp70j DC0.20 (56598763), 44 exp70k DC0.225 (56598765) PENDING at poll 11:11:11Z; 45 exp70g cap6 (submitted ~11:15Z);
  last slot today exp70q (cap6+thr0.3+fm) or exp70r (exp70q + DC0.20); exp70n (thr0.3 alone) dummy running.
- Dummy insertion anatomy (_dl/biohub-exp70*/ logs, 4 dummy clips): the per-video cap binds hard at cap 4
  (eligible 14/0/33/142 -> added 4/0/4/4); cap 6 -> 6/0/6/6. Lab ins_cap6 (reach0955/ins_cap6.notes.md): cap 4 binds on
  45/56 lab clips, uncapped 525 insertions vs 201 at cap 4 (thr 0.4). Hidden test ~100-130 videos -> the cap, not the
  threshold, is the binding insertion knob; thr only matters on clips with < cap eligible. steal_cap = floor(cap/2).
- 11:22Z reproduction check: rebuilding K2 (CONTEXT l.1773 command) with the current working-tree builder gives
  1f1ddb6d (= experiments/exp58_x138_safe_lowref, finals file untouched), and the exp70q command gives 33ab04d1 (= the
  committed exp70q). Builder sha df0fe7c7 (working tree carries another agent's uncommitted succ-base edits).
- 11:24Z built 20 rungs exp73a..exp73v with research/wf_ideas_v4/bigger_levers/prep_div_combos_build.sh (singles DC 0.15 /
  cap 8 / cap 12 / frame cap 2 / thr 0.2; K2+fm x DC {0.225,0.20,0.15}; packages I2 = cap 8 fcap 2 thr 0.4, I3 = cap 12
  fcap 2 thr 0.3, I4 ultra = cap 16 fcap 2 thr 0.2, each + forkmid x DC {0.25,0.225,0.20,0.15}). Cell-diff check vs K2 /
  exp70b: only cell-0 override lines differ; all private, internet off, T4, x138 docker pin.
- 11:24Z GPU: exp71 RUNNING, exp70n dummy QUEUED -> 2/2 busy -> nothing pushed (builds ready).
- 11:27Z python -m pytest -q tests: 438 passed.
- 11:33Z decision table + JSON written (prep_div_combos.json). Rows: D (43/44) x C (45) = 9 rows, modifiers for the last
  slot (L) and exp70n (T). Most-covered rungs: exp73c cap12 (6 rows), exp73a DC0.15 (5), exp73s I4 ultra (5),
  exp73m I3 (4) -> dummy these first once a lane frees.
- Judgment: the lab is against bigger caps (ins_cap6) but was wrong in sign for DC; the only large public signal is
  "fewer divisions = -0.005", so the rows lean to "more divisions" whenever a read is not negative. I4 ultra is a real
  cliff risk (up to ~1,200-1,600 extra insertions on the hidden test) and is placed first only in C+ rows or R5.
