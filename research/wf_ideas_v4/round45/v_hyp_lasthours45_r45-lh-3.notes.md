# R45-LH-3 verify notes (2026-09-29T18:30:39Z)
- verified: post_exp75 zip member = biohub-cell-tracking-during-development-publicleaderboard-2026-09-29T09:08:57.csv, 3991 rows; all 6 saved zips carry 'publicleaderboard' in the member name (no private sample exists to confirm the 'private' naming).
- R41-A7 (round41/report.json) = 00:07Z uptest save + read_selected + submissions list + stop pollers + commit. PRIVATE-READ v2 (d) CONTEXT l.2587-2593 already has hourly competition_submissions(page_size=100) from 00:15Z + board check.
- 18:32Z: post_exp75 ours #140 0.959, N 3991 -> lines 17/199/399 (floor). CONTEXT R44-A3: Chrome 20:15 MSK #154 of 4 005.
- lb_poll.py polls `kaggle competitions submissions -v` (last column privateScore, empty now) every 600 s; R41-A7 stops it at 00:07Z.
- kagglesdk 2.2.4 competition_api_service.py: ApiGetLeaderboardRequest.override_public doc "By default we return the private leaderboard if it's available, otherwise the public LB"; ApiDownloadLeaderboardRequest has only competition_name (no public/private switch; behaviour after reveal undocumented). All 6 local zips are 'publicleaderboard'-named; the 'private' name test is unverified.
- submissions CLI supports --page-size (max 200).
- Verdict: not refuted (0 score risk, no submit/tick, light load), fix: primary flip detector = submissions list privateScore non-empty (direct, binary); LB download only on flip; drop test vs final_0007Z (fallback post_exp75) by TeamId; medal lines approximate on N at read time; laptop on battery since 17:43Z -> overnight timers may stall (fail-soft).
