# schedule skeptic notes: ultrack-dense-6bba
- 2026-09-25T11:17:22Z started; no prior json. Read BRIEF.
- 11:2x sibling schedule verdicts for ideas 1 and 2 (dense-dorado-secondary, dense-primary-headrefit): BOTH refuted, P(scored gate-passing probe) 0.09 / 0.03-0.05. This idea only feeds them -> strictly longer chain.
- evidence checked: fn_anatomy_exp39.md a_never 1907 (44b6 167 / 6bba 1740) OK; register_44b6_dorado.py 84% within 2.5um OK; tools/build_dense_gt.py exists.
- ultrack_supplementary sparse_zebrafish config.toml fetched: database=postgresql, n_workers=25, window_size 25, overlap 5, time_limit 120000 s, threshold 0.4, min/max area 300/25000, max_distance 10, max_neighbors 5, weights -0.1. i.e. built for a cluster.
- PyPI ultrack 0.8.0: python >=3.11,<3.14; deps napari, zarr>=3, gurobipy, mip, higra, torch>=2.0.1 -> pip into Kaggle image will upgrade zarr/torch (torch 2.14 pulled here!). pip install here in a venv: works (~2 min).
- ultrack MIPSolver: tries config.solver_name (GRB default?) -> falls back to CBC only on InterfacingError. pip gurobipy has a size-limited licence (2000 vars) -> likely GurobiError on dense clips, not caught -> must force solver_name CBC (or heuristic solver).
- density: 6bba median 96 nodes/frame, densest quartile median 316, max 781; 44b6 ~270 (r2_critic.notes.md:12,17; r2_verify_overlap-consensus notes).
- 11:4x MEASURED here (4 CPU, ultrack 0.8.0 pip, CBC; synthetic 64x256x256 clip, 300 gaussian nuclei/frame, >=6 um apart, sigma 2.5 um, noise 0.05; scale 1.625/0.406/0.406; sparse_zebrafish thresholds):
  3 frames: detect_foreground+robust_invert 16.5 s, segment 8.0 s, link 9.2 s, solve 1.5 s.
  20 frames: fg/contours 107 s (5.4 s/frame, serial loop), segment 29 s (4 workers), link 9.6 s, solve 41 s (one CBC window, 37 s B&C).
  -> extrapolated 100 frames at ~300 nodes/frame: ~15-17 min/clip (fg ~9 min serial or ~2.5 min parallel, segment ~2.5 min, link ~1 min, solve ~4-5 windows x ~40-60 s). Real tissue (more hierarchy candidates, up to 781/frame) likely slower; median 6bba (96/frame) faster. Guess 199 clips = 25-60 CPU-kernel-h.
  Quality even on easy synthetic blobs: 271 tracked nodes/frame vs 300 true (0.90) -> under-detection with classical boundaries already on an easy case.
  Gurobi: pip gurobipy present but licence fails -> ultrack auto-falls back to CBC ("Gurobi environment could not be loaded") -> no crash. Needs `if __name__=='__main__'` guard (spawn multiprocessing) - first run crashed without it (in a notebook the segment workers may need n_workers=1 or a script file).
- raw.githubusercontent zebrahub.ipynb exists (200, 2.4 MB). unet-simview preprocessing undocumented (sibling note v_detector-retrain_ultrack-convention-localiser_schedule.notes.md:3); public.czbiohub.org 403 here -> weight reachability from Kaggle unknown (BROWSER_TODO #20).
- tools/build_dense_gt.py: teacher nodes added WITHOUT edges; keep-edges flag is new code; uses Windows junctions (friend A machine design).
- Agents cannot push kernels (BRIEF sec.3): every pilot/full/gate kernel goes through Vitalii / laptop agent.
- 2026-09-25T11:47:47Z final JSON written (refuted, P~0.05 as written, 0.10-0.15 repaired)
