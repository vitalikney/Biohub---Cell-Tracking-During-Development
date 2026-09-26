# -*- coding: utf-8 -*-
"""FAMILLE `move_nodes` PRETE POUR LE PACK -- le lissage temporel +-1 hors mitose.

CE QUE C EST, ET POURQUOI C EST UNE REGLE ET NON UN PLAN
--------------------------------------------------------
Le geste deplace 527 662 noeuds sur 60 films, donc environ 1,8 million sur 200.
Un PLAN de cette taille pese des dizaines de megaoctets, doit voyager dans le
dataset prive, et se perime des que le monde d entree change d un bit. La REGLE,
elle, tient en une fonction : elle lit le monde que le noyau vient de produire
et calcule ses deplacements. C est la seule forme qui ne peut pas se
desynchroniser de son monde -- le defaut qui a tue quatre chiffres le 05/09.

Elle est GT-FREE de bout en bout : elle ne lit que les positions, les trames et
les aretes. Aucun parametre n a ete regle sur la GT.

LA REGLE, exactement (formule IMPORTEE de `20_NUIT_0309`, non reecrite)
----------------------------------------------------------------------
Pour chaque noeud ayant EXACTEMENT un predecesseur et EXACTEMENT un successeur :
    0,5 x sa position
  + 0,25 x (predecesseur + mouvement median de la trame du predecesseur)
  + 0,25 x (successeur   - mouvement median de sa propre trame)
Les noeuds de MITOSE (deux successeurs ou deux predecesseurs) sont SAUTES : le
<< premier successeur >> serait un depart arbitraire qui tirerait le noeud vers
une seule des deux filles. Puis ARRONDI AU VOXEL, puis PORTE DE 7 um sur le
deplacement FINAL -- dans cet ordre, parce que l inverse laisse l arrondi
pousser un noeud juste au-dela de la porte.

CE QU ELLE NE TOUCHE PAS : aucune arete, aucun noeud ajoute ni retire. Elle est
donc ORTHOGONALE a l etage v17, qui n ajoute que des aretes : les deux gestes
s additionnent par construction, ils ne peuvent pas se defaire l un l autre.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time

import numpy as np

ICI = pathlib.Path(__file__).resolve().parent
SPRINT = ICI.parents[2]
_NUIT = os.environ.get("REFEVAL_NUIT_IMPL",
                       str(SPRINT.parent / "20_NUIT_0309" / "impl"))
for p in (str(ICI), _NUIT):
    if p and p not in sys.path:
        sys.path.insert(0, p)

import cell08_referee as R      # noqa: E402

#: um par voxel (z, y, x) de la grille NATIVE. Les 199 zarr d entrainement
#: portent tous cette echelle (`juge.DEFAULT_SCALE`).
S = np.array([1.625, 0.40625, 0.40625])
PORTE_UM = 7.0


def _lisser_hors_division(base, node_id, t, uv):
    """La formule de la nuit du 03/09. IMPORTEE si le module est la, sinon la
    MEME, recopiee ici pour que la famille soit AUTONOME dans le noyau Kaggle
    (le pack ne peut pas embarquer une lane entiere). Les deux chemins sont
    compares par `--parite` : ils doivent rendre le meme monde AU BIT.
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
    n_tri = n_saute = 0
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


def moves_du_film(node_id, t, zyx, edges, porte_um=PORTE_UM, lisser=None,
                  arrondi=True):
    """Les `move_nodes` d un film, et ses comptes.

    `arrondi` : la nuit du 03/09 arrondissait au voxel << impose par le format
    de soumission >>. METROLOGY a depuis etabli que le scorer HONORE les
    coordonnees flottantes (`csv_to_geffs.py` caste en Float64 sans arrondi ; un
    aller-retour CSV -> geff au bit sur 12,5 / 100,25 / 200,75). L arrondi n est
    donc PAS impose : c est un choix, et il jette de l information sous-voxel.
    On le rend optionnel pour que la question se MESURE au lieu de se supposer.
    """
    f = lisser or _lisser_hors_division
    e0 = np.asarray(zyx, dtype=np.float64)
    p, n_tri, n_saute = f(e0.copy(), node_id, t, edges)
    if arrondi:
        p = np.round(p)                   # ARRONDI PUIS PORTE, dans cet ordre
    d = (p - e0) * S[None, :]
    r = np.sqrt((d ** 2).sum(axis=1))
    hors = r > porte_um
    p[hors] = e0[hors]
    bouge = np.any(p != e0, axis=1)
    mv = [[int(node_id[i]), float(p[i, 0]), float(p[i, 1]), float(p[i, 2])]
          for i in np.nonzero(bouge)[0]]
    dep = r[bouge & ~hors]
    return mv, {"n_noeuds": int(len(node_id)), "n_lisses": int(n_tri),
                "n_sautes_mitose": int(n_saute), "n_hors_porte": int(hors.sum()),
                "n_deplaces": len(mv),
                "deplacement_median_um": float(np.median(dep)) if len(dep) else 0.0}


