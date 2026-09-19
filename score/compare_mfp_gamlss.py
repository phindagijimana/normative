"""Task 21: side-by-side MFP vs GAMLSS on the same IDEAS data.

For each of Tasks 5, 6, 7, 8: compute the metric under both algorithms and
report the two side-by-side, plus a direct per-region correlation of the
two algorithms' Z-scores (the "do the two algorithms agree on who is
abnormal?" test).
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

ROOT = Path("/mnt/nfs/home/URMC-SH/pndagiji/Documents/Normative")

# ---- Load both algorithm outputs ------------------------------------------
mfp = pd.read_csv(ROOT / "score/ideas_zscores_centilebrain.csv")
gml = pd.read_csv(ROOT / "score/ideas_zscores_centilebrain_gamlss.csv")

# In GAMLSS output, `z` is site-adapted (matches MFP semantics).
mfp = mfp[["subject_id", "cohort", "sex", "age", "measure", "region", "z"]].copy()
gml = gml[["subject_id", "cohort", "sex", "age", "measure", "region", "z"]].copy()
mfp["algo"] = "MFP"
gml["algo"] = "GAMLSS"
z_both = pd.concat([mfp, gml], ignore_index=True)

print(f"MFP    long-form: {len(mfp):>7} rows")
print(f"GAMLSS long-form: {len(gml):>7} rows\n")

# =============================================================================
# Task 5 — Calibration on controls: control SD per measure, MFP vs GAMLSS
# =============================================================================
print("=" * 70)
print("Task 5 — Control Z-score SD (should be ~1.0 for good calibration)")
print("=" * 70)
ctl = z_both[z_both["cohort"] == "control"]
per_measure = (ctl.groupby(["algo", "measure"])["z"]
                .agg(["mean", "std", "size"])
                .rename(columns={"mean": "mean_z", "std": "sd_z", "size": "n"}))
print(per_measure.to_string(float_format="%.3f"))

# Per-region SD comparison
per_region = (ctl.groupby(["algo", "measure", "region"])["z"]
                .std().unstack("algo").reset_index())
per_region.columns.name = None
per_region["diff_SD"] = per_region["GAMLSS"] - per_region["MFP"]
print("\nPer-region SD (control) — MFP vs GAMLSS (median across regions):")
med = per_region.groupby("measure")[["MFP", "GAMLSS", "diff_SD"]].median()
print(med.to_string(float_format="%.3f"))

# =============================================================================
# Task 6 — Convergence with IDEAS internal Z-scores
# =============================================================================
print("\n" + "=" * 70)
print("Task 6 — Correlation with IDEAS-internal ComBat Z-scores (patients)")
print("=" * 70)

ideas_thick = pd.read_csv(ROOT / "ideas_data/thick_zscores_patients.csv").set_index("ID")
ideas_area  = pd.read_csv(ROOT / "ideas_data/area_zscores_patients.csv").set_index("ID")
ideas_vol   = pd.read_csv(ROOT / "ideas_data/vol_zscores_patients.csv").set_index("ID")

sub_rename = {}
for hemi in ("Left", "Right"):
    for region in ("Thalamus", "Caudate", "Putamen", "Pallidum",
                   "Hippocampus", "Amygdala", "Accumbens-area"):
        sub_rename[f"{hemi}_{region.replace('-','_')}_volume"] = f"{hemi}-{region}"
ideas_vol = ideas_vol.rename(columns=sub_rename)

def convergence(algo, measure, ideas_df):
    df = z_both[(z_both["algo"] == algo) &
                (z_both["measure"] == measure) &
                (z_both["cohort"] == "patient")]
    wide = df.pivot_table(index="subject_id", columns="region", values="z")
    common_ids = sorted(set(wide.index) & set(ideas_df.index))
    common_regions = sorted(set(wide.columns) & set(ideas_df.columns))
    rs = []
    for r in common_regions:
        a = wide.loc[common_ids, r]
        b = ideas_df.loc[common_ids, r]
        v = a.notna() & b.notna()
        if v.sum() >= 20:
            rs.append(a[v].corr(b[v]))
    return np.array(rs)

for measure, ideas_df in [("thickness", ideas_thick),
                           ("area", ideas_area),
                           ("subcortical", ideas_vol)]:
    r_mfp = convergence("MFP", measure, ideas_df)
    r_gml = convergence("GAMLSS", measure, ideas_df)
    print(f"\n  {measure:12s}  MFP    median r={np.median(r_mfp):.3f}  "
          f"mean={r_mfp.mean():.3f}  frac r>0.7={(r_mfp > 0.7).mean() * 100:.0f}%  "
          f"(n={len(r_mfp)} regions)")
    print(f"  {measure:12s}  GAMLSS median r={np.median(r_gml):.3f}  "
          f"mean={r_gml.mean():.3f}  frac r>0.7={(r_gml > 0.7).mean() * 100:.0f}%")

# =============================================================================
# Direct MFP vs GAMLSS per-region correlation on patients
# =============================================================================
print("\n" + "=" * 70)
print("Head-to-head: do MFP and GAMLSS agree on who is abnormal per region?")
print("(Pearson r between the two algorithms' Z-scores across patients)")
print("=" * 70)

mfp_p = mfp[mfp["cohort"] == "patient"].pivot_table(
    index="subject_id", columns=["measure", "region"], values="z")
gml_p = gml[gml["cohort"] == "patient"].pivot_table(
    index="subject_id", columns=["measure", "region"], values="z")

common_ids = sorted(set(mfp_p.index) & set(gml_p.index))
common_cols = sorted(set(mfp_p.columns) & set(gml_p.columns))
head_to_head = []
for c in common_cols:
    a = mfp_p.loc[common_ids, c]
    b = gml_p.loc[common_ids, c]
    v = a.notna() & b.notna()
    if v.sum() >= 20:
        head_to_head.append({"measure": c[0], "region": c[1],
                             "r": a[v].corr(b[v])})
h2h = pd.DataFrame(head_to_head)
print(h2h.groupby("measure")["r"].describe()[["count", "mean", "50%", "min", "max"]]
      .rename(columns={"50%": "median"})
      .to_string(float_format="%.3f"))

# =============================================================================
# Task 7 — Classification: epilepsy vs control, MFP vs GAMLSS features
# =============================================================================
print("\n" + "=" * 70)
print("Task 7 — SVC epilepsy-vs-control AUC (100x 5-fold CV)")
print("=" * 70)

def repeated_cv_auc(X, y, n_repeats=100, n_splits=5):
    rng = np.random.default_rng(0)
    aucs = np.zeros(n_repeats)
    for r in range(n_repeats):
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True,
                              random_state=int(rng.integers(0, 2**31 - 1)))
        fold = []
        for tr, te in skf.split(X, y):
            pipe = make_pipeline(StandardScaler(), SVC(kernel="linear"))
            pipe.fit(X[tr], y[tr])
            fold.append(roc_auc_score(y[te], pipe.decision_function(X[te])))
        aucs[r] = np.mean(fold)
    return aucs

def build_X(df):
    w = df.pivot_table(index=["subject_id", "cohort"],
                        columns=["measure", "region"], values="z").reset_index()
    w = w.sort_values("subject_id").reset_index(drop=True)
    y = (w["cohort"].values == "patient").astype(int)
    feats = w.drop(columns=["subject_id", "cohort"]).values
    return feats, y

X_mfp, y = build_X(mfp)
X_gml, y2 = build_X(gml)
assert (y == y2).all(), "row order mismatch between MFP and GAMLSS pivots"

print(f"  Feature widths — MFP: {X_mfp.shape[1]}, GAMLSS: {X_gml.shape[1]}")
print(f"  Class balance — patient={y.sum()}, control={(1 - y).sum()}")

print("  Running MFP SVC ...")
a_mfp = repeated_cv_auc(X_mfp, y)
print(f"    AUC  mean={a_mfp.mean():.3f}  95% CI [{np.quantile(a_mfp, 0.025):.3f}, "
      f"{np.quantile(a_mfp, 0.975):.3f}]")
print("  Running GAMLSS SVC ...")
a_gml = repeated_cv_auc(X_gml, y)
print(f"    AUC  mean={a_gml.mean():.3f}  95% CI [{np.quantile(a_gml, 0.025):.3f}, "
      f"{np.quantile(a_gml, 0.975):.3f}]")
d = a_gml - a_mfp
print(f"  ΔAUC (GAMLSS − MFP): mean={d.mean():+.3f}  "
      f"95% CI [{np.quantile(d, 0.025):+.3f}, {np.quantile(d, 0.975):+.3f}]")

# =============================================================================
# Task 8 — Resection concordance
# =============================================================================
print("\n" + "=" * 70)
print("Task 8 — Preop |Z| vs resection %  (Spearman ρ, per subject)")
print("=" * 70)

res = pd.read_csv(ROOT / "ideas_data/table_resected.csv")
res = res.rename(columns={"Unnamed: 0": "region"})
res["region"] = res["region"].str.strip("'")

def normalise(name):
    name = name.strip()
    if name.startswith("ctx-lh-"): return f"lh_{name[len('ctx-lh-'):]}"
    if name.startswith("ctx-rh-"): return f"rh_{name[len('ctx-rh-'):]}"
    return name.replace("-Proper", "")

res["key"] = res["region"].map(normalise)
res_long = res.melt(id_vars=["region", "key"], var_name="subject_id",
                     value_name="resected_frac")
res_long["subject_id"] = res_long["subject_id"].astype(int)
res_long = res_long[res_long["resected_frac"] > 0]

def resection_rho(z_frame):
    z_frame = z_frame.copy()
    def coll(r):
        if r["measure"] in ("thickness", "area"):
            return "_".join(r["region"].split("_")[:2])
        return r["region"]
    z_frame["key"] = z_frame.apply(coll, axis=1)
    z_frame["abs_z"] = z_frame["z"].abs()
    z_per = z_frame.groupby(["subject_id", "key"])["abs_z"].max().reset_index()
    rhos = []
    for sid, rsub in res_long.groupby("subject_id"):
        zsub = z_per[z_per["subject_id"] == sid]
        if len(zsub) == 0: continue
        keys = sorted(set(zsub["key"]))
        zv = zsub.set_index("key")["abs_z"].reindex(keys).values
        rv = rsub.set_index("key")["resected_frac"].reindex(keys, fill_value=0).values
        if np.all(rv == 0): continue
        rho, _ = spearmanr(zv, rv)
        rhos.append(rho)
    return np.array(rhos)

rho_mfp = resection_rho(mfp)
rho_gml = resection_rho(gml)
print(f"  MFP    N={len(rho_mfp)}  ρ mean={rho_mfp.mean():.3f}  median={np.median(rho_mfp):.3f}  frac>0={(rho_mfp > 0).mean() * 100:.0f}%")
print(f"  GAMLSS N={len(rho_gml)}  ρ mean={rho_gml.mean():.3f}  median={np.median(rho_gml):.3f}  frac>0={(rho_gml > 0).mean() * 100:.0f}%")

# =============================================================================
# Save comparison summary
# =============================================================================
per_region.to_csv(ROOT / "score/task5_control_sd_mfp_vs_gamlss.csv", index=False)
h2h.to_csv(ROOT / "score/head_to_head_mfp_vs_gamlss_correlation.csv", index=False)
pd.DataFrame({"algo": ["MFP"] * len(a_mfp) + ["GAMLSS"] * len(a_gml),
              "auc": np.r_[a_mfp, a_gml]}).to_csv(
    ROOT / "score/task7_aucs_mfp_vs_gamlss.csv", index=False)
pd.DataFrame({"algo": ["MFP"] * len(rho_mfp) + ["GAMLSS"] * len(rho_gml),
              "rho": np.r_[rho_mfp, rho_gml]}).to_csv(
    ROOT / "score/task8_resection_rho_mfp_vs_gamlss.csv", index=False)
print(f"\nSaved comparison CSVs to score/")
