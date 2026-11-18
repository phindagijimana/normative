# Input schemas

Contracts for reusable entry points. Column names are case-sensitive.

## Morphometry cohort table (`--input` CSV)

Used by:

- `score/score_centilebrain.R`
- `score/score_centilebrain_gamlss.R`
- `score/score_pcn_toolkit.py`

### Required metadata

| Column | Type | Notes |
|---|---|---|
| `subject_id` | string or int | Unique per row |
| `cohort` | string | Must include `control` for site adaptation. Other labels (e.g. `patient`) are scored but do not estimate the offset |
| `sex` | `M` / `F` | Case-insensitive; other values dropped |
| `age` | float years | Continuous age preferred. IDEAS uses bin midpoints |

### Required morphometry columns

Desikan–Killiany naming as produced by FreeSurfer / IDEAS merge:

- Cortical thickness: `lh_<region>_thickness`, `rh_<region>_thickness` (34 regions × 2)
- Cortical area (MFP / GAMLSS): `lh_<region>_area`, `rh_<region>_area`
- Subcortical volumes (MFP / GAMLSS): CentileBrain aseg names, e.g. `Left-Thalamus`, `Right-Hippocampus`, …
- Intracranial volume for MFP subcortical models: `eTIV`

Region lists and exact aseg spellings live in `ideas_data/load_ideas.py`
(`DK_REGIONS`, `ASEG_REGIONS`).

### Site adaptation

Controls (`cohort == "control"`) estimate a per-region mean offset
(`mu_hat`) so patient Z-scores are centred for a new scanner / site
(Rutherford et al., *Nature Protocols* 2022). Use ≥ ~30 controls per sex
when possible; fewer increases offset variance.

### IDEAS helper

```bash
python3 ideas_data/load_ideas.py   # writes ideas_data/ideas_merged.csv
```

That file is a valid `--input` for the scorers.

---

## Single-subject FreeSurfer stats (`normreport`)

See `normreport/README.md` and `normreport/examples/demo_subject_stats.csv`.
Pass age/sex on the CLI; optional `--reference` control cohort CSV for
site-matched adaptation.

---

## Connectome normative modelling

### Matrices (`--matrices DIR`)

One square matrix per subject: `<subject>.csv`, `.txt`, or `.npy`.
Filename stem must match the `subject` column in covariates.

### Region labels (`--labels CSV`)

| Column | Notes |
|---|---|
| `name` | Region name (row/column order of each matrix) |
| `hemi` | `L`, `R`, or `M` |
| `base` | Homologue key shared by L/R copies of a region |
| `sublobe` | Hemisphere-free sublobe label for lateralised summaries |

Row order must match matrix order.

### Covariates (`--covariates CSV`)

| Column | Notes |
|---|---|
| `subject` | Matches matrix filename stem |
| `group` | `control` plus two patient labels passed to `--groups A B` |
| `age` | float |
| `sex` | used as a covariate |
| `op_side` | `L` / `R` for patients (ipsilateral / contralateral sublobes) |

Optional: `site` and any columns listed in `--extra-covariates`.

IDEAS outcome helper (after IDEAS metadata is downloaded):

```bash
python3 connectome_normative/ideas_covariates.py --out covariates.csv
```
