# h_github-intel notes
- 2026-09-25T10:41:47Z start: read BRIEF
- 11:05 GitHub MCP search_repositories "biohub cell tracking" -> 91 repos, "biohub kaggle" -> 52. Candidates by recency/description:
  kito2718 (updated 25 Sep), JunhaoLiXD, pathik1511, Caffeinated-Code, alvaromendizabal (0.947 repro + error analysis),
  davidlueng986-alt (auto R&D loop), Kai-Gowers v2, m9h/biohub-starter (embryo-disjoint validation), sota1111 claude/gpt,
  SarvarAi (0.895), tuannm3812 (0.817), tarunn613 (Cellpose-SAM + ILP), Agnuxo1 st-flow, Md-Ali-Azad, vietnq130593.
- 11:15 api.github.com and github.com HTML/codeload are 403 via proxy; GitHub MCP get_file_contents only allows our repo; MCP search_code works across GitHub; raw.githubusercontent.com works (200).
- search_code "estimated_number_of_nodes" -> 655 hits; new repos: matheuspf/cell-tracking (big agent repo), kevzho/kaggle-comps, naveenlx111-svg/Biohub, tossowski/BioHub (lb897), dappalumbo91/Wavegazer-Net, seshurajup/myclew, barbo0909, Abhirup-Choudhury, Ndabuddah, phucthaiv02, KHHH2312/vibecode, tom99763/celltrack-studio.
- matheuspf/cell-tracking docs/code-only-planning-20260915.md: best LOCAL 0.9352 (C4_m6, 199 clips, in-sample public detector); P0 0.9349; divisions 30TP/92FP/121FN; links 123,133TP/4,968FP/5,750FN; center recall 98.14%; 1,765 of 2,482 unmatched annots have a raw candidate nearby but no final center. No LB > 0.953.
- 11:25 seshurajup/myclew top40 ideas (Jul 5, pre-0.9 era) - obsolete. KHHH2312/vibecode grok-handoff: 0.955 was pre-17-Jul metric hack (FORKS) - irrelevant.
- JunhaoLiXD/Biohub_Cell_Tracking README: reproduced public 0.941 (LB 0.941) and 0.944; motion EMA alpha 0.4 local +0.0028 -> LB unchanged (0.933 earlier). Nothing > 0.953.
- kito2718: Japanese StarDist+btrack plan, CV 0.46 -> target; nothing usable.
- alvaromendizabal: 0.947 repro (Harmonic Fusion); 557 association features, synthetic div models, sparse-real div FT, all rejected by exact metric; active: fine-tune linker (no score). Portfolio only, no code.
- Kai-Gowers v2 reports: retrained pack recipe (DDP, 179 vols, 400 ep): LB 0.927 vs shipped 0.942; local held-out gap = det recall 96.7 vs 98.3 %; ep150 == ep385; _best > _last by 0.005-0.011; blend adds nothing w/ own seeds; DeepCenter no effect; PP +0.005 (div term). (reports/2026-09-16-ddp-score-sweep.md, 2026-09-17-leaderboard-0.927...)
