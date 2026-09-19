"""Load the downloaded IDEAS tabular files into a single per-subject DataFrame
suitable for CentileBrain MFPR scoring.

Output columns (see :func:`load` for the exact set):
* ``subject_id`` — int, 1..~442 for patients, 4001..4100 for controls
* ``cohort`` — "patient" or "control"
* ``sex`` — "M" or "F"
* ``age_bin`` — original bin label ("20 to 24")
* ``age`` — bin midpoint (float years). CentileBrain expects continuous age;
  the IDEAS release only ships 5-year bins for de-identification, so we use
  midpoints as a documented approximation.
* 68 columns ``lh_<region>_thickness`` / ``rh_<region>_thickness``  (DK)
* 68 columns ``lh_<region>_area``       / ``rh_<region>_area``      (DK)
* 14 aseg subcortical volume columns following CentileBrain conventions
* Global covariates: ``eTIV``, ``mean_thickness``, ``total_surface_area``
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent

# ---- CentileBrain-relevant region lists ---------------------------------

DK_REGIONS = [
    "bankssts", "caudalanteriorcingulate", "caudalmiddlefrontal", "cuneus",
    "entorhinal", "fusiform", "inferiorparietal", "inferiortemporal",
    "isthmuscingulate", "lateraloccipital", "lateralorbitofrontal", "lingual",
    "medialorbitofrontal", "middletemporal", "parahippocampal", "paracentral",
    "parsopercularis", "parsorbitalis", "parstriangularis", "pericalcarine",
    "postcentral", "posteriorcingulate", "precentral", "precuneus",
    "rostralanteriorcingulate", "rostralmiddlefrontal", "superiorfrontal",
    "superiorparietal", "superiortemporal", "supramarginal", "frontalpole",
    "temporalpole", "transversetemporal", "insula",
]  # 34 DK regions per hemisphere

# The 14 CentileBrain aseg subcortical measures (7 per hemisphere).
ASEG_REGIONS = [
    "Left-Thalamus", "Left-Caudate", "Left-Putamen", "Left-Pallidum",
    "Left-Hippocampus", "Left-Amygdala", "Left-Accumbens-area",
    "Right-Thalamus", "Right-Caudate", "Right-Putamen", "Right-Pallidum",
    "Right-Hippocampus", "Right-Amygdala", "Right-Accumbens-area",
]

# IDEAS releases numeric bins like "20 to 24", plus a top bin "70+". We treat
# each as the midpoint (or 72.5 for the open-ended bin).
_BIN_RE = re.compile(r"(\d+)\s*to\s*(\d+)")
_LESS_RE = re.compile(r"less\s*than\s*(\d+)", re.I)
_OVER_RE = re.compile(r"(?:over|more\s*than)\s*(\d+)", re.I)


def bin_to_midpoint(bin_label: str) -> float:
    """Return a numeric age for an IDEAS bin.

    Closed bins ("20 to 24") → midpoint (22.0).
    "Less than X" → X − 2.5 (assumes a 5-year lower tail).
    "Over X"      → X + 2.5 (assumes a 5-year upper tail; imputation is
    approximate — see feedback-ideas-age-binned memory).
    """
    if pd.isna(bin_label):
        return float("nan")
    bin_label = str(bin_label).strip()
    m = _BIN_RE.match(bin_label)
    if m:
        return (int(m.group(1)) + int(m.group(2))) / 2.0
    m = _LESS_RE.match(bin_label)
    if m:
        return int(m.group(1)) - 2.5
    m = _OVER_RE.match(bin_label)
    if m:
        return int(m.group(1)) + 2.5
    if bin_label.endswith("+"):
        return float(bin_label.rstrip("+")) + 2.5
    return float("nan")


def _read_stats(path: Path) -> pd.DataFrame:
    """Read a FreeSurfer stats file (regions × subjects) and return
    subjects × regions."""
    df = pd.read_csv(path, sep="\t", index_col=0)
    df.columns = df.columns.astype(int)
    return df.T  # rows = subjects, cols = regions


def _cortical_cols(measure_suffix: str) -> list[str]:
    """DK cortical column names in the raw stats files."""
    cols: list[str] = []
    for hemi in ("lh", "rh"):
        for region in DK_REGIONS:
            cols.append(f"{hemi}_{region}_{measure_suffix}")
    return cols


def load() -> pd.DataFrame:
    """Load and merge every IDEAS table into a single per-subject DataFrame."""
    # ---- stats ----------------------------------------------------------
    thick_p = _read_stats(HERE / "aparc_thick.txt")
    thick_c = _read_stats(HERE / "controls_aparc_thick.txt")
    area_p = _read_stats(HERE / "aparc_area.txt")
    area_c = _read_stats(HERE / "controls_aparc_area.txt")
    aseg_p = _read_stats(HERE / "aseg_vol.txt")
    aseg_c = _read_stats(HERE / "controls_aseg_vol.txt")

    # ---- cortical thickness (rename `_thickness` → keep as-is) ---------
    thick_cols = _cortical_cols("thickness")
    # Sanity: every expected DK column present in both patient and control tables
    for name, tbl in [("patients thickness", thick_p), ("controls thickness", thick_c)]:
        missing = set(thick_cols) - set(tbl.columns)
        if missing:
            raise ValueError(f"{name}: missing DK thickness cols {sorted(missing)[:5]}")

    # ---- cortical area — file uses `_area` suffix natively
    area_cols = _cortical_cols("area")
    for name, tbl in [("patients area", area_p), ("controls area", area_c)]:
        missing = set(area_cols) - set(tbl.columns)
        if missing:
            raise ValueError(f"{name}: missing DK area cols {sorted(missing)[:5]}")

    # ---- aseg volumes ---------------------------------------------------
    for name, tbl in [("patients aseg", aseg_p), ("controls aseg", aseg_c)]:
        missing = set(ASEG_REGIONS) - set(tbl.columns)
        if missing:
            raise ValueError(f"{name}: missing aseg cols {sorted(missing)[:5]}")

    def _core_block(thick: pd.DataFrame, area: pd.DataFrame, aseg: pd.DataFrame,
                    cohort_label: str) -> pd.DataFrame:
        idx = thick.index
        block = pd.concat(
            [
                thick[thick_cols],
                area[area_cols],
                aseg[ASEG_REGIONS],
                aseg[["EstimatedTotalIntraCranialVol"]].rename(
                    columns={"EstimatedTotalIntraCranialVol": "eTIV"}
                ),
            ],
            axis=1,
        )
        # Global covariates
        block["mean_thickness"] = (
            thick["lh_MeanThickness_thickness"] + thick["rh_MeanThickness_thickness"]
        ) / 2.0
        # CentileBrain trained the area model with a covariate literally
        # named `meanarea`. Provide bilateral mean of hemispheric totals.
        block["mean_surface_area"] = (
            area["lh_WhiteSurfArea_area"] + area["rh_WhiteSurfArea_area"]
        ) / 2.0
        block["total_surface_area"] = (
            area["lh_WhiteSurfArea_area"] + area["rh_WhiteSurfArea_area"]
        )
        block["cohort"] = cohort_label
        block.index.name = "subject_id"
        return block

    patients = _core_block(thick_p, area_p, aseg_p, "patient")
    controls = _core_block(thick_c, area_c, aseg_c, "control")
    stats = pd.concat([patients, controls]).reset_index()

    # ---- metadata -------------------------------------------------------
    meta_p = pd.read_csv(HERE / "Metadata_Release_Anon.csv")
    meta_c = pd.read_csv(HERE / "Metadata_Controls_Release.csv")
    # Harmonise columns: keep ID/Sex/Binned_Age_at_Scan from both, plus any
    # extra clinical fields on the patient side.
    meta_c = meta_c.rename(columns={"ID": "subject_id"})
    meta_p = meta_p.rename(columns={"ID": "subject_id"})
    meta = pd.concat([meta_p, meta_c], ignore_index=True)
    meta["subject_id"] = meta["subject_id"].astype(int)
    # Patient 209 appears twice in the IDEAS metadata release; the rows are
    # byte-identical, so deduplicate before merging.
    meta = meta.drop_duplicates(subset="subject_id", keep="first")
    meta = meta.rename(columns={"Sex": "sex", "Binned_Age_at_Scan": "age_bin"})
    meta["age"] = meta["age_bin"].map(bin_to_midpoint)

    df = stats.merge(meta, on="subject_id", how="left", validate="one_to_one")
    return df


def summary(df: pd.DataFrame) -> None:
    """Print a compact schema/coverage summary."""
    print(f"total rows: {len(df)}")
    print(f"cohorts:    {df['cohort'].value_counts().to_dict()}")
    print(f"sex:        {df['sex'].value_counts(dropna=False).to_dict()}")
    print(f"age bins:   {sorted(df['age_bin'].dropna().unique())}")
    print(f"age range (midpoint): {df['age'].min():.1f} – {df['age'].max():.1f}")
    print(f"missing sex/age: sex={df['sex'].isna().sum()}, age={df['age'].isna().sum()}")

    thick_cols = _cortical_cols("thickness")
    area_cols = _cortical_cols("area")
    print(f"cortical thickness cols: {len(thick_cols)}  (all present: "
          f"{set(thick_cols).issubset(df.columns)})")
    print(f"cortical area cols:      {len(area_cols)}  (all present: "
          f"{set(area_cols).issubset(df.columns)})")
    print(f"aseg subcortical cols:   {len(ASEG_REGIONS)} (all present: "
          f"{set(ASEG_REGIONS).issubset(df.columns)})")
    print(f"globals: eTIV, mean_thickness, total_surface_area present: "
          f"{{ 'eTIV' in df, 'mean_thickness' in df, 'total_surface_area' in df }}")


if __name__ == "__main__":
    df = load()
    summary(df)
    out = HERE / "ideas_merged.csv"
    df.to_csv(out, index=False)
    print(f"\nwrote {out} ({out.stat().st_size / 1024:.1f} KiB)")
