"""Task 7: epilepsy vs. control classification with CentileBrain Z-scores.

Mirrors the paper's HCP-EP experiment (Ge et al. 2024):
* Linear SVC, 5-fold CV × 100 repeats, AUC aggregated across folds
* Two feature sets: CentileBrain Z-scores vs. raw morphometry
* Report per-set AUC + a permutation test comparing them

NOTE ON `mu_hat`: the site-adaptation offset is estimated once on all
100 controls (see `score_centilebrain.R` and `../mu_hat.md`). This
introduces a small train-test leak for the classifier because those same
controls appear in the SVC training folds. Nested cross-validation of the
adaptation procedure closes the leak; expected to reduce the Z-score AUC
only marginally. Documented as Test 1 in `mu_hat.md`.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

RNG = np.random.default_rng(0)
N_REPEATS = 100
N_SPLITS = 5

ROOT = Path("/mnt/nfs/home/URMC-SH/pndagiji/Documents/Normative")

# --------- Load Z-scores (wide: subject × region_measure) ------------------
z_long = pd.read_csv(ROOT / "score/ideas_zscores_centilebrain.csv")
z_wide = z_long.pivot_table(
    index=["subject_id", "cohort", "sex", "age"],
    columns=["measure", "region"], values="z"
).reset_index()
z_wide.columns = ["_".join(c) if isinstance(c, tuple) else c for c in
                  [tuple(x for x in col if x) for col in z_wide.columns]]
print(f"Z-score wide matrix: {z_wide.shape}")

# --------- Load raw morphometry (from merged loader) -----------------------
raw = pd.read_csv(ROOT / "ideas_data/ideas_merged.csv")
region_cols_raw = [c for c in raw.columns
                   if any(c.startswith(p) for p in ("lh_", "rh_"))
                   or c.startswith("Left-") or c.startswith("Right-")]
# Also drop the "MeanThickness" and "WhiteSurfArea" hemisphere-total columns —
# not per-region.
region_cols_raw = [c for c in region_cols_raw
                   if "MeanThickness" not in c and "WhiteSurfArea" not in c]
print(f"Raw feature matrix: {raw.shape}, {len(region_cols_raw)} regional features")

# Ensure we work with the same subject set (some rows may lack all values)
merge_keys = ["subject_id", "cohort", "sex", "age"]
common_sids = sorted(set(z_wide["subject_id"]) & set(raw["subject_id"]))
z_wide = z_wide[z_wide["subject_id"].isin(common_sids)].sort_values("subject_id").reset_index(drop=True)
raw     = raw[raw["subject_id"].isin(common_sids)].sort_values("subject_id").reset_index(drop=True)
assert (z_wide["subject_id"].values == raw["subject_id"].values).all()

# Target: 1 = patient (epilepsy), 0 = control
y = (z_wide["cohort"].values == "patient").astype(int)
print(f"Class balance: patient={y.sum()}, control={(1 - y).sum()}")

# Feature matrices
X_z = z_wide.drop(columns=merge_keys).values
X_raw = raw[region_cols_raw].values

print(f"Feature widths — Z: {X_z.shape[1]}, raw: {X_raw.shape[1]}")

# --------- Classifier ------------------------------------------------------
def repeated_cv_auc(X, y, n_repeats=N_REPEATS, n_splits=N_SPLITS, rng=None):
    if rng is None:
        rng = np.random.default_rng(0)
    aucs = np.zeros(n_repeats)
    for r in range(n_repeats):
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True,
                              random_state=int(rng.integers(0, 2**31 - 1)))
        fold_auc = []
        for train_idx, test_idx in skf.split(X, y):
            pipe = make_pipeline(StandardScaler(),
                                 SVC(kernel="linear", probability=False))
            pipe.fit(X[train_idx], y[train_idx])
            scores = pipe.decision_function(X[test_idx])
            fold_auc.append(roc_auc_score(y[test_idx], scores))
        aucs[r] = np.mean(fold_auc)
    return aucs

print("\nRunning 100×5-fold CV on Z-score features ...")
aucs_z = repeated_cv_auc(X_z, y, rng=np.random.default_rng(1))
print(f"  AUC:  mean = {aucs_z.mean():.3f}   sd = {aucs_z.std():.3f}   "
      f"95% CI [{np.quantile(aucs_z, 0.025):.3f}, {np.quantile(aucs_z, 0.975):.3f}]")

print("\nRunning 100×5-fold CV on raw morphometry features ...")
aucs_raw = repeated_cv_auc(X_raw, y, rng=np.random.default_rng(2))
print(f"  AUC:  mean = {aucs_raw.mean():.3f}   sd = {aucs_raw.std():.3f}   "
      f"95% CI [{np.quantile(aucs_raw, 0.025):.3f}, {np.quantile(aucs_raw, 0.975):.3f}]")

# --------- Permutation test comparing the two -----------------------------
delta = aucs_z - aucs_raw
print(f"\nΔAUC (Z − raw): mean = {delta.mean():+.3f}   "
      f"95% CI [{np.quantile(delta, 0.025):+.3f}, {np.quantile(delta, 0.975):+.3f}]")

# A paired permutation test on the seed-matched folds
n_perm = 10_000
observed = delta.mean()
signs = RNG.choice([-1, 1], size=(n_perm, len(delta)))
perm_deltas = (signs * delta.reshape(1, -1)).mean(axis=1)
p_value = np.mean(np.abs(perm_deltas) >= abs(observed))
print(f"Paired permutation p (H0: ΔAUC=0):  {p_value:.4f}")

# Save
pd.DataFrame({
    "auc_zscore": aucs_z, "auc_raw": aucs_raw,
    "delta_zscore_minus_raw": delta,
}).to_csv(ROOT / "score/classification_aucs.csv", index=False)
print(f"\nSaved: {ROOT / 'score/classification_aucs.csv'}")
