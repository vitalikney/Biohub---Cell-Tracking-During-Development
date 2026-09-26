# -*- coding: utf-8 -*-
"""ETAGE FINAL -- retrait des secondes aretes de fourche que LE LIEUR LUI-MEME
juge les moins probables.

    python etage_final.py --entree <csv> --sortie <csv> --rapport <json>

CE QU IL FAIT, EN UNE PHRASE : parmi les noeuds a deux enfants, il retire la
seconde arete des fourches dont la plus faible des deux probabilites du lieur est
la plus basse -- deux par film au plus, et seulement sous 0,20.

POURQUOI CE CRITERE ET PAS UN AUTRE (mesure sur les 60 films de developpement,
politique FIGEE avant tout jugement des 139 tenus) :

  Cinq classements ont ete essayes sur les 170 fourches du canon (D), etiquetees
  par le scorer officiel (59 vraies / 111 fausses, taux de base 34,7 pct) :

    pm_prob_min croissant  ->  la tranche du bas contient 0 pct de vraies
    asymetrie, persistance, distance  ->  30 a 80 pct de vraies dans leur pire
                                          tranche : ils trient les VRAIES en
                                          tete, exactement a l envers.

  Seule l evidence du lieur separe. La geometrie, elle, ne separe pas : c est
  une mesure, pas une opinion.

L ECONOMIE, refaite plutot que reprise. J_div est GLOBAL, tp/(tp+fp+fn) =
59/262 : retirer une fourche FAUSSE vaut +0,0000857 de score, en retirer une
VRAIE coute -0,00038. Une tranche paie tant qu elle contient moins de
0,0000857/(0,00038+0,0000857) = 18,4 pct de vraies. La tranche retenue en
contient 0 sur les 60 films d ajustement.

TROIS PRUDENCES, chacune payee par une mesure :
  1. UNE PAIRE ABSENTE DU PROBMAT N EST PAS UNE PROBABILITE NULLE. Elle etait
     hors de la porte de 15 um : le lieur ne l a jamais evaluee. Les fourches
     sans probabilite lue contiennent 1 vraie sur 5 et FONT PERDRE (-0,00004) ;
     elles sont donc EXCLUES, pas classees en tete.
  2. RANG PAR FILM, jamais seuil absolu seul : le rang transporte d un embryon a
     l autre, les seuils absolus non.
  3. 0,20 est le DEBUT DU PLATEAU et non l argmax (0,30 rendrait +0,00189 contre
     +0,00171 : 10 pct de plus, colle au bord).

SANS PROBMAT JOIGNABLE, CE SCRIPT EST L IDENTITE et le dit dans son rapport. Il
ne devine pas : un retrait decide sans l evidence du lieur serait un retrait au
hasard, et au hasard on perd (34,7 pct de vraies).

Dependances : polars et numpy seulement (pas de scipy : l appariement au plus
proche voisin se fait par cases entieres et voisinage 3x3x3).
"""
import argparse
import glob
import hashlib
import json
import os
import time

import numpy as np
import polars as pl

# ------------------------------------------------------------------ POLITIQUE
# PARAMETRE (TIR-2, ordre ZEUS 22:30Z) : les deux constantes de politique sont
# desormais lues dans l ENVIRONNEMENT, avec pour DEFAUT les valeurs exactes du
# script 3af63f8d -- une variante est donc un carnet reconstruit par env seul, et
# BIOCEL_DROP_SEUIL=0.20 / BIOCEL_DROP_K=2 doit rendre le monde de 3af63f8d AU BIT.
SEUIL_PM_PROB = float(os.environ.get("BIOCEL_DROP_SEUIL", "0.20"))  # plateau mesure sur C60
K_PAR_FILM = int(os.environ.get("BIOCEL_DROP_K", "2"))              # rang par film
TOL_VOXELS = 2.0          # tolerance du pont vers le probmat (voxels decimes)
DECIMATION = 4.0          # la grille du probmat est [::1, ::4, ::4]
PROBMAT_DEFAUT = [
    os.environ.get("BIOCEL_PROBMAT_DIR", ""),
    "/workspace/SPRINT/work/div_wide_portes_199/probmat",
    "/kaggle/working/probmat",
    "probmat",
]


def _repertoire_probmat():
    for d in PROBMAT_DEFAUT:
        if d and os.path.isdir(d) and glob.glob(os.path.join(d, "*.npz")):
            return d
    return None


def _pont(noeuds, pm):
    """Associe chaque noeud du monde a un indice de `pm_coords`, par case
    entiere puis voisinage 3x3x3. Rend un dict node_id -> indice, sans scipy."""
    cases = {}
    for k, (t, z, y, x) in enumerate(pm.tolist()):
        cases.setdefault((int(t), int(z), int(y), int(x)), []).append(k)
    sortie = {}
    for nid, t, z, y, x in noeuds:
        zy, xx_ = y / DECIMATION, x / DECIMATION
        best, bd = None, TOL_VOXELS + 1.0
        cz, cy, cx = int(round(z)), int(round(zy)), int(round(xx_))
        for dz in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    for k in cases.get((int(t), cz + dz, cy + dy, cx + dx), ()):
                        pz, py, px = pm[k, 1], pm[k, 2], pm[k, 3]
                        dd = ((pz - z) ** 2 + (py - zy) ** 2
                              + (px - xx_) ** 2) ** 0.5
                        if dd < bd:
                            best, bd = k, dd
        if best is not None and bd <= TOL_VOXELS:
            sortie[nid] = best
    return sortie


