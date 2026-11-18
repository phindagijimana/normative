# Methods overview

Short science context for users of this toolkit. For full statistical
detail, use the citations on {doc}`references`.

## What is normative modelling?

A **normative model** predicts the expected value (and often variance) of a
brain measure given covariates such as age and sex, using a large healthy
reference. A new subject is scored as a **deviation** from that expectation,
commonly a Z-score:

$$
Z = \frac{y - \hat{\mu}(x)}{\hat{\sigma}(x)}
$$

Large \|Z\| marks atypical morphometry or connectivity relative to the
reference, not a clinical diagnosis by itself.

## Morphometry backends in this repo

| Backend | Idea | Reference scale |
|---|---|---|
| **CentileBrain MFP** | Multivariate fractional polynomials for the mean; RMSE-based scaling | ~37k lifespan training set (Ge et al. 2024) |
| **CentileBrain GAMLSS** | Distributional (LMS-family) models → centiles → Z via probit | Same CentileBrain reference |
| **PCN Toolkit Bayesian** | Hierarchical Bayesian regression with site effects | lifespan_DK ~46k / 59 sites (Rutherford et al.) |

All three are **applied**, not re-fit, for morphometry. Your local controls
are used only for **site adaptation** (below).

## Site adaptation

A new scanner / FreeSurfer stack shifts the mean of Z on healthy people away
from zero. Following Rutherford et al. (*Nature Protocols* 2022):

- **CentileBrain path:** estimate a per-region offset `mu_hat` from local
  controls (`cohort=control`), then centre patient scores.
- **PCN path:** use the toolkit’s built-in adaptation with the same controls
  as the adaptation set.

Practical rule of thumb: ≥ ~30 controls per sex when possible. Fewer controls
→ noisier offset (see `score/mu_hat_sample_size_sensitivity.R`).

## Interpreting morphometry Z-scores

- On well-adapted controls, Z should be roughly mean ≈ 0, SD ≈ 1.
- Extreme thresholds (e.g. \|Z\| > 1.96 or 2.3) are conventions for “unusual,”
  not disease labels.
- Cross-backend **agreement** (MFP vs GAMLSS vs PCN) is a robustness check:
  `normreport` flags consensus / disagreement per region.

## Connectome normative modelling

Here the normative model is fit **on your controls’ edges** (and a
node-strength comparator):

1. Transform edges (default `log1p`); keep edges consistently present in
   controls.
2. Regress each edge on covariates; score out-of-sample Z for patients
   (controls via K-fold CV).
3. Mark extreme deviations (\|Z\| > threshold).
4. Summarise at **connections**, **nodes** (deviation degree), and
   **lateralised sublobes** (ipsi / contra to `op_side`).
5. Compare two patient groups with permutation tests.

Design inspired by multiscale FC deviation work (e.g. Ilioska-style
connection / region / network summaries); this implementation targets
structural connectomes and surgical laterality.

## IDEAS as the worked example

[IDEAS](https://doi.org/10.1111/epi.18192) supplies public FreeSurfer stats
and metadata for patients and controls. Age in the public tables is
**binned**; scorers use bin midpoints as continuous age — an approximation
you should state if you publish IDEAS-based results.
