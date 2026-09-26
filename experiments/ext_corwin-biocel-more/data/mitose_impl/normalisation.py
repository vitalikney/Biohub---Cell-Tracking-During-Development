# Normalisation PAR IMAGE (p99 de l image (film,t)) et augmentation << lampe >> : UN SEUL module, importe par la cuisson, l entrainement et l etage.
"""Le module qui interdit d avoir deux reseaux sans le savoir.

LE PIEGE, NOMME AVANT D ETRE EVITE. Si la cuisson normalise d une facon,
l entrainement d une autre et l etage d une troisieme, nous n avons pas un
reseau mais trois, et rien ne le dira : les cartes seront plausibles, les
chiffres seront propres, et le monde ne bougera pas. La parade n est pas une
convention ecrite dans un rapport, c est un FICHIER : `fenetre_normalisee` est
la seule porte d entree des images dans toute la lane, et son empreinte
(`empreinte_module()`) est publiee dans chaque recu. Deux recus qui portent la
meme empreinte ont normalise pareil, au bit.

CE QUE << PAR IMAGE >> VEUT DIRE, ET POURQUOI.
On divise chaque trame par le p99 de CETTE trame, pas par le p99 du film. Le
mot de Guillaume que cette regle traduit : « soit la luminosite change pour
toutes les cellules -- microscope, densite de fluorescence -- soit elle change
pour UNE cellule, et la c est une mitose ». Normaliser par le film laisse passer
la derive globale dans le temps ; normaliser par l image la retire, et ce qui
reste est le changement d une cellule RELATIF a ses voisines au meme instant.
Gain MESURE de ce seul changement sur la voie crops (AUC-PR croisee
0,3683 -> 0,4019 ; second positif de C60 du rang 6 990 au rang 261, x27,
`mito_cnn/recus/R_LOEO_V2.json`) -- mais mesure AVEC le bogue des canaux
(10 vues sur 12) : sa valeur entiere est inconnue, et ce module ne la connait pas.

L ORDRE DES GESTES, QUI N EST PAS COMMUTATIF.
    lecture natif -> binning xy 2x2 -> AUGMENTATIONS PHOTOMETRIQUES -> p99 par image
La normalisation vient EN DERNIER (ANNEXE §2.5). Si elle venait avant, chaque
augmentation de gain serait immediatement annulee par la division et
l augmentation ne servirait a rien ; en la mettant apres, on apprend au reseau
que la lampe n existe pas -- ce qui est le but.

L AUGMENTATION << LAMPE >>, ET LE CHIFFRE QU ELLE REPRODUIT.
`R_TEST_LAMPE_199.json` (19 900 images, 73 s) mesure la derive intra-film du
p99 : rapport median x1,49, max x6,79, 80,4 pct des films derivent de plus de
20 pct, 17,1 pct de plus de 100 pct, et les huit pires courbes sont des RAMPES
LISSES ET MONOTONES -- c est l eclairement qui change, pas les cellules. Sans
cette augmentation, le reseau apprendra << tard = brillant >>, ce qui est un
routeur de temps deguise. La fonction de quantile `RAPPORT_LAMPE_QUANTILES`
reproduit les QUATRE chiffres mesures par construction, et
`verifier_lampe()` les remesure sur des tirages pour le prouver.

CE QUE CE MODULE NE FAIT PAS. Il ne retourne jamais en z (Delta z est
asymetrique : -1 47,7 pct, 0 43,3 pct, +1 9,0 pct) et ne permute jamais le
temps (l ordre EST le signal ; le duel N2 mesure 64,8 pct contre le temps
inverse, c est le signal le plus fort que nos reseaux savent lire -- l inverser
fabrique un negatif, pas une augmentation). Ces deux interdits vivent dans
`cibles.augmenter_geometrie`, qui n offre pas l axe z ni l axe t.
"""

from __future__ import annotations

import hashlib
import pathlib

import numpy as np

from grille import FACTEUR_XY, binner_xy

# --------------------------------------------------------------- constantes

SOUS_ECHANTILLON_P99 = 2
"""Un voxel sur deux par axe pour le p99. Le sous-echantillonnage fait partie de
la DEFINITION : train et inference doivent le partager, sinon les deux p99
different de quelques pour mille et les deux reseaux avec."""

