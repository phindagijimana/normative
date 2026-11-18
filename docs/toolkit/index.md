# This project (software toolkit)

This repository is **one implementation** that applies published morphometry
normative models and optional connectome normative analyses. It is separate
from the field primer under {doc}`../science/index`.

**Source:** <https://github.com/phindagijimana/normative>

## What the software provides

| Capability | Code | Learn by doing |
|---|---|---|
| Cohort morphometry Z-scores (CentileBrain MFP/GAMLSS, PCN) | `score/` | {doc}`../tutorials/01_ideas_morphometry`, {doc}`../tutorials/02_own_cohort` |
| Single-subject PDF + multi-backend Z | `normreport/` | {doc}`../tutorials/03_normreport` |
| Structural connectome normative contrasts | `connectome_normative/` | {doc}`../tutorials/04_connectome` |
| IDEAS download / merge (worked example) | `ideas_data/` | Tutorial 1 |

```{toctree}
:maxdepth: 1

mapping
```

## Quick links

- Install: {doc}`../installation`  
- Concept → folder / CLI map: {doc}`mapping`  
- Tutorials: {doc}`../tutorials/index`  
- CLI reference: {doc}`../usage/morphometry`, {doc}`../usage/normreport`,
  {doc}`../usage/connectome`  
- Input schemas: {doc}`../inputs`  
- Theory (field): {doc}`../science/index`  
- Citations: {doc}`../references`

## Design choice (important)

Morphometry backends are **wrapped**, not retrained. Connectome models are
**fit on your controls**. That mirrors the science split between public
mega-cohort charts and study-local network normative models
({doc}`../science/03_morphometry_models`, {doc}`../science/06_network_models`).
