# v_literature_l1-forkblob_feasibility notes (FEASIBILITY/SCHEDULE skeptic)
- 2026-09-25T17:45Z: started; no prior json existed. Sibling d2 feasibility json read (forkmid lab-gate pipeline, K3 calendar).
- 17:46Z clock (date -u). Read CONTEXT l.1600-1853 (§e slots S1-S21, R1-R10, dummy gates, T2-T7, 17:20/17:45 dummy PASS, night plan).
- Image access at the forkmid site: exp58 notebook post cell (code cell 7) defines read_test_frame(dataset,t,frame_cache)
  (l.139, blosc2 chunk read, FIFO cache FRAME_CACHE_MAX_FRAMES=48) and repair_frame_cache is a local of
  filter_output_graph (l.2001), still in scope at the FINAL print (l.2127) where FORKMID_CALL is spliced
  (tools/build_probe_kernel.py l.1777-1792). -> a forkblob call there can read frames. Implementable.
- Frame size: train 6bba_05db0fb1.zarr shape [100,64,256,256] uint16, chunk [1,64,256,256] = 8 MB/frame -> blosc read
  ~10-30 ms; crop blur tiny. ~15 forks/clip -> < 1 s/clip -> ~1-2 min over N~100. step0.md: K2 worst case ~7.8 h vs
  DIVINS gate 8.0 h (margin >= 12 min) -> forkblob (after insertion, per clip) delays later clips' gate checks by
  <= ~1 s each -> does not threaten the gate. 12 h hard limit irrelevant.
- Builder: forkmid is forced to be the last patch before safetail (l.2011-2018); forkblob needs the same ordering
  rule (after forkmid). forkmid_edges is pure; trainlab has its OWN forkmid copy (trainlab.py l.318) -> for forkblob
  make the kernel function pure with a frame-reader callback and exec it in the lab to avoid lab/kernel drift.
- Lab: trainlab arms are graph-only replays of exp60 dumps (l.72, l.493-511); forkblob arm needs local train zarr
  (398 files present locally = 199 clips) -> feasible, prototype forkvalley2.py already reads them.
- exp60 results dir absent at 17:46Z -> no lab number seen yet; pre-registration still possible (must precede ANY
  trainlab score run incl. partial shard A; T9 may run tonight).
- Prototype output (scratchpad forkvalley_exp56.csv): all 62 forks 'ign'; the 15 flagged are exactly the 15 with
  sister <= 5.0 um -> valley >= 0.95 never binds on the dummies (min flagged valley 0.959). Three forks at 5.09/5.20/5.30
  um (valley ~1.0) sit just above the distance threshold; one at 4.77 um valley 0.959. K2 has lowrefine + linefit
  shifts (sibling d2 note: 2 new non-inserted forks on K2 dummy) -> the dummy gate "count == 15 of 62" is ill-posed on
  K3; must be recomputed on the K2 dummy CSV with the kernel's own pure function.
- Governance: R3 criterion = "nodes unchanged or only coordinates"; R4 = "changers of node OR FORK set" and lists the
  DeepCenter threshold (K3b changes only forks) -> forkblob (fork removal only, like C04 forkmid) is ambiguous between
  R3 and R4; must be pre-registered explicitly before scores. R4 would need Delta >= +0.002 public.
- Calendar: implement tonight (~2.5 h patch+tests, 1 h arm, 0.5-1 h scoring) -> lab verdict 26.09 morning; K3 dummy
  ~0.5-0.7 GPU-h (quota ~5 h left after exp60 shards, weekly reset expected Sat 00:00Z unconfirmed); S4 26.09
  10:00-13:00 -> score ~18:00-21:00 26.09; fallback S7 27.09 <= 12:00 (R8 cutoff), score ~20:00 27.09, before
  S12 consolidation 28.09 12:00. K3 LB submit needs the user's OK (only K2 pre-approved) - user awake by S4.
- Coupling: if forkmid fails its T9 gate (P(pass) ~0.35-0.5 per d2 feasibility json), K3 = K2 + forkblob alone; if
  both pass they share S4 and a K3 < K2-0.001 kills both -> spare 26.09 slot (S3 held in branch A / S5 if K3b fails)
  or S7 can carry a forkblob-only build.
- Pre-reg caveat: thresholds use GT sister stats of ALL 151 train divisions, which include the lab's 99; no fork labels
  seen, acceptable but should be stated.
- 17:49Z: final JSON written (refuted=false, with gate fixes).
