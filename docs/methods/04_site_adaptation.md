# Site adaptation (why local controls matter)

## The beginner trap

You download a model trained on tens of thousands of brains, score your
cohort, and patient maps look dramatic — but **your healthy controls** also
have mean Z far from 0. That usually means **site / pipeline shift**, not
disease.

FreeSurfer version, field strength, head coil, and preprocessing all move
morphometry. A model that never saw your scanner will be mis-centred.

## What “site adaptation” means

Following Rutherford et al. (*Nature Protocols* 2022), use **local healthy
controls** scanned and processed like your patients to estimate and remove
the site offset before interpreting patients.

In this toolkit:

| Backend | Adaptation mechanism |
|---|---|
| CentileBrain MFP / GAMLSS | Empirical per-region offset `mu_hat` from rows with `cohort=control` |
| PCN Toolkit | Built-in adaptation API; same controls as the adaptation set |

Controls must be labelled exactly `cohort=control` in cohort tables
({doc}`../inputs`).

## Practical rules of thumb

- Prefer **≥ ~30 controls per sex** when possible.  
- Fewer controls → noisier offset (see `score/mu_hat_sample_size_sensitivity.R`).  
- Controls must match patient **acquisition + FreeSurfer** pipeline.  
- After adaptation, check control Z ≈ mean 0, SD 1 ({doc}`05_interpretation`).

## What adaptation is not

- Not ComBat across clinical sites (different tool, different goal).  
- Not retraining CentileBrain / PCN from scratch.  
- Not a license to ignore bad QC or wrong column schemas.

## Read next

{doc}`05_interpretation` — reading Z maps without overclaiming.

## Literature

- Rutherford S, et al. The normative modeling framework for computational
  psychiatry. *Nature Protocols* 2022 — **primary protocol** for adaptation.  
- Bayer JMM, et al. / related transfer literature — site effects in
  normative models (see protocol references).  
- Ge et al. 2024 — CentileBrain application context.
