# -*- coding: utf-8 -*-
"""REF-DATA -- LE CHARGEUR. Une fonction, et REF-MODEL n a plus rien a savoir.

    from referee_data import charge
    lot = charge(palier=60, split="train", familles=["W3_DUPLICATE"],
                 avec_crops=True, fold_embryon="A", lofo=None)

    lot.composantes          polars.DataFrame, une ligne par composante (SCHEMA s. 2)
    lot.n                    nombre de composantes
    lot.tokens(i)            np.float32 (n_tok, 22)   -- SCHEMA s. 4, <= 256 tokens
    lot.crop(i)              (img uint16 (7,19,19,19), valid uint8, q001[7], q999[7])
    lot.crop_normalise(i)    np.float32 (7,19,19,19)  -- normalisation CROPBANK_V0
    lot.label_bio(i)         +1 / -1 / 0
    lot.label_pay(i)         Delta exact du juge officiel, ou NaN

CE QUE LE CHARGEUR REFUSE DE DONNER, ET POURQUOI
  Il n expose AUCUN identifiant de film, AUCUN identifiant d embryon, AUCUN `t`
  absolu et AUCUNE position absolue dans `tokens()` ni dans `crop()`. Ces
  colonnes existent dans `lot.composantes` (traçabilité, splits, mesure) mais
  `tokens()` ne les lit pas. L identite de l embryon fuit a AUC 0,86 sur quatre
  statistiques de film : un referee qui reconnait l embryon ne transporte pas.
  `verifie_absence_de_fuite()` le controle et LEVE si une colonne interdite
  entre dans la matrice.

LA NORMALISATION DE REFERENCE est celle de FUNKE CROPBANK_V0
(`viewbank/banque.py::normalise_par_crop`), deja en service et reprise au bit de
`ff2e_data` : (x - mediane des voxels VALIDES) / (IQR des valides + 1e-6), clip
+-6, float32, 0 sur le padding. Son motif ecrit est notre regle : une
normalisation GLOBALE ferait entrer le niveau d intensite de l embryon dans le
tenseur. Le crop est stocke BRUT : les normalisations par trame, par image et
par film restent reproductibles depuis les quantiles de l index.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

import numpy as np

RACINE = pathlib.Path("/workspace/REFEREE/data")
SCHEMA_VERSION = "REFEREE-SCHEMA-v1"

# --- SCHEMA s. 4.1 : les sept types de tokens, dans cet ordre ---------------
TYPES = ("OBSERVATION", "VIE", "ARETE", "GAP", "DIVISION", "HIDDEN", "DUPLICATE")
TYPE_CODE = {n: i for i, n in enumerate(TYPES)}
# SCHEMA s. 4.2 : les 22 colonnes d un token, dans cet ordre. Il ne bouge pas.
COLONNES_TOKEN = (
    "type", "monde", "dt",
    "dz_um", "dy_um", "dx_um",
    "role", "prob", "prob_2", "marge", "support",
    "courbure_z", "courbure_y", "courbure_x",
    "degre_in", "degre_out", "longueur_um", "duree",
    "dist_ppv_um", "densite_7um", "rang", "presence",
)
N_COL_TOKEN = len(COLONNES_TOKEN)
TOP_K_MAX = 256          # lifetwin.contracts.contrats.TOP_K_MAX
SEUIL_DUPLICATE_UM = 7.0  # la PORTE DU JUGE, pas 5 um (voir tokens())

# CONVENTION DE NULLITE, heritee de CIBLAGE et rendue explicite (ordre ZEUS 3) :
# une preuve locale `p_*` vaut NaN quand il n y a RIEN a medianer -- jamais 0.
# Zero est une valeur mesuree (une densite nulle, un deplacement nul) ; NaN est
# une absence de mesure. Chaque consommateur impute EXPLICITEMENT et ajoute un
# indicateur de nullite ; le chargeur n impute jamais a votre place.
IMPUTATION = "aucune : NaN reste NaN, le consommateur impute et publie son indicateur"
ROLE_CODE = {"garde": 0, "retire": 1, "ajoute": 2, "deplace": 3,
             "commune": 4, "keep_seule": 5, "cand_seule": 6}

# Colonnes qui ne doivent JAMAIS entrer dans une matrice d entree.
INTERDITES = ("film", "embryon", "comp_key", "comp_uid", "t", "t_min", "t_max",
              "t_centre", "z_um", "y_um", "x_um", "centre_z_um", "centre_y_um",
              "centre_x_um", "centre_z_vox", "centre_y_vox", "centre_x_vox",
              "source_monde_keep", "source_monde_cand", "label_pay", "label_bio",
              "split", "palier")


class Lot:
    def __init__(self, comp, nodes, edges, index_crops, racine, palier, split):
        self.composantes = comp
        self._nodes = nodes
        self._edges = edges
        self._index = index_crops
        self._racine = pathlib.Path(racine)
        self._palier = palier
        self._split = split
        self._memmap: dict[str, tuple] = {}
        self._uid = list(comp["comp_uid"]) if comp.height else []
        self._pos = {u: i for i, u in enumerate(self._uid)}
        self._n_par_uid = None
        self._e_par_uid = None
        self._crop_par_uid = None

    # ------------------------------------------------------------------ base
    @property
    def n(self) -> int:
        return self.composantes.height

    def label_bio(self, i: int) -> int:
        return int(self.composantes["label_bio"][i])

    def label_pay(self, i: int) -> float:
        return float(self.composantes["label_pay"][i])

    # ---------------------------------------------------------------- tokens
    def _groupes(self):
        if self._n_par_uid is None:
            self._n_par_uid = {}
            if self._nodes is not None and self._nodes.height:
                for u, sous in self._nodes.group_by("comp_uid"):
                    cle = u[0] if isinstance(u, tuple) else u
                    self._n_par_uid[cle] = sous
            self._e_par_uid = {}
            if self._edges is not None and self._edges.height:
                for u, sous in self._edges.group_by("comp_uid"):
                    cle = u[0] if isinstance(u, tuple) else u
                    self._e_par_uid[cle] = sous
        return self._n_par_uid, self._e_par_uid

    def tokens(self, i: int) -> np.ndarray:
        """La sequence de tokens d une composante, SCHEMA s. 4.

        Ordre CANONIQUE et deterministe : tri par (monde, type, dt, dz, dy, dx).
        Le modele ne doit pas pouvoir lire l ordre de generation. Tronque a
        TOP_K_MAX par distance croissante au centre ; `presence` vaut 1 pour un
        token reel et 0 pour un remplissage.
        """
        nu, eu = self._groupes()
        uid = self._uid[i]
        lignes = []

        n = nu.get(uid)
        if n is not None:
            for r in n.iter_rows(named=True):
                deg_out = int(r.get("degre_out") or 0)
                typ = TYPE_CODE["DIVISION"] if deg_out >= 2 else TYPE_CODE["OBSERVATION"]
                lignes.append([
                    typ, float(r["monde"]), float(r["dt"]),
                    r["dz_um"], r["dy_um"], r["dx_um"],
                    float(ROLE_CODE.get(r.get("role", "garde"), 0)),
                    _f(r.get("edge_prob_out")), _f(r.get("edge_prob_out_2")),
                    _f(r.get("edge_prob_out")) - _f(r.get("edge_prob_out_2")),
                    _f(r.get("support_image")),
                    _f(r.get("colline_courbure_z")), _f(r.get("colline_courbure_y")),
                    _f(r.get("colline_courbure_x")),
                    float(r.get("degre_in") or 0), float(deg_out),
                    0.0, 0.0,
                    _f(r.get("dist_ppv_um")), _f(r.get("densite_7um")),
                    0.0, 1.0,
                ])
        # --- jeton DUPLICATE (ordre ZEUS 1) -----------------------------
        # Le seuil est 7,0 um, LA PORTE DU JUGE, et non 5 um : la distribution
        # mesuree des doublons REELS (DUPLICATE_FUSION, n=2 596) a une mediane
        # de 5,702 um et 71,69 pct de sa masse AU-DESSUS de 5 um. Un seuil a
        # 5 um ne verrait que 28 pct des doublons que le monde contient
        # vraiment. Meme seuil pour l emission des jetons et pour les
        # composantes : un objet, un seuil.
        if n is not None and n.height > 1:
            R = n.select(["monde", "dt", "dz_um", "dy_um", "dx_um"]).to_numpy()
            for x in range(len(R)):
                for y in range(x + 1, len(R)):
                    if R[x, 0] != R[y, 0] or R[x, 1] != R[y, 1]:
                        continue          # meme monde ET meme trame seulement
                    d = float(np.linalg.norm(R[x, 2:5] - R[y, 2:5]))
                    if d > SEUIL_DUPLICATE_UM:
                        continue
                    lignes.append([
                        TYPE_CODE["DUPLICATE"], float(R[x, 0]), float(R[x, 1]),
                        float((R[x, 2] + R[y, 2]) / 2.0),
                        float((R[x, 3] + R[y, 3]) / 2.0),
                        float((R[x, 4] + R[y, 4]) / 2.0),
                        float(ROLE_CODE["garde"]),
                        np.nan, np.nan, np.nan, np.nan,
                        np.nan, np.nan, np.nan,
                        0.0, 0.0, d, 0.0,
                        np.nan, np.nan, 0.0, 1.0,
                    ])

        e = eu.get(uid)
        if e is not None:
            for r in e.iter_rows(named=True):
                dt = int(r.get("dt") or 1)
                typ = TYPE_CODE["GAP"] if abs(dt) > 1 else TYPE_CODE["ARETE"]
                lignes.append([
                    typ, float(r["monde"]), float(dt),
                    0.0, 0.0, 0.0,
                    float(ROLE_CODE.get(r.get("role", "commune"), 4)),
                    _f(r.get("prob")), np.nan, np.nan, np.nan,
                    np.nan, np.nan, np.nan,
                    0.0, 0.0, _f(r.get("longueur_um")), 0.0,
                    np.nan, np.nan, 0.0, 1.0,
                ])

        if not lignes:
            return np.zeros((0, N_COL_TOKEN), dtype=np.float32)
        M = np.asarray(lignes, dtype=np.float32)
        # tri canonique : (monde, type, dt, dz, dy, dx)
        ordre = np.lexsort((M[:, 5], M[:, 4], M[:, 3], M[:, 2], M[:, 0], M[:, 1]))
        M = M[ordre]
        if len(M) > TOP_K_MAX:
            d = np.nan_to_num(np.linalg.norm(M[:, 3:6], axis=1), nan=1e9)
            garde = np.sort(np.argsort(d)[:TOP_K_MAX])
            M = M[garde]
        M[:, COLONNES_TOKEN.index("rang")] = np.arange(len(M), dtype=np.float32)
        return M

    # ----------------------------------------------------------------- crops
    def _crops(self):
        if self._crop_par_uid is None:
            self._crop_par_uid = {}
            if self._index is not None and self._index.height:
                for r in self._index.iter_rows(named=True):
                    self._crop_par_uid[r["crop_uid"]] = r
        return self._crop_par_uid

    def _pile(self, shard: str):
        if shard not in self._memmap:
            d = self._racine / "crops" / str(self._palier) / self._split
            img = np.load(d / f"{shard}.img.npy", mmap_mode="r")
            val = np.load(d / f"{shard}.valid.npy", mmap_mode="r")
            self._memmap[shard] = (img, val)
        return self._memmap[shard]

    def _crop_uid(self, i: int) -> str:
        """L identifiant du crop d une composante.

        Il se LIT dans la colonne `crop_uid` quand elle existe, et se RECALCULE
        sinon a partir de (film, t_centre, centre en voxels natifs) -- meme
        formule que `crops.py`, au chiffre pres. Les premiers shards ont ete
        ecrits sans cette colonne ; les recalculer ici evite de les regenerer.
        """
        c = self.composantes
        if "crop_uid" in c.columns:
            return c["crop_uid"][i]
        cle = "%s|%d|%.3f|%.3f|%.3f" % (
            c["film"][i], int(c["t_centre"][i]), float(c["centre_z_vox"][i]),
            float(c["centre_y_vox"][i]), float(c["centre_x_vox"][i]))
        return hashlib.sha1(cle.encode()).hexdigest()[:16]

    def crop(self, i: int):
        """(img uint16, valid uint8, q001[7], q999[7]) ou None si sans crop."""
        uid = self._crop_uid(i)
        r = self._crops().get(uid)
        if r is None:
            return None
        img, val = self._pile(r["shard"])
        return (np.asarray(img[r["row"]]), np.asarray(val[r["row"]]),
                np.asarray(r["q001"], dtype=np.float32),
                np.asarray(r["q999"], dtype=np.float32))

    def crop_normalise(self, i: int):
        """CROPBANK_V0 `normalise_par_crop`, au bit : (x - mediane_valide) /
        (IQR_valide + 1e-6), clip +-6, float32, 0 sur le padding. Rend None si
        moins de 1000 voxels valides -- le refus est celui du canon."""
        c = self.crop(i)
        if c is None:
            return None
        img, val, _, _ = c
        m = val.astype(bool)
        if int(m.sum()) < 1000:
            return None
        v = img[m].astype(np.float32)
        med = float(np.median(v))
        q1, q3 = np.quantile(v, [0.25, 0.75])
        iqr = float(q3 - q1)
        x = (img.astype(np.float32) - med) / (iqr + 1e-6)
        np.clip(x, -6.0, 6.0, out=x)
        x[~m] = 0.0
        return x

    # ------------------------------------------------------------- controles
    def verifie_absence_de_fuite(self) -> dict:
        """Le contrôle D4/C5 : aucune colonne interdite ne peut entrer dans une
        matrice d entree. LEVE si `COLONNES_TOKEN` en contient une."""
        fautives = [c for c in COLONNES_TOKEN if c in INTERDITES]
        if fautives:
            raise SystemExit("colonnes interdites dans les tokens : %s" % fautives)
        return {"colonnes_token": list(COLONNES_TOKEN),
                "n_colonnes": N_COL_TOKEN,
                "interdites_absentes": True,
                "top_k_max": TOP_K_MAX}


def _f(x) -> float:
    return float("nan") if x is None else float(x)


# ------------------------------------------------------------------- charge
def charge(palier: int = 60, split: str | None = None, familles=None,
           avec_crops: bool = True, fold_embryon: str | None = None,
           lofo: str | None = None, racine=RACINE, split_crops: str = "all") -> Lot:
    """Le lot demande. Aucune GT n est lue ; aucune fuite n est possible par
    construction (voir `Lot.verifie_absence_de_fuite`).

    `split`         "train" | "val" | "test" | None (tout) -- decoupe PAR FILM
    `familles`      liste de familles, ou None (toutes celles presentes)
    `fold_embryon`  "A" (apprend 44b6, juge 6bba) | "B" (l inverse) | None
    `lofo`          famille a EXCLURE de l apprentissage (leave-one-family-out)
    """
    import polars as pl
    racine = pathlib.Path(racine)
    d = racine / "composantes" / str(palier)
    fichiers = sorted(d.glob("*.comp.parquet"))
    if familles:
        fichiers = [p for p in fichiers
                    if p.name.split(".comp.")[0] in set(familles)]
    if not fichiers:
        raise SystemExit(f"aucune composante sous {d}")
    comp = pl.concat([pl.read_parquet(p) for p in fichiers], how="diagonal")

    sp = racine / "splits" / str(palier) / "SPLITS.json"
    par_film = {}
    if sp.is_file():
        par_film = json.loads(sp.read_text(encoding="utf-8"))["split_par_film"]
    comp = comp.with_columns(
        pl.col("film").replace_strict(par_film, default="inconnu").alias("split"))

    if split:
        comp = comp.filter(pl.col("split") == split)
    if lofo:
        comp = comp.filter(pl.col("famille") != lofo)
    if fold_embryon in ("A", "B"):
        embryons = sorted(set(comp["embryon"])) if comp.height else []
        if len(embryons) == 2:
            garde = embryons[0] if fold_embryon == "A" else embryons[1]
            comp = comp.filter(pl.col("embryon") == garde)
    if "holdout_naturel" in comp.columns and split in ("train", "val"):
        comp = comp.filter(~pl.col("holdout_naturel"))

    uids = set(comp["comp_uid"]) if comp.height else set()
    nodes = edges = None
    for p in fichiers:
        fam = p.name.split(".comp.")[0]
        pn = d / f"{fam}.nodes.parquet"
        pe = d / f"{fam}.edges.parquet"
        if pn.is_file():
            x = pl.read_parquet(pn).filter(pl.col("comp_uid").is_in(uids))
            nodes = x if nodes is None else pl.concat([nodes, x], how="diagonal")
        if pe.is_file():
            x = pl.read_parquet(pe).filter(pl.col("comp_uid").is_in(uids))
            edges = x if edges is None else pl.concat([edges, x], how="diagonal")

    index = None
    if avec_crops:
        pi = racine / "crops" / str(palier) / split_crops / "INDEX.parquet"
        if pi.is_file():
            index = pl.read_parquet(pi)
            if comp.height:
                if "crop_uid" in comp.columns:
                    garde = set(comp["crop_uid"])
                else:
                    garde = {hashlib.sha1(
                        ("%s|%d|%.3f|%.3f|%.3f" % (f, int(t), float(z), float(y),
                                                   float(x))).encode()).hexdigest()[:16]
                        for f, t, z, y, x in zip(
                            comp["film"], comp["t_centre"], comp["centre_z_vox"],
                            comp["centre_y_vox"], comp["centre_x_vox"])}
                index = index.filter(pl.col("crop_uid").is_in(garde))

    lot = Lot(comp, nodes, edges, index, racine, palier, split_crops)
    lot.verifie_absence_de_fuite()
    return lot


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--palier", type=int, default=60)
    ap.add_argument("--split", default=None)
    ap.add_argument("--familles", nargs="*", default=None)
    ap.add_argument("--racine", default=str(RACINE))
    a = ap.parse_args()
    lot = charge(palier=a.palier, split=a.split, familles=a.familles,
                 racine=a.racine)
    print(json.dumps({
        "schema_version": SCHEMA_VERSION,
        "n_composantes": lot.n,
        "colonnes": lot.composantes.columns,
        "par_famille": {k: int(v) for k, v in
                        zip(*[list(x) for x in
                              lot.composantes["famille"].value_counts()
                              .to_dict(as_series=False).values()])}
        if lot.n else {},
        "controle_fuite": lot.verifie_absence_de_fuite(),
    }, ensure_ascii=False)[:2000])
    if lot.n:
        M = lot.tokens(0)
        print("tokens[0] :", M.shape, "colonnes", N_COL_TOKEN)
        c = lot.crop(0)
        print("crop[0] :", None if c is None else (c[0].shape, c[0].dtype,
                                                   int(c[1].sum())))


# --------------------------------------------------------------- pandas
def charger(split: str | None = None, famille: str | None = None,
            palier: int = 60, racine=RACINE, split_crops: str = "all"):
    """Ordre ZEUS 6 : la porte pandas, pour que polars ne soit jamais la SEULE.

    Rend `(df, crops)` :
      `df`     pandas.DataFrame, une ligne par composante (SCHEMA s. 2)
      `crops`  dict decrivant les piles memmap :
               {"index": <chemin INDEX.parquet>, "racine": <dossier des shards>,
                "forme": (7, 19, 19, 19), "dtype": "uint16",
                "shards": {<nom>: {"img": <chemin .img.npy>,
                                   "valid": <chemin .valid.npy>}}}
    Les tableaux ne sont PAS charges : `np.load(chemin, mmap_mode="r")[row]`
    donne un crop sans lire le shard entier.
    """
    lot = charge(palier=palier, split=split,
                 familles=[famille] if famille else None,
                 avec_crops=True, racine=racine, split_crops=split_crops)
    df = lot.composantes.to_pandas()
    d = pathlib.Path(racine) / "crops" / str(palier) / split_crops
    shards = {}
    if d.is_dir():
        for p in sorted(d.glob("*.img.npy")):
            nom = p.name[: -len(".img.npy")]
            shards[nom] = {"img": str(p), "valid": str(d / f"{nom}.valid.npy")}
    return df, {"index": str(d / "INDEX.parquet"), "racine": str(d),
                "forme": (7, 19, 19, 19), "dtype": "uint16",
                "normalisation": "CROPBANK_V0 : (x - mediane_valide)/(IQR_valide + 1e-6), clip +-6, 0 sur le padding",
                "shards": shards}
