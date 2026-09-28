# v_hyp_prefreeze R28P-11 notes (2026-09-28T19:50:30Z)
- 20:2xZ: no prior v_hyp_prefreeze_r28p-11.json existed; started fresh.
- Feed: experiments/discussions/digest_20260928T1727Z.md = 1 new topic (744093, round(v,3) floats 0.954->0.946), 0 new comments; digest_20260928T1857Z.md = 0 new topics / 0 new comments; E10 FLAG none (best public nb 0.953). https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744093
- scan_browser.json r28-discussion-delta (Chrome recent-comments check 19:36-19:48Z): nothing newer than 743929 Cyrus (already logged). r28-e10-p1-null: no kernel change.
- CONTEXT l.4077-4082 (16:39Z): every candidate dummy CSV int64 z/y/x, 0 non-integer values (exp85a, exp87a, exp89p/q/r, exp75); coordinject writes max(0, round(v)). 744093 is a do-not-do we already satisfy; 'float output' closed.
- Refutation attempt 1: does 744093 + R28-RC-A (lab reproduces truncation loss: -0.0050 lab vs -0.008 LB) open a geometric lever (z shift I-029)? No: RC-A itself keeps it post-deadline (embryo-dependent bias 44b6 +0.15um vs 6bba +0.45um; Canh's constant xyz correction -0.0031 LB; z+0.1 on CI bed -0.00085 R25; outside {K,SEC,DIS 2.25,CI} cap).
- Refutation attempt 2: exploit int-casting scorer via output encoding? Int output == round already; any float encoding is at best identical (probes 32/33 ties by construction) or worse (floor). No lever.
- Refutation attempt 3: any other round-28 finding with a build? All scan_* findings are plan-issue / recheck / new-fact with 'No build'. None disclose a knob. Null stands.
- Nit: exp89l is not yet pushed; it is dry-run reproducible (cad1d47f, scan_hyp_prefreeze (2)) and built/dummied only at probe 51's read in branch A. 'exhausted by built files' should read 'by built or build-ready files'.
