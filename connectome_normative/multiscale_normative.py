#!/usr/bin/env python3
"""Multiscale normative modelling of structural connectomes (Ilioska et al. 2026 design).

Normative model per edge fit on controls; patients scored out-of-sample, controls by
K-fold CV. Extreme deviations (|z| > thr) are compared between two patient groups at
three scales: connections, nodes (deviation degree) and lateralised sublobes
(ipsilateral / contralateral to surgery). A node-strength normative model is run
alongside as the conventional comparator.

Inputs
  --matrices DIR     one N x N matrix per subject: <subject>.csv|.txt|.npy
  --labels CSV       columns: name, hemi (L/R/M), base (homolog key shared by the
                     L and R copy of a region), sublobe (hemisphere-free name);
                     row order = matrix order
  --covariates CSV   columns: subject, group, age, sex, op_side (L/R for patients),
                     optional site and any --extra-covariates
Run `--demo` for a synthetic end-to-end check.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

CONTROL = "control"


# ----------------------------------------------------------------------------- io

def load_matrix(path: Path) -> np.ndarray:
    if path.suffix == ".npy":
        return np.load(path)
    try:
        return np.loadtxt(path, delimiter=",")
    except ValueError:
        return np.loadtxt(path)


def load_inputs(mat_dir: Path, labels_csv: Path, cov_csv: Path):
    labels = pd.read_csv(labels_csv)
    cov = pd.read_csv(cov_csv)
    cov["subject"] = cov["subject"].astype(str)
    files = {p.stem: p for p in mat_dir.iterdir() if p.suffix in (".csv", ".txt", ".npy")}
    missing = [s for s in cov["subject"] if s not in files]
    if missing:
        raise SystemExit(f"{len(missing)} subjects lack a matrix, e.g. {missing[:5]}")
    W = np.stack([load_matrix(files[s]) for s in cov["subject"]]).astype(np.float64)
    if W.shape[1:] != (len(labels), len(labels)):
        raise SystemExit(f"matrix shape {W.shape[1:]} != {len(labels)} labels")
    return W, labels, cov


# -------------------------------------------------------------------- atlas logic

def norm_side(v) -> str | None:
    if pd.isna(v):
        return None
    v = str(v).strip().upper()
    return {"L": "L", "LEFT": "L", "R": "R", "RIGHT": "R"}.get(v)


def mirror_index(labels: pd.DataFrame) -> np.ndarray:
    """Index of each node's contralateral homolog (midline nodes map to themselves)."""
    key = {(h, b): i for i, (h, b) in enumerate(zip(labels["hemi"], labels["base"]))}
    out = np.empty(len(labels), dtype=int)
    for i, (h, b) in enumerate(zip(labels["hemi"], labels["base"])):
        if h == "M":
            out[i] = i
        else:
            other = (("R" if h == "L" else "L"), b)
            if other not in key:
                raise SystemExit(f"node {labels['name'][i]} has no homolog {other}")
            out[i] = key[other]
    return out


def canonical_nodes(labels: pd.DataFrame):
    """Canonical lateralised node list: ipsi_<base>, contra_<base>, mid_<base>."""
    bases_lr = labels.loc[labels["hemi"] != "M", ["base", "sublobe"]].drop_duplicates("base")
    bases_m = labels.loc[labels["hemi"] == "M", ["base", "sublobe"]]
    names, sub = [], []
    for side in ("ipsi", "contra"):
        for b, s in zip(bases_lr["base"], bases_lr["sublobe"]):
            names.append(f"{side}_{b}")
            sub.append(f"{side}_{s}")
    for b, s in zip(bases_m["base"], bases_m["sublobe"]):
        names.append(f"mid_{b}")
        sub.append(f"mid_{s}")
    return names, sub


def native_to_canonical(labels: pd.DataFrame, side: str) -> np.ndarray:
    names, _ = canonical_nodes(labels)
    pos = {n: i for i, n in enumerate(names)}
    out = np.empty(len(labels), dtype=int)
    for i, (h, b) in enumerate(zip(labels["hemi"], labels["base"])):
        lat = "mid" if h == "M" else ("ipsi" if h == side else "contra")
        out[i] = pos[f"{lat}_{b}"]
    return out


# ---------------------------------------------------------------- normative model

