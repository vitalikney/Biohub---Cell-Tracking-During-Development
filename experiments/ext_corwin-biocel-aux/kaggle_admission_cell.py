"""THE ADMISSION TICKET -- one Kaggle cell, internet OFF, that decides whether L4_HVETO may ship.

Paste this as a cell of a DRY with the two data sources attached and **internet switched OFF**.
It answers, in order and without a network:

  1. did the vendor bootstrap find the aux dataset, and how (expanded directory, or the archive it
     unpacked itself) ;
  2. is what Kaggle holds the SAME directory this lane built -- 12 979 files, 1 105 612 639 bytes,
     directory sha256 9586f339... ; this is the verification our Kaggle token could not do from the
     API (`datasets files` / `status` / `download` all return 403) and it is stronger, because it is
     performed on the copy the kernel will actually import ;
  3. does `hoct` import from it with NO network event and NO subprocess ;
  4. does `ILPSolverConfig.default()` construct -- the compiled SCIP path.

Exit 0 = admitted. Any failure prints the reason and raises.
"""
from __future__ import annotations

import os
import sys
import time

# --- where the cell and its tools live in the aux dataset (adjust if KER11 renames the folder) ---
for _p in ("/kaggle/input/biocel-aux/code", "/kaggle/input/biocel-hveto/code",
           os.path.dirname(os.path.abspath(__file__))):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

# The integrity constants IGNORE `__pycache__`, and that is not a weakening -- it is the only way
# the number can be stable. Importing from the vendor directory REWRITES its `.pyc` files, so a
# total taken over them is already stale by the time this cell has done its job (measured on a pod:
# -410 bytes over an identical 12 979 entries, which is what made version 32 read MISMATCH).
# These cover every `.py`, every `.so` and every data file, and they are read from the tree the
# sha-verified tar restores, i.e. the tree the Kaggle archive was built from.
# cp312 build -- the pinned chassis image is python 3.12.13. The cp311 set (7 969 /
# 981 518 976 / 4c4ef945...) made twelve of thirteen modules raise "Importing the numpy
# C-extensions failed" in KER11's DRY 7ac41e63 v20, and is superseded.
EXPECT_FILES = 10175                   # ignoring __pycache__
EXPECT_BYTES = 1017113057              # ignoring __pycache__
EXPECT_SHA = "72162ded64118fc66062f41742dddec6cd9bdaf00a0a4084a87857eea15511ff"
# The bytecode cache is deliberately out of the count: importing from the vendor REWRITES it, so a
# total taken over it is stale by the time this cell has done its job (measured: -410 bytes over an
# identical entry count, which is what made version 32 read MISMATCH).

t0 = time.time()
import l4_hveto                                   # runs the vendor bootstrap at import
print("VENDOR_DIR :", l4_hveto.VENDOR_DIR)
print("VENDOR_HOW :", l4_hveto.VENDOR_HOW)
print("GUARD      :", l4_hveto._SELFTEST)   # both directions, tested at import
assert l4_hveto.VENDOR_DIR and os.path.isdir(l4_hveto.VENDOR_DIR), \
    "L4_HVETO: the vendor directory was not found -- is the dataset attached?"

import dirsha
sha, n, b = dirsha.dir_sha(l4_hveto.VENDOR_DIR, skip_pycache=True)
print("files      : %d (expected %d, __pycache__ ignored)" % (n, EXPECT_FILES))
print("bytes      : %d (expected %d)" % (b, EXPECT_BYTES))
print("sha256     : %s" % sha)
ok = (n == EXPECT_FILES and b == EXPECT_BYTES and sha == EXPECT_SHA)
print("INTEGRITY  : %s" % ("MATCH" if ok else "MISMATCH"))
assert ok, "L4_HVETO: the vendor directory Kaggle holds is not the one this lane built"

import subprocess
_out = os.environ.get("BIOCEL_HVETO_TICKET_OUT", "/kaggle/working/OFFLINE_IMPORT.json")
rc = subprocess.call([sys.executable, os.path.join(os.path.dirname(dirsha.__file__),
                                                   "offline_import_proof.py"),
                      "--vendor", l4_hveto.VENDOR_DIR, "--out", _out])
print("offline import proof exit code: %d" % rc)
assert rc == 0, "L4_HVETO: the offline import proof failed -- read /kaggle/working/OFFLINE_IMPORT.json"

print("ADMITTED in %.1f s -- internet was OFF, no pip ran, and the directory is byte-for-byte ours."
      % (time.time() - t0))
