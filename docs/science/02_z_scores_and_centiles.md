# Z-scores and centiles

## Z-score (Gaussian-style deviation)

When a model supplies a predicted mean \(\hat{\mu}(x)\) and scale
\(\hat{\sigma}(x)\):

\[
Z = \frac{y - \hat{\mu}(x)}{\hat{\sigma}(x)}
\]

| | |
|---|---|
| \(Z \approx 0\) | close to expectation for covariates \(x\) |
| large positive | larger / thicker / stronger than expected |
| large negative | smaller / thinner / weaker than expected |

Under a normal assumption, \|Z\| > 1.96 is roughly the outer 5% two-tailed;
\|Z\| > 2.3 is a stricter “extreme” convention used in some network papers.
These are **thresholds for unusualness**, not disease labels (Rutherford et
al., 2022).

## Centiles (distributional charts)

LMS / GAMLSS-style models estimate a full conditional distribution. The
observation is mapped to a **centile** (e.g. 3rd, 50th, 97th). Centiles can
be converted to an equivalent normal Z via a probit transform. This matters
when morphometry is skewed (Cole & Green LMS tradition; GAMLSS practice in
CentileBrain — Ge et al., 2024).

## What covariates usually enter \(x\)

Commonly **age** and **sex**; sometimes intracranial volume, site, or other
nuisance variables depending on the model family. Using the wrong age
definition (e.g. age at surgery instead of age at scan) misplaces the person
on the chart.

## Population vs individual inference

- A single Z map describes **one person vs a reference**.  
- Cohort science still needs proper group statistics on those scores
  (multiplicity, confounds) — see Rutherford et al., 2022, reporting
  guidance.

## Read next

{doc}`03_morphometry_models` — how major published morphometry engines build
\(\hat{\mu}\) and \(\hat{\sigma}\).

## Key literature

- Rutherford et al., *Nature Protocols* 2022 — definitions and pitfalls.  
- Cole TJ, Green PJ. Smoothing reference centile curves: the LMS method.
  *Stat Med* 1992 (classic centile framework).  
- Ge et al., *Lancet Digital Health* 2024 — centile/Z outputs at scale.
