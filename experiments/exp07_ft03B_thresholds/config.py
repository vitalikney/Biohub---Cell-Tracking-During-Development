import os, json
os.environ["BIOHUB_HOLDOUT_JSON"] = json.dumps({"holdout": ["44b6_1d530831", "44b6_74d0c52e", "44b6_7a302da0", "44b6_87bba6c4", "44b6_9be80b04", "44b6_e28840c6", "6bba_43fea39d", "6bba_74686d6a", "6bba_b204cac7", "6bba_cdcfe533", "6bba_f20478e9", "6bba_fbc898dc"]})
os.environ.setdefault("BIOHUB_SWEEP_THRESHOLDS", "0.93,0.965,0.985")
os.environ.setdefault("BIOHUB_WEIGHTS_SUB", "exp03B")
print("sweep", os.environ["BIOHUB_SWEEP_THRESHOLDS"], os.environ["BIOHUB_WEIGHTS_SUB"])
