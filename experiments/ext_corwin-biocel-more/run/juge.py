# -*- coding: utf-8 -*-
"""ETAGE E0 -- LE JUGE. Le scorer OFFICIEL restaure, appele par film, agrege
par `summarise()`, et rien d'autre.

CE QUE CE MODULE EST
--------------------
La seule porte d'entree de la lane RADAR vers le bareme. Il ne calcule aucune
metrique de son cru : il *appelle* `tracking_cellmot.metrics.evaluate`,
`node_recall`, `per_sample_metrics` et `summarise` du bundle restaure
(`03_HERITAGE/scorer_bundle/restored`, commit amont `075fc5f`).

LES QUATRE GARDES, ET POURQUOI ELLES EXISTENT
---------------------------------------------
G-A  `assurer_scorer_officiel()` refuse de demarrer si `metrics.py` ou
     `division_metrics.py` n'ont pas EXACTEMENT le nombre de lignes et le
     sha256 du bundle restaure. Un scorer edite en silence rendrait tout
     chiffre de cette lane incomparable a l'ancre.

G-B  `garde_evaluate_datasets()` remplace `evaluate_datasets` par une fonction
     qui LEVE. Motif MESURE et non suppose : `evaluate_datasets()` micro-moyenne
     le Jaccard d'arete SANS le facteur nodal, et rend +0,0035 de plus que
     `summarise()` a l'ancre -- or la page Kaggle decrit `summarise()`. Un
     appel accidentel donnerait un score faux VERS LE HAUT, la pire direction.
     La garde est un `raise` nomme, jamais un `assert` (`python -O` les efface).

G-C  L'echelle voxel est LUE dans le zarr de chaque film
     (`multiscales[0].datasets[0].coordinateTransformations[0].scale[-3:]`,
     exactement la regle de `tracking_cellmot.io._parse_scale`), avec repli
     `DEFAULT_SCALE`. Mesure locale : les 199 zarrs d'entrainement portent tous
     `(1.625, 0.40625, 0.40625)` -- la lecture est donc un no-op ICI, et c'est
     precisement pourquoi elle doit rester CABLEE : rien ne garantit la meme
     valeur sur les deux embryons du test cache, et un seuil physique code en
     dur deviendrait faux EN SILENCE.

G-D  `assurer_assiette()` refuse une assiette incomplete. Un film manquant
     retire son poids `w_i` du denominateur et deplace `adj` sans rien dire.

CE QUE CE MODULE NE FAIT PAS
----------------------------
Il n'apprend rien, ne choisit rien, ne corrige rien. Il ouvre la GT (c'est son
metier : la GT MESURE) et n'en extrait aucune caracteristique reutilisable :
seules les sept compteurs et `estimated_number_of_nodes` en sortent.

ORDRE DES ARETES -- PIEGE NOMME
-------------------------------
Le plafond d'out-degree du scorer garde les deux plus PETITS `EDGE_ID`, et
`EDGE_ID` suit l'ORDRE D'INSERTION, lui-meme l'ordre des lignes du CSV. Tout
chargeur de ce module preserve donc l'ordre des aretes tel qu'il le lit, et ne
trie JAMAIS. Le tri par confiance est une decision d'export (`export.py`), pas
une commodite de chargement.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys
import warnings
from dataclasses import dataclass, field
from typing import Iterable

import numpy as np

# ------------------------------------------------------------------ chemins
_REPO_DEFAUT = "D:/Github/BIOCELL_WINNING"
REPO = pathlib.Path(os.environ.get("BIOCEL_REPO", _REPO_DEFAUT))
BIOCEL = pathlib.Path(os.environ.get("BIOCEL_BIOCEL", "D:/Github/BIOCEL"))

SCORER_SRC = REPO / "03_HERITAGE" / "scorer_bundle" / "restored" / "src"
SCORER_SCRIPTS = REPO / "03_HERITAGE" / "scorer_bundle" / "restored" / "scripts"
GT_DIR = pathlib.Path(os.environ.get(
    "RADAR_GT_DIR", str(BIOCEL / "data" / "raw" / "competition" / "train")))
A0_DIR = pathlib.Path(os.environ.get(
    "RADAR_A0_DIR", str(REPO / "07_STORE" / "WE" / "P1")))

#: Repli de `tracking_cellmot.io.DEFAULT_SCALE` (z, y, x) en um/voxel.
DEFAULT_SCALE: tuple[float, float, float] = (1.625, 0.40625, 0.40625)
#: Rayon d'appariement du juge (um). Valeur du scorer officiel.
GATE_UM: float = 7.0
#: Coefficient du terme nodal et poids du canal division (metrics.py).
ALPHA: float = 0.1
POIDS_DIVISION: float = 0.1

#: Temoins du bundle restaure -- lignes et sha256, mesures le 2026-09-03.
TEMOINS_SCORER: dict[str, tuple[int, str]] = {
    "metrics.py": (
        536, "cfdd596e3f8909cca14db0682889738b19ff75c3808b3773175aba9367ca7444"),
    "division_metrics.py": (
        574, "0635c38621a38f1eb4b55a302b4a817a88e9094930dfc2dab16faeeee60f4dc9"),
}

#: Les sept compteurs de `EvaluationResult`, dans l'ordre du scorer.
COMPTEURS = ("edge_tp", "edge_fp", "edge_fn",
             "division_tp", "division_fp", "division_fn", "num_pred_nodes")

#: L'ancre A (monde natif champion, 199 films). Source :
#: `04_SRC/biocel/common/anchor.py::ANCHOR` (D-010), elle-meme issue de
#: `03_HERITAGE/handoffs/ulysse/ULYSSE_FINAL_HANDOFF.md`.
ANCRE_A: dict = {
    "nom": "ULYSSE_199",
    "score": 0.9292977754628515,
    "adj_edge_jaccard": 0.9197233073777451,
    "division_jaccard": 0.09574468085106383,
    "edge_tp": 122844, "edge_fp": 5192, "edge_fn": 6039,
    "division_tp": 36, "division_fp": 225, "division_fn": 115,
    "num_pred_nodes": 3_992_404,
    "n_films": 199,
}


#: L'ancre ARGOS -- MEME monde de noeuds, 137 aretes posees de plus (l'autre
#: chargeur de champion, piege C86). Elle est ici parce qu'elle est, elle,
#: REJOUABLE : le monde `05_WORK/experiments/MOIRA/M_W_deploy/world_n7` la
#: rend AU BIT (mesure du 2026-09-03, recu `SCOREBOARD_W7_UNCUT.json`).
#: L'ancre A (ULYSSE) ne l'est pas : son `submission.csv` 199 films est PERDU
#: (D-010 ; `04_SRC/biocel/decision/champion_loader.py` le declare).
ANCRE_ARGOS: dict = {
    "nom": "ARGOS_199_AUTRE_CHARGEUR",
    "score": 0.9294725354987384,
    "adj_edge_jaccard": 0.919898067413632,
    "division_jaccard": 0.09574468085106383,
    "edge_tp": 122922, "edge_fp": 5251, "edge_fn": 5961,
    "division_tp": 36, "division_fp": 225, "division_fn": 115,
    "num_pred_nodes": 3_992_404,
    "n_films": 199,
}

#: A0 = `07_STORE/WE/P1` = le monde W7 moins les 4 513 coupes V1B_MAX_RD.
#: MESURE le 2026-09-03 (`SCOREBOARD.json`) ; reproduit les 199 lignes
#: scellees `MOIRA/M_W_deploy/out/rows/V1B/V1B_MAX_RD` au bit sur les sept
#: compteurs. Ce n'est PAS l'ancre A : les coupes ont retire 137 FP de
#: division et le score est PLUS HAUT de 4,2e-03.
A0_P1: dict = {
    "nom": "A0_P1_199",
    "score": 0.9335116032565778,
    "adj_edge_jaccard": 0.9201224819176657,
    "division_jaccard": 0.13389121338912133,
    "edge_tp": 122864, "edge_fp": 5155, "edge_fn": 6019,
    "division_tp": 32, "division_fp": 88, "division_fn": 119,
    "num_pred_nodes": 3_992_404,
    "n_films": 199,
}


class JugeRefuse(RuntimeError):
    """Une garde de l'etage E0 a mordu. `raise` nomme, jamais `assert` : sous
    `python -O` un `assert` disparait a la compilation et la garde ne mord
    plus, EN SILENCE."""


def exige(condition: bool, message: str) -> None:
    """La forme opposable d'une garde : un appel de fonction, qu'aucun drapeau
    de l'interpreteur ne supprime."""
    if not condition:
        raise JugeRefuse(message)


