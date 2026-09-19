# `score/` — analysis pipeline and results

Everything downstream of `ideas_data/ideas_merged.csv`. Scripts read the
merged IDEAS table and the CentileBrain / PCN Toolkit model files, and
write per-subject Z-scores and per-task summary tables. Nothing here
depends on external network access at run-time (except the R packages
`mfp` and `gamlss`, installed once from CRAN, and the `pcntoolkit`
Python package, installed once from PyPI; see the parent `SETUP.md`).

The files below are grouped by role rather than filesystem location.

## 1. Scoring pipelines — one per normative backend

| File | Language | Backend | Reads | Writes |
|---|---|---|---|---|
| `score_centilebrain.R` | R | CentileBrain-MFP | `../ideas_data/ideas_merged.csv` + `../centilebrain/models/MFPmodels_*.rds` | `ideas_zscores_centilebrain.csv`, `ideas_zscores_wide.csv`, `scoring_summary.txt` |
| `score_centilebrain_gamlss.R` | R | CentileBrain-GAMLSS | Same + `../centilebrain/models/GAMLSSmodels_*.rds` | `ideas_zscores_centilebrain_gamlss.csv` |
| `score_pcn_toolkit.py` | Python | PCN Toolkit (Rutherford 2022) | Same + `../pcn_models/braincharts/models/lifespan_DK_ct/` | `ideas_zscores_pcn.csv` |

All three scripts apply the site-adaptation procedure documented in
`../mu_hat.md` (Rutherford et al., *Nature Protocols* 2022). MFP and
GAMLSS use an empirical per-region offset estimated from IDEAS's 100
healthy controls; PCN Toolkit uses its own built-in adaptation
mechanism with the same controls as the adaptation set.

## 2. Cross-backend comparisons

| File | Purpose | Reads | Writes |
|---|---|---|---|
| `compare_mfp_gamlss.py` | 2-way MFP vs GAMLSS across Tasks 5–8 | The two CentileBrain Z-score CSVs | `task5_control_sd_mfp_vs_gamlss.csv`, `head_to_head_mfp_vs_gamlss_correlation.csv`, `task7_aucs_mfp_vs_gamlss.csv`, `task8_resection_rho_mfp_vs_gamlss.csv` |
| `compare_all_three.py` | 3-way MFP vs GAMLSS vs PCN across Tasks 5, 6, 8 (cortical thickness, the common intersection) | All three backends' Z-score CSVs | `task5_three_backend_control_sd.csv`, `task6_three_backend_convergence.csv`, `task8_three_backend_resection.csv` |

## 3. `mu_hat` robustness suite (Tests 1 and 2 in `../mu_hat.md`)

| File | Test | Reads | Writes |
|---|---|---|---|
| `mu_hat_cross_validation.R` | Test 1: K-fold cross-validation of the adaptation procedure | Same as the scoring scripts | `mu_hat_cv_results.csv` |
| `mu_hat_sample_size_sensitivity.R` | Test 2: `mu_hat` variance at N ∈ {10, 20, 30, 50, 75, 100} | Same | `mu_hat_sample_size_variance.csv` |
| `MU_HAT_ROBUSTNESS.md` | Interpretation + implications for the paper and the tool | — | Read this to understand the two tests |

**Key finding:** held-out control Z has median absolute mean 0.002 and
median SD 1.02–1.13; `mu_hat` stabilises at N ≥ 30 (SD ~0.11 on the
Z-scale) and is near-deterministic by N = 50 (SD ~0.03).

## 4. Task-specific analyses

### Task 5 — Calibration (per-region SD of Z on controls)

| File | Output |
|---|---|
| `analyze_scores.py` | Aggregates Task 5 + Task 6 for MFP; writes `per_region_controls_summary.csv` |
| `task5_control_sd_mfp_vs_gamlss.csv` | Side-by-side per-region SD, MFP vs GAMLSS |
| `task5_three_backend_control_sd.csv` | Per-region SD, MFP + GAMLSS + PCN, cortical thickness only |

### Task 6 — Convergence with IDEAS-internal ComBat Z-scores

