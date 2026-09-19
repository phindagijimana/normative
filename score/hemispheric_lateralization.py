"""Hemispheric lateralisation — does the more-deviant hemisphere on preop
Z-scores predict the actual side of resection (Op_Side)?

Method:
  * For each surgical patient with a valid Op_Side (L or R; exclude "B",
    "N", NaN), aggregate |Z| per hemisphere:
      LH_score = mean(|Z|) across lh_*_thickness + lh_*_area + Left-* subcortical
      RH_score = mean(|Z|) across rh_*_thickness + rh_*_area + Right-* subcortical
  * Predicted side = argmax(LH_score, RH_score)
  * Correct = predicted side == Op_Side
  * Report: overall accuracy, sensitivity per side, chi-square test of
    association, breakdown by Pathology if per-pathology N ≥ 20.
  * Do for both MFP and GAMLSS Z-scores.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

ROOT = Path("/mnt/nfs/home/URMC-SH/pndagiji/Documents/Normative")

# ---- Load Z-scores + metadata --------------------------------------------
mfp = pd.read_csv(ROOT / "score/ideas_zscores_centilebrain.csv")
gml = pd.read_csv(ROOT / "score/ideas_zscores_centilebrain_gamlss.csv")
meta = pd.read_csv(ROOT / "ideas_data/Metadata_Release_Anon.csv")
meta = meta.rename(columns={"ID": "subject_id"}).drop_duplicates(subset="subject_id")

def _hemi_of(region: str, measure: str) -> Optional[str]:
    """Return 'L', 'R', or None for a given region+measure."""
    if measure in ("thickness", "area"):
        if region.startswith("lh_"): return "L"
        if region.startswith("rh_"): return "R"
    elif measure == "subcortical":
        if region.startswith("Left-"):  return "L"
        if region.startswith("Right-"): return "R"
    return None

def lateralisation(z_long: pd.DataFrame, algo: str) -> pd.DataFrame:
    z = z_long[z_long["cohort"] == "patient"].copy()
    z["hemi"] = [_hemi_of(r, m) for r, m in zip(z["region"], z["measure"])]
    z = z[z["hemi"].isin(["L", "R"])].copy()
    z["abs_z"] = z["z"].abs()

    # Aggregate |Z| per subject × hemi
    hemi_scores = (z.groupby(["subject_id", "hemi"])["abs_z"].mean()
                    .unstack("hemi"))
    hemi_scores["pred_side"] = np.where(hemi_scores["L"] > hemi_scores["R"], "L", "R")
    hemi_scores = hemi_scores.reset_index()

    # Merge with Op_Side
    merged = hemi_scores.merge(
        meta[["subject_id", "Op_Side", "Pathology"]], on="subject_id", how="inner"
    )
    # Keep only L / R Op_Side
    merged = merged[merged["Op_Side"].isin(["L", "R"])].copy()
    merged["correct"] = merged["pred_side"] == merged["Op_Side"]

    # Overall stats
    n_total = len(merged)
    n_L = (merged["Op_Side"] == "L").sum()
    n_R = (merged["Op_Side"] == "R").sum()
    acc = merged["correct"].mean()
    sens_L = ((merged["Op_Side"] == "L") & (merged["pred_side"] == "L")).sum() / max(n_L, 1)
    sens_R = ((merged["Op_Side"] == "R") & (merged["pred_side"] == "R")).sum() / max(n_R, 1)

    # Chi-square test on 2x2 contingency
    ct = pd.crosstab(merged["Op_Side"], merged["pred_side"])
    try:
        chi2, p_val, dof, _ = chi2_contingency(ct)
    except Exception:
        p_val = np.nan

    rows = [{
        "algorithm": algo, "group": "all_surgical",
        "n": n_total, "n_L": int(n_L), "n_R": int(n_R),
        "accuracy": acc, "sens_L": sens_L, "sens_R": sens_R,
        "p_value_chi2": p_val,
    }]

    # Per-pathology stratification (only if N ≥ 20 in stratum)
    for pathology, sub in merged.groupby("Pathology"):
        if len(sub) < 20:
            continue
        n_L_p = (sub["Op_Side"] == "L").sum()
        n_R_p = (sub["Op_Side"] == "R").sum()
        acc_p = sub["correct"].mean()
        sens_L_p = ((sub["Op_Side"] == "L") & (sub["pred_side"] == "L")).sum() / max(n_L_p, 1)
        sens_R_p = ((sub["Op_Side"] == "R") & (sub["pred_side"] == "R")).sum() / max(n_R_p, 1)
        rows.append({
            "algorithm": algo, "group": f"pathology_{pathology}",
            "n": len(sub), "n_L": int(n_L_p), "n_R": int(n_R_p),
            "accuracy": acc_p, "sens_L": sens_L_p, "sens_R": sens_R_p,
            "p_value_chi2": np.nan,
        })

    return pd.DataFrame(rows)

mfp_res = lateralisation(mfp, "MFP")
gml_res = lateralisation(gml, "GAMLSS")

out = pd.concat([mfp_res, gml_res], ignore_index=True)
out.to_csv(ROOT / "score/lateralization_results.csv", index=False)

print("=" * 70)
print("Hemispheric lateralisation results")
print("=" * 70)
print(out.to_string(float_format="%.3f"))
print()
print(f"Saved: score/lateralization_results.csv")
