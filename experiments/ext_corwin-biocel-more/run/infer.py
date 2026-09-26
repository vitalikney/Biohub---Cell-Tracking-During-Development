"""`infer.py` -- le referee dans le noyau Kaggle. Autonome, sans pip, sans surprise.

Contrat (ZEUS 12:4xZ + REGLAGES-A) :
  entree  : `composantes_<film>.parquet` (produit sur place par le generateur de
            REF-DATA) + le chemin du zarr du film + les poids du pack_ref, tous
            deja dans le dataset ;
  sortie  : `decisions_<film>.parquet` -- `comp_id, famille, P_KEEP, P_REPLACE,
            P_ABSTAIN, E_keep, E_cand, U` ;
  echec   : TOUTE exception -> AUCUNE decision ecrite -> la cellule garde KEEP.
            Le referee ne peut donc pas faire perdre de score en tombant.

Quatre contraintes mecaniques, et comment elles sont tenues :
  1. **importable sans effet de bord** (le travailleur part en `spawn`, la
     cellule 06 a deja un contexte CUDA) : ce module ne charge RIEN a l'import.
     Ni poids, ni `.cuda()`, ni allocation. Tout passe par `initialiser()`.
  2. **respawn propre** : l'etat vit dans un unique dictionnaire de module,
     `_ETAT`, remis a zero par `liberer()`. Apres un `terminate`, le processus
     neuf rappelle `initialiser()` et reconstruit son contexte CUDA lui-meme.
     Aucun handle CUDA n'est capture dans une variable globale hors `_ETAT`.
  3. **previsible plutot que robuste** : le budget est applique par film en
     amont ; ce module publie son cout mesure et ne se defend pas d'un
     depassement -- il est tue et le film reste KEEP.
  4. **rien n'est reecrit** : les crops sont decoupes par `crops.Trames` de
     REF-DATA (grille du UNet, quantiles par trame) et les jetons par
     `referee_data.Lot.tokens`. Si l'un des deux manque, on ne devine pas : on
     rend un echec, donc KEEP.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time

import numpy as np

# --- AUCUN import lourd au niveau module : torch est importe dans initialiser()
_ETAT: dict = {}

RAYON = 9
DEMI_T = 3
COTE = 2 * RAYON + 1
N_TRAMES = 2 * DEMI_T + 1
SOUS = 4
COLONNES_SORTIE = ("comp_id", "famille", "P_KEEP", "P_REPLACE", "P_ABSTAIN",
                   "E_keep", "E_cand", "U")


def _chemins_impl(sup=None):
    c = [sup] if sup else []
    c += ["/kaggle/input/referee/impl", "/workspace/REFEREE/impl",
          str(pathlib.Path(__file__).resolve().parent),
          str(pathlib.Path(__file__).resolve().parent.parent / "impl")]
    return [x for x in c if x]


def initialiser(modele_pt: str, poids_teacher: str, *, appareil: str = "cuda",
                impl_refdata: str | None = None, impl_modele: str | None = None,
                bf16: bool = True, seuil_marge: float = 0.30,
                tout_vision: bool = False, seuils: dict | None = None,
                vision_max: int | None = None,
                budget_film_s: float | None = None,
                racine_pack: str | None = None) -> dict:
    """Charge une fois par travailleur. Rend une fiche (jamais les objets)."""
    import torch

    for c in _chemins_impl(impl_refdata) + _chemins_impl(impl_modele):
        if c not in sys.path:
            sys.path.insert(0, c)

    import schema_local as S
    from referee import LifeReferee
    from teacher import TeacherGele

    dev = torch.device(appareil if (appareil == "cpu" or
                                    (torch.cuda.is_available() and
                                     torch.cuda.device_count() > 0)) else "cpu")
    pt = torch.load(modele_pt, map_location="cpu", weights_only=False)
    cfg = pt.get("config", {})
    modele = LifeReferee(
        d=cfg.get("d", 256), tetes=cfg.get("tetes", 8),
        blocs_graphe=cfg.get("blocs_graphe", 4),
        blocs_predicteur=cfg.get("blocs_predicteur", 4),
        ffn=cfg.get("ffn", 1024), chute=0.0, taux_masque_contexte=0.0)
    modele.load_state_dict(pt["modele"])
    modele.eval().to(dev)
    teacher = TeacherGele(poids=poids_teacher,
                          racine_pack=(pathlib.Path(racine_pack)
                                       if racine_pack else None)).eval().to(dev)

    _ETAT.clear()
    _ETAT.update({
        "torch": torch, "S": S, "modele": modele, "teacher": teacher,
        "dev": dev, "bf16": bool(bf16 and dev.type == "cuda"),
        "seuil_marge": float(seuil_marge), "tout_vision": bool(tout_vision),
        "seuils": dict(seuils or {}),
        "vision_max": (int(vision_max) if vision_max else None),
        "budget_film_s": (float(budget_film_s) if budget_film_s else None),
        "sha_schema": S.sha_schema(), "sha_teacher": teacher.sha_poids,
        "parametres": modele.nb_parametres()["total"],
        "pas_entrainement": pt.get("pas"), "epoque": pt.get("epoque"),
    })
    return {k: _ETAT[k] for k in ("sha_schema", "sha_teacher", "parametres",
                                  "pas_entrainement", "epoque", "bf16")} | \
        {"appareil": str(dev)}


def liberer() -> None:
    """Rend l'etat vide. Un travailleur respawne repart de zero."""
    t = _ETAT.get("torch")
    _ETAT.clear()
    if t is not None:
        try:
            t.cuda.empty_cache()
        except Exception:
            pass


