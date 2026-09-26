"""Adaptateur du `REFEREE-SCHEMA-v0` (REF-DATA) vers l'entree du referee.

Ce module est la SEULE porte entre les donnees et le modele. Il ne redefinit
rien : il lit le schema publie (`SPRINT_48H/REFEREE/SCHEMA.md`, valide par ZEUS
le 05/09 12:09Z) et rend des tenseurs.

Ce que le schema fixe et que l'on recopie ici sans le discuter :
  - crop `(7, 19, 19, 19)` uint16 BRUT, grille 1,625 um isotrope, `dt` de -3 a +3 ;
  - normalisation PAR TRAME : `clip((x - q001) / (q999 - q001), 0, 1)` ;
  - jetons : un seul tableau `(n_tok, 22)` float32 pour LES DEUX mondes, avec un
    champ `monde` (0 = KEEP, 1 = CANDIDAT) ; sept types ; ordre canonique ;
  - `label_bio` : +1 = le candidat est la bonne histoire, -1 = KEEP l'est,
    0 = indecidable (une composante NON ANNOTEE n'entraine JAMAIS la preference).

Ce que ce module ajoute, et rien d'autre :
  - il SCINDE le tableau de jetons par `monde` (le modele lit une histoire a la fois) ;
  - il met les grandeurs a l'echelle (aucune n'est absolue) et pose un BIT DE
    VALIDITE par trait, pour qu'un `NaN` de colline ou un `-1` de proba ne se
    confonde jamais avec une mesure ;
  - il derive les positions des noeuds du centre EN VOXELS DU CROP, seul endroit
    ou le teacher gele peut aller chercher la cible d'un noeud.

Interdits verifies (SCHEMA §4.3) : aucun `film`, `embryon`, `t` absolu, position
absolue, statistique de film, sha ni compteur global n'entre dans le modele.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict

import numpy as np

VERSION_SCHEMA = "REFEREE-SCHEMA-v0"
VERSION_ADAPTATEUR = "REF_MODEL/adaptateur-v0"

# --------------------------------------------------------------------------
# Le crop 3D+t  (SCHEMA §3.1)
# --------------------------------------------------------------------------
NB_TRAMES = 7
DT_CROP = (-3, -2, -1, 0, 1, 2, 3)
IDX_CENTRE = (2, 3, 4)          # dt = -1, 0, +1 : MASQUEES
IDX_CONTEXTE = (0, 1, 5, 6)     # dt = -3, -2, +2, +3 : vues par le teacher
RAYON_VOXELS = 9
COTE_CROP = 2 * RAYON_VOXELS + 1        # 19
FORME_CROP = (NB_TRAMES, COTE_CROP, COTE_CROP, COTE_CROP)
PAS_UM = 1.625                          # grille du UNet, isotrope (SCHEMA §1)
RAYON_UM = RAYON_VOXELS * PAS_UM        # 14,625
PORTE_JUGE_UM = 7.0

CANAUX_TEACHER = 32
GRILLE_CIBLE = 3
NB_FENTES_PAR_TRAME = GRILLE_CIBLE ** 3
NB_FENTES_CIBLE = len(IDX_CENTRE) * NB_FENTES_PAR_TRAME       # 81
NB_JETONS_CONTEXTE = len(IDX_CONTEXTE) * NB_FENTES_PAR_TRAME  # 108

# --------------------------------------------------------------------------
# Les jetons  (SCHEMA §4)
# --------------------------------------------------------------------------
TYPES_JETON = ("OBSERVATION", "VIE", "ARETE", "GAP", "DIVISION", "HIDDEN", "DUPLICATE")
NB_TYPES = len(TYPES_JETON)
IDX_TYPE = {n: i for i, n in enumerate(TYPES_JETON)}

ROLES = ("garde", "retire", "ajoute", "deplace", "commune", "keep_seule", "cand_seule")
NB_ROLES = len(ROLES)

# Ordre de colonnes suppose du tableau `(n_tok, 22)`. REF-DATA publie l'ordre
# reel dans un sidecar ; `colonnes_jetons()` le lit s'il existe, et l'ordre
# ci-dessous n'est qu'un repli EXPLICITE (jamais un silence).
# ORDRE REEL, verifie contre `referee_data.COLONNES_TOKEN` de REF-DATA
# (SCHEMA v1 §4.2). `rang` et `presence` sont les deux dernieres : `rang` n'est
# PAS lu par le modele (il porterait l'ordre de generation), `presence` sert
# uniquement a jeter le remplissage.
COLONNES_JETONS_DEFAUT = (
    "type", "monde", "dt", "dz_um", "dy_um", "dx_um", "role",
    "prob", "prob_2", "marge", "support",
    "courbure_z", "courbure_y", "courbure_x",
    "degre_in", "degre_out", "longueur_um", "duree",
    "dist_ppv_um", "densite_7um", "rang", "presence",
)
LARGEUR_JETONS = 22   # SCHEMA §7 : `lot.tokens(i) -> (n_tok, 22)`

# Les traits CONTINUS lus par le modele, et leur echelle. Tout est relatif.
TRAITS = (
    "dt", "dz_um", "dy_um", "dx_um",
    "prob", "prob_2", "marge", "support",
    "courbure_z", "courbure_y", "courbure_x",
    "degre_in", "degre_out", "longueur_um", "duree",
    "dist_ppv_um", "densite_7um",
    "rayon_um",       # derive : distance au centre de la composante
    "flag_centre",    # derive : le jeton vit-il dans une trame MASQUEE
)
NB_TRAITS = len(TRAITS)
IDX_TRAIT = {n: i for i, n in enumerate(TRAITS)}
DIM_JETON = 2 * NB_TRAITS      # valeurs + bits de validite

ECHELLES = {
    "dt": 3.0, "dz_um": RAYON_UM, "dy_um": RAYON_UM, "dx_um": RAYON_UM,
    "prob": 1.0, "prob_2": 1.0, "marge": 1.0, "support": 1.0,
    "courbure_z": 1.0, "courbure_y": 1.0, "courbure_x": 1.0,
    "degre_in": 4.0, "degre_out": 4.0, "longueur_um": 10.0, "duree": 7.0,
    "dist_ppv_um": PORTE_JUGE_UM, "densite_7um": 8.0,
    "rayon_um": RAYON_UM, "flag_centre": 1.0,
}

NB_JETONS_MAX = 128            # par MONDE (le schema borne a 256 les deux reunis)
NB_NOEUDS_MAX = 24             # noeuds du centre echantillonnes chez le teacher

MOTS_INTERDITS = ("film", "embryon", "movie", "embryo", "dataset", "video", "sha",
                  "z_um_abs", "absolu", "node_id")

FAMILLES_NATURELLES = ("W1_TTA_ISO", "W2_PARAB", "W3_DUPLICATE",
                       "W4_SWAP_RELINK", "W5_GAP", "W6_DIVIDE")
TYPES_CORRUPTION = ("DROP", "DUPLICATE", "JITTER", "SWAP", "WRONG_PARENT",
                    "FALSE_DIVIDE", "MISSED_DIVIDE", "CLUMP", "PREBIRTH", "BROKEN_GAP")
FAMILLES_CORRUPTION = tuple("CORR_" + t for t in TYPES_CORRUPTION)

# Precision d'equilibre mesuree par PROOFREADER (20 films) : le seuil au-dessus
# duquel un arbitre cesse de perdre du score.
PRECISION_EQUILIBRE = {"W3_DUPLICATE": 0.573, "W4_SWAP_RELINK": 0.501}

COLONNES_DECISIONS = ("film", "comp_id", "famille", "P_KEEP", "P_REPLACE",
                      "P_ABSTAIN", "E_keep", "E_cand", "U")


def verifier_absence_de_fuite(noms) -> None:
    """Leve si un nom d'entree porte l'identite d'un film ou d'un embryon."""
    for nom in noms:
        bas = str(nom).lower()
        for interdit in MOTS_INTERDITS:
            if interdit in bas:
                raise ValueError(
                    f"entree interdite : '{nom}' contient '{interdit}' "
                    "(SCHEMA v0 §4.3 ; l'embryon ne sert QU'au split)"
                )


def colonnes_jetons(meta: dict | None = None) -> tuple:
    """L'ordre reel des colonnes de jetons, lu chez REF-DATA si publie."""
    if meta and "colonnes_jetons" in meta:
        noms = tuple(meta["colonnes_jetons"])
        verifier_absence_de_fuite(noms)
        return noms
    return COLONNES_JETONS_DEFAUT