# ------------------------------------------------------------- scorer pinne
_SCORER_VERIFIE: dict | None = None


def assurer_scorer_officiel(verbeux: bool = False) -> dict:
    """G-A. Verifie lignes + sha256 des deux modules du bareme, PUIS les met
    sur le `sys.path`. Rend le releve (chemin, lignes, sha) pour le recu."""
    global _SCORER_VERIFIE
    if _SCORER_VERIFIE is not None:
        return _SCORER_VERIFIE
    exige(SCORER_SRC.is_dir(), f"scorer restaure introuvable : {SCORER_SRC}")
    releve = {}
    base = SCORER_SRC / "tracking_cellmot"
    for nom, (lignes_att, sha_att) in TEMOINS_SCORER.items():
        p = base / nom
        exige(p.is_file(), f"module de bareme absent : {p}")
        brut = p.read_bytes()
        lignes = len(brut.splitlines())
        sha = hashlib.sha256(brut).hexdigest()
        exige(lignes == lignes_att,
              f"SCORER NON OFFICIEL : {nom} {lignes} lignes != {lignes_att}")
        exige(sha == sha_att,
              f"SCORER NON OFFICIEL : {nom} sha {sha} != {sha_att}")
        releve[nom] = {"chemin": str(p), "lignes": lignes, "sha256": sha}
    if str(SCORER_SRC) not in sys.path:
        sys.path.insert(0, str(SCORER_SRC))
    if verbeux:
        for k, v in releve.items():
            print(f"  scorer OK  {k:<22} {v['lignes']} l.  {v['sha256'][:16]}")
    _SCORER_VERIFIE = releve
    return releve


