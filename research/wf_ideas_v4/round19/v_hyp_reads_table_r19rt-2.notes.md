# v_hyp_reads_table_r19rt-2 notes (skeptic, value + feasibility)
- 2026-09-27 ~17:55Z: no prior JSON for this task; started.
- R19RT-2 is a sub-part of R19RT-1 (scan_hyp_reads_table.json, (2)(a) S1 rule and (2)(c) BLIND).
- Existing rule R13-A1 (2) (CONTEXT ~L2678-2690): FRESHNESS primary = SubmissionCount == base + refs COMPLETE; LastSubmissionDate secondary.
- TEST of guard (a) on our own history (experiments/lb_poll/ladder_watch/*/ CSV, our row TeamId 16810638):
  - S0 01:47Z: LSD 2026-09-26 00:02:18, count 40
  - 04:13Z: LSD 21:17:47 (exp70a 56589065 submit), count 41 (a scored 04:20 header)
  - 04:31Z: LSD 21:17:47 STILL, count 42 -> exp70e 56589025 (submitted 21:15:23, EARLIER than a) had scored (poll header 04:40:05Z)
  - 04:56Z: LSD 21:38:33 (exp70d), count 43
  - 07:37Z: LSD 00:05:50 (exp70b), count 44; 13:13Z: LSD 05:28:22, count 46
  => LastSubmissionDate = MAX submit time over our SCORED files, not the submit time of the most recently scored file.
  => Guard (a) "S1 valid only if LSD == ref submit time" would have made the valid 04:31Z S1 for exp70e never valid.
- 28 Sep W1 (R19RT-1 (3)): CI 00:05Z, SEC 00:10Z, DIV 00:45Z; CI runs ~2 h longer (exp75 dummy CI stage +443 s/4 videos, L ~9.6-9.8 h)
  -> SEC (submitted later) very likely scores BEFORE CI -> LSD = 00:10 forever -> CI's S1 never 'valid' under guard (a) -> the CI read (main hope) stalls. Guard (a) actively harmful.
- Guard (b) BLIND: logic right (k=0 => within-block gain invisible), but k history from e10_watch 'our team' lines: 11,11,12,14,15,16,7,5,4,4,5,5,5,5,5,5 (position-1); never near 0. P(k=0 at a 28 Sep S0) small (<~5%). Also it is only the extreme of the general low-power issue (gap to next team above unknown); R19RT-1 (2)(d) already says N4 ~ delta <= ~1e-5.
- Feasibility of logging: E10 snapshot already stores rows >= 0.953 incl. LSD and SubmissionCount; no extra API call. Fine.
- 2026-09-27 17:58Z: final JSON written (refuted=true; fix = SubmissionCount primary, LSD = max scored submit time).
