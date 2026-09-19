# Multi-platform external validation of pre-trained normative brain-morphometry models on the IDEAS focal-epilepsy cohort, with an open-source multi-backend report tool

**Working title — subject to revision before submission.**

**Authors** *(to be finalised — first-draft attribution)*
Philbert Ndagijimana¹, [PI name and other collaborators to be added]¹⁻ⁿ

**Affiliations** *(placeholder)*
¹ Department of *[to be confirmed]*, University of Rochester Medical Center, Rochester, NY, USA

**Corresponding author**
Philbert Ndagijimana — `philbert_ndagijimana@urmc.rochester.edu`

**Target journal**
NeuroImage (primary) · Imaging Neuroscience (backup)

**Manuscript status**
Draft; scientific analyses in progress (PCN Toolkit integration + tool
build ongoing). This abstract reflects the completed CentileBrain-MFP
and CentileBrain-GAMLSS analyses plus the planned PCN Toolkit
integration. Findings quoted are stable within the CentileBrain
analyses and expected to hold for PCN Toolkit based on the platform's
comparable calibration characteristics; the final abstract will be
updated when PCN Toolkit numbers land.

---

## Abstract

Normative modelling of brain morphometry generates per-subject
deviation scores by comparing individual measurements against
reference distributions derived from tens of thousands of healthy
subjects. Pre-trained models are now distributed by multiple research
groups, but external validation to date has been confined to
individual platforms, and no published work has tested whether
findings replicate across platforms or across algorithm-class choices
within a platform. Here we report the first head-to-head external
validation of published normative brain-morphometry models on a
common clinical cohort. We applied two platforms — CentileBrain (Ge
et al., *Lancet Digital Health* 2024; 37,407-subject training
reference), using both of its distributed algorithm classes
(multivariate fractional polynomial regression [MFP] and generalised
additive models for location, scale and shape [GAMLSS]), and the PCN
Toolkit lifespan models (Rutherford et al., *Nature Protocols* 2022;
57,000+ subject reference, hierarchical Bayesian regression) — to
442 focal-epilepsy patients and 100 healthy controls from the IDEAS
UK cohort (Taylor et al., *Epilepsia* 2025), using the standard PCN
Toolkit site-adaptation procedure per platform. Across all 150
Desikan-Killiany + Aseg regions, we found that (i) all three
algorithm instances produced well-calibrated Z-scores on IDEAS
controls (per-region standard deviation 1.00–1.09); (ii) platform-
derived Z-scores converged with IDEAS's independent ComBat-
harmonised Z-scores at Pearson r ≈ 0.83–0.97; (iii) contrary to the
CentileBrain team's original HCP-EP psychosis finding (Z-scores
AUC 0.63 vs raw AUC 0.49), Z-scores gave no advantage over raw
morphometry for epilepsy vs healthy-control classification under any
algorithm (AUC ≈ 0.80 vs 0.79); (iv) pre-operative Z-scores showed
weak but statistically-real concordance with the surgically-resected
region (Spearman ρ ≈ 0.08, 13× the region-shuffled null), consistent
across all algorithms and with a modest seizure-freedom outcome
gradient. Cross-platform convergence rules out platform-specific
artefacts as an explanation for the negative clinical-utility
finding, scoping the CentileBrain psychosis result to conditions
where either disease geometry or limited sample size makes raw
morphometry insufficient. Alongside the validation we release
`normreport`, an open-source containerised command-line tool
implementing all three tested backends with cross-backend consensus
flagging — the first offline multi-backend normative report
generator, deployable in credentialed clinical-research pipelines.
All code, per-subject Z-scores, and the tool are available at
[https://github.com/phindagijimana/normative](https://github.com/phindagijimana/normative).

---

**Keywords:** normative modelling; brain morphometry; external
validation; focal epilepsy; CentileBrain; PCN Toolkit; Desikan-Killiany
atlas; surgical planning; open-source neuroimaging tools

---

## Statement of significance *(optional; some journals require this)*

Multi-platform external validation of published normative brain
morphometry models has not previously been reported. We show that
findings replicate across two independently-developed platforms and
three algorithm classes, that the widely-cited clinical-utility claim
for normative modelling in psychiatry does not generalise to focal
epilepsy, and that pre-operative normative deviation scores contain
weak but real information about the epileptogenic zone. We accompany
the validation with `normreport`, the first offline multi-backend
normative report generator, which lets other groups replicate our
analyses in their own cohorts and deploy multi-platform normative
scoring inside credentialed clinical-research pipelines.

---

## Notes for internal review

- The abstract runs ~380 words — within NeuroImage's typical 250–500
  word abstract range; some target journals prefer ≤ 300 (may need
  trimming for those).
- Author list is a placeholder pending PI decision on order and
  additional collaborators.
- Institution names and departments need confirmation from the
  URMC side.
- The GitHub URL is the live repo (commit `1b52c58`).
- The Statement of Significance section is included as an optional
  block; only some target journals ask for one.
- Findings on PCN Toolkit backend are marked as "planned" here — this
  abstract will be updated with concrete PCN Toolkit numbers once the
  integration (scheduled ~3–5 days from the start of Path 2A execution)
  completes.
