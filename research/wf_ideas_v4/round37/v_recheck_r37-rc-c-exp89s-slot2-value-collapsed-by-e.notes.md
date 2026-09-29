# v_recheck R37-RC-C notes
- 2026-09-29T09:26:20Z start; no prior json
- 09:27Z poll.log l.29914 (header 09:18:30Z): 56656147 exp89r COMPLETE 0.957. CONTEXT 09:19Z line logs Rr '-', DIS ~0, rule (a) not met, exp89s not sent, slot-2 default now UNUSED. Commit 348b9dc.
- Finding's evidence ('09:18:30Z exp89r PENDING') is stale; action (1) 'before exp89r header' past; action (2) Russian text says default = send if >=0.958 -> condition already false, text would mislead; action (3) conditional on 0.958/0.959 -> moot.
- Core claim (exp89s insurance only) agrees with CONTEXT 09:19Z ('cannot become V_pub'); the MC adds P(exp89s V_pub | d_R .957) ~.0001 -> nothing new.
- Sanity: exp89t ~ 0.957 + 0.0015 (SEC removed) = ~0.9585 +- ~0.0012; P(>=0.9595) ~0.1-0.2 unconstrained -> finding's 0.11 plausible, info only.
- 09:27:11Z JSON written: refuted=true (stale/superseded)