# --------------------------------------------------------------------------
def _lot_polars(dossier: pathlib.Path, film: str | None):
    """Reconstruit un `referee_data.Lot` sans crops : ses jetons font foi."""
    import polars as pl
    from referee_data import Lot

    comps = sorted(dossier.glob("*.comp.parquet"))
    if not comps:
        comps = sorted(dossier.glob(f"composantes_{film}.parquet")) if film else []
    if not comps:
        raise FileNotFoundError(f"aucun catalogue de composantes sous {dossier}")
    comp = pl.concat([pl.read_parquet(p) for p in comps], how="diagonal")
    if film and "film" in comp.columns:
        comp = comp.filter(pl.col("film") == film)
    nodes = edges = None
    for p in comps:
        base = p.name.split(".comp.")[0]
        pn, pe = dossier / f"{base}.nodes.parquet", dossier / f"{base}.edges.parquet"
        if pn.is_file():
            x = pl.read_parquet(pn)
            nodes = x if nodes is None else pl.concat([nodes, x], how="diagonal")
        if pe.is_file():
            x = pl.read_parquet(pe)
            edges = x if edges is None else pl.concat([edges, x], how="diagonal")
    if nodes is not None and comp.height:
        uids = set(comp["comp_uid"])
        nodes = nodes.filter(pl.col("comp_uid").is_in(uids))
        if edges is not None:
            edges = edges.filter(pl.col("comp_uid").is_in(uids))
    return Lot(comp, nodes, edges, None, dossier, 0, None), comp


def _trames_du_film(film: str, zarr_dir: str, trames_utiles, fils: int = 4):
    """Lit les trames demandees EN PARALLELE, une seule fois chacune.

    Le chunk zarr est `(1, 64, 256, 256)` : une trame entiere est UN bloc
    compresse. Lire une ROI de 19x19x19 decompresse donc la trame complete et
    ne fait economiser RIEN -- mesure : 7,8 ms par ROI, soit 12,8 s pour 1 650
    ROI, contre 7,8 s pour lire les 100 trames une fois. La seule accélération
    possible est donc de decompresser PLUSIEURS TRAMES A LA FOIS : zstd rend le
    GIL, un pool de fils passe a l'echelle des vCPU disponibles.
    """
    import zarr
    from concurrent.futures import ThreadPoolExecutor
    g = zarr.open_group(str(pathlib.Path(zarr_dir) / f"{film}.zarr"), mode="r")
    arr = g["0"]
    T = int(arr.shape[0])
    utiles = sorted({min(max(int(t), 0), T - 1) for t in trames_utiles})

    def _une(t):
        v = np.asarray(arr[t, ::1, ::SOUS, ::SOUS])
        if v.dtype != np.uint16:
            v = np.clip(v, 0, 65535).astype(np.uint16)
        q = np.quantile(v, [0.001, 0.999])
        return t, v, float(q[0]), float(q[1])

    trames, quantiles = {}, {}
    with ThreadPoolExecutor(max_workers=max(1, fils)) as ex:
        for t, v, q0, q1 in ex.map(_une, utiles):
            trames[t] = v
            quantiles[t] = (q0, q1)
    forme = tuple(int(x) for x in arr.shape[1:])
    return trames, quantiles, T, forme


