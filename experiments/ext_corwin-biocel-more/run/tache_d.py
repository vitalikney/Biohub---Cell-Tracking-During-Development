# -*- coding: utf-8 -*-
"""CIBLAGE tache D -- pilote de l oracle par composante de desaccord.

Le score officiel est un RAPPORT DE SOMMES sur les films (juge.py::identite_adj).
Une composante ne touche qu UN film : on juge donc ce film-la dans le monde mixte
et on recompose le score de l assiette ENTIERE avec les compteurs des autres
films, exactement. Un jugement par composante, pas un par assiette.

Deux sources de mondes :
  --source parquet  : <racine>/nodes|edges/<film>.{nodes,edges}.parquet
  --source csv      : un submission.csv officiel (10 colonnes)
et, pour l ESSAI DE MACHINERIE, `--candidat nms:<d>` fabrique W1 en appliquant
au monde du temoin une suppression de non-maxima par distance de d um (glouton,
ordre d insertion faute de force de pic dans un monde deja lie).

EVAL_ONLY. CPU. Ecrit `CIBLAGE/recus/R_ORACLE_LOCAL_<etiquette>.json`.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import os
sys.path.insert(0, str(pathlib.Path(
    os.environ.get("BIOCEL_REPO", "D:/Github/BIOCELL_WINNING")) / "04_SRC"))
import oracle_local as OL  # noqa: E402
from lifetwin.radar import juge as J  # noqa: E402

RECUS = pathlib.Path(os.environ.get(
    "CIBLAGE_RECUS", str(pathlib.Path(__file__).resolve().parents[1] / "recus")))
ALPHA = 0.1


def date_u() -> str:
    return subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                          capture_output=True, text=True, check=True).stdout.strip()


def _idle():
    try:
        import psutil
        psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
    except Exception:
        pass


# ------------------------------------------------------------------ score
def score_assiette(lignes: dict) -> float:
    n1 = den = dtp = dfp = dfn = 0.0
    for r in lignes.values():
        w = r["edge_tp"] + r["edge_fp"] + r["edge_fn"]
        a = 1.0 - ALPHA * (r["num_pred_nodes"] - r["n_total"]) / r["n_total"]
        n1 += a * r["edge_tp"]
        den += w
        dtp += r["division_tp"]
        dfp += r["division_fp"]
        dfn += r["division_fn"]
    jd = dtp / (dtp + dfp + dfn) if (dtp + dfp + dfn) else 0.0
    return (n1 / den if den else 0.0) + ALPHA * jd


def ligne(m: J.Monde) -> dict:
    """Le juge officiel sur le monde CANONISE (voir oracle_local.canonise)."""
    r = J.juger_film(OL.canonise(m))
    return {k: float(r[k]) for k in ("edge_tp", "edge_fp", "edge_fn", "division_tp",
                                     "division_fp", "division_fn", "num_pred_nodes",
                                     "n_total")}


# ------------------------------------------------ fabrication des mondes W1
def nms_monde(W: J.Monde, echelle, d: float) -> J.Monde:
    """Suppression de non-maxima par distance sur un monde deja lie.

    Faute de force de pic (le monde n en porte pas), l ordre est celui des lignes,
    c est-a-dire l ordre de detection. Les aretes touchant un noeud supprime
    tombent. C est un candidat LOCAL par construction.
    """
    e = np.asarray(echelle, dtype=np.float64)
    P = W.zyx * e
    garde = np.ones(W.n_noeuds, dtype=bool)
    for k in np.unique(W.t):
        idx = np.nonzero(W.t == k)[0]
        if len(idx) < 2:
            continue
        Pk = P[idx]
        mort = np.zeros(len(idx), dtype=bool)
        d2 = d * d
        for a in range(len(idx)):
            if mort[a]:
                continue
            dd = Pk[a + 1:] - Pk[a]
            if len(dd):
                mort[a + 1:] |= (dd * dd).sum(axis=1) < d2
        garde[idx[mort]] = False
    vivants = set(int(x) for x in W.node_id[garde])
    ar = np.array([(int(u), int(v)) for u, v in W.edges
                   if int(u) in vivants and int(v) in vivants],
                  dtype=np.int64).reshape(-1, 2)
    return J.Monde(W.film, W.node_id[garde], W.t[garde], W.zyx[garde], ar,
                   provenance={"source": f"nms {d} um sur {W.provenance.get('source')}"})


_MONDES_CSV: dict = {}


def charge(film: str, spec: str) -> J.Monde:
    """Un monde. Les CSV sont lus UNE FOIS par processus et gardes en memoire :
    le submission.csv etage pese 160 Mo, le relire par film couterait des minutes."""
    kind, _, val = spec.partition(":")
    if kind == "parquet":
        return J.charger_parquet(film, pathlib.Path(val))
    if kind == "csv":
        if val not in _MONDES_CSV:
            _MONDES_CSV[val] = J.charger_csv(pathlib.Path(val))
        m = _MONDES_CSV[val].get(film)
        if m is None:
            raise SystemExit(f"{film} absent de {val}")
        return m
    raise SystemExit(f"source inconnue : {spec}")


# ------------------------------------------------------------- un film
CLES = ("edge_tp", "edge_fp", "edge_fn", "division_tp", "division_fp",
        "division_fn", "num_pred_nodes")


def prepare(film, w0_spec, w1_spec, rayon):
    W0 = charge(film, w0_spec)
    ech = J.echelle_du_film(film)
    if w1_spec.startswith("nms:"):
        W1 = nms_monde(W0, ech, float(w1_spec.split(":", 1)[1]))
    else:
        W1 = charge(film, w1_spec)
    m01, m10 = OL.appariement(W0, W1, ech, rayon)
    ent = OL.entites(W0, W1, m01, m10, ech)
    a0, a1, a1_p, d0, d1 = OL.aretes_differentes(W0, W1, m01, m10)
    ent = OL.entites_d_aretes(ent, W0, W1, a0, a1, d0, d1)
    if len(ent["type"]) == 0:
        return W0, W1, ent, m10, a0, a1, np.zeros(0, np.int64), 0, (d0, d1)
    comp, _, _ = OL.composantes(W0, W1, ent, a0, a1, a1_p, d0, d1, ech)
    return W0, W1, ent, m10, a0, a1, comp, int(comp.max()) + 1, (d0, d1)


def analyse_film(args) -> tuple[str, dict]:
    """Mesure le delta de compteurs de CHAQUE composante, par la voie RESTREINTE.

    ACCELERATION VERIFIEE, PAS SUPPOSEE. Le juge apparie trame par trame et ses
    compteurs sont des sommes sur les trames : la DIFFERENCE de compteurs entre
    W0 et M_c, calculee sur les seules trames touchees (elargies d une trame de
    chaque cote, pour prendre les aretes entrantes et sortantes), vaut la
    difference sur le film entier. `n_verif` composantes tirees au hasard sont
    recalculees par le film ENTIER et comparees au bit ; le recu publie le
    resultat de ce controle.
    """
    (film, w0_spec, w1_spec, rayon, n_max, graine, n_verif) = args
    _idle()
    t0 = time.perf_counter()
    W0, W1, ent, m10, a0, a1, comp, nc, (d0, d1) = prepare(film, w0_spec, w1_spec, rayon)
    l0 = ligne(W0)
    if nc == 0:
        return film, {"n_entites": 0, "n_composantes": 0, "ligne_W0": l0,
                      "ligne_W1": l0, "ligne_toutes_composantes": l0,
                      "deltas": {}, "verification": {"n": 0, "exactes": 0}}
    l1 = ligne(W1)
    lt = ligne(OL.monde_mixte(W0, W1, ent, m10, a0, a1, comp, set(range(nc))))

    annot = OL.composantes_annotees(W0, W1, ent, comp, J.echelle_du_film(film), film)
    rng = np.random.default_rng(graine)
    # TOUTES les composantes annotees (ce sont les seules qui decident, ordre ZEUS)
    # plus un echantillon des autres, pour publier le terme de noeuds.
    ia = np.nonzero(annot)[0]
    io = np.nonzero(~annot)[0]
    if n_max and len(io) > n_max:
        io = np.sort(rng.choice(io, n_max, replace=False))
    choix = np.sort(np.concatenate([ia, io])) if len(ia) or len(io) else np.arange(0)
    cache0 = {}
    deltas = {}
    for c in choix:
        tr = tuple(OL.trames_de(comp, ent, W0, W1, int(c)))
        if tr not in cache0:
            cache0[tr] = ligne(OL.restreint(W0, tr))
        Mc = OL.monde_mixte(W0, W1, ent, m10, a0, a1, comp, {int(c)})
        ls = ligne(OL.restreint(Mc, tr))
        deltas[int(c)] = {k: ls[k] - cache0[tr][k] for k in CLES}

    # --- controle : n_verif composantes recalculees par le film ENTIER ---
    verif = {"n": 0, "exactes": 0, "ecarts": []}
    if len(choix):
        for c in rng.choice(choix, size=min(n_verif, len(choix)), replace=False):
            lf = ligne(OL.monde_mixte(W0, W1, ent, m10, a0, a1, comp, {int(c)}))
            df = {k: lf[k] - l0[k] for k in CLES}
            verif["n"] += 1
            if all(abs(df[k] - deltas[int(c)][k]) < 1e-9 for k in CLES):
                verif["exactes"] += 1
            else:
                verif["ecarts"].append({"composante": int(c), "entier": df,
                                        "restreint": deltas[int(c)]})
    tailles = np.bincount(comp, minlength=nc)
    return film, {
        "composantes_annotees": [bool(x) for x in annot],
        "n_noeuds_W0": W0.n_noeuds, "n_noeuds_W1": W1.n_noeuds,
        "n_aretes_W0": W0.n_aretes, "n_aretes_W1": W1.n_aretes,
        "n_entites": int(len(ent["type"])),
        "entites_par_type": {t: int((ent["type"] == t).sum()) for t in ("r", "a", "m")},
        "n_aretes_differentes": [int(len(d0)), int(len(d1))],
        "n_composantes": nc,
        "n_composantes_annotees": int(annot.sum()),
        "taille_composante": {"median": float(np.median(tailles)), "max": int(tailles.max()),
                              "p90": float(np.quantile(tailles, 0.9))},
        "n_composantes_mesurees": int(len(choix)),
        "ligne_W0": l0, "ligne_W1": l1, "ligne_toutes_composantes": lt,
        "deltas": {str(k): v for k, v in deltas.items()},
        "verification": verif,
        "secondes": round(time.perf_counter() - t0, 1),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--etiquette", required=True)
    ap.add_argument("--films", required=True)
    ap.add_argument("--w0", required=True, help="parquet:<racine> ou csv:<chemin>")
    ap.add_argument("--w1", required=True, help="parquet:<racine>, csv:<chemin> ou nms:<d>")
    ap.add_argument("--rayon", type=float, default=OL.RAYON_DEFAUT)
    ap.add_argument("--max-composantes-par-film", type=int, default=50)
    ap.add_argument("--tirages-nuls", type=int, default=40)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--graine", type=int, default=20260905)
    ap.add_argument("--verifications-par-film", type=int, default=6)
    ap.add_argument("--essai-de-machinerie", action="store_true")
    a = ap.parse_args()
    _idle()

    films = json.loads(pathlib.Path(a.films).read_text(encoding="utf-8"))["films"]
    t0 = time.perf_counter()
    taches = [(f, a.w0, a.w1, a.rayon, a.max_composantes_par_film, a.graine,
               a.verifications_par_film) for f in films]
    par_film = {}
    with Pool(min(a.workers, 24)) as p:
        for i, (f, r) in enumerate(p.imap_unordered(analyse_film, taches), 1):
            par_film[f] = r
            print(f"[{i}/{len(films)}] {f} : {r['n_entites']} entites, "
                  f"{r['n_composantes']} composantes, {r.get('n_composantes_mesurees', 0)} mesurees, "
                  f"{r.get('secondes', 0)} s", flush=True)

    base = {f: par_film[f]["ligne_W0"] for f in films}
    s0 = score_assiette(base)
    s1 = score_assiette({f: par_film[f]["ligne_W1"] for f in films})
    s_tout = score_assiette({f: par_film[f]["ligne_toutes_composantes"] for f in films})

    # --- delta de chaque composante mesuree, sur l assiette entiere ---
    def _sc(f, dd, cles):
        m = dict(base)
        m[f] = {**base[f], **{k: base[f][k] + (dd[k] if k in cles else 0.0) for k in CLES}}
        return score_assiette(m) - s0

    CLES_N = ("num_pred_nodes",)
    CLES_A = tuple(k for k in CLES if k not in CLES_N)
    deltas, deltas_n, deltas_a, annotee = {}, {}, {}, {}
    for f in films:
        an = par_film[f].get("composantes_annotees", [])
        for c, dd in par_film[f].get("deltas", {}).items():
            cle = f"{f}#{c}"
            deltas[cle] = _sc(f, dd, CLES)
            deltas_n[cle] = _sc(f, dd, CLES_N)
            deltas_a[cle] = _sc(f, dd, CLES_A)
            annotee[cle] = bool(an[int(c)]) if an else False
    dv = np.array(list(deltas.values())) if deltas else np.zeros(0)
    print(f"\nscore W0 {s0:.10f}   W1 {s1:.10f}   (toutes composantes prises {s_tout:.10f})")
    print(f"ecart mecanique |toutes composantes - W1| = {abs(s_tout - s1):.3e}")
    na = sum(1 for k in annotee if annotee[k])
    dva = np.array([deltas[k] for k in deltas if annotee[k]]) if na else np.zeros(0)
    print(f"{na} composantes mesurees TOUCHENT une annotation sur {len(dv)} "
          f"({100 * na / max(len(dv), 1):.1f} %)")
    print(f"  terme de NOEUDS total (publie a part, jamais utilise pour decider) : "
          f"{sum(deltas_n.values()):+.6f} sur toutes, "
          f"{sum(deltas_n[k] for k in deltas_n if annotee[k]):+.6f} sur les annotees")
    print(f"  terme d ARETES total : {sum(deltas_a.values()):+.6f} sur toutes, "
          f"{sum(deltas_a[k] for k in deltas_a if annotee[k]):+.6f} sur les annotees")
    print(f"{len(dv)} composantes mesurees : {int((dv > 0).sum())} positives, "
          f"{int((dv < 0).sum())} negatives, {int((dv == 0).sum())} nulles ; "
          f"somme des positives {dv[dv > 0].sum() if len(dv) else 0:+.6f}")

    # --- oracle local JOINT, re-juge entier ---
    positives = {}
    for cle, v in deltas.items():
        if annotee[cle] and v > 0:
            f, c = cle.split("#")
            positives.setdefault(f, set()).add(int(c))

    K = sum(len(v) for v in positives.values())
    rng = np.random.default_rng(a.graine)
    cles = [k for k in deltas if annotee[k]]   # MEME vivier que l oracle
    tirages = []
    for _ in range(a.tirages_nuls):
        pick = rng.choice(len(cles), size=min(K, len(cles)), replace=False)
        par_f = {}
        for k in pick:
            f, c = cles[k].split("#")
            par_f.setdefault(f, set()).add(int(c))
        tirages.append(par_f)

    # Un seul lot de re-jugements, DEDUPLIQUE et PARALLELE : le monde mixte d un
    # film ne depend que de l ensemble de composantes qu il porte.
    besoins = set()
    for f, cs in positives.items():
        besoins.add((f, frozenset(cs)))
    for par_f in tirages:
        for f, cs in par_f.items():
            besoins.add((f, frozenset(cs)))
    besoins = sorted(besoins, key=lambda x: (x[0], sorted(x[1])))
    print(f"{len(besoins)} mondes mixtes a juger (oracle + {a.tirages_nuls} tirages), "
          f"dedupliques", flush=True)
    par_film_lots = {}
    for f, cs in besoins:
        par_film_lots.setdefault(f, []).append(sorted(cs))
    jobs = [(f, a.w0, a.w1, a.rayon, lots) for f, lots in sorted(par_film_lots.items())]
    faits = {}
    with Pool(min(a.workers, 24)) as p:
        for n_, (f, res) in enumerate(p.imap_unordered(_rejuge_job, jobs), 1):
            for cs, l in res:
                faits[(f, frozenset(cs))] = l
            print(f"  [{n_}/{len(jobs)}] films re-juges ({len(res)} mondes mixtes)", flush=True)

    def _lignes(par_f):
        lg = dict(base)
        for f, cs in par_f.items():
            lg[f] = faits[(f, frozenset(cs))]
        return lg

    lignes_or = _lignes(positives)
    s_or = score_assiette(lignes_or)
    print(f"ORACLE LOCAL JOINT (re-juge entier, composantes ANNOTEES) : {s_or - s0:+.6f}   "
          f"({K} composantes)")

    nuls = [score_assiette(_lignes(par_f)) - s0 for par_f in tirages]
    q = np.quantile(nuls, [0.5, 0.95, 0.99]) if nuls else np.zeros(3)
    print(f"TEMOIN DE HASARD ({len(nuls)} tirages de {K} composantes parmi {len(cles)}) : "
          f"median {q[0]:+.6f}  95e {q[1]:+.6f}  99e {q[2]:+.6f}  -> "
          f"{'DEPASSE' if s_or - s0 > q[1] else 'ne depasse pas'}")

    # --- contributions par embryon, par substitution ---
    contrib = {}
    for e in sorted({f.split("_")[0] for f in films}):
        lg = dict(base)
        for f, cs in positives.items():
            if f.split("_")[0] == e:
                lg[f] = lignes_or[f]
        contrib[e] = score_assiette(lg) - s0
    print("contributions par substitution : " + "  ".join(f"{k} {v:+.6f}" for k, v in contrib.items()))

    seuil = 0.005
    au_dessus = (s_or - s0) > max(q[1], 0.0)
    verdict = ("ABANDON DEFINITIF du ciblage local pour ce geste" if (s_or - s0) < 0.003
               else ("DIAGNOSTIC SEULEMENT (BANK), rien ne se construit"
                     if (s_or - s0) < seuil else
                     ("ARBITRE LOCAL a ouvrir (decision de ZEUS)"
                      if (au_dessus and all(v > 0 for v in contrib.values()))
                      else "REFUSE : au-dessus de 0,005 mais pas au-dessus du hasard "
                           "ou une contribution d embryon est negative")))
    print("VERDICT (regle pre-enregistree, addendum section 3) : " + verdict)

    out = {
        "lane": "CIBLAGE", "objet": "oracle par composante de desaccord (tache D)",
        "date_u": date_u(), "etiquette": a.etiquette,
        "essai_de_machinerie": bool(a.essai_de_machinerie),
        "regime": "EVAL_ONLY ; la GT ne sert qu a mesurer",
        "W0": a.w0, "W1": a.w1, "rayon_appariement_um": a.rayon,
        "porte_um": OL.PORTE_UM, "n_films": len(films),
        "graine": a.graine,
        "score_W0": s0, "score_W1": s1,
        "score_toutes_composantes_prises": s_tout,
        "ecart_mecanique": abs(s_tout - s1),
        "delta_toujours": s1 - s0,
        "n_composantes_total": int(sum(par_film[f]["n_composantes"] for f in films)),
        "n_composantes_mesurees": int(len(dv)),
        "verification_de_l_acceleration": {
            "n": int(sum(par_film[f]["verification"]["n"] for f in films)),
            "exactes": int(sum(par_film[f]["verification"]["exactes"] for f in films)),
            "ecarts": [e for f in films for e in par_film[f]["verification"]["ecarts"]]},
        "composantes_annotees": int(sum(1 for k in annotee if annotee[k])),
        "regle": "l oracle, le temoin de hasard et les contributions ne portent QUE "
                 "sur les composantes qui touchent au moins une annotation ; le terme "
                 "de noeuds est publie a part et ne decide de rien (ordre ZEUS, 05/09)",
        "terme_de_noeuds": {"toutes": float(sum(deltas_n.values())),
                            "annotees": float(sum(deltas_n[k] for k in deltas_n if annotee[k]))},
        "terme_d_aretes": {"toutes": float(sum(deltas_a.values())),
                           "annotees": float(sum(deltas_a[k] for k in deltas_a if annotee[k]))},
        "composantes_positives": int((dv > 0).sum()),
        "composantes_negatives": int((dv < 0).sum()),
        "composantes_nulles": int((dv == 0).sum()),
        "somme_des_deltas_positifs": float(dv[dv > 0].sum()) if len(dv) else 0.0,
        "oracle_local_joint": s_or - s0,
        "part_du_film_le_plus_contributif": _part_max(base, lignes_or, s0, s_or),
        "temoin_de_hasard": {"n_tirages": len(nuls), "K": K,
                             "tire_parmi": len(cles), "median": float(q[0]),
                             "centile_95": float(q[1]), "centile_99": float(q[2]),
                             "depasse_le_95e": bool(s_or - s0 > q[1])},
        "contributions_par_embryon": contrib,
        "verdict": verdict,
        "secondes": round(time.perf_counter() - t0, 1),
        "deltas_par_composante": deltas,
        "deltas_terme_de_noeuds": deltas_n,
        "deltas_terme_d_aretes": deltas_a,
        "composante_annotee": annotee,
        "par_film": {f: {k: v for k, v in par_film[f].items() if k != "deltas"}
                     for f in films},
    }
    RECUS.mkdir(parents=True, exist_ok=True)
    p = RECUS / f"R_ORACLE_LOCAL_{a.etiquette}.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(f"[recu] {p}  ({out['secondes']} s)")


_PREP = {}


def _rejuge_job(job):
    """TOUS les mondes mixtes d UN film, dans un seul processus de travail.

    `prepare` (appariement + composantes) coute de 30 s a 450 s selon le film :
    il ne doit tourner QU UNE FOIS par film. Regrouper les jobs par film est donc
    la difference entre quelques minutes et plusieurs heures."""
    film, w0, w1, rayon, lots = job
    _idle()
    W0, W1, ent, m10, a0, a1, comp, nc, _ = prepare(film, w0, w1, rayon)
    out = []
    for cs in lots:
        out.append((tuple(cs),
                    ligne(OL.monde_mixte(W0, W1, ent, m10, a0, a1, comp, set(cs)))))
    return film, out


_CACHE = {}


def _rejuge(film, a, composantes_choisies):
    """Re-juge un film dans le monde mixte portant `composantes_choisies`."""
    cle = (film, tuple(sorted(composantes_choisies)))
    if cle in _CACHE:
        return _CACHE[cle]
    W0 = charge(film, a.w0)
    if a.w1.startswith("nms:"):
        W1 = nms_monde(W0, J.echelle_du_film(film), float(a.w1.split(":", 1)[1]))
    else:
        W1 = charge(film, a.w1)
    ech = J.echelle_du_film(film)
    m01, m10 = OL.appariement(W0, W1, ech, a.rayon)
    ent = OL.entites(W0, W1, m01, m10, ech)
    a0, a1, a1_p, d0, d1 = OL.aretes_differentes(W0, W1, m01, m10)
    comp, _, _ = OL.composantes(W0, W1, ent, a0, a1, a1_p, d0, d1, ech)
    r = ligne(OL.monde_mixte(W0, W1, ent, m10, a0, a1, comp, set(composantes_choisies)))
    _CACHE[cle] = r
    return r


def _part_max(base, lignes_or, s0, s_or):
    parts = {}
    for f in lignes_or:
        if lignes_or[f] is base[f]:
            continue
        m = dict(base)
        m[f] = lignes_or[f]
        parts[f] = score_assiette(m) - s0
    if not parts:
        return 0.0
    return float(max(parts.values()) / (s_or - s0)) if (s_or - s0) else 0.0


if __name__ == "__main__":
    main()
