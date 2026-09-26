# Cibles de la tete MITOSE : H_m, H_f, H_mid, O (6 canaux), S, et les MASQUES A TROIS ETATS (positif / negatif certain / IGNORE).
"""Ce que le reseau doit apprendre, et surtout ce qu on lui interdit d apprendre.

LE FAIT QUI CHANGE TOUT (ANNEXE §2.1, D-551). La GT d entrainement porte
133 318 annotations, 128 883 aretes toutes a Delta t = 1, et 151 divisions.
Un noeud GT qui a EXACTEMENT UN enfant GT est un non-diviseur CERTAIN, et il y
en a 128 883 - 2 x 151 = 128 581. Nous ne sommes donc pas dans un probleme PU :
nous avons 151 positifs certains contre 128 581 negatifs certains, et
l incertitude ne porte que sur les 96 pct de volume non annote -- qui reste
IGNORE. 97,13 pct des noeuds de notre monde sont a plus de 3 um de toute
annotation : les declarer negatifs reviendrait a apprendre au reseau nos
propres erreurs.

D OU LE MASQUE A TROIS ETATS, qui est la piece centrale de ce fichier :

    +1  POSITIF CERTAIN   la mere d une division GT, a l instant t
     0  NEGATIF CERTAIN   un noeud GT a exactement un enfant, au meme instant
    -1  IGNORE            tout le reste : le volume non annote, ET les instants
                          t-1 et t-2 de la mere (§2.3), qui ne sont PAS des
                          negatifs -- nous ne savons pas quand la condensation
                          chromatinienne devient visible, aucun recu du projet
                          ne le mesure, et l intervalle physique entre deux
                          images n apparait nulle part dans nos pieces.

L ARBITRAGE QUE CE FICHIER TRANCHE, ET LE DIT. §2.3 ignore t-1 et t-2 ; §2.4
demande comme negatif dur << la meme mere 2 a 5 images avant >>. Les deux se
recouvrent en t-2. On prend la lecture SANS recouvrement : la fenetre ignoree
gagne toujours (`DISTANCE_IGNORE = 2`, jamais negative), et le MOTHER-SHOCK est
tire dans `DISTANCES_CHOC = (3, 4, 5)`. Cette lecture garde intact le negatif
N1 du duel apparie deja MESURE, qui est << la meme cellule a t-4 >>
(`REPRISE_MITO_TWIN.md` §4). Le parametre est expose : ZEUS peut le renverser
sans toucher au code.

LES CARTES (ANNEXE §2.2), grille 64 x 128 x 128, pas (1,625 ; 0,8125 ; 0,8125) um.

  H_m    1 canal, a t      gaussienne sigma = 1,625 um (sigma_z 1 voxel,
                           sigma_xy 2 voxels) sur la position ARRONDIE de la
                           mere, combinaison par MAX.
  H_f    1 canal, a t+1    deux gaussiennes, aux deux filles.
  H_mid  1 canal, a t+1    une gaussienne au barycentre des deux filles --
                           l objet qu UN SEUL pic peut porter, et celui dont le
                           decodeur a besoin pour proposer une PAIRE.
  O      6 canaux, a t     (d1 - rint(u)) et (d2 - rint(u)) en VOXELS DE
                           GRILLE, ecrits dans le masque positif seulement.
                           L ancre est la position ARRONDIE (voir le commentaire
                           dans `fabriquer_cibles`) : c est ce qui rend le
                           decodage exact au lieu de le laisser trainer un demi
                           voxel d erreur que rien ne rattrape.
  S      1 canal, a t      ||d1 - d2|| en MICROMETRES ; garde de decodage.

POURQUOI LA POSITION EST ARRONDIE. La gaussienne est centree sur le voxel
arrondi, donc sa valeur y vaut exactement 1,0 et l argmax de la carte EST ce
voxel. C est ce qui rend le decodage (pic) coherent avec la pose : le decalage
cible/decodage d un demi-voxel est l accident que ce projet a deja paye une
fois (`grille.py`, 2026-09-04).

CE QUE CE FICHIER NE FAIT PAS. Il ne lit aucun fichier, ne connait aucun chemin,
n ouvre aucun zarr : il recoit des coordonnees et rend des tableaux. C est ce
qui le rend testable sans donnees, et identique sur le PC, sur le pod et dans le
noyau Kaggle.
"""

from __future__ import annotations

import numpy as np

from grille import (FACTEUR_XY, FORME_GRILLE, dans_le_volume, grille_vers_um,
                    matrice_distances_um, pas_grille_um)

