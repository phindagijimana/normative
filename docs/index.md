# Normative modelling toolkit

Apply published **brain-morphometry** normative models and optional
**structural-connectome** normative analyses. The
[IDEAS](https://doi.org/10.1111/epi.18192) epilepsy cohort is the worked
example; the same entry points accept your own data when schemas match.

```{image} https://img.shields.io/badge/source-phindagijimana%2Fnormative-blue
:alt: Source repository
:target: https://github.com/phindagijimana/normative
```

## New here?

1. {doc}`installation` — Python, R, CentileBrain / PCN model clones  
2. {doc}`tutorials/index` — four short reuse tutorials  
3. {doc}`methods` — what the science is doing (one page)

## What this software does

| Capability | Entry point |
|---|---|
| Cohort morphometry Z-scores (CentileBrain MFP / GAMLSS, PCN) | `score/` |
| One FreeSurfer subject → PDF + Z-scores | `normreport/` |
| Connectome edge / node / sublobe normative contrasts | `connectome_normative/` |

## Documentation map

```{toctree}
:maxdepth: 2
:caption: Start

installation
tutorials/index
methods
```

```{toctree}
:maxdepth: 2
:caption: Reference

usage/morphometry
usage/normreport
usage/connectome
inputs
references
building
```

## Note

This toolkit **wraps** published morphometry models; it does not retrain them.
Connectome scripts fit normative models on **your** controls. Research use only.