# --------------------------------------------------------------------------
# Adaptation : (n_tok, 22) -> ce que le modele lit
# --------------------------------------------------------------------------
def adapter_jetons(bruts: np.ndarray, noms=None, monde: int = 0,
                   nb_max: int = NB_JETONS_MAX,
                   nb_noeuds: int = NB_NOEUDS_MAX) -> dict:
    """Scinde le tableau de jetons par monde et rend l'entree du referee.

    `bruts` : `(n_tok, 22)` float32, LES DEUX mondes melanges (SCHEMA §4.2).
    `monde` : 0 = KEEP, 1 = CANDIDAT.

    Rend `jetons (nb_max, 2*NB_TRAITS)`, `type_jeton`, `role_jeton`,
    `masque_jeton`, `noeuds_centre (nb_noeuds, 4)` en VOXELS DU CROP, et
    `masque_noeuds`. Les jetons sont tries par distance croissante au centre
    avant troncature : ce qui tombe est ce qui est loin.
    """
    noms = tuple(noms) if noms is not None else COLONNES_JETONS_DEFAUT
    col = {n: i for i, n in enumerate(noms)}
    if bruts.ndim != 2:
        raise ValueError(f"jetons attendus (n_tok, k), recu {bruts.shape}")
    bruts = np.asarray(bruts, dtype=np.float32)

    sel = bruts[:, col["monde"]].astype(np.int32) == int(monde)
    if "presence" in col:
        # les tokens sont remplis jusqu'a TOP_K_MAX : `presence` = 0 est du vide,
        # jamais une mesure (REF-DATA, referee_data.COLONNES_TOKEN)
        sel = sel & (bruts[:, col["presence"]] > 0.5)
    tab = bruts[sel]

    dz = tab[:, col["dz_um"]] if len(tab) else np.zeros(0, np.float32)
    dy = tab[:, col["dy_um"]] if len(tab) else np.zeros(0, np.float32)
    dx = tab[:, col["dx_um"]] if len(tab) else np.zeros(0, np.float32)
    rayon = np.sqrt(np.nan_to_num(dz) ** 2 + np.nan_to_num(dy) ** 2
                    + np.nan_to_num(dx) ** 2)
    ordre = np.argsort(rayon, kind="stable")[:nb_max]
    tab, rayon = tab[ordre], rayon[ordre]
    n = len(tab)

    jetons = np.zeros((nb_max, DIM_JETON), dtype=np.float32)
    types = np.zeros((nb_max,), dtype=np.int64)
    roles = np.zeros((nb_max,), dtype=np.int64)
    masque = np.zeros((nb_max,), dtype=bool)
    if n:
        masque[:n] = True
        types[:n] = np.clip(tab[:, col["type"]].astype(np.int64), 0, NB_TYPES - 1)
        roles[:n] = np.clip(tab[:, col["role"]].astype(np.int64), 0, NB_ROLES - 1)
        dt = tab[:, col["dt"]]
        derives = {"rayon_um": rayon, "flag_centre": (np.abs(dt) <= 1).astype(np.float32)}
        for k, nom in enumerate(TRAITS):
            brut = derives[nom] if nom in derives else tab[:, col[nom]]
            valide = np.isfinite(brut) & (brut > -0.5) if nom.startswith(("prob", "marge", "colline")) \
                else np.isfinite(brut)
            val = np.where(valide, brut, 0.0) / ECHELLES[nom]
            jetons[:n, k] = np.clip(val, -8.0, 8.0)
            jetons[:n, NB_TRAITS + k] = valide.astype(np.float32)

    # --- noeuds du centre : ce que le monde AFFIRME, en voxels du crop
    noeuds = np.zeros((nb_noeuds, 4), dtype=np.float32)
    masque_n = np.zeros((nb_noeuds,), dtype=bool)
    if n:
        est_obs = types[:n] == IDX_TYPE["OBSERVATION"]
        dt = tab[:, col["dt"]]
        au_centre = np.abs(dt) <= 1
        cand = np.where(est_obs & au_centre)[0][:nb_noeuds]
        for j, i in enumerate(cand):
            masque_n[j] = True
            noeuds[j] = (
                dt[i] + 1.0,                                     # dt -1,0,1 -> 0,1,2
                RAYON_VOXELS + np.nan_to_num(tab[i, col["dz_um"]]) / PAS_UM,
                RAYON_VOXELS + np.nan_to_num(tab[i, col["dy_um"]]) / PAS_UM,
                RAYON_VOXELS + np.nan_to_num(tab[i, col["dx_um"]]) / PAS_UM,
            )
        noeuds[:, 1:] = np.clip(noeuds[:, 1:], 0.0, COTE_CROP - 1.0)
    return {"jetons": jetons, "type_jeton": types, "role_jeton": roles,
            "masque_jeton": masque, "noeuds_centre": noeuds,
            "masque_noeuds": masque_n, "n_jetons_bruts": int(sel.sum()),
            "tronque": int(max(0, int(sel.sum()) - nb_max))}


