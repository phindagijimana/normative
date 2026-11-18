# Cohort morphometry scoring

Scripts in `score/` apply pre-trained models to a per-subject table and write
long-form Z-scores. Schema: {doc}`../inputs`.

## Scorers

| Script | Backend | Default output |
|---|---|---|
| `score/score_centilebrain.R` | CentileBrain MFP | `ideas_zscores_centilebrain.csv` |
| `score/score_centilebrain_gamlss.R` | CentileBrain GAMLSS | `ideas_zscores_centilebrain_gamlss.csv` |
| `score/score_pcn_toolkit.py` | PCN Toolkit Bayesian | `ideas_zscores_pcn.csv` |

Site adaptation uses rows with `cohort=control` (Rutherford et al. 2022).

## CLI

```bash
Rscript score/score_centilebrain.R --help
Rscript score/score_centilebrain_gamlss.R --help
python3 score/score_pcn_toolkit.py --help
```

Common flags:

| Flag | Meaning |
|---|---|
| `--input PATH` | Cohort CSV (default: `ideas_data/ideas_merged.csv`) |
| `--out-dir DIR` | Output directory (default: `score/`) |
| `--models DIR` | CentileBrain models dir (R scorers) |
| `--out-name NAME` | Output filename (PCN only) |

## Output columns

Common idea across backends:

`subject_id`, `cohort`, `sex`, `age`, `measure`, `region`, `observed`, `z`

plus backend-specific prediction / distribution fields.

## Optional IDEAS utilities

After scoring IDEAS, scripts such as `compare_all_three.py`,
`classify_epilepsy.py`, and `resection_concordance.py` reproduce the
validation suite. They are **not** required to score a new cohort. See
`score/README.md` in the repository for the full list.

## Site-adaptation checks

| Script | Purpose |
|---|---|
| `mu_hat_cross_validation.R` | K-fold CV of the control offset |
| `mu_hat_sample_size_sensitivity.R` | Offset variance vs control N |
| `mfpr_with_vs_without_stats.py` | MFP with vs without control offset |
