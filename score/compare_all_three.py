"""Three-backend comparison: MFP vs GAMLSS vs PCN Toolkit on cortical
thickness (the common intersection of what all three backends score).

Runs the same four validation tasks as compare_mfp_gamlss.py:
  Task 5 — Control Z SD per algorithm
  Task 6 — Convergence with IDEAS internal ComBat Z-scores
  Task 7 — SVC classification (deferred; use existing task7_aucs)
  Task 8 — Resection concordance (three-way)
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path("/mnt/nfs/home/URMC-SH/pndagiji/Documents/Normative")

mfp = pd.read_csv(ROOT / "score/ideas_zscores_centilebrain.csv")
gml = pd.read_csv(ROOT / "score/ideas_zscores_centilebrain_gamlss.csv")
pcn = pd.read_csv(ROOT / "score/ideas_zscores_pcn.csv")

# Keep common schema
for df, name in [(mfp, "MFP"), (gml, "GAMLSS"), (pcn, "PCN")]:
    df["algo"] = name

# Restrict all three to cortical thickness (PCN's common ground)
z_all = pd.concat([
    mfp[mfp["measure"] == "thickness"][["subject_id", "cohort", "sex", "age",
                                          "measure", "region", "z", "algo"]],
    gml[gml["measure"] == "thickness"][["subject_id", "cohort", "sex", "age",
                                          "measure", "region", "z", "algo"]],
    pcn[pcn["measure"] == "thickness"][["subject_id", "cohort", "sex", "age",
                                          "measure", "region", "z", "algo"]],
], ignore_index=True)

# ---- Task 5: control SD --------------------------------------------------
print("=" * 60)
print("Task 5 — Control Z SD (cortical thickness, 68 regions)")
print("=" * 60)
ctl = z_all[z_all["cohort"] == "control"]
per_region = (ctl.groupby(["algo", "region"])["z"].std().unstack("algo"))
print(f"Per-region SD median across all three algorithms:")
print(per_region.median().to_string(float_format="%.3f"))

per_region.to_csv(ROOT / "score/task5_three_backend_control_sd.csv")

# ---- Task 6: convergence with IDEAS internal ---------------------------
print("\n" + "=" * 60)
print("Task 6 — Convergence with IDEAS-internal ComBat Z-scores (patients)")
print("=" * 60)
ideas_thick = pd.read_csv(ROOT / "ideas_data/thick_zscores_patients.csv").set_index("ID")

results_conv = []
for algo in ("MFP", "GAMLSS", "PCN"):
    sub = z_all[(z_all["algo"] == algo) & (z_all["cohort"] == "patient")]
    wide = sub.pivot_table(index="subject_id", columns="region", values="z")
    # subject_id in PCN is string, MFP/GAMLSS is int — coerce
    wide.index = wide.index.astype(int)
    common_ids = sorted(set(wide.index) & set(ideas_thick.index))
    common_regions = sorted(set(wide.columns) & set(ideas_thick.columns))
    rs = []
    for r in common_regions:
        a = wide.loc[common_ids, r]
        b = ideas_thick.loc[common_ids, r]
        v = a.notna() & b.notna()
        if v.sum() >= 20:
            rs.append(a[v].corr(b[v]))
    rs = np.array(rs)
    results_conv.append({
        "algorithm": algo,
        "n_regions_matched": len(rs),
        "n_subjects": len(common_ids),
        "median_r": float(np.median(rs)),
        "mean_r": float(rs.mean()),
        "frac_r_gt_0.7": float((rs > 0.7).mean()),
        "frac_r_gt_0.9": float((rs > 0.9).mean()),
    })

conv = pd.DataFrame(results_conv)
print(conv.to_string(float_format="%.3f"))
conv.to_csv(ROOT / "score/task6_three_backend_convergence.csv", index=False)

# ---- Task 8: resection concordance -------------------------------------
print("\n" + "=" * 60)
print("Task 8 — Preop |Z| vs resection % (Spearman rho, per subject)")
print("=" * 60)
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

def _key(row):
    if row["measure"] == "thickness":
        return "_".join(row["region"].split("_")[:2])
    return row["region"]

def resection_rho(z_frame, algo_label):
    z_frame = z_frame.copy()
    z_frame["key"] = z_frame.apply(_key, axis=1)
    z_frame["abs_z"] = z_frame["z"].abs()
    z_frame["subject_id"] = z_frame["subject_id"].astype(int)
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
    rhos = np.array(rhos)
    return {"algorithm": algo_label, "n": len(rhos),
            "mean_rho": float(rhos.mean()),
            "median_rho": float(np.median(rhos)),
            "frac_pos": float((rhos > 0).mean())}

rhos_all = [
    resection_rho(mfp, "MFP"),
    resection_rho(gml, "GAMLSS"),
    resection_rho(pcn, "PCN"),
]
res_df = pd.DataFrame(rhos_all)
print(res_df.to_string(float_format="%.3f"))
res_df.to_csv(ROOT / "score/task8_three_backend_resection.csv", index=False)

print("\nDone. Three-backend comparison complete.")
