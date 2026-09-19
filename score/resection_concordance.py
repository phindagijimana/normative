"""Task 8: does the preop CentileBrain Z-score peak in the DK region that was
later resected? Restrict to surgical cases with good ILAE-1 outcome as the
strongest test (surgery corrected the epileptogenic zone → deviation there
should be a real biomarker of the epileptogenic focus).

Metrics per subject:
* Spearman correlation between per-region |Z| and per-region resection %
* Top-K precision: of the K regions with highest |Z|, how many are in the
  top K by resection %?
"""

from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import spearmanr

ROOT = Path("/mnt/nfs/home/URMC-SH/pndagiji/Documents/Normative")

# ---- Resection percentages (regions × subjects, transposed) ---------------
res = pd.read_csv(ROOT / "ideas_data/table_resected.csv")
res = res.rename(columns={"Unnamed: 0": "region"})
res["region"] = res["region"].str.strip("'")

# Normalise region names to a common per-DK-region key
def normalise(name: str) -> str:
    """Convert either 'ctx-lh-bankssts' or 'Left-Thalamus-Proper' to a canonical
    tag that also matches our Z-score naming."""
    name = name.strip()
    if name.startswith("ctx-lh-"):
        return f"lh_{name[len('ctx-lh-'):]}"
    if name.startswith("ctx-rh-"):
        return f"rh_{name[len('ctx-rh-'):]}"
    # subcortical: strip '-Proper' suffix
    return name.replace("-Proper", "")

res["key"] = res["region"].map(normalise)
res_long = res.melt(id_vars=["region", "key"], var_name="subject_id",
                    value_name="resected_frac")
res_long["subject_id"] = res_long["subject_id"].astype(int)
res_long = res_long[res_long["resected_frac"] > 0]  # keep only resected regions
print(f"Resection long-form: {len(res_long)} region-subject entries with resected > 0")
print(f"Subjects with any resection: {res_long['subject_id'].nunique()}")

# ---- Z-scores (long) — collapse across measure per region ------------------
z_long = pd.read_csv(ROOT / "score/ideas_zscores_centilebrain.csv")

def collapse_region_name(row):
    """Map (measure, region) to the same 'key' as the resection table.
    For cortical: derive from region string. For subcortical: region is
    already 'Left-Thalamus' etc."""
    if row["measure"] in ("thickness", "area"):
        # region like 'lh_bankssts_thickness' -> 'lh_bankssts'
        return "_".join(row["region"].split("_")[:2])
    return row["region"]

z_long["key"] = z_long.apply(collapse_region_name, axis=1)

# Combine thickness + area + subcortical into a single per-region deviation:
# take max |z| across measures (a region is "abnormal" if any measure is
# extreme).
z_long["abs_z"] = z_long["z"].abs()
z_per_region = z_long.groupby(["subject_id", "cohort", "sex", "age", "key"])["abs_z"].max().reset_index()

# ---- Load metadata for ILAE outcome & Op_Side -----------------------------
meta = pd.read_csv(ROOT / "ideas_data/Metadata_Release_Anon.csv")
meta = meta.rename(columns={"ID": "subject_id"}).drop_duplicates(subset="subject_id")

# Merge z per-region with per-subject metadata
z_per_region = z_per_region.merge(meta[["subject_id", "ILAE_Year1", "Op_Side"]],
                                  on="subject_id", how="left")

# ---- Concordance metrics per subject ---------------------------------------
def subject_concordance(subject_id, res_sub, z_sub):
    """Return per-subject Spearman r, top-3 precision, and rank of highest-|z|
    region among resected regions."""
    common = set(res_sub["key"]) & set(z_sub["key"])
    if not common:
        return None
    # Align on regions that exist in BOTH tables (we care about cortical +
    # subcortical DK regions that we have Z-scores for).
    all_keys = sorted(set(z_sub["key"]))
    z_map = z_sub.set_index("key")["abs_z"]
    r_map = res_sub.set_index("key")["resected_frac"].reindex(all_keys, fill_value=0)
    z_vals = z_map.reindex(all_keys).values
    r_vals = r_map.values
    if np.all(r_vals == 0):
        return None
    rho, _ = spearmanr(z_vals, r_vals)
    # Top-K precision
    top_k = 5
    top_by_z = pd.Series(z_vals, index=all_keys).nlargest(top_k).index
    top_by_r = pd.Series(r_vals, index=all_keys).nlargest(top_k).index
    top_k_hits = len(set(top_by_z) & set(top_by_r))
    # Which region has the maximum |z|? Was it resected at all?
    top_z_region = all_keys[int(np.argmax(z_vals))]
    top_z_resected = r_map[top_z_region] > 0
    return dict(subject_id=subject_id, rho=rho, top5_hits=top_k_hits,
                top_z_region=top_z_region, top_z_resected=top_z_resected,
                n_resected=int((r_vals > 0).sum()))

rows = []
for sid, res_sub in res_long.groupby("subject_id"):
    z_sub = z_per_region[z_per_region["subject_id"] == sid]
    if len(z_sub) == 0:
        continue
    d = subject_concordance(sid, res_sub, z_sub)
    if d is None:
        continue
    # Attach outcome from metadata
    ilae1 = meta.loc[meta["subject_id"] == sid, "ILAE_Year1"].squeeze()
    d["ILAE_Year1"] = ilae1 if not isinstance(ilae1, pd.Series) else np.nan
    rows.append(d)

conc = pd.DataFrame(rows)
conc.to_csv(ROOT / "score/resection_concordance.csv", index=False)

# ---- Report ----------------------------------------------------------------
def print_group(label, sub):
    if len(sub) == 0:
        print(f"\n{label} — N=0 (no subjects)")
        return
    print(f"\n{label} — N={len(sub)}")
    print(f"  Spearman rho (|Z| vs resection %):    "
          f"mean={sub['rho'].mean():.3f}  median={sub['rho'].median():.3f}  "
          f"positive fraction={(sub['rho'] > 0).mean() * 100:.0f}%")
    print(f"  top-5 hit rate (out of 5):            mean={sub['top5_hits'].mean():.2f}")
    print(f"  top-|Z| region was resected:          "
          f"{sub['top_z_resected'].mean() * 100:.0f}%")

print(f"\nTotal surgical subjects with Z + resection data: {len(conc)}")
print_group("All surgical patients", conc)
print_group("ILAE_Year1 = 1 (seizure-free at year 1)",
            conc[conc["ILAE_Year1"] == 1])
print_group("ILAE_Year1 >= 2 (not seizure-free)",
            conc[conc["ILAE_Year1"] >= 2])

# Comparison against a chance baseline: shuffle resection percentages
print("\n=== Permutation baseline (shuffle resected per subject) ===")
np.random.seed(0)
null_rhos = []
for sid, res_sub in res_long.groupby("subject_id"):
    z_sub = z_per_region[z_per_region["subject_id"] == sid]
    if len(z_sub) == 0:
        continue
    all_keys = sorted(set(z_sub["key"]))
    z_map = z_sub.set_index("key")["abs_z"].reindex(all_keys).values
    r_map = res_sub.set_index("key")["resected_frac"].reindex(all_keys, fill_value=0).values
    if np.all(r_map == 0):
        continue
    # Shuffle the resection assignments across regions
    shuffled = np.random.permutation(r_map)
    rho_null, _ = spearmanr(z_map, shuffled)
    null_rhos.append(rho_null)
null_rhos = np.array(null_rhos)
print(f"  null rho: mean={null_rhos.mean():+.3f}  median={np.median(null_rhos):+.3f}")

print(f"\nWrote: score/resection_concordance.csv ({len(conc)} rows)")
