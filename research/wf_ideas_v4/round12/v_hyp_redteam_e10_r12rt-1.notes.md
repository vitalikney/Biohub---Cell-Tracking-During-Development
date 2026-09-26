# v_hyp_redteam_e10_r12rt-1 notes
- 2026-09-26T20:43:29Z started; no prior answer json
- 20:40Z read scan_hyp_redteam_e10.json/.notes.md (finding R12RT-1, failure_modes, command_sequence step 2) and CONTEXT l.2217 (P4b(c): "record the version number"; port valid only if page shows the score on that same latest version).
- FACT kaggle 2.2.4 site-packages/kaggle/api/kaggle_api_extended.py l.6501-6629: kernels_pull parses owner/slug/VERSION and sends kernel_slug "slug/VERSION"; writes blob.source; metadata json has no version field (confirmed).
- FACT 20:44:33Z read-only get_kernel: amanatar/optimized-biohub-max-score -> current_version_number 5, blob sha 96387e7858e6 (= finding). With '/1', '/4', '/5' suffix -> HTTP 403 Forbidden. So a version-pinned pull is NOT available to us; only the latest. Premise of R12RT-1 holds.
- FACT: one get_kernel response carries both blob.source and metadata.current_version_number -> a single-response binding is possible (strictly atomic); the before/after bracket is equivalent because version numbers are monotonic.
- GAP: step 2 script prints the versions but does not take M nor exit non-zero on mismatch; e10_port_gate.py treats --version as INFO only (l.665-667, 959) and never reads e10_pull.json. Enforcement = operator reading output. Suggest assert v0==v1==M -> exit 1.
- Every failure of the check -> no port (safe direction); page/API numbering mismatch (deleted versions, running version) only yields false no-port. No scoring change, no R8 issue, implements P4b(c) -> no new OK needed.
- Verdict: NOT refuted; value = protection only (0 expected LB delta), feasibility high.
