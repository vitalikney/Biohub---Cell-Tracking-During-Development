import datetime, os, pathlib, subprocess, sys, time
LOG = pathlib.Path("experiments/lb_poll/poll.log")
LOG.parent.mkdir(parents=True, exist_ok=True)
CMD = [sys.executable, "-m", "kaggle", "competitions", "submissions", "biohub-cell-tracking-during-development", "-v"]
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")


def poll():
    """Return (stdout, note); retries up to 3 times when the CLI prints nothing (seen 25 Sep 15:26-16:06Z)."""
    note = ""
    for attempt in range(3):
        try:
            p = subprocess.run(CMD, capture_output=True, text=True, timeout=180, env=ENV, encoding="utf-8")
            if p.stdout.strip():
                return p.stdout, note
            note += f" [empty stdout, rc={p.returncode}, stderr={p.stderr.strip()[:200]!r}]"
        except Exception as exc:  # network, CLI
            note += f" [ERROR {exc}]"
        time.sleep(30)
    return "", note


while True:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out, note = poll()
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"=== {ts}{note}\n" + "\n".join(out.strip().splitlines()[:12]) + "\n")
    time.sleep(600)