def main():
    t0 = time.time()
    ap = argparse.ArgumentParser()
    ap.add_argument("--entree", required=True)
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--rapport", required=True)
    a = ap.parse_args()

    d = pl.read_csv(a.entree, schema_overrides={
        "node_id": pl.Int64, "t": pl.Int64, "z": pl.Int64, "y": pl.Int64,
        "x": pl.Int64, "source_id": pl.Int64, "target_id": pl.Int64})
    noeuds = d.filter(pl.col("row_type") == "node")
    aretes = d.filter(pl.col("row_type") == "edge")

    rep = _repertoire_probmat()
    retirees, motifs = [], []
    if rep is None:
        motifs.append("PROBMAT INTROUVABLE : identite. Un retrait decide sans "
                      "l evidence du lieur serait un retrait au hasard, et au "
                      "hasard la tranche contient 34,7 pct de vraies.")
    else:
        # fourches = sources de degre sortant EXACTEMENT 2
        deg = aretes.group_by(["dataset", "source_id"]).len()
        fourches = deg.filter(pl.col("len") == 2)
        cible = set(zip(fourches["dataset"].to_list(),
                        fourches["source_id"].to_list()))
        lignes = []
        for film in sorted(set(fourches["dataset"].to_list())):
            chemin = os.path.join(rep, film + ".npz")
            if not os.path.exists(chemin):
                motifs.append(f"probmat absent pour {film}")
                continue
            z = np.load(chemin)
            pm = z["pm_coords"].astype(np.int32)
            paires = {}
            for s, t_, p_ in zip(z["pm_src"].tolist(), z["pm_tgt"].tolist(),
                                 z["pm_prob"].tolist()):
                paires[(int(s), int(t_))] = float(p_)
            nf = noeuds.filter(pl.col("dataset") == film)
            vers = _pont(list(zip(nf["node_id"].to_list(), nf["t"].to_list(),
                                  nf["z"].to_list(), nf["y"].to_list(),
                                  nf["x"].to_list())), pm)
            af = aretes.filter(pl.col("dataset") == film)
            par_src = {}
            for s, t_ in zip(af["source_id"].to_list(), af["target_id"].to_list()):
                par_src.setdefault(int(s), []).append(int(t_))
            for s, enfants in par_src.items():
                if (film, s) not in cible or len(enfants) != 2:
                    continue
                a1, a2 = enfants
                i_s = vers.get(s)
                p1 = paires.get((i_s, vers.get(a1)), -1.0) if i_s is not None else -1.0
                p2 = paires.get((i_s, vers.get(a2)), -1.0) if i_s is not None else -1.0
                if p1 < 0 or p2 < 0:
                    continue           # probabilite non LUE : on s abstient
                faible = a1 if p1 <= p2 else a2
                lignes.append((film, s, faible, min(p1, p2)))
        # rang PAR FILM, puis seuil
        par_film = {}
        for film, s, faible, pmin in sorted(lignes, key=lambda r: r[3]):
            if pmin > SEUIL_PM_PROB:
                continue
            n = par_film.get(film, 0)
            if n >= K_PAR_FILM:
                continue
            par_film[film] = n + 1
            retirees.append([film, str(s), str(faible)])

    aret = {(f, s, t_) for f, s, t_ in retirees}
    corps, n_in = [], aretes.height
    with open(a.entree, "r", encoding="utf-8", newline="") as fh:
        tete = fh.readline().rstrip("\r\n")
        cols = tete.split(",")
        i_ds, i_rt = cols.index("dataset"), cols.index("row_type")
        i_s, i_t = cols.index("source_id"), cols.index("target_id")
        for ligne in fh:
            p = ligne.rstrip("\r\n").split(",")
            if p[i_rt] == "edge" and (p[i_ds], p[i_s], p[i_t]) in aret:
                continue
            corps.append(p)
    with open(a.sortie, "w", encoding="utf-8", newline="") as fh:
        fh.write(tete + "\n")
        for i, p in enumerate(corps):
            p[0] = str(i)
            fh.write(",".join(p) + "\n")

    rap = {
        "aretes_retirees": retirees,
        "aretes_ajoutees": [],
        "politique": {"classement": "pm_prob_min croissant, rang par film",
                      "K_par_film": K_PAR_FILM, "seuil": SEUIL_PM_PROB,
                      "exige_probabilite_LUE": True},
        "n_retirees": len(retirees), "n_aretes_entree": n_in,
        "variation_pct": round(100.0 * len(retirees) / max(n_in, 1), 5),
        "probmat": rep, "motifs": motifs,
        "secondes": round(time.time() - t0, 1),
    }
    with open(a.rapport, "w", encoding="utf-8") as fh:
        json.dump(rap, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: rap[k] for k in (
        "n_retirees", "n_aretes_entree", "variation_pct", "probmat", "motifs",
        "secondes")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
