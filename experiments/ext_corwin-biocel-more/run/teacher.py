"""Le TEACHER VISUEL GELE : l'encodeur du UNet deploye (pack_ref).

Choix publies (n°113 §4.3 : teacher gele, pas d'EMA, pas de JEPA depuis zero) :

  - **couche** : `unet_out`, la sortie du decodeur du `TemporalUNet3D` du pack
    deploye, AVANT `detect_head` (32 canaux, pleine resolution de la grille du
    reseau). C'est la couche que la chaine consomme deja pour predire les
    aretes : ses features sont exactement le langage dans lequel le champion
    voit le film.
  - **dimension** : 32 canaux par voxel ; reduits par `adaptive_avg_pool3d` a
    une grille 3x3x3 par trame, soit 27 vecteurs de dimension 32 par trame.
  - **cout** : mesure par `mesurer_cout()` et publie au recu.

Le UNet tourne sur le CROP, pas sur la trame entiere : il est entierement
convolutif (plus une attention temporelle par voxel), donc le calcul est licite,
et il est ~1000x moins cher. La contrepartie est nommee : le champ receptif est
tronque au bord du crop, donc ces features ne sont pas bit-a-bit celles de la
chaine deployee. Elles n'ont pas a l'etre -- l'entrainement et l'inference du
referee utilisent la MEME fonction, et le teacher est gele dans les deux cas.

Le teacher ne recoit jamais autre chose que des pixels : aucun jeton de monde,
aucune statistique de film. La normalisation est faite par TRAME en amont.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

from schema_local import (
    CANAUX_TEACHER,
    GRILLE_CIBLE,
    IDX_CENTRE,
    IDX_CONTEXTE,
    NB_TRAMES,
)

# Emplacements connus du depot de la chaine figee. L'ORDRE compte : la variable
# d'environnement d'abord, puis Kaggle, puis les pods, puis le PC.
#
# Pourquoi la variable vient en premier. Cette liste etait faite de deux chemins
# de pod et d'un chemin Windows : aucun chemin Kaggle. Sur Kaggle le depot fige
# est clone par le noyau lui-meme dans `/kaggle/working/tracking_repo`, et
# `initialiser()` levait donc en production -- le referee abandonnait, KEEP TOTAL
# sur 200 films, APRES avoir paye l'inference entiere. Mes essais ne pouvaient
# pas le voir : ils tournent sur le pod, ou le premier chemin existe.
# La lecon est dans l'ordre : **l'appelant doit pouvoir DIRE ou il est** plutot
# que de dependre d'une liste en dur qui ne connait que les machines deja vues.
VARIABLE_PACK = "BIOCEL_PACK_REPO"
RACINES_PACK = (
    Path("/kaggle/working/tracking_repo"),
    Path("/kaggle/input/tracking_repo"),
    Path("/workspace/SPRINT/packs/pack_ref/repo"),
    Path("/root/pack_ref/repo"),
    Path("D:/Github/BIOCELL_WINNING/05_WORK/experiments/ZEUS/NUIT_2608/"
         "A1_JUGE/chaine_figee/pack_repo"),
)
POIDS_CONNUS = (
    Path("/workspace/SPRINT/packs/pack_ref/weights/unet_transformer/split_0/"
         "edge_predictor_best.pth"),
    Path("/root/pack_ref/weights/unet_transformer/split_0/edge_predictor_best.pth"),
)
SHA_POIDS_ATTENDU = "12f6881ee3620a831697ca098ff8f48e687a24225f4e048b538deec3562fe771"

CONFIG_DEFAUT = {
    "unet_out_channels": 32,
    "unet_layers": [32, 64, 128],
    "downsample": [1, 4, 4],
    "window_size": 2,
}


def _est_un_depot(r: Path) -> bool:
    return (Path(r) / "src" / "biohub_tracking" / "models"
            / "temporal_unet.py").exists()


def _trouver_racine(racines=RACINES_PACK) -> Path | None:
    """La variable d'environnement prime sur la liste en dur : elle permet a
    l'appelant de nommer une machine que cette liste ne connait pas."""
    env = os.environ.get(VARIABLE_PACK)
    if env and _est_un_depot(Path(env)):
        return Path(env)
    for r in racines:
        if _est_un_depot(r):
            return r
    return None


