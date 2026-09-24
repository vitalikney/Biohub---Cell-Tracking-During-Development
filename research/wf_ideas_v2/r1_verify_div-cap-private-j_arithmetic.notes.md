# arithmetic verify div-cap-private-J (started)
- Selection grid (progress/*.jsonl, 64 6bba vids, exp39 7/15/57): TP SATURATES at 12 for every cap-6 config (a1_c6 t0.05..0.6 -> 12/24..34/52; a0_c6 12/31-32). a1 t0.5: c3 11/22, c4 12/27, c6 12/29 -> marginal c4->c6 0TP/2FP (70 more insertions: 229->299). a1 t0.4: c4 12/29 -> c6 12/31. s t0.6 c4 12/23 -> c6 12/25. a0 c3->c6 (t0.05..0.3): +2TP/+10FP (192->382 ins). s_c4_t0.5 13/25/51 is best J (0.146).
- Edge term per insertion config: s_c4_t0.5 edge 52551/3195/3278 vs exp39 52543/3189/3286 -> negligible (+0.00005 adj edge).
- Shipped probe 28 = cap 4, ens thr 0.4 (= OOF 0.5), steal on -> the refined 'looser threshold' is ALREADY shipped; going looser (a1 c4 t0.5 12/27 -> t0.4 12/29) is 0TP/2FP too.
- Local base with insertion (199 vids) = sel 13/25/51 + conf 20/39/67 = 33/64/118, D=215, J=0.1535, break-even 0.133 (not 0.12).
- dScore = 0.1*(n_eval/D)*(p(1+J)-J), n_eval/D scale-invariant ~12/215=0.056 for cap 4->8. p=0: -0.00086 (J.153) .. -0.0020 (J.36); p=.17: +0.00024 / -0.00072; p=.25: +0.00075 / -0.00011.
- Hypothesis +0.0015 mixes 13-15 forks (199 vids) with D~130 (135 vids): 2x overstatement; consistent value at p=.25 is +0.0008.
- Ceiling '+20 TP' double-counts cap-4 TP (23 is exp39, cap4 already at 33); selection shows 0 TP from cap>4 in all 12 grid configs.
- Resolution: P(0/12 | p=.17)=0.107; decision rule ">=0.25 with >=8" passes a true p=0.1 with prob 0.19.
- FINAL JSON written (refuted=true)