class GardeDatasets:
    """G-B. Remplace `tracking_cellmot.metrics.evaluate_datasets` par une
    fonction qui LEVE, pour toute la duree du bloc `with`.

    Deux sens exerces par le banc :
      * SENS PASSANT : le chemin `summarise()` de ce module traverse le bloc
        sans jamais toucher a `evaluate_datasets` -- la garde ne mord pas ;
      * SENS REFUSANT : un appel direct a `evaluate_datasets` leve
        `JugeRefuse`, et `n_appels` le compte.
    """

    def __init__(self) -> None:
        self.n_appels = 0
        self._original = None

    def __enter__(self) -> "GardeDatasets":
        assurer_scorer_officiel()
        import tracking_cellmot.metrics as MM
        self._original = MM.evaluate_datasets

        def _interdit(*a, **k):
            self.n_appels += 1
            raise JugeRefuse(
                "evaluate_datasets() APPELE : ecart mesure +0,0035 contre "
                "summarise() a l'ancre, et le facteur nodal y devient "
                "invisible. La page Kaggle decrit summarise().")

        MM.evaluate_datasets = _interdit
        return self

    def __exit__(self, *exc) -> None:
        import tracking_cellmot.metrics as MM
        MM.evaluate_datasets = self._original
        return None


def garde_evaluate_datasets() -> GardeDatasets:
    """Fabrique la garde G-B (voir `GardeDatasets`)."""
    return GardeDatasets()


# ------------------------------------------------------- echelle et assiette
_ECHELLES: dict[str, tuple[float, float, float]] = {}


def echelle_du_film(film: str, gt_dir: pathlib.Path | None = None
                    ) -> tuple[float, float, float]:
    """G-C. L'echelle (z, y, x) en um/voxel LUE dans le zarr du film.

    Reproduit `tracking_cellmot.io._parse_scale` a la lettre : le zarr est
    OME-NGFF, la transformation `scale` du premier dataset du premier
    multiscale, dont on garde les TROIS DERNIERES composantes (l'axe T porte
    la premiere). Repli `DEFAULT_SCALE` si le zarr est absent ou muet -- c'est
    le repli du scorer lui-meme (`evaluate.py::_read_scale`).
    """
    gt_dir = pathlib.Path(gt_dir) if gt_dir is not None else GT_DIR
    cle = f"{gt_dir}|{film}"
    if cle in _ECHELLES:
        return _ECHELLES[cle]
    zarr_path = gt_dir / f"{film}.zarr"
    echelle = DEFAULT_SCALE
    meta = zarr_path / "zarr.json"          # zarr v3
    zattrs = zarr_path / ".zattrs"          # zarr v2
    attrs: dict | None = None
    if meta.is_file():
        attrs = json.loads(meta.read_text(encoding="utf-8")).get("attributes")
    elif zattrs.is_file():
        attrs = json.loads(zattrs.read_text(encoding="utf-8"))
    if attrs and "multiscales" in attrs:
        tr = attrs["multiscales"][0]["datasets"][0]["coordinateTransformations"][0]
        exige(tr.get("type") == "scale",
              f"{film}: transformation zarr de type {tr.get('type')!r}, pas 'scale'")
        echelle = tuple(float(v) for v in tr["scale"][-3:])
    exige(len(echelle) == 3, f"{film}: echelle de longueur {len(echelle)}")
    _ECHELLES[cle] = echelle
    return echelle