def _noeuds_bruts(tab, col) -> list:
    """Les OBSERVATIONS des trames CENTRALES d'un monde, en voxels du crop."""
    if not len(tab):
        return []
    dt = tab[:, col["dt"]]
    est_obs = np.isin(tab[:, col["type"]].astype(int),
                      (IDX_TYPE["OBSERVATION"], IDX_TYPE["DIVISION"],
                       IDX_TYPE["DUPLICATE"]))
    garde = est_obs & (np.abs(dt) <= 1)
    sortie = []
    for i in np.where(garde)[0]:
        sortie.append((
            float(dt[i]) + 1.0,
            RAYON_VOXELS + float(np.nan_to_num(tab[i, col["dz_um"]])) / PAS_UM,
            RAYON_VOXELS + float(np.nan_to_num(tab[i, col["dy_um"]])) / PAS_UM,
            RAYON_VOXELS + float(np.nan_to_num(tab[i, col["dx_um"]])) / PAS_UM,
        ))
    return sortie


def noeuds_partages(bruts: np.ndarray, noms=None,
                    nb_noeuds: int = NB_NOEUDS_MAX,
                    tolerance_vox: float = 0.5) -> dict:
    """Les MEMES fentes de noeud pour les deux mondes, et qui les AFFIRME.

    Pourquoi c'est necessaire, et pas un detail. Une famille comme
    `DUPLICATE_PARASITE` se decide sur un noeud QUI DISPARAIT : le monde KEEP
    affirme une cellule a cet endroit, le monde candidat ne l'affirme pas. Si
    chaque monde n'etait interroge que sur SES propres noeuds, les deux energies
    seraient des moyennes sur des ensembles de fentes differents -- retirer un
    noeud bien predit ferait monter la moyenne, retirer un noeud mal predit la
    ferait baisser, et la comparaison mesurerait la taille de l'ensemble au lieu
    de la verite de l'histoire.

    Ici les deux mondes repondent sur l'UNION des noeuds, chacun avec un
    drapeau `affirme` (1 = mon histoire dit qu'il y a une cellule ici, 0 = elle
    dit qu'il n'y en a pas). Le monde qui affirme une cellule absente de l'image
    paie ; le monde qui nie une cellule presente paie aussi. C'est la question
    posee au film, et elle est la meme pour les deux.
    """
    noms = tuple(noms) if noms is not None else COLONNES_JETONS_DEFAUT
    col = {n: i for i, n in enumerate(noms)}
    bruts = np.asarray(bruts, dtype=np.float32)
    presents = (bruts[:, col["presence"]] > 0.5) if "presence" in col         else np.ones(len(bruts), dtype=bool)
    monde = bruts[:, col["monde"]].astype(np.int32)

    par_monde = {m: _noeuds_bruts(bruts[presents & (monde == m)], col)
                 for m in (0, 1)}

    union, cles = [], []
    for m in (0, 1):
        for n in par_monde[m]:
            cle = (round(n[0]), round(n[1] / tolerance_vox),
                   round(n[2] / tolerance_vox), round(n[3] / tolerance_vox))
            if cle not in cles:
                cles.append(cle)
                union.append(n)
    # les plus proches du centre d'abord : ce qui tombe a la troncature est loin
    centre = np.array([1.0, RAYON_VOXELS, RAYON_VOXELS, RAYON_VOXELS])
    if union:
        d = [float(np.linalg.norm(np.array(n)[1:] - centre[1:])) for n in union]
        ordre = np.argsort(d, kind="stable")[:nb_noeuds]
        union = [union[i] for i in ordre]
        cles = [cles[i] for i in ordre]

    noeuds = np.zeros((nb_noeuds, 4), dtype=np.float32)
    masque = np.zeros((nb_noeuds,), dtype=bool)
    affirme = np.zeros((2, nb_noeuds), dtype=np.float32)
    for j, n in enumerate(union):
        noeuds[j] = n
        masque[j] = True
    noeuds[:, 1:] = np.clip(noeuds[:, 1:], 0.0, COTE_CROP - 1.0)
    for m in (0, 1):
        propres = set()
        for n in par_monde[m]:
            propres.add((round(n[0]), round(n[1] / tolerance_vox),
                         round(n[2] / tolerance_vox), round(n[3] / tolerance_vox)))
        for j, cle in enumerate(cles):
            affirme[m, j] = 1.0 if cle in propres else 0.0
    return {"noeuds_centre": noeuds, "masque_noeuds": masque,
            "affirme": affirme, "n_union": len(union),
            "n_keep": len(par_monde[0]), "n_cand": len(par_monde[1])}


