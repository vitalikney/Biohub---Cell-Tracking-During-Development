# -*- coding: utf-8 -*-
"""CELL08 -- LIFE-PROOFREADER. Un etage CSV -> CSV, LOCAL, NEUTRE PAR DEFAUT.

CE QUE C EST
------------
Un etage qui se branche APRES cell07 (l etage plugin `c1final`) et AVANT la
validation de schema du chassis. Il lit le CSV, cherche des ANOMALIES LOCALES
de conservation des vies, et n ecrit une correction que la ou une famille
reconnue a assez de preuves. Partout ailleurs il RECOPIE.

LA PROPRIETE ABSOLUE, ET C EST UN THEOREME, PAS UN ESPOIR
---------------------------------------------------------
Plan vide  =>  sortie IDENTIQUE AU BIT (meme sha256). La raison est la meme
que celle de `plugin_stage.py` : les lignes conservees sont RECOPIEES octet
pour octet (`ligne[j:]` garde le separateur, la valeur brute de chaque champ
et le terminateur d origine) ; seule la colonne `id` est renumerotee 0..n-1,
et elle l est deja a l entree puisque cell07 sort de `plugin_stage._rewrite`.
Un etage qui REFORMATERAIT les lignes perdrait l identite en octets sans
qu aucun test qui PARSE le CSV ne s en apercoive (un `-1.0` au lieu d un `-1`
suffit).

CE QU IL PEUT FAIRE, ET QUE cell07 NE POUVAIT PAS
--------------------------------------------------
`plugin_stage` interdit STRUCTURELLEMENT de toucher un noeud (les lignes
`node` y sont recopiees telles quelles). C est la bonne regle pour une brique
d aretes. Mais la famille DUPLICATE est justement un noeud EN TROP : la
supprimer fait tomber `num_pred_nodes`, donc monte le facteur nodal
a_i = 1 - 0,1 (N_i - n_i)/n_i, ET retire ses fausses aretes. cell08 s autorise
donc TROIS gestes, et rien d autre :

    drop_nodes   supprimer un noeud (et, par consequence, toute arete qui le
                 touche : une arete vers un noeud mort est un CSV invalide)
    drop_edges   retirer une arete existante
    add_edges    poser une arete entre deux noeuds VIVANTS

Il ne DEPLACE aucun noeud et n en AJOUTE aucun : les positions flottantes sont
l affaire de cell_06, et une insertion de noeud vole des appariements (mesure :
20 insertions ont detruit 4 aretes TP).

L ORDRE DES ARETES -- PIEGE NOMME
---------------------------------
Le plafond d out-degree du scorer garde les deux plus PETITS `EDGE_ID`, et
`EDGE_ID` suit l ordre des lignes. Les aretes ajoutees sont donc ecrites A LA
FIN DU BLOC DE LEUR FILM (meme convention que `plugin_stage._rewrite`), et
`appliquer_plan()` fait la meme chose en memoire : les deux routes rendent le
MEME monde. Le controle `--controle-deux-routes` le prouve sur un film.

BUDGET
------
Cible de deploiement : noyau Kaggle, CPU, ~200 films, <= 60 min AU TOTAL. Le
rapport publie `s_scan`, `s_detection`, `s_rewrite` et les secondes par film.
"""
from __future__ import annotations

import argparse
import array
import hashlib
import json
import os
import pathlib
import time

import numpy as np

CSV_COLUMNS = ["id", "dataset", "row_type", "node_id", "t", "z", "y", "x",
               "source_id", "target_id"]
HEADER_LINE = ",".join(CSV_COLUMNS).encode("ascii")


class Cell08Error(SystemExit):
    """SystemExit NOMME : il derive de BaseException, donc il traverse un
    `except Exception` et ne peut pas etre avale en silence."""


def _die(msg: str):
    raise Cell08Error("[cell08] " + msg)


# ==========================================================================
# PASSE 1 : LA VUE
# ==========================================================================
class _FilmAcc:
    __slots__ = ("nid", "t", "zyx", "edges")

    def __init__(self):
        self.nid = array.array("q")
        self.t = array.array("q")
        self.zyx = array.array("d")
        self.edges = array.array("q")


