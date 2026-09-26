# round10 scan_browser notes (2026-09-26T15:16:19Z)
- started; no prior round10 scan_browser.json. Baseline = round9 (LB 12:46:30Z, rank 204/3928).
- 15:16:37Z LB CLI download (session scratchpad lb/r10/...2026-09-26T15_16_37.csv) vs round9 base 12:47:44 CSV (lb/r10/base_124744.csv; cmp10.py).
  3,930 teams (+2). 0.953 345 (335), 0.954 96 (93), 0.955 57 (55), 0.956 33 (30), 0.957 18 (20), 0.958 11 (9), 0.959 11 (10), >=0.96 67 (67), >=0.97 7 (7), >=0.953 638 (619, +19 in 2.5 h).
  Blocks: 0.957 90-107, 0.956 108-140, 0.955 141-197, 0.954 198-293, 0.953 294-638.
  OUR rank 210 (204), 0.954, 40 subs, 13th of 96 in 0.954 block. Silver 5% of 3930 = 196.5 -> 14 ranks below public silver line (8 in r9).
  37 changed; 154 teams with new subs. Top 20 unchanged in order; Tang 0.970->0.971 (#7 kept).
  Movers: 牛・狐・鳥 0.953->0.958 (#619->#89, sub 10:06Z); Efthimios 0.947->0.956 (#813->#139); wodedaodun 0.953->0.956 (#524->#118); Oleksandr Parfionov 0.957->0.959; Guest21222 0.957->0.958; Suuuiiii4 0.955->0.956; Jiacheng Zhao 0.953->0.955; MOHAMMADJAFAR ZAMANI 0.954->0.955; Pawan Rama Mali 0.953->0.955 (#196).
  New 0.954 entrants all BELOW us: Luon may Man #229, honjousetuna #263, natsu #268, insuperabilehart #292 (0.945->). The 6 extra teams above us come from 0.955+ growth (0.955 block now ends at 197 vs 191).
  17 more x138 copies to exactly 0.953 at #608-624 (subs 06:11-08:53Z; 10th window).
  Latest subs: stochar 0.954 #254 (14:27Z), Abdelghani Charouiti 0.954 #255 (14:31Z), Takahiro Saito 0.953 (14:09Z).
- 15:18Z CLI kernels --competition dateRun: NEW run amanatar/optimized-biohub-max-score lastRunTime 26 Sep 13:18:11Z (was 25 Sep 01:59Z), 58 votes (53); now #2 in scoreDescending (between HF v3 and kunaldesale). Earlier pull: experiments/ext_optimized-biohub-max-score (25 Sep; latest version then ERRORED). Need page score -> browser. Others unchanged (sarveshchhetri 12:40Z known). dateCreated unchanged.
  Datasets: NEW/updated haideptry/biohub-cpu-offline-artifacts-v1 (13:44Z, 47 KB, 15 dl); kssrikar4/biohub-model updated 12:53Z (110 MB now, 30 dl). Data files creationDate 2026-06-26 (unchanged). competitions list userRank 210, teamCount 3927.
- 15:19Z browser (own tab 1196279911, new group 1428895492) https://www.kaggle.com/code/amanatar/optimized-biohub-max-score : 'Version 1 of 5', 'Public Score 0.910', 'Best Score 0.953 V4', 58 votes, 69 copies; page shows last successful run (V1). CLI kernels status = RUNNING (new version started 13:18Z, unscored).
  Pulled latest source -> experiments/ext_optimized-biohub-max-score/v10_2026-09-26/ (+NOTES.md). v10 = v9 + 5 default-OFF levers (count_oracle, div_lineage, gap_predict, stitch, margin_repair) chosen by validator-gated train-stem sweep; VALIDATOR_ENABLE=1 -> P4b(d) fails; closed families. Not portable.
- ~15:19Z discussion?sort=recent-comments: NO new topic, NO new comment. 743006 'Last comment 5h ago by Rishavendra Sharma' (known r9, no host reply); 742942 'Last comment 6h ago by Himanish Goel' (known). Pinned unchanged (Workshop 10d, Discord 1mo, Welcome 2mo). Header '3 DAYS TO GO'.
- ~15:19Z /overview: 13,475 Entrants, 4,489 Participants, 3,927 Teams, 87,311 Submissions (+246 since 12:49Z ~= 98/h); 'September 29, 2026' '- Final Submission Deadline.'; 'CPU Notebook <= 12 hours run-time' / 'GPU ... <= 12 hours run-time' unchanged. No announcement.
- ~15:19Z x138 page: '199 votes', '280 copies' (277), 'Version 1 of 1', 'Comments (3)', 0.953. Unchanged except +3 copies. Tab closed (group auto-removed).
- 15:19Z dataset haideptry/biohub-cpu-offline-artifacts-v1 (13:44Z, 8 small files: optuna_1200_trials.csv, best_tracking_params_6d.json, scip_oracle_summary.json...; no description) = param-tuning artifacts; owner team prairieee (haideptry) at 0.953 #328 -> irrelevant, not pulled. haideptry kernels 'The 2965 Master Hybrid Engine' (13:54Z, 36 votes) not attached to the competition list (not in --competition lists) -> no score shown; irrelevant.
- E10 NOT triggered (no public heir >= 0.956; amanatar v10 unscored & would fail P4b(d)). Writing scan_browser.json 15:20Z.
- 15:20Z scan_browser.json written