def normaliser_crop(img: np.ndarray, q001: np.ndarray, q999: np.ndarray) -> np.ndarray:
    """Normalisation PAR TRAME du SCHEMA §3.2 (jamais par film)."""
    img = np.asarray(img, dtype=np.float32)
    lo = np.asarray(q001, dtype=np.float32).reshape(-1, 1, 1, 1)
    hi = np.asarray(q999, dtype=np.float32).reshape(-1, 1, 1, 1)
    return np.clip((img - lo) / np.maximum(hi - lo, 1e-6), 0.0, 1.0)


def cible_depuis_label(label_bio) -> np.ndarray:
    """`label_bio` -> cible du modele : 0 = KEEP est vrai, 1 = le candidat l'est.

    `label_bio == 0` (non annotee) n'entraine JAMAIS la preference : le masque
    `entrainable` rendu ici est le seul droit d'entree dans la perte de rang.
    """
    lab = np.asarray(label_bio)
    cible = (lab > 0).astype(np.int64)
    return cible, (lab != 0)


# --------------------------------------------------------------------------
# Empreinte et formes
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class FormesLot:
    lot: int
    crop: tuple
    jetons: tuple
    noeuds_centre: tuple

    def json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)


def formes_attendues(lot: int) -> FormesLot:
    return FormesLot(
        lot=lot,
        crop=(lot, *FORME_CROP),
        jetons=(lot, NB_JETONS_MAX, DIM_JETON),
        noeuds_centre=(lot, NB_NOEUDS_MAX, 4),
    )


