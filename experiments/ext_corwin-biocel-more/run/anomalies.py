# -*- coding: utf-8 -*-
"""CELL08 V0 -- LE RECENSEMENT DES ANOMALIES LOCALES, SANS GT.

L IDEE, EN UNE PHRASE : autour de la porte d appariement du juge (7 um), on ne
demande pas << ce pic est-il un doublon ? >> mais << combien de VIES entrent
dans cette zone, et combien doivent en sortir ? >>. C est la CONSERVATION
LOCALE DES VIES, et elle se lit dans le graphe seul -- aucune GT, aucune image.

LE DECLENCHEUR EST SANS GT. Il ne lit que : les positions (um), les trames, les
aretes, les degres entrant/sortant, la taille des composantes, et la continuite
de vitesse. La GT n intervient QUE dans `coincidence_gt()`, qui MESURE a
posteriori si une anomalie proposee correspond a une erreur du juge -- jamais
pour proposer.

LES DEUX FAMILLES DE V0, ET RIEN D AUTRE
----------------------------------------
DUPLICATE_FUSION   Une foule de DEUX noeuds a moins de `porte_um` dans la meme
                   trame, ou UNE seule vie entre (une arete depuis t-1) et UNE
                   seule sort (une arete vers t+1). La conservation dit : deux
                   noeuds pour une vie. Mondes : W0 (KEEP), W1 (fusion : on
                   garde le noeud le mieux supporte et on re-lie a travers
                   lui), W1' (suppression seche de l autre noeud).
                   CONTRE-EXEMPLE NOMME : 2 pistes avant et 2 apres = DEUX
                   VRAIES VIES (les voisines sont a ~5 um) ; 1 avant et 2
                   persistantes apres = DIVISION candidate. Les deux sont
                   exclues par la regle des degres, pas par un seuil de
                   distance.

DUPLICATE_PARASITE Une composante connexe COURTE (<= `parasite_max_noeuds`)
                   dont CHAQUE noeud est colle (< `parasite_d_um`) a un noeud
                   d une composante LONGUE (>= `parasite_min_voisin`) dans sa
                   propre trame. Monde W1' : la composante entiere disparait.
                   C est le pic redondant que le liage a promu en piste.

SWAP_2x2           Deux pistes qui se croisent a moins de `porte_um` et qui ont
                   echange leurs suites. Chaque noeud a exactement une entree
                   et une sortie ; les successeurs sont distincts ; et la
                   VITESSE des deux pistes, extrapolee depuis t-1, designe
                   l affectation CROISEE. Monde W2 : parentes echangees a
                   l instant du croisement.

CE QUE LE DECLENCHEUR NE FAIT PAS
---------------------------------
Il ne deplace aucun noeud (MOVE est V0-bis), n en ajoute aucun, ne comble aucun
trou (GAP), ne cree aucune division (DIVIDE), ne casse aucun agregat (CLUMP).
Chaque anomalie garde TOUJOURS l option KEEP : c est l oracle, puis l arbitre,
qui decident -- jamais le declencheur.

CHAQUE ANOMALIE PORTE SES PREUVES BRUTES (distance, degres, tailles de
composantes, gain de continuite). Les SEUILS ne sont donc pas cuits dans la
mesure : le recensement peut les balayer apres coup sans re-parcourir les films.
"""
from __future__ import annotations

import numpy as np

PORTE_UM = 7.0

DEFAUTS = {
    "porte_um": 7.0,             # la porte du juge : definition de la foule
    "parasite_max_noeuds": 3,    # une composante de <= 3 noeuds est courte
    "parasite_min_voisin": 10,   # ... collee a une composante de >= 10 noeuds
    "parasite_d_um": 5.0,        # ... a moins de 5 um, a CHAQUE trame
    "swap_marge_um": 1.0,        # gain de continuite exige pour proposer W2
    "familles": ["DUPLICATE_FUSION", "DUPLICATE_PARASITE", "SWAP_2x2"],
}


# ------------------------------------------------------------------ outils
class _UF:
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


