# -*- coding: utf-8 -*-
"""FAMILLE `drop_edges` PRETE POUR LE PACK -- la purge des fourches a fille morte.

LA REGLE, ECRITE SANS AMBIGUITE
-------------------------------
Une FOURCHE est un noeud `u` de degre SORTANT >= 2. Pour chacune de ses filles
`d`, on regarde sa PISTE AVAL :

    PISTE AVAL NULLE   `d` n a AUCUNE arete sortante -- la piste s arrete sur
                       elle, a l instant meme ou la division est censee avoir eu
                       lieu. Une vraie fille vit ; une fausse s eteint tout de
                       suite.

    BORD DE FILM       `d` est a la DERNIERE trame du film (`t(d) == max(t)`).
                       Une fille de la derniere trame n a AUCUNE chance d avoir
                       un successeur : son silence n est pas un defaut, c est la
                       fin de l enregistrement. Ces filles sont EXCLUES.

On coupe l arete `u -> d` quand `d` a une piste aval nulle HORS bord de film.

TROIS GARDES, et chacune ferme une facon de se tromper :
  1. on ne coupe JAMAIS si les DEUX filles sont mortes -- on ne saurait pas
     laquelle est la vraie, et couper les deux effacerait la fourche entiere ;
  2. on ne coupe JAMAIS la derniere arete sortante de `u` : apres la coupe, `u`
     garde au moins une fille. Aucune piste n est supprimee, la fourche
     redevient une piste simple ;
  3. on ne touche a aucun noeud, aucune position, aucune arete AJOUTEE : c est
     `drop_edges` et rien d autre.

Elle est GT-FREE : elle ne lit que les aretes et les trames.
ORTHOGONALE au lissage, qui ne bouge que des positions -- mesure a l appui,
l addition des deux vaut exactement la somme des deux (+0,001833 = +0,001017 +
+0,000816 sur les 139 films tenus, ecart nul a 1e-6).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

import numpy as np

ICI = pathlib.Path(__file__).resolve().parent
if str(ICI) not in sys.path:
    sys.path.insert(0, str(ICI))

import cell08_referee as R      # noqa: E402


def coupes_du_film(node_id, t, edges):
    """Les `drop_edges` de la purge, et ses comptes."""
    sortants: dict[int, list[int]] = {}
    for u, v in edges:
        sortants.setdefault(int(u), []).append(int(v))
    t_par_id = {int(x): int(t[k]) for k, x in enumerate(node_id)}
    t_max = int(t.max()) if len(t) else 0
    de = []
    n_fourches = n_deux_mortes = n_bord = 0
    for u, filles in sortants.items():
        if len(filles) < 2:
            continue
        n_fourches += 1
        mortes, bord = [], 0
        for d in filles:
            if sortants.get(d):
                continue
            if t_par_id.get(d, -1) >= t_max:
                bord += 1
                continue
            mortes.append(d)
        n_bord += bord
        if not mortes:
            continue
        if len(mortes) >= len(filles):
            # les DEUX filles sont mortes : on ne sait pas laquelle est la
            # vraie, et couper les deux effacerait la fourche entiere.
            n_deux_mortes += 1
            continue
        for d in mortes:
            de.append([int(u), int(d)])
    return de, {"n_noeuds": int(len(node_id)), "n_fourches": n_fourches,
                "n_coupes": len(de), "n_fourches_deux_filles_mortes":
                n_deux_mortes, "n_filles_au_bord_epargnees": n_bord,
                "t_max": t_max}


def detecteur(view, params=None):
    """L INTERFACE DU NOYAU : `view` -> plan. Aucun parametre regle."""
    plan = {}
    for film, v in view.items():
        de, _ = coupes_du_film(v["node_id"], v["t"], v["edges"])
        if de:
            plan[film] = {"drop_edges": de}
    return plan


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--dest", required=True)
    ap.add_argument("--plan-de-reference", default=None,
                    help="le plan de MITOSE : la regle doit le retrouver AU BIT")
    ap.add_argument("--sortie", required=True)
    a = ap.parse_args()

    t0 = time.perf_counter()
    sha_in = R.sha256_fichier(a.csv)
    term, view, layout = R.scan(a.csv)
    s_scan = time.perf_counter() - t0

    t1 = time.perf_counter()
    plan, cpts = {}, {}
    for film, v in view.items():
        de, c = coupes_du_film(v["node_id"], v["t"], v["edges"])
        cpts[film] = c
        if de:
            plan[film] = {"drop_edges": de}
    s_regle = time.perf_counter() - t1

    rap = R.run_cell08(a.csv, plan, dest=a.dest, verbose=False,
                       sha_monde_attendu=sha_in)
    tot = {k: sum(c[k] for c in cpts.values()) for k in
           ("n_noeuds", "n_fourches", "n_coupes",
            "n_fourches_deux_filles_mortes", "n_filles_au_bord_epargnees")}
    out = {"lane": "REF-EVAL",
           "objet": "famille drop_edges PRETE POUR LE PACK : purge des fourches "
                    "dont une fille a une piste aval NULLE hors bord de film",
           "date_u": R.date_u(),
           "regime": "GT-FREE : la regle ne lit que les aretes et les trames",
           "definition": {
               "fourche": "noeud de degre sortant >= 2",
               "piste_aval_nulle": "la fille n a AUCUNE arete sortante",
               "bord_de_film": "la fille est a la DERNIERE trame du film "
                               "(t == max(t)) : son silence est la fin de "
                               "l enregistrement, pas un defaut -- EXCLUE",
               "gardes": ["jamais si les DEUX filles sont mortes",
                          "jamais la derniere arete sortante de u",
                          "aucun noeud, aucune position, aucune arete ajoutee"]},
           "entree": {"csv": str(a.csv), "sha256": sha_in,
                      "n_films": len(layout["films"]),
                      "n_noeuds": layout["n_node"], "n_aretes": layout["n_edge"]},
           "sortie": {"csv": str(a.dest), "sha256": rap["sha256_out"],
                      "n_lignes": rap["n_rows_out"]},
           "gestes": {k: rap[k] for k in ("n_drop_edge", "n_drop_edge_orphelin",
                                          "n_drop_node", "n_add_edge",
                                          "n_move_node")},
           "totaux": tot, "par_film": {f: c for f, c in cpts.items()
                                       if c["n_coupes"]},
           "temps": {"s_scan": round(s_scan, 2), "s_regle": round(s_regle, 2),
                     "s_etage": rap["s_rewrite"],
                     "s_total": round(time.perf_counter() - t0, 2)}}
    n = max(1, len(layout["films"]))
    out["temps"]["s_par_film"] = round(out["temps"]["s_total"] / n, 4)
    out["temps"]["projection_200_films_s"] = round(
        out["temps"]["s_total"] / n * 200, 1)

    if a.plan_de_reference:
        ref = json.loads(pathlib.Path(a.plan_de_reference).read_text("utf-8"))
        rp = ref.get("plans", ref)
        mien = {f: sorted(map(tuple, v["drop_edges"])) for f, v in plan.items()}
        leur = {f: sorted(map(tuple, v.get("drop_edges", [])))
                for f, v in rp.items() if v.get("drop_edges")}
        out["parite_avec_le_plan_de_MITOSE"] = {
            "fichier": a.plan_de_reference,
            "n_coupes_regle": sum(len(v) for v in mien.values()),
            "n_coupes_plan": sum(len(v) for v in leur.values()),
            "films_en_trop": sorted(set(mien) - set(leur))[:10],
            "films_manquants": sorted(set(leur) - set(mien))[:10],
            "AU_BIT": bool(mien == leur)}

    p = pathlib.Path(a.sortie)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float),
                 encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "par_film"},
                     ensure_ascii=False, indent=1, default=float))
    print("[recu] " + str(p))


if __name__ == "__main__":
    main()
