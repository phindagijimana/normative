"""ILAE-1 seizure-freedom outcome prediction from preop normative Z-scores.

Method:
  * Subset to patients with ILAE_Year1 available.
  * Target: seizure_free = (ILAE_Year1 == 1)
  * Features: 150 per-region Z-scores (thickness + area + subcortical)
    OR raw morphometry (baseline for comparison), same structure as Task 7.
  * Model: L2-regularised logistic regression, 100 × 5-fold stratified CV,
    StandardScaler pipeline. AUC as primary metric.
  * Compare Z vs raw ΔAUC with paired permutation p-value.
  * Do for both MFP and GAMLSS.
  * If HS stratum has ≥ 30, also report within-HS AUC.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

RNG = np.random.default_rng(20260919)
N_REPEATS = 100
N_SPLITS = 5

ROOT = Path("/mnt/nfs/home/URMC-SH/pndagiji/Documents/Normative")

# ---- Load Z-scores + raw features + metadata -----------------------------
mfp = pd.read_csv(ROOT / "score/ideas_zscores_centilebrain.csv")
gml = pd.read_csv(ROOT / "score/ideas_zscores_centilebrain_gamlss.csv")
raw = pd.read_csv(ROOT / "ideas_data/ideas_merged.csv")
meta = pd.read_csv(ROOT / "ideas_data/Metadata_Release_Anon.csv")
meta = meta.rename(columns={"ID": "subject_id"}).drop_duplicates(subset="subject_id")

# Build wide Z-score matrices per algorithm
def build_z_wide(z_long):
    wide = z_long[z_long["cohort"] == "patient"].pivot_table(
        index="subject_id", columns=["measure", "region"], values="z")
    return wide.sort_index()

mfp_wide = build_z_wide(mfp)
gml_wide = build_z_wide(gml)

# Raw morphometry — 150 regional features
region_cols_raw = [c for c in raw.columns
                   if any(c.startswith(p) for p in ("lh_", "rh_"))
                   or c.startswith("Left-") or c.startswith("Right-")]
region_cols_raw = [c for c in region_cols_raw
                   if "MeanThickness" not in c and "WhiteSurfArea" not in c]
raw_p = raw[raw["cohort"] == "patient"].set_index("subject_id").sort_index()

# ---- Merge with outcome data ---------------------------------------------
outcome = meta.set_index("subject_id")[["ILAE_Year1", "Pathology"]].copy()
outcome = outcome.dropna(subset=["ILAE_Year1"])
outcome["seizure_free"] = (outcome["ILAE_Year1"] == 1).astype(int)

def prepare(features_df, outcome_df):
    common = sorted(set(features_df.index) & set(outcome_df.index))
    X = features_df.loc[common].values
    y = outcome_df.loc[common, "seizure_free"].values
    return X, y, common

def repeated_cv_auc(X, y, n_repeats=N_REPEATS, n_splits=N_SPLITS, seed=0):
    rng = np.random.default_rng(seed)
    aucs = np.zeros(n_repeats)
    for r in range(n_repeats):
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True,
                              random_state=int(rng.integers(0, 2**31 - 1)))
        fold_auc = []
        for tr, te in skf.split(X, y):
            pipe = make_pipeline(StandardScaler(),
                                 LogisticRegression(penalty="l2", max_iter=1000, C=1.0))
            pipe.fit(X[tr], y[tr])
            scores = pipe.decision_function(X[te])
            fold_auc.append(roc_auc_score(y[te], scores))
        aucs[r] = np.mean(fold_auc)
    return aucs

results = []
seeds = {"MFP-Z": 1, "MFP-raw": 2, "GAMLSS-Z": 3, "GAMLSS-raw": 4}

# ---- MFP Z-scores --------------------------------------------------------
X, y, ids = prepare(mfp_wide, outcome)
print(f"MFP Z: N patients with ILAE_Year1 = {len(y)}, "
      f"seizure_free = {y.sum()}, not_seizure_free = {(1-y).sum()}")
aucs = repeated_cv_auc(X, y, seed=seeds["MFP-Z"])
results.append({"algorithm": "MFP", "features": "Z-scores",
                "n": len(y), "n_pos": int(y.sum()), "n_neg": int((1-y).sum()),
                "mean_auc": aucs.mean(),
                "ci_lo": np.quantile(aucs, 0.025),
                "ci_hi": np.quantile(aucs, 0.975),
                "auc_arr": aucs})

# MFP raw
X_raw, y_raw, ids_raw = prepare(raw_p[region_cols_raw], outcome)
assert (y == y_raw).all()
aucs_raw = repeated_cv_auc(X_raw, y_raw, seed=seeds["MFP-raw"])
results.append({"algorithm": "MFP", "features": "raw",
                "n": len(y_raw), "n_pos": int(y_raw.sum()), "n_neg": int((1-y_raw).sum()),
                "mean_auc": aucs_raw.mean(),
                "ci_lo": np.quantile(aucs_raw, 0.025),
                "ci_hi": np.quantile(aucs_raw, 0.975),
                "auc_arr": aucs_raw})

# ---- GAMLSS Z-scores -----------------------------------------------------
X, y, ids = prepare(gml_wide, outcome)
aucs = repeated_cv_auc(X, y, seed=seeds["GAMLSS-Z"])
results.append({"algorithm": "GAMLSS", "features": "Z-scores",
                "n": len(y), "n_pos": int(y.sum()), "n_neg": int((1-y).sum()),
                "mean_auc": aucs.mean(),
                "ci_lo": np.quantile(aucs, 0.025),
                "ci_hi": np.quantile(aucs, 0.975),
                "auc_arr": aucs})

# GAMLSS raw uses same raw matrix (raw is algorithm-independent)
aucs_raw2 = repeated_cv_auc(X_raw, y_raw, seed=seeds["GAMLSS-raw"])
results.append({"algorithm": "GAMLSS", "features": "raw",
                "n": len(y_raw), "n_pos": int(y_raw.sum()), "n_neg": int((1-y_raw).sum()),
                "mean_auc": aucs_raw2.mean(),
                "ci_lo": np.quantile(aucs_raw2, 0.025),
                "ci_hi": np.quantile(aucs_raw2, 0.975),
                "auc_arr": aucs_raw2})

# ---- Paired ΔAUC permutation tests --------------------------------------
def perm_p(delta, n_perm=10_000):
    rng2 = np.random.default_rng(0)
    signs = rng2.choice([-1, 1], size=(n_perm, len(delta)))
    perm_deltas = (signs * delta.reshape(1, -1)).mean(axis=1)
    return float(np.mean(np.abs(perm_deltas) >= abs(delta.mean())))

d_mfp = results[0]["auc_arr"] - results[1]["auc_arr"]
d_gml = results[2]["auc_arr"] - results[3]["auc_arr"]

# Save summary
summary = pd.DataFrame([
    {k: v for k, v in r.items() if k != "auc_arr"} for r in results
])
summary["delta_vs_raw"] = np.nan
summary["p_value"] = np.nan
summary.loc[0, "delta_vs_raw"] = d_mfp.mean()
summary.loc[0, "p_value"] = perm_p(d_mfp)
summary.loc[2, "delta_vs_raw"] = d_gml.mean()
summary.loc[2, "p_value"] = perm_p(d_gml)

summary.to_csv(ROOT / "score/ilae_outcome_aucs.csv", index=False)

print()
print("=" * 70)
print("ILAE-1 seizure-freedom prediction results")
print("=" * 70)
print(summary.to_string(float_format="%.3f"))
print()
print(f"MFP ΔAUC (Z − raw)    = {d_mfp.mean():+.4f}  p = {perm_p(d_mfp):.4f}")
print(f"GAMLSS ΔAUC (Z − raw) = {d_gml.mean():+.4f}  p = {perm_p(d_gml):.4f}")
print()

# ---- Within-HS stratum (typically the largest single pathology) ----------
hs = meta[meta["Pathology"] == "HS"].copy()
hs = hs.dropna(subset=["ILAE_Year1"])
hs["seizure_free"] = (hs["ILAE_Year1"] == 1).astype(int)
hs_ids = set(hs["subject_id"])
if len(hs_ids) >= 30:
    print(f"HS stratum N = {len(hs_ids)} — running within-HS analysis")
    mfp_hs = mfp_wide.loc[[i for i in mfp_wide.index if i in hs_ids]]
    outcome_hs = hs.set_index("subject_id")[["seizure_free"]]
    X_hs, y_hs, _ = prepare(mfp_hs, outcome_hs)
    aucs_hs_z = repeated_cv_auc(X_hs, y_hs, seed=5)
    print(f"  MFP Z within HS:  AUC {aucs_hs_z.mean():.3f} "
          f"[{np.quantile(aucs_hs_z, 0.025):.3f}, {np.quantile(aucs_hs_z, 0.975):.3f}] "
          f"N={len(y_hs)}")
    X_hs_raw, y_hs_raw, _ = prepare(raw_p.loc[[i for i in raw_p.index if i in hs_ids], region_cols_raw],
                                     outcome_hs)
    aucs_hs_raw = repeated_cv_auc(X_hs_raw, y_hs_raw, seed=6)
    print(f"  Raw within HS:    AUC {aucs_hs_raw.mean():.3f} "
          f"[{np.quantile(aucs_hs_raw, 0.025):.3f}, {np.quantile(aucs_hs_raw, 0.975):.3f}]")

print()
print(f"Saved: score/ilae_outcome_aucs.csv")
