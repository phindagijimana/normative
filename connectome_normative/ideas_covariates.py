#!/usr/bin/env python3
"""Build covariates.csv for multiscale_normative.py from the IDEAS metadata.

Groups
  notSF1   ILAE outcome > 1 at year 1
  durable  ILAE 1 at every recorded year, with follow-up >= --min-followup years
  relapse  ILAE 1 at year 1, ILAE > 1 later (written only with --keep-relapse)
  control  IDEAS healthy controls
Patients seizure-free so far but with follow-up shorter than --min-followup are dropped.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

IDEAS = Path(__file__).resolve().parent.parent / "ideas_data"
sys.path.insert(0, str(IDEAS))
from load_ideas import bin_to_midpoint  # noqa: E402

YEARS = [f"ILAE_Year{i}" for i in range(1, 6)]


def outcome_group(row: pd.Series, min_followup: int) -> str | None:
    y = row[YEARS].to_numpy(float)
    seen = np.flatnonzero(~np.isnan(y))
    if np.isnan(y[0]):
        return None
    if y[0] > 1:
        return "notSF1"
    later = y[1:][~np.isnan(y[1:])]
    if (later > 1).any():
        return "relapse"
    return "durable" if seen.max() + 1 >= min_followup else None


def build(min_followup: int, keep_relapse: bool, prefix: str) -> pd.DataFrame:
    pat = pd.read_csv(IDEAS / "Metadata_Release_Anon.csv")
    ctl = pd.read_csv(IDEAS / "Metadata_Controls_Release.csv")
    pat["group"] = pat.apply(outcome_group, axis=1, min_followup=min_followup)
    keep = {"notSF1", "durable"} | ({"relapse"} if keep_relapse else set())
    pat = pat[pat["group"].isin(keep)]
    pat_out = pd.DataFrame({
        "subject": prefix + pat["ID"].astype(str), "group": pat["group"],
        "age": pat["Binned_Age_at_Scan"].map(bin_to_midpoint), "sex": pat["Sex"],
        "op_side": pat["Op_Side"], "op_type": pat["Op_Type"], "pathology": pat["Pathology"],
    })
    ctl_out = pd.DataFrame({
        "subject": prefix + ctl["ID"].astype(str), "group": "control",
        "age": ctl["Binned_Age_at_Scan"].astype(str).str.strip().map(bin_to_midpoint),
        "sex": ctl["Sex"], "op_side": np.nan, "op_type": np.nan, "pathology": np.nan,
    })
    out = pd.concat([ctl_out, pat_out], ignore_index=True)
    return out.dropna(subset=["age", "sex"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=Path("covariates.csv"))
    ap.add_argument("--min-followup", type=int, default=3, help="years required for 'durable'")
    ap.add_argument("--keep-relapse", action="store_true")
    ap.add_argument("--prefix", default="sub-", help="subject ID prefix matching matrix filenames")
    a = ap.parse_args()
    df = build(a.min_followup, a.keep_relapse, a.prefix)
    df.to_csv(a.out, index=False)
    print(df.groupby("group").agg(n=("subject", "size"), age_mean=("age", "mean"),
                                  female=("sex", lambda s: (s == "F").sum()),
                                  left_op=("op_side", lambda s: (s == "L").sum())))


if __name__ == "__main__":
    main()
