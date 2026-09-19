"""Task 5 & 6: sanity-check the CentileBrain-derived Z-scores on IDEAS.

Reads the long-form Z-scores produced by score_centilebrain.R and reports:
* Per-cohort, per-measure distributions (mean, SD, %|Z|>2)
* Per-region SD on controls — the calibration diagnostic
* Comparison against IDEAS's own ComBat-harmonised Z-scores
"""

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path("/mnt/nfs/home/URMC-SH/pndagiji/Documents/Normative")
Z = pd.read_csv(ROOT / "score/ideas_zscores_centilebrain.csv")

print("=" * 70)
print("CentileBrain Z-scores on IDEAS: distributional summary")
print("=" * 70)

# Overall by cohort / measure
grp = Z.groupby(["cohort", "measure"]).agg(
    n=("z", "size"),
    mean_z=("z", "mean"),
    sd_z=("z", "std"),
    pct_extreme=("z", lambda s: 100 * (s.abs() > 2).mean()),
)
print(grp.to_string(float_format="%.3f"))

print()
print("=" * 70)
print("Per-region SD on CONTROLS  (SD ≈ 1.0 = well-calibrated)")
print("=" * 70)
ctl = Z[Z["cohort"] == "control"]
per_region = ctl.groupby(["measure", "region"])["z"].agg(["mean", "std", "size"]).reset_index()
per_region.columns = ["measure", "region", "mean_z", "sd_z", "n"]
per_region = per_region.sort_values(["measure", "sd_z"], ascending=[True, False])

for measure in per_region["measure"].unique():
    sub = per_region[per_region["measure"] == measure]
    print(f"\n--- {measure} ({len(sub)} regions) ---")
    print(f"  SD range: [{sub['sd_z'].min():.2f}, {sub['sd_z'].max():.2f}]  "
          f"median: {sub['sd_z'].median():.2f}")
    # 5 worst & 5 best transfers (SD farthest from vs. closest to 1.0)
    sub = sub.assign(sd_dev=(sub["sd_z"] - 1.0).abs())
    print("  most over-dispersed on controls (SD >> 1):")
    for _, r in sub.nlargest(5, "sd_z").iterrows():
        print(f"    {r['region']:45s}  SD={r['sd_z']:.2f}  mean={r['mean_z']:.2f}")
    print("  best-calibrated (SD closest to 1):")
    for _, r in sub.nsmallest(5, "sd_dev").iterrows():
        print(f"    {r['region']:45s}  SD={r['sd_z']:.2f}  mean={r['mean_z']:.2f}")

# ---------------------------------------------------------------------------
# Task 6: compare with IDEAS's own ComBat-harmonised Z-scores
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("Task 6: Convergence with IDEAS internal Z-scores")
print("=" * 70)

# Load IDEAS Z-scores (patients only — that's what the release provides)
ideas_thick = pd.read_csv(ROOT / "ideas_data/thick_zscores_patients.csv")
ideas_area  = pd.read_csv(ROOT / "ideas_data/area_zscores_patients.csv")
ideas_vol   = pd.read_csv(ROOT / "ideas_data/vol_zscores_patients.csv")

print(f"IDEAS thickness Z: {ideas_thick.shape} (patients only)")
print(f"IDEAS area Z:      {ideas_area.shape}")
print(f"IDEAS volume Z:    {ideas_vol.shape}")

# For each measure, correlate per-region across matching patients.
def convergence(measure_label, ideas_df, area_rename=None):
    cb = Z[(Z["measure"] == measure_label) & (Z["cohort"] == "patient")]
    cb_wide = cb.pivot_table(index="subject_id", columns="region", values="z")
    ideas_df = ideas_df.set_index("ID")
    if area_rename is not None:
        ideas_df = ideas_df.rename(columns=area_rename)
    common_ids = sorted(set(cb_wide.index) & set(ideas_df.index))
    common_regions = sorted(set(cb_wide.columns) & set(ideas_df.columns))
    rows = []
    for region in common_regions:
        a = cb_wide.loc[common_ids, region]
        b = ideas_df.loc[common_ids, region]
        valid = a.notna() & b.notna()
        if valid.sum() >= 20:
            rows.append({"measure": measure_label, "region": region,
                         "r": a[valid].corr(b[valid]), "n": int(valid.sum())})
    df = pd.DataFrame(rows).sort_values("r", ascending=False)
    print(f"\n--- {measure_label} — N regions matched: {len(df)}, N common IDs: {len(common_ids)} ---")
    print(f"  r median={df['r'].median():.3f}  mean={df['r'].mean():.3f}  "
          f"range=[{df['r'].min():.3f}, {df['r'].max():.3f}]")
    print(f"  fraction r > 0.7:  {(df['r'] > 0.7).mean() * 100:.0f}%")
    print(f"  fraction r > 0.9:  {(df['r'] > 0.9).mean() * 100:.0f}%")
    print(f"  Top 3: {list(df.nlargest(3, 'r')['region'])}")
    print(f"  Bot 3: {list(df.nsmallest(3, 'r')['region'])}")
    return df

# IDEAS area columns use `_area` suffix, matching ours directly.
# IDEAS subcortical columns use `Left_Thalamus_volume` (underscore-dash swap).
sub_rename = {}
for hemi in ("Left", "Right"):
    for region in ("Thalamus", "Caudate", "Putamen", "Pallidum",
                   "Hippocampus", "Amygdala", "Accumbens-area"):
        old = f"{hemi}_{region.replace('-','_')}_volume"
        new = f"{hemi}-{region}"
        sub_rename[old] = new

corr_thick = convergence("thickness", ideas_thick)
corr_area  = convergence("area", ideas_area)
corr_sub   = convergence("subcortical", ideas_vol, area_rename=sub_rename)

# Save concatenated per-region convergence table
all_corr = pd.concat([corr_thick, corr_area, corr_sub], ignore_index=True)
all_corr.to_csv(ROOT / "score/ideas_vs_centilebrain_corr.csv", index=False)
per_region.to_csv(ROOT / "score/per_region_controls_summary.csv", index=False)

print(f"\nWrote:")
print(f"  score/per_region_controls_summary.csv  ({len(per_region)} rows)")
print(f"  score/ideas_vs_centilebrain_corr.csv   ({len(all_corr)} rows)")
