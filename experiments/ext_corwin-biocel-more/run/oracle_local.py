# -*- coding: utf-8 -*-
"""CIBLAGE tache D -- l ORACLE PAR COMPOSANTE DE DESACCORD.

THESE (Guillaume + HADES) : le film est une unite trop grossiere. Dans un meme
film, un geste aide une zone et abime une autre, et le label moyen du film annule
le signal. On mesure donc le prix LOCAL avant de construire quoi que ce soit.

DEFINITIONS, posees ici et pas ailleurs.
  APPARIEMENT. Deux mondes W0 (temoin) et W1 (candidat) sur le meme film. Par
  trame, on apparie les noeuds au plus proche voisin MUTUEL a moins de
  `--rayon` um (defaut 3,250 um, le pas de la grille de detection). Un noeud de
  W0 sans partenaire est RETIRE, un noeud de W1 sans partenaire est AJOUTE, un
  couple dont les positions different est DEPLACE.
  ENTITE. Un noeud retire, un noeud ajoute, ou un couple deplace. Les couples
  identiques ne sont pas des entites : les deux mondes y coincident.
  ARETE DIFFERENTE. Une arete de W0 absente de W1 (dans l espace des entites),
  ou l inverse.
  COMPOSANTE. Composante connexe des entites, deux entites etant liees si elles
  partagent une arete differente, si elles sont dans la MEME TRAME a moins de
  7,0 um (la porte du juge), ou si une arete (de W0 ou de W1) les relie a une
  trame d ecart.

  MONDE MIXTE M_c. W0 partout, sauf que les entites de c prennent leur version
  W1 : les RETIREES disparaissent, les AJOUTEES apparaissent, les DEPLACEES
  prennent la position W1. Les aretes touchant une entite de c viennent de W1,
  les autres de W0. L ORDRE DES ARETES est celui de W0 pour les siennes, et les
  aretes de W1 sont inserees a la place de la premiere arete de W0 supprimee
  (l ordre fixe EDGE_ID, donc le plafond d out-degree : il ne se bricole pas).

  Le score de M_c est celui du JUGE OFFICIEL sur le monde entier -- jamais un
  compteur local. C est le seul moyen de tenir compte du fait qu une composante
  deplace les appariements de ses voisines.

EVAL_ONLY : la GT ne sert qu a mesurer.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

import os
sys.path.insert(0, str(pathlib.Path(
    os.environ.get("BIOCEL_REPO", "D:/Github/BIOCELL_WINNING")) / "04_SRC"))
from lifetwin.radar import juge as J  # noqa: E402

PORTE_UM = 7.0
RAYON_DEFAUT = 3.25


# ------------------------------------------------------------- appariement
def appariement(W0: J.Monde, W1: J.Monde, echelle, rayon: float = RAYON_DEFAUT):
    """Plus proche voisin MUTUEL par trame, a moins de `rayon` um.

    Rend (m01, m10) : m01[i] = indice dans W1 du partenaire du noeud i de W0
    (-1 s il n en a pas), et reciproquement.
    """
    from scipy.spatial import cKDTree
    e = np.asarray(echelle, dtype=np.float64)
    P0 = W0.zyx * e
    P1 = W1.zyx * e
    m01 = np.full(W0.n_noeuds, -1, dtype=np.int64)
    m10 = np.full(W1.n_noeuds, -1, dtype=np.int64)
    trames = np.union1d(np.unique(W0.t), np.unique(W1.t))
    for k in trames:
        i0 = np.nonzero(W0.t == k)[0]
        i1 = np.nonzero(W1.t == k)[0]
        if not len(i0) or not len(i1):
            continue
        t0, t1 = cKDTree(P0[i0]), cKDTree(P1[i1])
        d01, j01 = t1.query(P0[i0], k=1, distance_upper_bound=rayon)
        d10, j10 = t0.query(P1[i1], k=1, distance_upper_bound=rayon)
        for a in range(len(i0)):
            b = j01[a]
            if b >= len(i1):
                continue
            if j10[b] < len(i0) and j10[b] == a:
                m01[i0[a]] = i1[b]
                m10[i1[b]] = i0[a]
    return m01, m10


def entites(W0, W1, m01, m10, echelle):
    """Les entites de desaccord et les aretes differentes.

    Rend un dictionnaire : `type` ('r', 'a', 'm'), `i0`, `i1` par entite, plus
    `ent_de_n0` / `ent_de_n1` (indice d entite d un noeud, -1 si aucune).
    """
    e = np.asarray(echelle, dtype=np.float64)
    typ, i0s, i1s = [], [], []
    ent_de_n0 = np.full(W0.n_noeuds, -1, dtype=np.int64)
    ent_de_n1 = np.full(W1.n_noeuds, -1, dtype=np.int64)
    for i in range(W0.n_noeuds):
        j = m01[i]
        if j < 0:
            ent_de_n0[i] = len(typ)
            typ.append("r")
            i0s.append(i)
            i1s.append(-1)
        elif not np.allclose(W0.zyx[i] * e, W1.zyx[j] * e, atol=1e-9):
            ent_de_n0[i] = ent_de_n1[j] = len(typ)
            typ.append("m")
            i0s.append(i)
            i1s.append(j)
    for j in range(W1.n_noeuds):
        if m10[j] < 0:
            ent_de_n1[j] = len(typ)
            typ.append("a")
            i0s.append(-1)
            i1s.append(j)
    return {"type": np.array(typ, dtype="<U1"), "i0": np.array(i0s, dtype=np.int64),
            "i1": np.array(i1s, dtype=np.int64),
            "ent_de_n0": ent_de_n0, "ent_de_n1": ent_de_n1}


def entites_d_aretes(ent, W0, W1, a0, a1, diff0, diff1):
    """AJOUTE une entite par arete DIFFERENTE dont aucun bout n est deja une entite.

    Sans cela un RE-LIAGE entre deux noeuds inchanges serait invisible : le
    controle de mecanique (toutes les composantes prises = W1) le revele
    aussitot -- il valait 3,299e-04 sur normimg_pur avant cette correction.
    Le type est 'E' (arete de W0 a retirer) ou 'A' (arete de W1 a poser).
    """
    typ = list(ent["type"])
    i0s = list(ent["i0"])
    i1s = list(ent["i1"])
    ent_de_a0 = np.full(len(a0), -1, dtype=np.int64)
    ent_de_a1 = np.full(len(a1), -1, dtype=np.int64)
    for k in diff0:
        u, v = a0[k]
        if ent["ent_de_n0"][u] < 0 and ent["ent_de_n0"][v] < 0:
            ent_de_a0[k] = len(typ)
            typ.append("E")
            i0s.append(int(u))
            i1s.append(-1)
    for k in diff1:
        u, v = a1[k]
        if ent["ent_de_n1"][u] < 0 and ent["ent_de_n1"][v] < 0:
            ent_de_a1[k] = len(typ)
            typ.append("A")
            i0s.append(-1)
            i1s.append(int(u))
    ent = dict(ent)
    ent["type"] = np.array(typ, dtype="<U1")
    ent["i0"] = np.array(i0s, dtype=np.int64)
    ent["i1"] = np.array(i1s, dtype=np.int64)
    ent["ent_de_a0"] = ent_de_a0
    ent["ent_de_a1"] = ent_de_a1
    return ent


def aretes_differentes(W0, W1, m01, m10):
    """Les aretes de W0 absentes de W1 et l inverse, dans l espace des noeuds de W0.

    Une arete de W1 dont un bout n a pas de partenaire ne peut pas exister dans
    W0 : elle est differente par construction.
    """
    idx0 = W0.index_par_id()
    idx1 = W1.index_par_id()
    a0 = np.array([[idx0[int(u)], idx0[int(v)]] for u, v in W0.edges], dtype=np.int64) \
        if W0.n_aretes else np.zeros((0, 2), np.int64)
    a1 = np.array([[idx1[int(u)], idx1[int(v)]] for u, v in W1.edges], dtype=np.int64) \
        if W1.n_aretes else np.zeros((0, 2), np.int64)
    # aretes de W1 projetees dans l espace des indices de W0 (-1 si sans partenaire)
    a1_p = np.where(a1 >= 0, m10[a1], -1) if len(a1) else np.zeros((0, 2), np.int64)
    s0 = {(int(u), int(v)) for u, v in a0}
    s1 = {(int(u), int(v)) for u, v in a1_p if u >= 0 and v >= 0}
    diff0 = np.array([k for k, (u, v) in enumerate(a0) if (int(u), int(v)) not in s1],
                     dtype=np.int64)
    diff1 = np.array([k for k, (u, v) in enumerate(a1_p)
                      if u < 0 or v < 0 or (int(u), int(v)) not in s0], dtype=np.int64)
    return a0, a1, a1_p, diff0, diff1


class UnionFind:
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


def composantes(W0, W1, ent, a0, a1, a1_p, diff0, diff1, echelle,
                porte_um: float = PORTE_UM):
    """Composantes connexes des entites (voir l en-tete du module)."""
    from scipy.spatial import cKDTree
    n = len(ent["type"])
    uf = UnionFind(n)
    e = np.asarray(echelle, dtype=np.float64)

    def ent_de(cote, i):
        return ent["ent_de_n0"][i] if cote == 0 else ent["ent_de_n1"][i]

    # 1. liens par arete differente ; une entite d arete se lie a ses bouts
    for k in diff0:
        u, v = a0[k]
        eu, ev = ent_de(0, u), ent_de(0, v)
        ea = ent.get("ent_de_a0", np.full(len(a0), -1))[k]
        for x, y in ((eu, ev), (ea, eu), (ea, ev)):
            if x >= 0 and y >= 0:
                uf.unis(x, y)
    for k in diff1:
        u, v = a1[k]
        eu, ev = ent_de(1, u), ent_de(1, v)
        ea = ent.get("ent_de_a1", np.full(len(a1), -1))[k]
        for x, y in ((eu, ev), (ea, eu), (ea, ev)):
            if x >= 0 and y >= 0:
                uf.unis(x, y)
    # 2. liens de proximite dans la MEME trame
    pos, tr = [], []
    for k in range(n):
        if ent["i0"][k] >= 0:
            pos.append(W0.zyx[ent["i0"][k]] * e)
            tr.append(W0.t[ent["i0"][k]])
        else:
            pos.append(W1.zyx[ent["i1"][k]] * e)
            tr.append(W1.t[ent["i1"][k]])
    pos = np.array(pos)
    tr = np.array(tr)
    for k in np.unique(tr):
        idx = np.nonzero(tr == k)[0]
        if len(idx) < 2:
            continue
        arbre = cKDTree(pos[idx])
        for a, b in arbre.query_pairs(porte_um):
            uf.unis(idx[a], idx[b])
    # 3. liens par arete a une trame d ecart (W0 et W1, differentes ou non)
    for a, cote in ((a0, 0), (a1, 1)):
        for u, v in a:
            eu, ev = ent_de(cote, u), ent_de(cote, v)
            if eu >= 0 and ev >= 0:
                uf.unis(eu, ev)

    racines = np.array([uf.trouve(k) for k in range(n)])
    _, comp = np.unique(racines, return_inverse=True)
    return comp, pos, tr


# --------------------------------------------------------------- monde mixte
def monde_mixte(W0, W1, ent, m10, a0, a1, comp, choisies: set) -> J.Monde:
    """W0 partout, sauf les entites des composantes `choisies`, prises de W1.

    `m10[j]` donne le partenaire W0 du noeud j de W1 (-1 s il n en a pas) : c est
    lui qui porte l identifiant dans le monde mixte, pour que les aretes de W1 se
    raccordent au reste de W0 sans renumeroter quoi que ce soit.
    """
    n = len(ent["type"])
    dans = np.isin(comp, list(choisies)) if choisies else np.zeros(n, dtype=bool)

    # --- noeuds ---
    garde0 = np.ones(W0.n_noeuds, dtype=bool)
    pos0 = W0.zyx.copy()
    for k in np.nonzero(dans)[0]:
        t = ent["type"][k]
        if t == "r":
            garde0[ent["i0"][k]] = False
        elif t == "m":
            pos0[ent["i0"][k]] = W1.zyx[ent["i1"][k]]
    ajoutes = [int(ent["i1"][k]) for k in np.nonzero(dans)[0] if ent["type"][k] == "a"]

    id0 = W0.node_id
    base = int(id0.max()) + 1 if len(id0) else 0
    id_ajout = {j: base + p for p, j in enumerate(ajoutes)}

    if ajoutes:
        node_id = np.concatenate([id0[garde0],
                                  np.array([id_ajout[j] for j in ajoutes], dtype=np.int64)])
        t_ = np.concatenate([W0.t[garde0], W1.t[ajoutes]])
        zyx = np.concatenate([pos0[garde0], W1.zyx[ajoutes]])
    else:
        node_id, t_, zyx = id0[garde0], W0.t[garde0], pos0[garde0]
    vivants = set(int(x) for x in node_id)

    def id_de_n1(j: int):
        """Identifiant du noeud j de W1 dans le monde mixte, ou None."""
        ek = ent["ent_de_n1"][j]
        if ek >= 0 and ent["type"][ek] == "a":
            return id_ajout.get(int(j))
        i = int(m10[j])
        if i < 0 or not garde0[i]:
            return None
        return int(id0[i])

    ea0 = ent.get("ent_de_a0", np.full(len(a0), -1, dtype=np.int64))
    ea1 = ent.get("ent_de_a1", np.full(len(a1), -1, dtype=np.int64))

    def touche0(k, u, v):
        eu, ev = ent["ent_de_n0"][u], ent["ent_de_n0"][v]
        return ((eu >= 0 and dans[eu]) or (ev >= 0 and dans[ev])
                or (ea0[k] >= 0 and dans[ea0[k]]))

    def touche1(k, u, v):
        eu, ev = ent["ent_de_n1"][u], ent["ent_de_n1"][v]
        return ((eu >= 0 and dans[eu]) or (ev >= 0 and dans[ev])
                or (ea1[k] >= 0 and dans[ea1[k]]))

    # --- L ORDRE DES ARETES. Il fixe EDGE_ID chez le juge, donc le plafond
    # d out-degree : il ne se bricole pas. On FUSIONNE les deux ordres en
    # s ancrant sur les aretes COMMUNES (celles qui existent des deux cotes) :
    # avant d emettre une arete commune gardee de W0, on emet toutes les aretes
    # de W1 qui la precedent dans W1. Ainsi, aucune composante prise redonne W0
    # exactement, et TOUTES les composantes prises redonnent W1 exactement --
    # c est le controle de mecanique du recu.
    a1_p = np.where(a1 >= 0, m10[a1], -1) if len(a1) else np.zeros((0, 2), np.int64)
    commune = {}
    for k in range(len(a1)):
        u, v = a1_p[k]
        if u >= 0 and v >= 0:
            commune.setdefault((int(u), int(v)), k)
    pris1 = np.array([touche1(k, a1[k][0], a1[k][1]) for k in range(len(a1))], dtype=bool)         if len(a1) else np.zeros(0, dtype=bool)

    aretes = []
    etat = {"j": 0}

    def emet_w1(limite):
        while etat["j"] < limite:
            k = etat["j"]
            if pris1[k]:
                au = id_de_n1(int(a1[k][0]))
                av = id_de_n1(int(a1[k][1]))
                if au is not None and av is not None and au in vivants and av in vivants:
                    aretes.append((au, av))
            etat["j"] += 1

    for k in range(len(a0)):
        u, v = a0[k]
        if touche0(k, u, v):
            continue
        k1 = commune.get((int(u), int(v)))
        if k1 is not None and k1 >= etat["j"]:
            emet_w1(k1)
            etat["j"] = k1 + 1
        au, av = int(id0[u]), int(id0[v])
        if au in vivants and av in vivants:
            aretes.append((au, av))
    emet_w1(len(a1))

    return J.Monde(W0.film, node_id, t_, zyx,
                   np.array(aretes, dtype=np.int64).reshape(-1, 2),
                   provenance={"source": "monde mixte", "n_composantes": len(choisies)})


# ------------------------------------------------ restriction a des trames
def restreint(W: J.Monde, trames) -> J.Monde:
    """Le monde reduit aux trames de `trames` (les aretes dont un bout sort tombent).

    Sert a l ACCELERATION : le juge apparie trame par trame et ses compteurs sont
    des sommes sur les trames ; la DIFFERENCE de compteurs entre deux mondes qui
    ne different que sur ces trames-la est donc la meme, restreinte ou entiere.
    Cette egalite n est PAS supposee : `tache_d.py` la verifie composante par
    composante sur un echantillon, contre le jugement du film entier.
    """
    tr = np.asarray(sorted(set(int(x) for x in trames)), dtype=np.int64)
    m = np.isin(W.t, tr)
    ids = set(int(x) for x in W.node_id[m])
    ar = np.array([(int(u), int(v)) for u, v in W.edges
                   if int(u) in ids and int(v) in ids],
                  dtype=np.int64).reshape(-1, 2)
    return J.Monde(W.film, W.node_id[m], W.t[m], W.zyx[m], ar,
                   provenance={"source": "restriction", "trames": tr.tolist()})


def trames_de(comp, ent, W0, W1, c: int, marge: int = 1):
    """Les trames touchees par la composante c, elargies de `marge` de chaque cote."""
    k = np.nonzero(comp == c)[0]
    ts = []
    for i in k:
        if ent["i0"][i] >= 0:
            ts.append(int(W0.t[ent["i0"][i]]))
        if ent["i1"][i] >= 0:
            ts.append(int(W1.t[ent["i1"][i]]))
    a, b = min(ts), max(ts)
    return list(range(a - marge, b + marge + 1))


# --------------------------------------- composantes qui touchent la GT
def composantes_annotees(W0, W1, ent, comp, echelle, film, porte_um: float = PORTE_UM):
    """Vrai pour une composante si l une de ses entites a une ANNOTATION a moins
    de `porte_um` dans sa trame.

    REGLE DE ZEUS (05/09) : la GT du concours est SPARSE. Retirer un noeud NON
    annote est << gratuit et payant >> dans la metrique -- le terme de noeuds
    a_i monte -- alors qu au test cache ce noeud peut tres bien etre annote. Un
    oracle qui collecte ce terme-la n est pas un oracle de suivi, c est un biais
    d echantillonnage. L oracle, le temoin de hasard, les contributions et tout
    label d apprentissage ne se calculent donc QUE sur les composantes annotees.
    """
    from scipy.spatial import cKDTree
    e = np.asarray(echelle, dtype=np.float64)
    g, _ = J.gt_du_film(film)
    a = g.node_attrs()
    gt_t = a["t"].to_numpy()
    G = np.stack([a["z"].to_numpy(), a["y"].to_numpy(), a["x"].to_numpy()],
                 axis=1).astype(np.float64) * e
    nc = int(comp.max()) + 1 if len(comp) else 0
    out = np.zeros(nc, dtype=bool)
    arbres = {}
    for k in range(len(ent["type"])):
        if out[comp[k]]:
            continue
        if ent["i0"][k] >= 0:
            t, p = int(W0.t[ent["i0"][k]]), W0.zyx[ent["i0"][k]] * e
        else:
            t, p = int(W1.t[ent["i1"][k]]), W1.zyx[ent["i1"][k]] * e
        if t not in arbres:
            m = gt_t == t
            arbres[t] = cKDTree(G[m]) if m.any() else None
        arbre = arbres[t]
        if arbre is not None and arbre.query(p, k=1)[0] <= porte_um:
            out[comp[k]] = True
    return out


# ------------------------------------------------------------- canonisation
def canonise(W: J.Monde) -> J.Monde:
    """Reordonne noeuds et aretes dans un ordre CANONIQUE, independant de la source.

    POURQUOI. Le juge n est pas invariant a l ordre des lignes : EDGE_ID suit
    l ordre d insertion et fixe le plafond d out-degree, et l appariement par
    trame depart les egalites par l indice. Mesure sur 6bba_57b7cc1e : le monde
    mixte << toutes composantes prises >> a exactement les MEMES noeuds et les
    MEMES aretes que W1 (0 en trop, 0 manquant) et pourtant un score different de
    7,07e-04 -- rien que par l ordre. C est l ordre de grandeur des effets que la
    tache D cherche : il faut donc l eliminer, pas le subir.

    On juge donc W0, W1 et TOUS les mondes mixtes dans le meme ordre canonique :
    noeuds tries par (t, z, y, x), aretes triees par (cle du noeud source, cle du
    noeud cible). Les scores canoniques ne sont pas les scores officiels du BANC ;
    le recu publie l ecart. Ce sont les DIFFERENCES qui sont mesurees, et elles
    sont alors exemptes d artefact d ordre.
    """
    o = np.lexsort((W.zyx[:, 2], W.zyx[:, 1], W.zyx[:, 0], W.t))
    node_id = W.node_id[o]
    t = W.t[o]
    zyx = W.zyx[o]
    rang = {int(v): i for i, v in enumerate(node_id)}
    if W.n_aretes:
        u = np.array([rang[int(x)] for x in W.edges[:, 0]], dtype=np.int64)
        v = np.array([rang[int(x)] for x in W.edges[:, 1]], dtype=np.int64)
        oe = np.lexsort((v, u))
        edges = W.edges[oe]
    else:
        edges = W.edges
    return J.Monde(W.film, node_id, t, zyx, edges,
                   provenance={**dict(W.provenance), "ordre": "canonique"})
