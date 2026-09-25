# lens_literature notes (started 2026-09-25T17:21Z)
- step1: lens_literature.json absent -> fresh run
- 17:5x UTC read: CONTEXT.md tail (pre-reg v3 rules, #34 0.953 L<=6.46h, #35 0.954 L<=7.73h, step0 N<=~100, dummy gates 18/18), FINAL_REPORT v3 §a-c,§i (closed list incl. BYTE ext, ultrack optional nodes, tracklet LAP, mirror daughter, split-aware relink, 2nd daughter by edge feats), experiments/ext_x138/DIFF.md (tail order), v3 h_literature.json + skeptic verdicts (byteext +0.0007, optional nodes +0.0003, LAP +0.0003).
- Implication: literature ideas already mined for node-recall/link; remaining unmined axes = division costs INSIDE the ILP (linajea-style cell-state classifier), uncertainty/MHT, runtime headroom (~4 h) uses.
- search 1: CTC Fluo-N3DH-CE -> Hirsch et al. MICCAI 2022 https://link.springer.com/chapter/10.1007/978-3-031-16440-8_3 (linajea + learnt division detector in ILP, beat CE leaders); Kaiser et al. 2024 mitosis-aware MHT https://arxiv.org/pdf/2403.15011 ; SAM4Track https://arxiv.org/html/2509.09943v1
- search 2: trackastra needs masks (https://arxiv.org/pdf/2405.15700); points-only use would need sphere masks -> weak fit.
- linajea+csc (Hirsch 2022, arXiv 2208.11467, pdf text extracted to scratchpad linajea.txt): 4-class cell-state ResNet18 (parent/daughter/continuation/polar body) as node costs + constraints parent->daughter in ILP; "lowers false divisions drastically" (Table 2 mskcc: FPdiv ~1.6 -> ~0.9). No such classifier exists for us (DeepCenter = nucleus-centre prior, 71 44b6 clips train / 128 6bba val; DivNet public = parent-only classifier, B20 closed: k=2 16 TP/319 FP, CONTEXT l.1011-1024). Retraining banned (R9) -> csc-in-ILP not doable; take only the training-free part: image evidence at forks.
- official metric (tools/official/metrics.md l.51-128): division window tolerates fork one frame late/early (parent anchor = GT parent or predecessor) -> fork temporal-shift idea is useless. FP fork only when local GT evidence.
- x138 cell 5 (scratchpad x138_cell5.py l.1474-1640): safe divisions = one-child source + orphan start at t+1, gates parent<=9, sister<=14, mutual NN, divergence>=2.25 at t+2, DeepCenter>=0.25 at the candidate daughter, symmetry 0.6; rank parent+0.15*sister. Caps 0.00375 edges global / 0.0076 frame NOT binding (dummy: 35/6/5/16 added vs caps ~94/70/23/254). DeepCenter rejects 84/121,149/155,8/13,203/222 geometric candidates (browser_intel §6.0B).
- No prior work used an image VALLEY / daughter-size test ON FORKS (grep valley: only hole-fill, dup-collapse, DoG). zhincez (CONTEXT l.210): dividing nuclei get SMALLER (half-max volume -0.27 at +3 frames vs same-frame controls, already lower at -2/-1), peak intensity holds.
- ILP_TIMEOUT 1200 s not binding (dummy ILP 5-90 s) -> no headroom idea there. DEEPCENTER_TTA already 1 in x138.
- OrganoidTracker 2.0 (Nat Methods 2025, https://www.biorxiv.org/content/10.1101/2024.10.11.617799v1.full): context-aware marginal link probs (subgraph <3 steps, partition function) -> filtering; on our metric edge removal = closed edge-filter line (0 on LB) -> not proposed.
- HOCT (https://arxiv.org/abs/2607.11754): needs segmentations + training -> not inference-only for us.
- Runtime: the binding constraint is NOT 12 h but K2's own DIVINS_DEADLINE_S 28,800 s (8.0 h) vs forecast <=7.8 h -> any rider costing > ~10 s/clip (N~100) before the insertion can skip insertion on late clips.
- 18:3x UTC PROTOTYPE (scratchpad forkvalley.py; exp56 dummy submission.csv = x138 verbatim on 4 train clips, local zarr,
  gaussian sigma zyx 0.6/1.5/1.5 vox, valley = min interior profile c1->c2 / min(ends)): 62 forks, ALL 'ignored' by the
  official metric on these clips (0 TP / 0 FP; 6bba_05db0fb1 has 3 GT div FN). Sister distance bands: <=5 um 15 forks,
  valley median 1.02, 100% >= 0.95 (one blob); 5-7 um 15 forks, 60% >= 0.95; 7-9 um 26 forks valley median 0.52; 9-12 um 6, 0.40.
  Control NN pairs of non-fork nodes: 3-5 um n=12 v95 0.67; 5-7 n=183 v95 0.39; 7-9 n=368 v95 0.22; 9-12 n=402 v95 0.23.
  => ~24% of x138 safe-div forks have sisters on ONE blob at t+1 (duplicate signature). Need GT sister distribution next.
- 18:5x UTC GT CHECK (scratchpad gtsister.py / forkvalley2.py, all 199 train geffs, 151 GT divisions, same valley def):
  GT sister distance at the first daughter frame: median 10.57 um (IQR 8.0-12.7), valley median 0.63.
  GT with sister <= 5 um: 5/151 (3.3%); sister <= 5 AND valley >= 0.95 ("one blob"): 3/151 (2.0%); of those still
  one blob at t+2: 1/151.  x138 dummy forks: one blob at t+1: 15/62 (24%) -> ~12x enrichment vs GT; their t+2 sister
  distance 5.3-8.0 um (GT at its first daughter frame: only 22/151 <= 7 um) -> looks like duplicate detections, not
  forks placed one frame early on an anaphase blob. 8/15 still one blob at t+2.
  Division-term arithmetic: removing one evaluable FP fork dJ ~ +J/S, losing one TP dJ = -1/S (S = TP+FP+FN) ->
  break-even FP:TP inside the vetoed cell ~ 1/J ~ 2.8 at J 0.36 (probe 26: 0.947->0.911 with safe divs off).
  Candidate idea #1 'forkblob': veto (drop added safe-div edge, nodes untouched, last edit next to forkmid) when
  sister1 <= 5.0 um AND valley1 >= 0.95 (thresholds fixed NOW from GT stats, lab only confirms).
- Idea #3 considered: DeepCenter-rejected geometric candidates rescued by image evidence (two blobs + daughter shrinkage,
  zhincez -0.27 half-max vol) = R4 fork adder, lab-only, P(gate) ~0.2.
- 17:39 UTC final JSON written: research/wf_ideas_v4/lens_literature.json (3 ideas: L1 forkblob, L2 deadline retune 12h, L3 DC-rescue image evidence; critique). Prototype scripts in session scratchpad: forkvalley.py, forkvalley2.py, gtsister.py
