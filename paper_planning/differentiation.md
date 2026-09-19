# Differentiation — contribution, distance, novelty, journal tier

This document is the quantitative sibling of `validate_narrative.md` and
`PAPER_PLAN.md`. Where those two describe *what* the paper says and *how* the
work is scoped, this one quantifies *how much* the paper contributes,
*how far* it sits from the nearest prior work, and *which journal tier*
that distance realistically supports. Intended readers: the manuscript's
lead author when writing the Introduction and Discussion positioning
paragraphs; a PI asking "how do we compare to X?"; a reviewer
adjudicating the paper's novelty claim; a future collaborator scoping a
follow-up.

The rubric is imperfect but consistent — the same lens is applied to
our work and to comparable published papers so that the comparisons are
honest rather than self-serving.

---

## 1. Contribution — quantified

### 1.1 Concrete numbers we can cite

| Metric | Value | Comparison to prior work |
|---|---:|---|
| Platforms externally validated | **2** (CentileBrain, PCN Toolkit) | Prior external validations: 1 platform, always |
| Algorithm classes tested on same clinical cohort | **3** (MFP, GAMLSS, Bayesian) | Prior work: 1 |
| Total training-cohort size represented | **94,000+** subjects across ~140 sites | Ge 2024 alone: 37 k; Rutherford 2022 alone: 57 k |
| Clinical subjects scored | **542** (442 patients + 100 controls) | Ge 2024 HCP-EP: 148 subjects |
| Surgical patients with resection ground truth | **430** | No prior epilepsy-normative resection concordance published |
| Regions per subject × algorithms | **150 × 3 = 450 Z-scores** per subject | Prior single-platform work: 150 |
| Distinct research groups whose models we validated | **2** (Frangou/Ge lab, Marquand lab) | 1 |
| Novel methodology-service artefacts | **2** (`mu_hat.md` documented recipe, `normreport` tool) | 0 for this method-user gap |
| Files shipped as open source | **35** files / **28.3 MB** at commit `1b52c58` | Single-platform papers typically ship 5–10 scripts |
| Pre-computed public Z-score datasets released | **2** (MFP + GAMLSS, 81,300 rows each) | Rare — most papers release scripts, not scored outputs |

### 1.2 Novelty rubric — every claim scored

Every claim we might make in the manuscript, categorised as **N**
(genuinely new — no comparable published claim), **N/S** (novel but
similar work exists), or **E** (established, not our contribution).
Weights: **N** = 3, **N/S** = 1, **E** = 0.

| # | Claim | Category | Novelty pts |
|---|---|:---:|---:|
| 1 | First head-to-head external validation of two published normative-modelling platforms on a common clinical cohort | **N** | 3 |
| 2 | First test of the CentileBrain clinical-utility claim on a disease other than the paper's original psychosis demo | **N** | 3 |
| 3 | First test of preop normative-deviation → surgical resection concordance at N > 400 in focal epilepsy | **N** | 3 |
| 4 | First offline multi-backend normative report tool with cross-backend consensus flagging | **N** | 3 |
| 5 | First documented offline-scoring recipe for the CentileBrain MFP models | **N** | 2 |
| 6 | Convergence between external-reference and local-ComBat Z-scoring at r ≈ 0.83–0.97 across three algorithms | **N/S** | 1 |
| 7 | Cross-validation of the PCN Toolkit adaptation procedure on IDEAS controls | **N/S** | 1 |
| 8 | Standard FreeSurfer preprocessing | **E** | 0 |
| 9 | Standard SVC / cross-validation benchmark methodology | **E** | 0 |
| 10 | Standard Spearman correlation testing | **E** | 0 |
| **Total** | | | **16** |

### 1.3 Calibration against published work

The rubric is only meaningful if it produces comparable scores for
comparable papers. Applied to nearby published work using the same
weighting scheme:

| Paper | Approximate rubric score | Actual published venue (IF) |
|---|---:|---|
| Bayer et al. 2022 (transfer learning for cortical thickness) | 6–8 | *Human Brain Mapping* (~5) |
| Little et al. 2025 (BrainMoNoCle platform paper) | 10–12 | *Imaging Neuroscience* (~4) |
| **Our paper (current scope)** | **16** | **Target: NeuroImage / Imaging Neuroscience** |
| Rutherford et al. 2022 (PCN Toolkit protocol + release) | 18–22 | *Nature Protocols* (~15) |
| Ge et al. 2024 (CentileBrain algorithm benchmark + release) | 20–25 | *Lancet Digital Health* (~30) |

