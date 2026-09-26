# -*- coding: utf-8 -*-
"""Les trois accesseurs qu attend `famille_insert_mere.detecteur`.

MITOSE livre une regle qui ne connait NI notre CSV, NI notre .npz, NI notre
zarr -- et c est voulu : « aucun identifiant P1 n y apparait, sur le test cache
il n en existe pas ». Elle demande donc trois accesseurs, et les ecrire est
notre part du contrat.

  view     .noeuds() -> (nid, t, z_vox, y_vox, x_vox) ; .successeurs(nid)
  probmat  .points() -> (idx, t, z, y, x) ; .proba_sortante_max(idx)
           .proba_arete(idx_src, idx_dst) -> float, -1 si absente
  image    tableau (T, Z, Y, X) en VOXEL NATIF

DEUX CHOIX QUI MERITENT D ETRE DITS :

1. L IMAGE N EST PAS CHARGEE EN MEMOIRE. On passe le tableau zarr TEL QUEL :
   il s indexe comme un tableau numpy mais ne lit que ce qu on touche. Charger
   un film entier (T x Z x Y x X) pour lire ~50 pics serait payer des
   gigaoctets pour des kilooctets.

2. LES TABLES DE PROBABILITE SONT CONSTRUITES UNE FOIS PAR FILM. `proba_arete`
   est appelee dans une boucle ; la resoudre par un balayage des 174 663
   aretes a chaque appel serait quadratique. Un dictionnaire (src, dst) -> p
   et un maximum par source coutent une passe et rendent les deux accesseurs
   en temps constant.
"""
from __future__ import annotations

import pathlib

import numpy as np


class VueFilm:
    """Le monde d UN film, vu depuis la `view` de `cell08_referee.scan`."""

    def __init__(self, v):
        self._nid = [int(x) for x in v["node_id"]]
        self._t = [int(x) for x in v["t"]]
        self._zyx = v["zyx"]
        self._succ = {}
        for u, w in v["edges"]:
            self._succ.setdefault(int(u), []).append(int(w))

    def noeuds(self):
        for i, nid in enumerate(self._nid):
            z, y, x = self._zyx[i]
            yield nid, self._t[i], float(z), float(y), float(x)

    def successeurs(self, nid):
        return list(self._succ.get(int(nid), ()))


class ProbmatFilm:
    """Le `.npz` probmat-1.0 d UN film.

    Schema verifie a l ouverture : `pm_coords` (N, 4) en (t, z, y, x),
    `pm_src` / `pm_tgt` / `pm_prob` paralleles. Si le schema changeait, mieux
    vaut lever ici que rendre des probabilites fausses en silence.
    """

    def __init__(self, chemin):
        z = np.load(str(chemin), allow_pickle=False)
        manquantes = [k for k in ("pm_coords", "pm_src", "pm_tgt", "pm_prob")
                      if k not in z.files]
        if manquantes:
            raise RuntimeError("probmat sans %r (cles : %r)"
                               % (manquantes, sorted(z.files)))
        self._coords = np.asarray(z["pm_coords"])
        if self._coords.ndim != 2 or self._coords.shape[1] != 4:
            raise RuntimeError("pm_coords de forme %r, attendu (N, 4)"
                               % (self._coords.shape,))
        src = np.asarray(z["pm_src"]).astype(np.int64)
        tgt = np.asarray(z["pm_tgt"]).astype(np.int64)
        prob = np.asarray(z["pm_prob"]).astype(np.float64)
        if not (len(src) == len(tgt) == len(prob)):
            raise RuntimeError("pm_src/pm_tgt/pm_prob de longueurs %d/%d/%d"
                               % (len(src), len(tgt), len(prob)))
        self.n_aretes = len(src)
        # UNE passe, deux tables : l accesseur devient constant.
        self._arete = {}
        self._max = {}
        for s, d, p in zip(src.tolist(), tgt.tolist(), prob.tolist()):
            c = self._arete.get((s, d))
            if c is None or p > c:
                self._arete[(s, d)] = p
            m = self._max.get(s)
            if m is None or p > m:
                self._max[s] = p
        self.schema = (str(z["pm_schema"]) if "pm_schema" in z.files else "?")
        self.porte_um = (float(z["pm_gate_um"])
                         if "pm_gate_um" in z.files else None)

    def points(self):
        for i, (t, zz, yy, xx) in enumerate(self._coords.tolist()):
            yield i, int(t), float(zz), float(yy), float(xx)

    def proba_sortante_max(self, idx):
        return float(self._max.get(int(idx), 0.0))

    def proba_arete(self, idx_src, idx_dst):
        return float(self._arete.get((int(idx_src), int(idx_dst)), -1.0))