# --------------------------------------------------------------- constantes

SIGMA_UM = 1.625
"""Sigma ISOTROPE en micrometres : 1 voxel en z, 2 voxels en xy sur la grille
128. L exprimer en um et non en voxels est ce qui rend deux grilles comparables."""

SEUIL_POSITIF = 0.05
"""Au-dessus de cette valeur de gaussienne, le voxel est declare POSITIF dans le
masque. A sigma = 1,625 um, cela couvre un rayon de ~2,45 sigma."""

RAYON_ETIQUETTE_UM = 3.0
"""Rayon autour d un noeud GT dans lequel l etiquette de ce noeud vaut. 3 um est
le rayon d appariement du juge officiel et le rayon d accrochage de la mere : la
region etiquetee et la region decodee sont ainsi le meme objet."""

DISTANCE_IGNORE = 2
"""Nombre d images AVANT l evenement qui sont IGNOREES (t-1, t-2), jamais
negatives. §2.3."""

DISTANCES_CHOC = (3, 4, 5)
"""MOTHER-SHOCK : la meme mere, remontee de 3 a 5 images. Voir l arbitrage du
docstring de module. Le duel apparie deja mesure utilise t-4, qui est dedans."""

RAYON_VOISINE_UM = 10.0
"""Negatif dur n. 3 : les voisines a moins de 10 um d une vraie mere, au MEME
instant -- meme eclairement, meme profondeur. Force la localisation plutot que
la detection d une << zone brillante >>."""

POIDS_NEGATIF_DUR = 3.0
"""Poids d un negatif dur dans la perte. Les negatifs 1 et 2 sont exactement
ceux qui mettent nos reseaux en echec (duel apparie : 54,6 pct contre la meme
cellule a t-4, 54,5 pct contre une fausse fourche, hasard = 50 pct)."""

POIDS_BRAS_ABLATION = 0.5
"""Poids d un positif pose sur un instant du bras d ablation (t-1, t-2)."""

FACTEUR_44B6 = 3.11
"""Desequilibre de couverture MESURE : 6bba 5,37 pct, 44b6 0,77 pct."""

TYPES_NEGATIFS_DURS = ("choc_mere", "fausse_fourche", "voisine", "continuite")
"""Les quatre negatifs de §2.4, dans l ordre du texte. `continuite` est le socle
(les 128 581) ; les trois autres sont les durs proprement dits."""

BRAS_FENETRE = {
    "t": (0,),
    "t-1,t": (-1, 0),
    "t-2,t-1,t": (-2, -1, 0),
}
"""Les trois bras d ablation de §2.3. `{t}` est le bras primaire ; les autres
etiquettent aussi les instants anterieurs, a poids 0,5."""

ETAT_POSITIF = np.int8(1)
ETAT_NEGATIF = np.int8(0)
ETAT_IGNORE = np.int8(-1)


class ErreurCible(ValueError):
    """Violation d invariant de construction des cibles."""


# ------------------------------------------------------------------ helpers

def sigmas_voxels(facteur_xy: int = FACTEUR_XY) -> tuple[float, float, float]:
    """(sigma_z, sigma_y, sigma_x) en VOXELS de grille pour SIGMA_UM."""
    pas = pas_grille_um(facteur_xy)
    return (SIGMA_UM / pas[0], SIGMA_UM / pas[1], SIGMA_UM / pas[2])


def _en_n3(a, nom: str) -> np.ndarray:
    if a is None:
        return np.zeros((0, 3), np.float64)
    x = np.asarray(a, dtype=np.float64)
    if x.size == 0:
        return np.zeros((0, 3), np.float64)
    if x.ndim == 1:
        x = x[None, :]
    if x.ndim != 2 or x.shape[1] != 3:
        raise ErreurCible(f"{nom} : attendu (N,3) en (z,y,x), recu "
                          f"{np.asarray(a).shape}")
    return x


def _offsets_ellipsoide(rayon_um: float,
                        facteur_xy: int = FACTEUR_XY) -> np.ndarray:
    """Decalages entiers (K,3) dont la distance PHYSIQUE au centre est
    <= rayon_um. L anisotropie 4:1 est portee par le pas, pas par une fenetre
    rectangulaire choisie a la main."""
    pas = np.asarray(pas_grille_um(facteur_xy), np.float64)
    demi = np.maximum(1, np.ceil(rayon_um / pas)).astype(int)
    gz, gy, gx = np.meshgrid(*[np.arange(-d, d + 1) for d in demi],
                             indexing="ij")
    off = np.stack([gz.ravel(), gy.ravel(), gx.ravel()], axis=1)
    d = np.sqrt(((off * pas) ** 2).sum(axis=1))
    return off[d <= rayon_um + 1e-9]