def sha_schema() -> str:
    charge = json.dumps({
        "schema": VERSION_SCHEMA, "adaptateur": VERSION_ADAPTATEUR,
        "crop": list(FORME_CROP), "pas_um": PAS_UM,
        "idx_centre": list(IDX_CENTRE), "idx_contexte": list(IDX_CONTEXTE),
        "canaux_teacher": CANAUX_TEACHER, "grille": GRILLE_CIBLE,
        "types": list(TYPES_JETON), "roles": list(ROLES),
        "traits": list(TRAITS), "echelles": ECHELLES,
        "nb_jetons_max": NB_JETONS_MAX, "nb_noeuds_max": NB_NOEUDS_MAX,
    }, sort_keys=True).encode("utf-8")
    return hashlib.sha256(charge).hexdigest()


# --------------------------------------------------------------------------
# Jeu factice AU FORMAT DU SCHEMA (avant que l'ecole n'existe)
# --------------------------------------------------------------------------
def jetons_factices(n_tok: int, rng, monde: int, decale_um: float = 0.0,
                    positions=None) -> np.ndarray:
    """Un tableau `(n_tok, 22)` conforme au SCHEMA §4.2."""
    tab = np.zeros((n_tok, LARGEUR_JETONS), dtype=np.float32)
    col = {n: i for i, n in enumerate(COLONNES_JETONS_DEFAUT)}
    tab[:, col["monde"]] = monde
    tab[:, col["type"]] = rng.integers(0, NB_TYPES, size=n_tok)
    tab[:, col["role"]] = rng.integers(0, NB_ROLES, size=n_tok)
    tab[:, col["dt"]] = rng.integers(-3, 4, size=n_tok)
    if positions is None:
        positions = rng.uniform(-RAYON_UM * 0.6, RAYON_UM * 0.6, size=(n_tok, 3))
    tab[:, col["dz_um"]] = positions[:, 0] + decale_um
    tab[:, col["dy_um"]] = positions[:, 1] + decale_um
    tab[:, col["dx_um"]] = positions[:, 2] + decale_um
    tab[:, col["prob"]] = rng.uniform(0.0, 1.0, size=n_tok)
    tab[:, col["prob_2"]] = rng.uniform(0.0, 1.0, size=n_tok)
    tab[:, col["marge"]] = tab[:, col["prob"]] - tab[:, col["prob_2"]]
    tab[:, col["support"]] = rng.uniform(0.0, 1.0, size=n_tok)
    for c in ("courbure_z", "courbure_y", "courbure_x"):
        tab[:, col[c]] = np.where(rng.random(n_tok) < 0.2, np.nan,
                                  rng.normal(0, 1, n_tok))
    tab[:, col["degre_in"]] = rng.integers(0, 3, size=n_tok)
    tab[:, col["degre_out"]] = rng.integers(0, 3, size=n_tok)
    tab[:, col["longueur_um"]] = rng.uniform(0.0, 8.0, size=n_tok)
    tab[:, col["duree"]] = rng.integers(1, 8, size=n_tok)
    tab[:, col["dist_ppv_um"]] = rng.uniform(1.0, 12.0, size=n_tok)
    tab[:, col["densite_7um"]] = rng.integers(0, 6, size=n_tok)
    tab[:, col["rang"]] = np.arange(n_tok, dtype=np.float32)
    tab[:, col["presence"]] = 1.0      # 0 = remplissage (REF-DATA)
    return tab


