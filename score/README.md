# `score/`

Cohort morphometry scorers and optional IDEAS analysis utilities.

**Docs:** [Tutorial 1](../docs/tutorials/01_ideas_morphometry.md) ·
[Tutorial 2](../docs/tutorials/02_own_cohort.md) ·
[CLI reference](../docs/usage/morphometry.md) ·
[Input schema](../docs/inputs.md)

## Scorers

```bash
Rscript score/score_centilebrain.R --help
Rscript score/score_centilebrain_gamlss.R --help
python3 score/score_pcn_toolkit.py --help
```

Defaults read `ideas_data/ideas_merged.csv` and write Z-score CSVs here.
Override with `--input` / `--out-dir` (and `--models` for CentileBrain).

## Other scripts

Adaptation checks: `mu_hat_*.R`, `mfpr_with_vs_without_stats.py`.  
Optional IDEAS validation utilities: `compare_*.py`, `classify_*.py`,
`resection_concordance.py`, `hemispheric_lateralization.py`,
`ilae_outcome_prediction.py`, … — not required to score a new cohort.
Checked-in `*.csv` files are precomputed IDEAS products; regenerate by
re-running the scripts.