def _blobs(coords_grille, forme, sigmas) -> tuple[np.ndarray, np.ndarray]:
    """Carte gaussienne combinee par MAX et PROPRIETAIRE de chaque voxel.

    Le proprietaire est indispensable : c est lui qui dit quels offsets O et
    quelle separation S ecrire dans un voxel positif quand deux meres se
    touchent. Depart d egalite DETERMINISTE : a valeur egale, le plus petit
    indice gagne (on parcourt dans l ordre et on n ecrase qu a valeur
    strictement superieure)."""
    z, y, x = (int(v) for v in forme)
    carte = np.zeros((z, y, x), np.float32)
    proprio = np.full((z, y, x), -1, np.int32)
    c = _en_n3(coords_grille, "_blobs")
    if c.shape[0] == 0:
        return carte, proprio
    s = np.asarray(sigmas, np.float64).reshape(1, 3)
    demi = np.maximum(1, np.ceil(3.0 * s.reshape(3))).astype(int)
    gz, gy, gx = np.meshgrid(*[np.arange(-d, d + 1) for d in demi],
                             indexing="ij")
    off = np.stack([gz.ravel(), gy.ravel(), gx.ravel()], axis=1)
    val_off = np.exp(-0.5 * (((off / s) ** 2).sum(axis=1))).astype(np.float32)
    r = np.rint(c).astype(np.int64)
    for i in range(r.shape[0]):
        pos = r[i][None, :] + off
        ok = np.all((pos >= 0) & (pos < np.array([z, y, x])), axis=1)
        p = pos[ok]
        v = val_off[ok]
        anc = carte[p[:, 0], p[:, 1], p[:, 2]]
        gagne = v > anc
        idx = p[gagne]
        carte[idx[:, 0], idx[:, 1], idx[:, 2]] = v[gagne]
        proprio[idx[:, 0], idx[:, 1], idx[:, 2]] = np.int32(i)
    return carte, proprio


def _marquer_disques(masque, coords_grille, valeur, off,
                     poids=None, tableau_poids=None, poids_par_point=None):
    """Marque `valeur` dans `masque` sur les disques physiques autour de chaque
    point ; ecrit aussi les poids si `tableau_poids` est fourni.

    Ecrase sans condition : l ordre d appel porte la priorite (IGNORE, puis
    NEGATIF, puis POSITIF), et cet ordre est ecrit une seule fois, dans
    `fabriquer_cibles`. `coords_grille` a None est un cas NORMAL (pas de
    negatif fourni) et ne fait rien -- il ne leve pas."""
    if coords_grille is None:
        return
    c = _en_n3(coords_grille, "_marquer_disques")
    if c.shape[0] == 0:
        return
    z, y, x = masque.shape
    r = np.rint(c).astype(np.int64)
    for i in range(r.shape[0]):
        pos = r[i][None, :] + off
        ok = np.all((pos >= 0) & (pos < np.array([z, y, x])), axis=1)
        p = pos[ok]
        masque[p[:, 0], p[:, 1], p[:, 2]] = valeur
        if tableau_poids is not None:
            w = poids if poids_par_point is None else float(poids_par_point[i])
            tableau_poids[p[:, 0], p[:, 1], p[:, 2]] = np.float32(w)


# --------------------------------------------------------- fabrique de cibles

