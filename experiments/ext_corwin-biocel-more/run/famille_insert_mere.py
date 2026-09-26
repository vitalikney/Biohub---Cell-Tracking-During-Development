# -*- coding: utf-8 -*-
"""FAMILLE `INSERT_MERE` -- LA REGLE DEPLOYEE, pas un plan.

    detecteur(view, probmat, image, bornes, q_etoile) -> plan cell08

CE QU'ELLE FAIT, en une phrase : pour chaque mere a out-degre EXACTEMENT 1, elle
cherche a t+1 un pic du `probmat` que le monde a JETE, a distance de fille, et
retient ceux qui ressemblent le plus a une seconde fille -- un objet lumineux et
net, detache de son fond, et LOIN de la soeur deja detectee.

POURQUOI UNE REGLE ET PAS UN PLAN. Sur le test cache il n'existe aucun
identifiant P1 : un plan scelle (`add_edges: [[12345, -1]]`) designe des noeuds
par leur numero et ne se deploie pas. Cette fonction recalcule ses candidates
sur le monde qu'elle recoit.

PLACE DANS LA CHAINE : cellule 08, APRES la famille LISSAGE et APRES la famille
PURGE (ordre du pack : v17 -> lissage -> purge -> insert). Deux consequences :
  * les POSITIONS vues ici sont celles d'APRES le lissage -- c'est exactement la
    fenetre sur laquelle les bornes de quantile ont ete calibrees
    (MONDE_LISSE, sha 59e01c75ae2bc3e24311f1e12fac821b787cf0c0a80798acf498b3024eee9236) ;
  * un noeud insere ici n'a PAS de piste aval. **L'ORDRE PURGE-PUIS-INSERT N'EST
    PAS UNE PREFERENCE, C'EST UNE CONDITION** : REF-EVAL a mesure le
    contrefactuel le 05/09 -- dans l'ordre inverse, la purge detruirait **246 des
    249 insertions**, parce qu'elle coupe les fourches dont une fille n'a aucune
    arete sortante et que c'est exactement la forme d'un noeud qu'on vient de
    creer. Si la purge devient un jour une regle evaluee APRES nous, elle DOIT
    exclure les noeuds crees dans le meme plan. Dans l'ordre actuel (purge avant
    insert, les deux en listes figees) le probleme ne se pose pas : j'ai verifie
    que les deux plans commutent -- 0 mere commune, 0 arete commune.

LES TROIS TRAITS, tous GT-free, combines par la MOYENNE DE LEURS QUANTILES
FIGES (aucun poids, aucun apprentissage a l'execution) :
  1. `contraste_pic_t1`  (REF-DATA) contraste du pic sur son fond local a t+1
  2. `cellness_pic`      (REF-DATA) RADIAL_CELLNESS : (moyenne r<2,5 um - mediane
                         4<r<7 um) / (1,4826 x MAD de la couronne)
  3. `d_d1_pic`          (MITOSE)   distance de la fille DEJA detectee au pic.
     Sens decroissant : une vraie fille manquante est LOIN de sa soeur -- mediane
     8,21 um contre 5,42 um pour les autres, ce qui est la separation
     soeur-soeur que la geometrie GT publiee annonce. Ce trait a remplace une
     indicatrice de valeur manquante qui portait le meme signal en cachette
     (cf. R_M41/R_M43) ; il est geometrique, gratuit et interpretable.

POURQUOI DES QUANTILES FIGES ET NON DES RANGS. Un RANG depend de la population :
une regle qui ne voit qu'un film ne peut pas calculer le rang global. Un QUANTILE
FIGE n'en depend pas -- les bornes sont calculees une fois sur le vivier de
reference, ecrites en dur, scellees par sha, et le score devient une fonction de
la SEULE VALEUR de la candidate. C'est ce qui rend la regle capable de reproduire
AU BIT un plan construit globalement (verifie : `FILM_PAR_FILM_EGALE_GLOBAL`).

EX AEQUO. Le score porte beaucoup d'ex aequo (6 527 sur 10 000 sur le vivier de
reference). Les departager par l'ordre des lignes ferait dependre le plan d'un
detail de stockage -- c'est ce qui a invalide un resultat de REF-MODEL. La CLE
SECONDAIRE est donc deterministe et fonction de la seule candidate :
    (score, contraste decroissant, z, y, x, identifiant de la mere)

MESURE DE REFERENCE (REF-EVAL, monde entier, 139 films tenus, sur SAFE v1) :
    SAFE v1 seul                +0,002984
    + INSERT-MERE parfilm2      +0,004603   (44b6 +0,006495 / 6bba +0,004381)
    + INSERT-MERE top500        +0,005687   (44b6 +0,011726, +7 TP / +2 FP)
"""
from __future__ import annotations