def normaliser_cropbank_v0(img: np.ndarray, valide: np.ndarray) -> np.ndarray:
    """La normalisation CANON de REF-DATA (`referee_data.crop_normalise`).

        (x - mediane des voxels valides) / (IQR des valides + 1e-6),
        clip +-6, 0 sur le remplissage, refus sous 1 000 voxels valides.

    Elle est PUREMENT LOCALE au crop : aucune constante de film, donc aucun
    canal de fuite d'embryon. C'est la SEULE normalisation du projet -- la
    normalisation par trame que ce fichier appliquait auparavant donnait des
    crops dans [0, 1] la ou l'ecole officielle donne des crops dans [-6, 6].
    Entrainer sur l'une et inferer sur l'autre aurait produit des decisions
    plausibles et fausses, sans qu'aucun controle ne le dise.
    """
    m = valide.astype(bool)
    n = int(m.sum())
    if n < 1000:
        return np.zeros_like(img, dtype=np.float32)
    v = img[m].astype(np.float32)
    med = float(np.median(v))
    q1, q3 = np.quantile(v, [0.25, 0.75])
    x = (img.astype(np.float32) - med) / (float(q3 - q1) + 1e-6)
    np.clip(x, -6.0, 6.0, out=x)
    x[~m] = 0.0
    return x


def _centre_unet(r) -> tuple:
    """Le centre sur la grille du UNet, quelle que soit la forme du catalogue.

    Les composantes portent `centre_{z,y,x}_vox` ; les corruptions portent un
    seul champ `centre_zyx_vox`. Une seule fonction lit les deux, sinon la
    convention de centrage se dedouble et derive.
    """
    if "centre_z_vox" in r:
        z, y, x = r["centre_z_vox"], r["centre_y_vox"], r["centre_x_vox"]
    else:
        z, y, x = (float(v) for v in r["centre_zyx_vox"])
    return int(round(float(z))), int(round(float(y) / SOUS)), int(round(float(x) / SOUS))