QUANTILE = 99.0
DECALAGES_DEFAUT = (-2, -1, 0, 1)
"""Fenetre d entree de l option B : t-2, t-1, t, t+1. `t+1` est indispensable
(les filles y vivent) ; `t-1` et `t-2` sont l objet de l ablation §2.3."""

# Fonction de quantile de la derive de lampe, calee sur les QUATRE chiffres
# mesures de `R_TEST_LAMPE_199.json`. Chaque couple est (probabilite, rapport) :
#   P(r > 1,20) = 0,804  ->  q(0,196) = 1,20
#   mediane                ->  q(0,500) = 1,49
#   P(r > 2,00) = 0,171  ->  q(0,829) = 2,00
#   maximum                ->  q(1,000) = 6,79
RAPPORT_LAMPE_QUANTILES = ((0.000, 1.00), (0.196, 1.20), (0.500, 1.49),
                           (0.829, 2.00), (1.000, 6.79))
LAMPE_MEDIANE_MESUREE = 1.49
LAMPE_MAX_MESURE = 6.79
LAMPE_PART_SUP_20PCT = 0.804
LAMPE_PART_SUP_100PCT = 0.171


class ErreurNormalisation(ValueError):
    """Violation d invariant de normalisation ou d augmentation."""


# ------------------------------------------------------- normalisation p99

def p99_image(volume) -> float:
    """p99 d UNE image (film, t), sur un voxel sur deux par axe.

    Rend 1,0 si le p99 n est pas fini ou n est pas > 0 : une trame noire ne doit
    pas fabriquer des infinis, et le repli est DECLARE par `p99_par_defaut` dans
    le rapport de l appelant."""
    a = np.asarray(volume, dtype=np.float32)
    if a.ndim != 3:
        raise ErreurNormalisation(f"p99_image attend (Z,Y,X), recu {a.shape}")
    s = SOUS_ECHANTILLON_P99
    p = float(np.percentile(a[::s, ::s, ::s], QUANTILE))
    return p if (np.isfinite(p) and p > 0.0) else 1.0


def normaliser_par_image(volume) -> tuple[np.ndarray, float]:
    """(Z,Y,X) -> (volume / p99 de CETTE image, p99 utilise), float32.

    C est LA fonction. Toute image qui entre dans un reseau de cette lane passe
    par elle, a la cuisson comme au deploiement."""
    a = np.asarray(volume, dtype=np.float32)
    p = p99_image(a)
    return (a / np.float32(p)).astype(np.float32), p


# ----------------------------------------------------- augmentation << lampe >>

def tirer_rapport_lampe(rng) -> float:
    """Tire un rapport de derive `r` (p99 fin / p99 debut de fenetre).

    Interpolation LINEAIRE EN LOG entre les quantiles mesures : le tirage
    reproduit la mediane, le maximum et les deux parts au-dessus de 20 pct et
    100 pct sans qu aucun de ces quatre chiffres n ait ete choisi ici."""
    u = float(rng.random())
    qs = RAPPORT_LAMPE_QUANTILES
    for (u0, r0), (u1, r1) in zip(qs[:-1], qs[1:]):
        if u <= u1 or (u1, r1) == qs[-1]:
            if u1 == u0:
                return float(r1)
            f = (u - u0) / (u1 - u0)
            return float(np.exp(np.log(r0) + f * (np.log(r1) - np.log(r0))))
    return float(qs[-1][1])


def profil_lampe(n_trames: int, rng, rapport: float = None) -> np.ndarray:
    """Gains multiplicatifs par trame, RAMPE LISSE ET MONOTONE de 1 a r.

    Monotone parce que les huit pires courbes mesurees le sont. Le sens est tire
    a pile ou face : une lampe qui faiblit est aussi vraie qu une lampe qui
    monte, et n autoriser que la montee apprendrait au reseau que le temps va
    dans le sens de la lumiere."""
    if n_trames < 1:
        raise ErreurNormalisation(f"n_trames doit etre >= 1, recu {n_trames}")
    r = tirer_rapport_lampe(rng) if rapport is None else float(rapport)
    if r <= 0:
        raise ErreurNormalisation(f"rapport de lampe doit etre > 0, recu {r}")
    if n_trames == 1:
        return np.ones(1, np.float32)
    g = np.exp(np.linspace(0.0, np.log(r), n_trames)).astype(np.float32)
    if rng.random() < 0.5:
        g = g[::-1].copy()
    return g


