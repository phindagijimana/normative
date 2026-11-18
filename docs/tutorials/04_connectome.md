# Tutorial 4 — Connectome normative modelling

**Goal.** Run the synthetic demo, then point the same CLI at your matrices.

**Prereqs.** `pip install pandas numpy scipy` (or `pip install -r requirements.txt`).
No CentileBrain / PCN models required.

## 1. Smoke test

```bash
cd /path/to/normative
python3 connectome_normative/multiscale_normative.py \
  --demo --out /tmp/connectome_demo
```

Open `/tmp/connectome_demo` for summary tables (edge / node / sublobe
contrasts on synthetic groups).

## 2. Prepare your inputs

See {doc}`../inputs` — briefly:

- **Matrices:** one `N×N` file per subject (`<subject>.csv|.txt|.npy`)
- **Labels CSV:** `name`, `hemi`, `base`, `sublobe` (row order = matrix order)
- **Covariates CSV:** `subject`, `group`, `age`, `sex`, `op_side`  
  (`group` must include `control` plus two patient labels)

## 3. Run a real comparison

```bash
python3 connectome_normative/multiscale_normative.py \
  --matrices /path/to/matrices \
  --labels /path/to/labels.csv \
  --covariates /path/to/covariates.csv \
  --groups groupA groupB \
  --out /path/to/results \
  --z-thr 2.3 \
  --n-perm 5000
```

Optional: `--vs-controls`, `--extra-covariates site`, `--transform log1p`.

## 4. IDEAS outcome covariates (optional)

If you already downloaded IDEAS metadata:

```bash
python3 connectome_normative/ideas_covariates.py --out covariates.csv
```

You still need connectivity matrices and labels; IDEAS OpenNeuro public
release does not ship DWI connectomes.

## 5. What to read next

- CLI reference: {doc}`../usage/connectome`  
- Multiscale idea (edges → nodes → sublobes): {doc}`../methods`
