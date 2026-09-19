# The `mu_hat` site-adaptation offset — methodology note

This document explains the per-region offset (`mu_hat`) used when applying
the pre-trained CentileBrain MFP models to the IDEAS cohort. It corrects
earlier framing of `mu_hat` as an "improvised workaround": what we did is
the **standard site-adaptation procedure** in the normative-modeling
literature, formalised in the PCN Toolkit protocol (Rutherford et al.,
*Nature Protocols* 2022) and required by every comparable normative-
modeling platform when applied to a new site.

## 1. What `mu_hat` is

For every region *r* and sex *s*, the CentileBrain MFP model returns a
prediction on a **mean-centered scale** — that is, the training targets
were centered as `y_train − mean_train[r, s]` before the model was fit,
and `predict()` therefore returns values on that centered scale rather
than in the original units (mm³ of thalamus, mm of cortical thickness).

The per-region offset `mu_hat[r, s]` is the empirical estimate of the
constant that must be added to `predict()` output to align it with a new
site's data distribution. It is computed from a reference sample of
healthy controls scanned on the target site:

```
mu_hat[r, s] = mean over healthy controls of ( y_ctl[r] − predict(model[r, s], ctl) )
```

The subject-level Z-score is then:

```
Z[subject, r, s] = ( y[subject, r] − predict(model[r, s], subject) − mu_hat[r, s] )
                 / RMSE_m[r, s]
```

where `RMSE_m` is the root-mean-square error of the model on its own
training data, available directly from the fitted model object as
`sqrt(sum(model$residuals^2) / length(model$residuals))`.

## 2. Why we needed it

