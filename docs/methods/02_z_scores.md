# Z-scores: the basic language

## Definition

A normative model predicts the expected value \(\hat{\mu}(x)\) of a brain
measure \(y\) given covariates \(x\) (commonly age and sex). Many models also
estimate a scale \(\hat{\sigma}(x)\). The usual deviation score is:

$$
Z = \frac{y - \hat{\mu}(x)}{\hat{\sigma}(x)}
$$

| Symbol | Meaning |
|---|---|
| \(y\) | Observed measure (e.g. thickness in one DK region) |
| \(x\) | Covariates used by the model |
| \(\hat{\mu}(x)\) | Predicted typical value |
| \(\hat{\sigma}(x)\) | Predicted typical spread |
| \(Z\) | How many SDs above/below expectation |

Some backends (e.g. GAMLSS) go through a **centile** first, then convert to a
Z via a normal probit — same *idea*, different distributional machinery
({doc}`03_backends`).

## What a large \|Z\| means

- **Does mean:** this region (or edge) is atypical **relative to the model’s
  healthy reference**, after accounting for the covariates the model uses.
- **Does not mean:** a disease label, surgical target, or proof of causation.

Thresholds such as \|Z\| > 1.96 (~5% two-tailed under a normal) or 2.3 are
**conventions** for “extreme,” not magic cut-offs (Rutherford et al. 2022).

## Polarity

- Positive Z: larger / thicker / stronger than expected.  
- Negative Z: smaller / thinner / weaker than expected.  

Which direction is “bad” depends on the biology and the question — do not
assume “negative = pathology.”

## One subject, many Z-scores

FreeSurfer Desikan–Killiany morphometry yields dozens of regional Z-scores
per measure (thickness, area, subcortical volume). Connectomes yield one Z
per retained edge (thousands), then summaries at nodes and sublobes
({doc}`06_connectome`).

## Ideal behaviour on healthy controls

After good **site adaptation** ({doc}`04_site_adaptation`):

- control Z mean ≈ 0  
- control Z SD ≈ 1  

If controls are badly shifted or inflated, patient Z-scores are not
trustworthy yet.

## Read next

{doc}`03_backends` — how CentileBrain and PCN build \(\hat{\mu}\) and
\(\hat{\sigma}\).

## Literature

- Rutherford et al., *Nature Protocols* 2022 — definitions, workflows, pitfalls.  
- Ge et al., *Lancet Digital Health* 2024 — CentileBrain Z-style outputs.  
- Cole TJ. The LMS method… *Stat Med* / related LMS literature — centile→Z idea
  behind GAMLSS-type charts.
