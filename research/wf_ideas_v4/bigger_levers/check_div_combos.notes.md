# check_div_combos notes (skeptic pass on prep_div_combos, 28 Sep division rungs exp73a..v)

- 2026-09-27 11:36Z builder drift: tools/build_probe_kernel.py is now sha256 0ec0fd1b5e644539... (prep JSON says
  df0fe7c7; another agent edited it again, +354/-18 vs HEAD). Build script prep_div_combos_build.sh = d2afdfb7 (matches).
- 11:37Z REBUILD: ran the build script with every line redirected to --out-dir _chk_div73/<name> (same names, so same
  slugs/ids). All 20 notebooks byte-identical to experiments/exp73*/ (sha256 match on all 20, kernel-metadata.json
  identical on all 20). K2 rebuilt with the current builder into _chk_div73/k2 -> 1f1ddb6d63b47f54... = finals file.
  Temporary folder deleted afterwards (11:45Z).
- 11:38Z CELL DIFF vs K2 (exp58_x138_safe_lowref): singles a..e differ only in cell 0; f..v differ in cells 0 and 7
  (forkmid patch). vs exp70b_k2_fm45 (dummied + scored K2+forkmid) exp73v differs only in cell 0: header name,
  DIVINS_CAP 4->16, FRAME_CAP 1->2, THRESH 0.4->0.2, + DEEPCENTER_SAFE_DIV_THRESHOLD 0.15 (appended after the base 0.25,
  read once in cell 2 via os.environ; not an x138 hard-set knob; exp70d DC0.30 moved the public score, so it takes effect).
  Metadata: private, internet off, T4, docker 37c64f7d, same 5 datasets as K2.
- 11:40Z DUMMY ANATOMY (_dl logs, 4 dummy clips), safe-division 'added' per clip: K2 35/6/5/17 = 63; DC0.30 31/0/5/7 = 43
  (-20, public -0.005); DC0.225 37/13/5/21 = 76; DC0.20 37/17/5/25 = 84; cap_skipped = 0 everywhere (global/frame frac caps
  do not bind), so DC 0.15 will add more forks (no dummy number yet; expect > 84 safe forks). Nodes are unchanged by
  insertion (it adds edges only: orphan v gets parent u, or a steal re-links v from w); node-count bonus not at risk.
- RUNTIME: insertion scores every candidate triple regardless of cap/threshold (cap/threshold only select), DC threshold is
  a gate, forkmid already ran in exp70b (dummy timings 82.6/124/21.9/298 s vs K2 81.6/119.8/20.4/287 s). Expected hidden
  runtime = K2's clean 7.54 h (+ a few min). Safetail deadlines (divins 28800 s, repair 34200 s) unchanged. Low risk.
- SCORE RISK: steal cap = floor(cap/2): I3 up to 6 steals/video, I4 up to 8 (K2: 2). Each steal removes an existing
  edge w->v (edge_prob < 0.3) -> edge-term risk on top of the division term. CONTEXT lab: division-add break-even precision
  q* = J/(1+J) = 0.161 on K2; orphan-attach precision 3.4%; ins_cap6 marginal forks 0 TP / 4 FP. Public is the only
  evidence for 'more divisions' (DC0.30 -0.005; insertion +0.001). DC side is the credible lever (DeepCenter-ranked,
  public-sign-confirmed); cap/threshold side is lab-negative and waits on probe 45 (cap 6).
- 11:39Z GPU: exp71-secft-all RUNNING, exp70n-k2-thr03 QUEUED -> no free lane, nothing pushed. exp70q/exp70r are not on
  Kaggle yet (kernels.get denied = never pushed): today's last-slot dummy also needs a lane before its submit.
- 11:41Z pytest: 454 passed, 1 skipped (python -m pytest -q tests). Finals: exp58 1f1ddb6d, exp58n clean in git.
- SCHEDULE: R8 cap = last ladder submit 29 Sep 02:00Z (CONTEXT 2521-2522; lifted only for exp72 and E10 v3). The
  '29 Sep slots to push the winner' means 00:00-02:00Z 29 Sep only, unless the user lifts R8 for these rungs.
- NAMING: the builder's E10 v3 succ base names SI kernels exp73[x]_si_<author>; our rungs use exp73a..v_k2_*. Slugs do not
  collide, but ledger lines like 'exp73a' become ambiguous. Always quote the full name.
- VERDICT 11:45Z: build GO (reproducible, finals intact, runtime ~K2). Fixes listed in check_div_combos.json.
