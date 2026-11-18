# Morphometry model families in the literature

Large public engines differ in **how** they model $y \mid x$, but share the
charting goal. Below is field-level vocabulary; software names are examples
from papers, not install instructions.

## Multivariate fractional polynomials (MFP)

Flexible polynomial-like age trends (often sex-stratified) for the mean,
with a scale used to form Z. **CentileBrain** publishes MFP models trained on
a large multi-site lifespan morphometry corpus (Ge et al., 2024).

**Intuition:** smooth, interpretable age curves without claiming a full
probability density for every region.

## GAMLSS / LMS-style distributional models

Model location, scale, and shape so centiles are well-defined under skewness.
CentileBrain also releases **GAMLSS** alternatives on the same reference
philosophy (Ge et al., 2024).

**Intuition:** “growth chart” distributions, not only a mean ± RMSE.

## Hierarchical Bayesian / PCN-style models

Hierarchical models shrink site and individual effects, enabling large
multi-site training. The **PCN Toolkit** lifespan Desikan–Killiany models
(Rutherford et al., *eLife* 2022) are a widely used instance; the *Nature
Protocols* paper explains how to apply them to new data.

**Intuition:** borrow strength across sites; still treat truly new scanners
carefully ({doc}`04_site_effects`).

## Related lifespan programmes

**Brain charts** (Bethlehem et al., *Nature* 2022) popularised lifespan
centile thinking for global and regional phenotypes. They are scientifically
related even when a given software stack does not wrap them.

## Why papers compare multiple algorithms

Model class changes Z magnitude and spatial pattern. Concordance across
MFP vs GAMLSS vs Bayesian charts is evidence of **robustness**, not proof of
ground truth (discussed in protocol and CentileBrain papers).

## Read next

{doc}`04_site_effects` — transferring charts to a new scanner or pipeline.

## Key literature

- Ge R, et al. *Lancet Digital Health* 2024 — CentileBrain MFP & GAMLSS.  
- Rutherford S, et al. *eLife* 2022 — hierarchical lifespan models.  
- Rutherford S, et al. *Nature Protocols* 2022 — applying such models.  
- Bethlehem RAI, et al. *Nature* 2022 — brain charts for the human lifespan.