def films_gt(gt_dir: pathlib.Path | None = None) -> list[str]:
    """Les noms de dataset presents en GT, tries."""
    gt_dir = pathlib.Path(gt_dir) if gt_dir is not None else GT_DIR
    return sorted(p.stem for p in gt_dir.glob("*.geff"))


def assurer_assiette(films: Iterable[str], attendu: int = 199) -> list[str]:
    """G-D. Refuse une assiette incomplete ou doublonnee."""
    f = list(films)
    exige(len(set(f)) == len(f), "assiette : un film apparait deux fois")
    exige(len(f) == attendu, f"assiette : {len(f)} films au lieu de {attendu}")
    return sorted(f)


# --------------------------------------------------------------- le monde
@dataclass
class Monde:
    """Un monde predit pour UN film. Coordonnees en INDICES VOXEL, ids NATIFS.

    `edges` est un tableau (m, 2) d'ids natifs dont L'ORDRE EST SIGNIFIANT
    (il fixe `EDGE_ID`, donc le plafond d'out-degree). `conf` est la confiance
    par arete quand la source en porte une, sinon `None`.
    """

    film: str
    node_id: np.ndarray
    t: np.ndarray
    zyx: np.ndarray
    edges: np.ndarray
    conf: np.ndarray | None = None
    provenance: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.node_id = np.asarray(self.node_id, np.int64).reshape(-1)
        self.t = np.asarray(self.t, np.int64).reshape(-1)
        self.zyx = np.asarray(self.zyx, np.float64).reshape(-1, 3)
        self.edges = np.asarray(self.edges, np.int64).reshape(-1, 2)
        exige(len(self.node_id) == len(self.t) == len(self.zyx),
              f"{self.film}: noeuds incoherents "
              f"({len(self.node_id)}/{len(self.t)}/{len(self.zyx)})")
        if self.conf is not None:
            self.conf = np.asarray(self.conf, np.float64).reshape(-1)
            exige(len(self.conf) == len(self.edges),
                  f"{self.film}: {len(self.conf)} confiances pour "
                  f"{len(self.edges)} aretes")

    @property
    def n_noeuds(self) -> int:
        return int(len(self.node_id))

    @property
    def n_aretes(self) -> int:
        return int(len(self.edges))

    def copie(self) -> "Monde":
        return Monde(self.film, self.node_id.copy(), self.t.copy(),
                     self.zyx.copy(), self.edges.copy(),
                     None if self.conf is None else self.conf.copy(),
                     dict(self.provenance))

    def index_par_id(self) -> dict[int, int]:
        return {int(v): i for i, v in enumerate(self.node_id)}


def charger_parquet(film: str, racine: pathlib.Path | None = None) -> Monde:
    """Le monde A0 depuis `<racine>/nodes/<film>.nodes.parquet` +
    `<racine>/edges/<film>.edges.parquet` (schema WORLD_N7 : `node_id, t,
    z_vox, y_vox, x_vox` et `u, v`). L'ordre des lignes est PRESERVE."""
    import polars as pl
    racine = pathlib.Path(racine) if racine is not None else A0_DIR
    pn = racine / "nodes" / f"{film}.nodes.parquet"
    pe = racine / "edges" / f"{film}.edges.parquet"
    exige(pn.is_file(), f"noeuds absents : {pn}")
    exige(pe.is_file(), f"aretes absentes : {pe}")
    n = pl.read_parquet(pn)
    e = pl.read_parquet(pe)
    zyx = np.column_stack([n["z_vox"].to_numpy(), n["y_vox"].to_numpy(),
                           n["x_vox"].to_numpy()]).astype(np.float64)
    uv = (np.column_stack([e["u"].to_numpy(), e["v"].to_numpy()]).astype(np.int64)
          if e.height else np.zeros((0, 2), np.int64))
    return Monde(film, n["node_id"].to_numpy().astype(np.int64),
                 n["t"].to_numpy().astype(np.int64), zyx, uv,
                 provenance={"source": "parquet", "racine": str(racine)})