import json
import math
from typing import Callable

import numpy as np

# --------------------------------------------------------------- constantes
UM = np.array([1.625, 0.40625, 0.40625])       # um par voxel natif (z, y, x)
PAS_PM = 1.625                                  # grille probmat, isotrope
RAYON_MONDE = 3.25                              # un pic est JETE au-dela
D_UP_MIN, D_UP_MAX = 4.0, 14.0                  # fenetre mere -> pic
D_D1P_MIN = 4.0                                 # le pic n'est pas la soeur
PROBA_PIC_MIN = 0.5                             # proba sortante du pic
#: PREFILTRE OBLIGATOIRE sur la probabilite que le LIEUR donne a l'arete
#: mere -> pic. Il a DEUX raisons, et chacune suffirait :
#:  (a) PARITE : le vivier de reference (10 000 candidates) a ete construit avec
#:      ce seuil ; sans lui la regle verrait 934 303 candidates et ne pourrait
#:      pas reproduire le plan ;
#:  (b) TEMPS : les deux traits photometriques coutent ~10,6 ms par candidate
#:      (mesure REF-DATA : 106 s pour 10 000). Sans prefiltre, 4 695 candidates
#:      par film feraient ~50 s/film, soit ~2,8 h sur 199 films -- hors du budget
#:      de 4 500 s du noyau. Avec, ~50 par film, soit ~0,5 s/film.
#: CE N'EST PAS UN SEUIL CHOISI, C'EST UNE BORNE DE TRONCATURE (defaut releve
#: par REF-EVAL le 05/09 19:2xZ). Le vivier de reference est un TOP-10000 : cette
#: valeur est simplement sa 10 000e, c'est-a-dire son MINIMUM. Je l'avais
#: arrondie a 0,6046 -- donc PLUS BAS que la coupe reelle -- et la regle admettait
#: des candidates que le vivier n'a jamais vues. Sur P1_V17 aucune n'a devance une
#: retenue et la parite tenait quand meme ; sur un autre monde rien ne le
#: garantit. La valeur EXACTE est donc rétablie ici.
#: RESERVE DE FOND, a porter dans tout reçu : une TRONCATURE et un SEUIL ne sont
#: pas le meme objet. Ils coincident sur le monde qui a servi a calibrer ; sur un
#: monde neuf, la population change et le nombre d'admises avec elle. C'est un
#: comportement VOULU (aucun re-ciblage n'est possible sur le test cache), mais
#: il doit etre mesure sur chaque monde, jamais suppose.
#: PROVENANCE : minimum de `p_lieur_u_p` sur `vivier_10000.parquet`
#: (sha 5bd962930a293fa140b4b9276bb7e82fc8724b7d9cdacaf49fba2aaa60834e93),
#: toutes decimales, jamais arrondi -- un arrondi vers le bas admet des
#: candidates hors vivier.
SEUIL_P_LIEUR = 0.6046308279037476
N_PAR_FILM = 5
CAP_PAR_FILM = 25

SHA_FENETRE = ("59e01c75ae2bc3e24311f1e12fac821b787cf0c0a80798acf498b30"
               "24eee9236")
#: DEUX SHA CIRCULENT POUR LES MEMES BORNES, et je les ai publies de facon
#: interchangeable -- faute a moi, relevee par ma propre garde :
#:   SHA_BORNES_FICHIER  6b8f64e5... : le sha256 du FICHIER sur le disque
#:   SHA_BORNES          f3ca79ba... : le sha256 du CONTENU, ecrit DANS le
#:                                     fichier et rendu par `charger_bornes`
#: La regle verifie le second, parce que c'est celui qui identifie les BORNES
#: elles-memes et non leur mise en forme. Tout reçu doit nommer les deux.
SHA_BORNES = ("f3ca79bafa85b130ff22bdaa8e96cfb16a28df4bef44fd4eef6d78458"
              "32735e3")
