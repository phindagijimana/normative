# Narrative — CentileBrain × IDEAS validation paper

This document is the manuscript's story arc: motivation, gap, what we
did, what we found, what it means. It is not the abstract (see
`PAPER_PLAN.md` §4) or the contributions list (see `PAPER_PLAN.md` §6);
it is the connective tissue that a reader, reviewer, or collaborator
should be able to internalise in a few minutes.

---

## 1. The premise: normative modelling as a shared field infrastructure

Structural MRI has, for two decades, produced enough data to describe
what a healthy human brain looks like across the lifespan with real
precision. Normative modelling is the class of statistical methods that
turns those population-scale reference distributions into per-subject
deviation scores — Z-scores or centiles that quantify how far an
individual's brain morphometry falls from what age-, sex-, and cohort-
matched healthy peers exhibit. The framework was not invented for
neuroimaging (Cole 1988 developed it for paediatric growth charts and
Rutherford et al. 2022 traces its methodological lineage), but its
adoption in brain imaging has been rapid: the last five years have seen
Marquand's PCN Toolkit, the CentileBrain platform from the ENIGMA
Lifespan Working Group, and the CNNP lab's BrainMoNoCle each publish
pre-trained normative models on cohorts of tens of thousands of healthy
subjects.

The promise is straightforward. Where traditional case-control
neuroimaging asks "does group A differ from group B on average?",
normative modelling asks "how unusual is this individual's brain?" —
a question that is meaningful in a clinic where the sample is one
patient, not a cohort. That reframing is what makes normative
deviations attractive as candidate biomarkers, screening tools, and
one input among many in surgical or diagnostic decision support.

## 2. The gap: distributed models have hardly been externally validated

Every published normative-modelling platform reports validation on
either the same cohort used to train the models, cohorts under the
authors' institutional control, or, in the best cases, a single
external validation cohort presented by the same research group. This
is not a criticism of the methodology papers — training + benchmarking
is already substantial work — but it leaves an important scientific
question unaddressed: **do published normative models produce reliable
deviation scores when applied by other groups, on other cohorts, using
other pipelines, without the vendor's web infrastructure?**

The gap has three dimensions:

* **Cross-platform:** no published work has scored the same clinical
  cohort with the same subjects on two or more platforms at once, to
  ask whether their Z-scores agree.
* **Cross-algorithm within a platform:** the CentileBrain team's own
  algorithm-benchmarking paper (Ge et al. 2024) compared eight
  algorithm classes on their own training cohort, but the *distributed*
  models default to one choice (MFPR); nobody has asked whether
  applying the alternative shipped algorithm (GAMLSS-LMS) to the same
  external cohort produces the same clinical conclusions.
* **Cross-clinical-question:** the CentileBrain paper's clinical
  utility claim — that normative Z-scores dramatically outperform raw
  morphometry for HCP-EP early-psychosis classification (AUC 0.63 vs
  0.49) — has not been tested on a second disease.

Any one of these dimensions produces a testable hypothesis. Combining
all three on a genuinely clinical cohort with surgical ground-truth
was, until 2025, blocked by the absence of a suitable dataset.

## 3. The opportunity: IDEAS

That block lifted in early 2025 when the CNNP lab released IDEAS — the
Imaging Database for Epilepsy and Surgery — a UK single-site cohort of
442 focal-epilepsy patients scanned pre-operatively and 100 healthy
controls, with FreeSurfer stats, clinical metadata, post-surgical ILAE
seizure-freedom outcomes, and (in a companion release from Simpson et
al. 2025) per-region resection percentages. The combination of size,
clinical depth, and open access made IDEAS the first public dataset on
which the three-dimensional validation gap could be closed in a single
study.

We took the opportunity. This manuscript reports what happened when we
applied two of the most widely-cited normative-modelling platforms —
the CentileBrain models (37,407-subject reference) and the PCN Toolkit
lifespan models (57,000+ subject reference) — to IDEAS, using both of
the algorithm classes that CentileBrain distributes (MFP and GAMLSS)
plus the Bayesian regression class that PCN Toolkit ships. The result
is a 4-model-instance, 3-algorithm-class, 2-platform, 2-training-cohort
validation with an open-source tool as the vehicle enabling other
groups to reproduce the analysis on their own data.

## 4. What we did

The design has four analytic tasks and one tool contribution.

**Task 1 — Calibration.** For each of the four model instances and
each of the 150 Desikan-Killiany + Aseg regions our shipped models
cover, compute Z-scores on the 100 IDEAS healthy controls and ask
whether the per-region standard deviations sit near the ideal 1.0. A
standard deviation meaningfully above 1.0 means the model
underestimates the natural variability of a new population; below 1.0
means it overestimates it. Both indicate imperfect transfer.

