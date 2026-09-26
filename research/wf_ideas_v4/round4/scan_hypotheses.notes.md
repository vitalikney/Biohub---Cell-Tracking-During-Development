# round4 scan_hypotheses notes (started 2026-09-26T00:46:29Z)
- 00:47Z: scan_hypotheses.json absent -> fresh run. date -u = 2026-09-26 00:46:48Z.
- Git check: 1017c41 (committer 2026-09-26T02:13:12+03:00 = 23:13:12Z 25 Sep) holds READ TABLE (CONTEXT.md l.1978), S4-S6 line (l.1968), biohub-research-round.js plancheck+report prompt edits. b2cb928 (00:02:49Z) holds RESUME POINT (l.2006). origin/main == HEAD == b2cb928 (pushed). Working tree: only ledger.md/poll.log modified (poller). K2 56563521 / twin 56563534 PENDING at 00:43:00Z poll -> all pre-score.
- round2/round3 REPORT.md files do NOT exist on disk (only report.json with report_md_ru); round3 note says main session should save it.
- Round 3 already computed insertion by density quartile (Q0 +0.0246, Q1 +0.0028, Q2 -0.0005, Q3 +0.0019, ALL +0.0065); need per-clip concentration (new).
- 01:00Z: exp60 insertion concentration (script: scratchpad ins_conc.py; official summarise via tools/score_geffs; 56 clips, ins35 vs control, IN-SAMPLE for DaughterNet):
  pooled +0.00648 (adj +0.00015, divJ +0.0633; div 16/25/83 -> 25/31/74). Evaluable changes in 15/56 clips only: 9 clips +1 TP each, 6 clips +1 FP each; 41 clips 0; 201 new forks, 45 clips hit cap 4.
  Jackknife: top influences 44b6_d754aa59 +0.00078, 6bba_55b7eebe, 6bba_6ca87370, 6bba_b204cac7 (+0.0007 each). Leave-top-k-out: k1 +0.00570, k2 +0.00494, k3 +0.00416, k5 +0.00257.
  Stratified clip bootstrap (4000): pooled 5/50/95% = +0.0028/+0.0063/+0.0107, P(<0)=0.001; 44b6 5% = 0.0000; 6bba 5% +0.0026.
  44b6: SELECTION delta 0.0000 (9 clips), CONFIRMATION +0.0157 = ONE TP (44b6_d754aa59) -> the CONTEXT '44b6 +0.0157' is a single event; 44b6/ALL +0.0058.
  Density (control nodes/frame; cuts 84.8/163.9/260.4): Q0 +0.0246 (7 TP/2 FP), Q1 +0.0028 (1/1), Q2 -0.0005 (0/1), Q3 +0.0019 (1/2). TP clip densities 46,55,56,58,59,64,75,128,286; FP 54,63,157,203,295,397. -> gain = sparse clips; dense half in-sample precision 2/6.
  Per-event arithmetic: +1 TP = +1/N divJ, +1 FP = -J/N; lab N=124, J=0.129 -> q*=0.114; public J~0.35 (probe 26: exp29-exp45 = 0.035) -> q*~0.26.