SHA_BORNES_FICHIER = ("6b8f64e5f078467e31f6c2f9a3c41419ba45b2312e7209cae26f1d"
                      "0d38f8b19f")

class FenetreInvalide(RuntimeError):
    """La regle REFUSE de tourner sur une vue dont la fenetre n'est pas la
    sienne. Ce n'est pas une precaution : RELAGES-A a construit sa cellule en
    VUE UNIQUE le 05/09 et a donne a INSERT le monde BRUT au lieu du monde
    LISSE ; les trois traits dependent des positions, et cela a produit 522
    insertions au lieu de 499 -- un ecart systematique, sur beaucoup de films,
    qu'aucun compteur ne signalait. La note en tete du fichier ne l'a pas
    empeche ; une exception, si."""


INVARIANTS = {
    "mere_out_degre_exactement_1": "une troisieme fille rend la fourche "
                                   "`malformed` : 0 TP et 1 FP",
    "jamais_d_arete_vers_la_soeur": "v17 la pose deja dans 26 cas sur 30 ; la "
                                    "republier ferait refuser le plan",
    "aucune_fille_a_deux_parents": "le noeud ajoute est neuf",
    "cap_dur_dans_la_regle": CAP_PAR_FILM,
    "n_par_film": N_PAR_FILM,
    "positions_lues_APRES_le_lissage": SHA_FENETRE,
    "prefiltre_p_lieur": "obligatoire : parite avec le vivier ET budget de temps",
}


# ------------------------------------------------- les masques photometriques
def _masques(demi):
    ax = [np.arange(-d, d + 1) * u for d, u in zip(demi, UM)]
    dz, dy, dx = np.meshgrid(*ax, indexing="ij")
    R = np.sqrt(dz ** 2 + dy ** 2 + dx ** 2)
    return R, (R >= 4.0) & (R <= 6.0), R < 2.5, (R > 4.0) & (R < 7.0)


_DEMI = np.ceil(7.0 / UM).astype(int)           # 5, 18, 18
_R, _M_FOND, _M_IN, _M_OUT = _masques(_DEMI)


def _boite(arr, t, z, y, x):
    """sous-cube centre, borde de NaN quand il sort du volume."""
    T = arr.shape[0]
    NZ, NY, NX = arr.shape[-3:]
    if t < 0 or t >= T:
        return None
    zi, yi, xi = int(round(z)), int(round(y)), int(round(x))
    a = [zi - _DEMI[0], yi - _DEMI[1], xi - _DEMI[2]]
    b = [a[i] + 2 * _DEMI[i] + 1 for i in range(3)]
    a2 = [max(0, a[i]) for i in range(3)]
    b2 = [min([NZ, NY, NX][i], b[i]) for i in range(3)]
    if any(a2[i] >= b2[i] for i in range(3)):
        return None
    sub = np.asarray(arr[t, a2[0]:b2[0], a2[1]:b2[1], a2[2]:b2[2]],
                     dtype=np.float32)
    B = np.full(_R.shape, np.nan, np.float32)
    B[a2[0] - a[0]:a2[0] - a[0] + sub.shape[0],
      a2[1] - a[1]:a2[1] - a[1] + sub.shape[1],
      a2[2] - a[2]:a2[2] - a[2] + sub.shape[2]] = sub
    return B


def traits_lumiere(image, t, z_vox, y_vox, x_vox):
    """(contraste, cellness) ou (nan, nan). Fond local soustrait."""
    B = _boite(image, t, z_vox, y_vox, x_vox)
    if B is None:
        return float("nan"), float("nan")
    ci = B[_M_IN]
    ci = ci[np.isfinite(ci)]
    co = B[_M_OUT]
    co = co[np.isfinite(co)]
    if ci.size < 5 or co.size < 20:
        return float("nan"), float("nan")
    m = float(np.median(co))
    mad = float(np.median(np.abs(co - m)))
    s = 1.4826 * mad
    cell = (float(ci.mean()) - m) / s if s > 1e-9 else float("nan")
    contr = (float(ci.mean()) - m) / (m + 1e-6)
    return contr, cell


