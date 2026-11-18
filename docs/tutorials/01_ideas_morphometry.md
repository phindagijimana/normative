# Tutorial 1 — Score the IDEAS cohort

**Goal.** End-to-end morphometry Z-scores on the public IDEAS tables using
CentileBrain (and optionally PCN).

**Time.** ~30–60 min the first time (mostly model clones + download).

**Prereqs.** {doc}`../installation` completed (Python, R `mfp`/`gamlss`,
CentileBrain clone). PCN is optional for this tutorial.

## 1. Get the working table

```bash
cd /path/to/normative
pip install -r requirements.txt
playwright install firefox

cd ideas_data
python3 fetch_figshare.py
python3 load_ideas.py          # writes ideas_merged.csv
cd ..
```

Check: `ideas_data/ideas_merged.csv` exists and has columns `subject_id`,
`cohort`, `sex`, `age`, plus `lh_*_thickness` regions.

IDEAS ages are **binned** in the public release; `load_ideas.py` maps bins
to midpoints. State that approximation if you publish results.

## 2. Score CentileBrain MFP

```bash
Rscript score/score_centilebrain.R
```

Writes under `score/`:

- `ideas_zscores_centilebrain.csv` — long-form Z
- `ideas_zscores_wide.csv`
- `scoring_summary.txt` — mean/SD of Z by cohort (controls should be near 0/1 after adaptation)

## 3. Score GAMLSS (optional second backend)

```bash
Rscript score/score_centilebrain_gamlss.R
```

## 4. Score PCN Toolkit (optional)

Needs the braincharts models from {doc}`../installation`.

```bash
python3 score/score_pcn_toolkit.py
```

## 5. What “reuse” looks like next

You just ran the default IDEAS paths. Tutorial 2 shows the same commands
with `--input` / `--out-dir` on **your** CSV. Schema: {doc}`../inputs`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Figshare download fails / HTTP 202 | Install Playwright Firefox; check network to figshare.com |
| Missing `.rds` models | Clone `centilebrain` at repo root |
| R can’t find `mfp` | `install.packages("mfp")`; scripts also look in `~/R/library` |
