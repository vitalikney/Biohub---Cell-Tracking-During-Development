import os, json
os.environ["BIOHUB_HOLDOUT_JSON"] = json.dumps({"holdout": ["44b6_1d530831", "44b6_74d0c52e", "44b6_7a302da0", "44b6_87bba6c4", "44b6_9be80b04", "44b6_e28840c6", "6bba_43fea39d", "6bba_74686d6a", "6bba_b204cac7", "6bba_cdcfe533", "6bba_f20478e9", "6bba_fbc898dc"]})
os.environ.setdefault("BIOHUB_WEIGHTS_SUB", "exp03B")
os.environ.setdefault("BIOHUB_SUBMIT_VALIDATE", "1")   # self-check on hold12 (set 0 for the real submission run)
os.environ.setdefault("BIOHUB_DET_THRESHOLD", "0.965")
os.environ.setdefault("BIOHUB_PP_GAP_UM", "5.0")
os.environ.setdefault("BIOHUB_PP_DIRECT_UM", "8.0")
os.environ.setdefault("BIOHUB_ILP_DIVISION_WEIGHT", "0.6")   # v2.1: ILP creates divisions itself
os.environ.setdefault("BIOHUB_PP_DIV_PARENT_UM", "0")      # v2.1: post-hoc divisions OFF
os.environ.setdefault("BIOHUB_PP_DIV_SISTER_UM", "12.0")
print({k: v for k, v in os.environ.items() if k.startswith("BIOHUB_") and k != "BIOHUB_HOLDOUT_JSON"})
