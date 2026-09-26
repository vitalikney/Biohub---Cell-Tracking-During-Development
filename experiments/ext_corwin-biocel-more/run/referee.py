r"""`LIFE-REFEREE` V0 : le modele qui prefere une histoire locale a une autre.

Architecture (HADES n°113 §4, n°114 amendements 1-3, mandat REF-MODEL §1) :

    crop 3D+t  --> TEACHER GELE (teacher.py) --> contexte visuel (t-3,t-2,t+2,t+3)
                                             \-> CIBLE          (t-1,t,t+1)  [MASQUEE]
    jetons du monde W --> encodeur de graphe --> representation du monde
    (contexte visuel + monde) --> predicteur --> prediction de la CIBLE
    erreur latente = E_BIO(W)   <-- n°114 la nomme `E_BIO(action)` : le monde
                                    candidat EST l'action dont on predit l'effet

Le point qui fait tout : **les pixels sont identiques pour tous les mondes**.
Seule l'histoire change. Le monde qui permet de mieux predire ce que le film
montre au centre est celui qui explique la vie. Une observation dupliquee, une
fille echangee, un parent faux : le graphe promet quelque chose que l'image ne
tient pas, et l'erreur latente monte.

Quatre lectures independantes de l'erreur :
  - `cible_grille`   : la structure des trames centrales, reduite en 3x3x3 ;
  - `cible_noeuds`   : les features du teacher AUX POSITIONS que le monde affirme
                       (c'est la que DUPLICATE et JITTER se paient) ;
  - `cible_contexte` : des fentes de contexte RETIREES de la memoire et a
                       reconstruire (la `context loss` de la recette n°114) ;
  - avant ET arriere : le meme reseau, le temps renverse, poids partages.

Deux etages, comme le runtime l'exige (n°113 §7, n°114 amendement 2) :
  - **etage LEGER** : les deux graphes seuls, sans une seule lecture d'image.
    Il ne choisit pas le monde ; il decide si la lecture chere est necessaire.
    Sa tete lit une representation DETACHEE : elle ne deforme pas le tronc BIO.
  - **etage VISION** : tout ce qui precede.

Trois tetes separees : preference (BIO), abstention (U), PAY (entree detachee).
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from schema_local import (
    CANAUX_TEACHER,
    DIM_JETON,
    IDX_CENTRE,
    IDX_TRAIT,
    NB_FENTES_CIBLE,
    NB_JETONS_CONTEXTE,
    NB_ROLES,
    NB_TRAITS,
    NB_TYPES,
)


# --------------------------------------------------------------------------
# Briques
# --------------------------------------------------------------------------
class BlocAuto(nn.Module):
    """Bloc transformer d'auto-attention, pre-norm (SDPA via MultiheadAttention)."""

    def __init__(self, d: int, tetes: int, ffn: int, chute: float):
        super().__init__()
        self.n1 = nn.LayerNorm(d)
        self.attn = nn.MultiheadAttention(d, tetes, dropout=chute, batch_first=True)
        self.n2 = nn.LayerNorm(d)
        self.ffn = nn.Sequential(
            nn.Linear(d, ffn), nn.GELU(), nn.Dropout(chute), nn.Linear(ffn, d)
        )
        self.chute = nn.Dropout(chute)

    def forward(self, x, masque_pad=None):
        h = self.n1(x)
        a, _ = self.attn(h, h, h, key_padding_mask=masque_pad, need_weights=False)
        x = x + self.chute(a)
        return x + self.chute(self.ffn(self.n2(x)))


