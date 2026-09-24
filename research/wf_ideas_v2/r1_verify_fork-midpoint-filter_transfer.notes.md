# transfer verify: fork-midpoint-filter (started)
- Source: scratchpad/div_audit8.json rows (66 labelled forks). Scripts scratchpad/fm_transfer.py, fm_transfer2.py.
- Removed FP (mid>=4) are dominated by z offset: zoff 3.2-5.0 um in 7/11 (z voxel 1.625, integer z coords). TP max mid 3.76 also has zoff 2.87.
- 44b6: FP mid>=4 = 1/10 (10%); 6bba 10/33 (30%). All 44b6 TP mid <= 2.51. Evidence for the rule is essentially one embryo (6bba).
- Node count untouched -> no node-multiplier artefact (passes that part of lens).
- fm_transfer3.py (vectorised sim, extra out-of-sample per-node error, mid-vector noise sqrt(1.5)*sd): mid4.0 P(TP lost) = 0/1.4/2.8/4.2/6.5% at extra sd z 0/0.4/0.6/0.8/1.0 um (xy 0/.15/.25/.3/.4). mid4.5: 0/0.2/0.6/1.3/2.6%. xy>=4.0: <=0.9% but only 4-5 FP.
- Public EV (TP19/FP13, +0.0069 J per FP, -0.0189 per TP): 44b6-like removal 10% -> +0.0009 at p=0, -0.0001 at p=2.8%, -0.0006 at 4.2%. 6bba-like 30% -> +0.0027..+0.0004. Sign depends on which embryo the test resembles.
- Population mismatch: audit = exp39 safe-div forks only; exp48 base adds divinsert forks (mid<=6.5, no symmetry gate), TP mid unmeasured; GT divisions 21% mid>=4 -> post-hoc forkmid on divinsert forks can undo part of probe 28's +0.001.
- 4 of 11 removed FP have ILP-side prob 0.0 (unscored relink) -> overlap with edge filter base must be measured.
- Verdict: refuted as proposed (FM40 on all forks); repair = 4.5 um, safe-div forks only, bundle-only.
