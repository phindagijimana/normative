# Structural connectome normative modelling

Fit a control normative model per edge (and a node-strength comparator),
score patients, and compare two patient groups at connection, node
(deviation degree), and ipsilateral/contralateral sublobe scales.

This path does **not** use CentileBrain or PCN morphometry models.

Schemas: [`../docs/INPUT_SCHEMA.md`](../docs/INPUT_SCHEMA.md).

## Dependencies

```bash
pip install pandas numpy scipy
```

## Smoke test

```bash
python3 connectome_normative/multiscale_normative.py --demo --out /tmp/connectome_demo
```

Writes summary tables under `/tmp/connectome_demo`.

## Run on your data

```bash
python3 connectome_normative/multiscale_normative.py \
  --matrices /path/to/matrices \
  --labels /path/to/labels.csv \
  --covariates /path/to/covariates.csv \
  --groups notSF1 durable \
  --out /path/to/results
```

Useful flags:

| Flag | Meaning |
|---|---|
| `--transform log1p` | Default edge transform |
| `--min-frac 0.75` | Keep edges non-zero in ≥ this fraction of controls |
| `--z-thr 2.3` | Extreme-deviation threshold |
| `--folds 5` | Control CV folds for in-sample control Z |
| `--n-perm 5000` | Permutations for group tests |
| `--vs-controls` | Also test each patient group vs controls |
| `--extra-covariates site …` | Extra columns from the covariates CSV |

Full help: `python3 connectome_normative/multiscale_normative.py --help`.

## IDEAS covariates helper

If you already downloaded IDEAS metadata under `ideas_data/`:

```bash
python3 connectome_normative/ideas_covariates.py --out covariates.csv
```

Builds `control` / `notSF1` / `durable` (optional `relapse`) rows with
age, sex, and `op_side`. You still need per-subject connectivity matrices
and a labels CSV aligned to matrix order.
