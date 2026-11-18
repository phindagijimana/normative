# Normative modelling toolkit

Reusable tools for applying published brain-morphometry normative models
(CentileBrain MFP / GAMLSS and PCN Toolkit) and for running a structural
connectome normative analysis. The IDEAS epilepsy cohort is the worked
example; the same entry points accept your own tables when they match the
documented schemas.

## Choose a path

| Goal | Start here |
|---|---|
| Score **one FreeSurfer subject** → PDF + Z-scores | [`normreport/`](normreport/README.md) |
| Score a **cohort table** (IDEAS or your own) | [`SETUP.md`](SETUP.md) → [`score/`](score/README.md) |
| Build / understand the **IDEAS** working table | [`ideas_data/`](ideas_data/README.md) |
| Structural **connectome** normative modelling | [`connectome_normative/`](connectome_normative/README.md) |
| Input column contracts | [`docs/INPUT_SCHEMA.md`](docs/INPUT_SCHEMA.md) |

## Quick start (IDEAS morphometry)

```bash
# 1. Dependencies + model clones — see SETUP.md
pip install -r requirements.txt
# R: install.packages(c("mfp", "gamlss", "gamlss.dist"))

# 2. IDEAS working table
cd ideas_data && python3 fetch_figshare.py && python3 fetch_resection.py && python3 load_ideas.py && cd ..

# 3. Score three backends
Rscript score/score_centilebrain.R
Rscript score/score_centilebrain_gamlss.R
python3 score/score_pcn_toolkit.py
```

## Quick start (your own morphometry cohort)

1. Build a CSV matching [`docs/INPUT_SCHEMA.md`](docs/INPUT_SCHEMA.md)
   (required: `subject_id`, `cohort`, `sex`, `age`, region columns; controls
   must use `cohort=control` for site adaptation).
2. Point the scorers at it:

```bash
Rscript score/score_centilebrain.R --input /path/to/cohort.csv --out-dir /path/to/out
Rscript score/score_centilebrain_gamlss.R --input /path/to/cohort.csv --out-dir /path/to/out
python3 score/score_pcn_toolkit.py --input /path/to/cohort.csv --out-dir /path/to/out
```

Or score one subject at a time with `normreport` and a site-matched
`--reference` control table.

## Quick start (connectome)

```bash
python3 connectome_normative/multiscale_normative.py --demo --out /tmp/connectome_demo
python3 connectome_normative/multiscale_normative.py --help
```

## Layout

```
├── README.md                 # this file
├── SETUP.md                  # OS, R/Python, CentileBrain + PCN clones
├── requirements.txt          # Python deps for score/ + connectome + ideas_data
├── docs/INPUT_SCHEMA.md      # cohort + connectome input contracts
├── ideas_data/               # download + merge IDEAS tabular inputs
├── score/                    # cohort scorers + optional IDEAS analyses
├── normreport/               # single-subject CLI + container
└── connectome_normative/     # edge/node/sublobe connectome normative scripts
```

## References

- Ge et al., *Lancet Digital Health* 2024 — CentileBrain
- Rutherford et al., *Nature Protocols* 2022 — site adaptation / PCN Toolkit
- Taylor et al., *Epilepsia* 2025 — IDEAS
