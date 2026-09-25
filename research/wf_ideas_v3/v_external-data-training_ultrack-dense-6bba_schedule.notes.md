# schedule skeptic notes: ultrack-dense-6bba
- 2026-09-25T11:17:22Z started; no prior json. Read BRIEF.
- 11:2x sibling schedule verdicts for ideas 1 and 2 (dense-dorado-secondary, dense-primary-headrefit): BOTH refuted, P(scored gate-passing probe) 0.09 / 0.03-0.05. This idea only feeds them -> strictly longer chain.
- evidence checked: fn_anatomy_exp39.md a_never 1907 (44b6 167 / 6bba 1740) OK; register_44b6_dorado.py 84% within 2.5um OK; tools/build_dense_gt.py exists.
- ultrack_supplementary sparse_zebrafish config.toml fetched: database=postgresql, n_workers=25, window_size 25, overlap 5, time_limit 120000 s, threshold 0.4, min/max area 300/25000, max_distance 10, max_neighbors 5, weights -0.1. i.e. built for a cluster.
- PyPI ultrack 0.8.0: python >=3.11,<3.14; deps napari, zarr>=3, gurobipy, mip, higra, torch>=2.0.1 -> pip into Kaggle image will upgrade zarr/torch (torch 2.14 pulled here!). pip install here in a venv: works (~2 min).
- ultrack MIPSolver: tries config.solver_name (GRB default?) -> falls back to CBC only on InterfacingError. pip gurobipy has a size-limited licence (2000 vars) -> likely GurobiError on dense clips, not caught -> must force solver_name CBC (or heuristic solver).
- density: 6bba median 96 nodes/frame, densest quartile median 316, max 781; 44b6 ~270 (r2_critic.notes.md:12,17; r2_verify_overlap-consensus notes).
