# -*- coding: utf-8 -*-
"""REF-DATA -- LIVRABLE 3 : les COMPOSANTES des familles, avec Delta EXACT.

Un enregistrement par composante de desaccord entre le monde KEEP (W0, temoin
epingle) et un monde CANDIDAT (W1), au schema REFEREE-SCHEMA-v0 :
  <famille>.comp.parquet   une ligne par composante (identite, enveloppe, labels)
  <famille>.nodes.parquet  une ligne par noeud     (comp_uid, monde, role, probas)
  <famille>.edges.parquet  une ligne par arete     (comp_uid, monde, role, proba)

C est la forme PHYSIQUE longue du schema : la forme LOGIQUE (nodes_keep,
nodes_cand, edges_keep, edges_cand par composante) s obtient par jointure sur
`comp_uid`. Motif : polars infere mal les listes de structs profondes, et la
forme longue se filtre et se memmappe sans deserialiser.

MACHINERIE REUTILISEE, JAMAIS REECRITE : CIBLAGE/impl/oracle_local.py (appariement
-> entites -> composantes -> monde mixte) et CIBLAGE/impl/tache_d.py (charge,
ligne, score_assiette, prepare, acceleration par trames touchees).

Le Delta d une composante est celui du JUGE OFFICIEL sur le monde ENTIER, en
ordre CANONIQUE, r=10 -- jamais un compteur local. L acceleration par trames
touchees est VERIFIEE par echantillon contre le film entier, pas supposee.

EVAL_ONLY : la GT ne sert qu a marquer `annotee` et a mesurer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, "/workspace/CIBLAGE/impl")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(
    os.environ.get("BIOCEL_REPO", "D:/Github/BIOCELL_WINNING")) / "04_SRC"))

import oracle_local as OL  # noqa: E402
import tache_d as TD  # noqa: E402
from lifetwin.radar import juge as J  # noqa: E402

SCHEMA_VERSION = "REFEREE-SCHEMA-v0"
CLES = TD.CLES
CLES_N = ("num_pred_nodes",)
CLES_A = tuple(k for k in CLES if k not in CLES_N)
PORTE = 7.0

ROLE_ENT = {"r": "retire", "a": "ajoute", "m": "deplace", "E": "keep_seule",
            "A": "cand_seule"}


def date_u() -> str:
    return subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                          capture_output=True, text=True, check=True).stdout.strip()


def uid(*parts) -> str:
    return hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()[:16]


def _degres(W, idx_par_id):
    ind = np.zeros(W.n_noeuds, dtype=np.int64)
    outd = np.zeros(W.n_noeuds, dtype=np.int64)
    for u, v in W.edges:
        outd[idx_par_id[int(u)]] += 1
        ind[idx_par_id[int(v)]] += 1
    return ind, outd


def _pm(chemin, film, echelle_iso):
    """probmat : par noeud source, meilleure et deuxieme meilleure sortante.

    Copie du geste de CIBLAGE/impl/arbitre_preuves.py (positions sur la grille
    SOUS-ECHANTILLONNEE isotrope 1,625 um).
    """
    if not chemin:
        return None
    p = pathlib.Path(chemin) / f"{film}.npz"
    if not p.is_file():
        return None
    z = np.load(p, allow_pickle=True)
    if "pm_coords" not in z or "pm_src" not in z:
        return None
    coords = np.asarray(z["pm_coords"])
    src = np.asarray(z["pm_src"]).astype(np.int64)
    dst = np.asarray(z["pm_tgt"]).astype(np.int64) if "pm_tgt" in z else None
    prob = np.asarray(z["pm_prob"]).astype(np.float64)
    n = len(coords)
    p1 = np.zeros(n)
    p2 = np.zeros(n)
    deg = np.zeros(n, dtype=np.int64)
    for i, pr in zip(src, prob):
        deg[i] += 1
        if pr > p1[i]:
            p2[i] = p1[i]
            p1[i] = pr
        elif pr > p2[i]:
            p2[i] = pr
    q1 = np.zeros(n)
    q2 = np.zeros(n)
    if dst is not None:
        for j, pr in zip(dst, prob):
            if pr > q1[j]:
                q2[j] = q1[j]
                q1[j] = pr
            elif pr > q2[j]:
                q2[j] = pr
    return {"t": coords[:, 0].astype(np.int64),
            "pos": coords[:, 1:].astype(np.float64) * echelle_iso,
            "p1": p1, "p2": p2, "q1": q1, "q2": q2, "deg": deg,
            "a_dst": dst is not None}


def _arbre_pm(pm, t_val):
    from scipy.spatial import cKDTree
    if pm is None:
        return None
    cle = ("_arbre", int(t_val))
    if cle not in pm:
        m = pm["t"] == int(t_val)
        pm[cle] = (cKDTree(pm["pos"][m]) if m.any() else None, np.nonzero(m)[0])
    return pm[cle]


def _lit_pm(pm, t_val, p_um, rayon=3.25):
    """(p_out, p_out_2, p_in, p_in_2) du noeud probmat le plus proche, ou NaN."""
    a = _arbre_pm(pm, t_val)
    nan = (float("nan"),) * 4
    if a is None or a[0] is None:
        return nan
    d, k = a[0].query(p_um, k=1)
    if d > rayon:
        return nan
    i = a[1][k]
    return (float(pm["p1"][i]), float(pm["p2"][i]),
            float(pm["q1"][i]) if pm["a_dst"] else float("nan"),
            float(pm["q2"][i]) if pm["a_dst"] else float("nan"))


# ------------------------------------------------- prepare a porte reglable
def prepare(film, w0_spec, w1_spec, rayon, porte_comp):
    """`tache_d.prepare` a l identique, sauf que la PORTE DE COMPOSANTE est un
    parametre au lieu d etre la constante 7,0 um.

    POURQUOI. La porte gouverne le lien << deux entites de la MEME TRAME a moins
    de porte_um >> dans `oracle_local.composantes`. A 7,0 um -- la porte du juge --
    des doublons voisins, qui sont par definition a moins de 7 um les uns des
    autres, se retrouvent CHAINES dans une seule composante. Le grain de decision
    devient alors plus gros que le grain de l erreur, et les contributions
    s annulent a l interieur d une composante. A 0,0 um, seules les liaisons par
    ARETE subsistent : le grain redevient celui de l anomalie.
    """
    W0 = TD.charge(film, w0_spec)
    ech = J.echelle_du_film(film)
    W1 = TD.charge(film, w1_spec)
    m01, m10 = OL.appariement(W0, W1, ech, rayon)
    ent = OL.entites(W0, W1, m01, m10, ech)
    a0, a1, a1_p, d0, d1 = OL.aretes_differentes(W0, W1, m01, m10)
    ent = OL.entites_d_aretes(ent, W0, W1, a0, a1, d0, d1)
    if len(ent["type"]) == 0:
        return W0, W1, ent, m10, a0, a1, np.zeros(0, np.int64), 0, (d0, d1)
    comp, _, _ = OL.composantes(W0, W1, ent, a0, a1, a1_p, d0, d1, ech,
                                porte_um=porte_comp)
    return W0, W1, ent, m10, a0, a1, comp, int(comp.max()) + 1, (d0, d1)


# --------------------------------------------------------------- un film
def un_film(args):
    (film, w0_spec, w1_spec, famille, palier, sha0, sha1, rayon, n_max,
     graine, n_verif, pm0_dir, pm1_dir, porte_comp) = args
    TD._idle()
    t0 = time.perf_counter()
    from scipy.spatial import cKDTree

    W0, W1, ent, m10, a0, a1, comp, nc, (d0, d1) = prepare(
        film, w0_spec, w1_spec, rayon, porte_comp)
    l0 = TD.ligne(W0)
    if nc == 0:
        # un film sans aucun desaccord : toutes les cles du contrat sont
        # presentes, sinon l agregation leve sur le dernier film.
        return film, {"n_composantes": 0, "n_composantes_annotees": 0,
                      "n_mesurees": 0, "ligne_W0": l0,
                      "ligne_W1": l0, "ligne_toutes": l0, "deltas": {},
                      "comp": [], "nodes": [], "edges": [],
                      "verification": {"n": 0, "exactes": 0, "ecarts": []},
                      "secondes": round(time.perf_counter() - t0, 1)}
    l1 = TD.ligne(W1)
    lt = TD.ligne(OL.monde_mixte(W0, W1, ent, m10, a0, a1, comp, set(range(nc))))

    ech = np.asarray(J.echelle_du_film(film), dtype=np.float64)
    P0 = W0.zyx * ech
    P1 = W1.zyx * ech
    i0 = W0.index_par_id()
    i1 = W1.index_par_id()
    ind0, outd0 = _degres(W0, i0)
    ind1, outd1 = _degres(W1, i1)
    echelle_iso = float(ech[0])
    pm0 = _pm(pm0_dir, film, echelle_iso)
    pm1 = _pm(pm1_dir, film, echelle_iso)

    arbres0 = {}
    for k in np.unique(W0.t):
        m = W0.t == int(k)
        arbres0[int(k)] = (cKDTree(P0[m]), np.nonzero(m)[0])

    # --- aretes touchees par composante (le meme geste que arbitre_preuves) ---
    ea0 = ent.get("ent_de_a0", np.full(len(a0), -1, dtype=np.int64))
    ea1 = ent.get("ent_de_a1", np.full(len(a1), -1, dtype=np.int64))
    tou0, tou1 = {}, {}
    for k in range(len(a0)):
        u, v = a0[k]
        for e in (ent["ent_de_n0"][u], ent["ent_de_n0"][v], ea0[k]):
            if e >= 0:
                tou0.setdefault(int(comp[e]), set()).add(k)
    for k in range(len(a1)):
        u, v = a1[k]
        for e in (ent["ent_de_n1"][u], ent["ent_de_n1"][v], ea1[k]):
            if e >= 0:
                tou1.setdefault(int(comp[e]), set()).add(k)
    diff0 = set(int(x) for x in d0)
    diff1 = set(int(x) for x in d1)

    annot = OL.composantes_annotees(W0, W1, ent, comp, ech, film)
    # graine DETERMINISTE : hash() de Python est randomise par processus.
    rng = np.random.default_rng(
        graine + int(hashlib.sha1(film.encode()).hexdigest()[:8], 16) % 100000)
    ia = np.nonzero(annot)[0]
    io = np.nonzero(~annot)[0]
    if n_max and len(io) > n_max:
        io = np.sort(rng.choice(io, n_max, replace=False))
    choix = np.sort(np.concatenate([ia, io])) if (len(ia) or len(io)) else np.arange(0)

    embryon = film.split("_")[0]
    cache0, deltas = {}, {}
    lignes_comp, lignes_nodes, lignes_edges = [], [], []

    for c in choix:
        c = int(c)
        tr = tuple(OL.trames_de(comp, ent, W0, W1, c))
        if tr not in cache0:
            cache0[tr] = TD.ligne(OL.restreint(W0, tr))
        Mc = OL.monde_mixte(W0, W1, ent, m10, a0, a1, comp, {c})
        ls = TD.ligne(OL.restreint(Mc, tr))
        dd = {k: ls[k] - cache0[tr][k] for k in CLES}
        deltas[c] = dd

        ks = np.nonzero(comp == c)[0]
        cu = uid(film, sha0[:12], sha1[:12], c)

        # --- noeuds de la composante, des deux cotes ---
        pts, tps = [], []
        vus0, vus1 = set(), set()
        for k in ks:
            j0 = int(ent["i0"][k])
            j1 = int(ent["i1"][k])
            typ = str(ent["type"][k])
            if j0 >= 0 and j0 not in vus0:
                vus0.add(j0)
                pts.append(P0[j0])
                tps.append(int(W0.t[j0]))
            if j1 >= 0 and j1 not in vus1:
                vus1.add(j1)
                if j0 < 0:
                    pts.append(P1[j1])
                    tps.append(int(W1.t[j1]))
        if not pts:
            continue
        pts = np.asarray(pts)
        tps = np.asarray(tps, dtype=np.int64)
        centre = pts.mean(axis=0)
        t_centre = int(np.median(tps))
        rayon_um = float(np.max(np.linalg.norm(pts - centre, axis=1))) if len(pts) > 1 else 0.0

        role_de_n0, role_de_n1 = {}, {}
        for k in ks:
            typ = str(ent["type"][k])
            j0 = int(ent["i0"][k])
            j1 = int(ent["i1"][k])
            if typ in ("r", "m") and j0 >= 0:
                role_de_n0[j0] = ROLE_ENT[typ]
            if typ in ("a", "m") and j1 >= 0:
                role_de_n1[j1] = ROLE_ENT[typ]

        def pousse(monde, j, W, P, ind, outd, pm, role):
            p = P[j]
            t = int(W.t[j])
            po, po2, pi, pi2 = _lit_pm(pm, t, p)
            arb = arbres0.get(t)
            dens = ppv = float("nan")
            if arb is not None and arb[0] is not None:
                dens = float(len(arb[0].query_ball_point(p, PORTE)))
                dq, _ = arb[0].query(p, k=min(2, len(arb[1])))
                ppv = float(np.atleast_1d(dq)[-1])
            lignes_nodes.append({
                "comp_uid": cu, "monde": monde, "id": int(W.node_id[j]),
                "dt": int(np.clip(t - t_centre, -127, 127)), "t": t,
                "dz_um": float(p[0] - centre[0]), "dy_um": float(p[1] - centre[1]),
                "dx_um": float(p[2] - centre[2]),
                "z_um": float(p[0]), "y_um": float(p[1]), "x_um": float(p[2]),
                "role": role, "edge_prob_out": po, "edge_prob_out_2": po2,
                "edge_prob_in": pi, "edge_prob_in_2": pi2,
                "degre_in": int(ind[j]), "degre_out": int(outd[j]),
                "densite_7um": dens, "dist_ppv_um": ppv,
            })

        for j in sorted(vus0):
            pousse(0, j, W0, P0, ind0, outd0, pm0, role_de_n0.get(j, "garde"))
        for j in sorted(vus1):
            pousse(1, j, W1, P1, ind1, outd1, pm1, role_de_n1.get(j, "garde"))

        # --- aretes de la composante, des deux cotes ---
        n_ar0 = n_ar1 = 0
        for k in sorted(tou0.get(c, ())):
            u, v = int(a0[k][0]), int(a0[k][1])
            lignes_edges.append({
                "comp_uid": cu, "monde": 0, "src": int(W0.node_id[u]),
                "dst": int(W0.node_id[v]),
                "dt": int(W0.t[v] - W0.t[u]),
                "prob": float(W0.conf[k]) if W0.conf is not None else float("nan"),
                "longueur_um": float(np.linalg.norm(P0[v] - P0[u])),
                "role": "keep_seule" if k in diff0 else "commune",
                "rang_ordre": int(k),
            })
            n_ar0 += 1
        for k in sorted(tou1.get(c, ())):
            u, v = int(a1[k][0]), int(a1[k][1])
            lignes_edges.append({
                "comp_uid": cu, "monde": 1, "src": int(W1.node_id[u]),
                "dst": int(W1.node_id[v]),
                "dt": int(W1.t[v] - W1.t[u]),
                "prob": float(W1.conf[k]) if W1.conf is not None else float("nan"),
                "longueur_um": float(np.linalg.norm(P1[v] - P1[u])),
                "role": "cand_seule" if k in diff1 else "commune",
                "rang_ordre": int(k),
            })
            n_ar1 += 1

        typ = ent["type"][ks]
        lignes_comp.append({
            "schema_version": SCHEMA_VERSION, "comp_uid": cu,
            "comp_key": f"{film}#{c}", "film": film, "comp_id": c,
            # le lien vers le crop, meme formule que `crops.py` : deux
            # composantes au meme endroit partagent le meme cube.
            "crop_uid": hashlib.sha1(
                ("%s|%d|%.3f|%.3f|%.3f" % (
                    film, t_centre, float(centre[0] / ech[0]),
                    float(centre[1] / ech[1]),
                    float(centre[2] / ech[2]))).encode()).hexdigest()[:16],
            # ordre ZEUS 7 : l unicite de (film, comp_id) doit etre GARANTIE
            # quand plusieurs familles cohabitent -- le numero de composante est
            # local a une paire de mondes, il se repete d une famille a l autre.
            "comp_id_prefixe": "%s_%06d" % (famille, c),
            "embryon": embryon, "famille": famille, "regime": "NATUREL",
            "palier": int(palier),
            "source_monde_keep": sha0, "source_monde_cand": sha1,
            "paire_rayon_um": float(rayon), "porte_um": PORTE, "r_um": 10.0,
            "t_min": int(tps.min()), "t_max": int(tps.max()), "t_centre": t_centre,
            "centre_z_um": float(centre[0]), "centre_y_um": float(centre[1]),
            "centre_x_um": float(centre[2]),
            "centre_z_vox": float(centre[0] / ech[0]),
            "centre_y_vox": float(centre[1] / ech[1]),
            "centre_x_vox": float(centre[2] / ech[2]),
            "echelle_z": float(ech[0]), "echelle_y": float(ech[1]),
            "echelle_x": float(ech[2]),
            "rayon_um": rayon_um, "n_trames": int(tps.max() - tps.min() + 1),
            "n_entites": int(len(ks)),
            "n_retires": int((typ == "r").sum()), "n_ajoutes": int((typ == "a").sum()),
            "n_deplaces": int((typ == "m").sum()),
            "n_aretes_keep_seules": int((typ == "E").sum()),
            "n_aretes_cand_seules": int((typ == "A").sum()),
            "n_noeuds_keep": len(vus0), "n_noeuds_cand": len(vus1),
            "n_aretes_keep": n_ar0, "n_aretes_cand": n_ar1,
            "annotee": bool(annot[c]),
            "d_edge_tp": int(dd["edge_tp"]), "d_edge_fp": int(dd["edge_fp"]),
            "d_edge_fn": int(dd["edge_fn"]),
            "d_division_tp": int(dd["division_tp"]),
            "d_division_fp": int(dd["division_fp"]),
            "d_division_fn": int(dd["division_fn"]),
            "d_num_pred_nodes": int(dd["num_pred_nodes"]),
        })

    # --- controle de l acceleration : film ENTIER contre voie restreinte ---
    verif = {"n": 0, "exactes": 0, "ecarts": []}
    if len(choix):
        for c in rng.choice(choix, size=min(n_verif, len(choix)), replace=False):
            c = int(c)
            lf = TD.ligne(OL.monde_mixte(W0, W1, ent, m10, a0, a1, comp, {c}))
            df = {k: lf[k] - l0[k] for k in CLES}
            verif["n"] += 1
            if all(abs(df[k] - deltas[c][k]) < 1e-9 for k in CLES):
                verif["exactes"] += 1
            else:
                verif["ecarts"].append({"composante": c, "entier": df,
                                        "restreint": deltas[c]})

    return film, {
        "n_composantes": nc, "n_composantes_annotees": int(annot.sum()),
        "n_mesurees": int(len(choix)),
        "ligne_W0": l0, "ligne_W1": l1, "ligne_toutes": lt,
        "deltas": {str(k): v for k, v in deltas.items()},
        "comp": lignes_comp, "nodes": lignes_nodes, "edges": lignes_edges,
        "verification": verif,
        "secondes": round(time.perf_counter() - t0, 1),
    }


# ------------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--famille", required=True)
    ap.add_argument("--films", required=True)
    ap.add_argument("--palier", type=int, required=True)
    ap.add_argument("--w0", required=True)
    ap.add_argument("--w1", required=True)
    ap.add_argument("--sha0", required=True)
    ap.add_argument("--sha1", required=True)
    ap.add_argument("--pm0", default="")
    ap.add_argument("--pm1", default="")
    ap.add_argument("--rayon", type=float, default=OL.RAYON_DEFAUT)
    ap.add_argument("--porte-composante", type=float, default=OL.PORTE_UM,
                    help="porte du lien de proximite entre entites de la MEME "
                         "trame (7,0 = la porte du juge ; 0,0 = grain anomalie)")
    ap.add_argument("--max-composantes-par-film", type=int, default=60)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--graine", type=int, default=20260905)
    ap.add_argument("--verifications-par-film", type=int, default=3)
    ap.add_argument("--sortie", default="/workspace/REFEREE/data/composantes")
    ap.add_argument("--recus", default="/workspace/REFEREE/recus")
    a = ap.parse_args()
    TD._idle()

    films = json.loads(pathlib.Path(a.films).read_text(encoding="utf-8"))["films"]
    t0 = time.perf_counter()
    taches = [(f, a.w0, a.w1, a.famille, a.palier, a.sha0, a.sha1, a.rayon,
               a.max_composantes_par_film, a.graine, a.verifications_par_film,
               a.pm0, a.pm1, a.porte_composante) for f in films]
    par_film = {}
    with Pool(min(a.workers, 24)) as p:
        for i, (f, r) in enumerate(p.imap_unordered(un_film, taches), 1):
            par_film[f] = r
            print("[%d/%d] %s : %d composantes, %d mesurees, %d s"
                  % (i, len(films), f, r["n_composantes"], r["n_mesurees"],
                     r["secondes"]), flush=True)

    base = {f: par_film[f]["ligne_W0"] for f in films}
    s0 = TD.score_assiette(base)
    s1 = TD.score_assiette({f: par_film[f]["ligne_W1"] for f in films})
    s_tout = TD.score_assiette({f: par_film[f]["ligne_toutes"] for f in films})

    def _sc(f, dd, cles):
        m = dict(base)
        m[f] = {**base[f], **{k: base[f][k] + (dd[k] if k in cles else 0.0)
                              for k in CLES}}
        return TD.score_assiette(m) - s0

    comp_rows, node_rows, edge_rows = [], [], []
    n_pos = n_neg = n_nul = 0
    somme_pos = 0.0
    for f in films:
        r = par_film[f]
        d = r["deltas"]
        for row in r["comp"]:
            c = str(row["comp_id"])
            dd = d[c]
            # ORDRE ZEUS 13:3xZ. Le score officiel se decompose en
            #   score = J_aretes + terme_de_comptage + 0,1 J_div
            # et `a_i = 1 - 0,1 (N_i - n_i)/n_i` RECOMPENSE le retrait d un
            # noeud (environ 6e-8 par noeud, gratuit sur un noeud non annote).
            # Ce qui DECIDE est donc `Delta J_aretes + 0,1 Delta J_div` ; le
            # terme de comptage part dans sa propre colonne et n entre dans
            # AUCUN label. Le Delta total reste publie pour le controle.
            ds = _sc(f, dd, CLES)          # Delta du score entier
            lp = _sc(f, dd, CLES_A)        # aretes + divisions : CE QUI DECIDE
            dc = _sc(f, dd, CLES_N)        # comptage : publie, ne decide de rien
            row["label_pay"] = float(lp)
            row["delta_comptage"] = float(dc)
            row["delta_score"] = float(ds)
            row["residu_decomposition"] = float(ds - lp - dc)
            # ORDRE ZEUS (C12) : `label_pay_valide` <=> le Delta porte une
            # PREFERENCE, c est-a-dire la composante touche une annotation. Un
            # Delta mesure sur une composante NON annotee ne porte que le terme
            # de noeuds et division_fp : il est exact, mais il ne vaut pas
            # label. Mettre True partout rendait le garde inoperant.
            row["label_pay_valide"] = bool(row["annotee"])
            row["terme_noeuds"] = float(dc)     # alias historique
            row["terme_aretes"] = float(lp)     # alias historique
            if row["annotee"]:
                row["label_pay_source"] = "SUBSTITUTION_ANNOTEE"
                # LA PREFERENCE SE LIT SUR LE TERME D ARETES, PAS SUR LE SCORE.
                # Mesure du BANC sur la famille DUPLICATE au socle r=10 :
                #   bras FUSION  score +0,0000526 = aretes -0,0000646 + comptage +0,0001172
                #   famille      score -0,0049976 = aretes -0,0119528 + comptage +0,0069552
                # Le << gain >> du bras FUSION est ENTIEREMENT le terme de
                # comptage, et son terme d aretes est NEGATIF ; sur la famille,
                # le comptage masque 58 pct de la perte. Un label pris sur le
                # score apprendrait au referee a RETIRER DES NOEUDS -- gratuit
                # dans la metrique (a_i = 1 - 0,1 (N-n)/n monte), faux dans le
                # monde, et dangereux au test cache ou le noeud retire peut
                # etre annote. C est la regle de ZEUS du 05/09, appliquee au
                # label et plus seulement au recu.
                row["label_bio"] = int(np.sign(lp))
                row["label_bio_source"] = ("ARETES_ET_DIVISIONS" if lp != 0.0
                                           else "AUCUN")
                row["label_bio_base"] = "d_J_aretes + 0,1 d_J_div"
            else:
                # GT SPARSE : une composante NON ANNOTEE ne porte JAMAIS de
                # preference. Son Delta ne vaut que par le terme de noeuds et
                # division_fp -- il sert au comptage, jamais a entrainer.
                row["label_pay_source"] = "SUBSTITUTION_TERME_NOEUDS"
                row["label_bio"] = 0
                row["label_bio_source"] = "AUCUN"
                row["label_bio_base"] = "aucune"
            if lp > 0:
                n_pos += 1
                somme_pos += lp
            elif lp < 0:
                n_neg += 1
            else:
                n_nul += 1
            comp_rows.append(row)
        node_rows.extend(r["nodes"])
        edge_rows.extend(r["edges"])

    import polars as pl
    out = pathlib.Path(a.sortie) / str(a.palier)
    out.mkdir(parents=True, exist_ok=True)

    def ecris(rows, suffixe):
        p = out / f"{a.famille}.{suffixe}.parquet"
        tmp = p.with_suffix(f".tmp{os.getpid()}")
        pl.DataFrame(rows).write_parquet(tmp)
        os.replace(tmp, p)
        return str(p), p.stat().st_size

    p_comp, o_comp = ecris(comp_rows, "comp")
    p_node, o_node = ecris(node_rows, "nodes")
    p_edge, o_edge = ecris(edge_rows, "edges")

    # --- C12 (bloquant) : aucune ligne valide sans annotation ---
    c12 = [r for r in comp_rows
           if r["label_pay_valide"] != (r["label_pay_source"] == "SUBSTITUTION_ANNOTEE")]
    if c12:
        raise SystemExit("C12 : %d lignes ou label_pay_valide ne suit pas "
                         "label_pay_source" % len(c12))

    # --- C11 (bloquant) : unicite de (film, comp_id_prefixe) ---
    vus = {}
    c11_doublons = []
    for r in comp_rows:
        cle = (r["film"], r["comp_id_prefixe"])
        if cle in vus:
            c11_doublons.append("%s|%s" % cle)
        vus[cle] = 1
    if c11_doublons:
        raise SystemExit("C11 : %d doublons (film, comp_id_prefixe), ex. %s"
                         % (len(c11_doublons), c11_doublons[:3]))

    ann = [r for r in comp_rows if r["annotee"]]
    dva = np.array([r["label_pay"] for r in ann]) if ann else np.zeros(0)
    v_n = sum(par_film[f]["verification"].get("n", 0) for f in films)
    v_e = sum(par_film[f]["verification"].get("exactes", 0) for f in films)
    ecarts = [e for f in films for e in par_film[f]["verification"]["ecarts"]]

    recu = {
        "lane": "REF-DATA", "schema_version": SCHEMA_VERSION,
        "objet": "composantes d une famille avec Delta EXACT par substitution",
        "date_u": date_u(), "famille": a.famille, "palier": a.palier,
        "regime": "EVAL_ONLY ; la GT ne sert qu a marquer annotee et a mesurer",
        "w0": a.w0, "w1": a.w1, "sha0": a.sha0, "sha1": a.sha1,
        "rayon_appariement_um": a.rayon, "porte_um": PORTE, "r_um": 10.0,
        "porte_de_composante_um": a.porte_composante,
        "n_films": len(films),
        "score_W0": s0, "score_W1": s1, "score_toutes_composantes": s_tout,
        "ecart_mecanique": abs(s_tout - s1),
        "n_composantes_total": sum(par_film[f].get("n_composantes", 0) for f in films),
        "n_composantes_annotees": sum(par_film[f].get("n_composantes_annotees", 0) for f in films),
        "n_mesurees": len(comp_rows),
        "n_positives": n_pos, "n_negatives": n_neg, "n_nulles": n_nul,
        "somme_des_deltas_positifs": somme_pos,
        "oracle_annotees_somme_positifs": float(dva[dva > 0].sum()) if len(dva) else 0.0,
        "n_annotees_mesurees": len(ann),
        "verification_de_l_acceleration": {"n": v_n, "exactes": v_e,
                                           "ecarts": ecarts[:5]},
        "fichiers": {"comp": [p_comp, o_comp], "nodes": [p_node, o_node],
                     "edges": [p_edge, o_edge]},
        "n_lignes": {"comp": len(comp_rows), "nodes": len(node_rows),
                     "edges": len(edge_rows)},
        "C12_label_pay_valide": {
            "n_valides": sum(1 for r in comp_rows if r["label_pay_valide"]),
            "n_non_valides": sum(1 for r in comp_rows if not r["label_pay_valide"]),
            "n_incoherentes": len(c12), "vert": not c12,
            "regle": "label_pay_valide <=> label_pay_source == SUBSTITUTION_ANNOTEE"},
        "C11_unicite_film_comp_id_prefixe": {"n_cles": len(vus),
                                             "n_doublons": len(c11_doublons),
                                             "vert": len(c11_doublons) == 0},
        "par_embryon": {
            e: {"n": sum(1 for r in comp_rows if r["embryon"] == e),
                "n_annotees": sum(1 for r in ann if r["embryon"] == e),
                "somme_positifs_annotees": float(sum(
                    r["label_pay"] for r in ann
                    if r["embryon"] == e and r["label_pay"] > 0))}
            for e in sorted({r["embryon"] for r in comp_rows})},
        "secondes": round(time.perf_counter() - t0, 1),
    }
    rp = pathlib.Path(a.recus)
    rp.mkdir(parents=True, exist_ok=True)
    f = rp / f"R_COMPOSANTES_{a.famille}_{a.palier}.json"
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(recu, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, f)
    print(json.dumps({k: recu[k] for k in
                      ("famille", "n_mesurees", "n_annotees_mesurees",
                       "n_positives", "n_negatives", "n_nulles",
                       "oracle_annotees_somme_positifs", "ecart_mecanique",
                       "secondes")}, ensure_ascii=False))
    print("verification acceleration : %d/%d exactes" % (v_e, v_n))


if __name__ == "__main__":
    main()
