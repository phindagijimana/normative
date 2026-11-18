"""Supplementary Table S3 — age-bin imputation sensitivity.

IDEAS releases age at scan in 5-year bins for anonymisation; the main
analyses impute bin midpoints. This script tests whether the four core
findings (calibration, convergence, classification, resection
concordance) are stable when ages are instead drawn uniformly within
each subject's bin.

For each of R replicates:
  1. Redraw age ~ Uniform(bin_lo, bin_hi) for every subject
  2. Overwrite the age column in ideas_merged.csv
  3. Re-run MFP scoring (fast; ~3.6 s)
  4. Recompute the four aggregate metrics in-process
The original merged CSV is backed up and restored at end.

MFP is the age-sensitive backend (fractional polynomials on age). GAMLSS
and PCN both fit smooth curves in age but their aggregate metrics are
also expected to be stable; we run MFP only to keep this cheap.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

REPO = Path(__file__).resolve().parent.parent
MERGED = REPO / "ideas_data" / "ideas_merged.csv"
BACKUP = REPO / "ideas_data" / "ideas_merged_backup_for_agebin_sensitivity.csv"
MFP_SCORES = REPO / "score" / "ideas_zscores_centilebrain.csv"
IDEAS_THICK = REPO / "ideas_data" / "thick_zscores_patients.csv"
OUT_CSV = REPO / "score" / "supp_table_s3_age_bin_sensitivity.csv"

R_REPLICATES = 10
SEED = 42


# The IDEAS age-bin midpoint mapping (see load_ideas.py). Bins are 5 y
# wide except for the open-ended tails.
BIN_RANGES = {
    # Patient-style ("X to Y", inclusive-exclusive)
    "15 to 20": (17.5, 20.0),
    "20 to 24": (20.0, 25.0),
    "25 to 29": (25.0, 30.0),
    "30 to 34": (30.0, 35.0),
    "35 to 39": (35.0, 40.0),
    "40 to 44": (40.0, 45.0),
    "45 to 49": (45.0, 50.0),
    "50 to 54": (50.0, 55.0),
    "55 to 59": (55.0, 60.0),
    "60 to 64": (60.0, 65.0),
    "65 to 70": (65.0, 67.5),
    # Control-style
    "Less than 20": (17.5, 20.0),
    "Over 55":      (55.0, 67.5),
}


def resample_ages(df, rng):
    """Return a copy of df with age redrawn uniformly within each
    subject's original 5-year bin."""
    out = df.copy()
    for bin_str, (lo, hi) in BIN_RANGES.items():
        mask = out["age_bin"].astype(str).str.strip() == bin_str
        n = int(mask.sum())
        if n:
            out.loc[mask, "age"] = rng.uniform(lo, hi, size=n)
    return out


def run_mfp_scoring():
    subprocess.run(
        ["Rscript", str(REPO / "score" / "score_centilebrain.R")],
        cwd=REPO, check=True, capture_output=True, text=True,
    )


def compute_metrics():
    """Aggregate the four core findings from the freshly-scored MFP CSV."""
    z = pd.read_csv(MFP_SCORES)

    # Task 5 — calibration: per-region control SD, median across regions.
    ctrl = z[z["cohort"] == "control"]
    per_region_sd = ctrl.groupby(["measure", "region"])["z"].std()
    task5_median_thickness = per_region_sd.xs("thickness").median()

    # Task 6 — convergence with IDEAS-internal thickness.
    thk = z[(z["measure"] == "thickness") & (z["cohort"] == "patient")]
    ideas = pd.read_csv(IDEAS_THICK).rename(columns={"ID": "subject_id"})
    ideas_long = ideas.melt(id_vars="subject_id", var_name="region",
                            value_name="z_ideas")
    joined = thk.merge(ideas_long, on=["subject_id", "region"])
    joined = joined.dropna(subset=["z", "z_ideas"])
    rs = []
    for region, sub in joined.groupby("region"):
        if len(sub) >= 20:
            rs.append(pearsonr(sub["z"], sub["z_ideas"])[0])
    task6_median_r = float(np.median(rs))

    # Task 7 — classification AUC. Wide table, 1 row per (subject,
    # measure) x 1 col per region. Restrict to cortical thickness for
    # speed; the manuscript's headline result holds under thickness alone.
    wide = z[z["measure"] == "thickness"].pivot_table(
        index=["subject_id", "cohort"], columns="region", values="z"
    ).dropna()
    y = (wide.index.get_level_values("cohort") == "patient").astype(int)
    X = wide.values
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    aucs = []
    for tr, te in skf.split(X, y):
        clf = LogisticRegression(C=1.0, max_iter=500, solver="liblinear")
        Xs = StandardScaler().fit(X[tr])
        clf.fit(Xs.transform(X[tr]), y[tr])
        score = clf.decision_function(Xs.transform(X[te]))
        from sklearn.metrics import roc_auc_score
        aucs.append(roc_auc_score(y[te], score))
    task7_auc = float(np.mean(aucs))

    # Task 8 — resection concordance, MFP full features. We reuse the
    # canonical resection_concordance.py so region-name alignment
    # exactly matches the main analysis; then read its output CSV.
    subprocess.run(
        ["python3", str(REPO / "score" / "resection_concordance.py")],
        cwd=REPO, check=True, capture_output=True, text=True,
    )
    task8_mean_rho = float(pd.read_csv(
        REPO / "score" / "resection_concordance.csv")["rho"].mean())

    return {
        "task5_control_thickness_median_sd": task5_median_thickness,
        "task6_convergence_median_r": task6_median_r,
        "task7_classification_auc": task7_auc,
        "task8_resection_mean_rho": task8_mean_rho,
    }


def main():
    rng = np.random.default_rng(SEED)

    if not BACKUP.exists():
        shutil.copy(MERGED, BACKUP)
        print(f"backed up {MERGED} to {BACKUP}")

    original = pd.read_csv(BACKUP, low_memory=False)

    # Point estimate: use the checked-in bin-midpoint ages.
    run_mfp_scoring()
    baseline = compute_metrics()
    print("baseline (bin midpoints):")
    for k, v in baseline.items():
        print(f"  {k}: {v:.4f}")

    replicate_rows = []
    for r in range(R_REPLICATES):
        perturbed = resample_ages(original, rng)
        perturbed.to_csv(MERGED, index=False)
        run_mfp_scoring()
        metrics = compute_metrics()
        metrics["replicate"] = r + 1
        replicate_rows.append(metrics)
        print(f"replicate {r + 1}: {metrics}")

    # Restore.
    shutil.copy(BACKUP, MERGED)
    run_mfp_scoring()  # re-run so on-disk score files match the merged CSV
    print(f"restored {MERGED} from backup")

    reps = pd.DataFrame(replicate_rows)
    summary = []
    for metric in ("task5_control_thickness_median_sd",
                   "task6_convergence_median_r",
                   "task7_classification_auc",
                   "task8_resection_mean_rho"):
        summary.append({
            "metric": metric,
            "midpoint_baseline": baseline[metric],
            "uniform_mean": reps[metric].mean(),
            "uniform_min": reps[metric].min(),
            "uniform_max": reps[metric].max(),
            "uniform_sd": reps[metric].std(),
            "n_replicates": len(reps),
        })
    out = pd.DataFrame(summary)
    out.to_csv(OUT_CSV, index=False)
    print(f"\nwrote {OUT_CSV}")
    print(out.to_string(index=False, float_format="%.4f"))


if __name__ == "__main__":
    main()