def _graphe(node_id, edges):
    """Indices internes, listes d adjacence, degres, composantes connexes."""
    idx = {int(v): i for i, v in enumerate(node_id)}
    n = len(node_id)
    m = len(edges)
    ei = np.empty((m, 2), np.int64)
    for k in range(m):
        ei[k, 0] = idx[int(edges[k, 0])]
        ei[k, 1] = idx[int(edges[k, 1])]
    sortants = [[] for _ in range(n)]
    entrants = [[] for _ in range(n)]
    for k in range(m):
        sortants[ei[k, 0]].append(k)
        entrants[ei[k, 1]].append(k)
    uf = _UF(n)
    for k in range(m):
        uf.unis(int(ei[k, 0]), int(ei[k, 1]))
    racines = np.array([uf.trouve(i) for i in range(n)])
    _, comp = np.unique(racines, return_inverse=True)
    taille = np.bincount(comp, minlength=comp.max() + 1 if n else 1)
    return idx, ei, sortants, entrants, comp, taille


def _foules(P, t, d_um):
    """Les composantes connexes du graphe << a moins de d_um dans la meme
    trame >>. Rend un dict {cle: [indices]} pour les foules de taille >= 2."""
    from scipy.spatial import cKDTree
    n = len(t)
    uf = _UF(n)
    couples = []
    for k in np.unique(t):
        idx = np.nonzero(t == k)[0]
        if len(idx) < 2:
            continue
        arbre = cKDTree(P[idx])
        for a, b in arbre.query_pairs(d_um):
            uf.unis(int(idx[a]), int(idx[b]))
            couples.append((int(idx[a]), int(idx[b])))
    if not couples:
        return {}, 0
    membres = {}
    for a, b in couples:
        for x in (a, b):
            membres.setdefault(uf.trouve(x), set()).add(x)
    return {r: sorted(v) for r, v in membres.items()}, len(couples)


