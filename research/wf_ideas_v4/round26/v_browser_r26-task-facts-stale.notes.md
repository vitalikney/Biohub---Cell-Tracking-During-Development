# v_browser_r26-task-facts-stale (verifier notes, 2026-09-28 ~13:30 UTC)
- CONTEXT.md L3856: 12:16Z probe 50 exp85a = 0.958 (56629533), R+, rank 134, UP 21; E10 trigger now >= 0.959.
- CONTEXT.md L3863: 12:16Z probe 51 exp87a submitted (ref 56640366, 12:14:57Z); expected read ~21:30-22:15Z (00:30-01:15 MSK).
- CONTEXT.md L3871/3885/3899: 12:17Z night list, 12:23Z risk stack exp89q/exp89r, 12:25Z user confirmed night + standing override.
- CONTEXT.md L3915: 13:14Z exp89q/exp89r dummy PASS; GPU ~2.5-3 h left (task says ~4 h).
- tools/kaggle_feed.py L172: --our-best default already 0.958 (so trigger = above 0.958) -> tool already refreshed; only the task text is stale.
- Other stale items in KEY FACTS: GPU ~4 h -> ~2.5-3 h; night slots now 00:05 (exp89r|exp89q), 00:06 exp75, 00:46 exp89p (fallback exp83c 00:07); dummies PASSED add exp89p, exp89q, exp89r; exp75 is a night file, no longer a probe-51 alternative.
- Verdict: finding correct, info-only, zero risk (task-text refresh, no model/submission change). No value/feasibility claim to refute.
