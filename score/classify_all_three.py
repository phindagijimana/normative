#!/usr/bin/env python3
"""Task 7 — epilepsy vs control AUC for all three backends.

Linear SVC, StandardScaler, 100 × 5-fold stratified CV. Same protocol as
compare_mfp_gamlss.py.

PCN only scores cortical thickness (68 regions), so the three-way
comparison uses thickness Z-scores for MFP, GAMLSS, and PCN. The
existing 150-region MFP vs GAMLSS AUCs stay in task7_aucs_mfp_vs_gamlss.csv.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent
REPO = Path("/mnt/nfs/home/URMC-SH/pndagiji/Documents/Normative")
if not REPO.exists():
    REPO = Path("/mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/Documents/Normative")

Z_DIR = BUNDLE / "CentileBrain"
if not (Z_DIR / "ideas_zscores_centilebrain.csv").exists():
    Z_DIR = REPO / "score"

OUT_DIRS = [HERE]
score_out = REPO / "score"
if score_out.exists() and score_out.resolve() != HERE.resolve():
    OUT_DIRS.append(score_out)


def load_z(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=["subject_id", "cohort", "measure", "region", "z"])
    df["subject_id"] = df["subject_id"].astype(int)
    return df


def thickness_wide(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["measure"] == "thickness"].pivot_table(
        index="subject_id", columns="region", values="z"
    )


def cohort_of(df: pd.DataFrame) -> pd.Series:
    return df.drop_duplicates("subject_id").set_index("subject_id")["cohort"]


def clean(X: np.ndarray) -> np.ndarray:
    med = np.nanmedian(X, axis=0)
    keep = ~np.isnan(med)
    X = np.array(X[:, keep], dtype=float, copy=True)
    med = med[keep]
    inds = np.where(np.isnan(X))
    X[inds] = np.take(med, inds[1])
    return X


def repeated_cv_auc(X: np.ndarray, y: np.ndarray,
                    n_repeats: int = 100, n_splits: int = 5) -> np.ndarray:
    rng = np.random.default_rng(0)
    aucs = np.zeros(n_repeats)
    for r in range(n_repeats):
        skf = StratifiedKFold(
            n_splits=n_splits, shuffle=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        fold = []
        for tr, te in skf.split(X, y):
            pipe = make_pipeline(StandardScaler(), SVC(kernel="linear"))
            pipe.fit(X[tr], y[tr])
            fold.append(roc_auc_score(y[te], pipe.decision_function(X[te])))
        aucs[r] = np.mean(fold)
    return aucs


def write_all(name: str, df: pd.DataFrame) -> None:
    for d in OUT_DIRS:
        df.to_csv(d / name, index=False)
        print(f"  wrote {d / name}")


mfp = load_z(Z_DIR / "ideas_zscores_centilebrain.csv")
gml = load_z(Z_DIR / "ideas_zscores_centilebrain_gamlss.csv")
pcn = load_z(Z_DIR / "ideas_zscores_pcn.csv")

Wm = thickness_wide(mfp)
Wg = thickness_wide(gml)
Wp = thickness_wide(pcn)
cohort = cohort_of(mfp)

common_ids = Wm.index.intersection(Wg.index).intersection(Wp.index)
common_regions = sorted(set(Wm.columns) & set(Wg.columns) & set(Wp.columns))
common_ids = common_ids.sort_values()
y = (cohort.loc[common_ids] == "patient").astype(int).to_numpy()

print(f"Common subjects: {len(common_ids)}  "
      f"(MFP {len(Wm)}, GAMLSS {len(Wg)}, PCN {len(Wp)})")
print(f"Common thickness regions: {len(common_regions)}")

Xm_a = clean(Wm.loc[common_ids, common_regions].to_numpy())
Xg_a = clean(Wg.loc[common_ids, common_regions].to_numpy())
Xp_a = clean(Wp.loc[common_ids, common_regions].to_numpy())
print(f"Feature width after NaN clean: "
      f"MFP {Xm_a.shape[1]}, GAMLSS {Xg_a.shape[1]}, PCN {Xp_a.shape[1]}")
print(f"Class balance: patient={y.sum()}, control={(1 - y).sum()}")

runs = [
    ("MFP", "thickness", Xm_a, y),
    ("GAMLSS", "thickness", Xg_a, y),
    ("PCN", "thickness", Xp_a, y),
]

rows = []
summary_rows = []
for algo, fset, X, y in runs:
    print(f"\nRunning {algo} ({X.shape[1]} thickness features) ...")
    aucs = repeated_cv_auc(X, y)
    lo, hi = np.quantile(aucs, [0.025, 0.975])
    print(f"  AUC mean={aucs.mean():.3f}  95% CI [{lo:.3f}, {hi:.3f}]")
    for i, a in enumerate(aucs):
        rows.append({"algo": algo, "feature_set": fset,
                     "n_features": X.shape[1], "repeat": i, "auc": float(a)})
    summary_rows.append({
        "algo": algo, "feature_set": fset, "n_features": X.shape[1],
        "n_subjects": len(y), "n_patient": int(y.sum()),
        "n_control": int((1 - y).sum()),
        "mean_auc": float(aucs.mean()),
        "sd_auc": float(aucs.std(ddof=1)),
        "ci_lo": float(lo), "ci_hi": float(hi),
    })

long = pd.DataFrame(rows)
summary = pd.DataFrame(summary_rows)

# Pairwise ΔAUC on matched repeats (same seed sequence → comparable)
def delta_row(a, b, label):
    d = long.loc[long["algo"] == a, "auc"].to_numpy() - \
        long.loc[long["algo"] == b, "auc"].to_numpy()
    lo, hi = np.quantile(d, [0.025, 0.975])
    return {"pair": label, "mean_delta": float(d.mean()),
            "ci_lo": float(lo), "ci_hi": float(hi)}


deltas = pd.DataFrame([
    delta_row("GAMLSS", "MFP", "GAMLSS − MFP"),
    delta_row("PCN", "MFP", "PCN − MFP"),
    delta_row("PCN", "GAMLSS", "PCN − GAMLSS"),
])
print("\nΔAUC (thickness, matched repeats)")
print(deltas.to_string(index=False, float_format="{:+.3f}".format))

write_all("task7_aucs_all_backends_thickness.csv", long)
write_all("task7_aucs_all_backends_thickness_summary.csv", summary)
write_all("task7_aucs_all_backends_thickness_delta.csv", deltas)
print("\nDone.")
