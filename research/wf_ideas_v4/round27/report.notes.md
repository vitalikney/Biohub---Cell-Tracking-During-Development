# round27 report notes

- 2026-09-28T16:08:16Z start: no report.json existed; synthesizing from scan_*.json + v_*.json verdicts
- 16:08:47Z battery (Win32_Battery, read-only): BatteryStatus=1 (on battery), 57%, Windows EstimatedRunTime 451 min. Series 64% 15:49Z (scan) -> 58% 16:04Z (verifier) -> 57% 16:08Z: ~22%/h under load => empty ~18:40Z worst case; Windows estimate ~23:40Z. Both before the 00:04Z batch.
- poll.log headers 15:41:53Z, 15:51:56Z, 16:01:59Z OK; 56640366 still PENDING at 16:01:59Z (l.23691). Poller phase ~10:03 min.
- feed digest 20260928T1556Z: 15 topics, 0 new topics/comments, E10 FLAG none; best public notebook 0.953 (kunaldesale/amanatar/raunakdey07/anvithpothula). Aggressive mode: nothing disclosed.
- e10 watch RUN 27 15:43Z signals 0; next 16:41:53Z.
- CONTEXT 15:43Z OPS line says 'network outage, not a sleep' -> wrong (PC27-01 confirmed by verifier). CONTEXT 15:57Z: Kaggle ban report elsewhere -> API load cut (feed every 90 min, minimise calls) -> R27N-6 tight-poll loop rejected also on that basis.
- Checked night-checklist mechanics: poll.log CSV header 'ref,fileName,date,description,status,publicScore,privateScore' (l.2); tools/runtime_ledger.py exp_token l.157 (EXP_TOKEN l.90, first expNN token) and RETRY_SLACK_S=210 l.42; kernels status output format 'has status "KernelWorkerStatus.COMPLETE"' (experiments/coordhead_retrain/captures/fetch.log l.181); submit template CONTEXT l.565 (positional competition, -k -v 1 -f submission.csv -m); dataset meta csv = ref,title,size,lastUpdated,downloadCount,... so cut -f1,3,4 = ref,size,lastUpdated (R27N-9 ok).
- nb_try gap: a daily-limit / allowance error would hit the HARD FAIL branch ('limit') and trigger the exp89p->exp83c fallback; it must STOP instead (exit 3). Added to R27-A5.
- Session cron clock = MSK (CONTEXT 10:52Z). Rounds 28 = 17:47Z (20:47 MSK), 29 = 20:17Z, 30 = 22:47Z; 01:17Z round missing (PC27-05b) -> covered by backup crons '20 3 29 9' / '50 3 29 9' / '30 4 29 9' (MSK).
- finals_card_v4_ru.md: l.31 unconditional 'Модель ... выше по бронзе у П1' (verifier defect 1), l.40 П3 silver '~0.51' (defect 2), l.101 token match on 'probe 52:' prefix (defect 3), l.113 pool rule 'CI L_hi <= 10.2 h' must follow GAP RULE v2 (new, R27-A2), l.58 DIS line wording (RC-A optional footnote).
- Merges: PC27-03 + R27N-10 + R27C-4 + R27-RC-B + PC27-04 + R27-NF -> R27-A3; PC27-06 + R27N-4 + R27N-3 + R27N-8 + R27N-9 + PC27-05b -> R27-A5; R27N-2 + R27N-7 + PC27-07 clarification -> R27-A4; PC27-05a + R27C-3 -> R27-A7; R27C-1 + R27C-2 + R27C-4 windows + RC-A footnote -> R27-A8.
- 2026-09-28T16:14:42Z Write of round27/REPORT.md refused by the harness ("Subagents should return findings as text, not write report files"); not circumvented. Russian report text goes into report.json field report_md_ru and the structured answer; the main session can write REPORT.md from it.
- 2026-09-28T16:16:57Z report.json written and parsed (9 actionable R27-A1..A9; A6 not covered).
