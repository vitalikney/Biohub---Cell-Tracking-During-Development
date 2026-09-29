# v_hyp_readscard37 R37-F6 notes (2026-09-29T09:26:21Z)
- Sources read: CONTEXT.md l.4380-4508 (08:19Z rule (a), 08:28Z hold, 08:51Z R36-A2, 09:00Z probe 55 read rule, 09:09Z exp75, 09:19Z exp89r 0.957 DIS ~0); round37/scan_hyp_readscard37.json F2/F3/F6; round36/REPORT.md (MC: exp89t P(>=0.960) 0.09-0.11 when exp89r <= 0.957; private ~0).
- 09:00Z rule: vs exp87a 0.959: >=0.960 -> V_pub; 0.959 -> V_pub only with attributable UP (S0 newest count-matched save before header, S1 right after). F6 restates it; no change proposed -> consistent with R-rules (no post-hoc edit).
- Arithmetic check: P(UP) ~ (P(DIS>0) 0.5 - P(>=0.960) ~0.12) * 0.8 = ~0.30; total switch ~0.40. Loose but only informational.
- pre_exp89t does NOT exist yet (grep: only mention in scan json); it is the F3 17:40Z save. experiments/lb_poll/_lb has S0_0729Z, S1_0753Z, S1_0934Z, S1_1214Z, S1_51, post_exp75. So the action depends on F3; needs a fallback clause (newest count-56 e10 snapshot <= 12:00Z, stale -> conservative, k biased to 0).
- Value: public UP at 0.959 would be ~1e-4-level on one embryo; switch is noise on private (DIS lab -0.0008/+0.0004). Rule pre-registered, so keeping it is correct; finding adds no measurable gain.
- Verdict: not refuted (info item, correct), gain ~0.
