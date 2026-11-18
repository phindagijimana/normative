# Normative modelling toolkit

Apply published **brain-morphometry** normative models and optional
**structural-connectome** normative analyses. The
[IDEAS](https://doi.org/10.1111/epi.18192) epilepsy cohort is the worked
example; the same entry points accept your own data when schemas match.

```{image} https://img.shields.io/badge/source-phindagijimana%2Fnormative-blue
:alt: Source repository
:target: https://github.com/phindagijimana/normative
```

## What this software does

1. **Cohort morphometry scoring** — CentileBrain MFP / GAMLSS and PCN Toolkit
   Bayesian models → regional Z-scores with site adaptation.
2. **Single-subject reports** — `normreport` CLI / container → PDF + Z-score
   table from one FreeSurfer subject.
3. **Connectome normative modelling** — control-fit edge models, patient
   deviations, group contrasts at connection / node / sublobe scales.

## Choose a path

| Goal | Page |
|---|---|
| Install dependencies and model files | {doc}`installation` |
| Run IDEAS or your own cohort end-to-end | {doc}`usage/quickstart` |
| Cohort scorers (CLI + outputs) | {doc}`usage/morphometry` |
| One subject → PDF | {doc}`usage/normreport` |
| Connectome pipeline | {doc}`usage/connectome` |
| Input column contracts | {doc}`inputs` |
| Short methods / science overview | {doc}`methods` |
| Citations | {doc}`references` |

```{toctree}
:maxdepth: 2
:caption: Documentation

installation
usage/quickstart
usage/morphometry
usage/normreport
usage/connectome
inputs
methods
references
building
```

## Note

This toolkit **wraps** published models (CentileBrain, PCN Toolkit). It does
not retrain those morphometry models. Connectome scripts fit normative models
on **your** control connectomes. For research use.
