- 2026-09-27T20:28:51Z start verification R20-RC-A
- 20:5xZ run_stats verified (_dl/biohub-exp70b-k2-fm45, exp70g-k2-cap6, exp78a-k2-cap8, exp70q-k2-maxdiv, exp76e-k2-fm-cap6 /run_stats.csv):
  eligible thr0.4 14/0/33/142 OK; added cap4 4/0/4/4, cap6 6/0/6/6, cap8 7/0/8/8 OK; steals cap4 = cap6 = 2/0/1/2 OK; skipped_steal_cap 0 everywhere OK;
  44b6_0113 at cap8: added 7 + skipped_used 6 + frame 1 = 14 -> exhausted OK; 6bba_05db skipped_cap_frame 10 (cap6) / 11 (cap8) OK;
  thr0.3 (exp70q) eligible 59/2/42/391, 2 inserts on 44b6_0b24 OK; divins_nodes_scored identical 3869/6988/661/20770 OK.
  CAVEAT: cap6->cap8 on 6bba_05db is +2 STEALS (orphan 4->4, steal 2->4). Orphan-only holds for 4->6 only; cap>=8 rungs (exp78a, exp78b w/ steal cap raised) mix in steals (edge-J cost).
- CONTEXT 18:56Z probe45 0.956 (#268->#162); 19:01Z exp78a/78b already built; 19:05Z session already re-ranked 28 Sep plan onto cap direction -> finding mostly redundant with executed plan.
- round20 scan_hyp_private_view r20pv-1: private C(cap6 - #37) ~ +0.0004 +- 0.002, P(C>0) ~0.5 -> public revival != private value.
- round20 scan_hyp_insertion_direction R20ID-1: extended lab (29 arms, in-sample) agrees in sign with public from cap>=12 -> 'lab has no say' is overclaimed; R20ID-4 trigger for thr axis is 46 >= 0.957, finding uses >= 0.956 (a tie with exp70g = no evidence for thr/fm).
- scan_plancheck PC20-01 codes vs own base 0.956; PC20-03 push 79a (CI) dummy first; PC20-09 last submit 01:45Z 29 Sep unless user lifts (finding says ~12:00Z).
- User lifted public-knob-ladder ban 26 Sep 20:33Z, aggressive mode 27 Sep 11:14-11:16Z -> knob rungs rule-compliant; byte-identical/fail-soft trivially (env knobs only, safetail gate).
- 21:00Z wrote final JSON (refuted=false with fixes)