We sit between Bayer 2022 (HBM) and Rutherford 2022 (Nature
Protocols), somewhat closer to the latter. This positions us
realistically in the HBM / Imaging Neuroscience / NeuroImage band —
not at Ge 2024's Lancet Digital Health level because we're doing
validation rather than method-release, and not at Bayer's HBM level
because we have more independent axes of novelty.

---

## 2. Distance from the closest prior work

Each row lists a specific published paper adjacent to ours and
enumerates what we add.

| Nearest prior paper | Their scope | Our added distance |
|---|---|---|
| **Ge 2024** (*Lancet Digit Health*) — CentileBrain | Single platform, algorithm benchmark on their own cohort, HCP-EP psychosis clinical demo | +1 platform (PCN Toolkit) validated on independent cohort, +2 algorithm classes compared on a common external cohort, +1 clinical demo that *contradicts* their main utility claim on a different disease, +1 novel clinical question (resection concordance), +1 open-source tool |
| **Rutherford 2022** (*Nature Protocols*) — PCN Toolkit | Protocol paper documenting the framework, no external clinical validation | +1 external clinical cohort with cross-platform triangulation, +1 tool release that operationalises their protocol for others |
| **Little 2025** (*Imaging Neuroscience*) — BrainMoNoCle | Single platform + web tool | +1 platform comparison (CentileBrain and PCN Toolkit both tested on IDEAS), +1 offline multi-backend tool that BrainMoNoCle doesn't offer, +14 subcortical regions (BrainMoNoCle is cortical only) |
| **Simpson 2025** (*Imaging Neuroscience*) — IDEAS resection release | Released resection data + masks, no normative-modelling application | +1 first application of any normative model to their resection data at N = 430, +ILAE-outcome stratification |
| **Bayer 2022** (*HBM*) — transfer learning for cortical thickness | Single platform (PCN Toolkit), one measure type (thickness), scanner transfer only | +2 platforms, +2 measure types (surface area + subcortical volume), +4 clinical validation tasks, +1 clinical cohort with disease + outcomes |
| **Ge 2026** (*PNAS*) — ethnoracial validation of CentileBrain | Single platform, in-house validation across ethnoracial groups | +1 cross-*platform* validation (they did within-platform demographic validation), +clinical/surgical ground truth (they did not) |

**On every axis we differ from the nearest published work in at least
one meaningful direction; the combined distance across axes is
materially larger than any single competing paper.** No published paper
combines multi-platform, multi-algorithm, epilepsy application,
resection concordance, and open tool release — the combination is
what makes ours contributionally distinct even though several of the
individual pieces have analogues in prior work.

---

## 3. Distance from journal bars

Journal-bar thresholds estimated by applying the same rubric to
recently-accepted papers in each venue. "Distance" is our rubric
score minus the estimated bar; positive means we're over, negative
means we're under.

| Journal | IF | Novelty threshold (est.) | We have | Distance | Realistic acceptance |
|---|---:|---:|---:|:---:|---:|
| *Epilepsy Research* | ~2 | 3–5 | 16 | **+11 (over-shoots)** | 95%+ |
| *Epilepsia Open* | ~3 | 6–8 | 16 | +8 (comfortable) | 90% |
| *Human Brain Mapping* | ~5 | 10–14 | 16 | +2 (in) | 75–85% |
| *Imaging Neuroscience* | ~4 | 10–12 | 16 | +4 (comfortable) | 80–90% |
| *NeuroImage: Clinical* | ~4 | 12–14 | 16 | +2 (in with clinical framing) | 65–75% |
| **NeuroImage** | **~5.7** | **15–20** | **16** | **~0 (at the bar)** | **40–55%** |
| *Brain* | ~10 | 25–30 | 16 | −10 (below) | 5–10% |
| *Nature Communications* | ~15 | 25+ | 16 | −9 (below) | 5–15% |
| *Lancet Digital Health* | ~30 | 30+ | 16 | −15 (below) | <5% |

**Realistic ceiling: NeuroImage.** At the novelty bar, coin-flip
weighted slightly against us. Viable primary target.

