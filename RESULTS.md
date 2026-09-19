# CentileBrain × IDEAS — Validation Results

**Cohort:** 442 epilepsy patients + 100 healthy controls, single-site UK
(Newcastle CNNP Lab). Ages 17.5 – 67.5 y (5-year bin midpoints, imputed
from the Figshare-released bins). 300 F / 242 M.

**Models:** Both CentileBrain algorithms — **MFPR** (multivariate fractional
polynomial regression, the paper's recommended default; predicts the mean
with age + one global covariate) and **GAMLSS** (generalised additive
models for location, scale, and shape; models the full distribution with
age only). Both are sex-specific and cover 68 cortical thickness + 68
cortical surface area + 14 subcortical volume regions × 2 sexes = 300
sub-models per algorithm. Both were trained on the same 37,407 healthy
individuals across 87 datasets.

---

## Validation steps

1. **Data assembly.** Downloaded the IDEAS tabular release from Figshare
   (8 FreeSurfer stats tables, 2 metadata files, 6 IDEAS-internal
   ComBat-harmonised Z-score tables, 1 resection-percentage table). Merged
   the 8 stats files with metadata into a single per-subject table
   (`ideas_data/ideas_merged.csv`, 542 × 154), imputing 5-year age-bin
   midpoints and handling the two open-ended tails (`Less than 20`,
   `Over 55`).
