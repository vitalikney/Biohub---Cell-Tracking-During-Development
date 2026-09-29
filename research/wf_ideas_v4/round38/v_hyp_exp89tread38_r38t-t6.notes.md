# v_hyp_exp89tread38_r38t-t6 notes (skeptic, R38T-T6 ERROR row)
- 2026-09-29T10:27Z start; no prior json. 0 Kaggle calls (local files only).
- Source row: round38/scan_hyp_exp89tread38.json R38T-T6 (+ T4 variants a/b/c).
- CONTEXT 09:00Z (l.~4458-4470): exp89t 56669888 T0 09:00:17Z; read rule '+' >=0.960 new V_pub; 0.959 only with UP; below -> no change. ERROR has no display -> no change (V_pub exp87a 56640366).
- poll.log header 10:18:41Z: 56669888 still PENDING (no early ERROR so far; dummy v1 PASS 08:59Z).
- CI L lower bound 8.88 h (exp75 probe 53, l.4473); typical CI L 9.28-9.48 h (exp89t entry). Resubmit at t: typical read t+9.3..9.5 h. For a read by ~19:45Z (tick time 20:00Z) t <= ~10:17-10:28Z -> already past at 10:27Z. Lower-bound edge 11:07Z (row's number) is correct but loose; the real edge is earlier.
- Possible counter-rule checked: R13-A1 (5) (l.2824-2826) 'unchanged resubmit of an ERRORed finals-relevant file (ERROR < 10 h latency)' ranks above empty for slots 27-29 Sep; W2 rule l.3160 'ERRORed single gets one unchanged resubmit if ERROR latency < 10 h and slot would stay empty'. Does NOT bind here: resubmit cannot read before the 20:00Z tick on typical L, and user holds slot 2 (08:28Z) -> their call; expected gain ~0 (DIS ~0 from exp89r 09:19Z). Row should cite this so it is not read as contradicting R13-A1 (5).
- Private risk: exp87a already COMPLETE -> its private score was computed in the same run; an exp89t ERROR (even a timeout) is no CI runtime risk for V_pub. Log ERROR latency only (R21RK-5/6 precedent l.3331).
- Verdict: not refuted (ops row correct, conservative); small text fixes.
- 10:31Z JSON written (refuted=false)
