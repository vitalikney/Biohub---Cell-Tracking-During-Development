# scan_hypotheses round3 notes (started 2026-09-25T22:15:47Z)

## 2026-09-25T22:16:28Z start
- Read CONTEXT tail l.1540-1984 (R1-R10, f, L, f2, exp60 T9 read 20:35, round2 closure 20:55, f2 OK 22:06), FINAL_REPORT_v4.md, round2/report.json + scan_hypotheses.json (R2S-1..8), KNOWLEDGE/INDEX.md.
- round2/REPORT.md does not exist (harness blocked it); text is inside round2/report.json plan_issues.


## 2026-09-25T22:18:01Z (b) insertion by density quartile (exp60 results.json per-clip rows, official summarise; scratchpad quart.py)
- quartile edges nodes/frame 83.7/160.7/258.8 (14 clips each). ins35 delta by quartile: Q0 +0.0246 (div 4/1/21 -> 11/3/14), Q1 +0.0028 (6/3/18 -> 7/4/17), Q2 -0.0005 (3/6/20 -> 3/7/20), Q3 +0.0019 (3/15/24 -> 4/17/23). ALL +0.0065 (16/25/83 -> 25/31/74).
- cap_video=4 binds on most clips (added=4 in ~40/56): insertion count is density-independent; precision is not: sparse half 8 TP/3 FP, dense half 1 TP/3 FP (in-sample upper bound, L5).
- dense half still above lab break-even q*=J/(1+J)~0.11 (1/4=0.25) -> no density gate warranted; nosteal0 identical to ins35 in dense half.


## 2026-09-25T22:23:22Z (a) x138 tail structural audit (scratchpad audit.py, 56 lab final graphs)
- isolated nodes 0, >2 children 0, multi-parent 0, dt!=1 edges 0 on all 56 clips; near-duplicate node pairs (<2 um, same frame, writer coords) 0-14/clip (sum ~190 of ~1.1 M nodes), exact duplicates 2 -> a dedupe/structure fix touches ~0.02% of nodes: EV ~0. CLOSE 'deterministic tail bug fix' class.
- total_node_ratio spans -0.64..+0.42; 44b6 heavily under-predicted (retention-guard fallback clips 44b6_9be80b04 -0.55, 44b6_e28840c6 -0.64). Known node-bonus effect, no action.
- ILP max 79.4 s (6bba_05db0fb1 dummy, 76k cand nodes), lab max 67.5 s (98k) vs timeout 1200 s -> 15x margin; no ILP-timeout nondeterminism risk.
## 2026-09-25T22:23:22Z (a) retention-guard flicker diagnostic (scratchpad flicker.py; retention_guard_*.jsonl use_primary per frame x GT edges)
- GT-edge FN rate by frame pair: all-blend clips 4.16% (24,572 edges); mixed clips: blend-blend 3.17% (12,156), prim-prim 10.71% (1,960), switch 6.05% (876); all-prim clips 6.43% (529).
- switch pairs sit between the two modes (no boundary penalty); prim frames are hard frames (selection effect). No hysteresis mechanism warranted. CLOSED.


## 2026-09-25T22:28:25Z (a) lab error decomposition (scratchpad bridge.py, 56 clips, official matching)
- link-miss GT-edge FN with both endpoints matched: 871 = 730 'pred parent linked to another child' (swap) + 141 'pred end without child'. With flicker.py: total FN 1,705 of 40,093 GT edges, node-miss 834 (49%).
- mutual-NN pred end(t) -> pred start(t+1) pairs within 2/3/4/5/7 um: 0 on all 56 clips (x138 relink/gapfill already bridges them) -> no bridging lever.
- => remaining edge-FN mass = detector misses + edge-model swaps; both need retraining (R9). Tail search exhausted.
## 2026-09-25T22:28:25Z (a) K2 safety checks
- lowrefine: v1284_coordinate_refinement.py (extracted from experiments/exp58_x138_safe_lowref nb) has bounded() head shift, np.clip to volume and an isfinite + 2 um max-shift check -> no NaN/out-of-volume path; plus the patch's shape check and try/except.
- GPU phase (launch -> first repair start): exp56 626 s, exp57b 545, exp58t 543, K2 550, twin 555 -> lowrefine GPU cost ~0. Repair sum: twin 219 s, K2 509 s (insertion).
## 2026-09-25T22:28:25Z (c) Kaggle CLI (read-only)
- kernels list --competition ... --sort-by dateRun: newest public run still raunakdey07/biohub-harmonic-fusion-v3 2026-09-25 09:09 UTC; nothing new.
- LB CSV 2026-09-25T22:23:38 (scratchpad lb/): 3,914 teams; us #164 at 0.954; 0.957 = 71-84, 0.956 = 85-106 (22), 0.955 = 107-146 (40), 0.954 = 147-211 (65), 0.953 = 212-492 (281). Silver ~5% = rank 196 (inside 0.954 block, 32 below us). >=0.954: 211 (195 at 18:08 -> +16 in 4.25 h). Top 0.975.
## 2026-09-25T22:28:25Z (d) finals-rule gaps
- K2 - #35 reads lowrefine alone (safetail inert: K1 sha == exp57b; insertion identical). twin - #34 reads lowrefine alone too. No lab for lowrefine (exp60 base has none; dummy +0.0025 only on head-train stem 6bba_05db0fb1).
- Gap 1: K2 <= 0.952 -> R3 drops lowrefine -> F1 must be K1 (exp58t) but K1 is unscored and its submit is approved only on K2 ERROR (round-1 item 6).
- Gap 2: f2 floor 'twin public >= 0.953' vs R3 tolerance -0.001: twin 0.952 would eject the twin for exp52 (0.950) although R3 keeps a -0.001 rider. Both F1 and F2 carry lowrefine (common mode, unhedged).
- insertion break-even: lab control div 16/25/83 J 0.129 -> q* = 0.114; ins35 201 added forks -> 9 TP, 6 FP, 186 ignored (93%). Private hurt needs OOF evaluable precision < ~11% (in-sample 60%).

## 2026-09-25T22:29:45Z final JSON written (8 findings R3S-1..R3S-8)
