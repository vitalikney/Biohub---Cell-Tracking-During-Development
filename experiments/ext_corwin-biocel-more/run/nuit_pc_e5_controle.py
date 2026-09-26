# -*- coding: utf-8 -*-
"""LE CONTROLE QUI TRANCHE : d'ou vient le gain de E5 ?

CE QUE S1 A MESURE
------------------
E5 est le SEUL estimateur qui fasse monter le score officiel des 199 films
(0,937383 -> 0,939438, soit +0,002054 ; edge_fp -291). Or S1 bis montre que E5
ne rapproche PAS nos noeuds des cellules annotees (gain median 0,027 um, comme
E1_r3). Deux causes possibles, et une seule est vraie :
  (H1) la LECTURE sous-voxel (E1_r3) apporte quelque chose une fois lissee ;
  (H2) c'est le LISSAGE TEMPOREL seul qui paie -- la coherence de la suite des
       positions, pas la justesse de chacune.

LE CONTROLE
-----------
`E5_SUR_E0` : EXACTEMENT la formule de E5 (0,5 / 0,25 / 0,25, voisins recales
par le mouvement median de la trame), mais appliquee a **E0** au lieu de
E1_r3. Si `E5_SUR_E0` rend le meme gain, H2 est vraie et la lecture sous-voxel
n'y est pour rien. Si le gain disparait, H1 est vraie.

Un second temoin, `E1_r3_SEUL_LISSE_0`, n'existe pas : E5 avec un poids 1,0 sur
le noeud EST E1_r3, deja mesure (score 0,936973).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

REPO = pathlib.Path("D:/Github/BIOCELL_WINNING")
sys.path.insert(0, str(REPO / "04_SRC"))
LANE = REPO / "01_PLAN/5_VICTOIRE/20_NUIT_0309"
MONDE = REPO / "05_WORK/experiments/ZEUS/2026-09-03_RADAR/JUGE/work/A0_WE_csv"
RELOC = REPO / "07_STORE/incoming/NUIT/NUIT_0309_1/RELOC"
S = np.array([1.625, 0.40625, 0.40625])


class ControleRefuse(RuntimeError):
    """Garde nommee -- jamais `assert`."""


def exige(c: bool, m: str) -> None:
    if not c:
        raise ControleRefuse(m)


def lisser(base: np.ndarray, node_id: np.ndarray, t: np.ndarray,
           uv: np.ndarray) -> tuple[np.ndarray, int]:
    """La formule de E5, recopiee du code du pod, appliquee a `base`."""
    idx = {int(v): i for i, v in enumerate(node_id)}
    pred: dict[int, list[int]] = {}
    succ: dict[int, list[int]] = {}
    for u, v in uv:
        succ.setdefault(int(u), []).append(int(v))
        pred.setdefault(int(v), []).append(int(u))
    depl: dict[int, list] = {}
    for u, v in uv:
        iu, iv = idx.get(int(u)), idx.get(int(v))
        if iu is None or iv is None:
            continue
        depl.setdefault(int(t[iu]), []).append(base[iv] - base[iu])
    med = {k: np.median(np.asarray(w, np.float64), axis=0) for k, w in depl.items()}
    out = base.copy()
    n_tri = 0
    for i in range(len(node_id)):
        nid = int(node_id[i])
        ps, ss = pred.get(nid), succ.get(nid)
        if not ps or not ss:
            continue
        ip, isu = idx.get(int(ps[0])), idx.get(int(ss[0]))
        if ip is None or isu is None:
            continue
        mp = med.get(int(t[ip]), np.zeros(3))
        mn = med.get(int(t[i]), np.zeros(3))
        out[i] = 0.5 * base[i] + 0.25 * (base[ip] + mp) + 0.25 * (base[isu] - mn)
        n_tri += 1
    return out, n_tri


def lisser_w2(base: np.ndarray, node_id: np.ndarray, t: np.ndarray,
              uv: np.ndarray) -> tuple[np.ndarray, int]:
    """Fenetre +-2 : poids 0,4 (noeud) / 0,2 (t-1, t+1) / 0,1 (t-2, t+2).
    Chaque voisin est recale par le mouvement median CUMULE des trames
    traversees -- pas par un seul deplacement : recaler un voisin a t-2 avec le
    mouvement d'une seule trame le laisserait a une trame de distance."""
    idx = {int(v): i for i, v in enumerate(node_id)}
    pred: dict[int, list[int]] = {}
    succ: dict[int, list[int]] = {}
    for u, v in uv:
        succ.setdefault(int(u), []).append(int(v))
        pred.setdefault(int(v), []).append(int(u))
    depl: dict[int, list] = {}
    for u, v in uv:
        iu, iv = idx.get(int(u)), idx.get(int(v))
        if iu is None or iv is None:
            continue
        depl.setdefault(int(t[iu]), []).append(base[iv] - base[iu])
    med = {k: np.median(np.asarray(w, np.float64), axis=0) for k, w in depl.items()}
    out = base.copy()
    n_tri = 0
    for i in range(len(node_id)):
        nid = int(node_id[i])
        chaine = {0: i}
        n = nid
        ok = True
        for k in (1, 2):                       # vers l'arriere
            ps = pred.get(n)
            if not ps or idx.get(int(ps[0])) is None:
                ok = False
                break
            n = int(ps[0]); chaine[-k] = idx[n]
        if not ok:
            continue
        n = nid
        for k in (1, 2):                       # vers l'avant
            ss = succ.get(n)
            if not ss or idx.get(int(ss[0])) is None:
                ok = False
                break
            n = int(ss[0]); chaine[k] = idx[n]
        if not ok:
            continue
        acc = 0.4 * base[i]
        for k, poids in ((-1, 0.2), (1, 0.2), (-2, 0.1), (2, 0.1)):
            j = chaine[k]
            v = base[j].copy()
            if k < 0:                           # avancer le passe vers t
                for pas in range(k, 0):
                    v = v + med.get(int(t[chaine[pas]]), np.zeros(3))
            else:                               # reculer le futur vers t
                for pas in range(k - 1, -1, -1):
                    v = v - med.get(int(t[chaine[pas]]), np.zeros(3))
            acc = acc + poids * v
        out[i] = acc
        n_tri += 1
    return out, n_tri