def design(cov: pd.DataFrame, ref: pd.DataFrame, extra: list[str], sites: list[str] | None):
    mu, sd = ref["age"].mean(), ref["age"].std(ddof=0) or 1.0
    a = (cov["age"].to_numpy(float) - mu) / sd
    sex = cov["sex"].astype(str).str.upper().str[0].map({"M": 1.0, "F": 0.0})
    if sex.isna().any():
        raise SystemExit("sex must be M/F")
    cols = [np.ones(len(cov)), a, a**2, sex.to_numpy()]
    for c in extra:
        m, s = ref[c].mean(), ref[c].std(ddof=0) or 1.0
        cols.append((cov[c].to_numpy(float) - m) / s)
    if sites:
        for s in sites[1:]:
            cols.append((cov["site"].astype(str) == s).to_numpy(float))
    return np.column_stack(cols)


def fit_predict_z(Xtr, Ytr, Xte, Yte):
    """Closed-form OLS per feature; z uses predictive SD including leverage."""
    XtX_inv = np.linalg.pinv(Xtr.T @ Xtr)
    B = XtX_inv @ Xtr.T @ Ytr
    dof = max(len(Xtr) - np.linalg.matrix_rank(Xtr), 1)
    sigma = np.sqrt(((Ytr - Xtr @ B) ** 2).sum(0) / dof)
    lev = np.einsum("ij,jk,ik->i", Xte, XtX_inv, Xte)
    with np.errstate(divide="ignore", invalid="ignore"):
        z = (Yte - Xte @ B) / (sigma[None, :] * np.sqrt(1.0 + lev)[:, None])
    z[:, sigma == 0] = np.nan
    return z


def normative_z(Y, X, is_ctrl, folds, rng):
    z = np.full(Y.shape, np.nan)
    ci = np.flatnonzero(is_ctrl)
    pi = np.flatnonzero(~is_ctrl)
    z[pi] = fit_predict_z(X[ci], Y[ci], X[pi], Y[pi])
    perm = rng.permutation(ci)
    for f in np.array_split(perm, folds):
        tr = np.setdiff1d(ci, f)
        z[f] = fit_predict_z(X[tr], Y[tr], X[f], Y[f])
    return z


# ------------------------------------------------------------------ inference

def bh(p):
    p = np.asarray(p, float)
    q = np.full_like(p, np.nan)
    ok = ~np.isnan(p)
    if ok.sum() == 0:
        return q
    pv = p[ok]
    o = np.argsort(pv)
    r = pv[o] * len(pv) / np.arange(1, len(pv) + 1)
    r = np.minimum.accumulate(r[::-1])[::-1]
    out = np.empty_like(pv)
    out[o] = np.minimum(r, 1)
    q[ok] = out
    return q


def perm_mean_diff(A, in_a, n_perm, rng, chunk=500):
    """Two-sided permutation test of mean(A[a]) - mean(A[b]) per column."""
    A = A.astype(np.float32)
    n, na = len(in_a), int(in_a.sum())
    nb = n - na

    def contrast(mask):
        return np.where(mask, 1.0 / na, -1.0 / nb).astype(np.float32)

    obs = contrast(in_a) @ A
    exceed = np.zeros(A.shape[1])
    done = 0
    while done < n_perm:
        c = min(chunk, n_perm - done)
        P = np.stack([contrast(rng.permutation(in_a)) for _ in range(c)])
        exceed += (np.abs(P @ A) >= np.abs(obs) - 1e-12).sum(0)
        done += c
    p = (exceed + 1) / (n_perm + 1)
    return obs, p


def overlap_auc_scores(values, thresholds):
    """Per-subject trapezoid AUC of indicator[value >= tau] over tau (S x K)."""
    ind = (values[..., None] >= np.asarray(thresholds)[None, None, :]).astype(float)
    return np.trapz(ind, x=thresholds, axis=-1)


def compare(scores, in_a, n_perm, rng, feature_names, label_a, label_b, extra_cols=None):
    obs, p = perm_mean_diff(scores, in_a, n_perm, rng)
    ma, mb = scores[in_a].mean(0), scores[~in_a].mean(0)
    with np.errstate(divide="ignore", invalid="ignore"):
        rel = np.where(mb > 0, (ma - mb) / mb, np.nan)
    df = pd.DataFrame({"feature": feature_names, f"value_{label_a}": ma,
                       f"value_{label_b}": mb, "diff": obs, "rel_diff": rel, "p": p})
    if extra_cols:
        for k, v in extra_cols.items():
            df[k] = v
    df["q_bh"] = bh(df["p"])
    return df.sort_values("p").reset_index(drop=True)


# -------------------------------------------------------------------- pipeline

