# scan_hyp_morning_brief notes (round 22)

- 2026-09-28 01:03Z start. No prior scan_hyp_morning_brief.json. Read-only work; files written: this notes file + the JSON only.
- Sources read: CONTEXT.md l.2599-2760 (RESUME 26 Sep 22:46Z, still the last one), l.3150-3380 (v2 (6)-(10), 45/46 reads,
  READ TABLE v3, N2 prereg, R8 COVERAGE 00:00Z, R21-A3 gates, W1 submits, W2 TABLE v4, W4 AMEND 2); round21/REPORT.md;
  round20+21 report.json actionable R20-A9, R20-A12, R21-A9, R21-A10, R21-A11; IDEAS.md header + tail (curation 21).
- W1 refs (experiments/lb_poll/poll.log l.18689-18754): 47 exp78b 56623073 00:06:09Z; 48 exp79a 56623105 00:06:33Z;
  49 exp78a 56624341 00:50:37Z; all PENDING at last header.
- Expected terminal: 47 ~07:28-08:00Z (K2 L 7.36-7.9 h); 49 ~08:12-08:45Z; 48 (CI) ~09:30-10:42Z (model 9.4-10.6 h).
  => at 08:00-09:30Z the brief can carry 47 (+ probably 49), NOT 48. W2a (08:45-10:00Z) needs both DIV reads.
- grep CONTEXT for 'FINALS CARD' / R20-A9 / R21-A9 text: 0 hits -> finals card lines NOT landed (deadline was before the
  first W1 terminal header ~07:30Z). IDEAS curation 21 also says R20-A9 NOT logged. The brief's section 3 quotes them.
- T_last inconsistency: v2 (7) CI = T_last - 2.4 h = ~08:00Z (R20-A12 text 'CI до ~08:00Z'); W4 AMEND 2 (5) says CI T_last ~07:30Z.
  Use the stricter 07:30Z in the message.
- Lift arithmetic: 29 Sep 5 slots; W4 <= 4 planned + 1 held for E10; after-02:00Z content restricted to non-CI twin of a '+' FULL,
  one DIV step under S3, E10 copy -> <= 2 extra files, submitted after W4 reads (~07:40-09:30Z), read by ~18:15Z (<19:00Z FINALS READ).
  P(an extra file raises V_pub display) ~0.15-0.35 (week record: 1 clear step (45) in ~10 knob probes 39-46);
  medal value <= 0.06 bronze spread among cap-family F1s (R21-A9 (iii)) x 0.35 = <= ~0.02 bronze; private ~0.
- Q3: R20-A12 says do not ask again unless a SEC file tops the display -> passive default line only.
- E10 after 02:00Z: W4 AMEND 2 (5) already allows under E10 v3 until ~10:00Z; R21-A10 asks confirmation, default YES.
- Nothing in this scan is a new mechanism; nothing reaches R8 (27 Sep 12:00Z passed).
- 01:12Z JSON written (9 findings: template, fill rules, finals-card blocker, send timing, lift arithmetic, CI T_last mismatch, RESUME POINT, Q3/E10 defaults, nothing reaches R8).
