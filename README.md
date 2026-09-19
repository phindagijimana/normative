# CentileBrain validation on the IDEAS epilepsy cohort

Applies both of the pre-trained CentileBrain algorithms — **MFPR** and
**GAMLSS** — to the IDEAS UK epilepsy cohort and tests four things:

1. Do the CentileBrain models transfer cleanly to a new UK single-site cohort? (calibration)
2. Do CentileBrain-derived Z-scores agree with IDEAS's own ComBat-harmonised Z-scores? (convergence)
3. Do Z-scores beat raw morphometry for epilepsy-vs-control classification? (clinical utility)
4. Do preop Z-scores localise the epileptogenic zone actually resected? (surgical concordance)

Both algorithms give consistent results across all four tasks, so the
findings do not depend on the algorithm choice.

**Paper scope (locked, Option A, aiming for NeuroImage):** 2 platforms
+ 3 algorithm classes + 2 training cohorts + open-source tool release
as a co-equal contribution. Scientific validation covers
CentileBrain-MFP (37k), CentileBrain-GAMLSS (37k), and the PCN Toolkit
Bayesian lifespan models (57k+), all on the IDEAS cohort; the tool
contribution is `normreport` — a CLI + container wrapping all three
backends, producing per-patient PDF reports with cross-backend
consensus/disagreement flagging.

The tool ships with IDEAS-controls-2025 as the default reference
cohort. **URMC-scanner-specific adaptation is a post-publication
v1.1 task**, done at URMC via retrospective control harvest — required
for local clinical deployment but explicitly not on the paper's
critical path.

See `paper_planning/PAPER_PLAN.md` for the full scope, journal-target
analysis, and reserved-but-not-in-scope options (BrainMoNoCle as a
third platform, CentileBrain training means as a supplementary
comparison — both have outreach emails drafted and held in reserve at
`tool_design/`). Tool design at `tool_design/ARCHITECTURE.md`.

**Source papers:**

- Ge R et al. *Normative modelling of brain morphometry across the lifespan with CentileBrain.* *Lancet Digital Health* 2024;6(3):e211–e221.
- Taylor P et al. *IDEAS — Imaging Database for Epilepsy and Surgery.* *Epilepsia* 2025;66(2):471–481.

**All four tasks complete for both algorithms.** See `RESULTS.md` for
headline numbers and interpretation.

## Repository layout

```
Normative/
├── README.md                    # this file
├── SETUP.md                     # external dependencies (R, Python, Playwright, CentileBrain repo)
├── RESULTS.md                   # 2-page findings summary
├── normative.md                 # summary of Ge et al. 2024 (source paper)
├── Normative modeling.pdf       # the paper itself
│
├── ideas_data/                  # IDEAS Figshare downloads + unified loader
│   ├── README.md                # per-file schema documentation
│   ├── fetch_figshare.py        # Playwright-driven Figshare downloader
│   ├── fetch_resection.py       # add resection percentages
│   ├── load_ideas.py            # merges 8 FreeSurfer stats + 2 metadata files
│   ├── ideas_merged.csv         # 542 subjects × 154 cols — the working table
│   ├── manifest.json            # Figshare file provenance record
│   ├── [17 downloaded .txt/.csv/.pdf]
│   └── _scratch/                # investigation/debug artifacts (not required)
│
├── centilebrain/                # bundled upstream CentileBrain repo (960 MB)
│   ├── models/                  # the pre-trained MFP .rds files we score against
│   ├── templates/               # canonical input column-name templates
│   └── ...                      # + GAMLSS alternates, brainAGE, demos (see SETUP.md)
│
└── score/                                     # analysis pipeline + outputs
    ├── score_centilebrain.R                    # applies MFP models to ideas_merged.csv
    ├── score_centilebrain_gamlss.R             # applies GAMLSS models
    ├── analyze_scores.py                       # Tasks 5 + 6 (MFP)
    ├── classify_epilepsy.py                    # Task 7 (MFP-only)
    ├── resection_concordance.py                # Task 8 (MFP-only)
    ├── compare_mfp_gamlss.py                   # Tasks 5–8 head-to-head, both algorithms
    ├── ideas_zscores_centilebrain.csv          # MFP long-form Z-scores (81,300 rows)
    ├── ideas_zscores_centilebrain_gamlss.csv   # GAMLSS long-form Z-scores (81,300 rows)
    ├── ideas_zscores_wide.csv                  # MFP wide table (1,626 rows subject × region_measure)
    ├── per_region_controls_summary.csv         # Task 5 per-region calibration (MFP)
    ├── task5_control_sd_mfp_vs_gamlss.csv      # Task 5 side-by-side
    ├── ideas_vs_centilebrain_corr.csv          # Task 6 per-region convergence (MFP)
    ├── head_to_head_mfp_vs_gamlss_correlation.csv  # MFP vs GAMLSS agreement per region
    ├── classification_aucs.csv                 # Task 7 MFP-only AUCs
    ├── task7_aucs_mfp_vs_gamlss.csv            # Task 7 both algorithms
    ├── resection_concordance.csv               # Task 8 per-subject (MFP)
    └── task8_resection_rho_mfp_vs_gamlss.csv   # Task 8 both algorithms
```

