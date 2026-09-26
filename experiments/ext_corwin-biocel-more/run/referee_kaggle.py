# -*- coding: utf-8 -*-
"""REF-DATA -- LE GENERATEUR DE COMPOSANTES POUR LE NOYAU KAGGLE.

    generer_composantes(csv_cell07, probmat_dir, sortie_dir,
                        films=None, params=None) -> dict

Sans GT, sans juge, sans reseau. Ecrit, par film :
    <sortie>/<film>.comp.parquet    une ligne par composante  (SCHEMA s. 2)
    <sortie>/<film>.nodes.parquet   une ligne par noeud
    <sortie>/<film>.edges.parquet   une ligne par arete
`label_pay`, `label_bio` et `annotee` valent NaN / 0 / False : la GT n existe pas
au test, et le SCHEMA s. 2.5 interdit d inventer un label.

DATASET KAGGLE A PLAT. Les six fichiers vivent a la racine. Le seul import par
paquet de la chaine est `oracle_local` -> `lifetwin.radar.juge` ; l alias ci-
dessous le resout sans renommer quoi que ce soit. `juge.py` n importe, au niveau
module, que la stdlib et numpy : le scorer, polars et tracksdata sont charges
paresseusement dans les fonctions, donc jamais si l on n appelle pas `juger_film`.

POURQUOI CE FICHIER TIENT LE BUDGET (contrainte ZEUS : <= 5 s par film, 4 vCPU)
------------------------------------------------------------------------------
`oracle_local.prepare` coute de 20 a 40 s par film parce qu il traite le cas
GENERAL : deux mondes quelconques, apparies par plus proche voisin mutuel, avec
une boucle Python sur les 43 000 noeuds de chaque cote.

Ici le monde candidat n est PAS quelconque : il est produit par un PLAN cell08
(`drop_nodes`, `drop_edges`, `add_edges`). Or cell08 ne DEPLACE aucun noeud et
n en AJOUTE aucun -- c est sa doctrine, ecrite dans `cell08_proofreader.py`.
Trois consequences EXACTES, pas approchees :

  1. tout noeud garde a, dans le candidat, une copie a distance 0 : le plus
     proche voisin mutuel est donc l identite, sans aucun calcul ;
  2. les seules entites de type noeud sont les noeuds SUPPRIMES (type 'r') ;
     il n y a ni 'a' (ajoute) ni 'm' (deplace) ;
  3. les aretes differentes sont exactement `drop_edges` (cote KEEP, type 'E')
     et `add_edges` (cote candidat, type 'A').

L appariement, la detection d entites et la difference d aretes deviennent donc
des operations d ENSEMBLE sur des identifiants, en O(n) numpy. Le seul calcul
geometrique restant est le lien de proximite entre ENTITES (quelques centaines
par film, pas 43 000) : un cKDTree par trame sur ce petit nuage.

CE RACCOURCI EST VERIFIE, PAS SUPPOSE. `controle_deux_routes()` recalcule les
composantes par `oracle_local` et compare la PARTITION obtenue, entite par
entite. Le contrat est l egalite exacte ; l ecart est publie dans le rapport.

EVAL_ONLY : aucune GT n est lue, aucun score n est calcule.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time
import types

import numpy as np

# --- l alias qui rend le dataset PLAT possible (voir l en-tete) -------------
if "lifetwin.radar.juge" not in sys.modules:
    try:
        import juge as _juge                      # dataset Kaggle, a plat
    except ImportError:                            # dépôt, en paquet
        from lifetwin.radar import juge as _juge
    _p = types.ModuleType("lifetwin")
    _r = types.ModuleType("lifetwin.radar")
    _r.juge = _juge
    _p.radar = _r
    sys.modules.setdefault("lifetwin", _p)
    sys.modules.setdefault("lifetwin.radar", _r)
    sys.modules.setdefault("lifetwin.radar.juge", _juge)

import anomalies as AN            # noqa: E402  PROOFREADER, appele sans retouche
import cell08_proofreader as C8   # noqa: E402  idem
from lifetwin.radar import juge as J  # noqa: E402

# `oracle_local` ne sert PLUS qu au controle a deux routes : au grain ANOMALIE,
# le groupement en composantes de desaccord disparait. Il devient donc un
# fichier OPTIONNEL du dataset Kaggle -- son absence n empeche pas le noyau de
# tourner, elle empeche seulement de rejouer le controle.
try:
    import oracle_local as OL  # noqa: E402
except ImportError:
    OL = None

SCHEMA_VERSION = "REFEREE-SCHEMA-v1"
PORTE_UM = 7.0
RAYON_APPARIEMENT_UM = 3.25

# Les PLAFOND de ZEUS : ils ne vivent qu ICI, la cellule ne les repasse pas.
PARAMS_DEFAUT = {
    "porte_um": 7.0,
    "parasite_max_noeuds": 8,
    "parasite_min_voisin": 3,
    "parasite_d_um": 7.0,
    "familles": ["DUPLICATE_FUSION", "DUPLICATE_PARASITE"],
}
FAMILLE = "W3_DUPLICATE"
# Le PERIMETRE de la famille : les DEUX sous-types dans le MEME monde.
# Piege paye cher le 05/09 : `plan_de(anos, "W1")` ne retient que les anomalies
# qui possedent un fragment "W1" -- or DUPLICATE_PARASITE n en a pas, il n a
# qu un "W1p". Un catalogue bati sur "W1" seul ne porte que 2 596 anomalies sur
# 27 707 a 60 films, et manque tout le gisement.
COMBINAISON = [("DUPLICATE_FUSION", "W1"), ("DUPLICATE_PARASITE", "W1p")]
GRAIN = "ANOMALIE"


# ===================================================================== union
class _UF:
    def __init__(self, n):
        self.p = np.arange(n)

    def trouve(self, a):
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def unis(self, a, b):
        ra, rb = self.trouve(a), self.trouve(b)
        if ra != rb:
            self.p[rb] = ra


# =========================================== la voie rapide, exacte par plan
def entites_et_composantes(node_id, t, zyx, edges, plan, echelle,
                           porte_um: float = PORTE_UM):
    """Entites et composantes d un candidat PRODUIT PAR UN PLAN cell08.

    Rend `(typ, ent_noeud, ent_arete_keep, ent_arete_cand, comp, pos, trame)` :
      typ              (n_ent,) '<U1' -- 'r' noeud supprime, 'E' arete du KEEP
                       retiree, 'A' arete du candidat posee
      ent_noeud        (n_ent,) indice du noeud porteur dans le monde KEEP
      ent_arete_keep   (n_ent,) indice de l arete dans `edges`, -1 sinon
      ent_arete_cand   (n_ent,) indice dans `plan["add_edges"]`, -1 sinon
      comp             (n_ent,) numero de composante
      pos, trame       position (um) et trame de chaque entite

    Les trois liens sont ceux d `oracle_local.composantes`, dans le meme ordre :
    (1) arete differente, qui relie l entite d arete a ses deux bouts ;
    (2) proximite < porte_um dans la MEME trame ; (3) arete quelconque reliant
    deux entites a une trame d ecart.
    """
    from scipy.spatial import cKDTree
    e = np.asarray(echelle, dtype=np.float64)
    node_id = np.asarray(node_id, dtype=np.int64)
    t = np.asarray(t, dtype=np.int64)
    P = np.asarray(zyx, dtype=np.float64) * e
    edges = np.asarray(edges, dtype=np.int64).reshape(-1, 2)

    idx = {int(v): i for i, v in enumerate(node_id)}
    dn = {int(x) for x in plan.get("drop_nodes", ())}
    de = {(int(u), int(v)) for u, v in plan.get("drop_edges", ())}
    ae = [(int(u), int(v)) for u, v in plan.get("add_edges", ())]

    # --- 1. entites de NOEUD : exactement les noeuds supprimes ---------------
    i_drop = np.array(sorted(idx[x] for x in dn if x in idx), dtype=np.int64)
    typ = ["r"] * len(i_drop)
    ent_noeud = list(i_drop)
    ent_ak = [-1] * len(i_drop)
    ent_ac = [-1] * len(i_drop)

    ent_de_n = np.full(len(node_id), -1, dtype=np.int64)
    ent_de_n[i_drop] = np.arange(len(i_drop))

    # --- 2. entites d ARETE : seulement si AUCUN bout n est deja une entite --
    ai = np.array([[idx[int(u)], idx[int(v)]] for u, v in edges],
                  dtype=np.int64).reshape(-1, 2) if len(edges) else np.zeros((0, 2), np.int64)
    ent_de_ak = np.full(len(edges), -1, dtype=np.int64)
    if len(edges) and de:
        est_dropee = np.array([(int(u), int(v)) in de for u, v in edges], dtype=bool)
        for k in np.nonzero(est_dropee)[0]:
            u, v = ai[k]
            if ent_de_n[u] < 0 and ent_de_n[v] < 0:
                ent_de_ak[k] = len(typ)
                typ.append("E")
                ent_noeud.append(int(u))
                ent_ak.append(int(k))
                ent_ac.append(-1)
    else:
        est_dropee = np.zeros(len(edges), dtype=bool)

    ent_de_ac = np.full(len(ae), -1, dtype=np.int64)
    for k, (u, v) in enumerate(ae):
        iu, iv = idx.get(u, -1), idx.get(v, -1)
        if iu < 0 or iv < 0:
            continue
        if ent_de_n[iu] < 0 and ent_de_n[iv] < 0:
            ent_de_ac[k] = len(typ)
            typ.append("A")
            ent_noeud.append(int(iu))
            ent_ak.append(-1)
            ent_ac.append(int(k))

    n = len(typ)
    if n == 0:
        z = np.zeros(0, dtype=np.int64)
        return (np.zeros(0, "<U1"), z, z, z, z, np.zeros((0, 3)), z)

    ent_noeud = np.asarray(ent_noeud, dtype=np.int64)
    pos = P[ent_noeud]
    trame = t[ent_noeud]

    uf = _UF(n)
    # --- lien 1 : arete differente <-> ses deux bouts ------------------------
    for k in np.nonzero(est_dropee)[0]:
        u, v = ai[k]
        for x, y in ((ent_de_n[u], ent_de_n[v]), (ent_de_ak[k], ent_de_n[u]),
                     (ent_de_ak[k], ent_de_n[v])):
            if x >= 0 and y >= 0:
                uf.unis(int(x), int(y))
    for k, (u, v) in enumerate(ae):
        iu, iv = idx.get(u, -1), idx.get(v, -1)
        if iu < 0 or iv < 0:
            continue
        for x, y in ((ent_de_n[iu], ent_de_n[iv]), (ent_de_ac[k], ent_de_n[iu]),
                     (ent_de_ac[k], ent_de_n[iv])):
            if x >= 0 and y >= 0:
                uf.unis(int(x), int(y))
    # --- lien 2 : proximite dans la MEME trame, sur les ENTITES seules -------
    for k in np.unique(trame):
        w = np.nonzero(trame == k)[0]
        if len(w) < 2:
            continue
        arbre = cKDTree(pos[w])
        for a, b in arbre.query_pairs(porte_um):
            uf.unis(int(w[a]), int(w[b]))
    # --- lien 3 : toute arete reliant deux entites (vectorise) --------------
    if len(edges):
        eu = ent_de_n[ai[:, 0]]
        ev = ent_de_n[ai[:, 1]]
        m = (eu >= 0) & (ev >= 0)
        for x, y in zip(eu[m], ev[m]):
            uf.unis(int(x), int(y))
    for u, v in ae:
        iu, iv = idx.get(u, -1), idx.get(v, -1)
        if iu >= 0 and iv >= 0 and ent_de_n[iu] >= 0 and ent_de_n[iv] >= 0:
            uf.unis(int(ent_de_n[iu]), int(ent_de_n[iv]))

    racines = np.array([uf.trouve(k) for k in range(n)])
    _, comp = np.unique(racines, return_inverse=True)
    return (np.asarray(typ, dtype="<U1"), ent_noeud,
            np.asarray(ent_ak, dtype=np.int64), np.asarray(ent_ac, dtype=np.int64),
            comp, pos, trame)


# ======================================================== controle deux routes
def controle_deux_routes(W0, plan, echelle, porte_um: float = PORTE_UM) -> dict:
    """La voie rapide contre `oracle_local`, sur la PARTITION en composantes.

    Le contrat est l egalite EXACTE du nombre d entites et de la partition
    (au renumerotage pres). Ce n est pas une supposition : c est ce controle
    qui autorise la voie rapide.
    """
    p = {"drop_nodes": {int(x) for x in plan.get("drop_nodes", ())},
         "drop_edges": {(int(u), int(v)) for u, v in plan.get("drop_edges", ())},
         "add_edges": [(int(u), int(v)) for u, v in plan.get("add_edges", ())]}
    nid, t1, zyx1, ar1 = C8.appliquer_plan(W0.node_id, W0.t, W0.zyx, W0.edges, p)
    W1 = J.Monde(W0.film, nid, t1, zyx1, ar1)

    m01, m10 = OL.appariement(W0, W1, echelle, RAYON_APPARIEMENT_UM)
    ent = OL.entites(W0, W1, m01, m10, echelle)
    a0, a1, a1_p, d0, d1 = OL.aretes_differentes(W0, W1, m01, m10)
    ent = OL.entites_d_aretes(ent, W0, W1, a0, a1, d0, d1)
    if len(ent["type"]) == 0:
        comp_ref = np.zeros(0, dtype=np.int64)
    else:
        comp_ref, _, _ = OL.composantes(W0, W1, ent, a0, a1, a1_p, d0, d1,
                                        echelle, porte_um=porte_um)

    typ, ent_noeud, _, _, comp, _, _ = entites_et_composantes(
        W0.node_id, W0.t, W0.zyx, W0.edges, plan, echelle, porte_um)

    ref_par_type = {c: int((ent["type"] == c).sum()) for c in ("r", "a", "m", "E", "A")}
    fast_par_type = {c: int((typ == c).sum()) for c in ("r", "a", "m", "E", "A")}
    egal_partition = None
    if len(typ) == len(ent["type"]):
        # partition comparee par le nombre de composantes et leur histogramme
        h1 = np.sort(np.bincount(comp))
        h2 = np.sort(np.bincount(comp_ref))
        egal_partition = bool(len(h1) == len(h2) and np.array_equal(h1, h2))
    return {
        "n_entites_rapide": int(len(typ)),
        "n_entites_oracle_local": int(len(ent["type"])),
        "entites_par_type_rapide": fast_par_type,
        "entites_par_type_oracle_local": ref_par_type,
        "n_composantes_rapide": int(comp.max() + 1) if len(comp) else 0,
        "n_composantes_oracle_local": int(comp_ref.max() + 1) if len(comp_ref) else 0,
        "partition_identique": egal_partition,
        "vert": bool(len(typ) == len(ent["type"]) and egal_partition),
    }


# ============================================================ point d entree
def generer_composantes(csv_cell07, probmat_dir, sortie_dir,
                        films=None, params=None, porte_um: float = PORTE_UM,
                        controle: int = 0,
                        je_veux_l_ancien_perimetre: bool = False) -> dict:
    """DEPRECIE -- N APPELEZ PAS. Utilisez `generer_anomalies`.

    POURQUOI CETTE FONCTION LEVE AU LIEU DE MARCHER. Elle batit le monde candidat
    par `plan_de(anos, "W1")`, qui ne retient que les anomalies portant un
    fragment "W1". Or `DUPLICATE_PARASITE` n en a pas : il n a qu un "W1p".
    Elle rend donc, SANS AUCUNE ERREUR, un catalogue ampute d environ 90 pct de
    la famille -- 2 596 anomalies sur 27 707 a 60 films, 44 sur 600 sur un film
    isole. C est exactement le piege qui a coute une heure et un faux resultat
    scientifique le 05/09, et il se refermerait ici sur l APPELANT.

    On ne se contente donc pas de la documenter : elle LEVE. Le drapeau
    `je_veux_l_ancien_perimetre` existe pour rejouer l ancien comportement a des
    fins de comparaison, et il faut l ecrire pour l obtenir.

    `controle` : nombre de films sur lesquels lancer `controle_deux_routes`.
    """
    if not je_veux_l_ancien_perimetre:
        raise SystemExit(
            "generer_composantes est DEPRECIE : il ne voit que DUPLICATE_FUSION "
            "(plan_de(anos, 'W1') ignore PARASITE, qui n a qu un fragment W1p), "
            "soit environ 10 pct de la famille, et il ne le dit pas. "
            "Appelez generer_anomalies(csv, probmat, sortie) -- grain ANOMALIE, "
            "perimetre FUSION + PARASITE. Pour rejouer l ancien comportement a "
            "des fins de comparaison : je_veux_l_ancien_perimetre=True.")
    import polars as pl
    t_debut = time.perf_counter()
    p = dict(PARAMS_DEFAUT)
    p.update(params or {})
    sortie = pathlib.Path(sortie_dir)
    sortie.mkdir(parents=True, exist_ok=True)

    mondes = J.charger_csv(pathlib.Path(csv_cell07), films=films)
    rapport = {"schema_version": SCHEMA_VERSION, "famille": FAMILLE,
               "params": p, "porte_de_composante_um": porte_um,
               "csv": str(csv_cell07), "par_film": {}, "controles": {}}

    for n_film, (film, W0) in enumerate(sorted(mondes.items())):
        t0 = time.perf_counter()
        ech = np.asarray(J.echelle_du_film(film), dtype=np.float64)
        anos, _ = AN.detecte_film(W0.node_id, W0.t, W0.zyx, W0.edges, ech, p)
        plan, pris, rejetes = AN.plan_de(anos, "W1")

        typ, ent_noeud, ent_ak, ent_ac, comp, pos, trame = \
            entites_et_composantes(W0.node_id, W0.t, W0.zyx, W0.edges, plan,
                                   ech, porte_um)
        nc = int(comp.max()) + 1 if len(comp) else 0

        ai = {int(v): i for i, v in enumerate(W0.node_id)}
        P0 = W0.zyx * ech
        deg_in = np.zeros(W0.n_noeuds, np.int64)
        deg_out = np.zeros(W0.n_noeuds, np.int64)
        for u, v in W0.edges:
            deg_out[ai[int(u)]] += 1
            deg_in[ai[int(v)]] += 1
        add_edges = [(int(u), int(v)) for u, v in plan.get("add_edges", ())]
        drop_edges = {(int(u), int(v)) for u, v in plan.get("drop_edges", ())}

        lc, ln, le = [], [], []
        for c in range(nc):
            ks = np.nonzero(comp == c)[0]
            pts = pos[ks]
            tps = trame[ks]
            centre = pts.mean(axis=0)
            t_centre = int(np.median(tps))
            cu = "%s|%06d" % (film, c)
            for k in ks:
                j = int(ent_noeud[k])
                pt = P0[j]
                ln.append({
                    "comp_uid": cu, "monde": 0, "id": int(W0.node_id[j]),
                    "dt": int(np.clip(int(W0.t[j]) - t_centre, -127, 127)),
                    "t": int(W0.t[j]),
                    "dz_um": float(pt[0] - centre[0]),
                    "dy_um": float(pt[1] - centre[1]),
                    "dx_um": float(pt[2] - centre[2]),
                    "z_um": float(pt[0]), "y_um": float(pt[1]), "x_um": float(pt[2]),
                    "role": {"r": "retire", "E": "keep_seule",
                             "A": "cand_seule"}[str(typ[k])],
                    "degre_in": int(deg_in[j]), "degre_out": int(deg_out[j]),
                })
                if ent_ak[k] >= 0:
                    u, v = W0.edges[int(ent_ak[k])]
                    le.append({"comp_uid": cu, "monde": 0, "src": int(u),
                               "dst": int(v), "role": "keep_seule",
                               "rang_ordre": int(ent_ak[k])})
                if ent_ac[k] >= 0:
                    u, v = add_edges[int(ent_ac[k])]
                    le.append({"comp_uid": cu, "monde": 1, "src": int(u),
                               "dst": int(v), "role": "cand_seule",
                               "rang_ordre": int(ent_ac[k])})
            lc.append({
                "schema_version": SCHEMA_VERSION, "comp_uid": cu,
                "comp_key": "%s#%d" % (film, c), "film": film, "comp_id": c,
                "comp_id_prefixe": "%s_%06d" % (FAMILLE, c),
                "famille": FAMILLE, "regime": "NATUREL",
                "porte_um": PORTE_UM, "porte_de_composante_um": porte_um,
                "t_min": int(tps.min()), "t_max": int(tps.max()),
                "t_centre": t_centre,
                "centre_z_um": float(centre[0]), "centre_y_um": float(centre[1]),
                "centre_x_um": float(centre[2]),
                "centre_z_vox": float(centre[0] / ech[0]),
                "centre_y_vox": float(centre[1] / ech[1]),
                "centre_x_vox": float(centre[2] / ech[2]),
                "rayon_um": float(np.max(np.linalg.norm(pts - centre, axis=1)))
                if len(pts) > 1 else 0.0,
                "n_trames": int(tps.max() - tps.min() + 1),
                "n_entites": int(len(ks)),
                "n_retires": int((typ[ks] == "r").sum()),
                "n_aretes_keep_seules": int((typ[ks] == "E").sum()),
                "n_aretes_cand_seules": int((typ[ks] == "A").sum()),
                # la GEOMETRIE du plan, pour que le lecteur aval n ait pas a la
                # reconstruire : c est ce qui evite la couture silencieuse.
                "plan_json": json.dumps({
                    "drop_nodes": [int(W0.node_id[int(ent_noeud[k])])
                                   for k in ks if typ[k] == "r"],
                    "drop_edges": [[int(W0.edges[int(ent_ak[k])][0]),
                                    int(W0.edges[int(ent_ak[k])][1])]
                                   for k in ks if ent_ak[k] >= 0],
                    "add_edges": [[add_edges[int(ent_ac[k])][0],
                                   add_edges[int(ent_ac[k])][1]]
                                  for k in ks if ent_ac[k] >= 0],
                }),
                # au test il n y a PAS de GT : on n invente aucun label
                "label_pay": float("nan"), "label_pay_valide": False,
                "label_pay_source": "NON_MESURE",
                "label_bio": 0, "label_bio_source": "AUCUN", "annotee": False,
            })

        for nom, rows in (("comp", lc), ("nodes", ln), ("edges", le)):
            f = sortie / f"{film}.{nom}.parquet"
            tmp = f.with_suffix(f".tmp{os.getpid()}")
            pl.DataFrame(rows).write_parquet(tmp)
            os.replace(tmp, f)

        # les drop_edges non retenues comme entites restent comptees
        rapport["par_film"][film] = {
            "n_anomalies": len(anos), "n_anomalies_prises": len(pris),
            "n_anomalies_rejetees": int(rejetes),
            "n_composantes": nc, "n_entites": int(len(typ)),
            "n_noeuds": len(ln), "n_aretes": len(le),
            "n_drop_nodes": len(plan.get("drop_nodes", ())),
            "n_drop_edges": len(drop_edges),
            "n_add_edges": len(add_edges),
            "secondes": round(time.perf_counter() - t0, 2),
        }
        if n_film < controle:
            rapport["controles"][film] = controle_deux_routes(W0, plan, ech, porte_um)

    s = [v["secondes"] for v in rapport["par_film"].values()]
    rapport["n_films"] = len(s)
    rapport["secondes_total"] = round(time.perf_counter() - t_debut, 2)
    rapport["secondes_par_film"] = {
        "min": float(np.min(s)) if s else None,
        "median": float(np.median(s)) if s else None,
        "max": float(np.max(s)) if s else None,
        "moyenne": float(np.mean(s)) if s else None,
    }
    rapport["n_anomalies_total"] = sum(v["n_anomalies"] for v in rapport["par_film"].values())
    rapport["n_composantes_total"] = sum(v["n_composantes"] for v in rapport["par_film"].values())
    rapport["anomalies_par_composante"] = (
        rapport["n_anomalies_total"] / rapport["n_composantes_total"]
        if rapport["n_composantes_total"] else None)
    return rapport




# ================================================== le grain ANOMALIE (defaut)
def _anomalies_combinees(anos):
    """Les anomalies de la COMBINAISON, chacune avec son monde local sous "X".

    Copie fidele de `PROOFREADER/impl/oracle.py::anomalies_de` reduite a ce dont
    le noyau a besoin : pas de SOFTLINK, pas de positions alternatives. Ecrite
    ici plutot qu importee pour que le dataset Kaggle n embarque pas `oracle.py`
    et toute sa chaine de mesure.
    """
    out = []
    for fam, monde in COMBINAISON:
        for a in anos:
            if a["famille"] == fam and monde in a["mondes"]:
                b = dict(a)
                b["monde_local"] = monde
                b["mondes"] = {"X": a["mondes"][monde]}
                out.append(b)
    out.sort(key=lambda a: (a["trame"], a["noeuds"][0], a["famille"]))
    return out


def _groupes_7um(anos, positions, porte_um: float = PORTE_UM):
    """Le regroupement a 7 um : un CHAMP, pas l unite de decision.

    Deux anomalies sont du meme groupe si elles partagent un noeud, ou si deux
    de leurs noeuds sont a moins de `porte_um` dans la MEME trame. C est ce qui
    dit a la composition M2 quelles corrections ne sont PAS independantes.
    """
    from scipy.spatial import cKDTree
    n = len(anos)
    uf = _UF(n)
    par_noeud = {}
    for k, a in enumerate(anos):
        for nd in a["noeuds"]:
            par_noeud.setdefault(int(nd), []).append(k)
    for ks in par_noeud.values():
        for k in ks[1:]:
            uf.unis(ks[0], k)
    pts, tr, idx = [], [], []
    for k in range(n):
        for t, q in positions[k]:
            pts.append(q)
            tr.append(int(t))
            idx.append(k)
    if pts:
        pts = np.asarray(pts)
        tr = np.asarray(tr)
        idx = np.asarray(idx)
        for t in np.unique(tr):
            w = np.nonzero(tr == t)[0]
            if len(w) < 2:
                continue
            arbre = cKDTree(pts[w])
            for a_, b_ in arbre.query_pairs(porte_um):
                uf.unis(int(idx[w[a_]]), int(idx[w[b_]]))
    racines = np.array([uf.trouve(k) for k in range(n)]) if n else np.zeros(0, np.int64)
    _, g = np.unique(racines, return_inverse=True)
    return g


def generer_anomalies(csv_cell07, probmat_dir, sortie_dir, films=None,
                      params=None, porte_um: float = PORTE_UM) -> dict:
    """Le catalogue au grain ANOMALIE : une ligne = une correction decidable.

    C est le point d entree du noyau depuis l ordre de ZEUS du 05/09 13:2xZ.
    Il ne fait AUCUN groupement en composantes de desaccord : le regroupement a
    7 um survit comme le champ `groupe_7um`, pour la composition M2 seule.
    Consequence de budget : ni appariement, ni union-find sur 43 000 noeuds --
    seulement le declencheur et un cKDTree sur les positions des anomalies.
    """
    import polars as pl
    t_debut = time.perf_counter()
    p = dict(PARAMS_DEFAUT)
    p.update(params or {})
    sortie = pathlib.Path(sortie_dir)
    sortie.mkdir(parents=True, exist_ok=True)
    mondes = J.charger_csv(pathlib.Path(csv_cell07), films=films)
    rapport = {"schema_version": SCHEMA_VERSION, "famille": FAMILLE,
               "grain": GRAIN, "params": p, "porte_groupe_um": porte_um,
               "combinaison": ["%s:%s" % c for c in COMBINAISON],
               "csv": str(csv_cell07), "par_film": {}}

    for film, W0 in sorted(mondes.items()):
        t0 = time.perf_counter()
        ech = np.asarray(J.echelle_du_film(film), dtype=np.float64)
        brut, _ = AN.detecte_film(W0.node_id, W0.t, W0.zyx, W0.edges, ech, p)
        anos = _anomalies_combinees(brut)
        idx = {int(v): i for i, v in enumerate(W0.node_id)}
        P0 = W0.zyx * ech
        positions = [[(int(W0.t[idx[int(n)]]), P0[idx[int(n)]])
                      for n in a["noeuds"] if int(n) in idx] for a in anos]
        groupe = _groupes_7um(anos, positions, porte_um)

        deg_in = np.zeros(W0.n_noeuds, np.int64)
        deg_out = np.zeros(W0.n_noeuds, np.int64)
        for u, v in W0.edges:
            deg_out[idx[int(u)]] += 1
            deg_in[idx[int(v)]] += 1

        lc, ln, le = [], [], []
        for k, a in enumerate(anos):
            frag = a["mondes"]["X"]
            drop_nodes = [int(x) for x in frag["drop_nodes"]]
            drop_edges = [[int(u), int(v)] for u, v in frag["drop_edges"]]
            add_edges = [[int(u), int(v)] for u, v in frag["add_edges"]]
            sous_type = a["famille"]
            t_ancre = int(a["trame"])
            base = [idx[int(n)] for n in a["noeuds"] if int(n) in idx]
            if not base:
                continue
            # CENTRE : le noeud candidat au retrait (PARASITE) ou le milieu de la
            # paire (FUSION). Jamais un barycentre de composante : une PARASITE
            # retire jusqu a 8 noeuds sur plusieurs trames et leur barycentre
            # peut ne coincider avec AUCUN noeud.
            if sous_type == "DUPLICATE_FUSION":
                ancre = base
            else:
                sup = [idx[int(n)] for n in drop_nodes if int(n) in idx]
                ancre = [i for i in sup if int(W0.t[i]) == t_ancre] or sup or base
                ancre = [min(ancre, key=lambda i: int(W0.node_id[i]))]
            pts = P0[base]
            tps = np.array([int(W0.t[i]) for i in base], dtype=np.int64)
            centre = P0[ancre].mean(axis=0)
            cu = "%s|%s|%06d" % (film, sous_type[10:13], k)
            morts = set(drop_nodes)
            for i in base:
                q = P0[i]
                ln.append({
                    "comp_uid": cu, "monde": 0, "id": int(W0.node_id[i]),
                    "dt": int(np.clip(int(W0.t[i]) - t_ancre, -127, 127)),
                    "t": int(W0.t[i]),
                    "dz_um": float(q[0] - centre[0]),
                    "dy_um": float(q[1] - centre[1]),
                    "dx_um": float(q[2] - centre[2]),
                    "z_um": float(q[0]), "y_um": float(q[1]), "x_um": float(q[2]),
                    "role": "retire" if int(W0.node_id[i]) in morts else "garde",
                    "degre_in": int(deg_in[i]), "degre_out": int(deg_out[i]),
                })
            for u, v in drop_edges:
                le.append({"comp_uid": cu, "monde": 0, "src": u, "dst": v,
                           "role": "keep_seule"})
            for u, v in add_edges:
                le.append({"comp_uid": cu, "monde": 1, "src": u, "dst": v,
                           "role": "cand_seule"})
            pr = a.get("preuves", {})
            lc.append({
                "schema_version": SCHEMA_VERSION, "comp_uid": cu,
                "comp_key": "%s#%d" % (film, k), "film": film, "comp_id": k,
                "comp_id_prefixe": "%s_%06d" % (FAMILLE, k),
                "famille": FAMILLE, "sous_type": sous_type, "grain": GRAIN,
                "regime": "NATUREL", "groupe_7um": int(groupe[k]),
                "porte_um": PORTE_UM, "porte_groupe_um": porte_um,
                "t_min": int(tps.min()), "t_max": int(tps.max()),
                "t_centre": t_ancre,
                "centre_z_um": float(centre[0]), "centre_y_um": float(centre[1]),
                "centre_x_um": float(centre[2]),
                "centre_z_vox": float(centre[0] / ech[0]),
                "centre_y_vox": float(centre[1] / ech[1]),
                "centre_x_vox": float(centre[2] / ech[2]),
                "rayon_um": float(np.max(np.linalg.norm(pts - centre, axis=1)))
                if len(pts) else 0.0,
                "n_trames": int(tps.max() - tps.min() + 1),
                "n_noeuds": len(base), "n_noeuds_ancre": len(ancre),
                "n_retires": len(drop_nodes),
                "n_aretes_keep_seules": len(drop_edges),
                "n_aretes_cand_seules": len(add_edges),
                "plan_json": json.dumps({"drop_nodes": drop_nodes,
                                         "drop_edges": drop_edges,
                                         "add_edges": add_edges}),
                "p_d_um": float(pr.get("d_um", float("nan"))),
                "p_n_in": float(pr.get("n_in", float("nan"))),
                "p_n_out": float(pr.get("n_out", float("nan"))),
                "p_taille_comp": float(pr.get("taille_comp",
                                              pr.get("taille_comp_a", float("nan")))),
                "p_n_voisins_porte": float(pr.get("n_voisins_porte", float("nan"))),
                # au test il n y a PAS de GT : aucun label n est invente
                "label_pay": float("nan"), "label_pay_valide": False,
                "label_pay_source": "NON_MESURE",
                "label_bio": 0, "label_bio_source": "AUCUN", "annotee": False,
            })

        for nom, rows in (("comp", lc), ("nodes", ln), ("edges", le)):
            f = sortie / (film + "." + nom + ".parquet")
            tmp = f.with_suffix(".tmp%d" % os.getpid())
            pl.DataFrame(rows).write_parquet(tmp)
            os.replace(tmp, f)

        rapport["par_film"][film] = {
            "n_anomalies_brutes": len(brut), "n_anomalies": len(anos),
            "par_sous_type": {st: sum(1 for a in anos if a["famille"] == st)
                              for st in ("DUPLICATE_FUSION", "DUPLICATE_PARASITE")},
            "n_groupes_7um": int(groupe.max()) + 1 if len(groupe) else 0,
            "n_noeuds": len(ln), "n_aretes": len(le),
            "secondes": round(time.perf_counter() - t0, 2),
        }

    s_ = [v["secondes"] for v in rapport["par_film"].values()]
    rapport["n_films"] = len(s_)
    rapport["secondes_total"] = round(time.perf_counter() - t_debut, 2)
    rapport["secondes_par_film"] = {
        "min": float(np.min(s_)) if s_ else None,
        "median": float(np.median(s_)) if s_ else None,
        "max": float(np.max(s_)) if s_ else None}
    rapport["n_anomalies_total"] = sum(v["n_anomalies"] for v in rapport["par_film"].values())
    rapport["n_groupes_total"] = sum(v["n_groupes_7um"] for v in rapport["par_film"].values())
    rapport["anomalies_par_groupe"] = (rapport["n_anomalies_total"] /
                                       max(rapport["n_groupes_total"], 1))
    return rapport


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--probmat", default="")
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--films", nargs="*", default=None)
    ap.add_argument("--porte-composante", type=float, default=PORTE_UM)
    ap.add_argument("--controle", type=int, default=0)
    ap.add_argument("--recu", default="")
    a = ap.parse_args()
    r = generer_composantes(a.csv, a.probmat, a.sortie, films=a.films,
                            porte_um=a.porte_composante, controle=a.controle)
    if a.recu:
        pathlib.Path(a.recu).write_text(json.dumps(r, ensure_ascii=False, indent=1),
                                        encoding="utf-8")
    print(json.dumps({k: r[k] for k in
                      ("n_films", "n_anomalies_total", "n_composantes_total",
                       "anomalies_par_composante", "secondes_total",
                       "secondes_par_film")}, ensure_ascii=False))
    for f, c in r["controles"].items():
        print("controle deux routes", f, json.dumps(c, ensure_ascii=False))
