# `score/` — cohort scoring and optional analyses

Apply pre-trained CentileBrain and PCN Toolkit models to a per-subject
morphometry table, then (optionally) run IDEAS validation utilities.

For column contracts see [`../docs/INPUT_SCHEMA.md`](../docs/INPUT_SCHEMA.md).
For installs and model clones see [`../SETUP.md`](../SETUP.md).

## 1. Scorers (reuse these)

| Script | Backend | Default input | Default outputs |
|---|---|---|---|
| `score_centilebrain.R` | CentileBrain MFP | `ideas_data/ideas_merged.csv` | `ideas_zscores_centilebrain.csv`, `ideas_zscores_wide.csv`, `scoring_summary.txt` |
| `score_centilebrain_gamlss.R` | CentileBrain GAMLSS | same | `ideas_zscores_centilebrain_gamlss.csv` |
| `score_pcn_toolkit.py` | PCN Toolkit Bayesian | same | `ideas_zscores_pcn.csv` |

All three apply **site adaptation** using rows with `cohort=control`
(Rutherford et al., *Nature Protocols* 2022): MFP/GAMLSS via a per-region
empirical offset; PCN via its built-in adaptation API.

### CLI

```bash
# Defaults (IDEAS layout after load_ideas.py)
Rscript score/score_centilebrain.R
Rscript score/score_centilebrain_gamlss.R
python3 score/score_pcn_toolkit.py

# Your own table
Rscript score/score_centilebrain.R \
  --input /path/to/cohort.csv \
  --models /path/to/centilebrain/models \
  --out-dir /path/to/out

Rscript score/score_centilebrain_gamlss.R \
  --input /path/to/cohort.csv \
  --models /path/to/centilebrain/models \
  --out-dir /path/to/out

python3 score/score_pcn_toolkit.py \
  --input /path/to/cohort.csv \
  --out-dir /path/to/out \
  --out-name my_zscores_pcn.csv
```

Long-form Z-score columns (common idea across backends):
`subject_id`, `cohort`, `sex`, `age`, `measure`, `region`, `observed`, `z`
(plus backend-specific prediction / distribution columns).

## 2. Site-adaptation checks

| Script | What it does |
|---|---|
| `mu_hat_cross_validation.R` | K-fold CV of the control offset on held-out controls |
| `mu_hat_sample_size_sensitivity.R` | Offset variance vs control N ∈ {10,…,100} |
| `mfpr_with_vs_without_stats.py` | MFP Z with vs without the control offset |

## 3. Optional IDEAS analysis utilities

These expect the default IDEAS Z-score CSVs in `score/` and the merged
IDEAS metadata. Useful to reproduce the IDEAS validation suite; not
required to score a new cohort.

| Area | Scripts |
|---|---|
| Summaries / calibration | `analyze_scores.py`, `compare_mfp_gamlss.py`, `compare_all_three.py`, `compare_three_summary.py`, `compare_three_extra.py`, `pairwise_z_pearson.py` |
| Classification | `classify_epilepsy.py`, `classify_all_three.py` |
| Resection / laterality / outcome | `resection_concordance.py`, `hemispheric_lateralization.py`, `ilae_outcome_prediction.py`, `bootstrap_lateralization_resection.py` |
| Other | `subgroup_analyses.py`, `power_calculation_negatives.py`, `mu_hat_age_bin_sensitivity.py` |

### Reproduce the IDEAS suite (after scoring)

```bash
cd score
python3 analyze_scores.py
python3 classify_epilepsy.py
python3 resection_concordance.py
python3 compare_mfp_gamlss.py
python3 compare_all_three.py
python3 pairwise_z_pearson.py
python3 classify_all_three.py
python3 compare_three_summary.py
python3 compare_three_extra.py
Rscript mu_hat_cross_validation.R
Rscript mu_hat_sample_size_sensitivity.R
python3 hemispheric_lateralization.py
python3 ilae_outcome_prediction.py
```

Runtime is on the order of ~30 minutes on a workstation. Scripts that
use randomness set fixed seeds.

## 4. Checked-in CSV products

Many `*.csv` files in this folder are precomputed IDEAS outputs so you can
inspect results without re-running. Re-run the scripts above to refresh
them. Prefer regenerating rather than editing by hand.
