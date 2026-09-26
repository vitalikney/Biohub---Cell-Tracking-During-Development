# -*- coding: utf-8 -*-
"""CANONISATION -- la DERNIERE etape de cell08, jamais avant l etage.

POURQUOI ELLE EST DANS LE NOYAU (ordre de ZEUS, 05/09 12:3xZ)
-------------------------------------------------------------
Le juge officiel n est PAS invariant a l ordre des lignes. Deux mondes portant
exactement les MEMES noeuds et les MEMES aretes rendent deux scores : ETAGE l a
mesure a **+1,32e-04** sur 60 films (0,8748216087 -> 0,8749536413), 44b6 ne
bougeant pas d un bit et 6bba portant tout l ecart. C est 14 % du Delta d un
reglage qui a coute une lane entiere. Le noyau Kaggle ne canonise pas.

C est un REORDONNANCEMENT PUR : memes noeuds, memes aretes, aucune valeur
reformatee, seule la colonne `id` (un index de ligne que le juge ne lit pas)
est renumerotee. Le gain n est donc pas un pari : c est la suppression d un
degre de liberte qui nous coutait, en moyenne, la moitie de son amplitude.

ELLE FERME AUSSI LA BOUCLE DES DEUX ROUTES. `oracle_local.monde_mixte` fusionne
les ordres d aretes de W0 et de W1 ; `cell08_referee` ecrit les aretes ajoutees
a la fin du bloc du film. Les deux mondes ont les memes noeuds et les memes
aretes, et deux ordres. Canonises, ils sont IDENTIQUES -- donc le Delta mesure
par la substitution exacte de CIBLAGE est EXACTEMENT celui du monde soumis.
Sans canonisation, ce transfert serait approche a 1,3e-04 pres, c est-a-dire du
meme ordre que le gain cherche.

LA REGLE est celle de `ETAGE/impl/pod/canoniser.py`, reprise TERME A TERME (ce
module la rend appelable ; il ne la modifie pas). Le controle `--parite` prouve
l egalite AU BIT avec le script d ETAGE sur un fichier reel.

  1. les films gardent l ordre du fichier d entree (ils sont deja contigus) ;
  2. dans un film, TOUTES les lignes `node` d abord, triees par (t, z, y, x)
     puis, a cle egale, par node_id -- tri TOTAL, aucun ex aequo ;
  3. puis toutes les lignes `edge`, triees par (cle(source), cle(cible)) ou
     `cle(n)` est le (t, z, y, x) du noeud n ; a cle egale, par
     (source_id, target_id) ;
  4. la colonne `id` est renumerotee 0..N-1 sur tout le fichier.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import cell08_referee as R  # noqa: E402


def canonise_csv(src, dst) -> dict:
    """Ecrit la forme canonique de `src` dans `dst`. Rend un rapport."""
    src, dst = pathlib.Path(src), pathlib.Path(dst)
    t0 = time.perf_counter()
    with open(src, "r", encoding="utf-8") as f:
        entete = f.readline()
        cols = entete.rstrip("\r\n").split(",")
        i_id, i_film, i_kind = (cols.index("id"), cols.index("dataset"),
                                cols.index("row_type"))
        i_nid, i_t = cols.index("node_id"), cols.index("t")
        i_z, i_y, i_x = cols.index("z"), cols.index("y"), cols.index("x")
        i_s, i_g = cols.index("source_id"), cols.index("target_id")
        ordre, par_film = [], {}
        for ligne in f:
            p = ligne.rstrip("\r\n").split(",")
            film = p[i_film]
            if film not in par_film:
                par_film[film] = ([], [])
                ordre.append(film)
            par_film[film][0 if p[i_kind] == "node" else 1].append(p)

    n_out = 0
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "w", encoding="utf-8", newline="") as fo:
        fo.write(entete)
        for film in ordre:
            noeuds, aretes = par_film[film]

            def cle_n(p):
                return (float(p[i_t]), float(p[i_z]), float(p[i_y]),
                        float(p[i_x]), int(p[i_nid]))

            noeuds.sort(key=cle_n)
            pos = {int(p[i_nid]): cle_n(p)[:4] for p in noeuds}
            manquants = [p for p in aretes
                         if int(p[i_s]) not in pos or int(p[i_g]) not in pos]
            if manquants:
                raise SystemExit(
                    "[canonisation] ARETE CITANT UN NOEUD ABSENT dans %s : %d"
                    % (film, len(manquants)))
            aretes.sort(key=lambda p: (pos[int(p[i_s])], pos[int(p[i_g])],
                                       int(p[i_s]), int(p[i_g])))
            for p in noeuds + aretes:
                p[i_id] = str(n_out)
                n_out += 1
                fo.write(",".join(p) + "\n")
    return {"n_films": len(ordre), "n_lignes": n_out,
            "s_canonisation": round(time.perf_counter() - t0, 2),
            "sha256_in": R.sha256_fichier(src),
            "sha256_out": R.sha256_fichier(dst),
            "s_par_film": round((time.perf_counter() - t0) / max(1, len(ordre)), 4)}


def memes_lignes(a, b) -> dict:
    """Deux CSV portent-ils les MEMES noeuds et les MEMES aretes (ordre libre) ?

    C est la preuve qu une canonisation n a rien ajoute ni retire. On compare
    des MULTI-ENSEMBLES de lignes SANS la colonne `id` : si un seul champ avait
    ete reformate, l egalite tomberait.
    """
    def sacs(path):
        n, e = {}, {}
        with open(path, "rb") as f:
            f.readline()
            for line in f:
                p = line.rstrip(b"\r\n").split(b",")
                d = n if p[2] == b"node" else e
                cle = b",".join(p[1:])
                d[cle] = d.get(cle, 0) + 1
        return n, e
    na, ea = sacs(a)
    nb, eb = sacs(b)
    return {"memes_noeuds": na == nb, "memes_aretes": ea == eb,
            "n_noeuds": [sum(na.values()), sum(nb.values())],
            "n_aretes": [sum(ea.values()), sum(eb.values())]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--dest", required=True)
    ap.add_argument("--parite", action="store_true",
                    help="compare AU BIT avec ETAGE/impl/pod/canoniser.py")
    ap.add_argument("--recu", default=None)
    a = ap.parse_args()
    rap = canonise_csv(a.csv, a.dest)
    rap["memes_lignes_que_l_entree"] = memes_lignes(a.csv, a.dest)
    rap["sha_different"] = rap["sha256_in"] != rap["sha256_out"]
    if a.parite:
        import subprocess
        ref = pathlib.Path(a.dest).with_suffix(".ETAGE.csv")
        script = ICI.parents[2] / "ETAGE" / "impl" / "pod" / "canoniser.py"
        subprocess.run([sys.executable, str(script), str(a.csv), str(ref)],
                       check=True)
        rap["parite_avec_ETAGE"] = {
            "script": str(script), "sha_ETAGE": R.sha256_fichier(ref),
            "sha_REFEVAL": rap["sha256_out"],
            "AU_BIT": R.sha256_fichier(ref) == rap["sha256_out"]}
    rap["date_u"] = R.date_u()
    print(json.dumps(rap, ensure_ascii=False, indent=1))
    if a.recu:
        p = pathlib.Path(a.recu)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rap, ensure_ascii=False, indent=1),
                     encoding="utf-8")
        print("[recu] " + str(p))


if __name__ == "__main__":
    main()
