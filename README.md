# Normative modelling tooling (IDEAS)

Code for applying pre-trained brain-morphometry normative models
(CentileBrain MFP / GAMLSS and PCN Toolkit) to the IDEAS epilepsy
cohort, plus the `normreport` CLI/container.

## Layout

```
Normative/
├── README.md                 # this file
├── SETUP.md                  # dependencies and external model clones
├── ideas_data/               # download + load IDEAS tabular inputs
├── score/                    # scoring scripts and analysis utilities
├── normreport/               # CLI + container for per-patient reports
└── connectome_normative/     # optional structural-connectome normative scripts
```

Operational docs only: `SETUP.md`, `ideas_data/README.md`,
`score/README.md`, `normreport/README.md`.

## Quick start

1. Install dependencies — see `SETUP.md`.
2. Clone CentileBrain models and (optionally) PCN Toolkit model bundles
   into the locations described in `SETUP.md`.
3. Build the IDEAS working table:

```bash
cd ideas_data
python3 fetch_figshare.py
python3 fetch_resection.py
python3 load_ideas.py
```

4. Score with each backend:

```bash
Rscript score/score_centilebrain.R
Rscript score/score_centilebrain_gamlss.R
python3 score/score_pcn_toolkit.py
```

5. Optional: install and run `normreport` — see `normreport/README.md`.

## Connectome scripts

`connectome_normative/` contains scripts that fit a normative model to
structural connectivity matrices. They do not use the CentileBrain or
PCN morphometry models. See script docstrings for inputs and usage.

## References

- Ge R et al. *Lancet Digital Health* 2024 — CentileBrain.
- Taylor P et al. *Epilepsia* 2025 — IDEAS.
- Rutherford et al. *Nature Protocols* 2022 — site adaptation.
