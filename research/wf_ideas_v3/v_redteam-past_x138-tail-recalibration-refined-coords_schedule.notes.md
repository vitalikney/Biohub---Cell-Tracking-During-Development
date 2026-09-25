# notes schedule-skeptic x138 tail recal (2026-09-25T11:22:07Z)
- read BRIEF.md; sibling value notes exist (linefit B28 grid, readmit/gapfill unrefined int16)
- 11:22:50 build_probe_kernel.py --base x138 --set ALREADY passes env overrides (cell 0 os.environ appended after x138's own lines). Dry-run in scratch copy OK: LINEFIT_WEIGHT=0.65, FLOW_TIGHT=6.5 appended. Knob env names: BIOHUB_OUTPUT_LINEFIT_WEIGHT/WINDOW, BIOHUB_MOTION_RELINK_FLOW_TIGHT_UM, BIOHUB_READMIT_RADIUS_UM (x138 cell 2). So the 'needs pass-through' dependency is ~0 h.
