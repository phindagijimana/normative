#!/usr/bin/env python3
"""One fair three-way table: MFP vs GAMLSS vs PCN on cortical thickness.

PCN only scores 68 thickness regions, so every metric here uses that
intersection. Pairwise Pearson r lives in pearson_r_all_pairs_*.csv;
this script stacks per-backend metrics (calibration, vs-IDEAS, AUC,
resection) and the three pairwise r values into two summary CSVs.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent
REPO = Path("/mnt/nfs/home/URMC-SH/pndagiji/Documents/Normative")
if not REPO.exists():
    REPO = Path("/mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/Documents/Normative")

Z_DIR = BUNDLE / "CentileBrain"
if not (Z_DIR / "ideas_zscores_centilebrain.csv").exists():
    Z_DIR = REPO / "score"

RES_PATH = REPO / "ideas_data" / "table_resected.csv"
if not RES_PATH.exists():
    RES_PATH = BUNDLE / "IDEAS_Data" / "table_resected.csv"

OUT_DIRS = [HERE]
score_out = REPO / "score"
if score_out.exists() and score_out.resolve() != HERE.resolve():
    OUT_DIRS.append(score_out)


def write_all(name: str, df: pd.DataFrame) -> None:
    for d in OUT_DIRS:
        df.to_csv(d / name, index=False)
        print(f"  wrote {d / name}")


def load_z(name: str) -> pd.DataFrame:
    df = pd.read_csv(Z_DIR / name,
                     usecols=["subject_id", "cohort", "measure", "region", "z"])
    df["subject_id"] = df["subject_id"].astype(int)
    return df[df["measure"] == "thickness"].copy()


# ---- fair thickness-only resection ρ ---------------------------------------
def resection_rho(z_frame: pd.DataFrame) -> np.ndarray:
    res = pd.read_csv(RES_PATH)
    res = res.rename(columns={"Unnamed: 0": "region"})
    res["region"] = res["region"].str.strip("'")

    def normalise(name):
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

    z = z_frame.copy()
    z["key"] = z["region"].map(lambda r: "_".join(str(r).split("_")[:2]))
    z["abs_z"] = z["z"].abs()
    z_per = z.groupby(["subject_id", "key"])["abs_z"].max().reset_index()
    rhos = []
    for sid, rsub in res_long.groupby("subject_id"):
        zsub = z_per[z_per["subject_id"] == sid]
        if len(zsub) == 0:
            continue
        keys = sorted(set(zsub["key"]))
        zv = zsub.set_index("key")["abs_z"].reindex(keys).values
        rv = rsub.set_index("key")["resected_frac"].reindex(keys, fill_value=0).values
        if np.all(rv == 0):
            continue
        rho, _ = spearmanr(zv, rv)
        if np.isnan(rho):
            continue
        rhos.append(rho)
    return np.array(rhos)


mfp_z = load_z("ideas_zscores_centilebrain.csv")
gml_z = load_z("ideas_zscores_centilebrain_gamlss.csv")
pcn_z = load_z("ideas_zscores_pcn.csv")

rho = {
    "MFP": resection_rho(mfp_z),
    "GAMLSS": resection_rho(gml_z),
    "PCN": resection_rho(pcn_z),
}
rho_rows = []
for algo, arr in rho.items():
    rho_rows.append({
        "algo": algo, "n": len(arr),
        "mean_rho": float(arr.mean()),
        "median_rho": float(np.median(arr)),
        "frac_pos": float((arr > 0).mean()),
    })
rho_df = pd.DataFrame(rho_rows)

# ---- assemble per-backend metrics from existing tables --------------------
sd = pd.read_csv(HERE / "task5_three_backend_control_sd.csv")
sd_med = sd[["MFP", "GAMLSS", "PCN"]].median()

ideas = pd.read_csv(HERE / "pearson_r_vs_ideas_summary.csv")
ideas = ideas.set_index("algorithm")

auc = pd.read_csv(HERE / "task7_aucs_all_backends_thickness_summary.csv")
auc = auc.set_index("algo")

per_backend = pd.DataFrame({
    "algo": ["MFP", "GAMLSS", "PCN"],
    "coverage": "68 cortical thickness regions",
    "control_sd_median": [float(sd_med[a]) for a in ("MFP", "GAMLSS", "PCN")],
    "vs_ideas_median_r": [float(ideas.loc[a, "median_r"]) for a in ("MFP", "GAMLSS", "PCN")],
    "vs_ideas_mean_r": [float(ideas.loc[a, "mean_r"]) for a in ("MFP", "GAMLSS", "PCN")],
    "auc_mean": [float(auc.loc[a, "mean_auc"]) for a in ("MFP", "GAMLSS", "PCN")],
    "auc_ci_lo": [float(auc.loc[a, "ci_lo"]) for a in ("MFP", "GAMLSS", "PCN")],
    "auc_ci_hi": [float(auc.loc[a, "ci_hi"]) for a in ("MFP", "GAMLSS", "PCN")],
    "resection_mean_rho": [float(rho_df.set_index("algo").loc[a, "mean_rho"])
                           for a in ("MFP", "GAMLSS", "PCN")],
    "resection_median_rho": [float(rho_df.set_index("algo").loc[a, "median_rho"])
                             for a in ("MFP", "GAMLSS", "PCN")],
    "resection_frac_pos": [float(rho_df.set_index("algo").loc[a, "frac_pos"])
                           for a in ("MFP", "GAMLSS", "PCN")],
})

pairs = pd.read_csv(HERE / "pearson_r_all_pairs_summary.csv")
pairs = pairs[pairs["pair"].str.contains("thickness")].copy()

print("=== Per-backend (thickness, all three) ===")
print(per_backend.to_string(index=False, float_format="%.3f"))
print("\n=== Pairwise Pearson r of patient Z (thickness) ===")
print(pairs.to_string(index=False, float_format="%.3f"))
print("\n=== Fair resection ρ (thickness only) ===")
print(rho_df.to_string(index=False, float_format="%.3f"))

write_all("compare_three_summary.csv", per_backend)
write_all("compare_three_pairs.csv", pairs)
write_all("task8_resection_all_backends_thickness.csv", rho_df)
print("\nDone.")
