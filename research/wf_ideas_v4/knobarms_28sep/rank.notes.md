# rank - final ordering of surviving knob arms (28 Sep)
- rank.json absent at start -> computed fresh.
- Inputs: v_1 (Z_WEIGHT, DOWN 0.6 only), v_2 (DISAPPEARANCE, fixed to 2.25/1.75, measured +-0.8% nodes, 1.5-2% edge churn,
  mostly on 44b6_0b24), v_9 (SISTER_SYMMETRY_TAU 0.7/0.5, +8/-9 forks, nodes ~0.01%). All other v_* refuted.
- Base recipe = exp70g probe.json: --base x138 --patch divinsert --patch lowrefine --patch safetail + DIVINS_ENABLE=1 STEAL=1
  CAP=6 FRAME_CAP=1 ALPHA=1 THRESH=0.4 DUMP=0, REPAIR_DEADLINE_S=34200, DIVINS_DEADLINE_S=28800, LOWREFINE_ENABLE=1,
  DEGRADE_KEEP_DIV=1.
- State: probe 50 (exp85a JT knobs) and 48 (CI) still PENDING (ledger 09:03Z). JT 743929: no reply on closed knobs yet.
- Slot math 29 Sep: 00:05-01:45 <= 3 (E10 first, FULL = K-lever exp86c/exp87a, one '?' test); after 02:00Z <= 2 non-CI
  (exp81 SEC contends). So the knob arms realistically get 1 slot (the 00:05-01:45 '?' test) and 1 after 02:00Z; a 3rd
  only if E10 does not fire or exp81 is already read.
- Ordering logic (no lab sign): D is the sibling of JT's disclosed ILP winner and re-wires edges at JT's scale (<1% nodes);
  UP 2.25 also matches the node-bonus direction and the lineage history (1.5 -> 2 was adopted). TAU 0.7 is a clean,
  exactly-sized division-term change (~+8 forks = cap step that read +0.002) but the DC 0.20/0.225 reads (adding
  marginal safe forks = tie) make a tie likely. D 1.75 is the other half of the D pair and is the favourite if
  probe 50 reads R+ (more nodes near track ends wins). TAU 0.5 likely '-' (DC 0.30 removal -0.005). Z 0.6 smallest,
  no disclosure.
- Conditional: if probe 50 = R+ swap exp88c (D 1.75) above exp88a; and if BASE moves to exp85a/exp86c, re-cut the top
  two arms on that base before 29 Sep (JT: arms off the current best).