def _crops(film: str, zarr_dir: str, comp, indices=None, fils: int = 4) -> np.ndarray:
    """Decoupe les crops, en respectant la convention de `crops.Trames`.

    `indices` : les seules lignes dont on veut le crop (l'etage leger a deja
    ecarte les autres). En rendre 1 650 en float32 couterait 317 Mo par film
    pour rien.
    """
    lignes = comp.to_dicts()
    if indices is None:
        indices = list(range(len(lignes)))
    besoins = set()
    for i in indices:
        tc = int(lignes[i]["t_centre"])
        besoins.update(range(tc - DEMI_T, tc + DEMI_T + 1))
    trames, quantiles, T, forme = _trames_du_film(film, zarr_dir, besoins, fils)
    Z, Y, X = forme
    GY, GX = (Y + SOUS - 1) // SOUS, (X + SOUS - 1) // SOUS
    sortie = np.zeros((len(indices), N_TRAMES, COTE, COTE, COTE), dtype=np.float32)
    for j, i in enumerate(indices):
        r = lignes[i]
        cz, cy, cx = _centre_unet(r)
        img = np.zeros((N_TRAMES, COTE, COTE, COTE), dtype=np.float32)
        val = np.zeros((N_TRAMES, COTE, COTE, COTE), dtype=bool)
        for k in range(N_TRAMES):
            t = int(r["t_centre"]) + (k - DEMI_T)
            tc = min(max(t, 0), T - 1)             # replication de la trame de bord
            v = trames.get(tc)
            if v is None:
                continue
            q0, q1 = quantiles[tc]
            z0, y0, x0 = cz - RAYON, cy - RAYON, cx - RAYON
            sz0, sy0, sx0 = max(z0, 0), max(y0, 0), max(x0, 0)
            sz1, sy1, sx1 = min(z0 + COTE, Z), min(y0 + COTE, GY), min(x0 + COTE, GX)
            if sz1 <= sz0 or sy1 <= sy0 or sx1 <= sx0:
                continue
            bloc = v[sz0:sz1, sy0:sy1, sx0:sx1].astype(np.float32)
            img[k, sz0 - z0:sz1 - z0, sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = bloc
            val[k, sz0 - z0:sz1 - z0, sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = True
        sortie[j] = normaliser_cropbank_v0(img, val)
    return sortie


def traiter_film(film: str, dossier_composantes: str, zarr_dir: str,
                 sortie_dir: str, *, lot: int = 64, fils: int = 4,
                 impl_refdata: str | None = None) -> dict:
    """Un film -> `decisions_<film>.parquet`. Toute exception = AUCUNE decision.

    L'ordre des etapes est dicte par le budget (6 ms par objet a la borne haute
    de 1 650 anomalies par film) :
      1. jetons de TOUS les objets (CPU, aucune image lue) ;
      2. etage LEGER sur tous, par lots (0,0985 ms par objet sur 4090) ;
      3. les seules trames dont les objets RETENUS ont besoin sont lues, en
         parallele (le chunk zarr est une trame entiere : lire une ROI ne fait
         economiser RIEN, decompresser a plusieurs fils fait tout) ;
      4. etage VISION sur le sous-ensemble retenu seulement.
    Lire l'image de 1 650 objets pour n'en juger que 7 % couterait 317 Mo et
    plusieurs secondes pour rien.

    Le fichier de decisions est ecrit A LA FIN DE CE FILM, jamais a la fin de
    tous : un depassement coute ce film, pas les 200.
    """
    t0 = time.perf_counter()
    fiche = {"film": film, "statut": "echec", "n_composantes": 0,
             "n_vision": 0, "n_trames_lues": 0, "secondes": 0.0,
             "secondes_jetons": 0.0, "secondes_leger": 0.0,
             "secondes_crops": 0.0, "secondes_vision": 0.0,
             "fichier": None, "erreur": None}
    try:
        if not _ETAT:
            raise RuntimeError("initialiser() n'a pas ete appele dans ce processus")
        torch = _ETAT["torch"]
        S = _ETAT["S"]
        from referee import preparer
        from referee_data import COLONNES_TOKEN

        lot_rd, comp = _lot_polars(pathlib.Path(dossier_composantes), film)
        n = comp.height
        fiche["n_composantes"] = int(n)
        if n == 0:
            fiche.update(statut="vide", secondes=time.perf_counter() - t0)
            return fiche

        dev, modele, teacher = _ETAT["dev"], _ETAT["modele"], _ETAT["teacher"]
        ctx = (torch.autocast(device_type="cuda", dtype=torch.bfloat16)
               if _ETAT["bf16"] else torch.autocast(device_type="cpu", enabled=False))
        familles = list(comp["famille"]) if "famille" in comp.columns else [""] * n
        ids = list(comp["comp_uid"]) if "comp_uid" in comp.columns else list(range(n))
        if "sous_type" in comp.columns:
            sous_type = list(comp["sous_type"])
        elif "corr_type" in comp.columns:
            sous_type = list(comp["corr_type"])
        else:
            sous_type = familles

        # --- 1. jetons (aucune image lue)
        t = time.perf_counter()
        blocs = []
        for i in range(n):
            jet = lot_rd.tokens(i)
            k = S.adapter_jetons(jet, COLONNES_TOKEN, monde=0)
            c = S.adapter_jetons(jet, COLONNES_TOKEN, monde=1)
            part = S.noeuds_partages(jet, COLONNES_TOKEN)
            for m, bloc in ((0, k), (1, c)):
                bloc["noeuds_centre"] = part["noeuds_centre"]
                bloc["masque_noeuds"] = part["masque_noeuds"]
                bloc["affirme_noeuds"] = part["affirme"][m]
            blocs.append((k, c))
        fiche["secondes_jetons"] = time.perf_counter() - t

        cles = ("jetons", "type_jeton", "role_jeton", "masque_jeton",
                "noeuds_centre", "masque_noeuds", "affirme_noeuds")

        def _mondes(indices):
            sortie = {}
            for j, nom in ((0, "keep"), (1, "cand")):
                sortie[nom] = {
                    cle: torch.from_numpy(
                        np.stack([blocs[i][j][cle] for i in indices])).to(dev)
                    for cle in cles}
            return sortie

        # --- 2. etage LEGER sur TOUS les objets
        t = time.perf_counter()
        marge = np.zeros(n, dtype=np.float32)
        with torch.no_grad():
            for d0 in range(0, n, lot):
                idx = list(range(d0, min(d0 + lot, n)))
                m = _mondes(idx)
                with ctx:
                    lg = modele.leger(m["keep"], m["cand"])
                marge[idx] = lg["marge_legere"].float().cpu().numpy()
        fiche["secondes_leger"] = time.perf_counter() - t

        seuils = _ETAT.get("seuils") or {}
        defaut = float(seuils.get("defaut", _ETAT["seuil_marge"]))
        seuil_de = np.array([float(seuils.get(str(sous_type[i]), defaut))
                             for i in range(n)], dtype=np.float32)
        vision = (np.ones(n, dtype=bool) if _ETAT["tout_vision"]
                  else (marge < seuil_de))
        retenus = [int(i) for i in np.where(vision)[0]]

        # PLAFOND DUR. Sans lui, le temps du film depend d'une propriete NON
        # MESUREE du modele (la fraction que l'etage leger ouvre), et un film
        # dense -- justement celui ou le referee a le plus a gagner -- depasse
        # le quota et se perd entier. Avec lui, le pire cas est connu d'avance.
        # Les retenus sont ordonnes par marge CROISSANTE : si l'on doit couper,
        # on garde les composantes les plus douteuses, celles ou la lecture du
        # film a le plus de chances de changer la decision.
        plafond = _ETAT.get("vision_max")
        fiche["n_vision_avant_plafond"] = len(retenus)
        if plafond and len(retenus) > int(plafond):
            retenus = [int(i) for i in
                       np.array(retenus)[np.argsort(marge[retenus], kind="stable")]
                       [: int(plafond)]]
            fiche["plafond_atteint"] = True
        fiche["n_vision"] = len(retenus)

        # --- 3 et 4. crops des SEULS retenus, puis vision
        colonnes = ("P_KEEP", "P_REPLACE", "P_ABSTAIN", "E_keep", "E_cand", "U")
        valeurs = {c: np.zeros(n, dtype=np.float32) for c in colonnes}
        valeurs["P_KEEP"][:] = 1.0            # KEEP par defaut, toujours
        if retenus:
            t = time.perf_counter()
            crops = _crops(film, zarr_dir, comp, indices=retenus, fils=fils)
            fiche["secondes_crops"] = time.perf_counter() - t
            besoins = set()
            for i in retenus:
                tc = int(comp["t_centre"][i])
                besoins.update(range(tc - DEMI_T, tc + DEMI_T + 1))
            fiche["n_trames_lues"] = len(besoins)
            t = time.perf_counter()
            budget = _ETAT.get("budget_film_s")
            with torch.no_grad():
                for d0 in range(0, len(retenus), lot):
                    if budget and (time.perf_counter() - t0) > float(budget):
                        # le temps est consomme : les composantes non lues
                        # restent KEEP, et on le DIT au lieu d'etre tue dehors
                        fiche["budget_epuise"] = True
                        fiche["n_vision"] = d0
                        break
                    sel = retenus[d0:d0 + lot]
                    m = _mondes(sel)
                    crop = torch.from_numpy(crops[d0:d0 + len(sel)]).to(dev)
                    with ctx:
                        lots = preparer(teacher, crop, m)
                        kk = modele.lire(lots["visuel_avant"], lots["visuel_arriere"],
                                         lots["keep"]["avant"], lots["keep"]["arriere"])
                        cc = modele.lire(lots["visuel_avant"], lots["visuel_arriere"],
                                         lots["cand"]["avant"], lots["cand"]["arriere"])
                        dd = modele.decider(kk, cc)
                    for c in colonnes:
                        valeurs[c][sel] = dd[c].float().cpu().numpy()
            fiche["secondes_vision"] = time.perf_counter() - t

        lignes = [{"comp_id": str(ids[i]), "famille": str(familles[i]),
                   **{c: float(valeurs[c][i]) for c in colonnes}}
                  for i in range(n)]

        import pyarrow as pa
        import pyarrow.parquet as pq
        sortie = pathlib.Path(sortie_dir)
        sortie.mkdir(parents=True, exist_ok=True)
        chemin = sortie / ("decisions_%s.parquet" % film)
        tmp = chemin.with_suffix(".parquet.tmp")
        pq.write_table(pa.Table.from_pylist(lignes), tmp)
        os.replace(tmp, chemin)
        fiche.update(statut="ok", fichier=str(chemin))
    except Exception as exc:                      # AUCUNE decision -> KEEP total
        fiche["erreur"] = "%s: %s" % (type(exc).__name__, exc)
        fiche["statut"] = "echec"
    fiche["secondes"] = time.perf_counter() - t0
    if fiche["n_composantes"]:
        fiche["ms_par_objet"] = fiche["secondes"] * 1e3 / fiche["n_composantes"]
    return fiche


# --------------------------------------------------------------------------
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--modele", required=True)
    ap.add_argument("--poids-teacher", required=True)
    ap.add_argument("--composantes", required=True)
    ap.add_argument("--zarr", required=True)
    ap.add_argument("--films", nargs="+", required=True)
    ap.add_argument("--sortie", default="decisions")
    ap.add_argument("--lot", type=int, default=64)
    ap.add_argument("--appareil", default="cuda")
    ap.add_argument("--impl-refdata", default=None)
    ap.add_argument("--racine-pack", default=None,
                    help="racine du depot de la chaine figee (celui qui porte "
                         "src/biohub_tracking) ; a defaut la variable "
                         "BIOCEL_PACK_REPO, puis une liste de chemins connus")
    ap.add_argument("--seuil-marge", type=float, default=0.30,
                    help="barre unique de marge legere (un scalaire)")
    ap.add_argument("--seuils-json", default=None,
                    help="table de seuils PAR SOUS-TYPE en JSON, la cle "
                         "defaut servant aux sous-types absents ; exemple : "
                         "{DUPLICATE_FUSION: 0.83, DUPLICATE_PARASITE: 0.65, "
                         "defaut: 0.5}")
    ap.add_argument("--fils", type=int, default=4,
                    help="fils de decompression des trames zarr")
    ap.add_argument("--vision-max", type=int, default=None,
                    help="plafond DUR du nombre d objets qui passent a l etage "
                         "vision, par film ; les plus douteux d abord (marge "
                         "legere croissante). Borne le pire cas par construction")
    ap.add_argument("--budget-film-s", type=float, default=None,
                    help="secondes au-dela desquelles on cesse d ouvrir la "
                         "vision ; les objets non lus restent KEEP et le recu "
                         "porte budget_epuise")
    ap.add_argument("--tout-vision", action="store_true")
    ap.add_argument("--recu", default=None)
    a = ap.parse_args()

    t0 = time.perf_counter()
    seuils = json.loads(a.seuils_json) if a.seuils_json else None
    fiche = initialiser(a.modele, a.poids_teacher, appareil=a.appareil,
                        impl_refdata=a.impl_refdata, seuil_marge=a.seuil_marge,
                        tout_vision=a.tout_vision, seuils=seuils,
                        vision_max=a.vision_max, budget_film_s=a.budget_film_s,
                        racine_pack=a.racine_pack)
    fiche["seuils"] = seuils
    fiche["secondes_initialisation"] = time.perf_counter() - t0
    fiches = [traiter_film(f, a.composantes, a.zarr, a.sortie, lot=a.lot,
                           fils=a.fils, impl_refdata=a.impl_refdata)
              for f in a.films]
    ok = [f for f in fiches if f["statut"] == "ok"]
    rapport = {
        "initialisation": fiche, "films": fiches,
        "n_films_ok": len(ok), "n_films_echec": len(fiches) - len(ok),
        "secondes_par_film_mediane": float(np.median([f["secondes"] for f in fiches]))
        if fiches else None,
        "secondes_crops_medianes": float(np.median(
            [f.get("secondes_crops", 0.0) for f in fiches])) if fiches else None,
        "ms_par_objet_mediane": float(np.median(
            [f.get("ms_par_objet", float("nan")) for f in fiches])) if fiches else None,
    }
    if a.recu:
        tmp = a.recu + ".tmp"
        pathlib.Path(tmp).write_text(json.dumps(rapport, indent=2, ensure_ascii=False),
                                     encoding="utf-8")
        os.replace(tmp, a.recu)
    print(json.dumps(rapport, indent=2, ensure_ascii=False))
