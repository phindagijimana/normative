#!/usr/bin/env python3
"""Pearson r of patient Z-scores for every backend pair.

Combinations (3 backends → 3 pairs, plus a three-way thickness table):
  MFP vs GAMLSS   — all 150 regions (thickness + area + subcortical)
  MFP vs PCN      — cortical thickness only (PCN's coverage)
  GAMLSS vs PCN   — cortical thickness only

Method matches compare_mfp_gamlss.py head-to-head:
  cohort = patient, pandas Series.corr() = Pearson, ≥ 20 complete pairs.

Writes canonical filenames (pearson_r_*) and keeps the legacy
head_to_head_mfp_vs_gamlss_correlation.csv name in sync.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent
REPO = Path(__file__).resolve().parents[1]

Z_DIR = BUNDLE / "CentileBrain"
if not (Z_DIR / "ideas_zscores_centilebrain.csv").exists():
    Z_DIR = REPO / "score"

OUT_DIRS = [HERE]
score_out = REPO / "score"
if score_out.exists() and score_out.resolve() != HERE.resolve():
    OUT_DIRS.append(score_out)


def load_z(path: Path, algo: str) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=["subject_id", "cohort", "measure", "region", "z"])
    df["subject_id"] = df["subject_id"].astype(int)
    df["algo"] = algo
    return df


def pivot_patients(df: pd.DataFrame, measure: str | None = None) -> pd.DataFrame:
    sub = df[df["cohort"] == "patient"]
    if measure is not None:
        sub = sub[sub["measure"] == measure]
    return sub.pivot_table(index="subject_id", columns="region", values="z")


def pairwise_r(a: pd.DataFrame, b: pd.DataFrame, min_n: int = 20) -> pd.DataFrame:
    ids = sorted(set(a.index) & set(b.index))
    regions = sorted(set(a.columns) & set(b.columns))
    rows = []
    for r in regions:
        x = a.loc[ids, r]
        y = b.loc[ids, r]
        ok = x.notna() & y.notna()
        n = int(ok.sum())
        if n < min_n:
            continue
        rows.append({"region": r, "r": float(x[ok].corr(y[ok])), "n": n})
    return pd.DataFrame(rows)


def summarise(pair: str, tab: pd.DataFrame) -> dict:
    r = tab["r"]
    return {
        "pair": pair,
        "n_regions": int(len(tab)),
        "n_subjects": int(tab["n"].min()) if len(tab) else 0,
        "median_r": float(r.median()),
        "mean_r": float(r.mean()),
        "min_r": float(r.min()),
        "max_r": float(r.max()),
        "frac_r_gt_0.7": float((r > 0.7).mean()),
        "frac_r_gt_0.9": float((r > 0.9).mean()),
    }


def write_all(name: str, df: pd.DataFrame) -> None:
    for d in OUT_DIRS:
        df.to_csv(d / name, index=False)
        print(f"  wrote {d / name}  ({len(df)} rows)")


mfp = load_z(Z_DIR / "ideas_zscores_centilebrain.csv", "MFP")
gml = load_z(Z_DIR / "ideas_zscores_centilebrain_gamlss.csv", "GAMLSS")
pcn = load_z(Z_DIR / "ideas_zscores_pcn.csv", "PCN")

mfp_all = pivot_patients(mfp)
gml_all = pivot_patients(gml)
mfp_th = pivot_patients(mfp, "thickness")
gml_th = pivot_patients(gml, "thickness")
pcn_th = pivot_patients(pcn, "thickness")

# --- all 150 regions: MFP vs GAMLSS (same as legacy head-to-head file) -----
r_mg = pairwise_r(mfp_all, gml_all)
r_mg.insert(0, "measure", r_mg["region"].map(
    lambda x: "thickness" if x.endswith("_thickness")
    else "area" if x.endswith("_area")
    else "subcortical"
))

# --- thickness only: all three pairs ---------------------------------------
r_mg_th = pairwise_r(mfp_th, gml_th)
r_mp_th = pairwise_r(mfp_th, pcn_th)
r_gp_th = pairwise_r(gml_th, pcn_th)

wide = (
    r_mg_th.rename(columns={"r": "r_mfp_gamlss", "n": "n_mfp_gamlss"})
    .merge(r_mp_th.rename(columns={"r": "r_mfp_pcn", "n": "n_mfp_pcn"}), on="region")
    .merge(r_gp_th.rename(columns={"r": "r_gamlss_pcn", "n": "n_gamlss_pcn"}), on="region")
)

summary = pd.DataFrame([
    summarise("MFP vs GAMLSS (150 regions)", r_mg),
    summarise("MFP vs GAMLSS (thickness)", r_mg_th),
    summarise("MFP vs PCN (thickness)", r_mp_th),
    summarise("GAMLSS vs PCN (thickness)", r_gp_th),
])

print("Pairwise Pearson r of patient Z-scores")
print(summary.to_string(index=False, float_format="%.3f"))
print()

write_all("pearson_r_mfp_vs_gamlss.csv", r_mg)
write_all("pearson_r_mfp_vs_pcn_thickness.csv", r_mp_th.assign(measure="thickness"))
write_all("pearson_r_gamlss_vs_pcn_thickness.csv", r_gp_th.assign(measure="thickness"))
write_all("pearson_r_all_pairs_thickness.csv", wide)
write_all("pearson_r_all_pairs_summary.csv", summary)
print("\nDone.")