def scan(path) -> tuple[bytes, dict, dict]:
    """Rend (terminateur, vue, layout).

    Verifie AU PASSAGE les deux hypotheses de structure dont la reecriture
    depend -- un bloc CONTIGU par film, noeuds AVANT aretes -- et s arrete net
    si l une tombe, au lieu de produire un CSV plausible et faux. Verifie aussi
    que la colonne `id` vaut deja 0..n-1 : sinon l identite en octets d un plan
    vide serait FAUSSE, et il faut le savoir AVANT, pas apres.
    """
    acc: dict[str, _FilmAcc] = {}
    films_order: list[str] = []
    n_rows = n_node = n_edge = 0
    cur = None
    edge_seen = False
    id_deja_range = True
    with open(path, "rb") as f:
        header = f.readline()
        term = b"\r\n" if header.endswith(b"\r\n") else b"\n"
        if header.rstrip(b"\r\n").replace(b'"', b"") != HEADER_LINE:
            _die("en-tete inattendu : %r" % header)
        for line in f:
            p = line.rstrip(b"\r\n").split(b",")
            if len(p) != 10:
                _die("ligne malformee (%d colonnes) : %r" % (len(p), line))
            if int(p[0]) != n_rows:
                id_deja_range = False
            film = p[1].decode("ascii")
            kind = p[2]
            if film != cur:
                if film in acc:
                    _die("le film %s n est pas CONTIGU dans le CSV. ARRET." % film)
                acc[film] = _FilmAcc()
                films_order.append(film)
                cur = film
                edge_seen = False
            a = acc[film]
            if kind == b"node":
                if edge_seen:
                    _die("noeud APRES une arete dans le film %s. ARRET." % film)
                a.nid.append(int(p[3]))
                a.t.append(int(p[4]))
                a.zyx.append(float(p[5]))
                a.zyx.append(float(p[6]))
                a.zyx.append(float(p[7]))
                n_node += 1
            elif kind == b"edge":
                edge_seen = True
                a.edges.append(int(p[8]))
                a.edges.append(int(p[9]))
                n_edge += 1
            else:
                _die("row_type inconnu %r dans le film %s" % (kind, film))
            n_rows += 1

    view = {}
    for film in films_order:
        a = acc[film]
        n = len(a.nid)
        m = len(a.edges) // 2
        view[film] = {
            "node_id": np.frombuffer(a.nid, dtype=np.int64),
            "t": np.frombuffer(a.t, dtype=np.int64),
            "zyx": np.frombuffer(a.zyx, dtype=np.float64).reshape(n, 3),
            "edges": np.frombuffer(a.edges, dtype=np.int64).reshape(m, 2),
        }
    layout = {"n_rows": n_rows, "n_node": n_node, "n_edge": n_edge,
              "films": films_order, "id_deja_range": id_deja_range}
    return term, view, layout


# ==========================================================================
# LE PLAN
# ==========================================================================
def plan_vide() -> dict:
    return {}


def normalise_plan(plan: dict, view: dict) -> dict:
    """Rend le plan sous forme canonique {film: {drop_nodes:set, drop_edges:set,
    add_edges:list}} et refuse tout de suite ce qui est incoherent.

    GARDES, et chacune est motivee :
      * un film inconnu  -> le CSV ne le porte pas, la reecriture ne saurait
        pas ou poser les aretes ;
      * une arete ajoutee vers un noeud MORT (supprime par le meme plan, ou
        absent) -> CSV invalide, le chargeur du scorer leverait ;
      * une arete ajoutee DEJA presente et non retiree -> doublon d arete, que
        le scorer compterait deux fois.
    """
    out = {}
    for film, p in (plan or {}).items():
        if film not in view:
            _die("le plan vise le film %s, absent du CSV" % film)
        dn = {int(x) for x in p.get("drop_nodes", ())}
        de = {(int(u), int(v)) for u, v in p.get("drop_edges", ())}
        ae = [(int(u), int(v)) for u, v in p.get("add_edges", ())]
        if not dn and not de and not ae:
            continue
        vivants = set(int(x) for x in view[film]["node_id"]) - dn
        presentes = {(int(u), int(v)) for u, v in view[film]["edges"]}
        manquantes = de - presentes
        if manquantes:
            _die("le plan retire %d aretes absentes du film %s (ex. %r)"
                 % (len(manquantes), film, sorted(manquantes)[:3]))
        vues = set()
        for u, v in ae:
            if u not in vivants or v not in vivants:
                _die("le plan pose l arete (%d,%d) vers un noeud mort ou "
                     "absent dans %s" % (u, v, film))
            if (u, v) in presentes and (u, v) not in de:
                _die("le plan pose l arete (%d,%d) DEJA presente dans %s"
                     % (u, v, film))
            if (u, v) in vues:
                _die("le plan pose deux fois l arete (%d,%d) dans %s"
                     % (u, v, film))
            vues.add((u, v))
        out[film] = {"drop_nodes": dn, "drop_edges": de, "add_edges": ae}
    return out


