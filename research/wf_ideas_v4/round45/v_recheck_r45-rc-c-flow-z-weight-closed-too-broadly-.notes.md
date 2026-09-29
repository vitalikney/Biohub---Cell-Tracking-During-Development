# R45-RC-C skeptic notes (29 Sep 2026 18:31 UTC / 21:31 MSK)
- No prior answer JSON in round45/ -> fresh check.
- ideas_29sep/v_4.json: refuted 0.6; Mahalanobis-optimal z weight ~1/sqrt(1.3..1.6) = 0.79-0.88 (from label-free temporal noise variance ratio, NOT GT residuals).
- knobarms_28sep/v_1.json: refuted UP 1.5 (1.4 -> 0.01-0.02% churn, 2.0 -> 0.03-0.04%); it KEPT DOWN 0.6 as one slot (refuted=false for DOWN). So "treated as closed since" is only via knobarms rank.json / ideas v_4, not the closed list.
- arms_0.notes.md l.7/9 CPU replay churn (4 visible clips): zw0.7 0.05-0.21%, zw0.5 1.30|0.14%, zw1.4 0.01-0.02%. By interpolation zw0.85 is ~0.02-0.1% edge churn, nodes ~0 -> same inert band as the UP arm that v_1 already called unreadable on a 3-decimal display.
- RESULTS.md probes 21-23 (relink knobs on exp29): all 0.945, -0.002 -> relink-class LB transfer <= 0 so far.
- Time now 18:31Z; ticks by 20:00Z; slot 2 closed (R40-A1); deadline 23:59Z. No build/dummy/probe is possible or allowed; post-deadline test has no competition value.
- Verdict: refuted (no value); bookkeeping correction only.