def fabriquer_cibles(meres_grille, filles_grille,
                     negatifs_t_grille=None, negatifs_t1_grille=None,
                     ignores_t_grille=None, ignores_t1_grille=None,
                     poids_negatifs_t=None, poids_negatifs_t1=None,
                     poids_positif: float = 1.0,
                     est_44b6: bool = False,
                     forme=FORME_GRILLE,
                     facteur_xy: int = FACTEUR_XY) -> dict:
    """Fabrique H_m, H_f, H_mid, O, S et les masques a trois etats.

    Toutes les coordonnees sont en VOXELS DE GRILLE (utiliser
    `grille.natif_vers_grille` en amont : la conversion vit a un seul endroit).

    `meres_grille`   (N,3) mere a t ; `filles_grille` (N,2,3) filles a t+1.
    `negatifs_*`     noeuds GT a un seul enfant, au meme instant : NEGATIFS
                     CERTAINS. `poids_negatifs_*` (N,) porte le poids par noeud
                     (POIDS_NEGATIF_DUR pour les durs).
    `ignores_*`      points a mettre explicitement a IGNORE (la mere a t-1/t-2
                     quand le bras ne les etiquette pas : jamais negatifs).
    `poids_positif`  1,0 pour l instant t ; POIDS_BRAS_ABLATION pour un instant
                     du bras d ablation.

    ORDRE DE PRIORITE DES ETATS, ecrit ici et nulle part ailleurs :
        fond IGNORE  ->  disques NEGATIFS  ->  points IGNORES explicites
                     ->  blobs POSITIFS
    Le positif gagne toujours ; l ignore explicite bat le negatif (une mere a
    t-1 est un noeud GT a un seul enfant, donc un << negatif certain >> au sens
    litteral : c est exactement l erreur que §2.3 interdit)."""
    z, y, x = (int(v) for v in forme)
    sig = sigmas_voxels(facteur_xy)
    m = _en_n3(meres_grille, "meres_grille")
    n = m.shape[0]
    f = np.asarray(filles_grille, np.float64) if n else np.zeros((0, 2, 3))
    if n and (f.ndim != 3 or f.shape[0] != n or f.shape[1:] != (2, 3)):
        raise ErreurCible(f"filles_grille : attendu ({n},2,3), recu {f.shape}")

    dedans = dans_le_volume(m, (z, y, x)) if n else np.zeros(0, bool)
    if n and not dedans.all():
        m = m[dedans]
        f = f[dedans]
        n = m.shape[0]

    # ---- cartes de chaleur
    H_m, proprio_m = _blobs(m, (z, y, x), sig)
    mid = f.mean(axis=1) if n else np.zeros((0, 3))
    H_mid, proprio_mid = _blobs(mid, (z, y, x), sig)
    filles_plates = f.reshape(-1, 3) if n else np.zeros((0, 3))
    H_f, _ = _blobs(filles_plates, (z, y, x), sig)

    # ---- offsets O (6 canaux, voxels de grille) et separation S (1, um)
    O = np.zeros((6, z, y, x), np.float32)
    S = np.zeros((1, z, y, x), np.float32)
    if n:
        pos = (H_m >= SEUIL_POSITIF) & (proprio_m >= 0)
        idx = proprio_m[pos]
        # ANCRE = la position ARRONDIE de la mere, pas sa position exacte.
        # C est le seul choix qui rend le decodage EXACT : le decodeur lit O au
        # voxel du pic, qui EST `rint(u)` ; poser `d1 - u` lui ferait rendre
        # `d1 + (rint(u) - u)`, soit jusqu a 0,5 voxel de grille d erreur
        # structurelle (0,41 um en xy, 0,81 um en z) qu aucun apprentissage ne
        # peut retirer. ECART ASSUME avec la lettre de l ANNEXE §2.2 (<< d1 - u
        # >>), declare au rapport : la difference est bornee par un demi-voxel
        # et elle est le prix de la coherence pose/decodage.
        ancre = np.rint(m)
        d1 = (f[:, 0, :] - ancre).astype(np.float32)      # (N,3) voxels grille
        d2 = (f[:, 1, :] - ancre).astype(np.float32)
        sep = np.sqrt(((grille_vers_um(f[:, 0, :], facteur_xy)
                        - grille_vers_um(f[:, 1, :], facteur_xy)) ** 2
                       ).sum(axis=1)).astype(np.float32)   # (N,) um
        zz, yy, xx = np.nonzero(pos)
        for k in range(3):
            O[k, zz, yy, xx] = d1[idx, k]
            O[3 + k, zz, yy, xx] = d2[idx, k]
        S[0, zz, yy, xx] = sep[idx]

    # ---- masques a trois etats
    off_etq = _offsets_ellipsoide(RAYON_ETIQUETTE_UM, facteur_xy)

    masque_m = np.full((z, y, x), ETAT_IGNORE, np.int8)
    poids_m = np.zeros((z, y, x), np.float32)
    _marquer_disques(masque_m, negatifs_t_grille, ETAT_NEGATIF, off_etq,
                     poids=1.0, tableau_poids=poids_m,
                     poids_par_point=poids_negatifs_t)
    _marquer_disques(masque_m, ignores_t_grille, ETAT_IGNORE, off_etq,
                     poids=0.0, tableau_poids=poids_m)
    pos_m = H_m >= SEUIL_POSITIF
    masque_m[pos_m] = ETAT_POSITIF
    poids_m[pos_m] = np.float32(poids_positif)

    masque_mid = np.full((z, y, x), ETAT_IGNORE, np.int8)
    poids_mid = np.zeros((z, y, x), np.float32)
    _marquer_disques(masque_mid, negatifs_t1_grille, ETAT_NEGATIF, off_etq,
                     poids=1.0, tableau_poids=poids_mid,
                     poids_par_point=poids_negatifs_t1)
    _marquer_disques(masque_mid, ignores_t1_grille, ETAT_IGNORE, off_etq,
                     poids=0.0, tableau_poids=poids_mid)
    pos_mid = H_mid >= SEUIL_POSITIF
    masque_mid[pos_mid] = ETAT_POSITIF
    poids_mid[pos_mid] = np.float32(poids_positif)

    if est_44b6:
        poids_m *= np.float32(FACTEUR_44B6)
        poids_mid *= np.float32(FACTEUR_44B6)

    inv = _verifier_invariants_masque(masque_m, poids_m, H_m)
    inv_mid = _verifier_invariants_masque(masque_mid, poids_mid, H_mid)

    return {
        "H_m": H_m, "H_f": H_f, "H_mid": H_mid, "O": O, "S": S,
        "masque_m": masque_m, "poids_m": poids_m,
        "masque_mid": masque_mid, "poids_mid": poids_mid,
        "proprio_m": proprio_m, "proprio_mid": proprio_mid,
        "meta": {
            "n_meres": int(n),
            "n_meres_hors_volume": int(len(dedans) - int(dedans.sum()))
            if len(dedans) else 0,
            "forme": [z, y, x], "facteur_xy": int(facteur_xy),
            "sigma_um": SIGMA_UM, "sigmas_voxels": list(sig),
            "poids_positif": float(poids_positif),
            "est_44b6": bool(est_44b6),
            "voxels_positifs_m": int(pos_m.sum()),
            "voxels_negatifs_m": int((masque_m == ETAT_NEGATIF).sum()),
            "voxels_ignores_m": int((masque_m == ETAT_IGNORE).sum()),
            "voxels_positifs_mid": int(pos_mid.sum()),
            "voxels_negatifs_mid": int((masque_mid == ETAT_NEGATIF).sum()),
            "voxels_ignores_mid": int((masque_mid == ETAT_IGNORE).sum()),
            "invariants_m": inv, "invariants_mid": inv_mid,
        },
    }


