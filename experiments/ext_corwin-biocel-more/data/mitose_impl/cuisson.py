# CUISSON du jeu mitose : recensement de la GT (divisions, continuites, negatifs durs par embryon) puis cuisson des cibles + masques + normalisation.
"""D1 commence ici. Deux modes, et le premier ne coute rien.

`--recenser` LIT LA GT SEULE (les `.geff`, qui sont des zarr) et publie, en
ENTIERS et par embryon : le nombre de divisions, de continuites, et de negatifs
durs par type. Aucune image n est ouverte, aucun GPU n est loue : c est la
mesure qui dit ce que la cuisson aura a cuire, et elle se relit en secondes.

`--cuire` produit le jeu : pour chaque evenement et chaque negatif retenu, une
fenetre normalisee PAR IMAGE et les cibles (H_m, H_f, H_mid, O, S) avec leurs
masques a trois etats, ecrites par blocs. Le volume RunPod a deja rendu des
fichiers de bonne taille au contenu faux quand il etait en quota : chaque bloc
est donc ecrit EN LOCAL puis copie, et son sha256 est RECALCULE A DESTINATION
et compare (memoire `runpod-volume-quota-silencieux`).

CE QUE LA GT DONNE, ET COMMENT ON LE LIT SANS LIBRAIRIE. Un `.geff` est un zarr
v3 : `nodes/ids` (N,), `nodes/props/{t,z,y,x}/values` (N,) int64, `edges/ids`
(E,2) uint64. Un noeud a deux successeurs EST une division ; un noeud a
exactement un successeur EST une continuite, c est-a-dire un NEGATIF CERTAIN.
On ne passe pas par `tracksdata` : la lecture directe est exacte, sans
dependance, et elle nous a permis de REMESURER les quatre chiffres du dossier
au lieu de les citer.

LES QUATRE NEGATIFS DURS (§2.4), tous obligatoires :
  1. `choc_mere`      la MEME mere, remontee de 3 a 5 images (MOTHER-SHOCK).
                      Sans lui le reseau apprend << quelle cellule >> et non
                      << quel instant >>.
  2. `fausse_fourche` les 111 fausses fourches du monde etiquetees par le juge
                      (111 FP sur 170 fourches evaluees). Le negatif le plus dur
                      qui existe. Il vient d un fichier EXTERNE : s il n est pas
                      fourni, son compte vaut 0 et le rapport le DIT -- un
                      negatif dur absent en silence serait une ecole amputee
                      sans que personne ne le sache.
  3. `voisine`        les noeuds a moins de 10 um d une vraie mere, au MEME
                      instant : meme eclairement, meme profondeur.
  4. `continuite`     les 128 581 noeuds a un seul enfant : le socle.

AVERTISSEMENT MESURE, a lire avant d esperer. Le duel apparie de MITO-TWIN sur
l embryon jamais vu rend 54,6 pct contre N1 (la meme cellule a t-4) et 54,5 pct
contre N3 (fausse fourche), pour 64,8 pct contre le temps inverse -- hasard
50 pct. Aujourd hui, la seule chose que nos reseaux savent lire est la fleche du
temps, et les negatifs 1 et 2 sont exactement ceux qui les mettent en echec.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import pathlib
import time

import numpy as np

import cibles as C
import normalisation as NORM
from grille import FORME_GRILLE, matrice_distances_um, natif_vers_grille


class ErreurCuisson(RuntimeError):
    """Refus NOMME de la cuisson."""


# ------------------------------------------------------------------ lecture GT

def lire_geff(chemin) -> dict:
    """Lit un `.geff` (zarr v3) sans librairie de suivi.

    Rend {ids, t, z, y, x, aretes (E,2), enfants, parents}. Les coordonnees sont
    en VOXELS NATIFS ENTIERS -- le repere du CSV de monde et du juge."""
    import zarr
    g = zarr.open(str(chemin), mode="r")
    ids = np.asarray(g["nodes"]["ids"]).astype(np.int64)
    props = g["nodes"]["props"]
    t = np.asarray(props["t"]["values"]).astype(np.int64)
    z = np.asarray(props["z"]["values"]).astype(np.int64)
    y = np.asarray(props["y"]["values"]).astype(np.int64)
    x = np.asarray(props["x"]["values"]).astype(np.int64)
    ar = np.asarray(g["edges"]["ids"]).astype(np.int64)
    if ar.ndim != 2 or ar.shape[1] != 2:
        raise ErreurCuisson(
            f"{chemin} : edges/ids de forme {ar.shape}, attendu (E,2)")
    enfants: dict = collections.defaultdict(list)
    parents: dict = {}
    for s, c in ar:
        enfants[int(s)].append(int(c))
        parents[int(c)] = int(s)
    pos = {int(i): (int(tt), int(zz), int(yy), int(xx))
           for i, tt, zz, yy, xx in zip(ids, t, z, y, x)}
    return {"ids": ids, "pos": pos, "aretes": ar,
            "enfants": dict(enfants), "parents": parents}


def evenements_du_film(gt: dict) -> tuple[list, list]:
    """(divisions, continuites) : listes de node_id.

    Une division est un noeud a EXACTEMENT deux enfants ; une continuite, a
    exactement un. Un noeud a trois enfants ou plus serait une anomalie de GT :
    on le COMPTE a part plutot que de le ranger dans l une des deux classes
    (mesure du dossier : outdeg >= 3 vaut 0 sur 133 318 noeuds -- si ce compte
    cesse d etre nul, c est la GT qui a change, pas notre code)."""
    div, cont, anomalies = [], [], []
    for u, e in gt["enfants"].items():
        if len(e) == 2:
            div.append(u)
        elif len(e) == 1:
            cont.append(u)
        elif len(e) >= 3:
            anomalies.append(u)
    if anomalies:
        raise ErreurCuisson(
            f"{len(anomalies)} noeuds a out-degre >= 3 : la GT a change "
            f"(mesure du dossier : 0 sur 133 318). Premiers : {anomalies[:5]}")
    return sorted(div), sorted(cont)


def remonter(gt: dict, u: int, k: int):
    """L ancetre de `u` a `k` images en arriere, ou None si la piste est coupee
    ou si l on sort du film. Les exclusions sont COMPTEES par l appelant,
    jamais remplacees en silence."""
    v = u
    for _ in range(int(k)):
        v = gt["parents"].get(v)
        if v is None:
            return None
    return v


def noeuds_du_monde(chemin_csv) -> dict:
    """{film: {t: [(z,y,x), ...]}} depuis un CSV de monde canonique.

    Sert au negatif dur n. 3 : la GT est trop EPARSE pour le fournir (MESURE
    ici : 2 lignes sur 199 films), parce que 97,13 pct des noeuds du monde sont
    a plus de 3 um de toute annotation. Les voisines viennent donc du MONDE, et
    la source est declaree dans le rapport -- ce ne sont pas des negatifs
    CERTAINS au sens de §2.1, ce sont des negatifs de LOCALISATION : le taux de
    base d une division sur une mere quelconque est de 4e-5."""
    par: dict = {}
    with open(chemin_csv, "r", encoding="utf-8") as fh:
        entete = fh.readline().rstrip("\n").split(",")
        ic = {c: i for i, c in enumerate(entete)}
        for l in fh:
            if not l.strip():
                continue
            ch = l.rstrip("\n").split(",")
            if ch[ic["row_type"]] != "node":
                continue
            par.setdefault(ch[ic["dataset"]], {}).setdefault(
                int(ch[ic["t"]]), []).append(
                    (int(ch[ic["z"]]), int(ch[ic["y"]]), int(ch[ic["x"]])))
    return par


def recenser_film(film: str, gt: dict, fourches_fp=None,
                  distances_choc=C.DISTANCES_CHOC,
                  rayon_voisine_um: float = C.RAYON_VOISINE_UM,
                  monde=None) -> dict:
    """Recense UN film : divisions, continuites, negatifs durs par type.

    Rend aussi la LISTE des lignes (film, type, node_id, t) : un compteur ne
    prouve que ce que prouve la ligne qui l incremente, et c est cette liste
    qui part dans `sorties/`."""
    div, cont = evenements_du_film(gt)
    lignes = []
    embryon = film.split("_")[0]
    ignores = set()
    exclusions = collections.Counter()

    for u in div:
        t = gt["pos"][u][0]
        lignes.append({"film": film, "embryon": embryon, "type": "division",
                       "node_id": u, "t": t,
                       "filles": sorted(gt["enfants"][u])})
        # instants IGNORES (t-1, t-2) : jamais negatifs
        for k in range(1, C.DISTANCE_IGNORE + 1):
            a = remonter(gt, u, k)
            if a is None:
                exclusions["ignore_piste_coupee"] += 1
            else:
                ignores.add(a)
        # negatif dur 1 : MOTHER-SHOCK a t-3..t-5
        for k in distances_choc:
            a = remonter(gt, u, k)
            if a is None:
                exclusions["choc_piste_coupee"] += 1
                continue
            lignes.append({"film": film, "embryon": embryon,
                           "type": "choc_mere", "node_id": a,
                           "t": gt["pos"][a][0], "mere": u, "recul": int(k)})

    # negatif dur 3 : les voisines a moins de 10 um d une vraie mere, meme t
    par_t: dict = collections.defaultdict(list)
    for nid, (t, z, y, x) in gt["pos"].items():
        par_t[t].append(nid)
    source_voisines = "monde" if monde is not None else "gt"
    for u in div:
        t = gt["pos"][u][0]
        if monde is not None:
            pts = monde.get(film, {}).get(int(t), [])
            noms = [None] * len(pts)
        else:
            voisins = [n for n in par_t[t] if n != u]
            pts = [gt["pos"][n][1:] for n in voisins]
            noms = voisins
        if not pts:
            continue
        p = np.array(pts, np.float64)
        pu = np.array([gt["pos"][u][1:]], np.float64)
        d = matrice_distances_um(natif_vers_grille(p), natif_vers_grille(pu))[:, 0]
        for n, pt, dd in zip(noms, pts, d):
            if C.RAYON_ETIQUETTE_UM < dd <= rayon_voisine_um:
                lignes.append({"film": film, "embryon": embryon,
                               "type": "voisine",
                               "node_id": (int(n) if n is not None else -1),
                               "zyx": [int(v) for v in pt],
                               "source": source_voisines,
                               "t": int(t), "mere": u, "d_um": float(dd)})

    # negatif dur 2 : les fausses fourches du monde (fichier externe)
    n_ff = 0
    if fourches_fp:
        for f in fourches_fp.get(film, []):
            n_ff += 1
            lignes.append({"film": film, "embryon": embryon,
                           "type": "fausse_fourche", "node_id": int(f[0]),
                           "t": int(f[1]) if len(f) > 1 else -1})

    # negatif dur 4 : le socle, moins les instants IGNORES
    n_ignores_retires = 0
    for u in cont:
        if u in ignores:
            n_ignores_retires += 1
            continue
        lignes.append({"film": film, "embryon": embryon, "type": "continuite",
                       "node_id": u, "t": gt["pos"][u][0]})

    return {
        "film": film, "embryon": embryon,
        "n_noeuds": len(gt["pos"]), "n_aretes": int(len(gt["aretes"])),
        "n_divisions": len(div), "n_continuites_brutes": len(cont),
        "n_continuites_retenues": len(cont) - n_ignores_retires,
        "n_ignores": len(ignores),
        "n_continuites_retirees_car_ignorees": n_ignores_retires,
        "n_fausses_fourches": n_ff,
        "source_voisines": source_voisines,
        "exclusions": dict(exclusions), "lignes": lignes,
    }


# --------------------------------------------------------------- la cuisson

def cuire_evenement(gt: dict, u: int, lire_trame, n_trames: int,
                    bras: str = "t", est_44b6: bool = False,
                    rng=None, augmenter: bool = False) -> dict:
    """Un evenement -> (fenetre normalisee, cibles, masques).

    La fenetre passe par `normalisation.fenetre_normalisee` -- LA porte
    d entree unique des images -- et les cibles par `cibles.fabriquer_cibles`.
    Aucune des deux n est reimplementee ici : c est exactement ce qui garantit
    que la cuisson, l entrainement et l etage voient le meme tenseur."""
    t = gt["pos"][u][0]
    filles = sorted(gt["enfants"][u])
    if len(filles) != 2:
        raise ErreurCuisson(f"noeud {u} : {len(filles)} enfants, 2 attendus")

    fen, jn = NORM.fenetre_normalisee(lire_trame, t, n_trames, rng=rng,
                                      augmenter=augmenter)
    m = natif_vers_grille(np.array([gt["pos"][u][1:]], np.float64))
    f = natif_vers_grille(np.array([gt["pos"][v][1:] for v in filles],
                                   np.float64))[None, :, :]

    # negatifs certains a t et t+1 : les noeuds a UN SEUL enfant du meme instant
    def _negatifs(instant):
        p, w = [], []
        for nid, (tt, z, y, x) in gt["pos"].items():
            if tt != instant or nid == u:
                continue
            if len(gt["enfants"].get(nid, ())) == 1:
                p.append((z, y, x))
                w.append(1.0)
        return (natif_vers_grille(np.array(p, np.float64)) if p
                else np.zeros((0, 3))), np.array(w, np.float64)

    neg_t, w_t = _negatifs(t)
    neg_t1, w_t1 = _negatifs(t + 1)

    # instants IGNORES : la mere a t-1, t-2 -- jamais negatifs
    ign = []
    for k in range(1, C.DISTANCE_IGNORE + 1):
        a = remonter(gt, u, k)
        if a is not None and gt["pos"][a][0] == t:
            ign.append(gt["pos"][a][1:])
    ign_g = natif_vers_grille(np.array(ign, np.float64)) if ign else None

    poids_positif = C.instants_du_bras(t, bras).get(t, 1.0)
    cib = C.fabriquer_cibles(m, f, negatifs_t_grille=neg_t,
                             negatifs_t1_grille=neg_t1,
                             ignores_t_grille=ign_g,
                             poids_negatifs_t=w_t, poids_negatifs_t1=w_t1,
                             poids_positif=poids_positif, est_44b6=est_44b6,
                             forme=FORME_GRILLE)
    return {"fenetre": fen, "cibles": cib, "journal_normalisation": jn,
            "mere": u, "t": int(t), "filles": filles,
            "n_negatifs_t": int(len(w_t)), "n_negatifs_t1": int(len(w_t1))}


def sha256_fichier(chemin) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def ecrire_bloc(local: pathlib.Path, destination: pathlib.Path,
                donnees: dict) -> dict:
    """Ecrit un bloc EN LOCAL, le copie a destination, RECALCULE le sha256 A
    DESTINATION et compare.

    Le volume RunPod en quota a deja rendu un fichier de bonne taille au
    contenu faux, et `df` mentait. Un sha calcule a la source ne prouve donc
    rien : seul celui relu a destination prouve quelque chose."""
    local.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(local, **donnees)
    sha_local = sha256_fichier(local)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.resolve() != local.resolve():
        destination.write_bytes(local.read_bytes())
    sha_dest = sha256_fichier(destination)
    if sha_local != sha_dest:
        raise ErreurCuisson(
            f"sha DIFFERENT apres copie : {local} {sha_local[:16]} -> "
            f"{destination} {sha_dest[:16]} (volume en quota ?)")
    return {"fichier": str(destination), "sha16": sha_dest[:16],
            "octets": destination.stat().st_size}


# ---------------------------------------------------------------------- main

def _films(argument, geff_dir) -> list[str]:
    if argument and pathlib.Path(argument).is_file():
        j = json.loads(pathlib.Path(argument).read_text("utf-8"))
        return sorted(j if isinstance(j, list) else j["films"])
    if argument:
        return sorted(s for s in argument.split(",") if s)
    return sorted(p.name[:-5] for p in pathlib.Path(geff_dir).glob("*.geff"))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Recense la GT mitose, puis cuit le jeu d entrainement.")
    p.add_argument("--geff-dir", required=True)
    p.add_argument("--zarr-dir", default=os.environ.get("BIOCEL_ZARR_DIR"))
    p.add_argument("--films", default=None,
                   help="JSON de films, liste separee par des virgules, ou "
                        "rien (tous les .geff du dossier)")
    p.add_argument("--fourches", default=None,
                   help="JSON {film: [[node_id, t], ...]} des fausses fourches "
                        "du juge (les 111 FP). Absent = compte 0, DECLARE.")
    p.add_argument("--monde", default=None,
                   help="CSV de monde canonique : source du negatif dur n. 3 "
                        "(voisines a moins de 10 um). Sans lui, les voisines "
                        "sont cherchees dans la GT, qui n en fournit que 2 sur "
                        "199 films (MESURE) -- et le rapport le dit.")
    p.add_argument("--bras", default="t", choices=sorted(C.BRAS_FENETRE))
    p.add_argument("--rapport", required=True)
    p.add_argument("--sorties", default=None,
                   help="dossier ou ecrire la LISTE des lignes recensees")
    p.add_argument("--cuire", action="store_true")
    p.add_argument("--sortie-dir", default=None)
    p.add_argument("--local-dir", default=None,
                   help="dossier LOCAL du pod ou le bloc est ecrit avant copie")
    p.add_argument("--evenements-par-bloc", type=int, default=32)
    p.add_argument("--essai-a-blanc", action="store_true",
                   help="cuit au plus 2 evenements par film et n ecrit rien")
    a = p.parse_args(argv)

    t0 = time.perf_counter()
    films = _films(a.films, a.geff_dir)
    fourches = None
    if a.fourches and pathlib.Path(a.fourches).is_file():
        fourches = json.loads(pathlib.Path(a.fourches).read_text("utf-8"))
    monde = noeuds_du_monde(a.monde) if a.monde else None

    par_film, toutes_lignes = {}, []
    for f in films:
        gt = lire_geff(pathlib.Path(a.geff_dir) / (f + ".geff"))
        r = recenser_film(f, gt, fourches_fp=fourches, monde=monde)
        toutes_lignes.extend(r.pop("lignes"))
        par_film[f] = r

    comptes = C.compter_negatifs_durs(
        l for l in toutes_lignes if l["type"] != "division")
    n_div = sum(v["n_divisions"] for v in par_film.values())
    par_embryon_div = collections.Counter(
        l["embryon"] for l in toutes_lignes if l["type"] == "division")

    rap = {
        "lane": "MITOSE", "objet": "recensement de la GT mitose",
        "n_films": len(films), "bras": a.bras,
        "n_divisions": n_div,
        "divisions_par_embryon": dict(par_embryon_div),
        "n_noeuds": sum(v["n_noeuds"] for v in par_film.values()),
        "n_aretes": sum(v["n_aretes"] for v in par_film.values()),
        "continuites_calculees_aretes_moins_2div":
            sum(v["n_aretes"] for v in par_film.values()) - 2 * n_div,
        "continuites_comptees_directement":
            sum(v["n_continuites_brutes"] for v in par_film.values()),
        "negatifs_durs": comptes,
        "fausses_fourches_fournies": bool(fourches),
        "source_des_voisines": "monde" if monde else "gt",
        "note_voisines": (
            "voisines cherchees dans le MONDE fourni" if monde else
            "voisines cherchees dans la GT SEULE : MESURE, elle n en fournit "
            "que 2 sur 199 films (97,13 pct des noeuds du monde sont a plus de "
            "3 um de toute annotation). Le negatif dur n. 3 exige --monde."),
        "note_fausses_fourches": (
            "fichier fourni" if fourches else
            "AUCUN fichier de fausses fourches : le negatif dur n. 2 des 111 FP "
            "est ABSENT de ce recensement, et son compte vaut 0 -- ce n est pas "
            "une mesure a zero, c est une entree manquante"),
        "exclusions": dict(collections.Counter(
            {k: sum(v["exclusions"].get(k, 0) for v in par_film.values())
             for k in set().union(*[set(v["exclusions"])
                                    for v in par_film.values()] or [set()])})),
        "par_film": par_film,
        "temoin": {
            "id": "ANNEXE_MITOSE_HEATMAP_2_1",
            "sha16": "e61e58d22013b518",
            "chemin": "01_PLAN/5_VICTOIRE/95_PLAN_TOP3_0709/"
                      "ANNEXE_MITOSE_HEATMAP.md",
            "valeur": {"n_noeuds": 133318, "n_aretes": 128883,
                       "n_divisions": 151, "n_continuites": 128581,
                       "noeuds_6bba": 113121, "noeuds_44b6": 20197,
                       "films_6bba": 128, "films_44b6": 71,
                       "outdeg_sup_3": 0, "fusions": 0},
            "harnais": "impl/cuisson.lire_geff (lecture zarr directe du .geff, "
                       "sans tracksdata)",
            "assiette": "A199, les 199 .geff de train",
            "note": "ces chiffres sont ceux du DOSSIER ; le recensement les "
                    "REMESURE. Ils ne concordent que si l assiette est A199 "
                    "entiere -- sur trois films le temoin ne s applique pas, "
                    "et le champ `temoin_applicable` le dit.",
        },
        "temoin_applicable": bool(len(films) == 199),
        "controle_interne_continuites": bool(
            sum(v["n_continuites_brutes"] for v in par_film.values())
            == sum(v["n_aretes"] for v in par_film.values()) - 2 * n_div),
        "empreinte_normalisation": NORM.empreinte_module(),
        "secondes": round(time.perf_counter() - t0, 2),
        "horodatage_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    if a.sorties:
        d = pathlib.Path(a.sorties)
        d.mkdir(parents=True, exist_ok=True)
        p_l = d / "lignes_recensement.jsonl"
        with open(p_l, "w", encoding="utf-8") as fh:
            for l in toutes_lignes:
                fh.write(json.dumps(l, ensure_ascii=False) + "\n")
        rap["fichier_lignes"] = str(p_l)
        rap["n_lignes_ecrites"] = len(toutes_lignes)

    if a.cuire or a.essai_a_blanc:
        if not a.zarr_dir:
            raise ErreurCuisson("--zarr-dir est obligatoire pour cuire")
        import zarr
        blocs, cuits = [], 0
        tampon: dict = {}
        rng = np.random.default_rng(20260907)
        for f in films:
            gt = lire_geff(pathlib.Path(a.geff_dir) / (f + ".geff"))
            div, _ = evenements_du_film(gt)
            if a.essai_a_blanc:
                div = div[:2]
            if not div:
                continue
            arr = zarr.open(str(pathlib.Path(a.zarr_dir) / (f + ".zarr")),
                            mode="r")["0"]
            n_trames = int(arr.shape[0])
            cache: dict = {}

            def lire_trame(k, _a=arr, _c=cache):
                k = int(k)
                if k not in _c:
                    _c[k] = np.asarray(_a[k])
                return _c[k]

            for u in div:
                ech = cuire_evenement(gt, u, lire_trame, n_trames,
                                      bras=a.bras,
                                      est_44b6=f.startswith("44b6"), rng=rng)
                cuits += 1
                if a.essai_a_blanc:
                    continue
                tampon[f"{f}__{u}__fenetre"] = ech["fenetre"]
                for k in ("H_m", "H_f", "H_mid", "O", "S", "masque_m",
                          "poids_m", "masque_mid", "poids_mid"):
                    tampon[f"{f}__{u}__{k}"] = ech["cibles"][k]
                if len(tampon) >= a.evenements_par_bloc * 10:
                    n = len(blocs)
                    loc = pathlib.Path(a.local_dir or a.sortie_dir) \
                        / f"bloc_{n:04d}.npz"
                    dst = pathlib.Path(a.sortie_dir) / f"bloc_{n:04d}.npz"
                    blocs.append(ecrire_bloc(loc, dst, tampon))
                    tampon = {}
                cache.clear()
        if tampon and not a.essai_a_blanc:
            n = len(blocs)
            loc = pathlib.Path(a.local_dir or a.sortie_dir) / f"bloc_{n:04d}.npz"
            dst = pathlib.Path(a.sortie_dir) / f"bloc_{n:04d}.npz"
            blocs.append(ecrire_bloc(loc, dst, tampon))
        rap["cuisson"] = {"n_evenements_cuits": cuits, "blocs": blocs,
                          "essai_a_blanc": bool(a.essai_a_blanc)}

    pathlib.Path(a.rapport).write_text(
        json.dumps(rap, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: rap[k] for k in
                      ("n_films", "n_divisions", "divisions_par_embryon",
                       "n_noeuds", "n_aretes",
                       "continuites_calculees_aretes_moins_2div",
                       "fausses_fourches_fournies", "secondes")
                      if k in rap}, ensure_ascii=False))
    if "cuisson" in rap:
        print(json.dumps(rap["cuisson"] if not rap["cuisson"]["blocs"]
                         else {"n_evenements_cuits":
                               rap["cuisson"]["n_evenements_cuits"],
                               "n_blocs": len(rap["cuisson"]["blocs"])},
                         ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
