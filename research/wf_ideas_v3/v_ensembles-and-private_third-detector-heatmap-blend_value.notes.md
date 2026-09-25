# third-detector-heatmap-blend - VALUE/TRANSFER skeptic notes
- 2026-09-25T11:14:27Z started; no prior json. Read BRIEF.md.
- x138 cell 3 l.652-663 / cell 4 l.60-160 checked: blend is on det LOGITS, secondary aligned per frame to primary mean/std (scale clamp 0.5-2), 0.2 P + 0.8 S, retention guard falls back to PRIMARY-only if blended candidates < 0.90 x primary. Primary = pilkwang support-pack-50ep, secondary = pilkwang seed314159. Threshold 0.965, LOWDET 0.3 readmit + gap filler already reuse sub-threshold peaks (cell 0 l.95-106).
- browser_research pass2 l.77: leonixis v5-candidates = "all-train 199 videos, 60 epochs, WARM START from v3res; LB checkpoint-pick set" -> NOT independent (warm start) and epoch selected on public LB. Alone 0.947 = tie with the wall.
- pass2 l.54-55: andnyu/biohub-synthetic-conditional-third-model = 0.946 (public notebook with a 'third model', below the 0.947 wall; unknown whether detector or edge model).
- RESULTS.md l.37,39,42,46: ALL FOUR detector-blend perturbations on LB were negative: sec weight 0.5 -0.002; sec:=exp08 -0.016; sec:=friend A scratch -0.025; sec:=exp23 (ft seed314159) -0.007. Zero positives.
- CONTEXT l.355: +0.046 = public pipeline (4 heuristics incl. dual-seed blend) vs our clean pipeline; dual-seed share is NOT isolated -> idea's evidence misattributed.
- Budget-guard value verdict (v_..._x138-budget-aware-deadline_value.json): refuted as a standalone, private ~+0.002 insurance; dependency weak.
