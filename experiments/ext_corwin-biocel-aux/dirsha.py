"""ENG/HVETO -- the directory sha, reproduced portably.

The reference number was produced on Linux by

    cd <dir> && find . -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum

which is NOT portable to Git Bash on Windows: coreutils there defaults to BINARY mode and prints
`<hash> *./path` (space + asterisk) instead of `<hash>  ./path` (two spaces), so the outer hash of
the same bytes comes out different. `sort` is also locale-sensitive.

This reimplements the pipeline byte for byte, with the ordering pinned to raw byte order (the C
locale, which is what an unset LC_ALL gives on the pod). It is validated by running it on the SAME
machine that produced the reference: if it prints the reference there, it is the reference here.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys


def dir_sha(root: str, skip_pycache: bool = False):
    """`skip_pycache=True` ignores `__pycache__/` and `*.pyc`.

    THIS IS NOT COSMETIC AND IT COST A KAGGLE RUN. A vendor directory that is imported FROM is
    rewritten BY the import: CPython refreshes `__pycache__/*.pyc` in place, so the byte total moves
    (measured: -410 bytes over the same 12 979 entries) and any pinned hash is stale the moment the
    cell it protects has run once. The integrity check must therefore cover what nobody rewrites --
    every `.py`, every `.so`, every data file -- and ignore the bytecode cache, which is derived.
    """
    root = os.path.abspath(root)
    paths = []
    for r, dirs, files in os.walk(root):
        dirs.sort()
        if skip_pycache and "__pycache__" in dirs:
            dirs.remove("__pycache__")
        for f in files:
            if skip_pycache and f.endswith(".pyc"):
                continue
            p = os.path.join(r, f)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            rel = "./" + os.path.relpath(p, root).replace(os.sep, "/")
            paths.append(rel)
    paths.sort(key=lambda s: s.encode("utf-8", "surrogateescape"))
    outer = hashlib.sha256()
    total = 0
    for rel in paths:
        h = hashlib.sha256()
        with open(os.path.join(root, rel[2:]), "rb") as fh:
            for c in iter(lambda: fh.read(1 << 20), b""):
                h.update(c)
                total += len(c)
        outer.update(("%s  %s\n" % (h.hexdigest(), rel)).encode("utf-8", "surrogateescape"))
    return outer.hexdigest(), len(paths), total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--expect", default="")
    ap.add_argument("--skip-pycache", action="store_true")
    a = ap.parse_args()
    sha, n, b = dir_sha(a.dir, skip_pycache=a.skip_pycache)
    print("dir     %s%s" % (os.path.abspath(a.dir),
                            "  (__pycache__ ignored)" if a.skip_pycache else ""))
    print("files   %d" % n)
    print("bytes   %d" % b)
    print("sha256  %s" % sha)
    if a.expect:
        ok = (sha == a.expect)
        print("EXPECT  %s -> %s" % (a.expect, "MATCH" if ok else "MISMATCH"))
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
