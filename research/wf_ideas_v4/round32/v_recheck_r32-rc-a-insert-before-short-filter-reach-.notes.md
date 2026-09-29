# v_recheck R32-RC-A (insert before short filter) — skeptic notes
- 2026-09-29T03:33:09Z start; no prior json/notes.
- Code order re-verified (exp85a notebook, joined code cells, 5861 lines): OUTPUT_MIN_TRACK_LEN env default 6 (l.283); def filter_short_track_components l.4253; call l.4666; divinsert block l.4670-4711 (after filter). Claim holds.
- tailreach_out.json (scratchpad r32): 99 GT div (44b6 11, 6bba 88); FN_filter_deleted+present = 3 (all 6bba, t_parent 24/47/54, 45-75 frames from end); +1 filter_deleted with no parent; FN_present+present 72 (62+10). Numbers match the finding.
- Skeptic caveats (do not change verdict): (a) lab = 2 train embryos, 44b6 contributes 0, so the 3/99 rate is a 1-embryo estimate; (b) script counts only short-filter deletions, not geometry filter / prune_isolated; (c) control is x138+safetail without insertion, not the exp85a cap-6 base; (d) the arm would also let DaughterNet attach to short FP fragments -> new FP pairs. Even 2-3x reach stays <= ~+0.005 lab with no replay path and no slot on the final day.
- Verdict: finding stands (no build, curator note). refuted=false.
