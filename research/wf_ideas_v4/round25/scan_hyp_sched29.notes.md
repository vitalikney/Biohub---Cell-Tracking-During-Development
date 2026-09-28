# round25 scan_hyp_sched29 notes
- 2026-09-28T10:17:34Z start; folder created
- 10:25Z read CONTEXT tail (last entry 10:16Z: exp87a/83c/88a/88b PASS, private hedge proposal exp75, 3 night + 2 morning proposal, open Q1-Q3 to user); round24 report.json R24-A1..A11; round21 build_env_git_bash.
- 10:25Z feed digests 0905Z..1009Z: 0 new topics/comments, E10 FLAG none (top public 0.953) -> no new disclosed knob this round.
- State: 50 exp85a PENDING (reads ~12:30-13:00Z); 51 = exp87a (R+) or exp83c (R0/R-/R?) per W2b amendment A (CONTEXT 09:35Z); exp88c dummy pushed 10:07Z.
- Latencies: non-CI K2 family L 7.0-7.8 h (47: 7.27-7.39, 49: 7.0-7.04, 45 <=7.67); CI exp79a L 9.27-9.45 h (CONTEXT 09:35Z).
- exp86c: 07:28Z PASS with gate85 criteria (forks 84); R24-A4 stricter gate 'forks >= 85' never re-logged -> check item (forks metric-ignored, M5).
- 10:40Z BUILD VERIFY (scratch mirror = copy of tools/ + experiments/exp56_x138_verbatim + exp39 base under the session scratchpad; nothing written in experiments/): env = round21 build_env_git_bash (B, KB, C6, CI, N2) + JT/RA92 + D25='--set ILP_DISAPPEARANCE_WEIGHT=2.25', D17='...=1.75', T7='--set SAFE_DIV_SISTER_SYMMETRY_TAU=0.7'.
  Rebuilt byte-identical to repo: exp88a 710a23b9, exp88b 5bcbe5db, exp88c 7b0591ac, exp87a 2e40c57f, exp79a 5f9b265d, exp83c e8f5a8a6, exp86c 9436e809, exp85a e6337843. exp75 rebuild ab621c13 vs repo 4653611e: only the position of the two DIVINS_CAP/FRAME_CAP lines in cell 0 differs (old --set order) -> functionally identical.
  New sha8 (arg order: $B $KB $C6 [JT|RA92|RA90] [D] [T] [N2] [CI]): exp89a_k2cap6_ci_dis225 ddd97ed3; exp89b_k2cap6_ci_tau07 4f2f4ee9; exp89c_k2cap6_ci_dis225_tau07 8c65ebe4; exp89d_k2cap6_dis225_tau07 49574d1d; exp89e_k2cap6_k_dis175 61b59191; exp89f_k2cap6_k_tau07 2092cf43; exp89g_k2cap6_k_ci_dis175 6490121d; exp89h_k2cap6_ra092_ci 39c0452f; exp89i_k2cap6_ra092_ci_dis175 a2a7fc58; exp89j_k2cap6_ra092_dis175 e5dc89f4; exp89k_k2cap6_div04_ra090 59e181b4; exp89l_k2cap6_k_sec_ci cad1d47f; exp89m_k2cap6_sec_ci_dis225 fb6cb18f; exp89n_k2cap6_sec_ci_tau07 98da86b9. (sha includes the folder name in the cell-0 header.)
  Cell diffs vs parent: only the knob line(s) in cell 0 (+ the cell-1 drift-guard value for DISAPPEARANCE; TAU has no guard entry, same as exp88b); _ci vs non-CI adds the coordinject cells (as exp79a vs exp70g).
- tools/runtime_ledger.py EXP_RULES (l.77-84): exp89* falls to r"exp8\d[a-z]*" -> safetail (9.5 h) -> CI members need a safetail_ci rule above l.83.
- Latency arithmetic: probe 51 submit ~12:30-13:00Z + CI L 9.27-9.45 (exp79a) -> 21:45-22:30Z; logged CI band up to 10.9 h -> up to 23:54Z > 23:30Z freeze => night list must not depend on 51.
  Night non-CI at 00:05Z/00:25Z + L 7.0-7.8 -> reads 07:05-08:15Z; CI 00:06Z -> ~09:25-09:35Z (band to 11:00Z). Morning CI 09:30Z -> 18:46-18:57Z at 9.27-9.45 h (20:24Z at 10.9 h); non-CI 11:30Z -> 18:30-19:18Z.
- LB one-lever record vs parent (probes 39-49): '+' 2 (70g +0.002, 79a +0.001) of ~11 -> P(+) ~0.2 per untested arm; P(>=1 of 2) ~0.36; additivity 1 datapoint pending (51).
- 2026-09-28T10:30:46Z final JSON written: research/wf_ideas_v4/round25/scan_hyp_sched29.json (12 findings R25S-1..12)
