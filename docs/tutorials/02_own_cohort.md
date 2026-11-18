# Tutorial 2 — Reuse scorers on your own cohort

**Goal.** Apply the same morphometry scorers to a non-IDEAS table.

**Prereqs.** Tutorial 1 or at least working CentileBrain models
({doc}`../installation`). Schema: {doc}`../inputs`.

## 1. Build a cohort CSV

One row per subject. Minimum metadata:

| Column | Example |
|---|---|
| `subject_id` | `sub-01` |
| `cohort` | `control` or `patient` |
| `sex` | `M` / `F` |
| `age` | `34.0` (years, continuous) |

Plus FreeSurfer-style region columns, e.g. `lh_bankssts_thickness`, …
and for MFP subcortical models `eTIV` + aseg names.

**Critical:** include enough healthy rows with `cohort=control` so site
adaptation can estimate the offset (≥ ~30 per sex when possible).

You can start from `ideas_data/ideas_merged.csv` as a column template, or
from region lists in `ideas_data/load_ideas.py`.

## 2. Score with explicit paths

```bash
Rscript score/score_centilebrain.R \
  --input /path/to/my_cohort.csv \
  --models /path/to/normative/centilebrain/models \
  --out-dir /path/to/out

Rscript score/score_centilebrain_gamlss.R \
  --input /path/to/my_cohort.csv \
  --out-dir /path/to/out

python3 score/score_pcn_toolkit.py \
  --input /path/to/my_cohort.csv \
  --out-dir /path/to/out \
  --out-name my_zscores_pcn.csv
```

## 3. Check adaptation

On controls in the output CSV, Z should be roughly mean ≈ 0, SD ≈ 1.
If control means are far from zero, check that `cohort` is exactly
`control` and that age/sex/region columns match the expected names.

Optional helpers (same repo):

```bash
Rscript score/mu_hat_cross_validation.R
Rscript score/mu_hat_sample_size_sensitivity.R
```

## 4. Next steps

- Single subject PDF instead of a full cohort → Tutorial 3  
- Reference CLI details → {doc}`../usage/morphometry`  
- Why site adaptation → {doc}`../methods`