def augmenter_photometrie(fenetre: np.ndarray, rng,
                          lampe: bool = True) -> tuple[np.ndarray, dict]:
    """Augmentations photometriques de l ANNEXE §2.5, appliquees a la fenetre
    ENTIERE (W,Z,Y,X) AVANT la normalisation.

    - gain global log-uniforme [0,6 ; 1,6] ;
    - profil lisse en z (cloche, rampe ou plateau, amplitude 0,4-1,0) ;
    - derive du fond (+0 a +40 pct) et des pics (0 a -14 pct) A TRAVERS la
      fenetre -- c est la derive mesuree du dossier, pas une invention ;
    - halo additif basse frequence ;
    - bruit poissonien ;
    - << lampe >> : rampe monotone de rapport tire sur les quantiles mesures ;
    - ecretage a >= 0.

    Rend (fenetre augmentee float32, journal des tirages). Le journal est rendu
    pour qu un lot reproche puisse etre rejoue a l identique : une augmentation
    qu on ne sait pas rejouer n est pas mesurable."""
    a = np.asarray(fenetre, dtype=np.float32)
    if a.ndim != 4:
        raise ErreurNormalisation(
            f"augmenter_photometrie attend (W,Z,Y,X), recu {a.shape}")
    w, z, y, x = a.shape
    j: dict = {}

    gain = float(np.exp(rng.uniform(np.log(0.6), np.log(1.6))))
    a = a * np.float32(gain)
    j["gain"] = gain

    # Profil en z : l eclairement en profondeur n est pas plat, et il ne derive
    # pas de la meme facon d un film a l autre.
    forme_z = int(rng.integers(0, 3))
    amp = float(rng.uniform(0.4, 1.0))
    u = np.linspace(0.0, 1.0, z, dtype=np.float32)
    if forme_z == 0:                                   # cloche
        p = 1.0 - amp * (2.0 * u - 1.0) ** 2
    elif forme_z == 1:                                 # rampe
        p = 1.0 - amp * u
    else:                                              # plateau + chute
        p = np.where(u < 0.7, 1.0, 1.0 - amp * (u - 0.7) / 0.3)
    if rng.random() < 0.5:
        p = p[::-1].copy()
    a = a * p.astype(np.float32).reshape(1, z, 1, 1)
    j["profil_z"] = {"forme": int(forme_z), "amplitude": amp}

    # Derive du fond et des pics A TRAVERS la fenetre (mesuree : fond +0 a
    # +40 pct, pics 0 a -14 pct).
    d_fond = float(rng.uniform(0.0, 0.40))
    d_pic = float(rng.uniform(-0.14, 0.0))
    tw = np.linspace(0.0, 1.0, w, dtype=np.float32).reshape(w, 1, 1, 1)
    fond = np.float32(np.percentile(a, 20.0))
    a = (a - fond) * (1.0 + np.float32(d_pic) * tw) \
        + fond * (1.0 + np.float32(d_fond) * tw)
    j["derive_fond"] = d_fond
    j["derive_pic"] = d_pic

    # Halo additif basse frequence : un gradient plan, le defaut d illumination
    # le plus banal d un microscope.
    if rng.random() < 0.5:
        h = float(rng.uniform(0.0, 0.15)) * float(np.percentile(a, 99.0))
        gy = np.linspace(-1.0, 1.0, y, dtype=np.float32).reshape(1, 1, y, 1)
        gx = np.linspace(-1.0, 1.0, x, dtype=np.float32).reshape(1, 1, 1, x)
        ang = float(rng.uniform(0.0, 2.0 * np.pi))
        a = a + np.float32(h) * (np.cos(ang) * gy + np.sin(ang) * gx)
        j["halo"] = {"amplitude": h, "angle": ang}

    if lampe:
        g = profil_lampe(w, rng)
        a = a * g.reshape(w, 1, 1, 1)
        j["lampe"] = {"gains": [float(v) for v in g],
                      "rapport": float(g[-1] / g[0])}

    # Bruit poissonien : sur des intensites deja mises a l echelle, on tire le
    # bruit a l echelle du signal (lambda = a / k, puis * k) plutot que sur des
    # comptes bruts qu on n a plus.
    if rng.random() < 0.7:
        k = float(rng.uniform(0.5, 4.0))
        a = np.asarray(rng.poisson(np.clip(a, 0.0, None) / k), np.float32) * k
        j["poisson_k"] = k

    a = np.clip(a, 0.0, None).astype(np.float32)
    return a, j


