# v_github-intel_successor-port_value notes (2026-09-25)
- Fri Sep 25 10:55:35 UTC 2026 started; brief read
- Read BRIEF.md; research/browser_research_2026-09-24_pass2.md (lines 1-60, 90-140); browser_research_2026-09-24.md (180-215);
  h_kaggle-intel.json (lens summary); grep of discussions_summary.md / CONTEXT.md for noise evidence.
- Numbers confirmed: Tennant rank 32 = 0.959, Pothula rank 58 = 0.956 (pass2 l.110-111); x138 0.953 public, 41 teams at 0.953;
  Pothula stub kernel 24 Sep (pass2 l.18); Tennant public kernels 0.942-0.947 (browser_research l.118-121) while team = 0.959.
- KEY behavioural fact: both authors publish BELOW their own team score: Pothula published 0.953 while at 0.956 (margin 0.003);
  Tennant's newest public (readmit-v1 0.946, 19 Sep) is 0.013 below his 0.959. => any successor they release is likely
  <= (own score - 0.003): Pothula -> ~0.953-0.954 (nothing new), Tennant -> ~0.956 at most.
- Medal zone: 3,872 teams -> silver ~top 5% (~190), gold ~top 17. Both authors are in silver; publishing their best invites
  copy+rider teams to pass them. Incentive against release in the last 4 days (guess, standard Kaggle behaviour).
- Selection bias: team score = max over many public submissions on ONE embryo; public knob tweaks proven to be noise
  (identical notebooks 0.946/0.942, discussions_summary l.101,128; CONTEXT l.229). A +0.003 max-of-N public gap shrinks to
  ~+0.001-0.002 expected true gain; private transfer of public-selected post-proc ~0.5x (lab +0.0019 -> LB +0.001, BRIEF).
- WebSearch 'kaggle biohub ... anvithpothula OR thtennant': no new notebooks indexed (titles only; kaggle.com blocked, not tried).
- Arithmetic: E[public gain] = P(release>=0.954 by 28 Sep) 0.3 (idea's guess; I'd say 0.15-0.3) x E[gain|release] ~+0.002
  x P(passes gate >= base+0.002 | true +0.002, noise 0.003) ~0.5 => ~+0.0003..+0.0006. Below +0.002 threshold -> REFUTED
  as a value line; keep as a zero-cost watch with a hard trigger.
- Fri Sep 25 10:57:10 UTC 2026 final JSON written (refuted=true)