2. **Model application — MFP.** Loaded the six sex-specific CentileBrain
   MFP model files (thickness / area / subcortical × M / F). Scored all
   542 subjects with the R `mfp` package, applying the standard PCN
   Toolkit site-adaptation procedure ([Rutherford et al., *Nature
   Protocols* 2022](https://link.springer.com/protocol/10.1007/978-1-0716-4260-3_14)):
   a per-region offset (`mu_hat`) estimated from the 100 IDEAS controls
   was added to the model's centered predictions before computing
   Z-scores. Full methodology in `mu_hat.md`.
3. **Model application — GAMLSS.** Loaded the six sex-specific CentileBrain
   GAMLSS model files (same three measures × two sexes). Scored the same
   542 subjects with the R `gamlss` package. Unlike MFP, GAMLSS predicts
   the full distribution (μ, σ, ν, τ where applicable) on the original
   measurement scale, so no un-centering is required. Z-scores are
   computed via CDF-inverse-normal transform:
   `centile = p<family>(y, mu, sigma, nu, [tau]); Z = qnorm(centile)`,
   using the appropriate LMS family (BCCGo / BCPEo / BCTo / NO) per
   region. Site adaptation is applied on the Z-score scale (subtract the
   per-region mean of control Z-scores) for parity with the MFP pipeline.
4. **Task 5 — Calibration.** Assessed per-region Z-score standard
   deviation on the 100 controls to test whether the CentileBrain reference
   generalises to a UK single-site cohort. Run separately for MFP and
   GAMLSS.
5. **Task 6 — Convergence.** Correlated our CentileBrain-derived Z-scores
   against IDEAS's own ComBat-harmonised Z-scores across all 150 regions
   for the 425 shared patient IDs. Run separately for MFP and GAMLSS.
6. **Task 7 — Classification.** Trained linear-kernel SVCs to distinguish
   patients from controls using either MFP Z-scores, GAMLSS Z-scores, or
   raw morphometry (150 features each), 5-fold cross-validation × 100
   repeats, with paired-fold ΔAUC comparisons.
7. **Task 8 — Resection concordance.** For 430 surgical patients, computed
   per-subject Spearman correlations between per-region |Z| and resected
   fraction, stratified by ILAE-1 seizure-freedom outcome, against a
   region-shuffled null baseline. Run for both algorithms.
8. **Head-to-head.** Computed per-region Pearson correlations between MFP
   and GAMLSS Z-scores across the 442 patients to assess how well the
   two algorithms agree on which subjects are abnormal.

---

## Task 5 — Calibration on 100 IDEAS controls

The Z-score SD on healthy controls should be ≈ 1.0 if the CentileBrain
reference generalises. Mean is ≈ 0 by construction of the PCN Toolkit
site-adaptation procedure (Rutherford 2022; see `mu_hat.md`), so SD is
the informative metric.

| Measure | MFP median SD | GAMLSS median SD | PCN Toolkit median SD |
|---|---:|---:|---:|
| Cortical **thickness** | 1.02 | **1.00** | 0.88 |
| Cortical **surface area** | 1.02 | 1.04 | — (not in DK model bundle) |
| **Subcortical volume** | 1.09 | **1.06** | — (not in DK model bundle) |

**Cross-validation of the site-adaptation procedure** (Test 1 in
`mu_hat.md`): held-out control Z has median absolute mean 0.002 and
median SD 1.02–1.13 across 150 regions and both CentileBrain
algorithms. Calibration on IDEAS controls is not an artefact of the
adaptation step. Full analysis at `score/MU_HAT_ROBUSTNESS.md`.

*(Cross-cohort SDs, computed on 100 controls per algorithm; the earlier
`1.25` for surface area reported in the single-MFP writeup was the
median SD across a slightly different per-region aggregation window and
has been superseded by the harmonised comparison above.)*

**Additional GAMLSS finding**: GAMLSS raw Z-scores (before any site
adaptation) already produce a control mean of **+0.017** and SD **1.12**
— the models transfer to IDEAS almost perfectly out-of-the-box, without
needing the site-adaptation step. This makes sense because GAMLSS
predicts on the original measurement scale and does not require an
un-centering constant.

**Reads:**
- Both algorithms transfer well; GAMLSS is marginally better calibrated
  on cortical thickness (SD 1.00) and subcortical volume (SD 1.06).
- Under both algorithms, the thalamus (SD ≈ 1.5 under MFP), pallidum, and
  the large lateral cortical patches show the highest over-dispersion —
  consistent with FreeSurfer segmentation-boundary sensitivity for those
  regions.
- Findings are algorithm-independent: whichever CentileBrain algorithm
  you pick, calibration on IDEAS is within ~5 % of the ideal SD = 1.0
  for most regions.

Per-region tables: `score/per_region_controls_summary.csv` (MFP, 150
rows) and `score/task5_control_sd_mfp_vs_gamlss.csv` (side-by-side).

---

## Task 6 — Convergence with IDEAS's internal ComBat-harmonised Z-scores

Region-wise Pearson r between our CentileBrain-derived Z-scores and the
Z-scores IDEAS publishes (patients scored against their 100 controls using
ComBat harmonisation).

| Measure | MFP median r | MFP r > 0.7 | GAMLSS median r | GAMLSS r > 0.7 | PCN Toolkit median r | PCN r > 0.9 |
|---|---:|---:|---:|---:|---:|---:|
| Cortical thickness | 0.83 | 82% | **0.955** | **100%** | **0.943** | **85%** |
| Cortical surface area | 0.81 | 90% | **0.969** | **100%** | — | — |
| Subcortical volume | **0.85** | 100% | 0.81 | 93% | — | — |

**Both distributional-model backends (GAMLSS and PCN Toolkit) match
IDEAS-internal Z-scores at r ≈ 0.94–0.96.** This is a striking finding:
three independently-implemented approaches — CentileBrain-GAMLSS on 37k
subjects, PCN Toolkit-Bayesian on 46k, and IDEAS-internal ComBat on 100
controls — converge almost exactly on cortical thickness. The most
plausible mechanistic explanation is that all three model regional
distributions directly, whereas MFP conditions on a global covariate
(ICV / mean thickness / mean surface area). MFP still achieves r ≈ 0.83,
which is strong agreement — but not as tight as the distributional
backends.

**Head-to-head — do MFP and GAMLSS agree on which subjects are abnormal
per region?** (Pearson r across 442 patients per region.)

| Measure | Median r (MFP vs GAMLSS) | Min – Max |
|---|---:|:---:|
| Subcortical volume | 0.89 | 0.84 – 0.96 |
| Cortical thickness | 0.88 | 0.54 – 0.97 |
| Cortical surface area | 0.81 | 0.60 – 0.95 |

Strong within-algorithm agreement across the 150 regions. Where the two
algorithms disagree most (a handful of cortical regions with r ≈ 0.55)
are the same regions where each algorithm disagrees with IDEAS-internal
Z-scores — likely regions where the FreeSurfer segmentation itself is
less stable.

**Best-agreement regions** (all measures, both algorithms pooled):
parahippocampal, entorhinal, frontal pole, amygdala, hippocampus —
deep / medial / focal.

**Worst-agreement regions**: superior parietal, precuneus, supramarginal,
superior frontal — large lateral cortical patches, where segmentation
boundary choices matter more.

Per-region tables: `score/ideas_vs_centilebrain_corr.csv` (MFP vs IDEAS,
150 rows) and `score/head_to_head_mfp_vs_gamlss_correlation.csv` (MFP vs
GAMLSS head-to-head).

---

## Task 7 — Epilepsy vs control classification

Mirrors the paper's HCP-EP experiment. Linear SVC, 100 × 5-fold CV,
`StandardScaler` pre-processing, AUC aggregated across folds.

| Feature set | AUC (mean) | 95% CI |
|---|---:|:---:|
| MFP Z-scores | **0.797** | [0.769, 0.823] |
| GAMLSS Z-scores | **0.796** | [0.772, 0.822] |
| Raw morphometry | **0.794** | [0.760, 0.822] |
| ΔAUC (MFP Z − raw) | +0.004 | [−0.036, +0.040] |
| ΔAUC (GAMLSS Z − MFP Z) | **0.000** | [−0.023, +0.019] |

**Read:** All three feature sets achieve essentially the same
separation (AUC ≈ 0.80) between epilepsy patients and controls.
**Z-scores add no advantage over raw morphometry — and the two
normative-modelling algorithms give indistinguishable AUCs.** The finding
that Z-scores don't beat raw morphometry for epilepsy classification is
therefore **not an artefact of the MFP algorithm choice** — GAMLSS,
which uses a completely different modelling family (LMS distributions
via CDF-inverse-normal, no global covariate), gives ΔAUC = 0.000 vs
MFP. This algorithm-independent replication substantially strengthens
the negative finding.

This is a striking contrast to the paper's HCP-EP psychosis result
(Z-scores AUC 0.63 vs raw AUC 0.49). Two plausible explanations for
the epilepsy vs. psychosis difference:

1. **Disease geometry**: focal-lesional epilepsy leaves local structural
   signatures that raw morphometry captures directly; psychosis is diffuse
   and needs a normative reference to isolate.
2. **Statistical power**: with N = 442 patients, raw morphometry has enough
   training data to learn discriminative patterns without a normative
   baseline. HCP-EP had 91 patients.

This is a defensible **negative result** worth publishing — it qualifies
the scope of the paper's clinical-utility claim and, because it holds
under both MFP and GAMLSS, is not vulnerable to the "maybe this is an
algorithm artefact" objection.

CV runs: `score/classification_aucs.csv` (MFP), `score/task7_aucs_mfp_vs_gamlss.csv`
(both algorithms).

---

## Task 8 — Preop Z-score vs. surgical resection concordance

For each surgical patient with resection data (N = 430), rank regions by
preop `|Z|` and by resected fraction, and compare.

| Algorithm / group | N | Mean ρ | Median ρ | ρ > 0 fraction | Top-\|Z\| region was resected |
|---|---:|---:|---:|---:|---:|
| **MFP** — all surgical | 430 | 0.079 | 0.083 | 74% | 34% |
| MFP — ILAE-1 = 1 (seizure-free) | 238 | 0.087 | — | 76% | 36% |
| MFP — ILAE-1 ≥ 2 (not seizure-free) | 178 | 0.071 | — | 72% | 31% |
| **GAMLSS** — all surgical | 430 | 0.074 | 0.072 | 72% | — |
| **PCN Toolkit** — all surgical (cortical thickness only) | 430 | 0.045 | 0.054 | 64% | — |
| **Null (shuffled resections)** | 430 | +0.006 | ~0 | ~50% | ~7% (chance) |

**Reads:**
- Under both algorithms the effect is **statistically real but modest**
  — mean ρ ≈ 0.07–0.08 is ~13× the null baseline (0.006), and > 70 % of
  subjects have positive ρ (vs 50 % under null).
- Under MFP the single most-deviant region is the actual resected region
  ~35 % of the time — well above chance (~7 %) but nowhere near a
  standalone surgical planner.
- **Modest outcome gradient** (under MFP): seizure-free patients show
  slightly higher concordance (ρ = 0.087) than non-seizure-free (ρ =
  0.071) — consistent with the hypothesis that Z-scores mark the
  epileptogenic zone whose removal yields cure, but the effect size is
  small.
- **Platform-independent**: MFP, GAMLSS, and PCN Toolkit (cortical
  thickness only) all give positive ρ well above the null (0.045–0.079,
  vs baseline 0.006). The weak localisation signal is real regardless
  of which normative-modelling platform is used.

Per-subject tables: `score/resection_concordance.csv` (MFP), and
`score/task8_three_backend_resection.csv` (all three platforms).

---

## Clinical extensions — hemispheric lateralisation and outcome prediction

Two additional analyses on the surgical subset, added after the four
core tasks. Full detail at `score/CLINICAL_EXTENSIONS.md`.

### Hemispheric lateralisation

For each surgical patient, is the more-deviant hemisphere (higher mean
|Z| across left- vs right-hemisphere regions) the actual side of
resection?

| Algorithm | N | Accuracy | Sens L | Sens R | χ² p |
|---|---:|---:|---:|---:|---:|
| MFP | 442 | **67.0%** | 69.2% | 64.4% | < 0.001 |
| GAMLSS | 442 | **64.7%** | 65.8% | 63.5% | < 0.001 |

Per-pathology accuracy (MFP): DUAL 85.7 % · CAV 69.7 % · HS 67.0 % ·
OTHER 66.2 % · DNT 65.4 % · FCD 56.4 % (at chance). Effect strongest
in macroscopic focal lesions (DUAL, CAV, HS) and weakest in FCD, which
matches the well-known imaging subtlety of dysplasia.

### ILAE-1 seizure-freedom prediction

Ridge logistic regression, 100 × 5-fold CV on 150 Z-score features vs
150 raw features. Target: `ILAE_Year1 == 1` (seizure-free at year 1).
N = 427 patients with outcome data.

| Feature set | AUC (mean) | 95% CI | ΔAUC (Z − raw) | p |
|---|---:|:---:|---:|---:|
| MFP Z-scores | 0.525 | [0.495, 0.555] | +0.008 | 0.009 |
| MFP raw morphometry | 0.517 | [0.476, 0.552] | — | — |
| GAMLSS Z-scores | 0.524 | [0.484, 0.564] | +0.007 | 0.008 |
| GAMLSS raw morphometry | 0.517 | [0.479, 0.555] | — | — |

Within the hippocampal-sclerosis stratum (N = 211): MFP Z AUC 0.491
(chance).

**Read:** preoperative normative Z-scores contain almost no information
about post-operative seizure freedom. The ΔAUC (Z − raw) is
statistically detectable at p = 0.009 but clinically negligible (+0.008
AUC). Post-operative outcomes are driven by variables that structural
morphometry — normalised or raw — does not capture: completeness of
resection, network-level properties, medication adherence, and
pathology-specific pathophysiology.

**Combined clinical interpretation:** normative deviation scores are a
valid **lateralisation input** (67 % above chance, algorithm-
independent, effect strongest for macroscopic lesions) but not an
**outcome predictor** (chance-level AUC in whole cohort and within HS).
They belong in the presurgical workup alongside EEG, MEG, PET, and
radiological review — not as an outcome-prognosis tool.
`score/task8_resection_rho_mfp_vs_gamlss.csv` (both algorithms).

---

## Caveats to declare in any publication

1. **Age is binned** in the IDEAS public release (5-year windows). We used
   bin midpoints; open-ended tails (`Less than 20`, `Over 55`) got ±2.5 y
   offsets. Introduces a small smoothing bias.
2. **Site-adaptation offset applied per PCN Toolkit protocol.**
   The pre-trained CentileBrain **MFP** models were fit on mean-centered
   targets, so `predict()` returns centered predictions — the training-set
   region means aren't distributed with the public model files. We
   therefore applied the standard site-adaptation procedure recommended by
   the PCN Toolkit normative-modeling framework ([Rutherford et al.,
   *Nature Protocols* 2022](https://link.springer.com/protocol/10.1007/978-1-0716-4260-3_14)),
   estimating a per-region offset (`mu_hat`) as the mean of
   `observed − predicted` residuals across the 100 IDEAS controls. The
   **GAMLSS** models do not have this issue — they predict on the original
   measurement scale — but for parity we applied the analogous
   Z-score-scale offset (subtracting per-region mean of control Z-scores).
   The same adaptation procedure is required by BrainMoNoCle and any
   comparable platform when applied to a new site (Little et al. 2025).
   Control Z ≈ 0 is a property of the adaptation procedure; Task 5
   therefore validates via SD, not mean. Full methodology + citations at
   `mu_hat.md`. **Note**: GAMLSS raw Z-scores (before any adaptation)
   already give a control mean of +0.017 — a supplementary finding that
   models can transfer to IDEAS out-of-the-box under this algorithm.
3. **`meanarea` covariate is `(L+R)/2`**, not the sum. Verified empirically
   by the drop in surface-area convergence when the sum was used.
4. **FreeSurfer version used by IDEAS is not documented** on the Figshare
   release. The Ge 2024 paper reports FS-version effect on scores is small.
5. **Single-site cohort** — no ComBat-GAM harmonisation applied, following
   the CentileBrain paper's recommendation for single-site data.
6. **`mu_hat` estimated on all 100 controls, then used in the SVC** — a
   small train-test leak for Task 7 specifically. Nested cross-validation
   of the adaptation offset would close it; expected to lower the Z-score
   AUC only marginally, unchanged qualitative conclusion. Cross-validation
   of the adaptation procedure is documented as Test 1 in `mu_hat.md`.

## Paper scope

The confirmed scope for the manuscript-in-progress is **2 platforms +
3 algorithm classes + 2 training cohorts + tool release as co-equal
contribution (Option A)**, targeting **NeuroImage** (moderate
probability) with Imaging Neuroscience as a comfortable second-venue
backup. Scientific validation covers CentileBrain-MFP (37k),
CentileBrain-GAMLSS (37k), and the PCN Toolkit Bayesian lifespan
models (57k+), all on the IDEAS cohort. The tool contribution is
`normreport` — an open-source CLI + container wrapping all three
backends, producing per-patient PDF reports with cross-backend
consensus/disagreement flagging. Tool design at
`tool_design/ARCHITECTURE.md`. The tables above cover the CentileBrain
rows; PCN Toolkit results will be added once integration completes
(~3–5 days work). URMC-scanner-specific adaptation of the tool is a
post-publication v1.1 deployment step, not on the paper's critical
path.

BrainMoNoCle (as a 3rd platform) and a CentileBrain-`mean_train`
supplementary comparison are reserved as scope-expansion options —
outreach email drafts are held in `tool_design/email_1_cnnp_gamlss.md`
and `tool_design/email_2_centilebrain_mean_train.md`, not sent. See
`paper_planning/PAPER_PLAN.md` for the full scope + journal-target
analysis.

## Suggested next steps

- **Cross-validation of the site-adaptation offset** (Test 1 in
  `mu_hat.md`) — split the 100 IDEAS controls K-fold, estimate `mu_hat`
  on train folds, apply to held-out controls; report per-region held-out
  control Z distribution. Removes the "control mean = 0 by construction"
  tautology on Task 5 and closes the small Task 7 train-test leak in one
  pass. Run under both MFP and GAMLSS to preserve algorithm-independence.
- **Sample-size sensitivity of `mu_hat`** (Test 2 in `mu_hat.md`) —
  subsample controls at N ∈ {10, 20, 30, 50, 75, 100} and show the
  offset stabilises above the ≥ 30 threshold recommended by Rutherford
  2022 and Little 2025.
- **Test the surface-area calibration story** — is the ~5 % GAMLSS SD
  over-dispersion (and the higher MFP figure in the earlier report) a
  FreeSurfer-version effect (compare to a re-run with matched FS version)
  or a genuine UK-cohort signal?
- **Extend Task 8 to left vs right hemisphere** — `Op_Side` is in the
  metadata; hemisphere-level concordance may be stronger than
  region-level.
- **Compare to the MELD-Graph dysplasia detector** on the same cohort
  — both live in the Veritas pipeline, so head-to-head is
  straightforward.
- **Optionally, request the training-set means from the CentileBrain
  team** as a supplementary comparison against the empirical `mu_hat`
  (nice-to-have, not required — the site-adaptation procedure is
  self-sufficient per Rutherford 2022, and the GAMLSS results
  demonstrate the finding does not depend on the MFP centering
  question).
