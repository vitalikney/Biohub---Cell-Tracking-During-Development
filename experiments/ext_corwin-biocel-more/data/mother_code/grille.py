# Conventions de coordonnees de la lane MITOSE : NATIF (64,256,256) <-> GRILLE (64,128,128) <-> micrometres, aller-retour prouve.
"""Le seul endroit de la lane ou une convention de coordonnees est ecrite.

POURQUOI CE FICHIER EXISTE ALORS QU IL EN EXISTE DEJA UN.
`01_PLAN/5_VICTOIRE/30_TRAIN_0409/impl/train/grille.py` porte les memes
conventions et les a prouvees. Nous ne l importons pas : l etage de mitose doit
partir dans un dataset Kaggle en clair avec `torch/numpy/zarr` seulement, sans
remonter dans l arborescence du depot. Ce module est donc une RECOPIE ASSUMEE
des trois conventions, avec un test d aller-retour qui refuse de mentir, et un
test de CONCORDANCE (`concorde_avec`) qui compare nos constantes a celles du
module d origine quand son dossier est fourni. Deux reperes qui divergent d un
demi-voxel, c est le decalage cible/decodage que le projet a deja paye.

TROIS REPERES, UN SEUL EST PHYSIQUE.

  (1) NATIF   (64, 256, 256), pas (1,625 ; 0,40625 ; 0,40625) um. C est le
              repere du geff, du CSV de monde et du juge officiel.

  (2) GRILLE  (64, 128, 128) par MOYENNE DE BLOCS 2x2 en xy (aucun photon jete),
              pas (1,625 ; 0,8125 ; 0,8125) um. C est la grille des cartes de
              chaleur H_m, H_f, H_mid, O, S.

              Le bloc j regroupe les natifs [2j, 2j+1] ; son photocentre, en
              INDICES natifs, vaut 2j + 0,5 -- et NON 2j. D ou :

                  natif  = 2 * grille + 0,5
                  grille = (natif - 0,5) / 2

              La lecture naive `y_grille = y/2` place la cible a 0,203 um du
              photocentre en y ET en x, soit 0,287 um dans le plan : plus de la
              moitie du plancher de 0,498 um du format de soumission.
              En z, aucun regroupement : z_grille = z_natif exactement.

  (3) MICROMETRES : `natif * (1,625 ; 0,40625 ; 0,40625)`. Une fois en um,
              toutes les distances sont euclidiennes et l anisotropie 4:1 cesse
              d etre un piege. C est le repere du NMS PHYSIQUE de 4 um, des
              rayons d accrochage (3 um mere, 4 um filles) et du rejet a 20 um.

AUCUNE fonction de ce module n arrondit, n ecrete ni ne caste, sauf celles dont
le nom le dit. L arrondi n a lieu qu a un seul endroit de la lane : la pose de
la cible gaussienne (`cibles.py`), et c est ce qui rend l argmax de la carte
egal a la position arrondie -- donc le decodage coherent avec la pose.
"""

from __future__ import annotations

import numpy as np

# ------------------------------------------------------------------ constantes

VOXEL_Z_UM = 1.625
"""Pas natif en z, en micrometres (attrs `multiscales` du zarr)."""

VOXEL_XY_NATIF_UM = 0.40625
"""Pas natif en y et x, en micrometres."""

FACTEUR_XY = 2
"""Moyenne de blocs 2x2 en xy : (256,256) -> (128,128). Aucun photon jete."""

VOXEL_XY_GRILLE_UM = VOXEL_XY_NATIF_UM * FACTEUR_XY          # 0.8125
PAS_GRILLE_UM = (VOXEL_Z_UM, VOXEL_XY_GRILLE_UM, VOXEL_XY_GRILLE_UM)

