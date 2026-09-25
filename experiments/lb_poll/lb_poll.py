import datetime, os, pathlib, subprocess, sys, time
LOG = pathlib.Path("experiments/lb_poll/poll.log")
LOG.parent.mkdir(parents=True, exist_ok=True)
CMD = [sys.executable, "-m", "kaggle", "competitions", "submissions", "biohub-cell-tracking-during-development", "-v"]
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")
while True:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        out = subprocess.run(CMD, capture_output=True, text=True, timeout=180, env=ENV, encoding="utf-8").stdout
    except Exception as exc:  # network, CLI
        out = f"ERROR {exc}"
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"=== {ts}\n" + "\n".join(out.strip().splitlines()[:10]) + "\n")
    time.sleep(600)
