# scan_hyp_ladder_next notes (round 13, 2026-09-26T22:46:00Z)

## 22:46-23:00Z reading
- Time now 26 Sep 22:46Z. Probes 39 exp70e (21:15:23Z), 40 exp70a (21:17:47Z), 41 exp70d (21:38:33Z) PENDING (poll.log). Probe 42 = exp70b (fm45) at 00:05Z (CONTEXT 21:56Z cap-6 arm negative -> exp70b; exp70g not submitted).
- LB snapshot experiments/e10_watch/20260926T2246Z.txt: 3,935 teams; we are rank 229, 15th of 100 in the 0.954 block (215-314); 0.955 block 63 teams (152-214), 0.956 38 (114-151). Neighbour directly above: #228 AkiraIshikawa (last sub 14:52:53Z), below: #230 koucha. Our LB LastSubmissionDate = 2026-09-26 00:02:18 = #38's submit time, i.e. PENDING probes 39-41 are not reflected -> the field = submit time of the latest SCORED sub (usable as an LB-freshness check).
- In-block history: 6th of 73 after P36 (00:47Z) -> 12th of 87 at 08:38Z after K2 scored 07:34Z (6 entrants passed; no evidence K2 > P36 unrounded).
- r_ladder.json L5 + v_ladder.json corrections (7): POSITIVE = display >= 0.955 or 0.954 with an attributable in-block UP move; NEGATIVE = <= 0.953; NEUTRAL = 0.954 with no move or a non-attributable move. NEUTRAL knobs neither combined nor banned.
- exp60 results.md: arms with a lab sign >= 0 on BOTH embryos: ins35 (in K2), forkmid45 (44b6 0.0000, 6bba +0.0002; lowrefine-sensitivity arm removes 4 TP), lp30 (round 4: +0.00083, 51/56). dc0.30 44b6 -0.0006; dc0.35 cliff; cap6 -0.00057 (both negative); cap8 44b6 -0.00079; linefit_w07 44b6 -0.0031. Round 12: readmitted-leaf drop 44b6 -0.00058; gapfill_peak drop +0.00012 (negligible, new code). z +0.1 vox (I-029) both positive in-sample but closed for finals + new code (no builder patch). => no NEW existing-knob single with a both-embryo lab sign.
- Valid --set knobs (I-309): DEEPCENTER_GAP_THRESHOLD, DEEPCENTER_SAFE_DIV_THRESHOLD, LOWDET_THRESHOLD, LEAF_PRUNE_MIN_EDGE_PROB, DIVINS_*. No lab data for GAP/LOWDET on x138; DIVINS_THRESH 0.3 / lp50 / dc0.275 = threshold neighbours (I-310, banned).
- KEY STRUCTURE: after 39-42 the only UNSCORED combos of {lp30, dc0.30, fm45} are lp+fm (exp70c), dc+fm (exp70h), lp+dc+fm (exp70f): every informed combo needs fm45 (probe 42, scores ~07:30Z) to be POSITIVE.

## 23:05Z dry builds (scratchpad only; builder imported with ROOT monkeypatched to scratchpad/r13ladder; nothing written under experiments/)
- Reproduced repo shas: exp70a 132438a9626400e4, exp70b b8e7ece1a33cd2a1, exp70e c0f3380c04af3ae6 (== experiments/*).
- Combos: exp70c_k2_lp30_fm45 a7271d4e9a758607 (== r_ladder's quoted exp70c sha), exp70h_k2_dc030_fm45 7ed29dd35a32774f, exp70f_k2_lp30_dc030_fm45 b009bedd4ce4b2f6. Kernel ids vitaliineibauer/biohub-exp70{c,h,f}-..., private, internet off, 5 dataset sources, kernel_sources [].
- Diffs: c vs a = cell0 name+FORKMID line, cell7 +88 lines (forkmid); c vs b = cell0, cell2 +4 (lp knob), cell7 +66 (leafprune); f vs e = cell0 + cell7 88; h vs b = cell0 only (3 lines). All code cells compile.
- leafprune+forkmid and dc+forkmid have NEVER run together on Kaggle -> a dummy is mandatory (not only formal).
- Node identity check for combo dummies: forkmid never touches nodes -> exp70c nodes == exp70a dummy (120,719), exp70f == exp70e (120,707), exp70h == exp70d (121,240); forks <= parent.

## Timing (K2 latency 7.36-7.54 h, CONTEXT 07:35Z)
- 39 exp70e 21:15:23 -> 04:37-04:48Z; 40 exp70a 21:17:47 -> 04:39-04:50Z; 41 exp70d 21:38:33 -> 05:00-05:11Z; 42 exp70b 00:05 -> 07:27-07:38Z. 39 and 40 are 2.4 min apart -> high co-completion risk with the 10-min poller (experiments/lb_poll/lb_poll.py sleeps 600 s).
- Resolution estimate (assumption: uniform 0.954 block): 100 teams over <= 0.001 -> ~1e-5 spacing; 15th -> B0 ~0.95436; display flip needs ~+0.00014; passing one neighbour needs ~+1e-5.
- ORDER EFFECT: after one probe raises the team best, later probes register UP only if they beat that new best; their 'no move' is then uninformative (NEUTRAL), incl. exp70b's fm45 read at 07:30Z.
- 2026-09-26T22:56:48Z read round13 scan_plancheck (PC13-03/04/06/07 folded in: stop rule exempts blind rungs, 8.0 h insertion-gate check, slot priority); final JSON written research/wf_ideas_v4/round13/scan_hyp_ladder_next.json (7 findings)
