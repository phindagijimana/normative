#!/usr/bin/env python3
"""MFPR with the control offset vs MFPR with mu_hat = 0.

Six contrasts on the same CentileBrain MFP scores:
  1. Control (and patient) mean and SD of Z
  2. |Z| > 1.96 call agreement on patients
  3. Control tail rate
  4. Per-region Pearson r of each version vs IDEAS ComBat Z
  5. Lateralisation accuracy (McNemar) and resection Spearman rho (Wilcoxon)
  6. Sex difference in the offset, in Z units
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import binomtest, pearsonr, spearmanr, wilcoxon

REPO = Path(__file__).resolve().parents[1]

SCORE = REPO / "score"
IDEAS = REPO / "ideas_data"
SHARE = REPO / "CentileShare" / "hypothesis"
THRESH = 1.96
FIG_DIRS = [
    REPO / "manuscript" / "figures",
    REPO / "CentileShare" / "hypothesis" / "figures",
    REPO / "CentileShare" / "compare" / "figures",
]


def write(name: str, df: pd.DataFrame) -> None:
    for d in (SCORE, SHARE):
        d.mkdir(parents=True, exist_ok=True)
        path = d / name
        df.to_csv(path, index=False)
        print(f"wrote {path}")


def cohen_kappa(a: np.ndarray, b: np.ndarray) -> float:
    a = a.astype(bool)
    b = b.astype(bool)
    p0 = float((a == b).mean())
    pe = float(a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean()))
    if pe >= 1.0:
        return 1.0 if p0 >= 1.0 else 0.0
    return (p0 - pe) / (1 - pe)


def hemi_of(region: str) -> str | None:
    if str(region).startswith("lh_"):
        return "L"
    if str(region).startswith("rh_"):
        return "R"
    return None


def load_mfp() -> pd.DataFrame:
    df = pd.read_csv(SCORE / "ideas_zscores_centilebrain.csv")
    df["subject_id"] = df["subject_id"].astype(int)
    df["z_with"] = df["z"]
    df["z_without"] = (df["observed"] - df["predicted"]) / df["rmse_m"]
    return df


def summarise_z(df: pd.DataFrame, cohort: str) -> pd.DataFrame:
    rows = []
    sub = df[df["cohort"] == cohort]
    for measure, g in sub.groupby("measure"):
        for label, col in (("with", "z_with"), ("without", "z_without")):
            by = g.groupby("region")[col]
            mean_r = by.mean()
            sd_r = by.std()
            rows.append({
                "cohort": cohort,
                "measure": measure,
                "version": label,
                "n_regions": int(mean_r.shape[0]),
                "n_subjects": int(g["subject_id"].nunique()),
                "median_region_mean_z": float(mean_r.median()),
                "median_region_sd_z": float(sd_r.median()),
                "cell_mean_z": float(g[col].mean()),
                "cell_sd_z": float(g[col].std()),
            })
    return pd.DataFrame(rows)


def region_calibration(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    ctl = df[df["cohort"] == "control"]
    for (measure, region), g in ctl.groupby(["measure", "region"]):
        rows.append({
            "measure": measure,
            "region": region,
            "n": int(len(g)),
            "mean_with": float(g["z_with"].mean()),
            "sd_with": float(g["z_with"].std()),
            "mean_without": float(g["z_without"].mean()),
            "sd_without": float(g["z_without"].std()),
            "shift_z": float((g["z_without"] - g["z_with"]).mean()),
        })
    return pd.DataFrame(rows)


def call_agreement(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    pat = df[df["cohort"] == "patient"]
    for measure, g in pat.groupby("measure"):
        a = (g["z_with"].abs() > THRESH).to_numpy()
        b = (g["z_without"].abs() > THRESH).to_numpy()
        rows.append({
            "cohort": "patient",
            "measure": measure,
            "threshold": THRESH,
            "n_cells": int(len(a)),
            "n_subjects": int(g["subject_id"].nunique()),
            "n_regions": int(g["region"].nunique()),
            "pct_agree": float((a == b).mean()),
            "cohen_kappa": cohen_kappa(a, b),
            "rate_with": float(a.mean()),
            "rate_without": float(b.mean()),
            "pct_with_only": float((a & ~b).mean()),
            "pct_without_only": float((~a & b).mean()),
            "pct_both": float((a & b).mean()),
        })
    return pd.DataFrame(rows)


def tail_rates(df: pd.DataFrame) -> pd.DataFrame:
    ctl = df[df["cohort"] == "control"]
    rows = []
    for (measure, region), g in ctl.groupby(["measure", "region"]):
        rows.append({
            "measure": measure,
            "region": region,
            "n": int(len(g)),
            "tail_with": float((g["z_with"].abs() > THRESH).mean()),
            "tail_without": float((g["z_without"].abs() > THRESH).mean()),
        })
    per = pd.DataFrame(rows)
    summary = (
        per.groupby("measure")
        .agg(
            n_regions=("region", "nunique"),
            median_tail_with=("tail_with", "median"),
            median_tail_without=("tail_without", "median"),
            mean_tail_with=("tail_with", "mean"),
            mean_tail_without=("tail_without", "mean"),
        )
        .reset_index()
    )
    return per, summary


def vs_ideas(df: pd.DataFrame) -> pd.DataFrame:
    files = {
        "thickness": IDEAS / "thick_zscores_patients.csv",
        "area": IDEAS / "area_zscores_patients.csv",
        "subcortical": IDEAS / "vol_zscores_patients.csv",
    }
    rows = []
    pat = df[df["cohort"] == "patient"]
    for measure, path in files.items():
        ideas = pd.read_csv(path).rename(columns={"ID": "subject_id"})
        ideas["subject_id"] = ideas["subject_id"].astype(int)
        if measure == "subcortical":
            # IDEAS uses Left_Thalamus_volume; MFP uses Left-Thalamus.
            rename = {}
            for hemi in ("Left", "Right"):
                for region in ("Thalamus", "Caudate", "Putamen", "Pallidum",
                               "Hippocampus", "Amygdala", "Accumbens-area"):
                    old = f"{hemi}_{region.replace('-', '_')}_volume"
                    rename[old] = f"{hemi}-{region}"
            ideas = ideas.rename(columns=rename)
        long = ideas.melt(id_vars="subject_id", var_name="region", value_name="z_ideas")
        ours = pat[pat["measure"] == measure][
            ["subject_id", "region", "z_with", "z_without"]
        ]
        joined = ours.merge(long, on=["subject_id", "region"], how="inner")
        for region, g in joined.groupby("region"):
            g = g.dropna()
            if len(g) < 20:
                continue
            r_with, _ = pearsonr(g["z_with"], g["z_ideas"])
            r_without, _ = pearsonr(g["z_without"], g["z_ideas"])
            rows.append({
                "measure": measure,
                "region": region,
                "n": int(len(g)),
                "r_with": r_with,
                "r_without": r_without,
            })
    return pd.DataFrame(rows)


def plot_vs_ideas(tab: pd.DataFrame) -> None:
    thick = tab[tab["measure"] == "thickness"]
    fig, ax = plt.subplots(figsize=(6.5, 4.5), dpi=300)
    bins = np.linspace(0.4, 1.0, 25)
    series = (
        ("r_with", "#d62728", "MFPR with controls"),
        ("r_without", "#ff7f0e", "MFPR without controls"),
    )
    for col, color, label in series:
        vals = thick[col].to_numpy()
        median = float(np.median(vals))
        ax.hist(
            vals, bins=bins, color=color, alpha=0.55,
            edgecolor="white", linewidth=0.7,
            label=f"{label} (median r = {median:.2f}, N = {len(vals)})",
        )
        ax.axvline(median, color=color, linestyle=":", linewidth=1.2)
    ax.set_xlabel("Per-region Pearson r vs. IDEAS-internal ComBat Z-scores", fontsize=10)
    ax.set_ylabel("Number of Desikan–Killiany cortical thickness regions", fontsize=10)
    ax.set_xlim(0.4, 1.0)
    ax.tick_params(labelsize=9)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(loc="upper left", fontsize=8, frameon=False)
    fig.tight_layout()
    for d in FIG_DIRS:
        d.mkdir(parents=True, exist_ok=True)
        fig.savefig(d / "figure_mfpr_vs_ideas_with_without.png", dpi=300)
        fig.savefig(d / "figure_mfpr_vs_ideas_with_without.pdf")
        print(f"wrote {d / 'figure_mfpr_vs_ideas_with_without.png'}")
    plt.close(fig)


def lateralise(z: pd.DataFrame, col: str, meta: pd.DataFrame) -> pd.DataFrame:
    t = z[(z["cohort"] == "patient") & (z["measure"] == "thickness")].copy()
    t["hemi"] = t["region"].map(hemi_of)
    t = t[t["hemi"].isin(["L", "R"])]
    t["abs_z"] = t[col].abs()
    hemi = t.groupby(["subject_id", "hemi"])["abs_z"].mean().unstack("hemi")
    hemi["pred_side"] = np.where(hemi["L"] > hemi["R"], "L", "R")
    merged = hemi.reset_index().merge(
        meta[["subject_id", "Op_Side"]], on="subject_id", how="inner"
    )
    merged = merged[merged["Op_Side"].isin(["L", "R"])].copy()
    merged["correct"] = merged["pred_side"] == merged["Op_Side"]
    return merged[["subject_id", "Op_Side", "pred_side", "correct"]]


def resection_rho_by_subject(z_frame: pd.DataFrame, col: str) -> pd.Series:
    res = pd.read_csv(IDEAS / "table_resected.csv")
    res = res.rename(columns={res.columns[0]: "region"})
    res["region"] = res["region"].astype(str).str.strip("'")

    def normalise(name: str) -> str:
        name = str(name).strip()
        if name.startswith("ctx-lh-"):
            return f"lh_{name[len('ctx-lh-'):]}"
        if name.startswith("ctx-rh-"):
            return f"rh_{name[len('ctx-rh-'):]}"
        return name.replace("-Proper", "")

    res["key"] = res["region"].map(normalise)
    res_long = res.melt(id_vars=["region", "key"], var_name="subject_id",
                        value_name="resected_frac")
    res_long["subject_id"] = res_long["subject_id"].astype(int)
    res_long = res_long[res_long["resected_frac"] > 0]

    z = z_frame[z_frame["measure"] == "thickness"].copy()
    z["key"] = z["region"].map(lambda r: "_".join(str(r).split("_")[:2]))
    z["abs_z"] = z[col].abs()
    z_per = z.groupby(["subject_id", "key"])["abs_z"].max()
    rhos = {}
    for sid, rsub in res_long.groupby("subject_id"):
        if sid not in z_per.index.get_level_values(0):
            continue
        zsub = z_per.loc[sid]
        keys = zsub.index
        zv = zsub.reindex(keys).to_numpy()
        rv = rsub.drop_duplicates("key").set_index("key")["resected_frac"].reindex(keys, fill_value=0).to_numpy()
        if np.all(rv == 0) or np.all(np.isnan(zv)):
            continue
        rho, _ = spearmanr(zv, rv)
        if np.isnan(rho):
            continue
        rhos[int(sid)] = float(rho)
    return pd.Series(rhos, name=col)


def sex_offset(df: pd.DataFrame, pooled_r: pd.DataFrame) -> pd.DataFrame:
    # One shift per region x sex. Constant within the block.
    shift = (
        df.groupby(["measure", "region", "sex"])
        .apply(lambda g: float((g["z_without"] - g["z_with"]).mean()), include_groups=False)
        .rename("shift_z")
        .reset_index()
    )
    wide = shift.pivot_table(index=["measure", "region"], columns="sex", values="shift_z")
    wide = wide.reset_index()
    wide["abs_sex_diff_z"] = (wide["F"] - wide["M"]).abs()
    thick_r = pooled_r.rename(columns={"r": "pooled_r"})
    out = wide.merge(thick_r, on=["measure", "region"], how="left")
    return out


def main() -> None:
    df = load_mfp()
    # Sanity: without-controls Z matches (observed - predicted) / RMSE.
    chk = df.dropna(subset=["z_with", "z_without"])
    shift = (chk["z_without"] - chk["z_with"]) - (chk["mu_hat"] / chk["rmse_m"])
    print(f"max |shift - mu_hat/RMSE| = {shift.abs().max():.3e}")

    cal = summarise_z(df, "control")
    cal = pd.concat([cal, summarise_z(df, "patient")], ignore_index=True)
    print("\n=== Calibration ===")
    print(cal.to_string(index=False, float_format="%.3f"))
    write("mfpr_controls_calibration.csv", cal)
    write("mfpr_controls_calibration_by_region.csv", region_calibration(df))

    calls = call_agreement(df)
    print("\n=== |Z|>1.96 agreement (patients) ===")
    print(calls.to_string(index=False, float_format="%.3f"))
    write("mfpr_controls_call_agreement.csv", calls)

    tails, tail_sum = tail_rates(df)
    print("\n=== Control tail rate (|Z|>1.96), median across regions ===")
    print(tail_sum.to_string(index=False, float_format="%.3f"))
    write("mfpr_controls_tail_rate_by_region.csv", tails)
    write("mfpr_controls_tail_rate.csv", tail_sum)

    ideas = vs_ideas(df)
    print("\n=== vs IDEAS ComBat Z ===")
    for measure, g in ideas.groupby("measure"):
        print(
            f"  {measure}: N={len(g)}  "
            f"median r with={g['r_with'].median():.3f}  "
            f"without={g['r_without'].median():.3f}  "
            f"median (with-without)={(g['r_with'] - g['r_without']).median():.3f}"
        )
    write("mfpr_controls_vs_ideas_r.csv", ideas)
    plot_vs_ideas(ideas)

    meta = pd.read_csv(IDEAS / "Metadata_Release_Anon.csv").rename(columns={"ID": "subject_id"})
    meta = meta.drop_duplicates("subject_id")
    meta["subject_id"] = meta["subject_id"].astype(int)
    lat_with = lateralise(df, "z_with", meta).rename(columns={"correct": "correct_with", "pred_side": "pred_with"})
    lat_without = lateralise(df, "z_without", meta).rename(columns={"correct": "correct_without", "pred_side": "pred_without"})
    lat = lat_with.merge(lat_without[["subject_id", "correct_without", "pred_without"]], on="subject_id")
    both_right = int((lat["correct_with"] & lat["correct_without"]).sum())
    with_only = int((lat["correct_with"] & ~lat["correct_without"]).sum())
    without_only = int((~lat["correct_with"] & lat["correct_without"]).sum())
    n_disc = with_only + without_only
    mcnemar_p = float(binomtest(with_only, n_disc, 0.5).pvalue) if n_disc else float("nan")
    lat_sum = pd.DataFrame([{
        "n": int(len(lat)),
        "accuracy_with": float(lat["correct_with"].mean()),
        "accuracy_without": float(lat["correct_without"].mean()),
        "n_with_only_correct": with_only,
        "n_without_only_correct": without_only,
        "n_both_correct": both_right,
        "mcnemar_p": mcnemar_p,
    }])
    print("\n=== Lateralisation (thickness, Op_Side L/R) ===")
    print(lat_sum.to_string(index=False, float_format="%.4f"))
    write("mfpr_controls_lateralisation.csv", lat_sum)

    print("\nResection rho (thickness)...")
    rho_with = resection_rho_by_subject(df[df["cohort"] == "patient"], "z_with")
    rho_without = resection_rho_by_subject(df[df["cohort"] == "patient"], "z_without")
    both = pd.concat([rho_with.rename("rho_with"), rho_without.rename("rho_without")], axis=1).dropna()
    diff = both["rho_with"] - both["rho_without"]
    w = wilcoxon(both["rho_with"], both["rho_without"], zero_method="wilcox")
    res_sum = pd.DataFrame([{
        "n": int(len(both)),
        "mean_rho_with": float(both["rho_with"].mean()),
        "mean_rho_without": float(both["rho_without"].mean()),
        "median_rho_with": float(both["rho_with"].median()),
        "median_rho_without": float(both["rho_without"].median()),
        "frac_pos_with": float((both["rho_with"] > 0).mean()),
        "frac_pos_without": float((both["rho_without"] > 0).mean()),
        "median_paired_diff": float(diff.median()),
        "wilcoxon_stat": float(w.statistic),
        "wilcoxon_p": float(w.pvalue),
    }])
    print(res_sum.to_string(index=False, float_format="%.4f"))
    write("mfpr_controls_resection.csv", res_sum)

    pooled = pd.read_csv(SCORE / "mfpr_with_vs_without_r.csv")
    sex = sex_offset(df, pooled)
    thick = sex[sex["measure"] == "thickness"].dropna(subset=["pooled_r"])
    r_link, p_link = spearmanr(thick["abs_sex_diff_z"], thick["pooled_r"])
    sex_sum = pd.DataFrame([{
        "measure": measure,
        "n_regions": int(len(g)),
        "median_abs_sex_diff_z": float(g["abs_sex_diff_z"].median()),
        "max_abs_sex_diff_z": float(g["abs_sex_diff_z"].max()),
    } for measure, g in sex.groupby("measure")])
    print("\n=== |female shift − male shift| in Z units ===")
    print(sex_sum.to_string(index=False, float_format="%.3f"))
    print(f"thickness Spearman(|sex diff|, pooled r) = {r_link:.3f}  p = {p_link:.3e}")
    write("mfpr_controls_sex_offset.csv", sex)
    write("mfpr_controls_sex_offset_summary.csv", sex_sum)
    print("\nDone.")


if __name__ == "__main__":
    main()