| File | Output |
|---|---|
| `ideas_vs_centilebrain_corr.csv` | Per-region Pearson r, MFP vs IDEAS-internal, all measures |
| `head_to_head_mfp_vs_gamlss_correlation.csv` | Per-region r, MFP vs GAMLSS (algorithm agreement) |
| `task6_three_backend_convergence.csv` | Summary table of median r per backend vs IDEAS-internal |

### Task 7 — Epilepsy vs control classification

| File | Purpose |
|---|---|
| `classify_epilepsy.py` | Linear-SVC benchmark, MFP Z vs raw morphometry |
| `classification_aucs.csv` | Per-repeat AUCs across 100 × 5-fold CV |
| `task7_aucs_mfp_vs_gamlss.csv` | Per-repeat AUCs, both algorithms |

### Task 8 — Resection concordance

| File | Purpose |
|---|---|
| `resection_concordance.py` | Per-subject Spearman ρ (\|Z\| vs resection %), MFP + GAMLSS |
| `resection_concordance.csv` | Per-subject ρ, MFP (430 rows) |
| `task8_resection_rho_mfp_vs_gamlss.csv` | Per-subject ρ, both algorithms |
| `task8_three_backend_resection.csv` | Summary table of mean ρ per backend |

### Clinical extensions (Tasks 5a and 6a in the manuscript)

| File | Purpose |
|---|---|
| `hemispheric_lateralization.py` | Does more-deviant hemisphere identify Op_Side? Per-algorithm + per-pathology accuracy |
| `lateralization_results.csv` | Accuracy, sensitivity per side, chi-square p, per pathology (14 rows) |
| `ilae_outcome_prediction.py` | Ridge logistic regression: preop Z-scores → ILAE-1 seizure-freedom AUC |
| `ilae_outcome_aucs.csv` | AUC + 95% CI + ΔAUC (Z − raw) + permutation p per algorithm |
| `CLINICAL_EXTENSIONS.md` | Interpretation + implications for the paper and the tool |

## 5. Per-subject Z-score outputs (the paper's Contribution #5)

| File | Rows | Contents |
|---|---:|---|
| `ideas_zscores_centilebrain.csv` | 81,300 | Long-form MFP Z-scores: subject × measure × region × observed × predicted × RMSE_m × z |
| `ideas_zscores_centilebrain_gamlss.csv` | 81,300 | Long-form GAMLSS Z-scores: subject × measure × region × observed × distribution params × centile × z_raw × z_shift × z |
| `ideas_zscores_pcn.csv` | 36,856 | Long-form PCN Toolkit Z-scores (cortical thickness only): subject × measure × region × observed × pcn_region × z |
| `ideas_zscores_wide.csv` | 1,626 | Wide MFP table: one row per (subject, measure), one column per region |

## Reproducing everything from scratch

From the repository root:

```bash
# Prerequisites — see ../SETUP.md
# 1. R packages: mfp, gamlss (from CRAN, one-time)
# 2. Python: pandas, numpy, scipy, scikit-learn, pcntoolkit (from PyPI)
# 3. CentileBrain repo cloned at ../centilebrain/
# 4. PCN Toolkit braincharts cloned at ../pcn_models/braincharts/
#    with lifespan_DK_46K_59sites.zip extracted into
#    ../pcn_models/braincharts/models/lifespan_DK_ct/

# Score all three backends (~15 min total)
Rscript score_centilebrain.R
Rscript score_centilebrain_gamlss.R
python3 score_pcn_toolkit.py

# Run comparisons + task analyses (~10 min total; dominated by SVC × 100 repeats)
python3 analyze_scores.py
python3 classify_epilepsy.py
python3 resection_concordance.py
python3 compare_mfp_gamlss.py
python3 compare_all_three.py

# mu_hat robustness (~5 min)
Rscript mu_hat_cross_validation.R
Rscript mu_hat_sample_size_sensitivity.R

# Clinical extensions (~5 min)
python3 hemispheric_lateralization.py
python3 ilae_outcome_prediction.py
```

Total end-to-end runtime: ~30 min on a workstation. The pipeline is
deterministic given fixed random seeds (already set in every script
that uses randomness).
