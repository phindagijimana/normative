# Morphometry backends (CentileBrain & PCN)

This toolkit **does not retrain** large morphometry models. It **scores** new
subjects with published backends and then adapts to your site
({doc}`04_site_adaptation`).

## Three backends side by side

| Backend | Statistical idea | Training scale (approx.) | In this repo |
|---|---|---|---|
| **CentileBrain MFP** | Multivariate fractional polynomials for the mean; scale via RMSE | ~37k (Ge et al. 2024) | `score_centilebrain.R`, `normreport` |
| **CentileBrain GAMLSS** | Distributional LMS-family models → centile → Z | same CentileBrain reference | `score_centilebrain_gamlss.R`, `normreport` |
| **PCN Toolkit Bayesian** | Hierarchical Bayesian regression with site effects | ~46k / 59 sites (Rutherford *eLife* 2022) | `score_pcn_toolkit.py`, `normreport` |

### CentileBrain MFP (beginner intuition)

Think: flexible age curves (fractional polynomials), stratified by sex,
producing a predicted mean and an error scale used to form Z.

### CentileBrain GAMLSS (beginner intuition)

Think: model the **whole distribution** (location/scale/shape), read a
centile for the observed value, map that centile to a normal Z. Useful when
skewness matters.

### PCN Bayesian (beginner intuition)

Think: a hierarchical model that was trained across many sites, so site
variation is part of the model. New sites still need **adaptation** when they
were not in training (Rutherford et al. 2022).

## Why run more than one?

Algorithms disagree. Multi-backend **consensus** (as in `normreport`) is a
practical robustness check: regions extreme in all backends are stronger
leads than regions extreme in only one.

## What each backend needs from you

Shared idea (see {doc}`../inputs`):

- demographics: age, sex  
- morphometry columns in CentileBrain / FreeSurfer-style names  
- local **controls** for site adaptation  

PCN in this repo focuses on **cortical thickness** (lifespan DK bundle).
CentileBrain MFP/GAMLSS also cover area and selected subcortical volumes.

## Read next

{doc}`04_site_adaptation` — why your scanner still needs local controls.

## Literature

- Ge R, et al. Normative modelling of brain morphometry across the lifespan
  with CentileBrain. *Lancet Digital Health* 2024;6:e211–e221.  
- Rutherford S, et al. Charting brain growth and aging at high spatial
  precision. *eLife* 2022 (PCN / braincharts models).  
- Rutherford S, et al. *Nature Protocols* 2022 (how to apply / adapt).  
- Upstream: [CentileBrain](https://github.com/CentileBrain/centilebrain),
  [braincharts](https://github.com/predictive-clinical-neuroscience/braincharts).