def detecteur(view, params=None):
    """L INTERFACE DU NOYAU : `view` -> plan. Deux reglages seulement, tous deux
    avec une valeur par defaut : `porte_um` (7,0) et `arrondi` (vrai)."""
    q = params or {}
    porte = float(q.get("porte_um", PORTE_UM))
    arrondi = bool(q.get("arrondi", True))
    plan = {}
    for film, v in view.items():
        mv, _ = moves_du_film(v["node_id"], v["t"], v["zyx"], v["edges"], porte,
                              arrondi=arrondi)
        if mv:
            plan[film] = {"move_nodes": mv}
    return plan


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--dest", required=True)
    ap.add_argument("--porte-um", type=float, default=PORTE_UM)
    ap.add_argument("--parite", action="store_true",
                    help="compare la formule RECOPIEE a la formule IMPORTEE de "
                         "la lane de la nuit : les deux doivent rendre le meme "
                         "monde AU BIT")
    ap.add_argument("--sortie", required=True)
    a = ap.parse_args()

    t0 = time.perf_counter()
    sha_in = R.sha256_fichier(a.csv)
    term, view, layout = R.scan(a.csv)
    s_scan = time.perf_counter() - t0

    t1 = time.perf_counter()
    plan, cpts = {}, {}
    for film, v in view.items():
        mv, c = moves_du_film(v["node_id"], v["t"], v["zyx"], v["edges"],
                              a.porte_um)
        cpts[film] = c
        if mv:
            plan[film] = {"move_nodes": mv}
    s_regle = time.perf_counter() - t1

    rap = R.run_cell08(a.csv, plan, dest=a.dest, verbose=False,
                       sha_monde_attendu=sha_in)
    out = {"lane": "REF-EVAL",
           "objet": "famille move_nodes PRETE POUR LE PACK : lissage temporel "
                    "+-1 hors mitose, porte 7 um, arrondi",
           "date_u": R.date_u(),
           "regime": "GT-FREE : la regle ne lit que positions, trames et aretes",
           "forme": "REGLE executable dans cell08 (`famille_lissage.detecteur`), "
                    "PAS un plan : un plan de 1,8 million de deplacements "
                    "pese des dizaines de Mo et se perime des que le monde "
                    "d entree change d un bit",
           "orthogonalite": "aucune arete touchee, aucun noeud ajoute ni retire "
                            "-- orthogonale a l etage v17 qui n ajoute que des "
                            "aretes : les deux gestes s additionnent par "
                            "construction",
           "entree": {"csv": str(a.csv), "sha256": sha_in,
                      "n_films": len(layout["films"]),
                      "n_noeuds": layout["n_node"],
                      "n_aretes": layout["n_edge"]},
           "sortie": {"csv": str(a.dest), "sha256": rap["sha256_out"],
                      "n_lignes": rap["n_rows_out"],
                      "mode_flottant": rap["mode_flottant_en_sortie"]},
           "gestes": {k: rap[k] for k in ("n_move_node", "n_drop_node",
                                          "n_add_node", "n_drop_edge",
                                          "n_add_edge")},
           "porte_um": a.porte_um,
           "totaux": {k: sum(c[k] for c in cpts.values()) for k in
                      ("n_noeuds", "n_lisses", "n_sautes_mitose",
                       "n_hors_porte", "n_deplaces")},
           "deplacement_median_um_median_par_film": float(np.median(
               [c["deplacement_median_um"] for c in cpts.values()])),
           "par_film": cpts,
           "temps": {"s_scan": round(s_scan, 2), "s_regle": round(s_regle, 2),
                     "s_etage": rap["s_rewrite"],
                     "s_total": round(time.perf_counter() - t0, 2)}}
    n = max(1, len(layout["films"]))
    out["temps"]["s_par_film"] = round(out["temps"]["s_total"] / n, 3)
    out["temps"]["projection_200_films_s"] = round(
        out["temps"]["s_total"] / n * 200, 1)

    if a.parite:
        from nuit_pc_e5_controle import lisser_hors_division as importee
        # ECHANTILLON A PAS CONSTANT, jamais << les N premiers >>. MITOSE a
        # trouve le 05/09 qu un essai de parite sur les cinq premiers films par
        # ordre alphabetique -- les plus petits -- repondait VRAI a tort : la
        # branche fautive n y etait jamais exercee. Un echantillon clairseme ne
        # peut pas exercer le chemin dense.
        films_tries = sorted(view)
        pas = max(1, len(films_tries) // 6)
        echantillon = films_tries[::pas][:6]
        ecarts = 0
        for film in echantillon:
            v = view[film]
            m1, _ = moves_du_film(v["node_id"], v["t"], v["zyx"], v["edges"],
                                  a.porte_um)
            m2, _ = moves_du_film(v["node_id"], v["t"], v["zyx"], v["edges"],
                                  a.porte_um, lisser=importee)
            ecarts += int(m1 != m2)
        out["parite_avec_la_lane_de_la_nuit"] = {
            "films_compares": echantillon, "n_films_compares": len(echantillon),
            "n_films_differents": ecarts, "AU_BIT": ecarts == 0,
            "echantillonnage": "a PAS CONSTANT sur les films tries, jamais les "
                               "N premiers : les premiers par ordre "
                               "alphabetique sont souvent les plus petits et "
                               "n exercent pas le chemin dense"}

    p = pathlib.Path(a.sortie)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float),
                 encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "par_film"},
                     ensure_ascii=False, indent=1, default=float))
    print("[recu] " + str(p))


if __name__ == "__main__":
    main()