# ------------------------------------------------ LA porte d entree des images

def trame_normalisee(lire_trame, f: int,
                     facteur_xy: int = FACTEUR_XY) -> tuple[np.ndarray, float]:
    """UNE trame : lecture -> binning xy -> p99 de CETTE image.

    Extraite pour pouvoir etre MEMOISEE au deploiement : sans augmentation, la
    normalisation d une trame ne depend d aucune autre trame, donc la calculer
    une fois par film au lieu d une fois par instant est IDENTIQUE AU BIT --
    et c est un facteur 4 sur le poste le plus cher de l etage (MESURE au smoke
    du 07/09 : 15,4 s de normalisation contre 1,6 s de reseau sur un film de
    99 instants, 4090)."""
    v = np.asarray(lire_trame(int(f)))
    if v.ndim != 3:
        raise ErreurNormalisation(
            f"lire_trame({f}) doit rendre (Z,Y,X), recu {v.shape}")
    return normaliser_par_image(binner_xy(v.astype(np.float32), facteur_xy))


def fenetre_normalisee(lire_trame, t: int, n_trames: int,
                       decalages=DECALAGES_DEFAUT,
                       facteur_xy: int = FACTEUR_XY,
                       rng=None, augmenter: bool = False,
                       lampe: bool = True,
                       cache_grille: dict = None) -> tuple[np.ndarray, dict]:
    """(W,Z,Y,X) normalisee PAR IMAGE, la seule fabrique d entree de la lane.

    `lire_trame(f) -> (Z,Y,X)` : une fermeture fournie par l appelant (zarr,
    tableau en memoire, faux zarr d un test). AUCUN chemin n entre ici : ce
    module ne sait pas ce qu est un fichier, ce qui le rend testable sans
    donnees et identique sur le pod, sur le PC et dans le noyau Kaggle.

    Les trames hors [0, n_trames-1] sont ECRETEES sur le bord (et le rapport le
    dit) : au premier instant d un film, t-2 n existe pas, et fabriquer une
    trame noire apprendrait au reseau que le debut du film est sombre.

    Rend (fenetre, journal). Le journal porte les p99 par trame, les trames
    reellement lues et les tirages d augmentation."""
    if n_trames < 1:
        raise ErreurNormalisation(f"n_trames doit etre >= 1, recu {n_trames}")
    dec = tuple(int(d) for d in decalages)
    trames = [int(min(max(t + d, 0), n_trames - 1)) for d in dec]
    ecretees = [int(t + d) for d in dec if not (0 <= t + d < n_trames)]

    j: dict = {"t": int(t), "decalages": list(dec), "trames_lues": trames,
               "trames_ecretees": ecretees, "facteur_xy": int(facteur_xy),
               "augmente": bool(augmenter),
               "memoise": bool(cache_grille is not None and not augmenter)}

    if cache_grille is not None and not augmenter:
        # CHEMIN MEMOISE, reserve a l inference (pas d augmentation) : chaque
        # trame est binnee et normalisee UNE fois. Aucune valeur ne change --
        # `verifier_memoisation()` le prouve au bit.
        pile, p99 = [], []
        for f in trames:
            if f not in cache_grille:
                cache_grille[f] = trame_normalisee(lire_trame, f, facteur_xy)
            v, pp = cache_grille[f]
            pile.append(v)
            p99.append(pp)
        a = np.stack(pile, axis=0)
        j["p99_par_trame"] = p99
        j["empreinte_sortie"] = empreinte(a)
        return a, j

    brut = []
    for f in trames:
        v = np.asarray(lire_trame(f))
        if v.ndim != 3:
            raise ErreurNormalisation(
                f"lire_trame({f}) doit rendre (Z,Y,X), recu {v.shape}")
        brut.append(binner_xy(v.astype(np.float32), facteur_xy))
    a = np.stack(brut, axis=0)

    if augmenter:
        if rng is None:
            raise ErreurNormalisation(
                "augmenter=True exige un rng : une augmentation non rejouable "
                "n est pas mesurable")
        a, j["photometrie"] = augmenter_photometrie(a, rng, lampe=lampe)

    # LA normalisation, EN DERNIER, trame par trame.
    p99 = []
    for i in range(a.shape[0]):
        a[i], p = normaliser_par_image(a[i])
        p99.append(p)
    j["p99_par_trame"] = p99
    j["empreinte_sortie"] = empreinte(a)
    return a, j