def _verifier_invariants_masque(masque, poids, carte) -> dict:
    """Trois invariants, verifies a la fabrication et non en aval :
    (a) tout voxel IGNORE a un poids EXACTEMENT nul -- sinon << ignore >> est un
        mot et non un etat ;
    (b) aucun voxel n est a la fois positif et de poids nul ;
    (c) le maximum de la carte vaut 1,0 des qu il y a un positif (la gaussienne
        est centree sur le voxel arrondi)."""
    ign = masque == ETAT_IGNORE
    pos = masque == ETAT_POSITIF
    return {
        "ignore_a_poids_nul": bool(np.all(poids[ign] == 0.0)),
        "positif_a_poids_non_nul": bool(np.all(poids[pos] > 0.0))
        if pos.any() else True,
        "max_carte": float(carte.max()) if carte.size else 0.0,
        "max_carte_vaut_un": bool(abs(float(carte.max()) - 1.0) < 1e-6)
        if pos.any() else True,
        "etats_presents": sorted(int(v) for v in np.unique(masque)),
    }


# ------------------------------------------------------ negatifs durs, comptes

def instants_ignores(t: int, distance: int = DISTANCE_IGNORE) -> list[int]:
    """Les instants JAMAIS negatifs autour d une division : t-1 .. t-distance."""
    return [int(t - k) for k in range(1, int(distance) + 1)]


def instants_du_bras(t: int, bras: str = "t") -> dict[int, float]:
    """{instant: poids positif} pour un bras d ablation de §2.3.

    `{t}` -> {t: 1,0} ; `{t-1,t}` -> {t: 1,0 ; t-1: 0,5} ; etc. Les instants
    anterieurs NON etiquetes par le bras restent IGNORES, jamais negatifs."""
    if bras not in BRAS_FENETRE:
        raise ErreurCible(
            f"bras inconnu : {bras!r} ; attendus {sorted(BRAS_FENETRE)}")
    return {int(t + d): (1.0 if d == 0 else POIDS_BRAS_ABLATION)
            for d in BRAS_FENETRE[bras]}