## Reproduction — 4 commands

Prerequisites listed in `SETUP.md`.

```bash
# 1. Download the IDEAS tabular data (~3.5 MB)
cd ideas_data && python3 fetch_figshare.py && python3 fetch_resection.py

# 2. Merge into a single subject-level table (writes ideas_merged.csv)
python3 load_ideas.py

# 3. Score with both CentileBrain algorithms (writes score/ideas_zscores_*.csv)
cd .. && Rscript score/score_centilebrain.R           # MFP
Rscript score/score_centilebrain_gamlss.R             # GAMLSS

# 4. Run the four validation analyses
python3 score/analyze_scores.py         # Tasks 5+6 (MFP)
python3 score/classify_epilepsy.py      # Task 7 (MFP)
python3 score/resection_concordance.py  # Task 8 (MFP)
python3 score/compare_mfp_gamlss.py     # Tasks 5–8 head-to-head, both algorithms
```

Total runtime end-to-end: ~20 min on a workstation (dominated by the
SVC 100×5-fold CV runs — two of them now, one per algorithm).

## Headline results (see `RESULTS.md` for detail)

| Task | Metric | MFP | GAMLSS | Read |
|---|---|---|---|---|
| 5 — calibration | Controls Z SD (median) | 1.02 / 1.09 / 1.02 | 1.00 / 1.06 / 1.04 | thickness / subcort / area — both algorithms transfer well |
| 6 — convergence | vs IDEAS-internal Z (median r) | 0.83 / 0.85 / 0.81 | **0.96 / 0.81 / 0.97** | GAMLSS matches IDEAS internals almost perfectly on cortical measures |
| 7 — classification | Epilepsy-vs-control AUC | **0.797** | **0.796** | Z-scores (either algorithm) give no advantage over raw morphometry (AUC 0.794) |
| 8 — resection | Preop \|Z\| vs resected fraction ρ | 0.079 | 0.074 | weak but real localisation, algorithm-independent, null baseline 0.006 |
| Head-to-head | MFP vs GAMLSS Z per region | median r 0.81–0.89 | — | strong agreement across algorithms |

## Non-obvious caveats (must appear in any writeup)

1. **IDEAS age is binned in 5-year windows** — we impute midpoints; open-ended
   bins (`Less than 20`, `Over 55`) use ±2.5 y offsets. Documented smoothing.
2. **Site-adaptation offset applied per PCN Toolkit protocol** — the
   pre-trained CentileBrain MFP models return predictions on a mean-
   centered scale and the training-set region means aren't distributed
   with the public model files. We therefore applied the standard site-
   adaptation procedure from the PCN Toolkit normative-modeling framework
   ([Rutherford et al., *Nature Protocols* 2022](https://link.springer.com/protocol/10.1007/978-1-0716-4260-3_14)),
   estimating a per-region offset from IDEAS's 100 healthy controls. The
   GAMLSS models don't need un-centering (they predict on the original
   scale) but we applied the analogous Z-score-scale offset for parity.
   This is the same adaptation procedure required by BrainMoNoCle and
   any comparable platform when applied to a new site. Control Z ≈ 0 is
   a property of the adaptation procedure, so the calibration test
   focuses on SD, not mean. Full methodology + citations in `mu_hat.md`.
3. **`meanarea` covariate is `(L+R)/2`**, not the sum — the sum tanked
   surface-area convergence from r=0.81 → 0.31. Verified empirically.
4. **FreeSurfer version used by IDEAS is not documented** on the Figshare
   release page. The Ge 2024 paper reports the FS-version effect on scores
   is small, so we proceed and note the mismatch as a small caveat.
5. **Single-site cohort** — ComBat-GAM harmonisation was skipped because it
   requires ≥ 2 sites; the CentileBrain paper endorses this choice.

## Provenance

- IDEAS release: [Figshare share tokens listed on the CNNP lab page](https://sites.google.com/view/cnnp-lab/ideas-data) and also mirrored on OpenNeuro as `ds005602`.
- CentileBrain: https://github.com/CentileBrain/centilebrain and https://centilebrain.org
- Source paper for the model: Ge R, Yu Y, Qi YX et al., *Lancet Digital Health* 2024;6(3):e211–e221. doi:10.1016/S2589-7500(23)00250-9

## Contact

Philbert Ndagijimana, URMC — `philbert_ndagijimana@urmc.rochester.edu`.
