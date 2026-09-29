# v_recheck R39-RC-C tie rule notes
- 2026-09-29T11:24:44Z started; no prior JSON present.
- e10_watch rows (0 API calls): 0913Z/0941Z Fanch #145 0.958 cnt57 last 02:18:47; 1013Z Fanch #139 0.959 cnt58 last 03:20:41 (count+1, date and display changed together, so the new best file IS the 03:20:41 one). Ours #140 -> #141 0.959 cnt56 (last 00:46:36 = latest scored file, not the best; best = exp87a 2026-09-28 12:14:57Z per ledger.md l.24). 1110Z Manish #142 0.959 cnt18 last 04:13:52 (0.956 -> 0.959 with cnt 17 -> 18).
- Earlier-time rule predicts Fanch below us (fails). Later-time rule predicts Manish above us (fails). Unrounded order explains both. 2 later files straddle us -> not time-ordered in either direction.
- LastSubmissionDate tracks the latest scored file (0113Z: 12:14:57 cnt53 with night files pending; now 00:46:36 cnt56), so the #126/#127/#128 'not time-ordered' sub-argument is weak alone; the Fanch/Manish pair is the decisive evidence.
- FINAL_REPORT_v4 sec.2 l.47: unrounded order, time only for byte copies (Rules 3.7.b); 34/43 earlier submitters below us in 0.954 block.
- Fanch 'earlier timestamp' line: only in round38 report.json new_facts (2) and the R38 card action's 'for reference' note; NOT in CONTEXT.md, NOT in scratchpad card_fill_1203_v3.txt (card l.15 already says 'выше чемпиона без округления'). Wording-only fix; no rule, no slot, no Kaggle call.
- Verdict: not refuted; info.
