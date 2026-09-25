# h_external-data-training notes
- 2026-09-25 ~11:05 UTC: started; BRIEF read; no prior json.
- 11:15 read CONTEXT.md (L3 dorado lines 1281-1293, resume 1500+), experiments/ext_x138/DIFF.md, tools/dorado_crops.py header,
  tools/register_44b6_dorado.py header, research/discussions_summary.md. Dorado = 522 T x 505x2217x2170 at Kaggle scale;
  tracks bundle 458,519 tracks, 38,068 slots/frame (tools/dorado_crops.py). 44b6 GT = Ultrack dorado points (84% within 2.5 um).
  Only prior external-data use = dorado DaughterNet (closed: val AUC parent 0.62). Nobody trained a DETECTOR/coord head on dorado.
- public.czbiohub.org: curl from this container -> proxy 403 (blocked here; was reachable from Colab/friend A per CONTEXT).
