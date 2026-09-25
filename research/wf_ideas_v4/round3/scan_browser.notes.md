# round3 scan_browser notes (25 Sep 2026)
- 22:16 UTC start; no prior round3/scan_browser.json (folder created). Baseline = round2 scan_browser (LB 19:46:38 UTC, 3,908 teams, us #157).

## 22:16 UTC LB (CLI leaderboard --download; scratchpad lb/r3/...2026-09-25T22_16_15.csv; cmp.py vs 19:46:38)
- 3,914 teams (19:46: 3,908). Counts: 0.953 280 (268), 0.954 65 (63), 0.955 40 (38), 0.956 23 (21), 0.957 14 (13); >=0.960 49 (47); >=0.970 6; >=0.953 491 (469).
- Blocks: 0.957 70-83; 0.956 84-106; 0.955 107-146; 0.954 147-211; 0.953 212-491.
- OUR: rank 164 (19:46: 157), 0.954, 37 subs, last 08:33:25. Silver ~196 (5% of 3,914) inside 0.954 block, 15 ranks above its end; we are 32 above the line.
- Top 19 unchanged. Big mover: #20 Syed Asad Ali (syed3000) 0.953 (#417) -> 0.965, 18 subs, last 12:24. LIN mimosa 0.957->0.962 (#31). Mositaku 0.955->0.958, Alfonso Sanchez 0.948->0.957, Miz 0.954->0.957, maesaer 0.954->0.956, Deep Thought 0.953->0.956, datnt114 0.953->0.955, Satwik 0.954->0.955, darkvector4 0.938->0.955; into 0.954: Gaiar Baimuratov, BobtheBot369 (0.945), Kita Renji, ssaakura (NEW, 2 subs), Reuben Ernser.
- 16 teams into 0.953 again at the block END (ranks 460-475, + 481, 486): last subs 13:14-15:11 (one 21:01) = late x138 copies.

## 22:20-22:30 UTC CLI code + movers
- CLI kernels list --competition --sort-by dateRun: newest still raunakdey07/biohub-harmonic-fusion-v3 (25 Sep 09:09) -> NO public notebook run since round 1/2. scoreDescending: nothing > 0.953 (top 4 = raunakdey07, amanatar, kunaldesale2408, anvithpothula x138).
- Movers' public code (kernels list --user / datasets list --user): syed3000 (Syed Asad Ali, 0.953->0.965 #20) has 3 kernels 'v12b our best private build', 'v17 the private build we SUBMITTED', 'v19 our best public build' (7-8 Sep) but metadata competition_sources = ai-agent-security-multi-step-tool-attacks (OTHER competition). alfonso1799 biohub notebooks last run 18 Sep (V50, pre-x138, known family). deepakjnath/biohub-climb-notes = 18 Aug (old). kksky9k datasets biohub-divaware-* 16-17 Sep (old). linmimosa, achenyyc, versavice, darkvector4, sha1ng, valtrix, ssaakura team, reubenernser: nothing public. -> nothing to pull.

## 22:20 UTC browser (own tab 1196279881 in a fresh MCP group)
- Discussion sort=published https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion?sort=published : newest listed = imissher 'Eight leaderboard experiments...' (13 h), SamoraDC (20 h). Topic 743006 'Beginner question: How do Public/Private splits usually work in biological datasets?' (Rishavendra Sharma, posted a day ago) shows activity '24 minutes ago': its 1 comment is by Gabriel (#1, 0.975): "I am also curious about the answer to this question." -> no information.
- Discussion sort=recent-comments: only change vs round 2 = topic 743006 (Gabriel's one-line comment above). No other new topic or comment; pinned host topics unchanged (9d / 25d / 2mo) -> no announcement.
- Code tab 'Recently Created' (https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/code?sortBy=dateCreated): newest unpinned = 'Robust Cell Tracking ... via Chan.' 2d ago; nothing new.
- x138 https://www.kaggle.com/code/anvithpothula/biohub-0-953-lb-runnable-with-public-datasets : 'Version 1 of 1', Comments (3), 183 votes, 260 copies (258 at 19:50), 1,908 views (1,873).
- Overview: Entry Deadline September 22, 2026; Final Submission Deadline September 29, 2026; 'CPU Notebook <= 12 hours run-time', 'GPU Notebook <= 12 hours run-time', internet disabled, external data allowed -> unchanged.
- Tab closed 22:27 UTC (group auto-removed).
- CLI: competitions files creationDate 2026-06-26 (unchanged). datasets --search biohub --sort-by updated: only new = kragglenote2forwork/biohub-sub-cache2 (20:06 UTC, size 0, 1 download) = empty, irrelevant. models list --search biohub: no new biohub model.
- Nothing pulled into experiments/ext_* this round.
- 22:31 UTC: final JSON written to research/wf_ideas_v4/round3/scan_browser.json.
- 22:31 UTC: final JSON written to research/wf_ideas_v4/round3/scan_browser.json.