def charger_csv(csv_path: pathlib.Path | str, films: Iterable[str] | None = None
                ) -> dict[str, Monde]:
    """Les mondes d'un `submission.csv` officiel (10 colonnes). L'ordre des
    lignes d'arete de chaque dataset est PRESERVE tel quel : c'est lui qui
    fixe `EDGE_ID` chez le juge."""
    import polars as pl
    df = pl.read_csv(str(csv_path))
    manquantes = [c for c in ("dataset", "row_type", "node_id", "t", "z", "y",
                              "x", "source_id", "target_id") if c not in df.columns]
    exige(not manquantes, f"colonnes absentes du CSV : {manquantes}")
    voulus = set(films) if films is not None else None
    out: dict[str, Monde] = {}
    for (nom,), g in df.group_by("dataset", maintain_order=True):
        if voulus is not None and nom not in voulus:
            continue
        nr = g.filter(pl.col("row_type") == "node")
        er = g.filter(pl.col("row_type") == "edge")
        zyx = np.column_stack([nr["z"].to_numpy(), nr["y"].to_numpy(),
                               nr["x"].to_numpy()]).astype(np.float64)
        uv = (np.column_stack([er["source_id"].to_numpy(),
                               er["target_id"].to_numpy()]).astype(np.int64)
              if er.height else np.zeros((0, 2), np.int64))
        out[nom] = Monde(nom, nr["node_id"].to_numpy().astype(np.int64),
                         nr["t"].to_numpy().astype(np.int64), zyx, uv,
                         provenance={"source": "csv", "csv": str(csv_path)})
    return out


# ------------------------------------------------------------------- la GT
_GT: dict = {}


def gt_du_film(film: str, gt_dir: pathlib.Path | None = None):
    """(graphe GT, `estimated_number_of_nodes`). Le second est `nan` quand le
    `.geff` ne le porte pas -- c'est le cas au TEST : il faut alors le
    regresser (voir `mesure_ntrue` de la lane)."""
    assurer_scorer_officiel()
    gt_dir = pathlib.Path(gt_dir) if gt_dir is not None else GT_DIR
    cle = f"{gt_dir}|{film}"
    if cle not in _GT:
        import tracksdata as td
        from geff import GeffMetadata
        p = gt_dir / f"{film}.geff"
        exige(p.exists(), f"GT absente : {p}")
        r = td.graph.IndexedRXGraph.from_geff(p)
        g = r[0] if isinstance(r, tuple) else r
        try:
            meta = GeffMetadata.read(p)
            n_total = float((meta.extra or {}).get(
                "estimated_number_of_nodes", float("nan")))
        except Exception:
            n_total = float("nan")
        _GT[cle] = (g, n_total)
    return _GT[cle]


def n_true(film: str, gt_dir: pathlib.Path | None = None) -> float:
    """`estimated_number_of_nodes` du `.geff`, ou `nan`."""
    return gt_du_film(film, gt_dir)[1]


# ------------------------------------------------------- le chemin officiel
def construire_graphe(monde: Monde):
    """Le graphe `tracksdata` du monde, ids natifs remappes, ORDRE DES ARETES
    PRESERVE (c'est le chemin de `scripts/csv_to_geffs.py`)."""
    assurer_scorer_officiel()
    import polars as pl
    import tracksdata as td
    g = td.graph.InMemoryGraph()
    for cle in ("z", "y", "x"):
        g.add_node_attr_key(cle, pl.Float64, -999999.0)
    internes = g.bulk_add_nodes([
        {"t": int(ti), "z": float(zi), "y": float(yi), "x": float(xi)}
        for ti, (zi, yi, xi) in zip(monde.t, monde.zyx)])
    ext = {int(e): i for e, i in zip(monde.node_id, internes)}
    if monde.n_aretes:
        g.bulk_add_edges([{"source_id": ext[int(s)], "target_id": ext[int(d)]}
                          for s, d in monde.edges])
    return g, ext


def juger_film(monde: Monde, gt_dir: pathlib.Path | None = None,
               echelle: tuple[float, float, float] | None = None) -> dict:
    """LA ligne officielle d'un film : les sept compteurs + `node_recall`,
    `total_node_ratio`, `edge_jaccard`, `adj_edge_jaccard`.

    `echelle` est LUE dans le zarr du film si elle n'est pas fournie (G-C).
    """
    assurer_scorer_officiel()
    from tracking_cellmot.metrics import evaluate, node_recall, per_sample_metrics
    gt, n_total = gt_du_film(monde.film, gt_dir)
    ech = echelle if echelle is not None else echelle_du_film(monde.film, gt_dir)
    g, _ = construire_graphe(monde)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        er = evaluate(g, gt, scale=tuple(ech), max_distance=GATE_UM)
        rec = node_recall(g, gt) if (g.num_nodes() and g.num_edges()) else 0.0
    ligne = per_sample_metrics(er, n_total, rec)
    return {"dataset": monde.film, "scale": list(ech),
            "n_total": n_total,
            **{k: (float(v) if isinstance(v, (int, float, np.floating)) else v)
               for k, v in ligne.items()}}