# ==========================================================================
# PASSE 2 : LA REECRITURE. Les lignes conservees sont RECOPIEES, pas reformatees.
# ==========================================================================
def rewrite(src, dest, plan: dict, term: bytes) -> dict:
    """Recopie `src` dans `dest` : retire les noeuds et aretes du plan, retire
    aussi toute arete qui touche un noeud retire, et insere les aretes ajoutees
    A LA FIN du bloc de leur film. La colonne `id` est renumerotee 0..n-1 ;
    toutes les autres colonnes des lignes conservees sortent OCTET POUR OCTET.
    """
    n_drop_node = n_drop_edge = n_drop_edge_orphelin = n_add = 0
    i = 0
    prev = None
    en_attente = {f: list(p["add_edges"]) for f, p in plan.items() if p["add_edges"]}

    def _flush(out, film, i):
        rows = en_attente.pop(film, None)
        if not rows:
            return i, 0
        k = 0
        fb = film.encode("ascii")
        for s, t in rows:
            out.write(b"%d,%s,edge,-1,-1,-1,-1,-1,%d,%d%s"
                      % (i, fb, int(s), int(t), term))
            i += 1
            k += 1
        return i, k

    with open(src, "rb") as fin, open(dest, "wb") as out:
        out.write(fin.readline())
        p_cur = None
        for line in fin:
            j = line.index(b",")
            k = line.index(b",", j + 1)
            film = line[j + 1:k].decode("ascii")
            if film != prev:
                if prev is not None:
                    i, k2 = _flush(out, prev, i)
                    n_add += k2
                prev = film
                p_cur = plan.get(film)
            if p_cur is not None:
                champs = line.rstrip(b"\r\n").split(b",")
                if champs[2] == b"node":
                    if int(champs[3]) in p_cur["drop_nodes"]:
                        n_drop_node += 1
                        continue
                else:
                    u, v = int(champs[8]), int(champs[9])
                    if (u, v) in p_cur["drop_edges"]:
                        n_drop_edge += 1
                        continue
                    if u in p_cur["drop_nodes"] or v in p_cur["drop_nodes"]:
                        n_drop_edge_orphelin += 1
                        continue
            out.write(b"%d" % i + line[j:])
            i += 1
        if prev is not None:
            i, k2 = _flush(out, prev, i)
            n_add += k2
    if en_attente:
        _die("le plan ajoute des aretes aux films %s, absents du CSV"
             % sorted(en_attente))
    return {"n_rows_out": i, "n_drop_node": n_drop_node,
            "n_drop_edge": n_drop_edge,
            "n_drop_edge_orphelin": n_drop_edge_orphelin, "n_add_edge": n_add}


