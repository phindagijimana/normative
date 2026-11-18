"""Task 5 (calibration) and Task 6 (convergence) stratified by age band
and sex, on the IDEAS healthy controls / patients. Produces
supplementary tables to be added to validate_manuscript_tables.docx as
Supp Tables S4 (age-stratified calibration) and S5 (sex-stratified
convergence).

These are subgroup analyses reviewers routinely request. Uses only
existing scoring outputs — no new scoring runs.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

ROOT = Path("/mnt/nfs/home/URMC-SH/pndagiji/Documents/Normative")
SCORE = ROOT / "score"

AGE_BANDS = [(17.5, 30.0, "17-29"),
             (30.0, 45.0, "30-44"),
             (45.0, 67.5, "45-67")]


def s4_age_stratified_calibration():
    """Per-region control SD stratified by age band, per backend x measure."""
    rows = []
    for backend, csv in [("MFP", "ideas_zscores_centilebrain.csv"),
                          ("GAMLSS", "ideas_zscores_centilebrain_gamlss.csv"),
                          ("PCN", "ideas_zscores_pcn.csv")]:
        df = pd.read_csv(SCORE / csv)
        df = df[df["cohort"] == "control"].copy()
        for lo, hi, label in AGE_BANDS:
            sub = df[(df["age"] >= lo) & (df["age"] < hi)]
            n_subjects = sub["subject_id"].nunique()
            if n_subjects < 5:
                continue
            for meas, meas_label in [("thickness", "Cortical thickness"),
                                      ("area", "Cortical surface area"),
                                      ("subcortical", "Subcortical volume")]:
                m = sub[sub["measure"] == meas]
                if len(m) == 0:
                    continue
                per_region_sd = m.groupby("region")["z"].std()
                rows.append({
                    "backend": {"MFP": "CentileBrain-MFP",
                                "GAMLSS": "CentileBrain-GAMLSS",
                                "PCN": "PCN Toolkit-Bayesian"}[backend],
                    "measure": meas_label,
                    "age_band": label,
                    "n_controls": n_subjects,
                    "n_regions": len(per_region_sd),
                    "median_control_sd": float(per_region_sd.median()),
                })
    out = pd.DataFrame(rows)
    out.to_csv(SCORE / "supp_table_s4_age_stratified_calibration.csv", index=False)
    print(f"wrote supp_table_s4_age_stratified_calibration.csv ({len(out)} rows)")
    print(out.to_string(index=False, float_format="%.3f"))
    return out


def s5_sex_stratified_convergence():
    """Per-region convergence r vs IDEAS-internal, stratified by sex."""
    ideas = pd.read_csv(ROOT / "ideas_data" / "thick_zscores_patients.csv")
    ideas = ideas.rename(columns={"ID": "subject_id"})
    ideas_long = ideas.melt(id_vars="subject_id", var_name="region",
                            value_name="z_ideas")
    meta = pd.read_csv(ROOT / "ideas_data" / "Metadata_Release_Anon.csv")
    meta["sex"] = meta["sex"].astype(str).str.upper().str.strip() if "sex" in meta.columns else None
    # Use ideas_merged for sex info
    merged = pd.read_csv(ROOT / "ideas_data" / "ideas_merged.csv", low_memory=False)
    sex_by_id = merged.set_index("subject_id")["sex"].str.upper().to_dict()

    rows = []
    for backend, csv in [("MFP", "ideas_zscores_centilebrain.csv"),
                          ("GAMLSS", "ideas_zscores_centilebrain_gamlss.csv"),
                          ("PCN", "ideas_zscores_pcn.csv")]:
        df = pd.read_csv(SCORE / csv)
        df = df[(df["measure"] == "thickness") & (df["cohort"] == "patient")]
        df["sex"] = df["subject_id"].map(sex_by_id)
        joined = df.merge(ideas_long, on=["subject_id", "region"], how="inner")
        joined = joined.dropna(subset=["z", "z_ideas", "sex"])
        for sex in ("F", "M"):
            s = joined[joined["sex"] == sex]
            if s.empty:
                continue
            rs = []
            for region, g in s.groupby("region"):
                if len(g) >= 20:
                    rs.append(pearsonr(g["z"], g["z_ideas"])[0])
            if rs:
                rows.append({
                    "backend": {"MFP": "CentileBrain-MFP",
                                "GAMLSS": "CentileBrain-GAMLSS",
                                "PCN": "PCN Toolkit-Bayesian"}[backend],
                    "sex": sex,
                    "n_regions": len(rs),
                    "median_r": float(np.median(rs)),
                    "mean_r": float(np.mean(rs)),
                    "frac_r_gt_0.9": float(np.mean(np.asarray(rs) > 0.9)),
                })
    out = pd.DataFrame(rows)
    out.to_csv(SCORE / "supp_table_s5_sex_stratified_convergence.csv",
               index=False)
    print(f"\nwrote supp_table_s5_sex_stratified_convergence.csv ({len(out)} rows)")
    print(out.to_string(index=False, float_format="%.3f"))
    return out


if __name__ == "__main__":
    s4_age_stratified_calibration()
    s5_sex_stratified_convergence()