# ------------------------------------------------------- le declencheur V0
def detecte_film(node_id, t, zyx, edges, echelle, params: dict | None = None):
    """Rend (anomalies, statistiques). SANS GT.

    Une anomalie est un dict :
      famille, noeuds (ids natifs), trame, preuves (dict de nombres bruts),
      mondes {"W1": plan, "W1p": plan, "W2": plan} -- chacun un fragment de
      plan cell08 {drop_nodes, drop_edges, add_edges}. W0 = ne rien faire, et
      il n est jamais ecrit : c est l absence de plan.
    """
    p = dict(DEFAUTS)
    p.update(params or {})
    e = np.asarray(echelle, np.float64)
    P = np.asarray(zyx, np.float64) * e
    t = np.asarray(t, np.int64)
    node_id = np.asarray(node_id, np.int64)
    idx, ei, sortants, entrants, comp, taille = _graphe(node_id, edges)
    familles = set(p["familles"])

    anomalies = []
    foules, n_couples = _foules(P, t, float(p["porte_um"]))
    n_foules2 = sum(1 for v in foules.values() if len(v) == 2)

    def nid(i):
        return int(node_id[i])

    # ---------------------------------------------------------- DUPLICATE
    #  Conservation : combien de vies entrent, combien sortent.
    if "DUPLICATE_FUSION" in familles:
        for membres in foules.values():
            if len(membres) != 2:
                continue                     # V0 : les foules de 2, et elles seules
            a, b = membres
            din_a, dout_a = len(entrants[a]), len(sortants[a])
            din_b, dout_b = len(entrants[b]), len(sortants[b])
            n_in, n_out = din_a + din_b, dout_a + dout_b
            if n_in != 1 or n_out != 1:
                continue                     # 2->2 = deux vies ; 1->2 = division
            # le noeud le MIEUX SUPPORTE : d abord le degre, puis la continuite
            deg_a, deg_b = din_a + dout_a, din_b + dout_b
            if deg_a != deg_b:
                garde, mort = (a, b) if deg_a > deg_b else (b, a)
            else:
                garde, mort = (a, b) if nid(a) < nid(b) else (b, a)
            drop_edges, add_edges = [], []
            for k in entrants[mort] + sortants[mort]:
                u, v = int(ei[k, 0]), int(ei[k, 1])
                drop_edges.append((nid(u), nid(v)))
                nu = garde if u == mort else u
                nv = garde if v == mort else v
                if nu != nv:
                    add_edges.append((nid(nu), nid(nv)))
            deja = {(nid(int(ei[k, 0])), nid(int(ei[k, 1])))
                    for k in entrants[garde] + sortants[garde]}
            add_edges = [x for x in add_edges if x not in deja]
            w1 = {"drop_nodes": [nid(mort)], "drop_edges": drop_edges,
                  "add_edges": add_edges}
            w1p = {"drop_nodes": [nid(mort)], "drop_edges": [], "add_edges": []}
            anomalies.append({
                "famille": "DUPLICATE_FUSION",
                "trame": int(t[a]), "noeuds": [nid(a), nid(b)],
                "preuves": {
                    "d_um": float(np.linalg.norm(P[a] - P[b])),
                    "n_in": int(n_in), "n_out": int(n_out),
                    "deg_garde": int(max(deg_a, deg_b)),
                    "deg_mort": int(min(deg_a, deg_b)),
                    "taille_comp_a": int(taille[comp[a]]),
                    "taille_comp_b": int(taille[comp[b]]),
                    "meme_composante": bool(comp[a] == comp[b]),
                    "n_voisins_porte": 2,
                },
                "mondes": {"W1": w1, "W1p": w1p},
            })

    if "DUPLICATE_PARASITE" in familles:
        from scipy.spatial import cKDTree
        d_par = float(p["parasite_d_um"])
        courtes = np.nonzero(taille <= int(p["parasite_max_noeuds"]))[0]
        if len(courtes):
            longue = taille[comp] >= int(p["parasite_min_voisin"])
            par_trame = {}
            for k in np.unique(t[longue]):
                sel = np.nonzero(longue & (t == k))[0]
                par_trame[int(k)] = (sel, cKDTree(P[sel]))
            for c in courtes:
                membres = np.nonzero(comp == c)[0]
                ok, dmax, voisins = True, 0.0, []
                for i in membres:
                    arbre = par_trame.get(int(t[i]))
                    if arbre is None:
                        ok = False
                        break
                    d, j = arbre[1].query(P[i], k=1,
                                          distance_upper_bound=d_par)
                    if not np.isfinite(d):
                        ok = False
                        break
                    dmax = max(dmax, float(d))
                    voisins.append(int(arbre[0][j]))
                if not ok:
                    continue
                morts = [nid(int(i)) for i in membres]
                anomalies.append({
                    "famille": "DUPLICATE_PARASITE",
                    "trame": int(t[membres[0]]), "noeuds": morts,
                    "preuves": {
                        "d_um": dmax,
                        "taille_comp": int(len(membres)),
                        "taille_comp_voisine": int(taille[comp[voisins[0]]]),
                        "n_in": int(sum(len(entrants[int(i)]) for i in membres)),
                        "n_out": int(sum(len(sortants[int(i)]) for i in membres)),
                        "n_voisins_porte": len(set(voisins)),
                    },
                    "mondes": {"W1p": {"drop_nodes": morts, "drop_edges": [],
                                       "add_edges": []}},
                })

    # --------------------------------------------------------------- SWAP
    if "SWAP_2x2" in familles:
        marge = float(p["swap_marge_um"])
        for membres in foules.values():
            if len(membres) != 2:
                continue
            a, b = membres
            if not (len(entrants[a]) == len(sortants[a]) == 1):
                continue
            if not (len(entrants[b]) == len(sortants[b]) == 1):
                continue
            pa = int(ei[entrants[a][0], 0])
            pb = int(ei[entrants[b][0], 0])
            sa = int(ei[sortants[a][0], 1])
            sb = int(ei[sortants[b][0], 1])
            if pa == pb or sa == sb:
                continue                      # une division, pas un croisement
            if t[sa] != t[sb] or t[pa] != t[pb]:
                continue                      # les deux sorties doivent etre en phase
            # vitesse constante depuis t-1, extrapolee a t+1
            pred_a = P[a] + (P[a] - P[pa])
            pred_b = P[b] + (P[b] - P[pb])
            c_actuel = (np.linalg.norm(P[sa] - pred_a)
                        + np.linalg.norm(P[sb] - pred_b))
            c_croise = (np.linalg.norm(P[sb] - pred_a)
                        + np.linalg.norm(P[sa] - pred_b))
            gain = float(c_actuel - c_croise)
            if gain <= marge:
                continue
            # preuve INDEPENDANTE : la meme lecture, en marche arriere
            r_pred_a = P[a] + (P[a] - P[sa])
            r_pred_b = P[b] + (P[b] - P[sb])
            r_actuel = (np.linalg.norm(P[pa] - r_pred_a)
                        + np.linalg.norm(P[pb] - r_pred_b))
            r_croise = (np.linalg.norm(P[pb] - r_pred_a)
                        + np.linalg.norm(P[pa] - r_pred_b))
            anomalies.append({
                "famille": "SWAP_2x2",
                "trame": int(t[a]),
                # les QUATRE noeuds que la correction touche : l echange
                # deplace les aretes a->s_a et b->s_b, donc les successeurs
                # comptent autant que le croisement lui-meme. C est cette
                # liste que lit la regle d annotation.
                "noeuds": [nid(a), nid(b), nid(sa), nid(sb)],
                "preuves": {
                    "d_um": float(np.linalg.norm(P[a] - P[b])),
                    "gain_continuite_um": gain,
                    "gain_arriere_um": float(r_actuel - r_croise),
                    "d_croisement_sorties_um": float(
                        np.linalg.norm(P[sa] - P[sb])),
                    "n_in": 2, "n_out": 2,
                    "meme_composante": bool(comp[a] == comp[b]),
                    "n_voisins_porte": 2,
                },
                "mondes": {"W2": {
                    "drop_nodes": [],
                    "drop_edges": [(nid(a), nid(sa)), (nid(b), nid(sb))],
                    "add_edges": [(nid(a), nid(sb)), (nid(b), nid(sa))],
                }},
            })

    stats = {
        "n_noeuds": int(len(node_id)), "n_aretes": int(len(edges)),
        "n_couples_sous_porte": int(n_couples),
        "n_foules": int(len(foules)),
        "n_foules_de_2": int(n_foules2),
        "n_composantes": int(len(taille)),
        "n_composantes_courtes": int((taille <= int(p["parasite_max_noeuds"])).sum()),
    }
    return anomalies, stats


