"""Bootstrap 95% CIs on the lateralisation accuracy and per-subject
resection Spearman rho estimates. NeuroImage reviewers expect a CI on
every reported metric; adds rigor without new experiments.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/mnt/nfs/home/URMC-SH/pndagiji/Documents/Normative")
SCORE = ROOT / "score"
OUT_LAT = SCORE / "lateralization_bootstrap_ci.csv"
OUT_RES = SCORE / "resection_bootstrap_ci.csv"

N_BOOT = 10_000
RNG = np.random.default_rng(20260919)


def _ci(values, alpha=0.05):
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if v.size == 0:
        return np.nan, np.nan, np.nan
    return v.mean(), np.percentile(v, 100 * alpha / 2), np.percentile(v, 100 * (1 - alpha / 2))


def bootstrap_accuracy(correct: np.ndarray, n_boot: int = N_BOOT):
    """Percentile bootstrap on the mean of a 0/1 vector."""
    n = len(correct)
    idx = RNG.integers(0, n, size=(n_boot, n))
    boot = correct[idx].mean(axis=1)
    return _ci(boot)


def bootstrap_mean_rho(rhos: np.ndarray, n_boot: int = N_BOOT):
    n = len(rhos)
    idx = RNG.integers(0, n, size=(n_boot, n))
    boot = rhos[idx].mean(axis=1)
    return _ci(boot)


def lateralisation_cis():
    """Bootstrap the accuracy in lateralization_results.csv.

    The raw per-subject correct/incorrect labels aren't in that CSV,
    but we can reconstruct them from lateralization_per_subject.csv if it
    exists, else approximate a beta-distribution CI on (accuracy, N).
    """
    lat = pd.read_csv(SCORE / "lateralization_results.csv")

    per_subj_path = SCORE / "lateralization_per_subject.csv"
    if per_subj_path.exists():
        per = pd.read_csv(per_subj_path)
    else:
        per = None

    rows = []
    for _, r in lat.iterrows():
        n = int(r["n"])
        acc = float(r["accuracy"])
        if per is not None and "algorithm" in per and "group" in per:
            mask = (per["algorithm"] == r["algorithm"]) & (per["group"] == r["group"])
            if mask.any():
                correct = per.loc[mask, "correct"].to_numpy(dtype=float)
                mean, lo, hi = bootstrap_accuracy(correct)
                rows.append({**r.to_dict(),
                             "acc_ci_lo": lo, "acc_ci_hi": hi,
                             "ci_method": "bootstrap"})
                continue
        # Fallback: Wilson (or Clopper-Pearson) CI on a binomial proportion
        from scipy.stats import beta as beta_dist
        k = int(round(acc * n))
        lo = beta_dist.ppf(0.025, k, n - k + 1) if k > 0 else 0.0
        hi = beta_dist.ppf(0.975, k + 1, n - k) if k < n else 1.0
        rows.append({**r.to_dict(),
                     "acc_ci_lo": lo, "acc_ci_hi": hi,
                     "ci_method": "clopper-pearson"})
    df = pd.DataFrame(rows)
    df.to_csv(OUT_LAT, index=False)
    print(f"wrote {OUT_LAT} ({len(df)} rows)")
    print(df[["algorithm", "group", "n", "accuracy",
              "acc_ci_lo", "acc_ci_hi", "ci_method"]].to_string(index=False))


def resection_cis():
    per = pd.read_csv(SCORE / "task8_resection_rho_mfp_vs_gamlss.csv")
    three = pd.read_csv(SCORE / "task8_three_backend_resection.csv")

    rows = []
    for algo in ("MFP", "GAMLSS"):
        rhos = per[per["algo"] == algo]["rho"].to_numpy(dtype=float)
        mean, lo, hi = bootstrap_mean_rho(rhos)
        rows.append({"backend": f"CentileBrain-{algo}",
                     "n": len(rhos),
                     "mean_rho": mean,
                     "ci_lo": lo,
                     "ci_hi": hi,
                     "feature_set": "150 regions"})
    # PCN
    pcn_row = three[three["algorithm"] == "PCN"].iloc[0]
    # Reconstruct per-subject from ideas_zscores_pcn.csv? Simpler: use the
    # aggregate summary's mean and estimate CI parametrically via SE of a
    # mean of correlations (Fisher z). Here we simply annotate that the
    # three-backend PCN CI is limited to 68 cortical thickness regions;
    # to keep the table consistent, compute a Fisher-z-based CI from
    # (mean, N, sd approximated).
    pcn_mean = float(pcn_row["mean_rho"])
    pcn_median = float(pcn_row["median_rho"])
    n = int(pcn_row["n"])
    # Approximate SD from mean/median gap + n
    # Better: leave as point + note
    rows.append({"backend": "PCN Toolkit-Bayesian",
                 "n": n,
                 "mean_rho": pcn_mean,
                 "ci_lo": np.nan,
                 "ci_hi": np.nan,
                 "feature_set": "68 regions (per-subject data not exported)"})
    df = pd.DataFrame(rows)
    df.to_csv(OUT_RES, index=False)
    print(f"\nwrote {OUT_RES} ({len(df)} rows)")
    print(df.to_string(index=False))


if __name__ == "__main__":
    lateralisation_cis()
    resection_cis()
