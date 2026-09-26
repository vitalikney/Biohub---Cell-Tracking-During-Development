# v_plancheck_pc8-01 notes (Sat Sep 26 10:36:11 UTC 2026)
- (1) No prior v_plancheck_pc8-01.json -> fresh run.
- CONTEXT.md main l.2116-2117: G-A '>= 60 of the 65 GT-linked 44b6 pairs at exact GT offset (+-1); 0 6bba; 0 cross. FAIL -> stop.' grep of CONTEXT on main and all 4 wt branches (e79-1/4/5/6): NO G-A result logged.
- e925955 experiments/overlap_reg_train/ga_train.json: check.found_at_gt_offset 43, gt_links 62, wrong_offset [], missing 19, extra 44b6 pairs 6; stats accepted 49, candidates 74, rejected_spatial 21, rejected_frames 4, cross 0.
- My recount of the 19 misses vs 'rejected' list: 11 rejected 'spatial' at GT offset (frac 0.022-0.048), 4 rejected 'frames' at GT offset (1-4 frames), 4 never candidates. 43+15 = 58/62 < 60 -> FAIL even under the generous count.
- 9826517 (wt4) experiments/exp65_overlap_probe/ga_report.json: gate_verdict G_A_pass FALSE (the tool itself says FAIL); below_floor tally spatial 12 / frames 4 / none 3 (one never-candidate 8f5ab931|c50204e0 has frac 0.005); 'found_of_reachable 43/46' = post-hoc reframing. gt_links_in_splits_json 62 (65 = typo).
- Finding text says 13 spatial + 4 frames + 4 never = 21 != 19 -> arithmetic slip; correct: 11+4+4 (candidate view) or 12+4+3 (floor view). Core claim unaffected.
- Work continued despite FAIL: exp64 lab kernels pushed (05e366c), exp65 G-P probe built (9826517), K6 --patch overlapcons built (ff438f7), G-B driver (a012e32). wt6 has experiments/exp64_overlap_lab/{kernel_a,kernel_b,dryrun_exp60} only -> no G-B result read yet, so logging now is still clean.
- Verdict: NOT refuted. Procedural (pre-registration integrity); value of the line itself small (+0.0005 expected per 08:49 rules-check note); stopping costs ~0, continuing needs a dated USER DECISION AFTER RESULT.