def composante_factice(rng, avec_signal: bool = True,
                       oriente: int | None = None) -> dict:
    """Une composante entiere au format du schema : crop brut + jetons + label.

    `avec_signal` : le monde SUR pose ses observations centrales sur des
    gaussiennes reelles de l'image, le monde corrompu les decale de 4 um. Le
    modele DOIT pouvoir separer les deux ; c'est le controle du chemin passant.

    `oriente` : 0 = KEEP porte l'histoire SURE (label_bio = -1), 1 = c'est le
    CANDIDAT qui la porte (label_bio = +1). Les deux orientations existent dans
    l'ecole (SCHEMA §5 : une paire = deux lignes qui partagent le crop), sans
    quoi le modele apprendrait « toujours KEEP » et n'aurait rien lu du film.
    """
    if oriente is None:
        oriente = int(rng.integers(0, 2))
    n_sur = int(rng.integers(8, 40))
    n_faux = int(rng.integers(8, 40))
    monde_sur, monde_faux = (0, 1) if oriente == 0 else (1, 0)
    pos_sur = rng.uniform(-RAYON_UM * 0.5, RAYON_UM * 0.5, size=(n_sur, 3))
    j_keep = jetons_factices(n_sur, rng, monde=monde_sur, positions=pos_sur)
    j_cand = jetons_factices(n_faux, rng, monde=monde_faux, decale_um=4.0)
    img = rng.normal(600.0, 40.0, size=FORME_CROP).astype(np.float32)
    if avec_signal:
        col = {n: i for i, n in enumerate(COLONNES_JETONS_DEFAUT)}
        for i in range(n_sur):
            if j_keep[i, col["type"]] != IDX_TYPE["OBSERVATION"]:
                continue
            dt = j_keep[i, col["dt"]]
            if abs(dt) > 1:
                continue
            z = RAYON_VOXELS + j_keep[i, col["dz_um"]] / PAS_UM
            y = RAYON_VOXELS + j_keep[i, col["dy_um"]] / PAS_UM
            x = RAYON_VOXELS + j_keep[i, col["dx_um"]] / PAS_UM
            _gaussienne(img[int(dt) + 3], z, y, x, amplitude=900.0)
    img = np.clip(img, 0, 65535).astype(np.uint16)
    q001 = np.full(NB_TRAMES, 560.0, dtype=np.float32)
    q999 = np.full(NB_TRAMES, 1500.0, dtype=np.float32)
    return {"jetons": np.concatenate([j_keep, j_cand], axis=0),
            "img": img, "q001": q001, "q999": q999,
            "label_bio": -1 if oriente == 0 else +1,
            "label_pay": float(rng.normal(0, 1.3e-4))}


def _gaussienne(vol: np.ndarray, z: float, y: float, x: float,
                sigma: float = 1.5, amplitude: float = 1.0) -> None:
    zz, yy, xx = np.meshgrid(np.arange(vol.shape[0]), np.arange(vol.shape[1]),
                             np.arange(vol.shape[2]), indexing="ij")
    d2 = (zz - z) ** 2 + (yy - y) ** 2 + (xx - x) ** 2
    vol += (amplitude * np.exp(-d2 / (2 * sigma ** 2))).astype(vol.dtype)


if __name__ == "__main__":
    print("schema      :", VERSION_SCHEMA, "/", VERSION_ADAPTATEUR)
    print("sha         :", sha_schema())
    print("crop        :", FORME_CROP, "pas", PAS_UM, "um")
    print("jetons      :", NB_JETONS_MAX, "x", DIM_JETON,
          f"({NB_TRAITS} traits + {NB_TRAITS} bits de validite)")
    print("cibles      :", NB_FENTES_CIBLE, "x", CANAUX_TEACHER)
    print("contexte    :", NB_JETONS_CONTEXTE, "x", CANAUX_TEACHER)
