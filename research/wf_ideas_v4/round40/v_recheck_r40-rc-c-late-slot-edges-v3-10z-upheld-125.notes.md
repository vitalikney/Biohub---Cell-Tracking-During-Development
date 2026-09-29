# R40-RC-C verify notes (13:26Z)
- 13:27Z sources: CONTEXT.md l.4582-4592 (12:59Z entry: 'non-CI ~9.0-9.5 h -> ~14:30-15:00Z; CI 10.75 h -> ~13:15Z'); v3 FINAL_REPORT l.179-180 (S17 <= 02:00, hard edge 10:00); digest_20260929T1258Z (Deotte 744250 12:57:37Z, https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744250); ledger.md header 13:19:14Z.
- Ledger L check: non-CI safetail exp78a/exp70a (6.87,7.04], exp89p (7.02,7.20], exp70q (7.64,7.81] (max); exp58n safetail_noins (6.69,6.87] omitted by finding (min is 6.69 not 6.87; harmless). CI exp75 (8.88,9.05] .. exp87a (9.30,9.48]: matches. x138 verbatim exp56 (6.29,6.46]; exp57b (6.72,7.73]. Deadlines: safetail 9.5 h, safetail_ci 10.75 h, x138 7.5 h.
- Edge arithmetic (finish by 23:59Z): 9.5h->14:29Z; 7.81h->16:10Z; 10.75h->13:14Z; 9.48h->14:30Z; 6.46h->17:31Z; 7.73h->16:15Z; x138 gate 7.5h->16:29Z. All finding numbers correct.
- Caveat 1: 'at 13:20Z no family can read before 20:00Z' is literally false for a verbatim x138 without dummy (13:20+6.29..6.46 = 19:37-19:48Z); true once the ~25-30 min dummy is included (13:27Z now + 0.5h + 6.29h = 20:14Z). Practical verdict holds.
- Caveat 2: E10 edge assumes x138-verbatim L; a >=0.960 notebook adds steps, L unknown; gate-based E10 edge = 23:59 - 7.5h - 0.5h dummy = ~16:00Z (19:00 MSK); observed-based ~17:00Z (20:00 MSK) is the latest, not the default.
- Caveat 3: observed-max edges (non-CI 16:10Z, CI 14:30Z) must not replace the pre-registered family deadlines; final-day queue can stretch L. Moot anyway: slot 2 is E10-only (11:54Z entry), no non-CI/CI candidate exists.
- E10 flag: none (digest 12:58Z best public biohub 0.953).
- Verdict: not refuted; low value (clarification only, ~0 LB), 0 API calls; amend the line wording.