def voisines_dures(mere_grille, noeuds_grille,
                   rayon_um: float = RAYON_VOISINE_UM,
                   facteur_xy: int = FACTEUR_XY) -> np.ndarray:
    """Indices des noeuds a moins de `rayon_um` d une vraie mere, au MEME
    instant : le negatif dur n. 3. Le noeud le plus proche de la mere (la mere
    elle-meme si elle est dans la liste) est exclu par le rayon minimal."""
    m = _en_n3(mere_grille, "voisines_dures[mere]")
    p = _en_n3(noeuds_grille, "voisines_dures[noeuds]")
    if m.shape[0] == 0 or p.shape[0] == 0:
        return np.zeros(0, np.int64)
    d = matrice_distances_um(p, m, facteur_xy).min(axis=1)
    return np.nonzero((d <= rayon_um) & (d > RAYON_ETIQUETTE_UM))[0]


def compter_negatifs_durs(lignes) -> dict:
    """Compte les negatifs durs PAR EMBRYON ET PAR TYPE, en entiers.

    `lignes` : iterable de dicts portant au moins `embryon` et `type`. Le compte
    est celui des LIGNES REELLEMENT PRESENTES : << un compteur ne prouve que ce
    que prouve la ligne qui l incremente >>. Aucun compte n est derive d une
    formule ici, et la liste elle-meme part dans `sorties/`."""
    par: dict = {}
    total: dict = {}
    inconnus: dict = {}
    n = 0
    for ligne in lignes:
        n += 1
        e = str(ligne.get("embryon", "?"))
        ty = str(ligne.get("type", "?"))
        if ty not in TYPES_NEGATIFS_DURS:
            inconnus[ty] = inconnus.get(ty, 0) + 1
        par.setdefault(e, {}).setdefault(ty, 0)
        par[e][ty] += 1
        total[ty] = total.get(ty, 0) + 1
    return {"n_lignes": n, "par_embryon": par, "total_par_type": total,
            "types_inconnus": inconnus,
            "types_attendus": list(TYPES_NEGATIFS_DURS),
            "tous_types_presents": bool(
                all(t in total for t in TYPES_NEGATIFS_DURS))}


# ------------------------------------------------- augmentations geometriques

def augmenter_geometrie(fenetre, coords: dict, rng,
                        forme=None) -> tuple[np.ndarray, dict, dict]:
    """Retournements y/x et rotations de 90 deg en xy, appliques EXACTEMENT au
    volume et aux coordonnees.

    JAMAIS l axe z (Delta z est asymetrique : -1 47,7 pct, 0 43,3 pct,
    +1 9,0 pct -- un retournement en z fabrique une geometrie qui n existe pas).
    JAMAIS l axe du temps (l ordre EST le signal ; le duel N2 mesure 64,8 pct
    contre le temps inverse : l inverser fabrique un negatif, pas une
    augmentation). Ces deux axes ne sont meme pas offerts par la signature.

    L echelle [0,90 ; 1,10] de §2.5 n est PAS ici : elle exige un
    reechantillonnage, elle vit dans la boucle d entrainement (torch), et la
    melanger a des transformations exactes rendrait ce test-ci inexact.

    `fenetre` (W,Z,Y,X) ; `coords` {nom: (N,3) ou (N,2,3)} en voxels de grille.
    Rend (fenetre transformee, coords transformees, journal)."""
    a = np.asarray(fenetre)
    if a.ndim != 4:
        raise ErreurCible(f"augmenter_geometrie attend (W,Z,Y,X), recu {a.shape}")
    _, _, y, x = a.shape
    if forme is None:
        forme = (a.shape[1], y, x)

    flip_y = bool(rng.random() < 0.5)
    flip_x = bool(rng.random() < 0.5)
    k = int(rng.integers(0, 4))

    def _t_coords(c):
        c = np.asarray(c, np.float64).copy()
        forme_orig = c.shape
        c = c.reshape(-1, 3)
        if c.shape[0]:
            if flip_y:
                c[:, 1] = (y - 1) - c[:, 1]
            if flip_x:
                c[:, 2] = (x - 1) - c[:, 2]
            for _ in range(k):
                # np.rot90(axes=(-2,-1)) : (yy, xx) -> (X-1-xx, yy)
                yy, xx = c[:, 1].copy(), c[:, 2].copy()
                c[:, 1] = (x - 1) - xx
                c[:, 2] = yy
        return c.reshape(forme_orig)

    if flip_y:
        a = np.flip(a, axis=-2)
    if flip_x:
        a = np.flip(a, axis=-1)
    if k:
        a = np.rot90(a, k, axes=(-2, -1))
    a = np.ascontiguousarray(a)

    sortie = {nom: _t_coords(c) for nom, c in coords.items()}
    return a, sortie, {"flip_y": flip_y, "flip_x": flip_x, "rot90": k,
                       "axes_interdits": ["z", "t"]}