# ------------------------------------------------------------- empreintes

def empreinte(x) -> str:
    """sha256 des octets d un tableau, 16 premiers hexa.

    Sur `float32` contigu et en ordre C : deux tableaux de meme empreinte sont
    egaux AU BIT. C est le temoin de << un seul module >>."""
    a = np.ascontiguousarray(np.asarray(x, dtype=np.float32))
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


def empreinte_module() -> str:
    """sha256 de CE fichier, 16 premiers hexa. Publie dans chaque recu : deux
    recus de meme empreinte ont normalise pareil."""
    p = pathlib.Path(__file__)
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


# ------------------------------------------------------ temoins a deux sens

def verifier_determinisme(graine: int = 20260907) -> dict:
    """Le MEME tenseur d entree donne la MEME sortie, et un tenseur different en
    donne une differente. Les deux sens, sinon un hachage constant passerait."""
    rng = np.random.default_rng(graine)
    n_t, z, y, x = 8, 8, 32, 32
    pile = rng.uniform(0.0, 1000.0, size=(n_t, z, y * 2, x * 2)).astype(np.float32)

    def lire(f):
        return pile[int(f)]

    a1, j1 = fenetre_normalisee(lire, 3, n_t)
    a2, j2 = fenetre_normalisee(lire, 3, n_t)
    pile2 = pile.copy()
    pile2[3, 0, 0, 0] += np.float32(12345.0)

    def lire2(f):
        return pile2[int(f)]

    a3, j3 = fenetre_normalisee(lire2, 3, n_t)
    return {
        "empreinte_1": j1["empreinte_sortie"],
        "empreinte_2": j2["empreinte_sortie"],
        "empreinte_entree_modifiee": j3["empreinte_sortie"],
        "identiques_au_bit": bool(j1["empreinte_sortie"] == j2["empreinte_sortie"]
                                  and np.array_equal(a1, a2)),
        "sensible_a_l_entree": bool(j1["empreinte_sortie"]
                                    != j3["empreinte_sortie"]),
        "p99_par_trame": j1["p99_par_trame"],
        "forme": list(a1.shape),
        "ok": bool(j1["empreinte_sortie"] == j2["empreinte_sortie"]
                   and j1["empreinte_sortie"] != j3["empreinte_sortie"]),
        "_a3_non_nul": bool(np.isfinite(a3).all()),
    }


def verifier_ordre_normalisation(graine: int = 7) -> dict:
    """La normalisation vient APRES l augmentation : preuve executee.

    Un gain global constant applique AVANT la normalisation par image doit
    disparaitre (la division par le p99 l annule exactement) ; le meme gain
    applique APRES ne disparaitrait pas. On mesure les deux."""
    rng = np.random.default_rng(graine)
    v = rng.uniform(1.0, 1000.0, size=(4, 16, 16)).astype(np.float32)
    a, _ = normaliser_par_image(v)
    b, _ = normaliser_par_image(v * np.float32(3.7))
    apres = (a * np.float32(3.7))
    return {
        "ecart_max_gain_avant_normalisation": float(np.abs(a - b).max()),
        "ecart_max_gain_apres_normalisation": float(np.abs(a - apres).max()),
        "ok": bool(np.abs(a - b).max() < 1e-5
                   and np.abs(a - apres).max() > 1e-3),
    }


