# Methods overview

Full stats: {doc}`references`.

A **normative model** predicts brain measures given covariates (age, sex, …)
from a healthy reference. New subjects get deviations, usually

$$
Z = \frac{y - \hat{\mu}(x)}{\hat{\sigma}(x)}
$$

Large \|Z\| means atypical vs the reference — not a diagnosis.

| Backend | Idea | Scale |
|---|---|---|
| CentileBrain MFP | Fractional polynomials + RMSE scaling | ~37k (Ge 2024) |
| CentileBrain GAMLSS | LMS distributions → centile → Z | same |
| PCN Bayesian | Hierarchical regression + sites | ~46k / 59 sites |

Morphometry models are **applied**, not re-fit. Local `cohort=control` rows
drive **site adaptation** (Rutherford 2022): CentileBrain via per-region
`mu_hat`; PCN via built-in adaptation. Aim for ≥ ~30 controls/sex.

Well-adapted controls: Z mean ≈ 0, SD ≈ 1. Thresholds like \|Z\| > 1.96 / 2.3
are conventions. `normreport` flags cross-backend agreement.

**Connectomes:** fit on *your* control edges (`log1p`, consistency filter) →
patient Z (controls via CV) → extremes → connection / node / ipsi–contra
sublobe summaries → permutation group tests.

**IDEAS:** public ages are binned; we use midpoints — disclose that if you publish.