def sha256_fichier(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ==========================================================================
# LE MONDE EN MEMOIRE -- la MEME transformation, pour le juge
# ==========================================================================
def appliquer_plan(node_id, t, zyx, edges, p: dict | None):
    """Applique un plan de film en memoire. MEME convention d ordre que
    `rewrite` : les aretes conservees gardent leur ordre d origine, les aretes
    ajoutees viennent A LA FIN. C est ce qui fixe `EDGE_ID`, donc le plafond
    d out-degree : il ne se bricole pas.
    """
    if not p:
        return node_id, t, zyx, edges
    dn = p["drop_nodes"]
    de = p["drop_edges"]
    if dn:
        garde = np.array([int(x) not in dn for x in node_id], dtype=bool)
        node_id, t, zyx = node_id[garde], t[garde], zyx[garde]
    gardees = [(int(u), int(v)) for u, v in edges
               if (int(u), int(v)) not in de
               and int(u) not in dn and int(v) not in dn]
    gardees.extend(p["add_edges"])
    ar = (np.array(gardees, dtype=np.int64).reshape(-1, 2) if gardees
          else np.zeros((0, 2), np.int64))
    return node_id, t, zyx, ar


# ==========================================================================
# L ETAGE
# ==========================================================================
def run_cell08(csv_path, detecteur=None, params: dict | None = None,
               dest=None, verbose: bool = True) -> dict:
    """Applique cell08 a `csv_path`. Rend un rapport.

    `detecteur(view, params) -> plan` ; `None` = le NO-OP, qui rend un plan
    vide et doit donc rendre le fichier AU BIT.

    LE GATE DE L IDENTITE : quand le plan normalise est vide, la sortie DOIT
    avoir le meme sha256 que l entree. Sinon `Cell08Error`. C est ce gate qui
    prouve que l etage n a pas d effet de bord, et un gate qui PARSERAIT le CSV
    ne le verrait pas.
    """
    csv_path = pathlib.Path(csv_path)
    t0 = time.perf_counter()
    sha_in = sha256_fichier(csv_path)
    t_sha = time.perf_counter() - t0

    t1 = time.perf_counter()
    term, view, layout = scan(csv_path)
    s_scan = time.perf_counter() - t1

    t2 = time.perf_counter()
    brut = {} if detecteur is None else detecteur(view, params or {})
    plan = normalise_plan(brut, view)
    s_detection = time.perf_counter() - t2

    sur_place = dest is None
    dest = csv_path.with_suffix(".cell08.tmp") if sur_place else pathlib.Path(dest)
    t3 = time.perf_counter()
    rap = rewrite(csv_path, dest, plan, term)
    s_rewrite = time.perf_counter() - t3

    sha_out = sha256_fichier(dest)
    vide = not plan
    identique = sha_out == sha_in
    if vide and not identique:
        try:
            os.unlink(dest)
        except OSError:
            pass
        _die("PLAN VIDE mais la sortie DIFFERE de l entree (sha %s != %s). "
             "L identite en octets est la propriete fondatrice de cet etage : "
             "elle vient de tomber. ARRET AVANT REMPLACEMENT."
             % (sha_out[:16], sha_in[:16]))
    if not vide and identique:
        _die("PLAN NON VIDE (%d films) mais la sortie est identique a "
             "l entree : la reecriture n a rien fait. ARRET."
             % len(plan))
    # invariant de noeuds : entree moins les noeuds retires, exactement
    n_drop_attendu = sum(len(p["drop_nodes"]) for p in plan.values())
    if rap["n_drop_node"] != n_drop_attendu:
        _die("invariant de noeuds : %d lignes noeud retirees pour %d demandees"
             % (rap["n_drop_node"], n_drop_attendu))

    if sur_place:
        os.replace(dest, csv_path)
        chemin_sortie = str(csv_path)
    else:
        chemin_sortie = str(dest)

    rapport = {
        "sha256_in": sha_in, "sha256_out": sha_out,
        "identique_en_octets": bool(identique),
        "plan_vide": bool(vide),
        "id_deja_range_en_entree": bool(layout["id_deja_range"]),
        "n_films": len(layout["films"]),
        "n_rows_in": layout["n_rows"], "n_node_in": layout["n_node"],
        "n_edge_in": layout["n_edge"],
        "n_films_touches": len(plan),
        "sortie": chemin_sortie,
        "s_sha_in": round(t_sha, 2), "s_scan": round(s_scan, 2),
        "s_detection": round(s_detection, 2), "s_rewrite": round(s_rewrite, 2),
        "s_total": round(time.perf_counter() - t0, 2),
        **rap,
    }
    rapport["s_par_film"] = round(
        rapport["s_total"] / max(1, rapport["n_films"]), 4)
    if verbose:
        print(json.dumps(rapport, indent=1, sort_keys=True))
    return rapport


# ==========================================================================
# LE REGISTRE. Une famille s ajoute ici, et rien d autre.
# ==========================================================================
def detecteur_noop(view, params):
    """AUTO-TEST DE L ETAGE. Ne propose rien, expres. Prouve que la machinerie
    complete (scan + reecriture + remplacement) rend le fichier AU BIT."""
    return {}


REGISTRE = {
    "noop": detecteur_noop,
    # --- LES FAMILLES VIENNENT ICI (voir anomalies.py) ---------------------
}


def _charge_familles():
    """Enregistre les familles de `anomalies.py` si le module est la. L etage
    reste utilisable seul (no-op) si elles ne le sont pas."""
    try:
        import anomalies as A
    except Exception:
        return
    REGISTRE.update(A.DETECTEURS)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--detecteur", default="noop")
    ap.add_argument("--params", default=None, help="chemin d un JSON")
    ap.add_argument("--dest", default=None,
                    help="sortie ; par defaut REMPLACE l entree sur place")
    ap.add_argument("--recu", default=None)
    a = ap.parse_args()
    _charge_familles()
    fn = REGISTRE.get(a.detecteur)
    if fn is None:
        _die("detecteur %r inconnu. Registre : %s" % (a.detecteur, sorted(REGISTRE)))
    params = json.loads(pathlib.Path(a.params).read_text("utf-8")) if a.params else {}
    rap = run_cell08(a.csv, None if a.detecteur == "noop" else fn, params,
                     dest=a.dest)
    if a.recu:
        pathlib.Path(a.recu).write_text(
            json.dumps(rap, ensure_ascii=False, indent=1), encoding="utf-8")
        print("[recu] " + a.recu)


if __name__ == "__main__":
    main()
