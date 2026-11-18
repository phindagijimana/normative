# Connectome normative modelling

Fit a control normative model per edge (and a node-strength comparator), score
patients, and compare two patient groups at connection, node (deviation
degree), and ipsilateral / contralateral sublobe scales.

Does **not** use CentileBrain or PCN morphometry models.

## Smoke test

```bash
python3 connectome_normative/multiscale_normative.py --demo --out /tmp/connectome_demo
```

## Run on your data

```bash
python3 connectome_normative/multiscale_normative.py \
  --matrices /path/to/matrices \
  --labels /path/to/labels.csv \
  --covariates /path/to/covariates.csv \
  --groups notSF1 durable \
  --out /path/to/results
```

Inputs: {doc}`../inputs`.

## Useful flags

| Flag | Meaning |
|---|---|
| `--transform log1p` | Default edge transform |
| `--min-frac` | Keep edges non-zero in ≥ this fraction of controls |
| `--z-thr` | Extreme-deviation threshold (default 2.3) |
| `--folds` | Control CV folds |
| `--n-perm` | Permutations for group tests |
| `--vs-controls` | Also test each group vs controls |
| `--extra-covariates` | Extra columns from the covariates CSV |

```bash
python3 connectome_normative/multiscale_normative.py --help
```

## IDEAS covariates helper

After IDEAS metadata is downloaded:

```bash
python3 connectome_normative/ideas_covariates.py --out covariates.csv
```

You still supply connectivity matrices and region labels aligned to matrix
order.