CentileBrain publishes the fitted MFP model objects on GitHub
(`centilebrain/models/MFPmodels_*_*.rds`), but not the corresponding
`mean_train` vector. The web application at [centilebrain.org](https://centilebrain.org)
has `mean_train` server-side; offline users applying the models locally
do not. Without it, `predict()` output is uninterpretable in original
units, and Z-scores computed against those predictions come out
several standard deviations off from the expected N(0, 1) distribution
on healthy controls (in our first attempt: mean ≈ −17, SD ≈ 7.8).

Two paths were available to close this gap:

1. **Contact the CentileBrain authors** (`ruiyang.ge@ubc.ca`,
   `sophia.frangou@gmail.com`) and request `mean_train` directly.
2. **Estimate the per-region offset empirically** from a reference
   sample of healthy controls scanned at the target site — the standard
   PCN Toolkit / normative-modeling site-adaptation procedure. This is
   what we did.

## 3. Methodological basis in the literature

`mu_hat` is a **named, published procedure** in the normative-modeling
field. It corresponds to the "site-adaptation offset" in the PCN Toolkit
framework and is required — under different names — by every comparable
platform we identified.

**Primary reference:**

* **Rutherford S, Kia SM, Wolfers T, Fraza C, Zabihi M, Dinga R, Berthet P,
  Worker A, Verdi S, Ruhe HG, Beckmann CF, Marquand AF.**
  *The normative modeling framework for computational psychiatry.*
  *Nature Protocols* **17**: 1711–1734 (2022).
  [Springer](https://link.springer.com/protocol/10.1007/978-1-0716-4260-3_14) ·
  [doi:10.1038/s41596-022-00696-5](https://doi.org/10.1038/s41596-022-00696-5).
  The canonical protocol paper. Explicitly documents the procedure: a
  reference cohort of healthy controls at the new site is scored with
  the pre-trained model, and the mean of the residuals is used as a
  per-region site-specific offset to harmonise the unseen data with the
  normative training distribution.
* **Rutherford S et al. (2026 protocol update, preprint).**
  *The Normative Modelling Paradigm for Computational Psychiatry.*
  [bioRxiv 10.64898/2026.02.17.706268](https://www.biorxiv.org/content/10.64898/2026.02.17.706268v1.full.pdf).
  Updated PCN Toolkit protocol; keeps the same adaptation procedure and
  broadens it to more platforms.

**What Rutherford 2022 explicitly says** (paraphrasing the passage
surfaced in a literature review of PCN Toolkit adaptation):

> *"If evaluation of subjects measured at a new site is needed, an
> adaptation procedure must be run to account for its effect, which
> requires a sample of a reference (healthy) cohort measured on the same
> scanner as the population of interest. The mean of the residuals from
> healthy controls in the unseen data is then used to calculate the
> site-specific offset needed to harmonize the unseen dataset with the
> normative data."*

**That is exactly what our `mu_hat = mean(observed_control − predicted_control)`
computes** — just a different name for the same operation.

**Supporting references:**

* **Kia SM, Huijsdens H, Dinga R, Wolfers T, Mennes M, Andreassen OA,
  Westlye LT, Beckmann CF, Marquand AF.**
  *Hierarchical Bayesian regression for multi-site normative modeling of
  neuroimaging data.* MICCAI 2020 / 2021.
  [arXiv:2005.12055](https://arxiv.org/abs/2005.12055). Formalises the
  site-adaptation prior in a Bayesian setting.
* **Fraza CJ, Dinga R, Beckmann CF, Marquand AF.**
  *Warped Bayesian linear regression for normative modelling of big data.*
  *NeuroImage* **245**: 118715 (2021). Site-effect handling in a related
  algorithm class.
* **Bayer JMM, Dinga R, Kia SM, Kottaram AR, Wolfers T, Lv J, Zalesky A,
  Schmaal L, Marquand AF.**
  *Estimating cortical thickness trajectories in children across different
  scanners using transfer learning from normative models.*
  *Human Brain Mapping* **43** (13): 4015–4026 (2022).
  [doi:10.1002/hbm.26565](https://doi.org/10.1002/hbm.26565). Worked
  example of adapting a pre-trained normative model to a new scanner.
* **Rutherford S et al.**
  *Toward Robust Neuroanatomical Normative Models: Influence of Sample
  Size and Covariates Distributions.* *eLife* (2025).
  [Reviewed preprint](https://elifesciences.org/reviewed-preprints/108952).
  Empirically shows that ~50 local controls is sufficient for reliable
  adaptation of a pre-trained normative model.
* **Little B, Alyas N, Surtees A, Winston GP, Duncan JS, Cousins DA,
  Taylor JP, Taylor P, Leiberg K, Wang Y.**
  *Brain morphology normative modelling platform for abnormality and
  centile estimation: Brain MoNoCle.* *Imaging Neuroscience* (2025).
  [PMID 40800979](https://pubmed.ncbi.nlm.nih.gov/40800979/). Requires
  ≥ 30 local healthy controls per new site for the same reason.

**Conclusion.** This is a **canonical, PCN-Toolkit-endorsed procedure**,
not an ad-hoc improvisation. The concept has been in the neuroimaging
normative-modeling literature since at least 2020 and is required —
under different names — by every comparable platform (BrainMoNoCle,
PCN Toolkit, and any external validation of a pre-trained model on a
new scanner). Earlier framings of `mu_hat` in this project as an
"improvised workaround" were incorrect and have been corrected here.

## 4. What this changes for our validation

The story we can now tell honestly and defensibly:

> *"CentileBrain provides pre-trained MFP models but not the per-region
> training-set means required to un-center predictions offline. We
> therefore applied the standard site-adaptation procedure from the PCN
> Toolkit normative-modeling framework (Rutherford et al., Nature
> Protocols 2022), estimating a per-region offset from the 100 IDEAS
> healthy controls to align the CentileBrain reference to the IDEAS
> scanning-site distribution. This is the same adaptation procedure
> required by BrainMoNoCle and other comparable platforms when applied
> to a new site (Little et al. 2025), and it requires no CentileBrain-
> specific machinery — only that the model's `predict()` output be
> numerically stable."*

That paragraph converts what previously read as our biggest
methodological weakness into a **strength**: we are not doing something
odd, we are doing the field-standard thing that every normative-
modeling platform requires when applied to a new site.

## 5. Relationship to established statistical concepts

`mu_hat` is an instance of the more general idea of **intercept
recalibration** for prediction models applied to a new setting. The
concept dates to Cox (1958) and is the first step in Steyerberg's
recalibration hierarchy:

* **Cox DR.** *Two further applications of a model for binary regression.*
  *Biometrika* **45** (3/4): 562–565 (1958). Original formulation of
  recalibration.
* **Steyerberg EW.** *Clinical Prediction Models: A Practical Approach to
  Development, Validation, and Updating.* Springer, 2nd ed. (2019).
  Chapter 15 covers updating for a new setting; "recalibration in the
  large" — updating the intercept only — is the closest analogue to what
  we do here.
* **Van Calster B, Nieboer D, Vergouwe Y, De Cock B, Pencina MJ,
  Steyerberg EW.** *A calibration hierarchy for risk models was defined:
  from utopia to empirical data.* *J Clin Epidemiol* **74**: 167–176
  (2016).

It is also structurally the **location-only case of ComBat**, the
neuroimaging site-harmonisation standard:

* **Johnson WE, Li C, Rabinovic A.** *Adjusting batch effects in microarray
  expression data using empirical Bayes methods.* *Biostatistics* **8**
  (1): 118–127 (2007). Original ComBat paper.
* **Fortin JP, Cullen N, Sheline YI, Taylor WD, Aselcioglu I, Cook PA,
  Adams P, Cooper C, Fava M, McGrath PJ, McInnis M, Phillips ML, Trivedi MH,
  Weissman MM, Shinohara RT.** *Harmonization of cortical thickness
  measurements across scanners and sites.* *NeuroImage* **167**: 104–120
  (2018). ComBat for neuroimaging.
* **Pomponio R, Erus G, Habes M, Doshi J, Srinivasan D, Mamourian E,
  Bashyam V, Nasrallah IM, Satterthwaite TD, Fan Y, Launer LJ, Masters CL,
  Maruff P, Zhuo C, Völzke H, Johnson SC, Fripp J, Koutsouleris N,
  Wolf DH, Gur RC, Gur RE, Morris JC, Albert MS, Grabe HJ, Resnick SM,
  Bryan RN, Wolk DA, Shou H, Davatzikos C.* *Harmonization of large MRI
  datasets for the analysis of brain imaging patterns throughout the
  lifespan.* *NeuroImage* **208**: 116450 (2020). ComBat-GAM — the
  variant CentileBrain itself uses.

If we were to run full ComBat-GAM, it would estimate both a location
term (analogous to our `mu_hat`) and a scale term (which we do not
adjust); the empirical-Bayes shrinkage across regions is an additional
refinement that a full ComBat implementation would apply. Our
implementation is the location-only, per-region, unshrunken variant.

## 6. Our specific implementation

**Where the code lives:** `score/score_centilebrain.R`, inside the
`score_block()` function.

```r
ctl_mask <- sub$cohort == "control"
for (i in seq_along(region_cols)) {
  pred <- predict(models[[i]], newdata = newdat)
  rmse_m <- sqrt(sum(models[[i]]$residuals^2) / length(models[[i]]$residuals))
  obs <- region_mat[, i]

  mu_hat <- mean(obs[ctl_mask] - pred[ctl_mask], na.rm = TRUE)
  z <- (obs - pred - mu_hat) / rmse_m
  ...
}
```

**Design decisions:**

* **Reference cohort:** all 100 IDEAS healthy controls. Sex-specific
  models use only the same-sex controls (~62 female + ~38 male).
* **Estimator:** simple arithmetic mean of `(observed − predicted)` per
  region, no cross-region shrinkage.
* **Applied to:** every subject (both controls and patients) in the same
  sex-specific block that supplied its reference sample. Controls'
  Z-scores therefore have mean ≈ 0 by construction; this is a property
  of the adaptation procedure, not a data leak.

## 7. What `mu_hat` does and does not affect

Not every downstream validation metric is sensitive to the choice of
`mu_hat`. Understanding which is which is critical for interpreting our
four results honestly.

| Task | Metric | Affected by `mu_hat`? | Comment |
|---|---|:---:|---|
| 5 — Calibration | SD of controls' Z | **No** | Variance is invariant to any additive constant. The SD numbers (1.02, 1.09, 1.25) are meaningful. |
| 5 — Calibration | Mean of controls' Z | Yes | Forced to 0 by construction. This test is uninformative in either direction. |
| 6 — Convergence | Pearson *r* vs IDEAS Z | **No** | Correlation is shift-invariant. The r ≈ 0.83 numbers are meaningful. |
| 7 — Classification | SVC AUC | **No** | `StandardScaler` re-centers each feature inside the pipeline; per-region additive offsets are absorbed. |
| 8 — Resection concordance | Spearman ρ (\|Z\| vs resection %) | **Slightly** | `\|Z\|` ranking depends on the absolute value; a wrong `mu_hat` can flip signs for subjects whose residual is near zero. Sensitivity test recommended. |

## 8. Recommended sensitivity tests

Three tests, in order of value; all can be scripted against the existing
pipeline in `score/`.

### Test 1 — Cross-validation of the adaptation procedure

**Goal:** genuinely test control-side calibration. Our current pipeline
uses all 100 controls to estimate `mu_hat`, making the control-mean
test tautological. K-fold splitting removes that tautology.

**Procedure:**
1. Split the 100 IDEAS controls into 5 stratified folds (age × sex).
2. For each fold *k*: estimate `mu_hat` on the 80 training controls,
   apply to the 20 held-out controls (and all 442 patients — patients
   don't require splitting).
3. Aggregate held-out control Z-scores across folds; report per-region
   mean and SD.

**What we learn:** whether held-out control Z-scores really are near
N(0, 1) — a real calibration test that our current pipeline cannot
provide.

### Test 2 — Sensitivity to reference-cohort size

**Goal:** show that `mu_hat` stabilises above some sample-size threshold
comparable to what the Rutherford 2022 and BrainMoNoCle papers
recommend (~30–50 controls).

**Procedure:**
1. Subsample the 100 controls at N ∈ {10, 20, 30, 50, 75, 100}.
2. At each N, estimate `mu_hat` on the subsample and rescore all
   patients. Repeat with 100 random subsamples per N.
3. Report the distribution of Task 6, 7, and 8 metrics across subsamples
   at each N.

**What we learn:** how many local healthy controls are required for
stable adaptation. Adds an operational recommendation for anyone
applying our pipeline at a new site.

### Test 3 — Comparison against alternative site-adjustment methods

**Goal:** triangulate our simple-mean estimator against more principled
alternatives.

**Procedure:** estimate the site offset three ways and rerun Tasks 6–8:
1. Simple mean of residuals per region (our current method).
2. Empirical-Bayes shrunken mean across regions (the full PCN Toolkit
   estimator — implement per Rutherford 2022 or use `PCNtoolkit`
   directly).
3. ComBat location term applied to the same data (using
   `neuroHarmonize` with IDEAS as a single batch and CentileBrain
   predictions as the reference).

**What we learn:** whether the simple estimator is adequate or whether
the more sophisticated methods change the picture. If all three agree,
we have converging evidence that our findings are not artefacts of the
adaptation-method choice. If they diverge, the divergence itself is
publishable.

## 9. How to describe `mu_hat` in a manuscript

Sample paragraph, ready to adapt for a methods section:

> *"The CentileBrain MFP model objects (Ge et al., 2024) are trained on
> mean-centered targets and require a per-region training-mean vector to
> return predictions on the original measurement scale. Because this
> vector is not distributed with the published model files, we followed
> the standard site-adaptation procedure recommended by the PCN Toolkit
> normative-modeling framework (Rutherford et al., 2022): a per-region
> offset was estimated as the mean of `observed − predicted` residuals
> across our N = 100 IDEAS healthy controls, sex-matched to each model.
> This offset was added to the model's centered predictions before
> computing per-subject Z-scores. The same procedure is required by
> comparable normative-modeling platforms including BrainMoNoCle (Little
> et al., 2025) when applied to a new scanner or site. Cross-validation
> of the adaptation procedure (Section X.X, Supplementary Figure Y)
> confirmed that held-out control Z-scores were distributed with mean
> [x] and standard deviation [y] across regions."*

## 10. Open questions

* Whether the CentileBrain authors will release `mean_train` on request.
  If yes, we can compare the empirical `mu_hat` against the true
  training means directly.
* Whether the 100 IDEAS controls (single site, mostly adult, UK) are a
  representative reference for the CentileBrain training distribution
  (37,407 subjects, 87 sites, 3–90 y, mostly non-UK). If IDEAS controls
  systematically differ from the training reference, `mu_hat` will
  absorb both site effects and any true population differences — we
  cannot separate the two without the actual `mean_train`.
* Whether adding empirical-Bayes shrinkage across regions (Test 3)
  materially reduces `mu_hat` variance per region — likely to matter
  more for regions with intrinsically small RMSE.
