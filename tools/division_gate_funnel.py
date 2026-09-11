"""Gate-by-gate survival of the 151 REAL divisions under the public safe-division gate stack.
Measured on ground-truth geometry only (no model), so it is an upper bound on what the gate can ever reach."""
import os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "tools/official/src"); sys.path.insert(0, "tools/official/scripts")
from pathlib import Path
import numpy as np, tracksdata as td
DATA = Path("biohub-cell-tracking-during-development/train")
SCALE = np.array([1.625, 0.40625, 0.40625])
EXIST_CHILD_MAXU, MAXU, SISTER_MAXU, TAU, DIVERGE = 10.0, 9.0, 14.0, 0.6, 2.25

rows = []
for g in sorted(DATA.glob("*.geff")):
    try:
        pr = td.graph.IndexedRXGraph.from_geff(g)
        gr = pr[0] if isinstance(pr, tuple) else pr
    except Exception:
        continue
    na = gr.node_attrs().to_pandas().set_index("node_id")
    pos = {int(i): np.array([r.z, r.y, r.x]) * SCALE for i, r in na.iterrows()}
    tt = {int(i): int(r.t) for i, r in na.iterrows()}
    out = {}
    for s, d in gr.edge_list():
        out.setdefault(int(s), []).append(int(d))
    for s, ch in out.items():
        if len(ch) != 2:
            continue
        d0, d1 = ch
        a, b = np.linalg.norm(pos[s]-pos[d0]), np.linalg.norm(pos[s]-pos[d1])
        # the gate treats one daughter as the "existing child" and the other as the candidate;
        # the ranker keeps the tighter one as existing child, so take min as existing, max as candidate
        child_dist, parent_dist = float(min(a, b)), float(max(a, b))
        sister = float(np.linalg.norm(pos[d0]-pos[d1]))
        gc = []
        for c in (d0, d1):
            k = out.get(c, [])
            gc.append(k[0] if len(k) == 1 and tt.get(k[0]) == tt[s]+2 else None)
        gdist = float(np.linalg.norm(pos[gc[0]]-pos[gc[1]])) if all(x is not None for x in gc) else None
        rows.append(dict(child=child_dist, parent=parent_dist, sister=sister,
                         sym=abs(child_dist-parent_dist)/max((child_dist+parent_dist)/2, 1e-6),
                         gdist=gdist))

n = len(rows)
print(f"real divisions analysed: {n}\n")
alive = [True]*n
def step(name, fn):
    global alive
    before = sum(alive)
    alive = [a and fn(r) for a, r in zip(alive, rows)]
    after = sum(alive)
    print(f"{name:38} {after:4d}/{n}  ({100*after/n:5.1f}%)   lost {before-after}")

print("CUMULATIVE survival through the public gate stack (GT geometry, best case):")
step("start", lambda r: True)
step(f"existing-child dist <= {EXIST_CHILD_MAXU}", lambda r: r['child'] <= EXIST_CHILD_MAXU)
step(f"parent dist <= {MAXU}", lambda r: r['parent'] <= MAXU)
step(f"sister dist <= {SISTER_MAXU}", lambda r: r['sister'] <= SISTER_MAXU)
step(f"divergence: gc_dist - sister >= {DIVERGE}", lambda r: r['gdist'] is not None and r['gdist']-r['sister'] >= DIVERGE)
step(f"symmetry ratio <= {TAU}", lambda r: r['sym'] <= TAU)

print("\nINDIVIDUAL cost of each gate (how many of the 151 it alone rejects):")
for name, fn in [(f"existing-child > {EXIST_CHILD_MAXU}", lambda r: r['child'] > EXIST_CHILD_MAXU),
                 (f"parent > {MAXU}", lambda r: r['parent'] > MAXU),
                 (f"sister > {SISTER_MAXU}", lambda r: r['sister'] > SISTER_MAXU),
                 (f"divergence < {DIVERGE}", lambda r: not (r['gdist'] is not None and r['gdist']-r['sister'] >= DIVERGE)),
                 (f"symmetry > {TAU}", lambda r: r['sym'] > TAU)]:
    k = sum(1 for r in rows if fn(r))
    print(f"  {name:34} rejects {k:4d}  ({100*k/n:5.1f}%)")

print("\nALTERNATIVE stack: drop symmetry + divergence, add a MINIMUM sister separation")
for ms in [0, 4, 5, 6, 7]:
    keep = sum(1 for r in rows if r['child'] <= EXIST_CHILD_MAXU and r['parent'] <= MAXU
               and ms <= r['sister'] <= SISTER_MAXU)
    print(f"  min_sister={ms:<2}  real divisions reachable: {keep:4d}/{n}  ({100*keep/n:5.1f}%)")
