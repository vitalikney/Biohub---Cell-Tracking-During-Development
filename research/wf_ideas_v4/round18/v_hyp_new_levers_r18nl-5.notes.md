# v_hyp_new_levers_r18nl-5 notes (skeptic, round 18)
- 2026-09-27 ~15:30Z: no prior JSON for this task; started.
- I-120 ledger: research/KNOWLEDGE/IDEAS.md l.399 = deferred-after-deadline (1st place no gain; synthetic division gate -0.004 LB; hikaggler gain on his own model only).
- imissher https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743222 (research/wf_ideas_v3/browser_intel.md l.123): secondary adapted on 600 synthetic + 40 real, lr 1e-5, 6 h -> 0.939, logged there as "(-0.006)". His unmodified runs 0.948/0.946; nominal stack 0.947 -> -0.008 is the stack-nominal delta, -0.006..-0.009 depending on reference. Sign unambiguous.
- hikaggler https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/741749 (browser_intel.md l.137): +0.012 is a 24-video HOLD-OUT gain (0.9146 -> 0.9269) vs his own scratch model (0.939 pipeline), not an LB gain; all 2,174 seqs -0.005; synthetic pretraining pushes node count up, nothing on divisions. Freitas CC0 set IS public; only y3uanm's set is non-public (reach0955/r_retrain.json RT-1).
- Our swap record 0/5 on LB (reach0955/v_retrain.json no_go_items). R8 cutoff 27 Sep 12:00Z already passed; no-retraining rule; 80-epoch pretrain + FT does not fit 12 h/T4 or 2 days.
- Verdict: finding holds (stay closed); minor wording fixes only.