FORME_NATIVE = (64, 256, 256)
FORME_GRILLE = (64, FORME_NATIVE[1] // FACTEUR_XY, FORME_NATIVE[2] // FACTEUR_XY)

FACTEURS_VALIDES = (1, 2, 4)


class ErreurGrille(ValueError):
    """Violation d invariant de conversion de coordonnees."""


def _verifier_facteur(f: int) -> int:
    f = int(f)
    if f not in FACTEURS_VALIDES:
        raise ErreurGrille(
            f"facteur_xy doit etre dans {FACTEURS_VALIDES}, recu {f}")
    return f


def forme_grille(facteur_xy: int = FACTEUR_XY) -> tuple[int, int, int]:
    """(Z,Y,X) de la grille pour un facteur de moyenne de blocs donne."""
    f = _verifier_facteur(facteur_xy)
    return (FORME_NATIVE[0], FORME_NATIVE[1] // f, FORME_NATIVE[2] // f)


def pas_grille_um(facteur_xy: int = FACTEUR_XY) -> tuple[float, float, float]:
    """(dz, dy, dx) en um : ce qu un voxel de grille mesure.

    Sert a TOUTES les distances physiques : sigma de cible, rayon de NMS,
    rayons d accrochage, rejet a 20 um."""
    f = _verifier_facteur(facteur_xy)
    return (VOXEL_Z_UM, VOXEL_XY_NATIF_UM * f, VOXEL_XY_NATIF_UM * f)


def _decalage(facteur_xy: int) -> np.ndarray:
    f = _verifier_facteur(facteur_xy)
    return np.array([0.0, (f - 1) / 2.0, (f - 1) / 2.0], dtype=np.float64)


def _facteurs(facteur_xy: int) -> np.ndarray:
    f = _verifier_facteur(facteur_xy)
    return np.array([1.0, float(f), float(f)], dtype=np.float64)


def _en_n3(a, nom: str) -> np.ndarray:
    x = np.asarray(a, dtype=np.float64)
    if x.ndim == 1:
        x = x[None, :]
    if x.ndim != 2 or x.shape[1] != 3:
        raise ErreurGrille(
            f"{nom} : attendu (N,3) en (z,y,x), recu {np.asarray(a).shape}")
    return x


# ------------------------------------------------- natif <-> grille (moyenne)

def natif_vers_grille(zyx_natif, facteur_xy: int = FACTEUR_XY) -> np.ndarray:
    """(N,3) voxels NATIFS -> (N,3) voxels de GRILLE, flottants.

    Ne filtre rien : une coordonnee hors volume ressort hors volume. Le filtrage
    appartient a l appelant."""
    a = _en_n3(zyx_natif, "natif_vers_grille")
    return (a - _decalage(facteur_xy)) / _facteurs(facteur_xy)


def grille_vers_natif(zyx_grille, facteur_xy: int = FACTEUR_XY) -> np.ndarray:
    """(N,3) voxels de GRILLE -> (N,3) voxels NATIFS, flottants.

    C est cette fonction que le decodeur applique a l indice du pic : aucun cast
    entier ici, le CSV arrondit, pas nous."""
    a = _en_n3(zyx_grille, "grille_vers_natif")
    return a * _facteurs(facteur_xy) + _decalage(facteur_xy)


# ------------------------------------------------------------- distances, um

def natif_vers_um(zyx_natif) -> np.ndarray:
    """(N,3) voxels natifs -> (N,3) micrometres. Repere du juge officiel."""
    a = _en_n3(zyx_natif, "natif_vers_um")
    return a * np.array([VOXEL_Z_UM, VOXEL_XY_NATIF_UM, VOXEL_XY_NATIF_UM])


def um_vers_natif(zyx_um) -> np.ndarray:
    """Inverse exact de `natif_vers_um`."""
    a = _en_n3(zyx_um, "um_vers_natif")
    return a / np.array([VOXEL_Z_UM, VOXEL_XY_NATIF_UM, VOXEL_XY_NATIF_UM])


def grille_vers_um(zyx_grille, facteur_xy: int = FACTEUR_XY) -> np.ndarray:
    """(N,3) voxels de grille -> (N,3) micrometres ABSOLUS.

    DEFINIE PAR COMPOSITION des deux conversions deja prouvees, jamais par
    `p * pas` : cette derniere oublie le demi de centre de bloc (0,287 um dans
    le plan a F=2). Elle ne mordrait pas sur un NMS (qui ne lit que des
    differences) mais un repere faux qui ne mord pas encore est un repere
    faux -- le bogue a deja ete trouve une fois dans ce projet, le 2026-09-04."""
    return natif_vers_um(grille_vers_natif(zyx_grille, facteur_xy))


def um_vers_grille(zyx_um, facteur_xy: int = FACTEUR_XY) -> np.ndarray:
    """Inverse exact de `grille_vers_um`."""
    return natif_vers_grille(um_vers_natif(zyx_um), facteur_xy)


def distances_um(a_grille, b_grille, facteur_xy: int = FACTEUR_XY) -> np.ndarray:
    """Distances 3D en um entre deux jeux de points de GRILLE, appariees terme a
    terme. (N,3) et (N,3) -> (N,)."""
    a = _en_n3(a_grille, "distances_um[a]")
    b = _en_n3(b_grille, "distances_um[b]")
    if a.shape != b.shape:
        raise ErreurGrille(f"formes incompatibles : {a.shape} vs {b.shape}")
    pas = np.asarray(pas_grille_um(facteur_xy), dtype=np.float64)
    return np.sqrt((((a - b) * pas) ** 2).sum(axis=-1))


def matrice_distances_um(a_grille, b_grille,
                         facteur_xy: int = FACTEUR_XY) -> np.ndarray:
    """(N,3) x (M,3) -> (N,M) distances en um. Sert a l accrochage et au NMS.

    Ecrite ici et nulle part ailleurs : une seconde formule de distance dans la
    lane serait une seconde verite."""
    a = _en_n3(a_grille, "matrice_distances_um[a]")
    b = _en_n3(b_grille, "matrice_distances_um[b]")
    pas = np.asarray(pas_grille_um(facteur_xy), dtype=np.float64)
    d = (a[:, None, :] - b[None, :, :]) * pas.reshape(1, 1, 3)
    return np.sqrt((d ** 2).sum(axis=2))


def dans_le_volume(zyx_grille, forme=None) -> np.ndarray:
    """Masque (N,) : `round(p)` tombe-t-il dans [0, S-1] par axe ?

    Critere `-0,5 <= p < S - 0,5`, c est-a-dire exactement la condition pour que
    la cible gaussienne soit posable au voxel arrondi. Ecrit une seule fois pour
    que la cuisson, les augmentations et le decodeur utilisent LE MEME critere."""
    a = _en_n3(zyx_grille, "dans_le_volume")
    s = np.asarray(forme if forme is not None else FORME_GRILLE, dtype=np.float64)
    if s.shape != (3,):
        raise ErreurGrille(f"forme attendue (Z,Y,X), recue {s.shape}")
    return np.all((a >= -0.5) & (a < s - 0.5), axis=1)


# ------------------------------------------------------- binning et controles

def binner_xy(volume: np.ndarray, facteur_xy: int = FACTEUR_XY) -> np.ndarray:
    """(Z,Y,X) natif -> (Z, Y/f, X/f) par MOYENNE de blocs f x f en xy.

    Moyenne et non pas : aucun photon n est jete, et c est la seule difference
    qui compte entre notre grille et celle du liage gele (qui, lui, decime)."""
    f = _verifier_facteur(facteur_xy)
    v = np.asarray(volume)
    if v.ndim != 3:
        raise ErreurGrille(f"binner_xy attend (Z,Y,X), recu {v.shape}")
    z, y, x = v.shape
    if y % f or x % f:
        raise ErreurGrille(
            f"binner_xy : (Y,X)=({y},{x}) non divisible par facteur_xy={f}")
    return v.reshape(z, y // f, f, x // f, f).mean(axis=(2, 4))


def verifier_aller_retour(facteur_xy: int = FACTEUR_XY,
                          graine: int = 20260907) -> dict:
    """Prouve que les compositions sont l identite, dans les DEUX sens.

    Rend un constat (dict) ; ne leve pas. Cette fonction est le temoin du module :
    tant qu elle passe, aucun decalage cible/decodage ne peut naitre ici."""
    rng = np.random.default_rng(graine)
    p_natif = rng.uniform(0.0, 63.0, size=(512, 3))
    p_natif[:, 1:] = rng.uniform(0.0, 255.0, size=(512, 2))

    g = natif_vers_grille(p_natif, facteur_xy)
    retour_natif = grille_vers_natif(g, facteur_xy)
    e_ng = float(np.abs(retour_natif - p_natif).max())

    um = natif_vers_um(p_natif)
    e_num = float(np.abs(um_vers_natif(um) - p_natif).max())

    um_g = grille_vers_um(g, facteur_xy)
    e_gum = float(np.abs(um_vers_grille(um_g, facteur_xy) - g).max())

    # Une difference de 1 voxel de grille en xy DOIT valoir exactement le pas.
    a = np.array([[10.0, 20.0, 30.0]])
    b = np.array([[10.0, 21.0, 30.0]])
    d_un_voxel_xy = float(distances_um(a, b, facteur_xy)[0])
    c = np.array([[11.0, 20.0, 30.0]])
    d_un_voxel_z = float(distances_um(a, c, facteur_xy)[0])

    pas = pas_grille_um(facteur_xy)
    return {
        "facteur_xy": int(facteur_xy),
        "forme_grille": list(forme_grille(facteur_xy)),
        "pas_grille_um": list(pas),
        "erreur_max_natif_grille_natif": e_ng,
        "erreur_max_natif_um_natif": e_num,
        "erreur_max_grille_um_grille": e_gum,
        "distance_un_voxel_xy_um": d_un_voxel_xy,
        "distance_un_voxel_z_um": d_un_voxel_z,
        "ok": bool(e_ng < 1e-9 and e_num < 1e-9 and e_gum < 1e-9
                   and abs(d_un_voxel_xy - pas[1]) < 1e-12
                   and abs(d_un_voxel_z - pas[0]) < 1e-12),
    }


def concorde_avec(src_grille: str) -> dict:
    """Compare NOS constantes a celles d un autre module `grille.py` (chemin
    donne en ARGUMENT, jamais en dur) et rend le constat.

    Sert a prouver que la recopie n a pas derive de l original du PLOT 4D. Si le
    fichier est absent, le constat le dit -- il ne leve pas : la concordance est
    une verification, pas une dependance."""
    import importlib.util
    import pathlib

    p = pathlib.Path(src_grille)
    if p.is_dir():
        p = p / "grille.py"
    if not p.is_file():
        return {"fichier": str(p), "present": False, "concorde": None,
                "motif": "fichier absent"}
    spec = importlib.util.spec_from_file_location("_autre_grille", str(p))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    champs = ("VOXEL_Z_UM", "VOXEL_XY_NATIF_UM", "FACTEUR_XY",
              "VOXEL_XY_GRILLE_UM", "FORME_NATIVE", "FORME_GRILLE")
    ecarts = {}
    for c in champs:
        nous = globals().get(c)
        eux = getattr(mod, c, None)
        if isinstance(nous, tuple):
            different = (eux is None) or (tuple(nous) != tuple(eux))
        else:
            different = (nous != eux)
        if different:
            ecarts[c] = {"nous": nous, "eux": eux}
    # Meme geometrie sur des points tires : la preuve qui compte.
    rng = np.random.default_rng(1)
    p_natif = rng.uniform(0.0, 60.0, size=(256, 3))
    e = float(np.abs(natif_vers_grille(p_natif)
                     - mod.natif_vers_grille(p_natif)).max())
    e2 = float(np.abs(grille_vers_um(natif_vers_grille(p_natif))
                      - mod.grille_vers_um(mod.natif_vers_grille(p_natif))).max())
    return {"fichier": str(p), "present": True, "ecarts_constantes": ecarts,
            "erreur_max_natif_vers_grille": e, "erreur_max_grille_vers_um": e2,
            "concorde": bool(not ecarts and e < 1e-12 and e2 < 1e-12)}


__all__ = [
    "VOXEL_Z_UM", "VOXEL_XY_NATIF_UM", "FACTEUR_XY", "VOXEL_XY_GRILLE_UM",
    "PAS_GRILLE_UM", "FORME_NATIVE", "FORME_GRILLE", "ErreurGrille",
    "forme_grille", "pas_grille_um", "natif_vers_grille", "grille_vers_natif",
    "natif_vers_um", "um_vers_natif", "grille_vers_um", "um_vers_grille",
    "distances_um", "matrice_distances_um", "dans_le_volume", "binner_xy",
    "verifier_aller_retour", "concorde_avec",
]
