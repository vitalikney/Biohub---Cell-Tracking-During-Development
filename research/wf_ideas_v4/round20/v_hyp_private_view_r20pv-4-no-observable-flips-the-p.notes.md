# v_hyp_private_view r20pv-4 notes (skeptic, round 20)
- 2026-09-27T20:28:12Z start; no prior json/notes for this task
- source: research/wf_ideas_v4/round20/scan_hyp_private_view.json finding r20pv-4 (+ notes)
- LB recount from experiments/e10_watch/20260927T1943Z.txt and T2002Z.txt (CSV rows): >=0.954 = 402, not 400 (>=0.960 = 88, not 86); 0.954 = 115; 0.953 = 404 (19:43Z), 406 (20:02Z). Our row #163 at 0.956. Small count slip; no effect on the conclusion.
- Structural point: N954 can only grow (best public scores never go down), so RGROW=0 already is the most A-friendly field an observable can show. No reading at 29 Sep 17-18Z can fall below the stalled case.
- Round 16 r16fc-5 (round16/scan_hyp_forecast_update.json) said 'N954 < ~450 -> the twin hedge regains up to ~0.05'. N954 is already 402, and that hedge is about #38 vs nothing, not A vs P1.
- Re-ran the MC (scratchpad r20/mc.py, seeds 11/23) at RGROW=0,0 and 0,0.2. P1 {exp70g,#37} minus A {#37,#38}:
  - base: bronze +0.02..+0.05, silver +0.22..+0.23
  - overfit: bronze -0.013..-0.017, silver +0.17..+0.18 (P_Xplus_bronze 0.91-1.0; X+ rank median 355-372)
  - qpub0: bronze -0.016..+0.007, silver +0.12
  - qpub0_pes: bronze -0.023..+0.007, silver +0.12
  - inspes_qlo: bronze +0.00..+0.03, silver +0.17
  So the finding's bronze band '-0.01..+0.004' is too narrow. In a stalled field A leads by up to ~0.02 in overfit or lab-adverse worlds. That is at seed-noise size (~0.015 between seeds) and inside model error. The silver edge of +0.12..+0.23 holds. The claim 'no observable flips the pick' survives: the worst case is a ~0.02 bronze tie against a >= 0.12 silver loss.
- The finding is information only: no mechanism, no R8 or R1-R10 issue, no runtime, no slot. The N954 log is already inside the scheduled watcher snapshot (0 extra API).
- 2026-09-27T20:30:33Z final JSON written (refuted=false, band corrected)