def importer_unet(racine: Path | None = None):
    """Importe `TemporalUNet3D` du depot fige. Ne le recopie jamais."""
    racine = racine or _trouver_racine()
    if racine is None:
        raise FileNotFoundError(
            "depot de la chaine figee introuvable. Cherche dans "
            f"${VARIABLE_PACK} (={os.environ.get(VARIABLE_PACK) or 'non pose'}) "
            "puis : " + ", ".join(str(r) for r in RACINES_PACK)
            + f". Pose {VARIABLE_PACK} ou passe racine_pack=... "
            "pour nommer une machine que cette liste ne connait pas."
        )
    src = str(racine / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    from biohub_tracking.models.temporal_unet import TemporalUNet3D  # noqa: E402
    return TemporalUNet3D


def sha256_fichier(chemin: Path, bloc: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as fh:
        while True:
            morceau = fh.read(bloc)
            if not morceau:
                break
            h.update(morceau)
    return h.hexdigest()


class TeacherGele(nn.Module):
    """Encodeur visuel gele. `requires_grad_(False)` et `eval()` en permanence.

    Sorties, pour un crop `(B, T, Z, Y, X)` deja normalise par trame :
      - `contexte` : `(B, len(IDX_CONTEXTE) * G^3, C)` -- ce que le predicteur voit ;
      - `cible`    : `(B, len(IDX_CENTRE)  * G^3, C)` -- ce qu'il doit predire ;
      - `carte_centre` : `(B, len(IDX_CENTRE), C, Z, Y, X)` pour echantillonner
        les cibles AUX POSITIONS des noeuds du monde.
    """

    def __init__(self, poids: Path | str | None = None,
                 racine_pack: Path | None = None,
                 config: dict | None = None,
                 verifier_sha: bool = True,
                 aleatoire_si_absent: bool = False):
        super().__init__()
        TemporalUNet3D = importer_unet(racine_pack)
        chemin = None
        if poids is not None:
            chemin = Path(poids)
        else:
            for p in POIDS_CONNUS:
                if p.exists():
                    chemin = p
                    break

        cfg = dict(CONFIG_DEFAUT)
        if chemin is not None and (chemin.parent / "config.json").exists():
            cfg.update(json.loads((chemin.parent / "config.json").read_text()))
        if config:
            cfg.update(config)
        self.config = cfg
        self.canaux = int(cfg["unet_out_channels"])

        self.unet = TemporalUNet3D(
            in_channels=1,
            out_channels=self.canaux,
            layers=cfg["unet_layers"],
            gradient_checkpointing=False,
        )
        self.sha_poids = None
        self.source_poids = None
        if chemin is not None and chemin.exists():
            self.sha_poids = sha256_fichier(chemin) if verifier_sha else None
            if verifier_sha and self.sha_poids != SHA_POIDS_ATTENDU:
                raise ValueError(
                    f"sha des poids inattendu : {self.sha_poids} "
                    f"(attendu {SHA_POIDS_ATTENDU}) -- reference non immuable"
                )
            etat = torch.load(chemin, map_location="cpu", weights_only=True)
            # Le point de sauvegarde porte tout `UNetNodeTransformer` ; on ne
            # garde que le tronc `unet.*` (le teacher n'est PAS la tete d'aretes).
            tronc = {k[len("unet."):]: v for k, v in etat.items() if k.startswith("unet.")}
            manquants, inattendus = self.unet.load_state_dict(tronc, strict=False)
            if manquants:
                raise ValueError(f"poids manquants dans le tronc UNet : {manquants[:5]}")
            self.source_poids = str(chemin)
        elif not aleatoire_si_absent:
            raise FileNotFoundError(
                "poids du pack_ref introuvables ; passe `aleatoire_si_absent=True` "
                "UNIQUEMENT pour un essai de formes (jamais pour une mesure)"
            )

        self.eval()
        for p in self.parameters():
            p.requires_grad_(False)

    def train(self, mode: bool = True):  # le teacher ne sort jamais d'eval
        return super().train(False)

    @torch.no_grad()
    def cartes(self, crop: torch.Tensor) -> torch.Tensor:
        """`(B, T, Z, Y, X)` -> `(B, T, C, Z, Y, X)` (sortie du decodeur)."""
        if crop.dim() != 5:
            raise ValueError(f"crop attendu (B, T, Z, Y, X), recu {tuple(crop.shape)}")
        fenetre = crop.unsqueeze(2)              # (B, T, 1, Z, Y, X)
        return self.unet(fenetre)                # (B, T, C, Z, Y, X)

    @staticmethod
    def _reduire(cartes: torch.Tensor, grille: int = GRILLE_CIBLE) -> torch.Tensor:
        """`(B, T, C, Z, Y, X)` -> `(B, T * grille^3, C)`."""
        B, T, C = cartes.shape[:3]
        plat = cartes.reshape(B * T, C, *cartes.shape[3:])
        red = F.adaptive_avg_pool3d(plat, (grille, grille, grille))
        return red.reshape(B, T, C, -1).permute(0, 1, 3, 2).reshape(B, -1, C)

    @torch.no_grad()
    def forward(self, crop: torch.Tensor,
                idx_contexte=IDX_CONTEXTE,
                idx_centre=IDX_CENTRE) -> dict:
        cartes = self.cartes(crop)
        ctx = self._reduire(cartes[:, list(idx_contexte)])
        cible = self._reduire(cartes[:, list(idx_centre)])
        return {
            "contexte": ctx,
            "cible": cible,
            "carte_centre": cartes[:, list(idx_centre)],
        }

    @staticmethod
    def echantillonner(carte_centre: torch.Tensor,
                       noeuds: torch.Tensor) -> torch.Tensor:
        """Features du teacher AUX POSITIONS des noeuds du monde.

        `carte_centre` : `(B, Tc, C, Z, Y, X)` ; `noeuds` : `(B, N, 4)` =
        `(index de trame centrale, z, y, x)` en voxels du crop, FLOTTANTS.
        Interpolation trilineaire (`grid_sample`), donc differentiable en
        position -- mais le teacher reste gele : c'est la CIBLE qui bouge.
        Rend `(B, N, C)`.
        """
        B, Tc, C, Z, Y, X = carte_centre.shape
        N = noeuds.shape[1]
        t_idx = noeuds[..., 0].round().long().clamp(0, Tc - 1)       # (B, N)
        # coordonnees normalisees dans [-1, 1] pour grid_sample (x, y, z)
        z = noeuds[..., 1] / max(Z - 1, 1) * 2 - 1
        y = noeuds[..., 2] / max(Y - 1, 1) * 2 - 1
        x = noeuds[..., 3] / max(X - 1, 1) * 2 - 1
        grille = torch.stack([x, y, z], dim=-1)                      # (B, N, 3)
        sortie = carte_centre.new_zeros(B, N, C)
        for t in range(Tc):
            sel = (t_idx == t)                                        # (B, N)
            if not bool(sel.any()):
                continue
            g = torch.where(sel.unsqueeze(-1), grille, torch.zeros_like(grille))
            g = g.reshape(B, N, 1, 1, 3)
            ech = F.grid_sample(carte_centre[:, t], g, mode="bilinear",
                                padding_mode="border", align_corners=True)
            ech = ech.reshape(B, C, N).permute(0, 2, 1)               # (B, N, C)
            sortie = torch.where(sel.unsqueeze(-1), ech, sortie)
        return sortie

    def fiche(self) -> dict:
        return {
            "couche": "unet_out (sortie du decodeur, avant detect_head)",
            "canaux": self.canaux,
            "grille_reduction": GRILLE_CIBLE,
            "nb_trames": NB_TRAMES,
            "idx_contexte": list(IDX_CONTEXTE),
            "idx_centre": list(IDX_CENTRE),
            "config": self.config,
            "sha_poids": self.sha_poids,
            "source_poids": self.source_poids,
            "parametres_geles": sum(p.numel() for p in self.parameters()),
        }


@torch.no_grad()
def mesurer_cout(teacher: TeacherGele, lot: int = 32, repetitions: int = 10,
                 appareil: str = "cuda") -> dict:
    """Cout du teacher par composante, mesure (pas estime)."""
    from schema_local import FORME_CROP
    dev = torch.device(appareil if appareil == "cpu" or (torch.cuda.is_available() and torch.cuda.device_count() > 0) else "cpu")
    teacher = teacher.to(dev)
    crop = torch.rand(lot, *FORME_CROP, device=dev)
    for _ in range(3):
        teacher(crop)
    if dev.type == "cuda":
        torch.cuda.synchronize()
    t0 = time.perf_counter()
    for _ in range(repetitions):
        teacher(crop)
    if dev.type == "cuda":
        torch.cuda.synchronize()
    dt = (time.perf_counter() - t0) / repetitions
    return {
        "appareil": str(dev),
        "lot": lot,
        "ms_par_lot": dt * 1e3,
        "ms_par_composante": dt * 1e3 / lot,
        "repetitions": repetitions,
    }