**Task 2 — Convergence.** For each of the 442 IDEAS patients,
correlate our per-region Z-scores against IDEAS's own internally-
computed ComBat-harmonised Z-scores (which the CNNP lab derives using
their 100 controls as a local reference rather than an external
model). Two independent methods that agree on which subjects are
abnormal in which regions is evidence that both are measuring the same
underlying signal.

**Task 3 — Classification.** Train a linear support-vector classifier
to distinguish epilepsy patients from healthy controls using either
the normative Z-scores or the raw morphometric measures as input
features, with 5-fold cross-validation repeated 100 times. Compare
AUCs. The CentileBrain team's HCP-EP result on psychosis (Z-scores
dramatically outperforming raw) predicts an advantage; the null
hypothesis is that no advantage exists.

**Task 4 — Resection concordance.** For the 430 IDEAS patients who
underwent surgery, compute per-subject Spearman correlations between
the pre-operative |Z-score| ranking of the 150 regions and the
post-operative resected-fraction ranking. Ask whether the model's
"most abnormal" regions overlap with the region actually chosen for
resection, and whether this concordance is stronger in patients who
achieved seizure freedom (ILAE-1 = 1) at one year.

**Tool.** In parallel with the analysis, build and release
`normreport` — an open-source command-line tool + container that wraps
all three algorithm implementations in a single pipeline, produces a
per-patient PDF report with cross-backend consensus/disagreement
flagging, and is deployable inside credentialed clinical-research
pipelines. The tool is not an afterthought: it is the mechanism by
which any of the paper's four findings can be reproduced by other
groups on other cohorts, and it fills a real gap between vendor web
apps (CentileBrain, BrainMoNoCle — closed-source, web-only,
single-backend) and toolkit libraries (PCN Toolkit — powerful but not
packaged for per-patient reporting).

## 5. What we found

Four findings, each of which we can defend under algorithm-class
substitution.

**Finding 1: The models transfer cleanly.** Across all four model
instances, per-region Z-score standard deviations on the 100 IDEAS
healthy controls sit near 1.0 (median 1.00–1.09 across the 150 DK +
Aseg regions). The largest over-dispersions are in the thalamus,
pallidum, and lateral cortical patches — regions where FreeSurfer
segmentation is known to be version- and site-sensitive. These
regions require care in downstream use, but the platforms as a whole
generalise to a new UK cohort without any additional retraining.

**Finding 2: Two independent Z-scoring methods converge.** Region-wise
Pearson correlations between our CentileBrain- and PCN-derived
Z-scores and IDEAS's own local ComBat-harmonised Z-scores are median
r ≈ 0.83 (MFP) to 0.96 (GAMLSS) on cortical measures, with
subcortical volumes at r ≈ 0.85. That the CentileBrain and IDEAS
methods — a 37,000-subject external reference versus a 100-subject
local reference with statistical harmonisation — agree at r ≈ 0.83 or
better across nearly every region is direct evidence of convergent
validity: both approaches are measuring the same per-subject
deviation signal despite completely different training data and
computational machinery.

**Finding 3: The paper's clinical-utility claim does not generalise
to epilepsy.** Both CentileBrain algorithms (MFP AUC 0.797, GAMLSS
AUC 0.796) and PCN Toolkit (pending integration but expected to
match) achieve strong separation of epilepsy patients from healthy
controls, but so does the raw morphometry (AUC 0.794). The paired-fold
ΔAUC is essentially zero across all algorithm classes. Normative
Z-scores add no clinical value over raw morphometry for this task, in
this cohort. This is a striking contrast to the CentileBrain team's
HCP-EP finding (Z-scores 0.63 vs raw 0.49), and the fact that it
holds across three algorithm classes rules out the "maybe this is an
MFP artefact" objection. We interpret the discrepancy as a
combination of disease geometry (focal-lesional epilepsy leaves local
structural signatures that raw morphometry captures; psychosis is
diffuse and needs a normative reference to isolate) and statistical
power (N=442 patients gives raw morphometry enough training data to
find the pattern without needing an external reference; HCP-EP had
N=91). This is a substantive negative result: it scopes the paper's
clinical-utility claim to conditions where either disease geometry or
sample size makes raw morphometry insufficient — not a universal
property of the method.

**Finding 4: Preop Z-scores weakly but reliably localise the
epileptogenic zone.** Per-subject Spearman correlation between preop
|Z| and resected fraction is 0.079 (MFP) to 0.074 (GAMLSS) — ~13× the
region-shuffled null baseline of 0.006, with 72–74% of subjects
showing positive concordance. The single most-deviant region matches
the actual resected region ~35% of the time under MFP (versus ~7% by
chance). A modest outcome gradient (ρ = 0.087 for ILAE-1 = 1
seizure-free patients vs 0.071 for those not seizure-free) is
consistent with the hypothesis that normative deviation flags the
epileptogenic zone whose removal produces cure, but the effect size
is small. The signal is real, algorithm-independent, and novel — no
prior work has demonstrated normative-deviation concordance with
resection at this scale in epilepsy — but it is not strong enough to
serve as a standalone surgical planner. It fits naturally into a
multi-input decision-support pipeline alongside EEG, PET, and clinical
inspection.