def run(W, labels, cov, groups, out: Path, z_thr=2.3, min_frac=0.9, transform="log1p",
        folds=10, n_perm=10000, deg_thr=(1, 20), net_thr=(1, 10), extra=(), seed=0,
        vs_controls=False):
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    labels = labels.reset_index(drop=True)
    cov = cov.reset_index(drop=True).copy()
    cov["group"] = cov["group"].astype(str)
    is_ctrl = (cov["group"] == CONTROL).to_numpy()
    if is_ctrl.sum() < 20:
        raise SystemExit(f"only {is_ctrl.sum()} controls; need a reference cohort")
    for g in groups:
        if g not in set(cov["group"]):
            raise SystemExit(f"group {g!r} not found in covariates")

    cov["side"] = cov["op_side"].map(norm_side) if "op_side" in cov else None
    pat = ~is_ctrl
    if cov.loc[pat, "side"].isna().any():
        raise SystemExit("every patient needs op_side L or R")
    p_left = (cov.loc[pat, "side"] == "L").mean()
    cov.loc[is_ctrl, "side"] = np.where(rng.random(is_ctrl.sum()) < p_left, "L", "R")

    sites = None
    if "site" in cov and cov.loc[is_ctrl, "site"].nunique() > 1:
        sites = sorted(cov.loc[is_ctrl, "site"].astype(str).unique())
        unseen = set(cov["site"].astype(str)) - set(sites)
        if unseen:
            raise SystemExit(f"sites without controls: {unseen}")
    X = design(cov, cov[is_ctrl], list(extra), sites)

    N = len(labels)
    mir = mirror_index(labels)
    iu = np.triu_indices(N, 1)
    frac = (W[is_ctrl] > 0).mean(0)
    frac_sym = np.minimum(frac, frac[np.ix_(mir, mir)])
    keep_mat = frac_sym >= min_frac
    np.fill_diagonal(keep_mat, False)
    keep = keep_mat[iu]
    ei, ej = iu[0][keep], iu[1][keep]
    E = len(ei)
    if E == 0:
        raise SystemExit("no edges survive the consistency filter")

    Y = W[:, ei, ej]
    if transform == "log1p":
        Y = np.log1p(Y)
    strength = np.zeros((len(W), N))
    np.add.at(strength.T, ei, Y.T)
    np.add.at(strength.T, ej, Y.T)

    z_edge = normative_z(Y, X, is_ctrl, folds, rng)
    z_str = normative_z(strength, X, is_ctrl, folds, rng)

    cnames, csub = canonical_nodes(labels)
    C = len(cnames)
    maps = {s: native_to_canonical(labels, s) for s in ("L", "R")}
    ref_map = maps["L"]
    canon_pairs = np.sort(np.stack([ref_map[ei], ref_map[ej]], 1), 1)
    canon_key = {tuple(p): k for k, p in enumerate(canon_pairs)}
    if len(canon_key) != E:
        raise SystemExit("canonical edge mapping is not one-to-one")
    order = np.empty((len(W), E), dtype=int)
    for s, side in enumerate(cov["side"]):
        m = maps[side]
        pr = np.sort(np.stack([m[ei], m[ej]], 1), 1)
        order[s] = [canon_key[tuple(p)] for p in pr]
    zc = np.empty_like(z_edge)
    for s in range(len(W)):
        zc[s, order[s]] = z_edge[s]
    z_str_c = np.empty_like(z_str)
    for s, side in enumerate(cov["side"]):
        z_str_c[s, maps[side]] = z_str[s]
    edge_names = [f"{cnames[a]}--{cnames[b]}" for a, b in canon_pairs]

    sub_names = sorted(set(csub))
    sub_idx = np.array([sub_names.index(x) for x in csub])
    sa, sb = np.sort(np.stack([sub_idx[canon_pairs[:, 0]], sub_idx[canon_pairs[:, 1]]], 1), 1).T
    pair_list = sorted(set(zip(sa, sb)))
    pair_id = {p: k for k, p in enumerate(pair_list)}
    edge_pair = np.array([pair_id[(a, b)] for a, b in zip(sa, sb)])
    pair_names = [f"{sub_names[a]}::{sub_names[b]}" for a, b in pair_list]
    pair_kind = ["within" if a == b else "between" for a, b in pair_list]

    ctrl_z = z_edge[is_ctrl]
    expected = 2 * stats.norm.sf(z_thr)
    qc = {
        "n_subjects": int(len(W)), "n_controls": int(is_ctrl.sum()),
        "groups": {g: int((cov["group"] == g).sum()) for g in cov["group"].unique()},
        "n_nodes": N, "n_edges_kept": int(E), "n_edges_possible": int(len(iu[0])),
        "min_nonzero_frac": min_frac, "transform": transform, "z_thr": z_thr,
        "sites_modelled": sites, "extra_covariates": list(extra),
        "control_cv_z_mean": float(np.nanmean(ctrl_z)),
        "control_cv_z_sd": float(np.nanstd(ctrl_z)),
        "control_cv_extreme_frac": float(np.nanmean(np.abs(ctrl_z) > z_thr)),
        "expected_extreme_frac_gaussian": float(expected),
        "control_pseudo_side_p_left": float(p_left),
    }
    (out / "qc.json").write_text(json.dumps(qc, indent=2))
    np.savez_compressed(out / "deviations.npz", subjects=cov["subject"].to_numpy(),
                        z_edges_canonical=zc.astype(np.float32), edge_names=np.array(edge_names),
                        z_strength_canonical=z_str_c.astype(np.float32),
                        node_names=np.array(cnames))

    comparisons = [tuple(groups)]
    if vs_controls:
        comparisons += [(g, CONTROL) for g in groups]
    deg_t = np.arange(deg_thr[0], deg_thr[1] + 1)
    net_t = np.arange(net_thr[0], net_thr[1] + 1)
    summary = []

    for ga, gb in comparisons:
        sel = cov["group"].isin([ga, gb]).to_numpy()
        in_a = (cov.loc[sel, "group"] == ga).to_numpy()
        tag = f"{ga}_vs_{gb}"
        zs = zc[sel]
        row = {"comparison": tag, f"n_{ga}": int(in_a.sum()), f"n_{gb}": int((~in_a).sum())}

        for sign, ext in (("pos", np.nan_to_num(zs) > z_thr), ("neg", np.nan_to_num(zs) < -z_thr)):
            burden = ext.sum(1)
            u = stats.mannwhitneyu(burden[in_a], burden[~in_a], alternative="two-sided")
            row[f"burden_{sign}_median_{ga}"] = float(np.median(burden[in_a]))
            row[f"burden_{sign}_median_{gb}"] = float(np.median(burden[~in_a]))
            row[f"burden_{sign}_mannwhitney_p"] = float(u.pvalue)

            df = compare(ext.astype(float) * 100, in_a, n_perm, rng, edge_names, ga, gb)
            df.to_csv(out / f"{tag}_connections_{sign}.csv", index=False)
            row[f"conn_{sign}_max_overlap_pct"] = float(max(df.iloc[:, 1].max(), df.iloc[:, 2].max()))
            row[f"conn_{sign}_n_q05"] = int((df["q_bh"] < 0.05).sum())

            deg = np.zeros((len(zs), C))
            np.add.at(deg.T, canon_pairs[:, 0], ext.T)
            np.add.at(deg.T, canon_pairs[:, 1], ext.T)
            scores = overlap_auc_scores(deg, deg_t) * 100
            df = compare(scores, in_a, n_perm, rng, cnames, ga, gb,
                         {"sublobe": [csub[i] for i in range(C)]})
            df.to_csv(out / f"{tag}_nodes_{sign}.csv", index=False)
            row[f"node_{sign}_n_q05"] = int((df["q_bh"] < 0.05).sum())

            cnt = np.zeros((len(zs), len(pair_list)))
            np.add.at(cnt.T, edge_pair, ext.T)
            tot = cnt.sum(1, keepdims=True)
            pct = np.divide(cnt * 100, tot, out=np.zeros_like(cnt), where=tot > 0)
            scores = overlap_auc_scores(pct, net_t) * 100
            df = compare(scores, in_a, n_perm, rng, pair_names, ga, gb, {"kind": pair_kind})
            df.to_csv(out / f"{tag}_sublobes_{sign}.csv", index=False)
            row[f"sublobe_{sign}_n_q05"] = int((df["q_bh"] < 0.05).sum())

        pos, neg = (np.nan_to_num(zs) > z_thr).sum(1), (np.nan_to_num(zs) < -z_thr).sum(1)
        ratio = np.divide(pos, pos + neg, out=np.full(len(pos), 0.5), where=(pos + neg) > 0)
        t = stats.ttest_ind(ratio[in_a], ratio[~in_a], equal_var=False)
        row["pos_fraction_welch_p"] = float(t.pvalue)

        df = compare(z_str_c[sel], in_a, n_perm, rng, cnames, ga, gb,
                     {"sublobe": [csub[i] for i in range(C)]})
        df.rename(columns={f"value_{ga}": f"mean_z_{ga}", f"value_{gb}": f"mean_z_{gb}"}, inplace=True)
        df.drop(columns="rel_diff").to_csv(out / f"{tag}_node_strength_z.csv", index=False)
        row["strength_n_q05"] = int((df["q_bh"] < 0.05).sum())
        summary.append(row)

    pd.DataFrame(summary).to_csv(out / "summary.csv", index=False)
    return qc, summary


