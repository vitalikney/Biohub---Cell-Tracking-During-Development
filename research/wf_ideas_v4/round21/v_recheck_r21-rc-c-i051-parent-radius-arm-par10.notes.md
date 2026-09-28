# v_recheck R21-RC-C I-051 par10 — notes (2026-09-27T23:29:04Z)
- start: no prior json answer.
- 2026-09-28 verified r21_par_exp60_agg.json (scratchpad divpp): par10 forks 44b6 +26 ign / 6bba +69 (1 TP, 68 ign), nodes +21/+40, dc_miss 465+710=1175, W/L 0/4 + 1/8 -> finding numbers match.
- The single TP is fork 5351 in 6bba_5c039895 (div_tp 2->3). Verifier script scratchpad divpp/r21v_tpmiss.py: replay par10 with unseen DC points REJECTED (score 0) -> div_tp back to 2, TP fork 5351 gone. So the ONE evaluable TP is itself a DC-miss fork; its kernel survival is ~25-28% (DC pass rate), not certain. Expected lab value ~0.27 x 0.00095 ~ +0.00026 on 6bba. Strengthens 'blind and tiny'.
- DC-strict lower bound (scratchpad divpp/r21v_strict_all.py, unseen DC -> 0 = reject): par10 adds only 2 forks on all 56 clips (6bba_786893ac +1, 6bba_969618f6 +1), 0 of them the TP. 93 of 95 lab adds are DC-unknown.
- Probe 41 (exp70d dc0.30) = 0.949 while lab was >=0 on both embryos -> both-embryo rule not predictive (CONTEXT l.2534, l.2789-2799). Probe 45 cap 6 = 0.956 (CONTEXT l.3196). I-051 row in research/KNOWLEDGE/IDEAS.md l.369.
- Verdict: NOT refuted (closure stands, reason 'blind and tiny' is right and even stronger). Wording fix: '1 TP / 0 FP' must say the TP is itself DC-unscored; expected lab ~+0.0003 on 6bba, public expectation well under +0.0006.