class BlocCroise(nn.Module):
    """Bloc de decodage : auto-attention des requetes, puis attention croisee."""

    def __init__(self, d: int, tetes: int, ffn: int, chute: float):
        super().__init__()
        self.n1 = nn.LayerNorm(d)
        self.auto = nn.MultiheadAttention(d, tetes, dropout=chute, batch_first=True)
        self.n2 = nn.LayerNorm(d)
        self.nm = nn.LayerNorm(d)
        self.croise = nn.MultiheadAttention(d, tetes, dropout=chute, batch_first=True)
        self.n3 = nn.LayerNorm(d)
        self.ffn = nn.Sequential(
            nn.Linear(d, ffn), nn.GELU(), nn.Dropout(chute), nn.Linear(ffn, d)
        )
        self.chute = nn.Dropout(chute)

    def forward(self, q, memoire, masque_memoire=None):
        h = self.n1(q)
        a, _ = self.auto(h, h, h, need_weights=False)
        q = q + self.chute(a)
        m = self.nm(memoire)
        c, _ = self.croise(self.n2(q), m, m, key_padding_mask=masque_memoire,
                           need_weights=False)
        q = q + self.chute(c)
        return q + self.chute(self.ffn(self.n3(q)))


class EncodeurGraphe(nn.Module):
    """Jetons du monde -> representation. Aucune entree absolue, aucun film.

    Les champs categoriels du SCHEMA v0 (`type`, `role`) deviennent des
    plongements ; les 19 traits continus, chacun double d'un bit de validite,
    passent par un MLP. Un jeton GLOBAL est prepose : il porte le resume du monde.
    """

    def __init__(self, d: int, tetes: int, blocs: int, ffn: int, chute: float):
        super().__init__()
        self.emb_type = nn.Embedding(NB_TYPES, d)
        self.emb_role = nn.Embedding(NB_ROLES, d)
        self.jeton_global = nn.Parameter(torch.zeros(1, 1, d))
        nn.init.trunc_normal_(self.jeton_global, std=0.02)
        self.proj = nn.Sequential(nn.Linear(DIM_JETON, d), nn.GELU(), nn.Linear(d, d))
        self.norme = nn.LayerNorm(d)
        self.blocs = nn.ModuleList([BlocAuto(d, tetes, ffn, chute) for _ in range(blocs)])

    def forward(self, jetons, type_jeton, role_jeton, masque):
        x = self.proj(jetons) + self.emb_type(type_jeton) + self.emb_role(role_jeton)
        B = x.shape[0]
        x = torch.cat([self.jeton_global.expand(B, -1, -1), x], dim=1)
        masque = torch.cat(
            [torch.ones(B, 1, dtype=torch.bool, device=x.device), masque], dim=1)
        x = self.norme(x)
        pad = ~masque
        for bloc in self.blocs:
            x = bloc(x, masque_pad=pad)
        return x, masque


def _sinus(valeurs: torch.Tensor, dim: int) -> torch.Tensor:
    """Encodage sinusoidal d'un scalaire continu -> `(..., dim)`."""
    moitie = dim // 2
    freq = torch.exp(
        torch.arange(moitie, device=valeurs.device, dtype=valeurs.dtype)
        * (-math.log(1000.0) / max(moitie - 1, 1))
    )
    ang = valeurs.unsqueeze(-1) * freq * math.pi
    return torch.cat([torch.sin(ang), torch.cos(ang)], dim=-1)


def _moyenne_masquee(x, masque):
    m = masque.unsqueeze(-1).to(x.dtype)
    return (x * m).sum(1) / m.sum(1).clamp(min=1.0)


