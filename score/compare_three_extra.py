#!/usr/bin/env python3
"""Extra three-way stats on cortical thickness (MFP, GAMLSS, PCN):

1. Hemispheric lateralisation — does mean |Z| pick Op_Side?
2. Abnormality-call agreement — do |Z| > 1.96 flags match across backends?
3. Control tail rate — fraction of control Z with |Z| > 1.96 (ideal ≈ 5%).

All three use the 68 thickness regions PCN scores. Do not mix with the
150-region MFP/GAMLSS lateralisation in score/lateralization_results.csv.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent
REPO = Path(__file__).resolve().parents[1]

Z_DIR = BUNDLE / "CentileBrain"
if not (Z_DIR / "ideas_zscores_centilebrain.csv").exists():
    Z_DIR = REPO / "score"

META = REPO / "ideas_data" / "Metadata_Release_Anon.csv"
if not META.exists():
    META = BUNDLE / "IDEAS_Data" / "Metadata_Release_Anon.csv"

OUT_DIRS = [HERE]
score_out = REPO / "score"
if score_out.exists() and score_out.resolve() != HERE.resolve():
    OUT_DIRS.append(score_out)

THRESH = 1.96  # two-sided 5% under N(0,1)


def write_all(name: str, df: pd.DataFrame) -> None:
    for d in OUT_DIRS:
        df.to_csv(d / name, index=False)
        print(f"  wrote {d / name}")


def load_z(name: str, algo: str) -> pd.DataFrame:
    df = pd.read_csv(name, usecols=["subject_id", "cohort", "measure", "region", "z"])
    df["subject_id"] = df["subject_id"].astype(int)
    df = df[df["measure"] == "thickness"].copy()
    df["algo"] = algo
    return df


def cohen_kappa(a: np.ndarray, b: np.ndarray) -> float:
    a = a.astype(bool)
    b = b.astype(bool)
    n = len(a)
    if n == 0:
        return float("nan")
    p0 = (a == b).mean()
    p_yes = a.mean() * b.mean()
    p_no = (1 - a.mean()) * (1 - b.mean())
    pe = p_yes + p_no
    if pe >= 1.0:
        return 1.0 if p0 >= 1.0 else 0.0
    return float((p0 - pe) / (1 - pe))


mfp = load_z(Z_DIR / "ideas_zscores_centilebrain.csv", "MFP")
gml = load_z(Z_DIR / "ideas_zscores_centilebrain_gamlss.csv", "GAMLSS")
pcn = load_z(Z_DIR / "ideas_zscores_pcn.csv", "PCN")
z_all = pd.concat([mfp, gml, pcn], ignore_index=True)

# =====================================================================
# 1. Lateralisation (thickness only)
# =====================================================================
meta = pd.read_csv(META).rename(columns={"ID": "subject_id"})
meta = meta.drop_duplicates(subset="subject_id")


def hemi_of(region: str) -> str | None:
    if region.startswith("lh_"):
        return "L"
    if region.startswith("rh_"):
        return "R"
    return None


def lateralise(z_long: pd.DataFrame, algo: str) -> pd.DataFrame:
    z = z_long[z_long["cohort"] == "patient"].copy()
    z["hemi"] = z["region"].map(hemi_of)
    z = z[z["hemi"].isin(["L", "R"])].copy()
    z["abs_z"] = z["z"].abs()
    hemi = z.groupby(["subject_id", "hemi"])["abs_z"].mean().unstack("hemi")
    hemi["pred_side"] = np.where(hemi["L"] > hemi["R"], "L", "R")
    hemi = hemi.reset_index()
    merged = hemi.merge(meta[["subject_id", "Op_Side", "Pathology"]],
                        on="subject_id", how="inner")
    merged = merged[merged["Op_Side"].isin(["L", "R"])].copy()
    merged["correct"] = merged["pred_side"] == merged["Op_Side"]
    n_L = int((merged["Op_Side"] == "L").sum())
    n_R = int((merged["Op_Side"] == "R").sum())
    ct = pd.crosstab(merged["Op_Side"], merged["pred_side"])
    try:
        _, p_val, _, _ = chi2_contingency(ct)
    except ValueError:
        p_val = np.nan
    rows = [{
        "algo": algo, "feature_set": "thickness_68", "group": "all_surgical",
        "n": len(merged), "n_L": n_L, "n_R": n_R,
        "accuracy": float(merged["correct"].mean()),
        "sens_L": float(((merged["Op_Side"] == "L") & (merged["pred_side"] == "L")).sum() / max(n_L, 1)),
        "sens_R": float(((merged["Op_Side"] == "R") & (merged["pred_side"] == "R")).sum() / max(n_R, 1)),
        "p_value_chi2": float(p_val),
    }]
    for pathology, sub in merged.groupby("Pathology"):
        if len(sub) < 20:
            continue
        n_Lp = int((sub["Op_Side"] == "L").sum())
        n_Rp = int((sub["Op_Side"] == "R").sum())
        rows.append({
            "algo": algo, "feature_set": "thickness_68",
            "group": f"pathology_{pathology}",
            "n": len(sub), "n_L": n_Lp, "n_R": n_Rp,
            "accuracy": float(sub["correct"].mean()),
            "sens_L": float(((sub["Op_Side"] == "L") & (sub["pred_side"] == "L")).sum() / max(n_Lp, 1)),
            "sens_R": float(((sub["Op_Side"] == "R") & (sub["pred_side"] == "R")).sum() / max(n_Rp, 1)),
            "p_value_chi2": np.nan,
        })
    return pd.DataFrame(rows)


lat = pd.concat([
    lateralise(mfp, "MFP"),
    lateralise(gml, "GAMLSS"),
    lateralise(pcn, "PCN"),
], ignore_index=True)

print("=== Lateralisation (thickness, all surgical) ===")
print(lat[lat["group"] == "all_surgical"].to_string(index=False, float_format="%.3f"))

# =====================================================================
# 2. Abnormality-call agreement on patients (|Z| > 1.96)
# =====================================================================
pat = z_all[z_all["cohort"] == "patient"].copy()
wide = pat.pivot_table(index=["subject_id", "region"], columns="algo", values="z")
wide = wide.dropna(subset=["MFP", "GAMLSS", "PCN"])
flags = wide.abs() > THRESH

pair_rows = []
for a, b in (("MFP", "GAMLSS"), ("MFP", "PCN"), ("GAMLSS", "PCN")):
    fa, fb = flags[a].to_numpy(), flags[b].to_numpy()
    agree = fa == fb
    pair_rows.append({
        "pair": f"{a} vs {b}",
        "threshold": THRESH,
        "n_cells": int(len(fa)),
        "n_subjects": int(wide.index.get_level_values("subject_id").nunique()),
        "n_regions": int(wide.index.get_level_values("region").nunique()),
        "pct_agree": float(agree.mean()),
        "cohen_kappa": cohen_kappa(fa, fb),
        "pct_both_abnormal": float((fa & fb).mean()),
        "pct_a_only": float((fa & ~fb).mean()),
        "pct_b_only": float((~fa & fb).mean()),
        "rate_abnormal_a": float(fa.mean()),
        "rate_abnormal_b": float(fb.mean()),
    })
calls = pd.DataFrame(pair_rows)
print("\n=== Abnormality-call agreement (patients, |Z| > 1.96) ===")
print(calls.to_string(index=False, float_format="%.3f"))

# =====================================================================
# 3. Control tail rate
# =====================================================================
ctl = z_all[z_all["cohort"] == "control"].copy()
tail_rows = []
for algo, sub in ctl.groupby("algo"):
    rates = sub.groupby("region")["z"].apply(lambda s: float((s.abs() > THRESH).mean()))
    tail_rows.append({
        "algo": algo,
        "threshold": THRESH,
        "n_controls": int(sub["subject_id"].nunique()),
        "n_regions": int(len(rates)),
        "median_frac_|Z|>1.96": float(rates.median()),
        "mean_frac_|Z|>1.96": float(rates.mean()),
        "min_frac": float(rates.min()),
        "max_frac": float(rates.max()),
        "expected_under_N01": 0.05,
    })
tails = pd.DataFrame(tail_rows)
print("\n=== Control tail rate (|Z| > 1.96; ideal ≈ 0.05) ===")
print(tails.to_string(index=False, float_format="%.3f"))

# one-row-per-backend extra summary
extra = lat[lat["group"] == "all_surgical"][
    ["algo", "n", "accuracy", "sens_L", "sens_R", "p_value_chi2"]
].rename(columns={"n": "n_surgical", "accuracy": "lateralization_accuracy"})
extra = extra.merge(tails[["algo", "median_frac_|Z|>1.96", "mean_frac_|Z|>1.96"]],
                    on="algo")

write_all("lateralization_all_backends_thickness.csv", lat)
write_all("abnormality_agreement_thickness.csv", calls)
write_all("control_tail_rate_thickness.csv", tails)
write_all("compare_three_extra_summary.csv", extra)
print("\nDone.")
