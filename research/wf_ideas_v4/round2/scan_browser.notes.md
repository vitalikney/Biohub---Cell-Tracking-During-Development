# round2 scan_browser notes (25 Sep 2026)
- 19:47 UTC start; no prior scan_browser.json in round2 (folder created). Baseline = round-1 intel_browser (LB 16:52 UTC; 18:08 UTC intel in CONTEXT: #151/3,905).

## 19:46 UTC LB (CLI leaderboard --download; scratchpad lb/new/...2026-09-25T19_46_38.csv; compared with 18:08:23 and 16:52:13 snapshots)
- 3,908 teams (18:08: 3,905). Counts: 0.953 268 (261), 0.954 63 (62), 0.955 38 (35), 0.956 21 (21), 0.957 13 (12); >=0.960 47 (47); >=0.970 6; >=0.953 469 (456).
- Blocks: 0.957 67-79; 0.956 80-100; 0.955 101-138; 0.954 139-201; 0.953 202-469.
- OUR: rank 157 (18:08: 151; 16:52: 149), 0.954, 37 subs, last 08:33:25. 44 teams below us in the 0.954 block (31 with last sub before ours).
- Silver ~rank 195 (5% of 3,908) now lies INSIDE the 0.954 block (139-201), 6 ranks above its end; bronze ~391 inside 0.953.
- Top 22 unchanged (Gabriel/Sergio 0.975, yu4u 0.973 ...). Only top-25 mover: #23 'que la cuenten como quieran' (germanjurado1) 0.963->0.964 (0.958 at 16:52).
- Movers since 18:08 (all LastSubmission 11:46-16:33 UTC = hidden-rerun latency, so these are late-scored subs): r3takahashi 0.953->0.958 (#61, 120 subs); andrei6184 0.947->0.957 (#78); t-enstar 0.950->0.955; 4kut4 0.949->0.955; Korokke3 0.954->0.955; Taisei, Euphor_M 0.953->0.954; 10 teams 0.947/0.948/0.952 -> 0.953 placed at ranks 445-469 (block END = late x138 copies).
- Named: Anvith Pothula 0.956 #85 (no new sub since 24 Sep 06:57); y3uanm 0.956 #84; Justin CH123 0.956 #91; easonyanyan 0.954 #152; Kunal Desale 0.953 #238 (36th of 268 in block); Aman Atar 0.953 #402; Corwin 0.965 #17 (unchanged).

## 19:50-20:05 UTC browser (own tab, closed at the end) + CLI
- Discussions sort=published and sort=recent-comments (https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion): NO new topic and NO new comment since round 1 (newest topic still imissher "Eight leaderboard experiments on the public 0.947 stack" posted 11h ago, 0 comments; SamoraDC "Winner deliverables..." 17h; newest comment "errors in annotated ground truth" last by Satwik 1d ago). Pinned topics unchanged (last comments 9d/25d/2mo) -> no host announcement.
- Code: CLI kernels list --competition --sort-by dateRun: newest still raunakdey07/biohub-harmonic-fusion-v3 (25 Sep 09:09) -> no public notebook run since round 1. Browser Code tab 'Recently Created': newest unpinned = 2 days old. Score sort: nothing > 0.953.
- x138 page https://www.kaggle.com/code/anvithpothula/biohub-0-953-lb-runnable-with-public-datasets : still "Version 1 of 1", 0.953, 183 votes, Comments (3), Copy & Edit 258 (was 256), 1,873 views.
- Overview: timeline unchanged (Entry/Team merger 22 Sep 2026, Final Submission 29 Sep 2026); Code Requirements "GPU Notebook <= 12 hours run-time" unchanged; sidebar "Awards Points & Medals".
- Data: CLI competitions files creationDate 2026-06-26 (unchanged).
- Datasets search 'biohub' sorted by updated: nothing new since round 1 except dariushafshar/kaggle-competition-leaderboard-intelligence (15:11, generic LB data, not code). 
- Movers' public code: r3takahashi, andrei6184, tstustatama (t-enstar), naokwmr (4kut4), korokke3, germanjurado1, taikiara, euphor, laughingmen, willzhaoo: no biohub kernels, no datasets -> nothing to pull. No experiments/ext_ folder created this round.
- 20:05 UTC: final JSON written to research/wf_ideas_v4/round2/scan_browser.json.