def image_du_film(racine_zarr, film):
    """Le tableau (T, Z, Y, X) en voxel natif, SANS le charger en memoire.

    On rend l objet zarr : il s indexe comme un tableau numpy et ne lit que ce
    qu on touche. La regle ne lit que des boites autour de ~50 pics.
    """
    import zarr
    p = pathlib.Path(racine_zarr) / ("%s.zarr" % film)
    if not p.exists():
        raise FileNotFoundError("zarr absent : %s" % p)
    g = zarr.open(str(p), mode="r")
    # Les .zarr de la competition portent le volume sous la cle "0".
    a = g["0"] if hasattr(g, "__getitem__") and "0" in getattr(
        g, "array_keys", lambda: [])() or "0" in getattr(
        g, "group_keys", lambda: [])() else g
    try:
        a = g["0"]
    except Exception:                                            # noqa: BLE001
        a = g
    if getattr(a, "ndim", 0) == 5:          # (T, C, Z, Y, X) -> canal 0
        a = a[:, 0]
    return a


class _Depassement(Exception):
    """Le film a depasse son temps. Ce n est pas une erreur : c est la garde."""


def _minuteur(secondes):
    """Rend (armer, desarmer). Sur Unix, interrompt REELLEMENT l appel."""
    import signal
    if not hasattr(signal, "setitimer") or not hasattr(signal, "SIGALRM"):
        return None, None                      # pas d interruption possible

    def _sonne(_s, _f):
        raise _Depassement("depassement de %.2f s" % secondes)

    def armer():
        signal.signal(signal.SIGALRM, _sonne)
        signal.setitimer(signal.ITIMER_REAL, secondes)

    def desarmer():
        signal.setitimer(signal.ITIMER_REAL, 0.0)
    return armer, desarmer


def plan_du_monde(vue, racine_probmat, racine_zarr, regle, bornes, q_etoile,
                  films=None, journal=None, t_film=20.0, t_total=1500.0, **kw):
    """Applique la regle FILM PAR FILM et rend un plan {film: plan}.

    Un film qui echoue n empeche pas les autres : son erreur est journalisee
    et il est simplement absent du plan. Une famille qui tombe entierement
    parce qu un film manque son zarr serait une famille fragile.
    """
    import time as _time
    armer, desarmer = _minuteur(t_film)
    out = {}
    rap = {"par_film": {}, "n_films": 0, "n_echecs": 0,
           "t_film_s": t_film, "t_total_s": t_total,
           "interruption_reelle": armer is not None,
           "insert_films_sautes": 0, "sautes_par_temps_film": [],
           "sautes_par_temps_total": [], "secondes_cumulees": 0.0}
    if armer is None:
        rap["avertissement"] = (
            "signal.setitimer absent (Windows) : la garde par film MESURE "
            "apres coup au lieu d INTERROMPRE. Le pire cas n est donc PAS "
            "borne ici. Sur Kaggle et sur les pods, l interruption est reelle.")
    for film in sorted(vue) if films is None else films:
        d, t0 = {}, _time.monotonic()
        if rap["secondes_cumulees"] >= t_total:
            # LE SEUIL GLOBAL : on ne commence meme pas.
            rap["sautes_par_temps_total"].append(film)
            rap["insert_films_sautes"] += 1
            rap["par_film"][film] = {"saute": "budget INSERT epuise",
                                     "insertions": 0}
            rap["n_films"] += 1
            continue
        try:
            pm = ProbmatFilm(pathlib.Path(racine_probmat) / ("%s.npz" % film))
            im = image_du_film(racine_zarr, film)
            if armer is not None:
                armer()
            try:
                p = regle.detecteur(VueFilm(vue[film]), pm, im, bornes,
                                    q_etoile, journal=journal, **kw) or {}
            finally:
                if desarmer is not None:
                    desarmer()
            dt = _time.monotonic() - t0
            n = len(p.get("add_nodes") or ())
            if armer is None and dt > t_film:
                # Sans interruption : on ECARTE le resultat plutot que de
                # pretendre que la garde a tenu.
                rap["sautes_par_temps_film"].append(film)
                rap["insert_films_sautes"] += 1
                d = {"saute": "depassement mesure apres coup (%.1f s)" % dt,
                     "secondes": round(dt, 2), "insertions": 0}
            else:
                if n:
                    out[film] = p
                d = {"insertions": n, "aretes": len(p.get("add_edges") or ()),
                     "secondes": round(dt, 2), "n_aretes_probmat": pm.n_aretes,
                     "schema": pm.schema}
        except _Depassement as e:
            rap["sautes_par_temps_film"].append(film)
            rap["insert_films_sautes"] += 1
            d = {"saute": str(e), "secondes": round(_time.monotonic() - t0, 2),
                 "insertions": 0}
        except Exception as e:                                   # noqa: BLE001
            rap["n_echecs"] += 1
            d = {"erreur": "%s: %s" % (type(e).__name__, str(e)[:180]),
                 "secondes": round(_time.monotonic() - t0, 2)}
        rap["secondes_cumulees"] += _time.monotonic() - t0
        rap["par_film"][film] = d
        rap["n_films"] += 1
    rap["secondes_cumulees"] = round(rap["secondes_cumulees"], 2)
    rap["insertions_totales"] = sum(
        v.get("insertions", 0) for v in rap["par_film"].values())
    return out, rap
