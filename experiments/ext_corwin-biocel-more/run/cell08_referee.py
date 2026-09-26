# -*- coding: utf-8 -*-
"""CELL08 REFEREE -- l etage de PROOFREADER etendu aux SIX FAMILLES de mondes.

CE QU IL AJOUTE A `cell08_proofreader`
--------------------------------------
PROOFREADER a prouve un etage CSV -> CSV a TROIS gestes (drop_nodes,
drop_edges, add_edges) et son theoreme : plan vide => sortie AU BIT. Cet
etage-ci HERITE de ce module (il ne le recopie pas) et lui ajoute les deux
gestes que les six familles du LIFE-REFEREE exigent, et rien de plus :

    move_nodes   deplacer un noeud (W2 parabole, et le type 'm' du monde mixte
                 de CIBLAGE : un couple appareille dont la position differe)
    add_nodes    poser un noeud qui n existe pas dans le monde KEEP (W1 TTA
                 corrigee iso-compte, W5 GAP : le type 'a' du monde mixte)

Les six familles se ramenent TOUTES a ces cinq gestes, parce que la difference
entre deux mondes se decompose exactement en entites r / m / a / E / A
(`CIBLAGE/impl/oracle_local.py::entites`) :

    W1 TTA corrigee iso   -> move + add + drop + aretes
    W2 parabole           -> move seul
    W3 DUPLICATE/FUSION   -> drop_nodes + aretes
    W4 SWAP/RELINK        -> drop_edges + add_edges
    W5 GAP                -> add_edges (+ add_nodes si le monde candidat en pose)
    W6 DIVIDE CUT+ADD     -> drop_edges + add_edges

LES QUATRE PROPRIETES QUI SE PROUVENT, ET QUI SONT DES THEOREMES
----------------------------------------------------------------
1. LISTE DE DECISIONS VIDE => SORTIE AU BIT (meme sha256). Herite : les lignes
   conservees sont RECOPIEES octet pour octet. Le gate de `run_cell08` leve un
   `Cell08Error` avant tout remplacement si l egalite tombe.
2. KEEP PAR DEFAUT. Une composante sans decision REPLACE explicite n existe pas
   dans le plan. La foule est portante (PROOFREADER RENDU §4) : on ne compose
   QUE ce que le referee designe, jamais une famille entiere.
3. IDENTIFIANTS UNIQUES. Les noeuds ajoutes recoivent `max(node_id du film)+1,
   +2, ...`. Une arete peut viser un noeud ajoute par la reference LOCALE
   NEGATIVE `-(k+1)` -> `add_nodes[k]`. Toute collision est refusee.
4. GARDE DE METROLOGY -- LE POINT DECIMAL. `pl.read_csv` du scorer infere le
   schema sur 100 lignes : une colonne z ENTIERE suivie d un flottant plus loin
   leve `ComputeError` et la soumission ECHOUE. Des qu une decision ecrit une
   coordonnee non entiere dans un CSV dont les coordonnees sont entieres, cet
   etage FLOTTANTISE TOUTES les lignes noeud (`12` -> `12.0`, exact : on
   suffixe `.0`, on ne reformate pas). La transformation ne change aucune
   valeur -- `csv_to_geffs.py` caste en Float64 des deux cotes.

L ORDRE DES LIGNES -- PIEGE NOMME, ET SA RESOLUTION
---------------------------------------------------
Le juge n est PAS invariant a l ordre (ETAGE RENDU §6 : +1,32e-04 rien que par
l ordre). Conventions de cet etage, identiques sur les DEUX routes (CSV et
memoire), ce qui rend le controle des deux routes AU BIT :

    * les noeuds ajoutes sont ecrits A LA FIN DU BLOC DE NOEUDS de leur film
      (le scan refuse un noeud apres une arete : la structure l impose) ;
    * les aretes ajoutees sont ecrites A LA FIN DU BLOC DU FILM (convention de
      `plugin_stage._rewrite`, heritee de PROOFREADER) ;
    * la colonne `id` est renumerotee 0..n-1.

Le monde mixte de CIBLAGE, lui, fusionne les deux ordres. Les deux mondes ont
alors les MEMES noeuds et les MEMES aretes, et un ordre different. C est
pourquoi TOUT jugement passe par la CANONISATION (`ETAGE/impl/pod/canoniser.py`
ou `oracle_local.canonise`) : canoniser pour juger, jamais avant l etage.

BUDGET
------
Le rapport publie `s_scan`, `s_detection`, `s_rewrite`, les secondes par film,
et `flottantise` (le surcout du point decimal).
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import sys
import time

import numpy as np

ICI = pathlib.Path(__file__).resolve().parent
# `cell08_proofreader` vit dans la lane PROOFREADER. Dans le depot il est deux
# niveaux au-dessus ; sur un pod, la lane est deployee ailleurs et le chemin est
# donne par REFEVAL_PROOF_IMPL. On essaie les deux, dans cet ordre, et on ne
# fait CONFIANCE a aucun des deux : l import qui suit dira lequel a marche.
import os  # noqa: E402
for _p in (os.environ.get("REFEVAL_PROOF_IMPL"),
           str(ICI.parents[2] / "PROOFREADER" / "impl"),
           str(ICI / "impl_proof"), str(ICI.parent / "impl_proof")):
    if _p and pathlib.Path(_p).is_dir() and _p not in sys.path:
        sys.path.insert(0, _p)

import cell08_proofreader as C8  # noqa: E402

CSV_COLUMNS = C8.CSV_COLUMNS
Cell08Error = C8.Cell08Error
sha256_fichier = C8.sha256_fichier


def sha_concorde(declare, reel) -> bool:
    """Le sha declare par un plan concorde-t-il avec celui du monde ?

    On accepte un PREFIXE d au moins 12 caracteres : les recus de ce sprint
    citent souvent les mondes par leurs 16 premiers (`e5804496b02d627e`), et
    refuser cette forme ferait echouer la garde sur des plans JUSTES -- une
    garde qui refuse tout ne protege rien. En dessous de 12 caracteres on
    refuse : un prefixe trop court ne distingue plus deux mondes.
    """
    if not declare or not reel:
        return False
    d, r = str(declare).strip().lower(), str(reel).strip().lower()
    if len(d) < 12 or len(r) < 12:
        return False
    return r.startswith(d) or d.startswith(r)

_die = C8._die

FAMILLES = ("W1_TTA_ISO", "W2_PARAB", "W3_DUPLICATE", "W4_SWAP_RELINK",
            "W5_GAP", "W6_DIVIDE")


def date_u() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


# ==========================================================================
# PASSE 1 : LA VUE. Meme scan que PROOFREADER, plus DEUX faits de forme dont
# la garde de METROLOGY et l allocation d identifiants dependent.
# ==========================================================================
def scan(path) -> tuple[bytes, dict, dict]:
    """Rend (terminateur, vue, layout).

    Ajoute a `C8.scan` :
      * `tous_flottants` -- vrai si TOUTE ligne noeud porte un point decimal en
        z, y ET x. S il est faux, ecrire une coordonnee flottante impose de
        flottantiser tout le fichier (garde de METROLOGY) ;
      * `max_node_id` par film -- la base d allocation des noeuds ajoutes ;
      * `n_node` par film -- pour le controle d invariant.
    """
    term, view, layout = C8.scan(path)
    tous_flottants = True
    toutes_entieres = True
    with open(path, "rb") as f:
        f.readline()
        for line in f:
            p = line.rstrip(b"\r\n").split(b",")
            if p[2] != b"node":
                continue
            if not (b"." in p[5] and b"." in p[6] and b"." in p[7]):
                tous_flottants = False
            # LE TEXTE ET LA VALEUR SONT DEUX CHOSES, et l avoir oublie a
            # produit un monde au mauvais format le 05/09 : << 8.0 >> s ECRIT
            # en flottant et VAUT un entier. La page Kaggle exige des entiers,
            # et REF-DATA a mesure qu un lecteur polars en Int64 ECHOUE sur
            # << 8.0 >> des le premier noeud. Il faut donc savoir si les
            # VALEURS sont entieres, pas seulement comment elles s ecrivent.
            for c in (p[5], p[6], p[7]):
                if b"." in c and c.split(b".", 1)[1].strip(b"0"):
                    toutes_entieres = False
                    break
            if not tous_flottants and not toutes_entieres:
                break
    layout["tous_flottants"] = tous_flottants
    layout["toutes_valeurs_entieres"] = toutes_entieres
    for film, v in view.items():
        v["max_node_id"] = int(v["node_id"].max()) if len(v["node_id"]) else -1
    return term, view, layout


# ==========================================================================
# LE PLAN ETENDU
# ==========================================================================
def _coord(x) -> float:
    v = float(x)
    if not np.isfinite(v):
        _die("coordonnee non finie : %r" % (x,))
    return v


def _entier(v: float) -> bool:
    return float(v).is_integer()


def normalise_plan(plan: dict, view: dict) -> dict:
    """Forme canonique {film: {drop_nodes, move_nodes, add_nodes, drop_edges,
    add_edges, id_ajoutes}} et refus immediat de tout ce qui est incoherent.

    GARDES, chacune motivee (les trois premieres sont celles de PROOFREADER) :
      * film inconnu -> la reecriture ne saurait pas ou poser les lignes ;
      * arete retiree absente / arete posee en double / arete posee deja
        presente -> le scorer compterait faux ;
      * arete posee vers un noeud MORT ou ABSENT -> CSV invalide ;
      * NOUVEAU : `move_nodes` sur un noeud absent ou supprime par le meme plan
        -> le geste n a pas de cible ;
      * NOUVEAU : un noeud ajoute dont l identifiant existe deja -> le CSV
        porterait deux fois le meme `node_id` et le chargeur du scorer les
        confondrait. Les identifiants sont donc ALLOUES ici, jamais fournis.
      * NOUVEAU : une reference locale `-(k+1)` hors de `add_nodes` -> arret.
    """
    out = {}
    for film, p in (plan or {}).items():
        if film not in view:
            _die("le plan vise le film %s, absent du CSV" % film)
        v = view[film]
        dn = {int(x) for x in p.get("drop_nodes", ())}
        mv = {}
        for e in p.get("move_nodes", ()):
            nid, z, y, x = (int(e[0]), _coord(e[1]), _coord(e[2]), _coord(e[3]))
            if nid in mv:
                _die("le plan deplace deux fois le noeud %d dans %s" % (nid, film))
            mv[nid] = (z, y, x)
        an = []
        for e in p.get("add_nodes", ()):
            t, z, y, x = (int(e[0]), _coord(e[1]), _coord(e[2]), _coord(e[3]))
            an.append((t, z, y, x))
        de = {(int(u), int(v_)) for u, v_ in p.get("drop_edges", ())}
        ae_brut = [(int(u), int(v_)) for u, v_ in p.get("add_edges", ())]
        if not (dn or mv or an or de or ae_brut):
            continue

        presents = set(int(x) for x in v["node_id"])
        if len(presents) != len(v["node_id"]):
            _die("le film %s porte des node_id EN DOUBLE a l entree" % film)
        vivants = presents - dn

        # --- identifiants alloues, uniques par construction --------------
        base = v["max_node_id"] + 1
        id_ajoutes = [base + k for k in range(len(an))]
        for nid in id_ajoutes:
            if nid in presents:
                _die("collision d identifiant %d dans %s" % (nid, film))
        vivants |= set(id_ajoutes)

        def resous(x: int) -> int:
            if x < 0:
                k = -x - 1
                if k >= len(an):
                    _die("reference locale %d hors de add_nodes (%d) dans %s"
                         % (x, len(an), film))
                return id_ajoutes[k]
            return x

        for nid in mv:
            if nid not in presents:
                _die("le plan deplace le noeud %d, absent de %s" % (nid, film))
            if nid in dn:
                _die("le plan deplace ET supprime le noeud %d dans %s" % (nid, film))

        presentes = {(int(u), int(v_)) for u, v_ in v["edges"]}
        manquantes = de - presentes
        if manquantes:
            _die("le plan retire %d aretes absentes du film %s (ex. %r)"
                 % (len(manquantes), film, sorted(manquantes)[:3]))
        ae, vues = [], set()
        for u, v_ in ae_brut:
            u, v_ = resous(u), resous(v_)
            if u not in vivants or v_ not in vivants:
                _die("le plan pose l arete (%d,%d) vers un noeud mort ou absent "
                     "dans %s" % (u, v_, film))
            if (u, v_) in presentes and (u, v_) not in de:
                _die("le plan pose l arete (%d,%d) DEJA presente dans %s"
                     % (u, v_, film))
            if (u, v_) in vues:
                _die("le plan pose deux fois l arete (%d,%d) dans %s" % (u, v_, film))
            vues.add((u, v_))
            ae.append((u, v_))

        out[film] = {"drop_nodes": dn, "move_nodes": mv, "add_nodes": an,
                     "drop_edges": de, "add_edges": ae, "id_ajoutes": id_ajoutes}
    return out


def plan_a_des_flottants(plan: dict) -> bool:
    """Vrai si une coordonnee ECRITE par le plan n est pas entiere."""
    for p in plan.values():
        for z, y, x in p["move_nodes"].values():
            if not (_entier(z) and _entier(y) and _entier(x)):
                return True
        for _, z, y, x in p["add_nodes"]:
            if not (_entier(z) and _entier(y) and _entier(x)):
                return True
    return False


# ==========================================================================
# LE FORMAT DES COORDONNEES
# ==========================================================================
def fmt_coord(v: float, mode_flottant: bool = True) -> bytes:
    """Texte d une coordonnee ECRITE par cet etage, DANS LE MODE DU FICHIER.

    LA GARDE DE METROLOGY JOUE DANS LES DEUX SENS. `pl.read_csv` infere le
    schema sur 100 lignes : un `12.0` isole dans un fichier entier leve autant
    qu un `12` isole dans un fichier flottant. Le mode est donc decide UNE FOIS
    pour tout le fichier (`mode_flottant`), et cette fonction s y conforme.

    En mode flottant, `repr` d un float Python est la plus courte chaine qui
    relit EXACTEMENT le meme double : l aller-retour CSV -> Float64 est sans
    perte, et METROLOGY a verifie l aller-retour CSV -> geff au bit (12,5 /
    100,25 / 200,75). En mode entier, la valeur DOIT etre entiere -- sinon le
    plan n aurait pas du laisser `mode_flottant` a faux, et on s arrete.
    """
    if not mode_flottant:
        if not _entier(v):
            _die("coordonnee non entiere %r ecrite en mode ENTIER : la garde de "
                 "METROLOGY imposait de flottantiser le fichier. ARRET." % (v,))
        return b"%d" % int(v)
    s = repr(float(v))
    if "e" in s or "E" in s:                 # 1e-05 : illisible pour un humain,
        s = "%.10f" % float(v)               # et le scorer lit les deux ; on
        s = s.rstrip("0")                    # prefere la forme longue.
        if s.endswith("."):
            s += "0"
    if "." not in s:
        s += ".0"
    return s.encode("ascii")


def flottantise(champs: list[bytes]) -> None:
    """Suffixe `.0` aux colonnes z, y, x qui n ont pas de point decimal.

    EXACT PAR CONSTRUCTION : on n a pas reformate le nombre, on lui a ajoute une
    partie decimale nulle. `12` -> `12.0`, `-1` -> `-1.0`. Aucune valeur ne
    change ; seule la forme change, et c est la forme que `pl.read_csv` regarde.
    """
    for j in (5, 6, 7):
        c = champs[j]
        if b"." not in c and b"e" not in c and b"E" not in c:
            champs[j] = c + b".0"


# ==========================================================================
# PASSE 2 : LA REECRITURE
# ==========================================================================
def rewrite(src, dest, plan: dict, term: bytes,
            mode_flottant: bool = True,
            forcer_flottants: bool = False,
            forcer_entiers: bool = False) -> dict:
    """Recopie `src` dans `dest` en appliquant les CINQ gestes.

    Conventions d ordre (voir l en-tete) : noeuds ajoutes a la fin du bloc de
    noeuds du film, aretes ajoutees a la fin du bloc du film.
    """
    n = {"n_drop_node": 0, "n_move_node": 0, "n_add_node": 0, "n_drop_edge": 0,
         "n_drop_edge_orphelin": 0, "n_add_edge": 0, "n_lignes_flottantisees": 0,
         "n_lignes_entierisees": 0}
    i = 0
    prev = None
    p_cur = None
    noeuds_faits = False   # le bloc de noeuds du film courant est ferme

    def ecrit_noeuds_ajoutes(out, film, p, i):
        if p is None or not p["add_nodes"]:
            return i
        fb = film.encode("ascii")
        for (t, z, y, x), nid in zip(p["add_nodes"], p["id_ajoutes"]):
            out.write(b"%d,%s,node,%d,%d,%s,%s,%s,-1,-1%s"
                      % (i, fb, nid, t, fmt_coord(z, mode_flottant),
                         fmt_coord(y, mode_flottant),
                         fmt_coord(x, mode_flottant), term))
            i += 1
            n["n_add_node"] += 1
        return i

    def ecrit_aretes_ajoutees(out, film, p, i):
        if p is None or not p["add_edges"]:
            return i
        fb = film.encode("ascii")
        for s, t in p["add_edges"]:
            out.write(b"%d,%s,edge,-1,-1,-1,-1,-1,%d,%d%s"
                      % (i, fb, int(s), int(t), term))
            i += 1
            n["n_add_edge"] += 1
        return i

    with open(src, "rb") as fin, open(dest, "wb") as out:
        out.write(fin.readline())
        for line in fin:
            j = line.index(b",")
            k = line.index(b",", j + 1)
            film = line[j + 1:k].decode("ascii")
            if film != prev:
                if prev is not None:
                    if not noeuds_faits:
                        i = ecrit_noeuds_ajoutes(out, prev, p_cur, i)
                    i = ecrit_aretes_ajoutees(out, prev, p_cur, i)
                prev = film
                p_cur = plan.get(film)
                noeuds_faits = False
            est_noeud = line[k + 1:k + 6] == b"node,"
            if not est_noeud and not noeuds_faits:
                i = ecrit_noeuds_ajoutes(out, film, p_cur, i)
                noeuds_faits = True
            if p_cur is None and not (forcer_flottants or forcer_entiers):
                out.write(b"%d" % i + line[j:])
                i += 1
                continue
            champs = line.rstrip(b"\r\n").split(b",")
            if est_noeud:
                nid = int(champs[3])
                if p_cur is not None and nid in p_cur["drop_nodes"]:
                    n["n_drop_node"] += 1
                    continue
                if p_cur is not None and nid in p_cur["move_nodes"]:
                    z, y, x = p_cur["move_nodes"][nid]
                    champs[5] = fmt_coord(z, mode_flottant)
                    champs[6] = fmt_coord(y, mode_flottant)
                    champs[7] = fmt_coord(x, mode_flottant)
                    n["n_move_node"] += 1
                elif forcer_flottants:
                    avant = (champs[5], champs[6], champs[7])
                    flottantise(champs)
                    if (champs[5], champs[6], champs[7]) != avant:
                        n["n_lignes_flottantisees"] += 1
                elif forcer_entiers:
                    avant = (champs[5], champs[6], champs[7])
                    for _c in (5, 6, 7):
                        champs[_c] = fmt_coord(float(champs[_c]), False)
                    if (champs[5], champs[6], champs[7]) != avant:
                        n["n_lignes_entierisees"] += 1
            elif p_cur is not None:
                u, v = int(champs[8]), int(champs[9])
                if (u, v) in p_cur["drop_edges"]:
                    n["n_drop_edge"] += 1
                    continue
                if u in p_cur["drop_nodes"] or v in p_cur["drop_nodes"]:
                    n["n_drop_edge_orphelin"] += 1
                    continue
            champs[0] = b"%d" % i
            out.write(b",".join(champs) + term)
            i += 1
        if prev is not None:
            if not noeuds_faits:
                i = ecrit_noeuds_ajoutes(out, prev, p_cur, i)
            i = ecrit_aretes_ajoutees(out, prev, p_cur, i)
    n["n_rows_out"] = i
    return n


# ==========================================================================
# LE MONDE EN MEMOIRE -- LA MEME transformation, MEMES conventions d ordre
# ==========================================================================
def appliquer_plan(node_id, t, zyx, edges, p: dict | None):
    """Applique un plan de film en memoire, avec l ordre de `rewrite` :
    noeuds ajoutes A LA FIN des noeuds, aretes ajoutees A LA FIN des aretes.
    C est ce qui rend le controle des deux routes AU BIT.
    """
    if not p:
        return node_id, t, zyx, edges
    dn, mv, an = p["drop_nodes"], p["move_nodes"], p["add_nodes"]
    de = p["drop_edges"]
    node_id = np.asarray(node_id, dtype=np.int64)
    t = np.asarray(t, dtype=np.int64)
    zyx = np.array(zyx, dtype=np.float64, copy=True)
    if mv:
        pos = {int(v_): k for k, v_ in enumerate(node_id)}
        for nid, (z, y, x) in mv.items():
            zyx[pos[int(nid)]] = (z, y, x)
    if dn:
        garde = np.array([int(x) not in dn for x in node_id], dtype=bool)
        node_id, t, zyx = node_id[garde], t[garde], zyx[garde]
    if an:
        node_id = np.concatenate(
            [node_id, np.array(p["id_ajoutes"], dtype=np.int64)])
        t = np.concatenate([t, np.array([e[0] for e in an], dtype=np.int64)])
        zyx = np.concatenate(
            [zyx, np.array([[e[1], e[2], e[3]] for e in an], dtype=np.float64)])
    gardees = [(int(u), int(v_)) for u, v_ in edges
               if (int(u), int(v_)) not in de
               and int(u) not in dn and int(v_) not in dn]
    gardees.extend(p["add_edges"])
    ar = (np.array(gardees, dtype=np.int64).reshape(-1, 2) if gardees
          else np.zeros((0, 2), np.int64))
    return node_id, t, zyx, ar


# ==========================================================================
# L ETAGE
# ==========================================================================
def run_cell08(csv_path, plan_brut: dict | None = None, dest=None,
               verbose: bool = True, forcer_flottants: bool | None = None,
               sha_monde_attendu: str | None = None,
               entiers: bool | None = None) -> dict:
    """Applique cell08-referee a `csv_path` avec un plan DEJA CONSTRUIT.

    LE GATE DE L IDENTITE (herite, et c est lui qui vaut G0) : plan normalise
    vide => sha256 de sortie == sha256 d entree, sinon `Cell08Error` AVANT tout
    remplacement.
    """
    csv_path = pathlib.Path(csv_path)
    t0 = time.perf_counter()
    sha_in = sha256_fichier(csv_path)
    t_sha = time.perf_counter() - t0

    # ---- LA GARDE D ORIGINE ------------------------------------------
    # Un plan est ecrit dans les identifiants d UN monde. Applique a un AUTRE
    # monde, il coupe et pose des aretes AU HASARD -- et rien ne leve : les
    # identifiants existent, les aretes existent, le CSV reste valide. Le
    # chiffre qui sort est parfaitement credible et ne veut rien dire.
    # C est la QUATRIEME fois aujourd hui que cette classe de faute frappe
    # (oracle DUPLICATE contre un temoin r=8 perime ; Delta60 du BANC contre une
    # reference non canonisee ; plans MITOSE ecrits dans les identifiants du
    # monde LISSE). Le plan DECLARE donc le sha du monde auquel il appartient,
    # et l etage REFUSE de l appliquer ailleurs.
    if sha_monde_attendu and not sha_concorde(sha_monde_attendu, sha_in):
        _die("GARDE D ORIGINE : le plan declare appartenir au monde %s... mais "
             "on l applique a %s... Un plan applique au mauvais monde coupe et "
             "pose des aretes AU HASARD sans qu aucune verification ne leve. "
             "ARRET." % (sha_monde_attendu[:16], sha_in[:16]))

    t1 = time.perf_counter()
    term, view, layout = scan(csv_path)
    s_scan = time.perf_counter() - t1

    t2 = time.perf_counter()
    plan = normalise_plan(plan_brut or {}, view)
    s_detection = time.perf_counter() - t2

    # ---- LE FORMAT DES COORDONNEES -----------------------------------
    # La page Kaggle exige des ENTIERS, et REF-DATA a mesure qu un lecteur
    # polars en Int64 ECHOUE sur << 8.0 >> des le premier noeud. Or ce module
    # deduisait son format du monde d ENTREE : P1_V17 stocke des entiers en
    # texte flottant (<< 8.0 >>), donc il ressortait en flottant, alors que
    # div_wide ressortait en entier. LE MEME CODE PRODUISAIT DEUX FORMATS.
    #
    # On regarde donc les VALEURS et non le texte. Mais on ne reformate JAMAIS
    # sous plan vide : le theoreme fondateur de cet etage est << plan vide =>
    # sortie AU BIT >>, et le faire tomber pour une question de format aurait
    # coute plus que le format ne rapporte. Un monde deja ecrit ne change de
    # forme que si on lui demande AUSSI de changer de contenu -- ou par un
    # appel explicite (entiers=True).
    toutes_entieres = bool(layout.get("toutes_valeurs_entieres", False)
                           and not plan_a_des_flottants(plan))
    if entiers is None:
        entiers = bool(toutes_entieres and plan)
    if entiers and not toutes_entieres:
        _die("ecriture en ENTIERS demandee, mais le monde ou le plan porte des "
             "coordonnees non entieres. ARRET.")
    mode_flottant = bool(not entiers
                         and (layout["tous_flottants"]
                              or plan_a_des_flottants(plan)))
    if forcer_flottants is None:
        forcer_flottants = bool(mode_flottant and not layout["tous_flottants"])
    forcer_entiers = bool(entiers and layout["tous_flottants"])

    sur_place = dest is None
    dest = (csv_path.with_suffix(".cell08.tmp") if sur_place
            else pathlib.Path(dest))
    dest.parent.mkdir(parents=True, exist_ok=True)
    t3 = time.perf_counter()
    rap = rewrite(csv_path, dest, plan, term, mode_flottant,
                  forcer_flottants, forcer_entiers)
    s_rewrite = time.perf_counter() - t3

    sha_out = sha256_fichier(dest)
    vide = not plan
    identique = sha_out == sha_in
    if vide and not identique:
        try:
            dest.unlink()
        except OSError:
            pass
        _die("PLAN VIDE mais la sortie DIFFERE de l entree (sha %s != %s). "
             "L identite en octets est la propriete fondatrice de cet etage : "
             "elle vient de tomber. ARRET AVANT REMPLACEMENT."
             % (sha_out[:16], sha_in[:16]))
    if not vide and identique:
        _die("PLAN NON VIDE (%d films) mais la sortie est identique a l entree :"
             " la reecriture n a rien fait. ARRET." % len(plan))
    manquants = sorted(set(plan) - set(layout["films"]))
    if manquants:
        _die("le plan vise des films absents du CSV : %r" % manquants)
    n_drop = sum(len(p["drop_nodes"]) for p in plan.values())
    n_add = sum(len(p["add_nodes"]) for p in plan.values())
    n_move = sum(len(p["move_nodes"]) for p in plan.values())
    n_ae = sum(len(p["add_edges"]) for p in plan.values())
    if (rap["n_drop_node"], rap["n_add_node"], rap["n_move_node"],
            rap["n_add_edge"]) != (n_drop, n_add, n_move, n_ae):
        _die("invariant des gestes : applique %r pour demande %r"
             % ((rap["n_drop_node"], rap["n_add_node"], rap["n_move_node"],
                 rap["n_add_edge"]), (n_drop, n_add, n_move, n_ae)))
    attendu = layout["n_rows"] - rap["n_drop_node"] - rap["n_drop_edge"] \
        - rap["n_drop_edge_orphelin"] + rap["n_add_node"] + rap["n_add_edge"]
    if rap["n_rows_out"] != attendu:
        _die("invariant de lignes : %d en sortie pour %d attendues"
             % (rap["n_rows_out"], attendu))

    if sur_place:
        import os
        os.replace(dest, csv_path)
        chemin_sortie = str(csv_path)
    else:
        chemin_sortie = str(dest)

    rapport = {
        "etage": "cell08_referee", "date_u": date_u(),
        "sha256_in": sha_in, "sha256_out": sha_out,
        "sha_monde_attendu": sha_monde_attendu,
        "garde_d_origine": ("verifiee" if sha_monde_attendu else
                            "NON DEMANDEE -- le plan n a pas declare son monde"),
        "identique_en_octets": bool(identique), "plan_vide": bool(vide),
        "id_deja_range_en_entree": bool(layout["id_deja_range"]),
        "tous_flottants_en_entree": bool(layout["tous_flottants"]),
        "mode_flottant_en_sortie": bool(mode_flottant),
        "flottantise": bool(forcer_flottants),
        "entierise": bool(forcer_entiers),
        "toutes_valeurs_entieres_en_entree":
            bool(layout.get("toutes_valeurs_entieres", False)),
        "n_films": len(layout["films"]), "n_rows_in": layout["n_rows"],
        "n_node_in": layout["n_node"], "n_edge_in": layout["n_edge"],
        "n_films_touches": len(plan), "sortie": chemin_sortie,
        "s_sha_in": round(t_sha, 2), "s_scan": round(s_scan, 2),
        "s_detection": round(s_detection, 2), "s_rewrite": round(s_rewrite, 2),
        "s_total": round(time.perf_counter() - t0, 2), **rap,
    }
    rapport["s_par_film"] = round(rapport["s_total"]
                                  / max(1, rapport["n_films"]), 4)
    if verbose:
        print(json.dumps(rapport, indent=1, sort_keys=True))
    return rapport


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--plan", default=None,
                    help="JSON du plan par film ; absent = NO-OP")
    ap.add_argument("--dest", default=None)
    ap.add_argument("--recu", default=None)
    ap.add_argument("--sha-monde", default=None,
                    help="sha256 du monde auquel le plan appartient : l etage "
                         "REFUSE de l appliquer a un autre")
    a = ap.parse_args()
    brut = (json.loads(pathlib.Path(a.plan).read_text("utf-8"))
            if a.plan else {})
    sha = a.sha_monde
    if isinstance(brut, dict) and "plans" in brut:
        sha = sha or brut.get("source_monde_keep_sha256_natif")             or brut.get("source_monde_keep")
        brut = brut["plans"]
    rap = run_cell08(a.csv, brut, dest=a.dest, sha_monde_attendu=sha)
    if a.recu:
        p = pathlib.Path(a.recu)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rap, ensure_ascii=False, indent=1),
                     encoding="utf-8")
        print("[recu] " + str(p))


if __name__ == "__main__":
    main()
