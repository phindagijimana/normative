# Tutorial 2 — Your own cohort

**Goal.** Same scorers, non-IDEAS table. **Schema:** {doc}`../inputs`.

CSV columns: `subject_id`, `cohort` (include `control`), `sex`, `age`, plus
DK/`eTIV`/aseg columns (see `ideas_data/load_ideas.py` or IDEAS merge as template).
Prefer ≥ ~30 controls/sex for adaptation.

```bash
Rscript score/score_centilebrain.R --input my_cohort.csv --out-dir out/
Rscript score/score_centilebrain_gamlss.R --input my_cohort.csv --out-dir out/
python3 score/score_pcn_toolkit.py --input my_cohort.csv --out-dir out/ --out-name z_pcn.csv
```

On controls, Z ≈ mean 0, SD 1. If not, check `cohort=control` and column names.
CLI details: {doc}`../usage/morphometry`. Single-subject PDF: Tutorial 3.