def agreger(lignes: list[dict]) -> dict:
    """`summarise()` du bareme OFFICIEL -- jamais `evaluate_datasets()`.

    C'est la formule que decrit la page Kaggle : `adj` pondere par
    `w_i = TP+FP+FN` par film, divisions micro-moyennees, puis
    `score = adj + 0,1 x J_div`.
    """
    assurer_scorer_officiel()
    from tracking_cellmot.metrics import summarise
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        s = dict(summarise(lignes))
    s["edge_tp"] = int(sum(r["edge_tp"] for r in lignes))
    s["edge_fp"] = int(sum(r["edge_fp"] for r in lignes))
    s["edge_fn"] = int(sum(r["edge_fn"] for r in lignes))
    s["num_pred_nodes"] = int(sum(r["num_pred_nodes"] for r in lignes))
    s["W"] = s["edge_tp"] + s["edge_fp"] + s["edge_fn"]
    s["D"] = s["division_tp"] + s["division_fp"] + s["division_fn"]
    return s


# ----------------------------------------------------------- identite adj
def identite_adj(lignes: list[dict]) -> dict:
    """`adj = Somme(a_i x TP_i) / Somme(w_i)` avec `a_i = 1 - 0,1 (N_i - n_i)/n_i`.

    Ce n'est pas une approximation : c'est `summarise()` reecrit. Le module
    la publie a cote de `adj` du scorer, et l'ecart des deux est un TEMOIN
    (attendu ~1e-16). C'est cette identite qui rend chaque geste chiffrable
    SANS re-scorer.
    """
    n1 = 0.0
    den = 0
    for r in lignes:
        den += int(r["edge_tp"]) + int(r["edge_fp"]) + int(r["edge_fn"])
        n_i = float(r["n_total"]) if "n_total" in r else float("nan")
        if n_i == n_i and n_i > 0:
            a_i = 1.0 - ALPHA * (float(r["num_pred_nodes"]) - n_i) / n_i
        else:
            a_i = float("nan")
        n1 += a_i * float(r["edge_tp"])
    return {"adj_identite": n1 / den if den else float("nan"),
            "N1": n1, "W": den}


def sha_sortie(objet) -> str:
    """Le sha256 d'une sortie JSON canonique (cles triees, separateurs fixes,
    flottants en `repr` : aucune troncature d'arrondi)."""
    txt = json.dumps(objet, sort_keys=True, ensure_ascii=True,
                     separators=(",", ":"), default=_json_defaut)
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()


def _json_defaut(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"non serialisable : {type(o)}")


def comparer_a_l_ancre(resume: dict, ancre: dict | None = None) -> dict:
    """Le rejeu de l'ancre A, compteur par compteur. AU BIT sur les entiers,
    egalite exacte de `repr` sur les flottants."""
    a = dict(ANCRE_A if ancre is None else ancre)
    ecarts = {}
    for cle in ("edge_tp", "edge_fp", "edge_fn", "division_tp", "division_fp",
                "division_fn", "num_pred_nodes"):
        ecarts[cle] = int(resume[cle]) - int(a[cle])
    for cle in ("score", "adj_edge_jaccard", "division_jaccard"):
        ecarts[cle] = float(resume[cle]) - float(a[cle])
    au_bit = (all(ecarts[c] == 0 for c in
                  ("edge_tp", "edge_fp", "edge_fn", "division_tp",
                   "division_fp", "division_fn", "num_pred_nodes"))
              and repr(float(resume["score"])) == repr(float(a["score"]))
              and repr(float(resume["adj_edge_jaccard"])) == repr(float(a["adj_edge_jaccard"])))
    return {"AU_BIT": bool(au_bit), "ecarts": ecarts,
            "mesure": {c: resume[c] for c in
                       ("score", "adj_edge_jaccard", "division_jaccard",
                        "edge_tp", "edge_fp", "edge_fn", "division_tp",
                        "division_fp", "division_fn", "num_pred_nodes", "n")},
            "attendu": a}
