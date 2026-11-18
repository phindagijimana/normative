# Normative modelling toolkit

Reusable tools for applying published brain-morphometry normative models
(CentileBrain MFP / GAMLSS and PCN Toolkit) and for structural-connectome
normative analysis. IDEAS is the worked example; the same entry points accept
your own data when schemas match.

**Documentation (Read the Docs style):** see [`docs/`](docs/index.md) — build
locally with Sphinx, or enable the project on
[Read the Docs](https://readthedocs.org/) (config: [`.readthedocs.yaml`](.readthedocs.yaml)).

[![Documentation](https://img.shields.io/badge/docs-Sphinx%20%2F%20RTD-blue)](docs/index.md)
[![Source](https://img.shields.io/badge/source-GitHub-black)](https://github.com/phindagijimana/normative)

## Choose a path

| Goal | Start here |
|---|---|
| Full docs (install, usage, methods) | [`docs/index.md`](docs/index.md) |
| Score **one FreeSurfer subject** → PDF | [`normreport/`](normreport/README.md) |
| Score a **cohort table** | [`docs/usage/morphometry.md`](docs/usage/morphometry.md) |
| Structural **connectome** modelling | [`docs/usage/connectome.md`](docs/usage/connectome.md) |
| Input column contracts | [`docs/inputs.md`](docs/inputs.md) |
| Short methods / science | [`docs/methods.md`](docs/methods.md) |

## Quick start (IDEAS morphometry)

```bash
pip install -r requirements.txt
# R: install.packages(c("mfp", "gamlss", "gamlss.dist"))
# clone CentileBrain (+ optional PCN) — see docs/installation.md

cd ideas_data && python3 fetch_figshare.py && python3 load_ideas.py && cd ..
Rscript score/score_centilebrain.R
Rscript score/score_centilebrain_gamlss.R
python3 score/score_pcn_toolkit.py
```

## Quick start (your own cohort)

```bash
Rscript score/score_centilebrain.R --input cohort.csv --out-dir out/
python3 score/score_pcn_toolkit.py --input cohort.csv --out-dir out/
```

Schema: [`docs/inputs.md`](docs/inputs.md).

## Build the docs site locally

```bash
pip install -r docs/requirements.txt
sphinx-build -b html docs docs/_build/html
# open docs/_build/html/index.html
```

## Layout

```
├── docs/                     # Sphinx / Read the Docs site
├── SETUP.md                  # short install mirror (see docs/installation.md)
├── ideas_data/               # IDEAS download + merge
├── score/                    # cohort scorers + optional analyses
├── normreport/               # single-subject CLI + container
└── connectome_normative/     # connectome normative scripts
```

## References

- Ge et al., *Lancet Digital Health* 2024 — CentileBrain
- Rutherford et al., *Nature Protocols* 2022 — site adaptation / PCN Toolkit
- Taylor et al., *Epilepsia* 2025 — IDEAS
