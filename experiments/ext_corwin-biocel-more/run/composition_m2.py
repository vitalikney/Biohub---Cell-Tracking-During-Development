# -*- coding: utf-8 -*-
"""COMPOSITION M2 -- garder un ensemble COMPATIBLE de remplacements (n 113 8).

LE PROBLEME, ET POURQUOI IL EST REEL
------------------------------------
Le referee juge une composante en supposant que TOUT LE RESTE DU MONDE EST
KEEP. Si l on applique deux remplacements qui se touchent, aucun des deux n a
ete evalue dans le monde ou l autre existe : le Delta mesure ne dit plus rien.
Pire, PROOFREADER a montre le mecanisme exact -- << la foule est portante >> :
retirer un noeud libere une annotation, l appariement bipartite de la trame se
reorganise, et une VOISINE correcte y perd son partenaire. Deux corrections
voisines s abiment donc l une l autre meme quand chacune est juste.

M2 = un COUPLAGE SANS CONFLIT, glouton par marge decroissante.

    deux remplacements sont INCOMPATIBLES s ils partagent
        un noeud                (meme node_id touche des deux cotes)
        une arete               (meme couple (u,v) pose ou retire)
        un VOISINAGE de trame   (deux points a moins de 7,0 um, |dt| <= 1)

    en conflit, LA PLUS FORTE MARGE GAGNE ; la perdante retombe sur KEEP.

Les 7,0 um sont la porte du juge (`DistanceMatching(max_distance=7.0)`) : au
dela, deux gestes ne peuvent pas se disputer une annotation. |dt| <= 1 est
CONSERVATEUR (la definition de composante de CIBLAGE ne lie que la MEME trame)
et le recu publie ce que dt=0 aurait donne, pour que le prix du choix soit lu.

DETERMINISME
------------
L ordre est `(-marge, film, famille, comp_id)` : totalement ordonne, aucun
depart d egalite par le hasard, aucune dependance a l ordre des fichiers. Deux
executions rendent le meme plan, donc le meme sha256 de CSV.

KEEP PAR DEFAUT
---------------
Une composante sans decision, sous le seuil, de famille inconnue, ou dont le
plan est vide : KEEP. Jamais une famille entiere. Jamais un remplacement par
defaut d information.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import cell08_referee as R  # noqa: E402

PORTE_UM = 7.0
DT_VOISINAGE = 1
FAMILLES = set(R.FAMILLES)


# ==========================================================================
# LECTURE -- deux portages, une seule semantique (CONTRAT_DECISIONS.md 3)
# ==========================================================================
def _liste(v):
    if v is None:
        return []
    if isinstance(v, np.ndarray):
        return v.tolist()
    return list(v)


def plan_de_ligne(row: dict) -> dict:
    """Le plan geometrique d une composante, quel que soit le portage."""
    if row.get("plan_json"):
        p = json.loads(row["plan_json"])
    else:
        p = {k: _liste(row.get(k)) for k in
             ("drop_nodes", "move_nodes", "add_nodes", "drop_edges", "add_edges")}
    return {
        "drop_nodes": [int(x) for x in _liste(p.get("drop_nodes"))],
        "move_nodes": [[int(e[0]), float(e[1]), float(e[2]), float(e[3])]
                       for e in _liste(p.get("move_nodes"))],
        "add_nodes": [[int(e[0]), float(e[1]), float(e[2]), float(e[3])]
                      for e in _liste(p.get("add_nodes"))],
        "drop_edges": [[int(e[0]), int(e[1])]
                       for e in _liste(p.get("drop_edges"))],
        "add_edges": [[int(e[0]), int(e[1])]
                      for e in _liste(p.get("add_edges"))],
    }


def plan_vide(p: dict) -> bool:
    return not any(p[k] for k in ("drop_nodes", "move_nodes", "add_nodes",
                                  "drop_edges", "add_edges"))


def fusionne(plans: list[dict]) -> dict:
    """Concatene des plans de composantes DISJOINTES en un plan de film.

    Les references locales negatives sont RE-INDEXEES : `add_nodes` est
    concatene, donc `-(k+1)` de la composante c devient `-(offset_c + k + 1)`.
    Sans cela, deux composantes qui posent chacune un noeud viseraient le meme.
    """
    out = {"drop_nodes": [], "move_nodes": [], "add_nodes": [],
           "drop_edges": [], "add_edges": []}
    for p in plans:
        off = len(out["add_nodes"])
        out["drop_nodes"].extend(p["drop_nodes"])
        out["move_nodes"].extend(p["move_nodes"])
        out["add_nodes"].extend(p["add_nodes"])
        out["drop_edges"].extend(p["drop_edges"])
        for u, v in p["add_edges"]:
            out["add_edges"].append([u - off if u < 0 else u,
                                     v - off if v < 0 else v])
    return out


# ==========================================================================
# LA DECISION -- pre-enregistree, KEEP par defaut
# ==========================================================================
def barre_de(row: dict, seuil: float, seuils: dict | None) -> tuple[float, str]:
    """La barre qui s applique a CETTE ligne, et d ou elle vient.

    POURQUOI UNE BARRE PAR SOUS-TYPE (demande de REGLAGES-A, 05/09 13:1xZ) :
    la precision d EQUILIBRE n est pas une constante. REF-MODEL mesure 0,8333
    pour `DUPLICATE_FUSION` au socle r=10 -- se tromper y coute cinq fois ce que
    reussir rapporte -- contre 0,542 pour les composantes de `normimg_pur`.
    Appliquer la meme barre aux deux se paie DIRECTEMENT en score : trop basse
    sur FUSION, on perd ; trop haute sur PARASITE, on laisse le gisement.

    Ordre de resolution, sans surprise : `seuils[sous_type]`, puis
    `seuils[famille]`, puis `seuils["defaut"]`, puis le scalaire `seuil`.
    Sans le parametre, le comportement est EXACTEMENT celui d avant.
    """
    if not seuils:
        return seuil, "scalaire"
    for cle in ("sous_type", "famille"):
        v = row.get(cle)
        if v is not None and v in seuils:
            return float(seuils[v]), cle
    if "defaut" in seuils:
        return float(seuils["defaut"]), "defaut"
    return seuil, "scalaire"


def decide(row: dict, seuil: float,
           seuils: dict | None = None) -> tuple[bool, float, str]:
    """(remplace, marge, motif). Tout ce qui n est pas un REPLACE net est KEEP."""
    try:
        pk = float(row.get("P_KEEP", 0.0))
        pr = float(row.get("P_REPLACE", 0.0))
        pa = float(row.get("P_ABSTAIN", 0.0))
    except (TypeError, ValueError):
        return False, 0.0, "probabilites illisibles"
    if not all(np.isfinite(x) for x in (pk, pr, pa)):
        return False, 0.0, "probabilite non finie"
    m = row.get("marge")
    marge = float(m) if m is not None and np.isfinite(float(m)) else pr - max(pk, pa)
    if row.get("famille") not in FAMILLES:
        return False, marge, "famille inconnue : %r" % (row.get("famille"),)
    barre, _ = barre_de(row, seuil, seuils)
    if pr < barre:
        return False, marge, "sous le seuil (%.4f < %.4f)" % (pr, barre)
    if not (pr > pk and pr > pa):
        return False, marge, "P_REPLACE n est pas le maximum"
    return True, marge, ""


# ==========================================================================
# LES CONFLITS
# ==========================================================================
def empreinte(p: dict, view_film: dict, echelle) -> dict:
    """Ce qu une composante OCCUPE : noeuds, aretes, points (t, position um).

    Les points comprennent les noeuds RETIRES, DEPLACES (position d arrivee ET
    de depart : les deux disputent une annotation), AJOUTES, et les extremites
    des aretes touchees. C est volontairement large : un faux conflit coute une
    correction, un conflit manque coute un Delta qui ne veut plus rien dire.
    """
    e = np.asarray(echelle, dtype=np.float64)
    nid = view_film["node_id"]
    idx = view_film["_idx"]
    t = view_film["t"]
    zyx = view_film["zyx"]
    noeuds, aretes, pts = set(), set(), []

    def ajoute_existant(n):
        k = idx.get(int(n))
        if k is None:
            return
        noeuds.add(int(n))
        pts.append((int(t[k]), zyx[k] * e))

    for n in p["drop_nodes"]:
        ajoute_existant(n)
    for n, z, y, x in p["move_nodes"]:
        ajoute_existant(n)
        k = idx.get(int(n))
        if k is not None:
            pts.append((int(t[k]), np.array([z, y, x], dtype=np.float64) * e))
    for tt, z, y, x in p["add_nodes"]:
        pts.append((int(tt), np.array([z, y, x], dtype=np.float64) * e))
    for u, v in p["drop_edges"] + p["add_edges"]:
        aretes.add((int(u), int(v)))
        for n in (u, v):
            if n >= 0:
                ajoute_existant(n)
    return {"noeuds": noeuds, "aretes": aretes, "points": pts}


class Index:
    """Index des composantes DEJA PRISES : noeuds, aretes, et une grille de
    `porte_um` par trame. Sans grille, le test de voisinage serait quadratique
    en nombre de composantes prises et le film le plus dense couterait des
    minutes ; avec elle, il est lineaire.
    """

    def __init__(self, porte_um: float, dt: int):
        self.porte = float(porte_um)
        self.dt = int(dt)
        self.noeuds: dict[int, dict] = {}
        self.aretes: dict[tuple, dict] = {}
        self.grille: dict[tuple, list] = {}

    def _cellules(self, t, pt, dt):
        c = np.floor(pt / self.porte).astype(np.int64)
        for tt in range(t - dt, t + dt + 1):
            for a in (-1, 0, 1):
                for b in (-1, 0, 1):
                    for d in (-1, 0, 1):
                        yield (tt, int(c[0]) + a, int(c[1]) + b, int(c[2]) + d)

    def conflit(self, emp: dict, dt: int | None = None):
        dt = self.dt if dt is None else dt
        for n in emp["noeuds"]:
            if n in self.noeuds:
                return "noeud partage", self.noeuds[n]
        for e in emp["aretes"]:
            if e in self.aretes:
                return "arete partagee", self.aretes[e]
        vus = set()
        for t, pt in emp["points"]:
            for cle in self._cellules(t, pt, dt):
                for (t2, p2, meta) in self.grille.get(cle, ()):
                    k = id(meta)
                    if k in vus:
                        continue
                    if abs(t - t2) <= dt and float(np.linalg.norm(pt - p2)) <= self.porte:
                        return ("voisinage %.1f um a |dt|<=%d" % (self.porte, dt),
                                meta)
                    vus.add(k)
        return None, None

    def ajoute(self, emp: dict, meta: dict) -> None:
        for n in emp["noeuds"]:
            self.noeuds[n] = meta
        for e in emp["aretes"]:
            self.aretes[e] = meta
        for t, pt in emp["points"]:
            c = np.floor(pt / self.porte).astype(np.int64)
            self.grille.setdefault((t, int(c[0]), int(c[1]), int(c[2])),
                                   []).append((t, pt, meta))


# ==========================================================================
# M2
# ==========================================================================
def coefficient_de_comptage(compteurs: dict) -> dict:
    """Le gain de SCORE que rapporte le retrait d UN noeud, film par film.

    Le bareme officiel porte `adj = Somme_i a_i TP_i / Somme_i w_i` avec
    `a_i = 1 - 0,1 (N_i - n_i) / n_i`. Retirer un noeud de N_i fait donc monter
    le score de `0,1 TP_i / (n_i Somme_j w_j)` -- de l ordre de 6e-8 par noeud.

    C EST UNE RECOMPENSE AU RETRAIT, ET ELLE NE DOIT JAMAIS DECIDER (ordre de
    ZEUS, 05/09 13:3xZ). La GT du concours est SPARSE : un noeud non annote est
    << gratuit et payant >> ici, alors qu au test cache il peut tres bien etre
    annote. Ce coefficient sert donc au CONTROLE -- savoir combien de score une
    composition doit au comptage plutot qu au suivi -- et a rien d autre.

    `compteurs` : {film: {edge_tp, edge_fp, edge_fn, n_total}} (les lignes du
    juge). Rend {film: gain de score par noeud retire}.
    """
    somme_w = sum(float(r["edge_tp"]) + float(r["edge_fp"]) + float(r["edge_fn"])
                  for r in compteurs.values())
    if somme_w <= 0:
        return {}
    return {f: 0.1 * float(r["edge_tp"]) / (float(r["n_total"]) * somme_w)
            for f, r in compteurs.items() if float(r["n_total"]) > 0}


def compose(lignes: list[dict], view: dict, echelles: dict, seuil: float,
            porte_um: float = PORTE_UM, dt: int = DT_VOISINAGE,
            seuils: dict | None = None,
            comptage: dict | None = None) -> tuple[dict, dict]:
    """Rend (plan par film, rapport).

    `lignes` : la jointure composantes x decisions, une par composante candidate.
    `view` : la vue du CSV KEEP (`cell08_referee.scan`).
    `echelles` : {film: (ez, ey, ex)} en um/voxel.
    """
    recues = len(lignes)
    retenues, refus = [], []
    par_sous_type: dict[str, dict] = {}
    for row in lignes:
        p = plan_de_ligne(row)
        remplace, marge, motif = decide(row, seuil, seuils)
        barre, source_barre = barre_de(row, seuil, seuils)
        st = str(row.get("sous_type") or row.get("famille"))
        d = par_sous_type.setdefault(st, {"n": 0, "barre": barre,
                                          "source_de_la_barre": source_barre,
                                          "n_REPLACE": 0, "n_appliquees": 0})
        d["n"] += 1
        d["n_REPLACE"] += int(remplace)
        if not remplace:
            refus.append({"film": row.get("film"), "comp_id": row.get("comp_id"),
                          "famille": row.get("famille"), "motif": motif or "KEEP",
                          "marge": marge})
            continue
        if plan_vide(p):
            refus.append({"film": row.get("film"), "comp_id": row.get("comp_id"),
                          "famille": row.get("famille"),
                          "motif": "plan vide", "marge": marge})
            continue
        retenues.append({**row, "_plan": p, "_marge": marge})

    # --- ordre TOTAL, deterministe -------------------------------------
    retenues.sort(key=lambda r: (-r["_marge"], str(r.get("film")),
                                 str(r.get("famille")), int(r.get("comp_id", 0))))

    par_film: dict[str, list] = {}
    for r in retenues:
        par_film.setdefault(str(r["film"]), []).append(r)

    par_famille: dict[str, dict] = {}
    for r in retenues:
        f = str(r.get("famille"))
        par_famille.setdefault(f, {"candidates": 0, "appliquees": 0})
        par_famille[f]["candidates"] += 1

    plan, rap_films = {}, {}
    n_pris = n_conflit = n_conflit_dt0 = 0
    detail_conflits = []
    for film, rs in par_film.items():
        if film not in view:
            for r in rs:
                refus.append({"film": film, "comp_id": r.get("comp_id"),
                              "famille": r.get("famille"),
                              "motif": "film absent du CSV KEEP",
                              "marge": r["_marge"]})
            continue
        v = dict(view[film])
        v["_idx"] = {int(x): k for k, x in enumerate(v["node_id"])}
        ech = echelles.get(film, (1.625, 0.40625, 0.40625))
        pris = []
        idx = Index(porte_um, dt)
        for r in rs:
            emp = empreinte(r["_plan"], v, ech)
            motif, gagnante = idx.conflit(emp)
            if motif:
                n_conflit += 1
                if idx.conflit(emp, dt=0)[0]:
                    n_conflit_dt0 += 1
                detail_conflits.append(
                    {"film": film, "comp_id": r.get("comp_id"),
                     "famille": r.get("famille"), "marge": r["_marge"],
                     "gagnante": gagnante.get("comp_id"),
                     "famille_gagnante": gagnante.get("famille"),
                     "marge_gagnante": gagnante.get("marge"), "motif": motif})
                refus.append({"film": film, "comp_id": r.get("comp_id"),
                              "famille": r.get("famille"),
                              "motif": "conflit M2 : " + motif, "marge": r["_marge"]})
                continue
            pris.append(r)
            idx.ajoute(emp, {"comp_id": r.get("comp_id"),
                             "famille": r.get("famille"), "marge": r["_marge"]})
            st = str(r.get("sous_type") or r.get("famille"))
            if st in par_sous_type:
                par_sous_type[st]["n_appliquees"] += 1
            par_famille.setdefault(str(r.get("famille")),
                                   {"candidates": 0, "appliquees": 0})
            par_famille[str(r.get("famille"))]["appliquees"] += 1
        if pris:
            plan[film] = fusionne([r["_plan"] for r in pris])
            n_pris += len(pris)
        rap_films[film] = {"candidates": len(rs), "appliquees": len(pris),
                           "rejetees_par_conflit": len(rs) - len(pris)}

    rap = {
        "seuil_P_REPLACE": seuil,
        "seuils_par_sous_type": seuils,
        "seuils_appliques_a_la_composition": bool(seuils),
        "par_sous_type": par_sous_type,
        "porte_um": porte_um, "dt_voisinage": dt,
        "n_decisions_recues": recues,
        "n_REPLACE_avant_M2": len(retenues),
        "n_appliquees": n_pris,
        "n_rejetees_par_conflit": n_conflit,
        "n_rejetees_par_conflit_si_dt0": n_conflit_dt0,
        "n_KEEP": recues - len(retenues),
        "motifs_de_KEEP": _compte([x["motif"].split(" (")[0] for x in refus]),
        "par_film": rap_films,
        "par_famille": par_famille,
        "conflits": detail_conflits[:200],
        "n_films_touches": len(plan),
        "gestes": {k: sum(len(p[k]) for p in plan.values()) for k in
                   ("drop_nodes", "move_nodes", "add_nodes", "drop_edges",
                    "add_edges")},
    }
    # --- le terme de COMPTAGE, analytique, EN CONTROLE SEULEMENT ---------
    net = {f: len(p["drop_nodes"]) - len(p["add_nodes"]) for f, p in plan.items()}
    rap["comptage"] = {
        "n_noeuds_retires_net": sum(net.values()),
        "gain_de_score_estime": (sum(net[f] * comptage.get(f, 0.0) for f in net)
                                 if comptage else None),
        "coefficients_fournis": bool(comptage),
        "usage": "CONTROLE SEULEMENT. Le terme de comptage recompense le "
                 "retrait d un noeud (environ 6e-8 par noeud) alors que la GT "
                 "est SPARSE : un noeud non annote est gratuit ici et peut "
                 "etre annote au test cache. Il ne decide de rien, il est "
                 "publie pour qu on sache ce qu une composition doit au "
                 "comptage plutot qu au suivi.",
    }
    return plan, rap


def _compte(xs):
    out = {}
    for x in xs:
        out[x] = out.get(x, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


# ==========================================================================
# LE TEMOIN -- les MEMES decisions, PERMUTEES entre composantes
# ==========================================================================
def permute(lignes: list[dict], graine: int) -> list[dict]:
    """Les memes decisions, redistribuees au hasard sur les memes composantes.

    C est le seul temoin honnete d une composition : il garde le NOMBRE de
    remplacements, la distribution des marges et la geometrie ; il ne detruit
    que l APPARIEMENT entre la decision et la composante. Si le monde composé
    ne bat pas ce temoin, le referee n a pas designe : il a compte.
    """
    rng = np.random.default_rng(graine)
    cles = ("P_KEEP", "P_REPLACE", "P_ABSTAIN", "marge", "E_keep", "E_cand", "U")
    dec = [{k: r.get(k) for k in cles} for r in lignes]
    ordre = rng.permutation(len(dec))
    return [{**r, **dec[int(ordre[i])]} for i, r in enumerate(lignes)]


# ==========================================================================
# L ORACLE -- la BORNE, jamais une decision de production
# ==========================================================================
def decisions_oracle(lignes: list[dict], cle: str = "delta_exact") -> list[dict]:
    """Decision = le SIGNE du Delta EXACT. C est le PLAFOND de la composition.

    Il lit la GT : il ne peut donc jamais etre soumis. Il repond a une seule
    question, mais elle est decisive : si le plafond lui-meme est sous +0,003,
    aucun modele ne franchira G2 sur cette matiere, et le probleme n est pas le
    referee -- c est le gisement.
    """
    out = []
    for r in lignes:
        d = r.get(cle)
        bon = d is not None and np.isfinite(float(d)) and float(d) > 0
        out.append({**r, "P_REPLACE": 1.0 if bon else 0.0,
                    "P_KEEP": 0.0 if bon else 1.0, "P_ABSTAIN": 0.0,
                    "marge": abs(float(d)) if d is not None
                    and np.isfinite(float(d)) else 0.0})
    return out


# ==========================================================================
# LA JOINTURE -- lire `decisions_<film>.parquet` et `composantes_*.parquet`
# ==========================================================================
def _lit_parquet(path) -> list[dict]:
    """Un parquet en liste de dictionnaires. pyarrow s il est la, polars sinon.

    Aucune des deux n est imposee : le pod porte polars, le PC porte les deux,
    et le noyau Kaggle porte polars. Un fichier illisible n est JAMAIS fatal --
    il est compte et la composante retombe sur KEEP, ce qui est la regle.
    """
    path = pathlib.Path(path)
    try:
        import pyarrow.parquet as pq
        return pq.read_table(path).to_pylist()
    except ImportError:
        pass
    import polars as pl
    return pl.read_parquet(path).to_dicts()


def _film_du_nom(nom: str, prefixe: str) -> str | None:
    """`decisions_44b6_d5e7d891.parquet` -> `44b6_d5e7d891`."""
    t = pathlib.Path(nom).stem
    return t[len(prefixe):] if t.startswith(prefixe) else None


def charge_decisions(dossier, motif: str = "decisions_*.parquet") -> tuple[list, dict]:
    """Les decisions de REF-MODEL, un fichier par film (CONTRAT_DECISIONS 2).

    Rend `(lignes, rapport)`. Chaque ligne porte au moins `film`, `comp_id`,
    `famille`, `P_KEEP`, `P_REPLACE`, `P_ABSTAIN` ; `film` est pris de la
    colonne si elle existe, sinon du NOM DU FICHIER -- jamais devine.

    UN DOSSIER VIDE, ABSENT, OU ILLISIBLE REND UNE LISTE VIDE, PAS UNE ERREUR :
    aucune decision, donc KEEP partout, donc le CSV sort AU BIT. C est
    exactement le comportement voulu quand le referee n a rien a dire.
    """
    d = pathlib.Path(dossier)
    rap = {"dossier": str(d), "existe": d.is_dir(), "n_fichiers": 0,
           "n_lignes": 0, "fichiers_illisibles": [], "films": [],
           "sans_comp_id": 0, "sans_film": 0}
    if not d.is_dir():
        return [], rap
    lignes = []
    for f in sorted(d.glob(motif)):
        rap["n_fichiers"] += 1
        film_du_nom = _film_du_nom(f.name, motif.split("*")[0])
        try:
            rows = _lit_parquet(f)
        except Exception as ex:                                # noqa: BLE001
            rap["fichiers_illisibles"].append({"fichier": f.name,
                                               "erreur": str(ex)[:200]})
            continue
        for r in rows:
            r = dict(r)
            if not r.get("film"):
                if film_du_nom is None:
                    rap["sans_film"] += 1
                    continue
                r["film"] = film_du_nom
            if r.get("comp_id") is None:
                rap["sans_comp_id"] += 1
                continue
            r["comp_id"] = int(r["comp_id"])
            lignes.append(r)
        if film_du_nom:
            rap["films"].append(film_du_nom)
    rap["n_lignes"] = len(lignes)
    rap["films"] = sorted(set(rap["films"]))
    return lignes, rap


class CatalogueIncomplet(RuntimeError):
    """Le catalogue existe mais ne porte pas de GEOMETRIE APPLICABLE.

    Le piege qu elle ferme (trouve par REGLAGES-A, 05/09 13:0xZ) : REF-DATA
    ecrit la FORME LONGUE -- `<x>.comp.parquet`, `<x>.nodes.parquet`,
    `<x>.edges.parquet`. Un glob `*.parquet` naif indexe les trois par
    (film, comp_id) et les `.nodes` ECRASENT les `.comp` : le catalogue perd sa
    geometrie, tous les plans sortent vides, cell08 rend le CSV au bit et TOUT
    A L AIR DE MARCHER. Un catalogue sans geometrie doit LEVER, pas se taire.
    """


def _monde_de(v) -> str:
    """`monde` peut etre une chaine ou un entier selon le writer.

    REF-DATA ecrit `monde` en Int64 (0 = KEEP, 1 = CANDIDAT) tandis que le
    schema le decrit en clair. On accepte les deux plutot que de lever sur une
    convention d encodage -- mais on refuse tout ce qui n est ni l un ni
    l autre, parce qu un `monde` mal lu inverserait KEEP et CANDIDAT en silence.
    """
    if isinstance(v, str):
        return v.strip().lower()
    if isinstance(v, bool):
        return "cand" if v else "keep"
    if isinstance(v, (int, np.integer)):
        if int(v) == 0:
            return "keep"
        if int(v) == 1:
            return "cand"
    raise CatalogueIncomplet(
        "colonne `monde` illisible : %r (attendu 'keep'/'cand' ou 0/1)" % (v,))


def _plan_depuis_longue(noeuds: list, aretes: list) -> dict:
    """Le plan d une composante, deduit des tables `nodes` et `edges` (SCHEMA 2.3).

    CE QUI EST DEDUCTIBLE SANS AMBIGUITE :
      * `retire`     -> `drop_nodes` (id du monde KEEP) ;
      * `keep_seule` -> `drop_edges` ;
      * `cand_seule` -> `add_edges`, A LA CONDITION que les identifiants du
        monde candidat soient ceux du monde KEEP -- c est le cas des mondes
        LOCAUX (W3-W6) fabriques par cell08, qui ne renumerotent rien.

    CE QUI NE L EST PAS, ET QUI LEVE PLUTOT QUE DE DEVINER :
      * `deplace` -- il faut apparier le noeud KEEP et le noeud CANDIDAT, et
        les deux tables ne portent pas ce lien ;
      * `ajoute`  -- la position doit revenir en INDICES VOXEL, or les tables
        ne portent que des um en float32 : l aller-retour n est pas exact, et
        une position approchee n est pas une position.
    En clair : W3/W4/W5/W6 passent, W1/W2 exigent une colonne `plan_json`.
    """
    dn, mv, an, de, ae = [], [], [], [], []
    for n in noeuds:
        role = str(n.get("role") or "").lower()
        monde = _monde_de(n.get("monde"))
        if role == "retire" and monde.startswith("keep"):
            dn.append(int(n["id"]))
        elif role == "deplace" and monde.startswith("keep"):
            mv.append(int(n["id"]))
        elif role == "ajoute":
            an.append(n)
    if mv or an:
        raise CatalogueIncomplet(
            "la composante porte %d noeud(s) DEPLACE(S) et %d AJOUTE(S) : la "
            "forme longue ne permet pas de les appliquer sans deviner "
            "(appariement KEEP<->CANDIDAT absent, positions en um float32). "
            "Une colonne `plan_json` est requise pour les familles W1 et W2."
            % (len(mv), len(an)))
    for e in aretes:
        role = str(e.get("role") or "").lower()
        if role == "keep_seule":
            de.append([int(e["src"]), int(e["dst"])])
        elif role == "cand_seule":
            ae.append([int(e["src"]), int(e["dst"])])
    return {"drop_nodes": dn, "move_nodes": [], "add_nodes": [],
            "drop_edges": de, "add_edges": ae}


def charge_composantes(source, motif: str = "*.comp.parquet",
                       exiger_geometrie: bool = True) -> tuple[dict, dict]:
    """Le catalogue de REF-DATA, indexe par `(film, comp_id)`, GEOMETRIE COMPRISE.

    `source` est un fichier `.comp.parquet` ou un dossier. La forme LONGUE est
    lue explicitement : `*.comp.parquet` porte les composantes,
    `*.nodes.parquet` et `*.edges.parquet` portent la geometrie, jointes par
    `comp_uid`. La forme COURTE (une colonne `plan_json`, ou les cinq colonnes
    de listes) reste acceptee telle quelle.

    `exiger_geometrie` (defaut) fait LEVER `CatalogueIncomplet` si aucune
    composante ne porte de geometrie applicable : sans cela, un catalogue muet
    produirait des plans vides et un CSV au bit, et l absence de correction
    passerait pour une decision.
    """
    s = pathlib.Path(source)
    if s.is_file():
        fichiers = [s]
    elif s.is_dir():
        fichiers = sorted(s.glob(motif))
        if not fichiers:
            # FORME COURTE : un parquet par famille ou par film, sans suffixe
            # `.comp`. On EXCLUT explicitement `.nodes` et `.edges` -- c est
            # precisement leur inclusion par un glob naif qui les faisait
            # ECRASER les composantes et vider tous les plans en silence.
            fichiers = [f for f in sorted(s.glob("*.parquet"))
                        if not (f.name.endswith(".nodes.parquet")
                                or f.name.endswith(".edges.parquet"))]
            motif = "*.parquet (hors .nodes/.edges)"
    else:
        fichiers = []
    rap = {"source": str(s), "motif": motif, "n_fichiers": len(fichiers),
           "n_composantes": 0, "fichiers_illisibles": [], "colonnes": [],
           "forme": None, "n_avec_geometrie": 0, "n_sans_geometrie": 0,
           "motifs_sans_geometrie": {}, "n_noeuds": 0, "n_aretes": 0}
    cat = {}
    for f in fichiers:
        try:
            rows = _lit_parquet(f)
        except Exception as ex:                                # noqa: BLE001
            rap["fichiers_illisibles"].append({"fichier": f.name,
                                               "erreur": str(ex)[:200]})
            continue
        if not rows:
            continue
        if not rap["colonnes"]:
            rap["colonnes"] = sorted(rows[0])
        courte = ("plan_json" in rows[0]) or ("drop_nodes" in rows[0])
        rap["forme"] = "courte" if courte else "longue"
        par_uid_n, par_uid_e = {}, {}
        if not courte:
            base = f.name[:-len(".comp.parquet")] if f.name.endswith(
                ".comp.parquet") else f.stem
            for suffixe, cible in ((".nodes.parquet", par_uid_n),
                                   (".edges.parquet", par_uid_e)):
                g = f.with_name(base + suffixe)
                if not g.is_file():
                    continue
                try:
                    for r in _lit_parquet(g):
                        cible.setdefault(r.get("comp_uid"), []).append(r)
                except Exception as ex:                        # noqa: BLE001
                    rap["fichiers_illisibles"].append(
                        {"fichier": g.name, "erreur": str(ex)[:200]})
            rap["n_noeuds"] += sum(len(v) for v in par_uid_n.values())
            rap["n_aretes"] += sum(len(v) for v in par_uid_e.values())
        for r in rows:
            r = dict(r)
            film, cid = r.get("film"), r.get("comp_id")
            if film is None or cid is None:
                continue
            if not courte:
                uid = r.get("comp_uid")
                try:
                    r.update(_plan_depuis_longue(par_uid_n.get(uid, []),
                                                 par_uid_e.get(uid, [])))
                except CatalogueIncomplet as ex:
                    m = str(ex)[:80]
                    rap["motifs_sans_geometrie"][m] =                         rap["motifs_sans_geometrie"].get(m, 0) + 1
            if plan_vide(plan_de_ligne(r)):
                rap["n_sans_geometrie"] += 1
            else:
                rap["n_avec_geometrie"] += 1
            cat[(str(film), int(cid))] = r
    rap["n_composantes"] = len(cat)
    if exiger_geometrie and cat and rap["n_avec_geometrie"] == 0:
        raise CatalogueIncomplet(
            "les %d composantes de %s ne portent AUCUNE geometrie applicable "
            "(forme %r, colonnes %r). Un catalogue muet produirait des plans "
            "vides et un CSV au bit : l absence de correction passerait pour "
            "une decision. ARRET. Motifs : %r"
            % (len(cat), s, rap["forme"], rap["colonnes"][:12],
               rap["motifs_sans_geometrie"]))
    return cat, rap


def joint(decisions: list, composantes: dict) -> tuple[list, dict]:
    """Joint decisions x composantes sur `(film, comp_id)`.

    Une DECISION SANS COMPOSANTE arrete le lot : elle signifierait que le
    catalogue et le modele ne parlent pas du meme monde, et appliquer une
    geometrie qu on n a pas verifiee est exactement ce qu on refuse. Une
    COMPOSANTE SANS DECISION est un KEEP, silencieusement -- c est la regle.
    """
    out, orphelines = [], []
    for r in decisions:
        cle = (str(r["film"]), int(r["comp_id"]))
        c = composantes.get(cle)
        if c is None:
            orphelines.append({"film": cle[0], "comp_id": cle[1]})
            continue
        out.append({**c, **r})
    rap = {"n_decisions": len(decisions), "n_composantes": len(composantes),
           "n_jointes": len(out), "n_decisions_orphelines": len(orphelines),
           "exemples_orphelines": orphelines[:10],
           "n_composantes_sans_decision": len(composantes) - len(out)}
    if orphelines:
        raise SystemExit(
            "[composition_m2] %d decisions visent une composante ABSENTE du "
            "catalogue (ex. %r). Le catalogue et le modele ne parlent pas du "
            "meme monde. ARRET." % (len(orphelines), orphelines[:3]))
    return out, rap
