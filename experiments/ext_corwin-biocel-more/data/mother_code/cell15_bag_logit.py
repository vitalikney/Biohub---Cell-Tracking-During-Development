# ENG/MOTHER -- CELL 15 IDENTITY REFERENCE: (film, t, z_um, y_um, x_um) -> bag logit.
# The v4 node head, five members, mean OF LOGITS. This is the whole recipe; anything
# a kernel cell does differently is a difference from the column of record.
#
# Modules (ship these three, from 10_CHANTIERS/20_MITOSE/impl/ in the repo -- NOT from
# another lane's tree on the volume): grille.py, normalisation.py, mh_net.py
# plus pp_crop.py from the ENG/PRIOR run's code/.
import numpy as np, torch, grille as G, pp_crop as C, mh_net

HALL = ["v4_node__hall_s%d__best_held_all.pt" % i for i in range(1, 6)]   # the five members


def load_bag(model_dir, device):
    """The five members. `strict=False` is the producer's own call (pp_v4score.load_head);
    a member missing a key is REFUSED rather than silently zero-initialised."""
    nets = []
    for name in HALL:
        blob = torch.load("%s/%s" % (model_dir, name), map_location=device,
                          weights_only=False)
        sd = blob["model"] if isinstance(blob, dict) and "model" in blob else blob
        net = mh_net.MitosisHead(in_channels=4, width=32)
        missing, _ = net.load_state_dict(sd, strict=False)
        if missing:
            raise SystemExit("REFUSED: %s missing %d keys" % (name, len(missing)))
        nets.append(net.eval().to(device))
    return nets


@torch.no_grad()
def bag_logit(nets, reader, t, p_um, device):
    """One mother -> one logit. `p_um` is (z_um, y_um, x_um) IN MICROMETRES, the float
    columns -- never the integer voxel ones, which disagree by up to 0,808 um.

    The lattice: micrometres -> native voxels -> the MITOSE grid (FACTEUR_XY = 2).
    The window: pp_crop.OFFSETS = (-2, -1, 0, +1) around t, clamped at the film's ends.
    The crop: (4, 11, 40, 40) float32, centred on the ROUNDED grid voxel.
    The normalisation: per-image p99, inside crop_from_film -- do not re-normalise.
    """
    grid = G.natif_vers_grille(G.um_vers_natif(np.asarray([p_um], dtype=np.float64)))
    reader.keep_only(set(C.clamped_frames(int(t), reader.n_frames)))
    crop, _ = C.crop_from_film(reader, int(t), grid[0])
    x = torch.from_numpy(
        np.ascontiguousarray(C.fed_view(crop), dtype=np.float32)[None]).to(device)
    with torch.autocast("cuda", dtype=torch.float16, enabled=(device.type == "cuda")):
        ys = [float(net(x).reshape(-1)[0]) for net in nets]
    return float(np.mean(ys))          # MEAN OF LOGITS, not of probabilities


if __name__ == "__main__":                      # the identity check, 20 mothers
    import polars as pl, sys
    MODELS = ("/workspace/STORE/20_MITOSE/models/"
              "20260907T2336Z__MIT__head-v2-predicted-candidates-seed-ensemble")
    ZARR = "/workspace/data_raw/competition/train"
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    nets = load_bag(MODELS, dev)
    t2 = pl.read_parquet("/workspace/STORE/ENGINE/prior_parent/mother_recus/"
                         "M3_FORK_MOTHER_LOGITS_V2.parquet").head(200)
    worst, n = 0.0, 0
    for film in t2["film"].unique().to_list():
        sub = t2.filter(pl.col("film") == film).head(4)
        pr = pl.read_parquet("/workspace/STORE/ENGINE/prior/%s.parquet" % film,
                             columns=["hyp_id", "t", "logit_bag"])
        ob = pl.read_parquet("/workspace/STORE/ENGINE/observe/%s.parquet" % film,
                             columns=["obs_id", "z_um", "y_um", "x_um"])
        reader = C.FilmReader(ZARR, film)
        for nid in sub["node_id"].to_list():
            r = pr.filter(pl.col("hyp_id") == nid)
            o = ob.filter(pl.col("obs_id") == nid)
            if not r.height or not o.height or r["logit_bag"][0] is None:
                continue
            got = bag_logit(nets, reader, r["t"][0],
                            (o["z_um"][0], o["y_um"][0], o["x_um"][0]), dev)
            d = abs(got - float(r["logit_bag"][0]))
            worst = max(worst, d); n += 1
            print("%-16s node %-10d bag %+8.4f  table %+8.4f  |d| %.5f"
                  % (film, nid, got, float(r["logit_bag"][0]), d), flush=True)
            if n >= 20:
                break
        if n >= 20:
            break
    print("IDENTITY on %d mothers: max |diff| = %.5f  (tolerance 0,026)" % (n, worst))
    sys.exit(0 if (n >= 20 and worst <= 0.026) else 1)