# ------------------------------------------------- fusion des plans locaux
def plan_de(anomalies, monde: str) -> dict:
    """Reunit les fragments `monde` ('W1', 'W1p', 'W2') d une liste d anomalies
    d UN film en un plan cell08. Les anomalies qui n ont pas ce monde sont
    ignorees. Deux anomalies qui se recouvrent (meme noeud, meme arete) sont
    un CONFLIT : on garde la premiere et on compte les rejetees, plutot que de
    fabriquer un plan que la normalisation refuserait.
    """
    dn, de, ae = set(), set(), []
    pris, rejetes = [], 0
    for k, a in enumerate(anomalies):
        f = a["mondes"].get(monde)
        if f is None:
            continue
        d1 = {int(x) for x in f["drop_nodes"]}
        d2 = {(int(u), int(v)) for u, v in f["drop_edges"]}
        a2 = [(int(u), int(v)) for u, v in f["add_edges"]]
        touche = d1 | {u for u, v in d2} | {v for u, v in d2} \
            | {u for u, v in a2} | {v for u, v in a2}
        deja = dn | {u for u, v in de} | {v for u, v in de} \
            | {u for u, v in ae} | {v for u, v in ae}
        if touche & deja:
            rejetes += 1
            continue
        dn |= d1
        de |= d2
        ae.extend(a2)
        pris.append(k)
    return {"drop_nodes": sorted(dn), "drop_edges": sorted(de),
            "add_edges": ae}, pris, rejetes


# --------------------------------------------------------- detecteur cell08
def _fabrique(monde_par_famille: dict):
    def detecteur(view, params):
        plan = {}
        for film, v in view.items():
            from lifetwin.radar import juge as J
            ech = J.echelle_du_film(film)
            anos, _ = detecte_film(v["node_id"], v["t"], v["zyx"], v["edges"],
                                   ech, params)
            choisies = [a for a in anos
                        if a["famille"] in monde_par_famille
                        and monde_par_famille[a["famille"]] in a["mondes"]]
            for a in choisies:
                a["mondes"] = {"X": a["mondes"][monde_par_famille[a["famille"]]]}
            f, _, _ = plan_de(choisies, "X")
            if f["drop_nodes"] or f["drop_edges"] or f["add_edges"]:
                plan[film] = f
        return plan
    return detecteur


DETECTEURS = {
    "duplicate_fusion": _fabrique({"DUPLICATE_FUSION": "W1"}),
    "duplicate_suppression": _fabrique({"DUPLICATE_FUSION": "W1p"}),
    "duplicate_parasite": _fabrique({"DUPLICATE_PARASITE": "W1p"}),
    "swap": _fabrique({"SWAP_2x2": "W2"}),
}