def verifier_lampe(n: int = 200000, graine: int = 20260907) -> dict:
    """Remesure sur des tirages les quatre chiffres de `R_TEST_LAMPE_199.json`.

    Ce n est pas une tautologie : la fonction de quantile pourrait etre mal
    interpolee, mal bornee, ou le sens aleatoire pourrait casser la monotonie.
    On mesure aussi la MONOTONIE des rampes, qui est le fait qualitatif du
    reçu (les huit pires courbes sont des rampes lisses)."""
    rng = np.random.default_rng(graine)
    r = np.array([tirer_rapport_lampe(rng) for _ in range(int(n))])
    g = [profil_lampe(4, rng) for _ in range(2000)]
    monotones = sum(1 for x in g
                    if np.all(np.diff(x) >= -1e-6) or np.all(np.diff(x) <= 1e-6))
    med = float(np.median(r))
    return {
        "n_tirages": int(n),
        "mediane_tiree": med, "mediane_mesuree_recu": LAMPE_MEDIANE_MESUREE,
        "max_tire": float(r.max()), "max_mesure_recu": LAMPE_MAX_MESURE,
        "part_sup_20pct_tiree": float((r > 1.20).mean()),
        "part_sup_20pct_recu": LAMPE_PART_SUP_20PCT,
        "part_sup_100pct_tiree": float((r > 2.00).mean()),
        "part_sup_100pct_recu": LAMPE_PART_SUP_100PCT,
        "rampes_monotones": f"{monotones}/2000",
        "ok": bool(abs(med - LAMPE_MEDIANE_MESUREE) < 0.02
                   and r.max() <= LAMPE_MAX_MESURE + 1e-9
                   and abs(float((r > 1.20).mean()) - LAMPE_PART_SUP_20PCT) < 0.02
                   and abs(float((r > 2.00).mean()) - LAMPE_PART_SUP_100PCT) < 0.02
                   and monotones == 2000),
    }


def verifier_memoisation(graine: int = 4242) -> dict:
    """Le chemin MEMOISE rend-il EXACTEMENT le chemin ordinaire ?

    Preuve au bit sur plusieurs instants successifs (c est la ou la memoisation
    mordrait si elle etait fausse : une trame partagee par deux fenetres). Le
    second sens est teste aussi : avec `augmenter=True`, la memoisation doit
    etre DESACTIVEE (une trame augmentee differe d une fenetre a l autre) --
    on verifie que le journal declare `memoise: false`."""
    rng = np.random.default_rng(graine)
    n_t = 10
    pile = rng.uniform(0.0, 900.0, size=(n_t, 6, 24, 24)).astype(np.float32)

    def lire(f):
        return pile[int(f)]

    cache: dict = {}
    ecarts, memoises = [], []
    for t in range(1, n_t - 1):
        a, ja = fenetre_normalisee(lire, t, n_t)
        b, jb = fenetre_normalisee(lire, t, n_t, cache_grille=cache)
        ecarts.append(float(np.abs(a - b).max()))
        memoises.append((ja["empreinte_sortie"] == jb["empreinte_sortie"],
                         jb["memoise"]))
    _, j_aug = fenetre_normalisee(lire, 3, n_t, cache_grille=cache,
                                  rng=np.random.default_rng(1), augmenter=True)
    return {
        "n_instants": n_t - 2, "ecart_max": max(ecarts),
        "empreintes_egales": all(e for e, _ in memoises),
        "memoise_declare": all(m for _, m in memoises),
        "memoise_desactive_sous_augmentation": bool(not j_aug["memoise"]),
        "n_trames_en_cache": len(cache),
        "ok": bool(max(ecarts) == 0.0 and all(e for e, _ in memoises)
                   and all(m for _, m in memoises) and not j_aug["memoise"]),
    }


__all__ = [
    "SOUS_ECHANTILLON_P99", "QUANTILE", "DECALAGES_DEFAUT",
    "RAPPORT_LAMPE_QUANTILES", "ErreurNormalisation",
    "p99_image", "normaliser_par_image", "tirer_rapport_lampe", "profil_lampe",
    "augmenter_photometrie", "trame_normalisee", "fenetre_normalisee",
    "empreinte", "verifier_memoisation",
    "empreinte_module", "verifier_determinisme", "verifier_ordre_normalisation",
    "verifier_lampe",
]