- Poll alignment: poller writes ts BEFORE CLI, cadence 600 s + ~2 s drift (00:02:53, 00:12:55 ... 00:43:00). Predicted polls 07:54:2xZ and 08:04:3xZ vs K2 8.0 h mark 08:02:12Z; F(K2)=7.87 h = 07:54:24Z. A completion in (07:54:2x, 08:02:12] is only seen at 08:04:3x -> L upper 8.04 h -> 'not clean' though clean. Fix: one extra poll ~08:00:30-08:01:30Z (same CMD/format, appended to poll.log), no rule change.
- Kaggle finals: auto-select = best public if none ticked; private uses the best of the selected (https://www.kaggle.com/general/19028 ; https://www.kaggle.com/docs/competitions). CONTEXT l.1728 already states private = max(F1,F2). 0.954 ties now: #35 56545786, P36 56555189 (diagnostic), maybe K2 -> auto-select could pick ungated #35/P36 and drop the twin.
- READ TABLE gaps: row 5 with twin ERROR (d2 undefined) not covered; rows 2-5 need both K2 and twin terminal; row 2 without OK gives F2 = exp52.

## SCORE-READ PROCEDURE (mechanical; applies the READ TABLE of CONTEXT.md 2026-09-25 23:12 UTC, commit 1017c41)
0. Pre-check (done 00:47Z): READ TABLE + S4-S6 line in 1017c41 (23:13:12Z), RESUME POINT in b2cb928 (00:02:49Z), origin/main == HEAD; K2/twin PENDING at 00:43:00Z. Record in the read entry: "table commit 1017c41 23:13Z < first K2/twin result seen <ts>".
1. `python tools/runtime_ledger.py --print` (or ledger.md). Take rows ref 56563521 (K2, exp58, safetail 9.5 h) and 56563534 (twin, exp58n, safetail_noins): status, public, L bounds "(lo, hi]".
2. Wait until BOTH are COMPLETE or ERROR (exception: K2 ERROR -> row 1 at once). Work in integer thousandths: k=round(1000*K2), w=round(1000*twin).
3. d1 = k - 954; d2 = w - 953; tk = w - k; clean = (K2 status COMPLETE and hi <= 8.00). hi carries +210 s per failed CLI attempt; hi > 8.00 or '?' = not clean.
4. First match:
   R1 K2 ERROR -> K1 exp58t v1 next slot [OK]; F1 = K1 once scored, R5-admissible, >= 0.953; F2 = twin by f2 else exp52. [no OK: §f fallback order]
   R2 twin COMPLETE and tk >= +2 -> F1 = twin; F2 = K2 if d1 >= -1 [OK]; else K1 if submitted+scored [OK]; [else exp52].
   R3 d1 >= -1 -> F1 = K2; F2 = twin if w >= 953; w == 952 -> twin with floor [OK] [else exp52]; w <= 951 or twin ERROR -> exp52.
   R4 d1 <= -2 and clean -> lowrefine out of F1; K1 [OK]; F1 = K1 once scored/admissible/>=0.953; F2 = twin if w >= 953 else exp52. No K1: F1 = twin if w >= 953 [OK] [else #34]; F2 = exp52.
   R5 d1 <= -2 and not clean -> d2 <= -2: as R4; d2 >= -1: F1 = K2, F2 = twin if w >= 953 (952 with floor OK) else exp52; raise runtime trigger after L(twin) vs L(K2) (L(twin) >= L(K2) - 0.3 h => queue delay).
      GAP: twin ERROR in R5 (d2 undefined) is not covered -> pre-register a line before any score (suggest: F1 = K2 (no clean evidence against lowrefine), F2 = exp52).
   Never: K1 at d1 = -1; exp56 (#34) while an admissible non-copy x138 file exists; two files with identical components.
5. Log in CONTEXT: k, w, d1, d2, tk, L bounds, clean, row, F1/F2 refs, [OK]s used or not. Commit.
Likely outcomes: k=954/955, w=953/954 -> R3 -> F1 = K2 56563521, F2 = twin 56563534. k=954, w=956 -> R2 (F2 = K2 needs OK, else exp52). k=953 -> d1=-1 -> R3. k<=952 -> R4/R5.

## FINALS-TICK CHECKLIST (29 Sep; deadline for ticks 20:00 UTC = 23:00 MSK; Kaggle hard end 23:59 UTC)
- 28 Sep evening: re-run the read; confirm F1/F2 refs in CONTEXT (+ any S12 consolidation per §f); no pending submission expected; no new builds after 29 Sep 02:00 except S17 emergency (hard 10:00).
- 29 Sep 12:00 UTC (15:00 MSK): reminder to the user with: F1 ref + description head ('probe 37: exp58 ...', submitted 00:02:12Z), F2 ref ('probe 38: exp58n ...', 00:02:18Z) or exp52 (56534391, 00:02:05Z 25 Sep) per the row.
- Tick on https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/submissions : exactly 2 checked, matched by ref/date not by score (K2, #35, P36 all 0.954; K2 and twin 6 s apart). Untick anything else. Reload, verify persistence, screenshot.
- Never tick: #34 exp56 (x138 copy, earlier-submission tie loses), #35 (L35 unproven), P36 (diagnostic), two files with the same components.
- Do NOT rely on auto-select: without ticks Kaggle takes the best public, i.e. 0.954 near-copies (#35/P36/K2) and drops the twin hedge; private = best of the selected.
- Record in CONTEXT with timestamp + commit.
- 00:53Z: wrote scan_hypotheses.json (8 findings R4H-1..8).
