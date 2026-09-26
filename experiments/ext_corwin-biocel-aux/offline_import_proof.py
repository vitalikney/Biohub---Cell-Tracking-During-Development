"""ENG/HVETO -- prove that importing `hoct` from a vendored directory touches NO network.

The container we were given refuses `unshare -n` (Operation not permitted) and carries no
`iptables`, so a true `--network none` namespace cannot be created on a RunPod pod. What CAN be
enforced, and is in one respect stricter, is a **Python audit hook that aborts the process on any
network or subprocess event**: it does not wait for a connection to fail, it forbids the attempt.

Enforced here, all of them fatal:
    socket.connect · socket.getaddrinfo · socket.gethostbyname · urllib.Request
    subprocess.Popen / os.exec* / os.system   (so a hidden `pip install` cannot pass either)
plus `PIP_NO_INDEX=1`, `PIP_NO_NETWORK=1`, and the proxy variables pointed at the discard port.

Run it with the vendor directory as the ONLY extra path:
    PYTHONPATH=<vendor> PYTHONNOUSERSITE=1 python3 offline_import_proof.py --vendor <vendor>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

VIOLATIONS = []
FATAL_PREFIXES = ("socket.connect", "socket.getaddrinfo", "socket.gethostbyname",
                  "urllib.Request", "ftplib.connect", "http.client.connect")
# A subprocess during import is not a network call, but it IS worth naming: some wheels shell out
# to probe the CPU. Anything outside this whitelist is fatal, because a hidden `pip` would land here.
SUBPROC_ALLOWED = ("lscpu", "uname", "getconf", "nproc")
SUBPROC_EVENTS = ("subprocess.Popen", "os.exec", "os.system", "os.spawn")
SUBPROCESSES = []

# ---------------------------------------------------------------------------
# ENG/KER11 2026-09-12T22:1xZ, ownership transferred by ZEUS for this fix only
# (ruling KER11-NIGHT-2 (e)). THE DEFECT THIS REPAIRS, in one sentence: on the
# real Kaggle image this proof called a LOCAL LIBRARY LOOKUP a network event and
# failed a run in which thirteen modules imported, five symbols resolved and
# ILPSolverConfig constructed -- with ZERO socket, DNS or urllib events.
#
# `ctypes.util.find_library` on Linux locates a shared object by shelling out:
# first `/sbin/ldconfig -p`, then, if that fails, `gcc -Wl,-t -o /tmp/... -l<name>`
# and `ld -t -L... -l<name>`. That is CPython's own documented implementation. It
# reads a cache and links a throwaway object ; it opens no socket and resolves no
# name, and it behaves identically in an airgapped box. numpy, torch and several
# wheels call it at import.
#
# So the triple is recorded under its own key, COUNTED and PRINTED -- never
# dropped -- and it does not fail the proof unless its argv carries something
# network-capable. `PASS` is false on a socket / DNS / urllib event, or on ANY
# OTHER subprocess: a hidden `pip install` still lands in the fatal branch,
# which is the property the original was defending and which is preserved here.
LOCAL_TOOLCHAIN = ("ldconfig", "gcc", "cc", "ld", "ld.so", "ld.bfd", "ld.gold")
LOCAL_TOOLCHAIN_CALLS = []
# an argv that could reach the network, even from a toolchain binary
NETWORKY = ("://", "http", "https", "ftp", "ssh", "scp", "curl", "wget", "@",
            "pip", "index-url", "extra-index", "--find-links")


def _networky(args):
    """Does this call carry anything that could reach the network ? Read from the
    argv the hook already captures -- no new instrumentation, no guessing."""
    try:
        flat = repr(args)
    except Exception:
        return "unreadable-argv"
    low = flat.lower()
    for tok in NETWORKY:
        if tok in low:
            return tok
    return ""


def _hook(event, args):
    for p in SUBPROC_EVENTS:
        if event.startswith(p):
            exe = ""
            try:
                exe = str(args[0])
            except Exception:
                pass
            SUBPROCESSES.append((event, exe[:120]))
            base = os.path.basename(exe.strip().split()[0]) if exe.strip() else ""
            if base in LOCAL_TOOLCHAIN:
                why = _networky(args)
                LOCAL_TOOLCHAIN_CALLS.append((event, exe[:120], repr(args)[:200], why))
                if why:
                    VIOLATIONS.append((event, "toolchain call carrying %r : %s"
                                       % (why, repr(args)[:160])))
                    raise PermissionError(
                        "OFFLINE PROOF: %s called with a network-capable argument %r"
                        % (base, why))
                return
            if base not in SUBPROC_ALLOWED:
                VIOLATIONS.append((event, repr(args)[:200]))
                raise PermissionError("OFFLINE PROOF: forbidden subprocess %r during import" % exe)
            return
    for p in FATAL_PREFIXES:
        if event.startswith(p):
            # loopback is not the network; everything else aborts
            if event.startswith("socket.connect"):
                try:
                    addr = args[1]
                    if isinstance(addr, tuple) and addr and str(addr[0]) in ("127.0.0.1", "::1"):
                        return
                except Exception:
                    pass
            VIOLATIONS.append((event, repr(args)[:200]))
            raise PermissionError("OFFLINE PROOF: forbidden event %r during import" % event)



# ===========================================================================
# BATTLE_RULES AMENDMENT 10(a) : A GUARD SHIPS WITH A PASSING FIXTURE DRAWN
# FROM THE REAL ENVIRONMENT IT PROTECTS, BESIDE ITS REFUSING ONE.
#
# The ADMITTING fixture below is not invented. It is the argv of the three calls
# this proof actually recorded on Kaggle, image
# gcr.io/kaggle-private-byod/python@sha256:37c64f7d..., python 3.12.13, internet
# OFF, in version 21 of corwin1979/biocel-run-7ac41e63 at 2026-09-12T21:44:00Z --
# the run this guard failed. Before the fix it produced PASS false with three
# "network_violations" on a run whose `failures` list was empty. After the fix it
# must PASS, and the refusing fixture must still refuse.
# ===========================================================================
FIXTURE_ADMIT = [   # verbatim shapes from the version-21 audit output
    ("subprocess.Popen",
     ("/sbin/ldconfig", ["/sbin/ldconfig", "-p"], None, {"LC_ALL": "C", "LANG": "C"})),
    ("subprocess.Popen",
     ("/usr/bin/gcc", ["/usr/bin/gcc", "-Wl,-t", "-o", "/tmp/tmp76rfnbtz", "-ldl"],
      None, {"SHELL": "/bin/bash", "NV_LIBCUBLAS_VERSION": "12.8.4.1-1"})),
    ("subprocess.Popen",
     ("ld", ["ld", "-t", "-L", "/usr/local/nvidia/lib64", "-L", "/usr/local/cuda/lib64",
             "-o", "/dev/null", "-ldl"], None, None)),
]
FIXTURE_REFUSE = [
    ("subprocess.Popen", ("/usr/bin/pip", ["pip", "install", "hoct"], None, None)),
    ("subprocess.Popen", ("/usr/bin/curl", ["curl", "https://pypi.org/simple"], None, None)),
    ("subprocess.Popen",
     ("/usr/bin/gcc", ["gcc", "--index-url", "https://pypi.org/simple"], None, None)),
]


def _selftest():
    """Both directions, on the real environment's own output."""
    global VIOLATIONS, SUBPROCESSES, LOCAL_TOOLCHAIN_CALLS
    ok = []
    VIOLATIONS, SUBPROCESSES, LOCAL_TOOLCHAIN_CALLS = [], [], []
    for ev, args in FIXTURE_ADMIT:
        _hook(ev, args)
    assert not VIOLATIONS, VIOLATIONS
    assert len(LOCAL_TOOLCHAIN_CALLS) == 3, LOCAL_TOOLCHAIN_CALLS
    ok.append("the REAL version-21 triple is admitted, counted 3, and not dropped")

    for i, (ev, args) in enumerate(FIXTURE_REFUSE):
        VIOLATIONS, SUBPROCESSES, LOCAL_TOOLCHAIN_CALLS = [], [], []
        try:
            _hook(ev, args)
        except PermissionError:
            assert VIOLATIONS, i
            continue
        raise AssertionError("fixture %d was NOT refused: %r" % (i, args))
    ok.append("pip, curl and a gcc carrying --index-url are all still refused")

    VIOLATIONS, SUBPROCESSES, LOCAL_TOOLCHAIN_CALLS = [], [], []
    try:
        _hook("socket.getaddrinfo", ("pypi.org", 443))
    except PermissionError:
        ok.append("a DNS lookup is still fatal")
    else:
        raise AssertionError("a DNS lookup was not refused")

    VIOLATIONS, SUBPROCESSES, LOCAL_TOOLCHAIN_CALLS = [], [], []
    _hook("socket.connect", (None, ("127.0.0.1", 8888)))
    assert not VIOLATIONS
    ok.append("loopback is still not the network")

    for i, s_ in enumerate(ok, 1):
        print("  %d PASS  %s" % (i, s_))
    print("[ker11] offline-proof selftest PASS : %d cases, an ADMITTING fixture "
          "taken from the real version-21 audit output and three refusing ones." % len(ok))
    return 0


