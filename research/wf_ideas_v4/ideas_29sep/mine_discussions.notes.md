# mine_discussions notes (29 Sep run started)

## Pass 1 (read all 45 threads + 24 digests; digests add only 743929/744093/743006 comments + notebook list, no public nb > 0.953)
Raw technique list to check against records:
- 743929 ILP_DIVISION_WEIGHT 1.2->0.4, READMIT 0.965->0.94 (adopted = K)
- 744093 float centroids -0.008 (closed)
- 741242 MOTION_RELINK_TIGHT_UM 5.5 selected by in-notebook 8-video sweep; HOCT deadline 10h, hidden test ~train size
- 743222 in-notebook sweep rewrites submission.csv; hidden rerun scores different 8 videos -> different config may win (trap); DET 0.965 optimum; relink off -; candidate thr 0.48->0.30 =0; zflip TTA =; secondary weight 0.65 -
- 740573 Ultrack ref configs: max_distance 10, max_neighbors 5, appear 0.002 / disappear 0.001 / division 0.001; public: div 1.2, dis 1.5, app 0
- 732103 (Le Quang Canh) asymmetric gate: second daughter arc needs ~2x gate; Hungarian relink destroys forks before safe-div
- 742266 relink cost: NN prob only via learned bonus <=1 um vs 1.8 um median step; feed edge prob into relink cost
- 739570 velocity-projected (EMA) gap closing
- 738217 hengck: reduce nodes by clustering + centroid; ultrack fg/boundary prob to estimate N_est
- 740145 hengck: several pred nodes matched to one GT node, metric only considers first 2
- 740573 hengck: division = bright thin lines; unannotated divisions frequent
- 742942 GT noise: daughter dropped 1 frame later, split coords offset
- 741749 conditional two-model fusion only on uncertain columns; node-count calibration predicted LB best

## Pass 2: check vs records (ideas.json 509 ideas, CONTEXT, FACTS, knobarms_28sep inventory, exp85a source)
Covered / closed (not returned):
- 743929 K (DIV 0.4, READMIT 0.94): adopted (exp85a probe 50 0.958).
- 744093 float centroids: closed; all night CSVs int64 (CONTEXT 16:39Z).
- 741242/743222 tight55 + in-kernel sweep trap: VALIDATOR_ENABLE "0" verified by me in exp85a, 87a, 89p, 89q, 89r, 89s, exp75; tight55 pinned (l.76). HOCT not in x138.
- 743222 DET 0.965 optimum, secondary weight, Z-flip TTA, candidate thr 0.30, relink off: I-309/I-150/DET closed; cell-3 hard-sets.
- 740573 Ultrack penalties: I-175 (S = A + Dis, fork thr Div - A -> APPEARANCE not independent), DIS 2.25 in risk stack, DIV < 0.4 closed.
- 732103 asymmetric daughter gate: I-080 refuted (reach audit); DaughterNet insertion covers orphan daughters.
- 742266 edge prob into relink: I-167 refuted; I-179 bonus 2.5 = P22 0.945 (up arm only).
- 739570 velocity-projected gap closing: I-174 lab neutral; VELOCITY_WEIGHT near-inert (knobarms arms_0 <= 0.03% churn).
- 738217 cluster->centroid: I-134 no-op (NMS). 740145 merges: official metric collapses merges (metrics.py l.89-134).
- 738217/739018 N_est count oracle: estimated_number_of_nodes only in train GT geffs (amanatar reads it in validator only); I-312 node-count rung lb-tested.
- 741749 conditional fusion: already in x138 (low_margin_consensus, F-MOD-30); synthetic pretraining closed.
- 739731 test-time adaptation: I-157 closed (public stack regression, feature drift for V1284/DaughterNet).
- 740573 synchrony prior: I-294 refuted on 199 GT geffs.
- 740573 appearance (bright/thin): I-056 lab-tested.
- 742942 GT-noise mimic: I-276 refuted. 742064 in-sample hold-out: recorded (CONTEXT).
- 743006/735352/743929 finals base rates + JT 'best + closest neighbour': recorded; user agreed hedge pair 16:32Z.
- OUTPUT_EDGE_MAX_UM 14: pre-relink, inert (knobarms inventory).
- 744093 + I-029 z-shift: coordinate class, closed for finals (skeptic R8); 744093 only adds magnitude evidence, no direction.
Residual (returned): LEARNED_BONUS down to code default 0.75 (only up arm tried, on exp29 family); Ultrack max_neighbors cap (no knob, needs patch); density-aware symmetry gate (I-334 deferred, no test proxy).
- 29 Sep run: final JSON written (3 candidates; MD-1 only feasible, borderline under user rule).
