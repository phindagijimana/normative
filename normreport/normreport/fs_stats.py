"""Parse FreeSurfer aparc/aseg stats files into a canonical per-subject
dictionary keyed by our internal region naming (matches IDEAS + the
CentileBrain templates).

Accepts either:
* A path to a FreeSurfer subject `stats/` directory, or
* A pre-extracted CSV with one row per subject and columns following the
  IDEAS `ideas_merged.csv` schema (68 lh_* thickness + 68 lh_* area + 14
  Left-*/Right-* subcortical + eTIV + mean_thickness + mean_surface_area).

For MVP we support the CSV path (fastest to test); native `stats/`
parsing is a v1.1 item.
"""
from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd


REQUIRED_GLOBALS = ("eTIV", "mean_thickness", "mean_surface_area")


def load_subject(source: Union[str, Path]) -> dict:
    """Return a per-subject dict of {region_name: value} plus globals.

    `source` may be:
      * a CSV file with a single row (or one row matching a subject_id
        supplied via the CLI)
      * a directory containing an `aparc_stats.csv` and/or
        `aseg_stats.csv` (v1.1 fallback; not implemented for MVP)
    """
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"Subject source not found: {source}")

    if path.is_file() and path.suffix in (".csv", ".tsv"):
        sep = "\t" if path.suffix == ".tsv" else ","
        df = pd.read_csv(path, sep=sep)
        if len(df) == 0:
            raise ValueError(f"Empty subject CSV: {source}")
        row = df.iloc[0].to_dict()
        _validate_subject_dict(row)
        return row

    raise NotImplementedError(
        f"Native FreeSurfer stats/ directory parsing is a v1.1 feature. "
        f"For v1.0 supply a CSV with the canonical schema (see the demo "
        f"in examples/demo_subject_stats.csv)."
    )


def _validate_subject_dict(d: dict) -> None:
    missing_globals = [g for g in REQUIRED_GLOBALS if g not in d]
    if missing_globals:
        raise ValueError(f"Subject CSV missing required global covariates: "
                         f"{missing_globals}. See examples/demo_subject_stats.csv")
    # Spot-check a few regional columns
    for c in ("lh_bankssts_thickness", "rh_insula_area", "Left-Thalamus"):
        if c not in d:
            raise ValueError(f"Subject CSV missing regional column: {c}")


def load_reference_cohort(path: Union[str, Path]) -> pd.DataFrame:
    """Load a reference-cohort CSV. Same schema as a subject CSV but with
    N > 1 rows, each representing a healthy control."""
    df = pd.read_csv(path)
    for c in REQUIRED_GLOBALS + ("sex", "age", "subject_id"):
        if c not in df.columns:
            raise ValueError(f"Reference cohort missing column: {c}")
    return df