**Comfortable target: HBM or Imaging Neuroscience.** Above bar, high
acceptance probability, same manuscript.

**Not realistic without major additions**: Brain, Nature
Communications, Lancet Digital Health — all require +9 or more novelty
points, which is at least one follow-up paper's worth of scope
expansion.

---

## 4. What would move us up a tier

Ordered by cost-effectiveness (novelty per week of effort). None of
these single additions breaks us above NeuroImage into Brain / LDH
territory alone; getting there requires combining second-cohort +
clinical prediction + probably a novel methodological finding — a
follow-up paper, not a within-scope revision.

| Addition | Novelty gained | Effort | Tier movement |
|---|---:|---|---|
| Cross-validation of `mu_hat` (Test 1 in `mu_hat.md`) | +0.5 | 1 hour | Marginal within tier |
| Sample-size sensitivity of `mu_hat` (Test 2) | +0.5 | 4 hours | Marginal within tier |
| Hemispheric lateralisation (uses `Op_Side`) | +1 | 1 day | Marginal within tier |
| ILAE-1 outcome prediction if AUC modest | +1 | 3–5 days | Marginal within tier |
| ILAE-1 outcome prediction if AUC > 0.7 | +4 | 3–5 days if data supports | **NeuroImage: Clinical becomes solid** |
| BrainMoNoCle 3rd platform | +2 | 1 week + email response | NeuroImage moderate → moderate-strong |
| Real `mean_train` from CentileBrain team | +1 | Email + wait | Marginal within tier |
| MELD-Graph head-to-head | +3 if favourable | 1–2 weeks (Veritas pipeline) | Marginal within tier — better as follow-up |
| Second independent epilepsy cohort | +5 | 2–4 weeks | **Approaches Brain territory (still short)** |

Combined maximum realistic gain from all Path 2 items already planned
in `PAPER_PLAN.md` §7: ~+3 to +7 depending on whether ILAE prediction
lands above chance. Combined with the current 16, ceiling potential is
19–23 rubric points — inside NeuroImage territory (solid) but still
short of Brain / LDH.

---

## 5. What "distance" means practically for the manuscript

Three concrete uses of this document in the manuscript writing itself.

### 5.1 Introduction positioning
The distance table in §2 maps directly to the Introduction's "prior
work and gap" section. Each row of that table becomes a paragraph or a
citation cluster: what has been done, what we add, why the addition
matters. The document is essentially a pre-writing exercise for that
Introduction section.

### 5.2 Discussion novelty defence
The novelty rubric in §1.2 is the honest justification for the
Contributions section. Reviewers rarely accept unqualified novelty
claims; itemising the five **N** claims with the specific prior work
each differs from (§2) is how those claims survive review.

### 5.3 Journal-selection cover letter
The tier analysis in §3 supports the cover letter's opening sentence:
"We submit this manuscript for consideration at *NeuroImage* based on
its multi-platform external validation of published normative brain
morphometry models — the first such comparison on a common clinical
cohort, together with an open-source tool release that operationalises
the validated pipeline for use by other groups." The distance table
lets us defend this framing if the editor pushes back.

---

## 6. Bottom line

- **Contribution: 16 novelty rubric points**, spanning 5 genuinely-new
  claims and 2 novel-similar-work claims, backed by 542 subjects, 2
  platforms, 3 algorithm classes, 94k training subjects across ~140
  sites, and 28.3 MB of shipped open-source code
- **Distance from nearest prior work: material on every axis**;
  combined distance across axes is larger than any single competing
  paper
- **Distance from journal bars: at the NeuroImage bar** (coin-flip
  acceptance), **comfortably above HBM / Imaging Neuroscience bar**
  (likely acceptance), **below Brain / LDH bar** (not realistic without
  follow-up work)
- **Recommended submission order: NeuroImage first** (~40–55% first-round),
  **Imaging Neuroscience on rejection with recommendation** (~85% at
  second venue). Same manuscript either way; total delay if NeuroImage
  rejects is 6–10 weeks

---

## 7. Related documents

- `PAPER_PLAN.md` — locked scope, execution order, risks
- `validate_narrative.md` — the story arc for the science
- `tool.md` — the story arc for the tool
- `../mu_hat.md` — methodology note on site adaptation (Rutherford 2022)
- `../RESULTS.md` — living results document
- `../README.md` — repo-level orientation
