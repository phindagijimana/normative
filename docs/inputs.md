# Input schemas

Column names are case-sensitive.

## Morphometry cohort table (`--input` CSV)

Used by `score/score_centilebrain.R`, `score/score_centilebrain_gamlss.R`,
and `score/score_pcn_toolkit.py`.

### Required metadata

| Column | Type | Notes |
|---|---|---|
| `subject_id` | string or int | Unique per row |
| `cohort` | string | Must include `control` for site adaptation. Other labels (e.g. `patient`) are scored but do not estimate the offset |
| `sex` | `M` / `F` | Case-insensitive; other values dropped |
| `age` | float years | Continuous age preferred. IDEAS uses bin midpoints |

### Required morphometry columns

Desikan–Killiany naming as in FreeSurfer / the IDEAS merge:

- Thickness: `lh_<region>_thickness`, `rh_<region>_thickness` (34 × 2)
- Area (MFP / GAMLSS): `lh_<region>_area`, `rh_<region>_area`
- Subcortical volumes (MFP / GAMLSS): CentileBrain aseg names
  (e.g. `Left-Thalamus`, `Right-Hippocampus`)
- ICV for MFP subcortical models: `eTIV`

Exact region lists: `ideas_data/load_ideas.py` (`DK_REGIONS`, `ASEG_REGIONS`).

### IDEAS helper

```bash
python3 ideas_data/load_ideas.py   # writes ideas_data/ideas_merged.csv
```

## Single-subject FreeSurfer stats (`normreport`)

See `normreport/examples/demo_subject_stats.csv`. Pass `--age` / `--sex` on
the CLI; optional `--reference` control table for site-matched adaptation.

## Connectome inputs

### Matrices (`--matrices DIR`)

One square matrix per subject: `<subject>.csv`, `.txt`, or `.npy`.
Filename stem must match `subject` in covariates.

### Region labels (`--labels CSV`)

| Column | Notes |
|---|---|
| `name` | Region name (matrix row/column order) |
| `hemi` | `L`, `R`, or `M` |
| `base` | Homologue key shared by L/R copies |
| `sublobe` | Hemisphere-free sublobe label |

### Covariates (`--covariates CSV`)

| Column | Notes |
|---|---|
| `subject` | Matrix filename stem |
| `group` | `control` plus two patient labels for `--groups A B` |
| `age` | float |
| `sex` | covariate |
| `op_side` | `L` / `R` for patients (ipsi / contra summaries) |

Optional: `site` and any `--extra-covariates` columns.
