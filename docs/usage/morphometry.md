# Morphometry CLI reference

How-to: {doc}`../tutorials/01_ideas_morphometry`, {doc}`../tutorials/02_own_cohort`.
Schema: {doc}`../inputs`.

| Script | Backend | Default output |
|---|---|---|
| `score/score_centilebrain.R` | CentileBrain MFP | `ideas_zscores_centilebrain.csv` |
| `score/score_centilebrain_gamlss.R` | CentileBrain GAMLSS | `ideas_zscores_centilebrain_gamlss.csv` |
| `score/score_pcn_toolkit.py` | PCN Bayesian | `ideas_zscores_pcn.csv` |

| Flag | Meaning |
|---|---|
| `--input` | Cohort CSV (default `ideas_data/ideas_merged.csv`) |
| `--out-dir` | Output directory (default `score/`) |
| `--models` | CentileBrain models dir (R) |
| `--out-name` | Output filename (PCN) |

**Outputs:** `subject_id`, `cohort`, `sex`, `age`, `measure`, `region`, `observed`, `z` (+ backend fields).

**Adaptation checks:** `mu_hat_cross_validation.R`, `mu_hat_sample_size_sensitivity.R`, `mfpr_with_vs_without_stats.py`.
