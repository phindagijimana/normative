# Input schemas

Column names are case-sensitive.

## Morphometry cohort (`--input`)

| Column | Notes |
|---|---|
| `subject_id` | Unique |
| `cohort` | Must include `control` for adaptation |
| `sex` | `M` / `F` |
| `age` | Years (continuous; IDEAS uses bin midpoints) |

Regions: `lh|rh_<dk>_thickness` / `_area`; aseg names + `eTIV` for MFP
subcortical. Lists: `ideas_data/load_ideas.py`.  
Helper: `python3 ideas_data/load_ideas.py` → `ideas_merged.csv`.

**normreport:** CSV like `normreport/examples/demo_subject_stats.csv`;
`--age` / `--sex`; optional `--reference` controls.

## Connectome

| Input | Contents |
|---|---|
| `--matrices` | `<subject>.csv\|.txt\|.npy` (stem = `subject`) |
| `--labels` | `name`, `hemi` (`L`/`R`/`M`), `base`, `sublobe` |
| `--covariates` | `subject`, `group`, `age`, `sex`, `op_side` (+ optional extras) |
