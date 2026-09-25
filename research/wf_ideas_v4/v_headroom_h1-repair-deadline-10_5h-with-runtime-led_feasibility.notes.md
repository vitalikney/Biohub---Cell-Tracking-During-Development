# H1 repair deadline 10.5h - feasibility notes (2026-09-25T17:41:13Z)

## Sources read (2026-09-25 ~17:10 UTC)
- tools/build_probe_kernel.py l.1846-1850: whitelist `REPAIR_DEADLINE_S != "34200"` -> exit unless --lab. l.1383-1462 safetail: DIVINS gate = elapsed >= DIVINS_DEADLINE_S or _deadline_degraded; the deadline check is per dataset at start (`_dataset_t0 - KERNEL_START_TS > REPAIR_DEADLINE_S`), KERNEL_START_TS set in cell 0 (so container boot before cell 0 + nbconvert ~25 s are outside the timer but inside Kaggle's 12 h).
- Change = one env value; code path already exists and was exercised by FD dummy -> byte-identical when not fired, fail-soft = existing degraded path. tests/test_safetail.py l.153-183 has the refusal cases to extend.
- _dl/biohub-exp58fd-x138-safe log: DEADLINE at 975 s; degraded FINAL 28.0/32.1/6.6/45.6 s (mean 28.1 s/clip, max 45.6).
- _dl/biohub-exp58-x138-safe-lowref log: repair 81.6/119.8/20.4/287.1 s (127.2 s/clip), kernel end ~1535 s.
- experiments/runtime_step0/step0.md: T(N)=300+(N/2)*318+N*r; N<=106 (L34), N<=97 (L35); L35<=7.73 h.
- CONTEXT.md l.1653-1656 R5: (a) latency <= 9.5 h for C01 builds, (b) step-0 forecast shows timer not fired with >=1 h margin. F2 rule and S10-S11 also hard-code 9.5 h. Pre-registration says "apply mechanically, do not rewrite" -> H1 needs an explicit user OK.
- Browser fact (CONTEXT 13:58 UTC): 12 h limit, https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/overview (Code Requirements); timeout = "Notebook Timeout" error, counts as a slot.

## Simulation (scratch sim.py; model = step0 + insertion gate at 8 h, repair 127.3 s/clip with insertion, 62 s without, degraded 28.1 s; slowdown s scales everything)
- N=97: 9.5 h deadline never fires until s~1.4; at s=1.5 9.5h degrades 12 clips, 10.5h 0 (runtime 9.82 h). Timeout for 10.5h only at s>=~2.25.
- N=106: s=1.3 -> 9.51 h, 0 degraded either way (idea's '1.25x -> 10.65 h, 26 degraded' is overstated; L35-scaled estimate gives 0-15). s=1.5: 32 vs 0 degraded. Timeout band CREATED by H1: s in ~[2.08, 2.13] (9.5h ends 11.74 h, 10.5h ends 12.02 h).
- N=130: H1 timeout band s ~[1.72, 1.88].
- N=199 world (hidden hardware faster for #34/#35, s~0.55): if a later run gets dummy speed (heterogeneous hardware), s=1.1 -> 9.5h 11.47 h vs 10.5h 11.87 h; s=1.15 -> 11.99 vs 12.15 h TIMEOUT. H1 lowers the timeout threshold from ~1.15 to ~1.08 in that world.
- Normal world (s~1, N<=97): no effect, 0 s added.

## Lens verdict notes
- Implementable in ~0.5 h, byte-identical when not fired, fail-soft, gated by the K3 dummy log line; rides K3 in S4 (26.09 ~10-13 UTC), scored well before 27.09 12:00; no extra slot.
- The proposed sha twin (K3 built with 34200) needs an EXTRA dummy (~0.5 GPU-h from the 11 h quota shared with exp60 lab) and is redundant: env value only enters a comparison that never fires on the dummy. Replace with the SAFETAIL log-line check + probe.json diff.
- R5(b) already admits 9.5-10.5 h latencies when the step-0 forecast (~7.9 h) has >=1 h margin -> the 'admissibility' benefit is mostly moot.
- Ledger clause "shift DIVINS_DEADLINE_S by the same delta" contradicts the idea's own risk note (do not move DIVINS later); drop it.
- Confound: in a slow world K2 (9.5 h) degraded vs K3 (10.5 h) not -> K3-K2 delta includes the deadline gain -> could admit forkmid under R4 wrongly. Latency is visible, so flag it.
- Timeout on F1-final (S12 28.09) would force S13/S17 re-runs; buffer exists (S17 29.09 <=02:00, scored by ~12:00).
