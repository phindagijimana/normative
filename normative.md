# Summary: Normative modelling of brain morphometry across the lifespan with CentileBrain

**Citation:** Ge R, Yu Y, Qi YX, et al. *Lancet Digital Health.* 2024;6(3):e211–e221. doi:10.1016/S2589-7500(23)00250-9

**Corresponding author:** Sophia Frangou (University of British Columbia) — ENIGMA Lifespan Working Group

**Resource:** [https://centilebrain.org/](https://centilebrain.org/)

---

## 1. Motivation

Normative modelling quantifies how much an individual's brain measure deviates from a healthy reference population (analogous to paediatric growth charts). Existing studies use a mix of linear, non-linear, and Bayesian algorithms chosen by researcher preference, on relatively modest samples (145–870 people). There has been **no systematic benchmarking** of algorithms or of the parameters that drive model performance — including a lack of empirical guidance on minimum required sample size.

**Aim:** Empirically identify the optimal algorithm and covariate combination for normative modelling of regional brain morphometry.

---

## 2. Data

- **37,407 healthy individuals** (19,964 F / 17,443 M), aged **3–90 years**, from **87 datasets across 20 countries** (Europe, Australia, USA, South Africa, East Asia).
- Structural T1-weighted MRI processed with **FreeSurfer**.
- **150 regional measures**: 68 Desikan-Killiany cortical-thickness regions, 68 cortical surface-area regions, 14 Aseg subcortical volumes.
- Additional longitudinal test sets: **SLIM** (n=118, ~2.35-yr interval) and **QTAB** (n=259, ~1.76-yr interval).
- Clinical test set: **HCP-EP** (91 early-psychosis patients + 57 controls).

---

## 3. Methods

### Design
- 80/20 stratified train/test split per sex, stratified by site and age.
- Sex-specific models built separately for each of the 150 regions.
- Five-fold cross-validation. Performance metrics: **MAE** (primary), **RMSE**, explained variance, and CPU time.

### Eight algorithms compared
| Algorithm | Type |
|---|---|
| OLSR | Ordinary least squares (linear) |
| BLR | Bayesian linear regression |
| GAMLSS | Generalised additive models for location, scale, shape |
| LMS | λ-μ-σ (Box-Cox-Cole-Green, GAMLSS subclass) |
| GPR | Gaussian process regression (non-parametric Bayesian) |
| WBLR | Warped Bayesian linear regression (PCNtoolkit) |
| HBR | Hierarchical Bayesian regression (PCNtoolkit) |
| **MFPR** | **Multivariate fractional polynomial regression** |

### Covariate optimisation
Candidate explanatory variables tested: scanner vendor, FreeSurfer version, Euler's number (scan quality), and **global neuroimaging measures** (intracranial volume, mean cortical thickness, total surface area), with linear and non-linear terms and their combinations.

### Site-effect handling
Compared modelling site as a random factor vs. harmonising with **ComBat-GAM**.

### Deviation score
For a pre-trained model, the individual Z-score is `Z = (y − ŷ) / RMSE_m`.

---

## 4. Key Results

### Best algorithm
- **MFPR emerged as optimal**, offering top-tier accuracy (MAE/RMSE) matched only by LMS/GPR/WBLR, while being one of the fastest (< 1 s CPU vs. 25–60 min for GPR).
- Optimised MFPR outperformed WBLR and GPR on the joint accuracy + efficiency criterion.
- GAMLSS, BLR, OLSR, and HBR performed statistically worse.

### Best covariates
- **Age (as non-linear fractional polynomials) + one global measure (linear)** is sufficient:
  - Intracranial volume → for subcortical volume models
  - Mean cortical thickness → for regional cortical-thickness models
  - Total cortical surface area → for regional surface-area models
- Scanner vendor, FreeSurfer version, and Euler's number contributed minimally.

### Sample size
- Model performance **plateaus at ~3,000 participants** per sex — a practical benchmark for future normative studies.

### Robustness
- Accuracy is stable across nine age bins (r > 0.98 vs. full-sample MAE/RMSE).
- Longitudinally stable across ~2-year re-scans (SLIM, QTAB).
- MFPR was best regardless of whether site was treated as a random effect or via ComBat-GAM harmonisation; ComBat-GAM avoids per-site recalibration when applying pre-trained models.

### Clinical utility (HCP-EP psychosis)
- SVCs trained on **Z-scores** distinguished psychosis patients from controls **above chance (AUC 0.63, p < 0.001)**, while an SVC on raw observed morphometry was **at chance (AUC 0.49)**.
- No model (Z-scored or raw) predicted PANSS symptom severity above chance.

---

## 5. Key Contributions

1. **First large-scale empirical benchmark** of eight normative-modelling algorithms on brain morphometry.
2. **Recommended pipeline:** sex-specific MFPR with non-linear age + linear global measure.
3. **Empirical sample-size floor:** ~3,000 participants per sex-specific model.
4. **Sex-specific models** for cortical thickness, cortical surface area, **and** subcortical volume — the surface-area normative models are new relative to prior lifespan efforts.
5. **Open resource:** models and scripts released via the **CentileBrain** web platform for community use.

---

## 6. Limitations

- Cross-sectional composition means older participants are likely survivorship-biased.
- Under-representation of young and middle-aged adults; limited long-term longitudinal data.
- Generalisability to specific ancestries not yet validated.
- Explanatory variables like childhood adversity, prematurity, or socioeconomic status were not incorporated — including them could improve fit but would restrict applicability to datasets that record them consistently.

---

## 7. Take-aways for Applied Work

- Use **MFPR** with age (fractional polynomial) and a **linear global brain measure** as covariates.
- Build **sex-specific** models; sex is a major variance source in brain morphology.
- Aim for **≥ 3,000 subjects per sex** in the reference sample.
- Prefer **ComBat-GAM** for site harmonisation when the pipeline must generalise to unseen sites.
- **Z-scores > raw morphometry** for downstream disease-classification tasks in psychiatry.
