# round26 scan_hyp_morning notes
- 2026-09-28T13:18:59Z start. No prior scan_hyp_morning.json. Read CONTEXT 3398-3923 (RESUME 01:48Z .. 13:14Z risk stack gates). State: probe50 exp85a 0.958 R+; probe51 exp87a (K+CI) pending read ~21:30-22:15Z; night 00:05 exp89r|q, 00:06 exp75, 00:46 exp89p (user confirmed 12:25Z).
- 13:30Z feed digests 1207Z/1237Z/1307Z: 0 new topics; 1 comment (743006 g john rao 12:27Z, two hidden embryos, first private second public, maybe mixed) - no knob; E10 FLAG none; top public notebooks 0.953. No new disclosure -> aggressive mode adds nothing new.
- 13:35Z scratch mirror (scratchpad/mirror26 = tools/ + exp56 + exp39): exp85a e6337843, exp89l cad1d47f (= R25S-3), exp89q b80dae26, exp89r 5894ea50 reproduce byte-identical (order $C6 $JT $N2 $D25 [$CI]).
  NEW dry-run builds: exp89s_k2cap6_k_dis225 = $B $KB $C6 $JT $D25 -> 8ed72e32 (diff vs exp85a: cell0 DIS line + cell1 drift-guard 2 -> 2.25 only);
  exp89t_k2cap6_k_dis225_ci = $B $KB $C6 $JT $D25 $CI -> 76b898dd (diff vs exp87a: same 2 lines only);
  exp91a_k2cap4_k = $B $KB $C4 $JT -> 395208ad (diff vs exp85a: DIVINS_CAP 6 -> 4 only); exp91b_k2cap4_k_ci = $B $KB $C4 $JT $CI -> d629801c (diff vs exp87a: CAP 6->4 only; vs exp75: + 2 K lines).
  kernel-metadata identical to parents modulo id/title. C4="--set DIVINS_CAP=4 --set DIVINS_FRAME_CAP=1".
- Ledger: tools/runtime_ledger.py l.82 CI regex exp89[abcghilmnor] -> exp89t needs 't' added; exp91b needs a safetail_ci rule (exp9\d not covered except exp90a).
- Latencies (ledger.md): exp85a L (7.01,7.19]; exp70g (7.49,7.67]; exp78a (6.87,7.04]; exp79a CI (9.27,9.45]; exp87a submitted 12:14:57Z.
- 13:40Z exp89u_k2cap4_k = $B $KB $C4 $JT -> 6df9c9b6 (diff vs exp85a: DIVINS_CAP 6 -> 4 only; = #37 + K). Name chosen so the ledger rule exp8\d -> safetail covers it (exp91a would map to 'unknown'). exp91a/b dropped.
  Ledger check (tools/runtime_ledger.py EXP_RULES): exp89s safetail OK; exp89t -> safetail (WRONG, needs 't' in the l.82 CI regex); exp89u safetail OK; exp89l safetail_ci OK.
- DIS prior from old lab: knobarms_28sep/v_2.notes.md: exp13 (old v2.1 pipeline, 48 local videos) DIS 1/2/3 = 0.9149/0.9158/0.9110. Quadratic fit: a=-0.00285, b=-0.00195 -> f(2.25)-f(2) = -0.0007, f(1.75)-f(2) = +0.0003. Formula node bonus (CONTEXT 12:23Z) ~+0.0007 for -0.73% nodes. Net prior ~0 +- 0.001. Old pipeline had no relink; lab sign history poor -> weak.
- Node predictions: DIS 2.25 delta = -883 (exp88a vs exp70g), -834 (exp89q vs exp89p) -> exp89s ~121,450-121,500; K delta identical across caps (+1,076; exp86a/b = 122,328) -> exp89u nodes = 122,328, LOWREFINE 148,020 exactly.
- Timing (L non-CI 6.87-7.81 h, CI 9.27-9.45 h, tail 10.9 h): 51 reads 21:31-21:42Z (tail 23:09Z); exp89q 06:57-07:54Z; exp89p 07:38-08:35Z; exp89r 09:21-09:32Z (tail 11:00Z); exp75 ~09:06-09:36Z. M1 at 08:40Z reads 18:07Z (tail 19:34Z); M2 at 11:00Z reads 18:47Z.
- 2026-09-28T13:30:28Z final JSON written (7 findings R26M-1..7).