# ------------------------------------------------------------------------ demo

def make_demo(seed=1, n_ctrl=100, n_a=30, n_b=30, per_sub=4, effect=1.5):
    """Synthetic atlas + connectomes. Group A ('notSF1') loses a random subset of
    ipsilateral mesial<->lateral temporal edges per subject (heterogeneous
    connections, convergent sublobe pair)."""
    rng = np.random.default_rng(seed)
    sublobes = ["frontal_lat", "frontal_orb", "temporal_mes", "temporal_lat",
                "parietal", "occipital", "insula"]
    rows = []
    for h in ("L", "R"):
        for s in sublobes:
            for k in range(per_sub):
                rows.append({"name": f"{h}_{s}_{k}", "hemi": h, "base": f"{s}_{k}", "sublobe": s})
    rows.append({"name": "brainstem", "hemi": "M", "base": "brainstem", "sublobe": "brainstem"})
    labels = pd.DataFrame(rows)
    N = len(labels)
    sub_arr = labels["sublobe"].to_numpy()
    hemi = labels["hemi"].to_numpy()
    base = 2.0 + 2.0 * (sub_arr[:, None] == sub_arr[None, :]) + 1.0 * (hemi[:, None] == hemi[None, :])
    base = (base + base.T) / 2
    groups = [CONTROL] * n_ctrl + ["notSF1"] * n_a + ["durable"] * n_b
    S = len(groups)
    age = rng.uniform(18, 60, S)
    sex = rng.choice(["M", "F"], S)
    side = [None if g == CONTROL else rng.choice(["L", "R"]) for g in groups]
    W = np.zeros((S, N, N))
    for s in range(S):
        lw = base - 0.01 * (age[s] - 40) + rng.normal(0, 0.35, (N, N))
        lw = (lw + lw.T) / 2
        if groups[s] == "notSF1":
            ipsi = side[s]
            mes = np.flatnonzero((sub_arr == "temporal_mes") & (hemi == ipsi))
            lat = np.flatnonzero((sub_arr == "temporal_lat") & (hemi == ipsi))
            pairs = [(i, j) for i in mes for j in lat]
            for k in rng.choice(len(pairs), size=3, replace=False):
                i, j = pairs[k]
                lw[i, j] -= effect
                lw[j, i] -= effect
        w = np.expm1(np.clip(lw, 0, None) * 1.5)
        w[rng.random((N, N)) < 0.02] = 0
        w = np.triu(w, 1)
        W[s] = w + w.T
    cov = pd.DataFrame({"subject": [f"s{s:03d}" for s in range(S)], "group": groups,
                        "age": age, "sex": sex, "op_side": side})
    return W, labels, cov


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--matrices", type=Path)
    ap.add_argument("--labels", type=Path)
    ap.add_argument("--covariates", type=Path)
    ap.add_argument("--groups", nargs=2, default=["notSF1", "durable"],
                    help="two patient group labels to compare (group A, group B)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--z-thr", type=float, default=2.3)
    ap.add_argument("--min-frac", type=float, default=0.9,
                    help="keep edges non-zero in >= this fraction of controls (mirror-symmetric)")
    ap.add_argument("--transform", choices=["log1p", "none"], default="log1p")
    ap.add_argument("--folds", type=int, default=10)
    ap.add_argument("--n-perm", type=int, default=10000)
    ap.add_argument("--deg-thr", type=int, nargs=2, default=[1, 20])
    ap.add_argument("--net-thr", type=int, nargs=2, default=[1, 10])
    ap.add_argument("--extra-covariates", nargs="*", default=[])
    ap.add_argument("--vs-controls", action="store_true", help="also test each group vs controls")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()

    if a.demo:
        W, labels, cov = make_demo()
    else:
        if not (a.matrices and a.labels and a.covariates):
            ap.error("--matrices, --labels and --covariates are required (or --demo)")
        W, labels, cov = load_inputs(a.matrices, a.labels, a.covariates)

    qc, summary = run(W, labels, cov, a.groups, a.out, a.z_thr, a.min_frac, a.transform,
                      a.folds, a.n_perm, tuple(a.deg_thr), tuple(a.net_thr),
                      a.extra_covariates, a.seed, a.vs_controls)
    print(json.dumps(qc, indent=2))
    print(pd.DataFrame(summary).T.to_string(header=False))


if __name__ == "__main__":
    main()