# ------------------------------------------------------------ quantile fige
def quantile_fige(bornes: list[float], x: float) -> float:
    """fonction de LA SEULE VALEUR : aucune population n'y entre."""
    if not (x == x):                       # NaN -> le pire quantile
        return 0.0
    n = len(bornes) - 1
    lo, hi = 0, len(bornes)
    while lo < hi:                          # searchsorted, cote droit
        mid = (lo + hi) // 2
        if bornes[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo / (n + 1)


# ------------------------------------------------------------- le detecteur
def detecteur(view, probmat, image, bornes: dict, q_etoile: float,
              sha_fenetre: str | None = None,
              manifeste: dict | None = None,
              n_par_film: int = N_PAR_FILM,
              cap_par_film: int = CAP_PAR_FILM,
              seuil_p_lieur: float = SEUIL_P_LIEUR,
              journal: Callable | None = None,
              retour_candidates: bool = False) -> dict:
    """Rend un plan `cell08` pour UN film.

    `view`     : .noeuds() -> (nid, t, z_vox, y_vox, x_vox) ; .successeurs(nid)
    `probmat`  : .points() -> (idx, t, z_pm, y_pm, x_pm) ; .proba_sortante_max(idx)
                 .proba_arete(idx_src, idx_dst) -> float (-1 si absente)
    `image`    : tableau (T, Z, Y, X) en VOXEL NATIF
    `bornes`   : {"contraste_pic_t1": [...], "cellness_pic": [...],
                  "d_d1_pic": [...], "sha256": "..."}
    `q_etoile` : seuil sur la moyenne des trois quantiles
    """
    # ---- CONDITION D'EXECUTION, pas un avertissement : l'appelant DOIT
    # declarer quelle fenetre il fournit, et ce doit etre le monde LISSE.
    # La garde n'interdit pas de tourner sur un AUTRE monde -- elle interdit de
    # tourner sur une fenetre que personne n'a declaree. Les fenetres legitimes
    # sont NOMMEES dans le manifeste ; une fenetre absente leve.
    # PLUS DE REPLI LITTERAL (defaut releve par RELAGES-A). L'ancien code
    # retombait sur `{SHA_FENETRE: ...}` = la fenetre ARRONDIE que j'avais
    # moi-meme retiree du manifeste : le chemin sans manifeste autorisait donc
    # silencieusement le MAUVAIS monde. « Consigner n'est pas appliquer » --
    # mettre a jour le manifeste ne mettait pas a jour la constante. Un defaut
    # PAR DEFAUT vaut mieux qu'un defaut PERIME.
    if manifeste is None:
        raise FenetreInvalide(
            "le manifeste est OBLIGATOIRE : c'est lui qui porte les fenetres "
            "autorisees et les scalaires exacts. Sans lui, la regle ne sait pas "
            "sur quel monde elle a le droit de tourner.")
    # Le manifeste peut arriver de `charger_manifeste` (qui pre-calcule
    # `_scal`) OU d'un `json.load` direct. La derivation est faite ICI, AVANT
    # la garde de fenetre, parce que la garde a besoin de ses seuils : la
    # laisser plus bas rejouait au bit le defaut de RELAGES-A (`KeyError:
    # '_scal'` sur les 199 films, avant tout calcul).
    if "_scal" not in manifeste:
        manifeste = dict(manifeste)
        manifeste["_scal"] = {k: float(v["valeur_repr"])
                              for k, v in manifeste["scalaires"].items()}
    autorisees = dict(manifeste.get("fenetres_autorisees", {}))
    _noeuds = list(view.noeuds())

    # ---- LA LISTE BLANCHE NE FRANCHIT PAS LA FRONTIERE DU DEPLOIEMENT.
    # Defaut trouve par RELAGES-A le 05/09 avant le premier run Kaggle, et il a
    # raison sur toute la ligne : le sha declare est celui du MONDE ENTIER
    # apres lissage. Hors ligne c'est nos 199 films ; sur Kaggle ce sera les
    # 200 films PRIVES, que personne n'a jamais vus. Aucune valeur ne peut donc
    # etre inscrite d'avance, et la regle aurait leve sur CHAQUE film -- la
    # cellule aurait attrape l'erreur famille par famille, le kernel aurait
    # rendu un CSV valide egal a SAFE v1, et la sonde n'aurait RIEN mesure.
    # Une garde qui echoue en silence en rendant un resultat plausible est pire
    # qu'une garde absente.
    #
    # Ce que la garde protege n'est pas l'IDENTITE du monde, c'est une
    # PROPRIETE : recevoir le monde BRUT (positions arrondies au voxel) au lieu
    # du monde LISSE change contraste_pic_t1, cellness_pic et d(d1,pic) sans
    # qu'aucun compteur ne bronche. Cette propriete, elle, se mesure partout.
    #
    # DEUX VOIES, UNE SEULE SEMANTIQUE, ET AUCUN DRAPEAU DE L'APPELANT :
    #   (1) sha connu du manifeste  -> controle par IDENTITE, le plus fort ;
    #   (2) sinon                   -> la regle MESURE elle-meme, sur la vue
    #       qu'elle a recue, la part de coordonnees entieres. Elle ne croit
    #       personne : un `production=True` tendu par l'appelant rendrait la
    #       garde decorative, ce qui est exactement le defaut qu'on corrige.
    #
    # RESERVE, ECRITE ICI PARCE QU'ELLE LIMITE CE QUE CE CONTROLE PROUVE :
    # il distingue « lisse » de « brut arrondi », PAS « lisse » de « lisse puis
    # autre chose ». C'est plus faible que l'identite. La preuve forte reste la
    # parite hors ligne au bit ; ceci est le filet de production.
    if sha_fenetre is not None and sha_fenetre in autorisees:
        preuve_fenetre = {"voie": "identite", "sha_fenetre": sha_fenetre,
                          "fenetre": autorisees[sha_fenetre]}
    else:
        _sc = manifeste["_scal"]
        _manque = [k for k in ("seuil_part_entiers",
                               "seuil_part_entiers_interieurs",
                               "min_interieurs_pour_controle")
                   if k not in _sc]
        if _manque:
            raise FenetreInvalide(
                "manifeste trop ancien : il ne declare pas les seuils de la "
                "garde de propriete " + repr(_manque) + ". Ces seuils DECIDENT "
                "si la regle a le droit de tourner ; les mettre en litteral "
                "dans le code est exactement ce que le manifeste scelle sert a "
                "empecher. Regenerer le manifeste.")
        s_glob = float(_sc["seuil_part_entiers"])
        s_int = float(_sc["seuil_part_entiers_interieurs"])
        n_min = int(float(_sc["min_interieurs_pour_controle"]))
        succ_l, pred_l = {}, {}
        for nid, _t, _z, _y, _x in _noeuds:
            for s in view.successeurs(nid):
                succ_l.setdefault(nid, set()).add(s)
                pred_l.setdefault(s, set()).add(nid)
        n = n_ent = n_int = n_int_ent = 0
        for nid, _t, z, y, x in _noeuds:
            ent = (float(z).is_integer() and float(y).is_integer()
                   and float(x).is_integer())
            n += 1
            n_ent += ent
            if len(succ_l.get(nid, ())) == 1 and len(pred_l.get(nid, ())) == 1:
                n_int += 1
                n_int_ent += ent
        if n == 0:
            raise FenetreInvalide("vue vide : aucune position a mesurer")
        p_glob = n_ent / n
        p_int = (n_int_ent / n_int) if n_int else None
        if p_glob >= s_glob:
            raise FenetreInvalide(
                f"fenetre NON LISSEE : {n_ent}/{n} positions ({p_glob:.4f}) "
                f"sont entieres, seuil {s_glob}. C'est le monde BRUT arrondi "
                "au voxel, pas le monde apres la famille lissage (ordre du "
                "pack : v17 -> lissage -> purge -> insert).")
        # Controle SECOND et PLUS FIN, mesure le 05/09 sur les mondes reels :
        # le lissage ne deplace que les noeuds INTERIEURS d'une chaine simple ;
        # les extremites et les fourches gardent leur position mesuree, donc
        # entiere. La part d'entiers sur TOUS les noeuds monte ainsi jusqu'a
        # 0,2409 (pire film) sur une fenetre parfaitement lissee, ce qui laisse
        # au seuil global une marge enorme et inutilisee. Sur les seuls
        # INTERIEURS, la separation est nette :
        #     P1 lisse      pire film 0,1190   |  BRUT V17  tous les films 1,0000
        #     div_wide O3   pire film 0,1190   |
        #     pos_parab     tous       0,0000  |
        # d'ou un seuil a 0,50 : quatre fois au-dessus du pire monde legitime,
        # deux fois au-dessous du monde brut.
        if p_int is not None and n_int >= n_min and p_int >= s_int:
            raise FenetreInvalide(
                f"fenetre NON LISSEE (controle fin) : {n_int_ent}/{n_int} "
                f"noeuds INTERIEURS de chaine ({p_int:.4f}) ont des positions "
                f"entieres, seuil {s_int}. Le lissage deplace precisement "
                "ces noeuds-la ; s'ils sont entiers, il n'a pas eu lieu.")
        preuve_fenetre = {
            "voie": "propriete_mesuree",
            "sha_fenetre_non_declare": sha_fenetre,
            "part_entiers": p_glob, "seuil_part_entiers": s_glob,
            "n_noeuds": n, "n_entiers": n_ent,
            "part_entiers_interieurs": p_int,
            "seuil_part_entiers_interieurs": s_int,
            "n_interieurs": n_int, "n_interieurs_entiers": n_int_ent,
            "controle_fin_applique": bool(p_int is not None and n_int >= n_min),
            "reserve": "distingue lisse de brut arrondi, PAS lisse de lisse "
                       "puis autre chose ; la preuve forte reste la parite "
                       "hors ligne au bit"}
    if journal is not None:
        journal({"preuve_fenetre": preuve_fenetre})
    # ---- les scalaires viennent du MANIFESTE SCELLE, jamais d'un litteral
    if manifeste is not None:
        # Le manifeste peut arriver de `charger_manifeste` (qui pre-calcule
        # `_scal`) OU d'un `json.load` direct. Exiger le premier etait un
        # couplage NON DOCUMENTE : RELAGES-A a charge le JSON lui-meme et la
        # regle a leve `KeyError: '_scal'` sur les 199 films, avant tout calcul.
        # Une regle qui n'accepte son propre fichier que par une porte non ecrite
        # n'est pas deployable.
        if "_scal" not in manifeste:
            manifeste = dict(manifeste)
            manifeste["_scal"] = {k: float(v["valeur_repr"])
                                  for k, v in manifeste["scalaires"].items()}
        sc = manifeste["_scal"]
        seuil_p_lieur = sc["seuil_p_lieur"]
        if q_etoile is None:
            raise FenetreInvalide("q_etoile doit etre nomme (q250 ou q500)")
        if isinstance(q_etoile, str):
            q_etoile = sc[f"q_etoile_{q_etoile}"]
        attendu_bornes = manifeste["bornes_quantiles"]["sha256_contenu"]
    if bornes.get("sha256") not in (None, attendu_bornes):
        raise FenetreInvalide(
            f"bornes de quantile inattendues : {bornes.get('sha256')!r}, "
            f"attendu {attendu_bornes!r}. Les bornes SONT la regle.")

    from scipy.spatial import cKDTree

    par_t, pos = {}, {}
    # `_noeuds` est deja materialise par la garde de fenetre : rappeler
    # `view.noeuds()` supposerait que l'appelant rende un iterateur NEUF a
    # chaque appel. Rien ne le garantit, et un generateur epuise donnerait
    # une vue VIDE sans lever.
    for nid, t, z, y, x in _noeuds:
        par_t.setdefault(int(t), []).append(nid)
        pos[nid] = np.array([float(z), float(y), float(x)])

    pm_par_t, pm_pos = {}, {}
    for idx, t, z, y, x in probmat.points():
        pm_par_t.setdefault(int(t), []).append(idx)
        # grille probmat -> VOXEL NATIF : z x1, y x4, x x4
        pm_pos[idx] = np.array([float(z), float(y) * 4.0, float(x) * 4.0])

    arbres = {t: (cKDTree(np.array([pos[i] * UM for i in ids])), ids)
              for t, ids in par_t.items() if ids}

    # Chaque noeud du monde -> son point probmat, pour lire p_lieur(u -> pic).
    # L'ORDRE D'ITERATION FAIT PARTIE DE LA DEFINITION, il n'est pas un detail :
    # plusieurs points du probmat peuvent tomber a moins de 3,25 um du meme
    # noeud, et c'est le PREMIER PAR INDICE CROISSANT qui gagne -- exactement
    # comme le vivier de reference l'a construit. Itérer par trame donnait un
    # autre gagnant, donc une autre probabilite p_lieur, donc une mere retenue
    # que le plan juge n'a pas (mesure du 05/09 19:0xZ : la mere 9668 de
    # 44b6_33b596bf, absente du vivier, apparaissait dans la regle).
    pm2w = {}
    for t, ids in pm_par_t.items():
        arb = arbres.get(t)
        if arb is None or not ids:
            continue
        d, j = arb[0].query(np.array([pm_pos[i] * UM for i in ids]), k=1)
        for k, i in enumerate(ids):
            if float(d[k]) <= RAYON_MONDE:
                pm2w[i] = arb[1][int(j[k])]
    n2pm = {}
    for i in sorted(pm2w):                 # INDICE CROISSANT, premier gagnant
        n2pm.setdefault(pm2w[i], i)

    cand = []
    for t in sorted(par_t):
        suiv = pm_par_t.get(t + 1)
        arb = arbres.get(t + 1)
        if not suiv or arb is None:
            continue
        jetes = []
        for i in suiv:
            if probmat.proba_sortante_max(i) < PROBA_PIC_MIN:
                continue
            d, _ = arb[0].query(pm_pos[i] * UM, k=1)
            if float(d) >= RAYON_MONDE:      # le monde l'a JETE
                jetes.append(i)
        if not jetes:
            continue
        arbre_j = cKDTree(np.array([pm_pos[i] * UM for i in jetes]))
        for u in par_t[t]:
            ss = list(dict.fromkeys(view.successeurs(u)))
            if len(ss) != 1:                 # out-degre EXACTEMENT 1
                continue
            d1 = ss[0]
            if d1 not in pos:
                continue
            pu, pd1 = pos[u] * UM, pos[d1] * UM
            # ---- ETAPE 1 : LE PIC DE LA MERE se choisit par la probabilite du
            # LIEUR, pas par le score final. C'est ainsi que le vivier de
            # reference a ete construit (un pic par mere, le meilleur au sens du
            # lieur), et une regle qui choisirait autrement ne reproduirait pas
            # le plan : mesure du 05/09 18:0xZ, un film sur 199 divergeait a
            # q500 pour cette raison. Bonus : un seul calcul photometrique par
            # mere au lieu de plusieurs.
            pic_mere = None
            for jj in arbre_j.query_ball_point(pu, r=D_UP_MAX):
                i = jetes[jj]
                pp = pm_pos[i] * UM
                d_up = float(np.linalg.norm(pu - pp))
                if d_up < D_UP_MIN:
                    continue
                d_d1p = float(np.linalg.norm(pd1 - pp))
                if d_d1p < D_D1P_MIN:
                    continue
                # PREFILTRE p_lieur AVANT l'image : c'est lui qui rend la regle
                # a la fois FIDELE au vivier et TENABLE dans le budget de temps
                iu = n2pm.get(u)
                if iu is None:
                    continue
                pl_ = probmat.proba_arete(iu, i)
                # ATTENTION A L'ORDRE : le seuil s'applique APRES le choix du
                # pic, jamais avant. Le vivier de reference choisit d'abord le
                # meilleur pic de la mere au sens du lieur, PUIS coupe a 0,6046 ;
                # une mere dont le meilleur pic est sous le seuil est ECARTEE et
                # ne se rattrape pas sur un pic moins bon. Filtrer d'abord
                # rattraperait ces meres et poserait des noeuds que le plan juge
                # n'a pas -- un film sur 199 divergeait a q500 pour cela.
                # departage deterministe a probabilite egale
                cle_pic = (-pl_, -probmat.proba_sortante_max(i),
                           pm_pos[i][0], pm_pos[i][1], pm_pos[i][2])
                if pic_mere is None or cle_pic < pic_mere[0]:
                    pic_mere = (cle_pic, i, d_d1p)
            # ---- ETAPE 2 : le SEUIL, sur le pic choisi et sur lui seul
            if pic_mere is not None and -pic_mere[0][0] >= seuil_p_lieur:
                _, i, d_d1p = pic_mere
                contr, cell = traits_lumiere(image, t + 1, *pm_pos[i])
                s = (quantile_fige(bornes["contraste_pic_t1"], contr)
                     + quantile_fige(bornes["cellness_pic"], cell)
                     + quantile_fige(bornes["d_d1_pic"], d_d1p)) / 3.0
                if s >= q_etoile:
                    # cle secondaire DETERMINISTE : jamais l'ordre des lignes
                    cle = (-s, -(contr if contr == contr else -1e9),
                           pm_pos[i][0], pm_pos[i][1], pm_pos[i][2], float(u))
                    cand.append({"cle": cle, "score": s, "pic": i, "t": t,
                                 "u": u, "p_lieur": -pic_mere[0][0]})

    # UN SEUL passage de tri, deterministe, puis le cap DUR de la regle.
    if retour_candidates:
        # la POPULATION ADMISE telle quelle, sans cap ni tri : c'est elle que le
        # temoin de hasard doit echantillonner, pas la selection.
        return [{"u": c["u"], "t": c["t"], "score": c["score"],
                 "p_lieur": c["p_lieur"],
                 "pic_zyx": list(pm_pos[c["pic"]])} for c in cand]
    cand.sort(key=lambda c: c["cle"])
    cand = cand[:min(n_par_film, cap_par_film)]

    plan = {"add_nodes": [], "add_edges": []}
    for k, c in enumerate(cand):
        z, y, x = pm_pos[c["pic"]]
        plan["add_nodes"].append([int(c["t"]) + 1, float(z), float(y), float(x)])
        plan["add_edges"].append([c["u"], -(k + 1)])
    if journal is not None:
        journal({"n_candidates": len(cand), "q_etoile": q_etoile,
                 "bornes_sha256": bornes.get("sha256")})
    return plan


def charger_manifeste(chemin: str, sha_attendu: str | None = None) -> dict:
    """Les scalaires qui DECIDENT vivent ici, pas dans le code (C7, HADES n 125).

    Motif : j'avais ecrit `0,6046` pour une coupe qui vaut 0,6046308279037476,
    arrondie VERS LE BAS -- la regle admettait des candidates hors vivier. Un
    litteral arrondi dans le code est indetectable ; un manifeste scelle ne
    l'est pas.

    Le canari du 05/09 montre que ce seuil est EXACTEMENT SUR UNE ARETE :
    `>= exact` admet 10 000 candidates, `> exact` n'en admet que 9 999, parce
    que la coupe EST le minimum du vivier. La comparaison `>=` fait donc partie
    de la definition, au meme titre que la valeur.
    """
    import hashlib
    brut = open(chemin, "rb").read()
    d = json.loads(brut.decode("utf-8"))
    sha_ecrit = d.pop("sha256", None)
    recalc = hashlib.sha256(json.dumps(
        d, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if sha_ecrit != recalc:
        raise FenetreInvalide(
            f"manifeste corrompu : sha ecrit {sha_ecrit!r}, recalcule {recalc!r}")
    if sha_attendu is not None and sha_attendu != recalc:
        raise FenetreInvalide(
            f"manifeste inattendu : {recalc!r}, attendu {sha_attendu!r}")
    d["sha256"] = recalc
    d["_scal"] = {k: float(v["valeur_repr"])
                  for k, v in d["scalaires"].items()}
    return d


def charger_bornes(chemin: str) -> dict:
    """Les bornes SONT la regle : leur sha doit etre declare dans tout plan."""
    d = json.loads(open(chemin, encoding="utf-8").read())
    out = {t["colonne"]: t["bornes"] for t in d["traits"]}
    out["sha256"] = d.get("sha256")
    return out
