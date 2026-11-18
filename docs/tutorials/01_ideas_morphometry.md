# Tutorial 1 — Score IDEAS

**Goal.** Morphometry Z-scores on public IDEAS. **Prereq:** {doc}`../installation`
(CentileBrain; PCN optional). First run ~30–60 min (clones + download).

```bash
cd /path/to/normative
cd ideas_data && python3 fetch_figshare.py && python3 load_ideas.py && cd ..

Rscript score/score_centilebrain.R              # → score/ideas_zscores_*.csv
Rscript score/score_centilebrain_gamlss.R       # optional
python3 score/score_pcn_toolkit.py              # optional; needs PCN models
```

Check `ideas_merged.csv` has `subject_id`, `cohort`, `sex`, `age`, `lh_*_thickness`.
IDEAS ages are **binned** → midpoints in `load_ideas.py` (disclose if publishing).
Controls in `scoring_summary.txt` should be near mean 0 / SD 1 after adaptation.

**Next:** Tutorial 2 (`--input` / `--out-dir`). Schema: {doc}`../inputs`.

| Problem | Fix |
|---|---|
| Figshare / HTTP 202 | `playwright install firefox` |
| Missing `.rds` | Clone `centilebrain` at repo root |
| No R `mfp` | `install.packages("mfp")` |