# --------------------------------------------------------------------------
# Le referee
# --------------------------------------------------------------------------
class LifeReferee(nn.Module):
    """Le referee V0. Taille visee : 5-15 M parametres entraines."""

    def __init__(self, d: int = 256, tetes: int = 8, blocs_graphe: int = 4,
                 blocs_predicteur: int = 4, ffn: int = 1024, chute: float = 0.1,
                 canaux_teacher: int = CANAUX_TEACHER,
                 nb_fentes: int = NB_FENTES_CIBLE,
                 nb_contexte: int = NB_JETONS_CONTEXTE,
                 taux_masque_contexte: float = 0.25):
        super().__init__()
        self.d = d
        self.canaux_teacher = canaux_teacher
        self.nb_fentes = nb_fentes
        self.nb_contexte = nb_contexte
        self.taux_masque_contexte = taux_masque_contexte

        self.graphe = EncodeurGraphe(d, tetes, blocs_graphe, ffn, chute)
        self.proj_visuel = nn.Sequential(
            nn.Linear(canaux_teacher, d), nn.GELU(), nn.Linear(d, d))
        self.pos_contexte = nn.Parameter(torch.zeros(1, nb_contexte, d))
        self.marque_visuelle = nn.Parameter(torch.zeros(1, 1, d))
        self.marque_monde = nn.Parameter(torch.zeros(1, 1, d))
        nn.init.trunc_normal_(self.pos_contexte, std=0.02)

        self.requetes_grille = nn.Parameter(torch.zeros(1, nb_fentes, d))
        self.requetes_contexte = nn.Parameter(torch.zeros(1, nb_contexte, d))
        nn.init.trunc_normal_(self.requetes_grille, std=0.02)
        nn.init.trunc_normal_(self.requetes_contexte, std=0.02)
        self.proj_noeud = nn.Sequential(
            nn.Linear(4 * 32, d), nn.GELU(), nn.Linear(d, d))
        self.requete_noeud = nn.Parameter(torch.zeros(1, 1, d))
        # 0 = « mon histoire dit qu'il n'y a PAS de cellule ici », 1 = « il y en a une ».
        # C'est la seule difference entre les deux mondes sur une fente partagee.
        self.emb_affirme = nn.Embedding(2, d)

        self.predicteur = nn.ModuleList(
            [BlocCroise(d, tetes, ffn, chute) for _ in range(blocs_predicteur)])
        self.norme_sortie = nn.LayerNorm(d)
        self.tete_cible = nn.Linear(d, canaux_teacher)

        # --- energie : erreurs mesurees + representation, pas l'une sans l'autre
        self.poids_grille = nn.Parameter(torch.tensor(1.0))
        self.poids_noeuds = nn.Parameter(torch.tensor(1.0))
        self.tete_energie = nn.Sequential(
            nn.Linear(2 * d + 6, d), nn.GELU(), nn.Dropout(chute), nn.Linear(d, 1))
        self.tete_abstention = nn.Sequential(
            nn.Linear(2 * d + 6, d // 2), nn.GELU(), nn.Linear(d // 2, 1))
        # --- PAY : entree DETACHEE, aucun gradient sur le tronc BIO
        self.tete_pay = nn.Sequential(
            nn.Linear(4 * d + 14, d // 2), nn.GELU(), nn.Linear(d // 2, 2))
        # --- ETAGE LEGER : les deux graphes seuls, entree DETACHEE elle aussi.
        #     Il ne choisit pas le monde : il decide si la vision est necessaire.
        self.tete_legere = nn.Sequential(
            nn.Linear(2 * d + 2, d // 2), nn.GELU(), nn.Linear(d // 2, 2))
        self.temperature = nn.Parameter(torch.tensor(1.0))
        # Les tetes partent PRES de zero (poids x0,01, biais nul) : sans cela
        # l'abstention et le declencheur naissent satures -- perte 7,5 et 8,4
        # mesurees au premier pas -- et passent leurs premieres epoques a revenir
        # de leur propre initialisation. On ne met PAS exactement zero : une
        # derniere couche nulle prive la couche precedente de tout gradient au
        # premier pas, et un essai qui verifie que « le gradient passe partout »
        # aurait raison de mordre.
        for tete in (self.tete_energie, self.tete_abstention,
                     self.tete_legere, self.tete_pay):
            derniere = [m for m in tete if isinstance(m, nn.Linear)][-1]
            with torch.no_grad():
                derniere.weight.mul_(0.01)
                derniere.bias.zero_()

    # ---------------------------------------------------------------- outils
    moyenne_masquee = staticmethod(_moyenne_masquee)

    def _requetes_noeuds(self, noeuds, affirme=None):
        """Requetes de noeud : la POSITION interrogee, plus ce que CE monde en dit.

        Les fentes sont PARTAGEES entre les deux mondes (schema_local.noeuds_partages) ;
        seul `affirme` change. Le monde qui affirme une cellule absente de l'image
        paie, et celui qui nie une cellule presente paie aussi.
        """
        codes = torch.cat([_sinus(noeuds[..., i], 32) for i in range(4)], dim=-1)
        q = self.proj_noeud(codes) + self.requete_noeud
        if affirme is not None:
            q = q + self.emb_affirme(affirme.round().long().clamp(0, 1))
        return q

    def _masque_contexte(self, B: int, device) -> torch.Tensor:
        """Fentes de contexte RETIREES de la memoire (context loss, n°114).

        A l'entrainement seulement : hors entrainement l'energie doit etre
        deterministe, sinon deux mesures du meme monde ne se comparent pas.
        """
        if not self.training or self.taux_masque_contexte <= 0:
            return torch.zeros(B, self.nb_contexte, dtype=torch.bool, device=device)
        return torch.rand(B, self.nb_contexte, device=device) < self.taux_masque_contexte

    # ---------------------------------------------------------------- avant
    def forward(self, visuel: dict, monde: dict) -> dict:
        """Une lecture d'un monde. `visuel` vient du teacher gele (partage entre
        les mondes : les pixels ne changent pas), `monde` porte les jetons."""
        B = visuel["contexte"].shape[0]
        dev = visuel["contexte"].device
        ctx = self.proj_visuel(visuel["contexte"]) + self.pos_contexte + self.marque_visuelle
        rep_monde, masque_monde = self.graphe(
            monde["jetons"], monde["type_jeton"],
            monde["role_jeton"], monde["masque_jeton"])
        memoire = torch.cat([ctx, rep_monde + self.marque_monde], dim=1)

        masque_ctx = self._masque_contexte(B, dev)
        pad = torch.cat([masque_ctx, ~masque_monde], dim=1)

        noeuds, masque_n = monde["noeuds_centre"], monde["masque_noeuds"]
        q = torch.cat([
            self.requetes_grille.expand(B, -1, -1),
            self.requetes_contexte.expand(B, -1, -1),
            self._requetes_noeuds(noeuds, monde.get("affirme_noeuds")),
        ], dim=1)
        for bloc in self.predicteur:
            q = bloc(q, memoire, masque_memoire=pad)
        pred = self.tete_cible(self.norme_sortie(q))

        a, b = self.nb_fentes, self.nb_fentes + self.nb_contexte
        pred_grille, pred_ctx, pred_noeuds = pred[:, :a], pred[:, a:b], pred[:, b:]

        err_g = 1.0 - F.cosine_similarity(pred_grille, visuel["cible"], dim=-1)
        err_c = 1.0 - F.cosine_similarity(pred_ctx, visuel["contexte"], dim=-1)
        err_n = 1.0 - F.cosine_similarity(pred_noeuds, monde["cible_noeuds"], dim=-1)

        e_grille = err_g.mean(1)
        m = masque_n.to(err_n.dtype)
        e_noeuds = (err_n * m).sum(1) / m.sum(1).clamp(min=1.0)
        e_noeuds_max = torch.where(masque_n, err_n,
                                   torch.full_like(err_n, -1e9)).max(1).values
        e_noeuds_max = torch.where(masque_n.any(1), e_noeuds_max,
                                   torch.zeros_like(e_noeuds_max))

        pool_monde = _moyenne_masquee(rep_monde, masque_monde)
        pool_ctx = ctx.mean(1)
        resume = torch.stack([
            e_grille, e_noeuds, e_noeuds_max, err_g.std(1),
            m.sum(1) / max(masque_n.shape[1], 1),
            masque_monde.to(err_g.dtype).mean(1),
        ], dim=-1)
        traits = torch.cat([pool_monde, pool_ctx, resume], dim=-1)

        energie = (
            F.softplus(self.poids_grille) * e_grille
            + F.softplus(self.poids_noeuds) * e_noeuds
            + self.tete_energie(traits).squeeze(-1)
        )
        # `E_mesuree` = l'energie SANS la tete apprise : uniquement l'erreur de
        # prediction latente. Elle ne contient AUCUN parametre ajuste sur des
        # etiquettes de preference. Publiee a part, elle repond a la seule
        # question qui compte : le modele LIT-IL le film ? Un ecart entre elle
        # et `E` dit ce que la tete a ajoute -- et, si la tete surapprend sur
        # peu d'etiquettes, c'est `E_mesuree` qui reste lisible.
        e_mesuree = (F.softplus(self.poids_grille) * e_grille
                     + F.softplus(self.poids_noeuds) * e_noeuds)
        return {
            "E": energie, "E_mesuree": e_mesuree,
            "e_grille": e_grille, "e_noeuds": e_noeuds,
            "err_grille": err_g, "err_contexte": err_c, "err_noeuds": err_n,
            "masque_contexte": masque_ctx, "traits": traits,
            "pred_grille": pred_grille, "pred_contexte": pred_ctx,
            "pred_noeuds": pred_noeuds,
            "rep_monde": rep_monde, "masque_monde": masque_monde,
            "pool_monde": pool_monde,
        }

    # ------------------------------------------------------- avant + arriere
    def lire(self, visuel_av: dict, visuel_ar: dict,
             monde_av: dict, monde_ar: dict) -> dict:
        av = self.forward(visuel_av, monde_av)
        ar = self.forward(visuel_ar, monde_ar)
        return {
            "E": 0.5 * (av["E"] + ar["E"]),
            "E_mesuree": 0.5 * (av["E_mesuree"] + ar["E_mesuree"]),
            "ecart_sens": (av["E"] - ar["E"]).abs(),
            "avant": av, "arriere": ar,
            "traits": 0.5 * (av["traits"] + ar["traits"]),
            "pool_monde": 0.5 * (av["pool_monde"] + ar["pool_monde"]),
        }

    # ------------------------------------------------------------ decisions
    def decider(self, keep: dict, cand: dict) -> dict:
        """KEEP / REPLACE / ABSTAIN a partir des deux energies.

        `P_ABSTAIN` sort de la MEME softmax que les deux autres : l'abstention
        est une decision apprise, pas un seuil pose apres la mesure.
        """
        e_keep, e_cand = keep["E"], cand["E"]
        u = self.tete_abstention(0.5 * (keep["traits"] + cand["traits"])).squeeze(-1)
        tau = F.softplus(self.temperature) + 1e-3
        logits = torch.stack([-tau * e_keep, -tau * e_cand, u], dim=-1)
        p = F.softmax(logits, dim=-1)
        return {
            "P_KEEP": p[:, 0], "P_REPLACE": p[:, 1], "P_ABSTAIN": p[:, 2],
            "E_keep": e_keep, "E_cand": e_cand, "U": F.softplus(u),
            "marge": e_keep - e_cand, "logits": logits,
            "traits_pay": torch.cat([keep["traits"], cand["traits"]], dim=-1),
        }

    def pay(self, decision: dict) -> dict:
        """Tete PAY, sur une entree DETACHEE. Aucun gradient vers le tronc BIO."""
        entree = torch.cat([
            decision["traits_pay"].detach(),
            decision["E_keep"].detach().unsqueeze(-1),
            decision["E_cand"].detach().unsqueeze(-1),
        ], dim=-1)
        s = self.tete_pay(entree)
        return {"delta_chapeau": s[:, 0], "logit_signe": s[:, 1]}

    # -------------------------------------------------------- etage LEGER
    def leger(self, monde_keep: dict, monde_cand: dict,
              detache: bool = True) -> dict:
        """Le declencheur : les deux graphes, AUCUNE lecture d'image.

        Il rend une marge. Si elle est franche, la composante ne paie jamais la
        vision. `detache=True` (defaut) : sa perte ne deforme pas le tronc BIO --
        le declencheur ne choisit pas le monde (n°113 §7).
        """
        rk, mk = self.graphe(monde_keep["jetons"], monde_keep["type_jeton"],
                             monde_keep["role_jeton"], monde_keep["masque_jeton"])
        rc, mc = self.graphe(monde_cand["jetons"], monde_cand["type_jeton"],
                             monde_cand["role_jeton"], monde_cand["masque_jeton"])
        pk, pc = _moyenne_masquee(rk, mk), _moyenne_masquee(rc, mc)
        if detache:
            pk, pc = pk.detach(), pc.detach()
        n = torch.stack([mk.to(pk.dtype).mean(1), mc.to(pk.dtype).mean(1)], dim=-1)
        s = self.tete_legere(torch.cat([pk, pc, n], dim=-1))
        return {"logit_replace": s[:, 0], "logit_doute": s[:, 1],
                "P_REPLACE_leger": torch.sigmoid(s[:, 0]),
                "marge_legere": (torch.sigmoid(s[:, 0]) - 0.5).abs() * 2.0}

    def nb_parametres(self) -> dict:
        return {
            "total": sum(p.numel() for p in self.parameters()),
            "graphe": sum(p.numel() for p in self.graphe.parameters()),
            "predicteur": sum(p.numel() for p in self.predicteur.parameters()),
            "tetes": sum(p.numel() for n, p in self.named_parameters()
                         if n.startswith("tete_")),
        }


# --------------------------------------------------------------------------
# Renversement du temps : le meme reseau, lu a l'envers
# --------------------------------------------------------------------------
def renverser_crop(crop: torch.Tensor) -> torch.Tensor:
    return crop.flip(1)


def renverser_monde(monde: dict, nb_trames_centre: int = len(IDX_CENTRE)) -> dict:
    """Renverse le temps DANS les jetons : `dt` change de signe, les degres
    entrant/sortant s'echangent (avec leurs bits de validite), et l'index de
    trame centrale se reflechit. Les poids sont partages."""
    jetons = monde["jetons"].clone()
    jetons[..., IDX_TRAIT["dt"]] = -jetons[..., IDX_TRAIT["dt"]]
    di, do = IDX_TRAIT["degre_in"], IDX_TRAIT["degre_out"]
    jetons[..., [di, do]] = jetons[..., [do, di]]
    jetons[..., [NB_TRAITS + di, NB_TRAITS + do]] = \
        jetons[..., [NB_TRAITS + do, NB_TRAITS + di]]
    noeuds = monde["noeuds_centre"].clone()
    noeuds[..., 0] = (nb_trames_centre - 1) - noeuds[..., 0]
    sortie = dict(monde)
    sortie["jetons"] = jetons
    sortie["noeuds_centre"] = noeuds
    return sortie


def preparer(teacher, crop: torch.Tensor, mondes: dict) -> dict:
    """Teacher UNE SEULE FOIS par sens, partage entre TOUS les mondes.

    C'est le `ENCODE ONCE` de n°114 a l'echelle de la composante : les pixels ne
    dependent pas de l'histoire, donc l'encodeur gele ne tourne pas deux fois.
    """
    with torch.no_grad():
        vis_av = teacher(crop)
        vis_ar = teacher(renverser_crop(crop))
    sortie = {"visuel_avant": vis_av, "visuel_arriere": vis_ar}
    for nom, monde in mondes.items():
        av = dict(monde)
        av["cible_noeuds"] = teacher.echantillonner(
            vis_av["carte_centre"], monde["noeuds_centre"])
        ar = renverser_monde(monde)
        ar["cible_noeuds"] = teacher.echantillonner(
            vis_ar["carte_centre"], ar["noeuds_centre"])
        sortie[nom] = {"avant": av, "arriere": ar}
    return sortie
