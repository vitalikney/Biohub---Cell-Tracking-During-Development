# arithmetic verify float-output-coords (started)
- scripts in scratchpad: roundfloor.py (variants r/f/floor/3dec), weights = D=TP+FP+FN per video (reproduces exp39 adj 0.90244 + 0.1*divJ 23/194=0.1186 -> 0.9143 OK)
- global recompute: J 122151/135729=0.90000 -> (122221)/(122221+6656+6662)=0.90174 (+0.0017) consistent with claim +0.0018; dFN=-dTP consistent; node count unchanged -> multiplier unchanged.
- scratchpad roundsafe.py/roundsafe.csv (76 s, 199 videos, same tail, D-weighted adj, video bootstrap CI90):
  all: r 0.90244 f 0.90422 (+0.00178 [0.00089,0.0027]); SAFE enc (float only when frac>=0, else round; floor(w)==round(v)) 0.90434 (+0.00190 [0.00115,0.00271])
  44b6: f +0.00195 [-0.00045,0.00428]; safe +0.00163 [-0.00087,0.00384]
  6bba: f +0.00175 [0.00078,0.00279]; safe +0.00195 [0.00115,0.00282]
  +1.0 um/axis gaussian noise (unseen-embryo proxy): rn 0.87978 fn 0.88208 -> +0.00230 (gain does NOT shrink with worse localisation)
- safe encoding is identical to today under server round() AND under int-truncation -> removes the -0.004 truncation downside; only parse error remains.
- target gap 0.97-0.948=0.022; this idea ~0.0015-0.002 = ~8% of gap.
