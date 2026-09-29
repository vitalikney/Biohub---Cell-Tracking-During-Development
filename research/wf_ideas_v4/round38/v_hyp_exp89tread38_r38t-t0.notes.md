# v_hyp_exp89tread38_r38t-t0 notes
- 2026-09-29T10:27Z started; no prior json. Verifying T0 vs CONTEXT.md l.4150-4529, runtime_ledger.py, uptest.py, poll.log.
- 10:30Z checks (0 Kaggle calls):
  * T0 56669888 submit 2026-09-29 09:00:17.723 (poll.log l.30274); +10.2 h = 19:12:17Z (22:12 MSK), +10.75 h = 19:45:17Z (22:45 MSK) - arithmetic OK.
  * poll.log last header 10:18:41Z: 56669888 PENDING (task text says 10:08:39Z; both PENDING).
  * tools/runtime_ledger.py: exp89t -> family safetail_ci (regex exp89[abcghilmnort]); first_result_upper = header + RETRY_SLACK_S x failed_attempts; failed_attempts = count of '[empty stdout' + '[ERROR' in the header note; HEADER regex accepts manual '=== <ts> [tag]' lines. Matches T0's L_hi definition.
  * CONTEXT 09:00Z entry: '+' >= 0.960 new V_pub; 0.959 only with attributable UP. 02:02Z (2): running champion conservative; tie orders (2)-(4) only for co-completions. R36-A2 (iii) SEC exception needs a SEC champion: exp87a has no SEC -> n/a. Consistent.
  * GAP RULE v2 (23:34Z freeze (1)) : 10.2-10.75 h '+'/'0u' stand UNPROVEN-ins, '0'/'-' -> '?'; > 10.75 h -> '?'. Since '0'/'-'/'?' all leave exp87a, only the 10.75 h edge can change V_pub - T0 claim correct.
  * round37/report.json R37-A3: S0 pre_exp89t 17:40Z (count 56) or e10_<ts> stale; 56->57 needed, one lag re-save; 'slot-2 file completed in between (56->58) = MASKED'. T0 = consolidation of R37-A3 + 09:00Z; no new rule.
  * Card v5 l.83: SELECTED read-only via competition_submissions(group=SUBMISSION_GROUP_SELECTED); used before (CONTEXT l.2132, l.2155). Expected {56563521, 56563534} = variant (c).
  * GAPS: (1) T0 wording 'count must move 56->57' and 'not a co-completion' hold only if slot 2 stays UNUSED (default; decision 11:50-12:00Z). If exp89s is sent at 12:00Z (read ~19:01-19:12Z) it can land inside exp89t's tail -> co-completion possible, and a 57->58 path appears. R26-A4 (b) (strictly lower display file does not mask) is dropped in this task text vs the scan's G2 cross-ref. (2) No 'other' SELECTED variant (0/1 selected, exp89t already ticked, unknown pair). (3) No explicit 'not terminal by the 19:45:17Z-equivalent header / 20:00Z' line (= '?', exp87a stays).
  * VALUE caveat: a '0u' swap exp87a -> exp89t rests on a sub-0.001 unrounded public move on one embryo (29%); DIS ~0 (dd = 0). Pre-registered at 09:00Z with the user's yes -> not reopened (post-hoc).