def lisser_hors_division(base: np.ndarray, node_id: np.ndarray,
                         t: np.ndarray, uv: np.ndarray):
    """La MEME formule, mais qui SAUTE tout noeud dont le predecesseur ou le
    successeur est ambigu : deux successeurs (mitose) ou deux predecesseurs.

    Pourquoi : `lisser` prend `succ[nid][0]`, c'est-a-dire le PREMIER successeur
    dans l'ordre des aretes. A une division, ce choix est arbitraire, et il
    deplace le noeud vers une seule des deux filles. La variante mesure ce que
    cet arbitraire coute -- ou rapporte. Elle rend aussi le compte des noeuds
    concernes.
    """
    idx = {int(v): i for i, v in enumerate(node_id)}
    pred: dict[int, list[int]] = {}
    succ: dict[int, list[int]] = {}
    for u, v in uv:
        succ.setdefault(int(u), []).append(int(v))
        pred.setdefault(int(v), []).append(int(u))
    depl: dict[int, list] = {}
    for u, v in uv:
        iu, iv = idx.get(int(u)), idx.get(int(v))
        if iu is None or iv is None:
            continue
        depl.setdefault(int(t[iu]), []).append(base[iv] - base[iu])
    med = {k: np.median(np.asarray(w, np.float64), axis=0)
           for k, w in depl.items()}
    out = base.copy()
    n_tri = 0
    n_saute = 0
    for i in range(len(node_id)):
        nid = int(node_id[i])
        ps, ss = pred.get(nid), succ.get(nid)
        if not ps or not ss:
            continue
        if len(ss) > 1 or len(ps) > 1:
            n_saute += 1
            continue
        ip, isu = idx.get(int(ps[0])), idx.get(int(ss[0]))
        if ip is None or isu is None:
            continue
        mp = med.get(int(t[ip]), np.zeros(3))
        mn = med.get(int(t[i]), np.zeros(3))
        out[i] = 0.5 * base[i] + 0.25 * (base[ip] + mp) + 0.25 * (base[isu] - mn)
        n_tri += 1
    return out, n_tri, n_saute


K_LOCAL = 20
#: Nombre de voisins A0 de la MEME trame sur lesquels la mediane du mouvement
#: est prise. 20 est la valeur du mandat implicite « local » lue comme un
#: voisinage de l'ordre de la dizaine ; elle n'a PAS ete balayee sur le score.