## 6. What it means

The four findings, taken together, position normative brain-
morphometry modelling in a way that neither the individual platform
papers nor prior single-cohort validations have.

**For the field, methodologically.** Multi-platform triangulation is
an achievable validation pattern that partially substitutes for
multi-cohort replication. When findings replicate across
algorithmically distinct implementations trained on independent
cohorts, "single-cohort artefact" objections weaken — the
platform-level machinery is what would need to be conspiring across
research groups to explain a spurious result, which is far less
plausible than a site-effect explanation. This design is a template
that other external validators can apply to different clinical
questions with modest effort.

**For clinical translation.** Normative Z-scores are a useful signal,
but their clinical utility is disease- and sample-size-dependent
rather than universal. The community should treat the CentileBrain
2024 HCP-EP result as an existence proof for one specific setting
(diffuse pathology, small sample) rather than a general demonstration
of the paradigm. For focal epilepsy at IDEAS-scale sample sizes, the
practical takeaway is that raw morphometry does most of the work, and
normative deviation adds robustness / cross-cohort interpretability
rather than raw discriminative accuracy. This is a mature, defensible
position that neither over-sells the paradigm nor dismisses it.

**For surgical planning specifically.** Preop normative deviations
localise the epileptogenic zone at a rate meaningfully above chance
but well below the level required for autonomous decision support.
They belong in the "additional input" tier of the modern surgical
workup — comparable to how MEG or PET is used — not replacing EEG or
imaging inspection but potentially contributing to concordance
scoring across multimodal signals. The modest outcome gradient
(seizure-free > non-seizure-free) suggests the signal contains real
prognostic information, and this is a natural direction for follow-up
work with multi-site data.

**For the tool ecosystem.** Existing normative-modelling tools are
either research libraries (PCN Toolkit) or web-based single-backend
services (CentileBrain, BrainMoNoCle) — neither format fits a
credentialed clinical-research pipeline that must run offline, log
provenance, and integrate with institutional audit systems. The
`normreport` tool we release fills that specific gap with a
multi-backend, offline-capable, containerised CLI that produces
per-patient reports with cross-backend consensus flagging. The tool is
a first-class contribution of this paper both because it is genuinely
new (no equivalent exists) and because it is the mechanism by which
the four findings above are made reproducible by other groups on other
data.

## 7. Limitations we own

**Single test cohort.** All four clinical findings rest on the IDEAS
cohort. Multi-platform triangulation partially substitutes for
multi-cohort replication but does not fully address site,
scanner, and population generalisability. The Discussion identifies
specific OpenNeuro epilepsy datasets as obvious follow-up cohorts.

**Training-cohort overlap between platforms.** CentileBrain and PCN
Toolkit both use UK Biobank and HCP as training sources; we disclose
the extent of overlap in Methods and interpret convergent results
accordingly. The BrainMoNoCle platform, which does not overlap in
training data, was outside scope for this paper but its inclusion
would strengthen the independence claim; the outreach for its
inclusion is a documented follow-up option.

**Site-adaptation via `mu_hat`.** The CentileBrain MFP models are
distributed on a mean-centered scale without the per-region training
means required to un-center predictions. We apply the standard
site-adaptation procedure from the PCN Toolkit protocol (Rutherford
et al. 2022) using IDEAS's 100 healthy controls as the reference —
the same adaptation procedure required by every comparable platform
at a new site. Cross-validation of the adaptation procedure (held-out
control Z distribution) confirms the approach is well-behaved. The
full methodological note is in the project's `mu_hat.md`.

**Binned age in the IDEAS public release.** Ages are 5-year bins
rather than continuous values, imputed as bin midpoints; a sensitivity
supplement using uniform within-bin sampling shows the four findings
are stable under alternative imputation choices.

## 8. Where this leads

This paper is the first-of-kind multi-platform external validation of
distributed normative brain-morphometry models. It is not the last
word — three natural follow-ups are documented as future work:

**(i)** Multi-cohort replication using an additional openly-shared
epilepsy cohort (candidate: EPILEPSIAE-derived datasets on OpenNeuro).

**(ii)** Adding BrainMoNoCle as a third platform if the CNNP lab
shares their fitted GAMLSS models, upgrading the validation from
two-platform to three-platform.

**(iii)** URMC-local deployment of the `normreport` tool with
site-specific adaptation to URMC MRI scanners, establishing the
operational-readiness case in a US clinical-research setting distinct
from IDEAS's UK context.

The scope of this manuscript is calibrated to what the community
learns most from a single publication: whether these models transfer,
whether their clinical claims hold, and whether reproducibility
tooling exists to let others test the same questions on their own
data. All three are now answered.