# ------------------------------------------------------ temoins a deux sens

def verifier_cibles(graine: int = 20260907) -> dict:
    """Verite FABRIQUEE : deux meres a des positions connues, deux filles
    chacune. On relit dans les cartes ce qu on y a mis -- et on verifie AUSSI
    ce qui ne doit PAS y etre (aucun voxel positif et negatif a la fois, aucun
    voxel ignore de poids non nul, aucun offset ecrit hors du masque positif)."""
    from grille import natif_vers_grille

    rng = np.random.default_rng(graine)
    u1 = np.array([20.0, 100.0, 120.0])            # natif
    d11 = np.array([21.0, 108.0, 126.0])
    d12 = np.array([19.0, 92.0, 114.0])
    u2 = np.array([40.0, 200.0, 60.0])
    d21 = np.array([41.0, 206.0, 66.0])
    d22 = np.array([39.0, 194.0, 54.0])
    meres = natif_vers_grille(np.stack([u1, u2]))
    filles = np.stack([natif_vers_grille(np.stack([d11, d12])),
                       natif_vers_grille(np.stack([d21, d22]))])

    negatifs = natif_vers_grille(
        np.stack([u1 + np.array([0.0, 40.0, 0.0]),
                  u1 + np.array([6.0, 0.0, 0.0]),
                  u2 + np.array([0.0, 0.0, 50.0])]))
    ignores = natif_vers_grille(u1 + np.array([0.0, 12.0, 0.0]))[None, 0]
    poids_neg = np.array([1.0, POIDS_NEGATIF_DUR, 1.0])

    c = fabriquer_cibles(meres, filles, negatifs_t_grille=negatifs,
                         negatifs_t1_grille=negatifs,
                         ignores_t_grille=ignores,
                         poids_negatifs_t=poids_neg, poids_positif=1.0)

    r = np.rint(meres).astype(int)
    lus = []
    for i in range(2):
        zz, yy, xx = r[i]
        lus.append({
            "H_m_au_pic": float(c["H_m"][zz, yy, xx]),
            "proprio": int(c["proprio_m"][zz, yy, xx]),
            "O_lu": [float(v) for v in c["O"][:, zz, yy, xx]],
            "O_attendu": [float(v) for v in
                          np.concatenate([filles[i, 0] - np.rint(meres[i]),
                                          filles[i, 1] - np.rint(meres[i])])],
            "S_lu": float(c["S"][0, zz, yy, xx]),
            "S_attendu": float(np.sqrt(
                ((grille_vers_um(filles[i, 0]) - grille_vers_um(filles[i, 1]))
                 ** 2).sum())),
        })
    e_o = max(max(abs(a - b) for a, b in zip(l["O_lu"], l["O_attendu"]))
              for l in lus)
    e_s = max(abs(l["S_lu"] - l["S_attendu"]) for l in lus)

    # H_mid : le pic doit tomber sur le barycentre arrondi des filles.
    mid_attendu = np.rint(filles.mean(axis=1)).astype(int)
    mid_ok = all(abs(float(c["H_mid"][tuple(mid_attendu[i])]) - 1.0) < 1e-6
                 for i in range(2))

    m = c["masque_m"]
    hors_positif = (m != ETAT_POSITIF)
    o_hors = float(np.abs(c["O"][:, hors_positif]).max())
    ign_poids = float(np.abs(c["poids_m"][m == ETAT_IGNORE]).max()) \
        if (m == ETAT_IGNORE).any() else 0.0
    # Le point explicitement IGNORE ne doit PAS etre negatif.
    ri = np.rint(ignores).astype(int)[0]
    etat_ignore_lu = int(m[tuple(ri)])
    # Le negatif dur doit porter le poids 3,0.
    rn = np.rint(negatifs[1]).astype(int)
    poids_dur_lu = float(c["poids_m"][tuple(rn)])

    # Augmentation geometrique : la distance mere-fille est INVARIANTE.
    fen = rng.uniform(0, 1, size=(4, 8, 16, 16)).astype(np.float32)
    _, co, _ = augmenter_geometrie(fen, {"meres": meres, "filles": filles},
                                   rng, forme=(64, 128, 128))
    # (les coordonnees sont sur 128 : on refait la transformation a la bonne
    #  taille pour mesurer l invariance)
    fen2 = rng.uniform(0, 1, size=(4, 64, 128, 128)).astype(np.float32)
    _, co2, jg = augmenter_geometrie(fen2, {"meres": meres, "filles": filles},
                                     rng)
    d_avant = np.sqrt(((grille_vers_um(meres) - grille_vers_um(filles[:, 0]))
                       ** 2).sum(axis=1))
    d_apres = np.sqrt(((grille_vers_um(co2["meres"])
                        - grille_vers_um(co2["filles"][:, 0])) ** 2).sum(axis=1))
    e_aug = float(np.abs(d_avant - d_apres).max())

    return {
        "pics": lus,
        "erreur_max_O": e_o, "erreur_max_S": e_s,
        "H_mid_au_barycentre": bool(mid_ok),
        "O_hors_masque_positif_max": o_hors,
        "poids_max_sur_ignore": ign_poids,
        "etat_du_point_ignore": etat_ignore_lu,
        "poids_lu_du_negatif_dur": poids_dur_lu,
        "erreur_max_distance_apres_augmentation_um": e_aug,
        "augmentation": jg,
        "comptes": c["meta"],
        "ok": bool(e_o < 1e-5 and e_s < 1e-3 and mid_ok and o_hors == 0.0
                   and ign_poids == 0.0 and etat_ignore_lu == int(ETAT_IGNORE)
                   and abs(poids_dur_lu - POIDS_NEGATIF_DUR) < 1e-6
                   and e_aug < 1e-9
                   and all(abs(l["H_m_au_pic"] - 1.0) < 1e-6 for l in lus)
                   and len(co) == 2),
    }