def lisser_local(base: np.ndarray, node_id: np.ndarray, t: np.ndarray,
                 uv: np.ndarray, k: int = K_LOCAL):
    """La formule de E5 hors mitose, mais le mouvement median est pris sur les
    `k` plus proches voisins A0 de la trame QUI PORTENT UNE ARETE, au lieu de
    toute la trame."""
    from scipy.spatial import cKDTree
    S_ = np.array([1.625, 0.40625, 0.40625])
    idx = {int(v): i for i, v in enumerate(node_id)}
    pred: dict[int, list[int]] = {}
    succ: dict[int, list[int]] = {}
    for u, v in uv:
        succ.setdefault(int(u), []).append(int(v))
        pred.setdefault(int(v), []).append(int(u))
    # deplacements par trame de depart, avec la position de leur source
    src: dict[int, list[int]] = {}
    vec: dict[int, list] = {}
    for u, v in uv:
        iu, iv = idx.get(int(u)), idx.get(int(v))
        if iu is None or iv is None:
            continue
        tu = int(t[iu])
        src.setdefault(tu, []).append(iu)
        vec.setdefault(tu, []).append(base[iv] - base[iu])
    arbres = {}
    for tu, ii in src.items():
        pts = base[np.asarray(ii)] * S_[None, :]
        arbres[tu] = (cKDTree(pts), np.asarray(vec[tu], np.float64))

    def med_locale(tu: int, point: np.ndarray) -> np.ndarray:
        e = arbres.get(tu)
        if e is None:
            return np.zeros(3)
        arbre, vs = e
        kk = min(k, len(vs))
        _d, j = arbre.query(point * S_, k=kk)
        j = np.atleast_1d(j)
        return np.median(vs[j], axis=0)

    out = base.copy()
    n_tri = 0
    for i in range(len(node_id)):
        nid = int(node_id[i])
        ps, ss = pred.get(nid), succ.get(nid)
        if not ps or not ss or len(ss) > 1 or len(ps) > 1:
            continue
        ip, isu = idx.get(int(ps[0])), idx.get(int(ss[0]))
        if ip is None or isu is None:
            continue
        mp = med_locale(int(t[ip]), base[ip])
        mn = med_locale(int(t[i]), base[i])
        out[i] = 0.5 * base[i] + 0.25 * (base[ip] + mp) + 0.25 * (base[isu] - mn)
        n_tri += 1
    return out, n_tri, 0


