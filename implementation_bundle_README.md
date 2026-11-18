# IDEAS × pre-trained normative brain-morphometry models — implementation

This bundle applies three pre-trained normative-modelling backends to
the IDEAS focal-epilepsy cohort and ships the resulting per-subject
Z-scores.

## Papers implemented

- **Cohort** — Taylor P, Wang Y, Simpson C, *et al.* *IDEAS — Imaging
  Database for Epilepsy and Surgery.* *Epilepsia* 2025;66(2):471–481.
  doi:10.1111/epi.18192

- **CentileBrain (MFP + GAMLSS)** — Ge R, Yu Y, Qi YX, *et al.*
  *Normative modelling of brain morphometry across the lifespan with
  CentileBrain: algorithm benchmarking and model optimisation.*
  *Lancet Digital Health* 2024;6(3):e211–e221.
  doi:10.1016/S2589-7500(23)00250-9

- **PCN Toolkit lifespan models** — Rutherford S, Fraza C, Dinga R,
  *et al.* *Charting brain growth and aging at high spatial
  precision.* *eLife* 2022;11:e72904. doi:10.7554/eLife.72904

- **Site-adaptation protocol** — Rutherford S, Kia SM, Wolfers T,
  *et al.* *The normative modeling framework for computational
  psychiatry.* *Nature Protocols* 2022;17:1711–1734.
  doi:10.1038/s41596-022-00696-5. See `mu_hat.md` for the
  application-specific methodology note.

## Bundle contents

```
implementation_bundle/
├── README.md                                  # this file
├── ideas_data/
│   └── ideas_merged.csv                       # working cohort table
│                                              # (542 × 154, from the
│                                              # Taylor 2025 Figshare release)
├── score/
│   ├── score_centilebrain.R                   # CentileBrain-MFP implementation
│   ├── score_centilebrain_gamlss.R            # CentileBrain-GAMLSS implementation
│   ├── score_pcn_toolkit.py                   # PCN Toolkit-Bayesian implementation
│   ├── ideas_zscores_centilebrain.csv         # MFP Z-scores (81,300 rows)
│   ├── ideas_zscores_centilebrain_gamlss.csv  # GAMLSS Z-scores (81,300 rows)
│   └── ideas_zscores_pcn.csv                  # PCN Z-scores (36,856 rows)
└── mu_hat.md                                  # site-adaptation methodology note
```

## Per-subject Z-score output schema

Each `ideas_zscores_*.csv` is long-form: one row per (subject × measure
× region). Common columns across all three files:

| Column | Meaning |
|---|---|
| `subject_id` | IDEAS anonymised ID |
| `cohort` | `patient` or `control` |
| `sex` | `M` / `F` |
| `age` | age at scan, imputed from IDEAS 5-year bin midpoints |
| `measure` | `thickness`, `area`, or `subcortical` |
| `region` | Desikan–Killiany cortical region or Aseg subcortical label |
| `observed` | raw morphometry value from FreeSurfer |
| `z` | site-adapted Z-score (the primary output) |

Backend-specific columns:

- **MFP** (`ideas_zscores_centilebrain.csv`): adds `predicted`,
  `mu_hat`, `rmse_m`. The mean-centered MFP prediction is un-centered
  by the empirical per-region `mu_hat` estimated on IDEAS controls;
  `rmse_m` is the model's residual SD from the CentileBrain training
  set.
- **GAMLSS** (`ideas_zscores_centilebrain_gamlss.csv`): adds full
  distribution parameters (`mu`, `sigma`, `nu`, `tau`), the `centile`
  (CDF of `observed` under the fitted distribution), `z_raw`
  (`qnorm(centile)` before site adaptation), and `z_shift` (the site-
  adaptation offset).
- **PCN Toolkit** (`ideas_zscores_pcn.csv`): adds `pcn_region` (the
  PCN naming — e.g. `L_bankssts` — to distinguish from IDEAS's
  `lh_bankssts_thickness`). Cortical thickness only.

## Reading the scripts

Each of the three scoring scripts is self-contained and its header
docstring lists inputs, outputs, and design decisions. The scripts
implement, in order:

1. **`score_centilebrain.R`** — Multivariate fractional polynomial
   regression (Royston & Sauerbrei) on age plus one linear global
   covariate (intracranial volume for subcortical, mean cortical
   thickness for thickness, mean cortical surface area for area).
   Sex-specific models. Predictions are on a mean-centered scale;
   we un-center per-region via the empirical `mu_hat` offset
   estimated from IDEAS controls (see `mu_hat.md`).

2. **`score_centilebrain_gamlss.R`** — Generalized Additive Models
   for Location, Scale and Shape (Rigby & Stasinopoulos) with
   penalised B-spline smoothing of the location, scale and shape
   parameters of an LMS-family distribution (BCCGo for thickness +
   subcortical, BCPEo for area). Z is computed as
   `qnorm(pBCCGo(observed, mu, sigma, nu))`. Site-adaptation offset
   applied for parity with the MFP output.

3. **`score_pcn_toolkit.py`** — Hierarchical Bayesian regression
   with warping (`blr` algorithm, cubic B-spline covariate expansion)
   from the pre-trained `lifespan_DK_46K_59sites` model bundle. Site
   adaptation is the PCN Toolkit's built-in mechanism: IDEAS controls
   (N=100) supply the adaptation data; IDEAS patients (N=442) are
   the test set. Cortical thickness only in the distributed
   Desikan–Killiany bundle.

## What's not in this bundle

- **Pre-trained model files.** The CentileBrain `.rds` files (~960
  MB) and the PCN Toolkit `lifespan_DK_46K_59sites` bundle (~1.5 GB)
  are not distributed here. Clone them from their public repositories
  to rerun the scoring:
  - CentileBrain: `git clone https://github.com/CentileBrain/centilebrain`
  - PCN Toolkit braincharts: `git clone https://github.com/predictive-clinical-neuroscience/braincharts`
    and extract the `lifespan_DK_46K_59sites.zip` under
    `models/lifespan_DK_ct/`.
  Each scoring script points at these paths via `ROOT` constants at
  the top; edit those to match your layout.

- **Downstream analyses** (calibration Task 5, convergence Task 6,
  classification Task 7, resection concordance Task 8, robustness
  tests, clinical extensions). Those live in a separate
  results-analysis bundle; this bundle is scoped to the scoring
  implementation and its outputs only.

- **The `normreport` tool.** The same three backends wrapped in a
  per-patient CLI + Singularity/Apptainer container are packaged
  separately.

## Contact

Philbert Ndagijimana, URMC — `philbert_ndagijimana@urmc.rochester.edu`
