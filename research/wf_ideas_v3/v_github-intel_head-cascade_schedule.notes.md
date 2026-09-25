## 2026-09-25T11:03:53Z schedule skeptic head-cascade: started, read BRIEF
- read ext_x138/DIFF.md: module decoded from exp56 notebook; refine() raises if |shift|>2.00001 um (must be adapted for 2 passes); capture mode saves only 224-d at INTEGER peaks -> pass-2 features need a NEW GPU capture (cannot be derived from the existing 7-sample capture).
- out_full_P.log leak5 OOF: none 1.6861 / public 1.5254 mean, 1.3501 median (199 v, 125,700 pairs) - idea numbers correct. Without x138 train: 179 v, public 1.5375. public residual bias z/y/x +0.40/+0.29/+0.35 um (systematic -> pass 2 plausible). public m7 132,326 < none 132,366.
- x138 probable training set = 20 stems (10 per embryo), NOT 10 as idea says in its protocol; list in out_full_P/report.json x138_probable_train.
- Evaluation needs GT geff: train_coordhead ran on user's Windows PC (data_dir C:\Users\vital\...); container has no data -> eval step is a USER action (or friend A).
- 5070 Ti speed 70-100 s/video is an unmeasured expectation (FRIEND_A_RUN.md step 1 asks friend to send X). Kaggle: pilot 201-214 s/video; 199 videos = 7.2 GPU-h -> ~130 s/video of session time.
- Kaggle max 2 concurrent sessions -> dummy run serialises after 2 capture kernels unless on sasyami.
- 2026-09-25T11:06:29Z final JSON written: refuted=false, feasible=true (with fixes: 20-stem exclusion, new GPU capture, user-run eval, cumulative clip)