def juger_une(args) -> dict:
    film, variante = args
    from lifetwin.radar import juge as J
    m = J.charger_parquet(film, MONDE)
    d = np.load(RELOC / f"{film}.npz", allow_pickle=False)
    exige(bool(np.array_equal(d["node_id"].astype(np.int64), m.node_id)),
          f"{film}: ordre des node_id different entre npz et monde")
    e0 = m.zyx.copy()
    if variante == "E5_SUR_E0":
        p, n_tri = lisser(e0.copy(), m.node_id, m.t, m.edges)
    elif variante == "E5_REJOUE":
        p, n_tri = lisser(d["E1_r3"].astype(np.float64), m.node_id, m.t, m.edges)
    elif variante == "E5_SUR_E0_ARRONDI":
        # LE SEUL CHIFFRE LIVRABLE : la page Evaluation impose des coordonnees
        # ENTIERES. On arrondit APRES le lissage, axe par axe.
        p, n_tri = lisser(e0.copy(), m.node_id, m.t, m.edges)
        p = np.round(p)
    elif variante == "E5_ARRONDI":
        p, n_tri = lisser(d["E1_r3"].astype(np.float64), m.node_id, m.t, m.edges)
        p = np.round(p)
    elif variante == "E5_SUR_E0_Z_SEUL":
        q, n_tri = lisser(e0.copy(), m.node_id, m.t, m.edges)
        p = e0.copy()
        p[:, 0] = q[:, 0]
    elif variante == "E5_SUR_E0_XY_SEUL":
        q, n_tri = lisser(e0.copy(), m.node_id, m.t, m.edges)
        p = e0.copy()
        p[:, 1:] = q[:, 1:]
    elif variante == "E5_SUR_E0_Z_SEUL_ARRONDI":
        q, n_tri = lisser(e0.copy(), m.node_id, m.t, m.edges)
        p = e0.copy()
        p[:, 0] = np.round(q[:, 0])
    elif variante == "E5_SUR_E0_HORS_DIVISION":
        p, n_tri, n_saute = lisser_hors_division(e0.copy(), m.node_id, m.t,
                                                 m.edges)
    elif variante == "E5_SUR_E0_HORS_DIVISION_ARRONDI":
        p, n_tri, n_saute = lisser_hors_division(e0.copy(), m.node_id, m.t,
                                                 m.edges)
        p = np.round(p)
    elif variante == "E5_SUR_E0_LOCAL":
        p, n_tri, _ = lisser_local(e0.copy(), m.node_id, m.t, m.edges)
    elif variante == "E5_SUR_E0_LOCAL_ARRONDI":
        p, n_tri, _ = lisser_local(e0.copy(), m.node_id, m.t, m.edges)
        p = np.round(p)
    elif variante == "E5_SUR_E0_W2":
        p, n_tri = lisser_w2(e0.copy(), m.node_id, m.t, m.edges)
    elif variante == "E5_SUR_E0_W2_ARRONDI":
        p, n_tri = lisser_w2(e0.copy(), m.node_id, m.t, m.edges)
        p = np.round(p)
    else:
        raise ControleRefuse(f"variante inconnue : {variante}")
    # la porte de 7 um, comme sur le pod
    dv = (p - m.zyx) * S[None, :]
    r = np.sqrt((dv ** 2).sum(axis=1))
    hors = (~np.isfinite(r)) | (r > 7.0)
    p[hors] = m.zyx[hors]
    m.zyx = p
    ligne = J.juger_film(m)
    ligne["variante"] = variante
    ligne["n_triangules"] = int(n_tri)
    ligne["n_hors_porte"] = int(hors.sum())
    return ligne


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--variantes", default="E5_SUR_E0,E5_REJOUE")
    a = ap.parse_args()
    from lifetwin.radar import juge as J
    films = sorted(p.stem for p in RELOC.glob("*.npz"))
    exige(len(films) == 199, f"{len(films)} films au lieu de 199")
    ref = json.loads((LANE / "recus" / "R_NUIT_RELOC_SCORING.json").read_text(
        encoding="utf-8"))["resume"]
    anc = LANE / "recus" / "R_NUIT_E5_CONTROLE.json"
    precedent = json.loads(anc.read_text(encoding="utf-8")) if anc.is_file() else {}
    out = {"date_u": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "regime": "EVAL_ONLY", "groupe": "199 films",
           "reference": {k: ref[k]["score"] for k in ("E0", "E1_r3", "E5")},
           "resume": dict(precedent.get("resume", {})),
           "delta_vs_E0": dict(precedent.get("delta_vs_E0", {})),
           "par_embryon": dict(precedent.get("par_embryon", {})),
           "par_film": dict(precedent.get("par_film", {}))}
    t0 = time.time()
    for variante in [v for v in a.variantes.split(",") if v]:
        with ProcessPoolExecutor(max_workers=a.procs) as ex:
            lignes = list(ex.map(juger_une, [(f, variante) for f in films],
                                 chunksize=4))
        r = J.agreger(lignes)
        out["resume"][variante] = {k: (float(v) if isinstance(
            v, (int, float, np.floating)) else v) for k, v in r.items()}
        out["resume"][variante]["n_triangules"] = int(
            sum(l["n_triangules"] for l in lignes))
        # CONTROLE BILATERAL : le gain doit se voir sur LES DEUX embryons, pas
        # sur leur moyenne. Un gain porte par un seul embryon serait un accident
        # de population, pas un geste.
        out.setdefault("par_embryon", {})[variante] = {}
        for emb in ("44b6", "6bba"):
            sel = [l for l in lignes if l["dataset"].startswith(emb)]
            if sel:
                # NE PAS nommer cette variable `a` : elle masquerait l'espace
                # de noms argparse du meme nom (bug attrape a la relecture).
                ag = J.agreger(sel)
                out["par_embryon"][variante][emb] = {
                    "n_films": len(sel),
                    "score": float(ag["score"]),
                    "edge_tp": int(ag["edge_tp"]), "edge_fp": int(ag["edge_fp"]),
                    "edge_fn": int(ag["edge_fn"])}
        out.setdefault("par_film", {})[variante] = {
            l["dataset"]: {k: float(l[k]) for k in
                           ("edge_tp", "edge_fp", "edge_fn", "adj_edge_jaccard")}
            for l in lignes}
        out["delta_vs_E0"][variante] = {
            "score": float(r["score"] - ref["E0"]["score"]),
            "edge_tp": int(r["edge_tp"] - ref["E0"]["edge_tp"]),
            "edge_fp": int(r["edge_fp"] - ref["E0"]["edge_fp"]),
            "edge_fn": int(r["edge_fn"] - ref["E0"]["edge_fn"])}
        print(f"{variante:<12} score={r['score']:.6f} "
              f"delta={r['score'] - ref['E0']['score']:+.6f} "
              f"fp={int(r['edge_fp'])}", flush=True)
    # LE VERDICT, ecrit par la mesure
    g5 = ref["E5"]["score"] - ref["E0"]["score"]
    g0 = out["delta_vs_E0"]["E5_SUR_E0"]["score"]
    out["verdict"] = {
        "gain_E5_sur_E1_r3": g5,
        "gain_E5_sur_E0": g0,
        "part_du_gain_expliquee_par_le_lissage_seul": (g0 / g5) if g5 else None,
        "lecture": ("H2 : le gain vient du LISSAGE TEMPOREL, pas de la lecture "
                    "sous-voxel" if g0 >= 0.8 * g5 else
                    "H1 : la lecture sous-voxel porte l'essentiel du gain"
                    if g0 <= 0.2 * g5 else
                    "les deux contribuent ; parts publiees, aucune conclusion "
                    "tranchee")}
    out["secondes"] = round(time.time() - t0, 1)
    dest = LANE / "recus" / "R_NUIT_E5_CONTROLE.json"
    dest.write_text(json.dumps(out, indent=1, ensure_ascii=False, default=float),
                    encoding="utf-8")
    print(json.dumps(out["verdict"], indent=1, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