def verifier_trois_etats(graine: int = 11) -> dict:
    """Le masque a-t-il VRAIMENT trois etats, et l ignore bat-il le negatif ?

    Chemin PASSANT : les trois etats sont presents dans un cas realiste.
    Chemin REFUSANT : sans aucun negatif fourni, il n y a AUCUN 0 dans le masque
    -- le fond est ignore, pas negatif. Un masque a deux etats passerait le
    premier test et echouerait celui-ci."""
    from grille import natif_vers_grille
    u = natif_vers_grille(np.array([[30.0, 128.0, 128.0]]))
    f = natif_vers_grille(np.array([[31.0, 136.0, 134.0],
                                    [29.0, 120.0, 122.0]]))[None, :, :]
    neg = natif_vers_grille(np.array([[30.0, 190.0, 128.0]]))

    avec = fabriquer_cibles(u, f, negatifs_t_grille=neg)
    sans = fabriquer_cibles(u, f)
    etats_avec = sorted(int(v) for v in np.unique(avec["masque_m"]))
    etats_sans = sorted(int(v) for v in np.unique(sans["masque_m"]))

    # L ignore explicite ecrase-t-il un negatif pose au meme endroit ?
    ecrase = fabriquer_cibles(u, f, negatifs_t_grille=neg,
                              ignores_t_grille=neg)
    r = np.rint(neg).astype(int)[0]
    etat_ecrase = int(ecrase["masque_m"][tuple(r)])

    return {
        "etats_avec_negatifs": etats_avec,
        "etats_sans_negatifs": etats_sans,
        "etat_apres_ecrasement_par_ignore": etat_ecrase,
        "part_ignoree_sans_negatifs": float(
            (sans["masque_m"] == ETAT_IGNORE).mean()),
        "ok": bool(etats_avec == [-1, 0, 1] and etats_sans == [-1, 1]
                   and etat_ecrase == int(ETAT_IGNORE)),
    }


__all__ = [
    "SIGMA_UM", "SEUIL_POSITIF", "RAYON_ETIQUETTE_UM", "DISTANCE_IGNORE",
    "DISTANCES_CHOC", "RAYON_VOISINE_UM", "POIDS_NEGATIF_DUR",
    "POIDS_BRAS_ABLATION", "FACTEUR_44B6", "TYPES_NEGATIFS_DURS",
    "BRAS_FENETRE", "ETAT_POSITIF", "ETAT_NEGATIF", "ETAT_IGNORE",
    "ErreurCible", "sigmas_voxels", "fabriquer_cibles", "instants_ignores",
    "instants_du_bras", "voisines_dures", "compter_negatifs_durs",
    "augmenter_geometrie", "verifier_cibles", "verifier_trois_etats",
]