def main():
    if "--selftest" in sys.argv:
        return _selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument("--vendor", required=True)
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"):
        os.environ[k] = "http://127.0.0.1:9"
    os.environ["PIP_NO_INDEX"] = "1"
    os.environ["PIP_NO_NETWORK"] = "1"
    os.environ["NO_PROXY"] = ""

    assert os.path.isdir(a.vendor), a.vendor
    if a.vendor not in sys.path:
        sys.path.insert(0, a.vendor)

    sys.addaudithook(_hook)

    mods = ["numpy", "torch", "scipy.ndimage", "skimage.segmentation", "zarr", "dask.array",
            "tracksdata", "hoct", "hoct.features", "hoct.inference", "hoct.inference._predict",
            "hoct._api", "hoct.tracking"]
    rows, bad = [], []
    t0 = time.time()
    for m in mods:
        t1 = time.time()
        try:
            mod = __import__(m, fromlist=["x"])
            f = getattr(mod, "__file__", "") or ""
            where = "VENDOR" if ("/" + os.path.basename(a.vendor.rstrip("/")) + "/") in f \
                else ("image" if f else "builtin")
            rows.append(dict(module=m, ok=True, source=where, file=f,
                             version=str(getattr(mod, "__version__", "")),
                             seconds=round(time.time() - t1, 3)))
            print("  OK   %-28s %-7s %-12s %.2fs" % (m, where,
                                                     getattr(mod, "__version__", ""),
                                                     time.time() - t1), flush=True)
        except Exception as e:
            bad.append(m)
            rows.append(dict(module=m, ok=False, error=repr(e)[:300],
                             seconds=round(time.time() - t1, 3)))
            print("  FAIL %-28s %s" % (m, repr(e)[:200]), flush=True)

    sym = {}
    try:
        from hoct._api import _create_dataset            # noqa: F401
        from hoct.features import create_graph           # noqa: F401
        from hoct.inference import model_predict         # noqa: F401
        import hoct.inference._predict as _p             # noqa: F401
        from hoct.tracking import ILPSolverConfig
        sym["five_symbols"] = True
        try:
            c = ILPSolverConfig.default()
            sym["ILPSolverConfig_default"] = type(c).__name__
        except Exception as e:
            sym["ILPSolverConfig_default"] = "FAILED: " + repr(e)[:200]
    except Exception as e:
        sym["five_symbols"] = "FAILED: " + repr(e)[:300]

    res = dict(vendor=a.vendor, python=sys.version.split()[0],
               modules=rows, failures=bad, symbols=sym,
               network_violations=VIOLATIONS, subprocesses=SUBPROCESSES,
               local_toolchain_calls=LOCAL_TOOLCHAIN_CALLS,
               local_toolchain_count=len(LOCAL_TOOLCHAIN_CALLS),
               _local_toolchain_note=("ctypes.util.find_library shells out to "
                                      "ldconfig / gcc / ld to LOCATE a shared "
                                      "object. Counted and printed here, never "
                                      "dropped ; fatal only if the argv carries "
                                      "something network-capable."),
               total_import_seconds=round(time.time() - t0, 2),
               PASS=bool(not bad and sym.get("five_symbols") is True and not VIOLATIONS))
    print(json.dumps({k: res[k] for k in ("failures", "symbols", "network_violations",
                                          "subprocesses", "local_toolchain_calls",
                                          "local_toolchain_count",
                                          "total_import_seconds", "PASS")},
                     indent=1))
    if a.out:
        with open(a.out, "w") as fh:
            json.dump(res, fh, indent=1)
    return 0 if res["PASS"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
