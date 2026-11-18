# Connectome CLI reference

How-to: {doc}`../tutorials/04_connectome`. Schema: {doc}`../inputs`.
No CentileBrain / PCN models.

| Flag | Meaning |
|---|---|
| `--matrices` | Dir of `<subject>.csv\|.txt\|.npy` |
| `--labels` | Region table (`name`, `hemi`, `base`, `sublobe`) |
| `--covariates` | `subject`, `group`, `age`, `sex`, `op_side` |
| `--groups A B` | Two patient group labels |
| `--out` | Results directory |
| `--transform` | `log1p` (default) or `none` |
| `--min-frac` | Edge consistency filter on controls |
| `--z-thr` | Extreme threshold (default 2.3) |
| `--folds` | Control CV folds |
| `--n-perm` | Permutations |
| `--vs-controls` | Also test each group vs controls |
| `--extra-covariates` | Extra covariate columns |
| `--demo` | Synthetic end-to-end run |

Helper: `python3 connectome_normative/ideas_covariates.py --out covariates.csv`.
