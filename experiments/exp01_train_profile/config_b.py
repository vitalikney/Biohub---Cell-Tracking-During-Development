import os
os.environ["BIOHUB_PROF_EXTRA_FLAGS"] = "--amp --no-grad-ckpt"
os.environ["BIOHUB_PROF_MAX_ITERS"] = "150"
print("profile flags:", os.environ["BIOHUB_PROF_EXTRA_FLAGS"])
