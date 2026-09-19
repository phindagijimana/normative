# Paper plan — CentileBrain × IDEAS validation

This document captures the narrative, novelty claims, contributions, and
journal-target analysis for the manuscript-in-progress. It is a living
document: update as the scope changes (adding platforms, cohorts,
analyses).

---

## 1. Current status vs realistic scenarios

### What is done on disk today
- **1 platform, 2 algorithms**: CentileBrain-MFP and CentileBrain-GAMLSS
- 1 cohort: IDEAS (442 focal-epilepsy patients + 100 healthy controls, UK
  single-site)
- 4 validation tasks: calibration, convergence, classification, resection
  concordance
- Full documentation: `README.md`, `RESULTS.md`, `mu_hat.md`, `SETUP.md`

### Confirmed scope (locked, aiming for NeuroImage): 2 platforms, 3 algorithm classes, 2 training cohorts, + tool as co-contribution

The paper will target this locked scope:

**Scientific validation** (Contributions #1–5):
- CentileBrain-MFP (37,407-subject training set)
- CentileBrain-GAMLSS (37,407-subject training set)
- PCN Toolkit-Bayesian (57,000+ subject training set)

**Tool release as co-equal contribution** (Contribution #6, new):
- `normreport` (working name) — CLI + container that wraps all three
  backends, produces a per-patient PDF report with cross-backend
  consensus/disagreement flagging, deployable in credentialed clinical
  pipelines. Ships open-source with the manuscript. See
  `~/Documents/Normative/tool_design/ARCHITECTURE.md`.

This gives us 3 algorithm classes across 2 platforms + 2 training cohorts
+ a genuinely novel tool release — the strongest package achievable
without external dependencies (BrainMoNoCle held in reserve).

**Rationale for Option A (tool as co-contribution):**
- Only lever we control that meaningfully improves NeuroImage odds
  (moves the tier ceiling from stretch to moderate)
- Tool has real novelty independent of the validation science (first
  offline multi-backend normative report generator; first cross-backend
  consensus flagging)
- Aligns with URMC's operational need (Veritas platform integration)
- Fits Philbert's publication targets (JOSS / Software Impacts /
  SoftwareX already on the strategic radar, per project memory)

### URMC data — not on paper critical path

URMC healthy controls and URMC patients are **required for tool
deployment at URMC** but **not required for the paper**. The paper's
scientific validation rests entirely on the IDEAS cohort (442 patients
+ 100 controls). The tool ships with IDEAS-controls-2025 as the default
reference cohort; URMC-scanner-specific `mu_hat` adaptation happens as
a post-paper deployment step (Version 1.1 of the tool, part of the
Veritas rollout).

Why URMC data does not go into this paper:
- The paper's four findings (calibration, convergence, classification,
  resection concordance) all rest on IDEAS's clinical data (patients +
  outcomes + resection masks). URMC controls alone would replicate only
  the calibration finding, not the clinical ones — modest paper
  strengthening for meaningful additional work.
- Time to acquire even retrospective URMC controls (~1–3 weeks) is
  comparable to the tool's remaining critical-path work. Sequentially
  it would push submission by that amount; in parallel it competes for
  the same operational bandwidth as tool packaging.
- URMC data can be added post-submission as a v1.1 tool release
  demonstrating operational readiness, and cited from any follow-up
  paper without penalty.

### Honest acceptance-probability realism

NeuroImage under this scope is a **moderate acceptance probability
target** — realistically 40–50% at first submission, higher on revision.
Imaging Neuroscience is the comfortable backup (~85% probability) with
essentially the same manuscript. Rejection at NeuroImage with a "send
elsewhere" verdict is a normal outcome that maps cleanly to Imaging
Neuroscience as the second-venue submission.

### Planned next additions (to complete the locked scope)
- **PCN Toolkit** (hierarchical Bayesian regression) — 3–5 days of work
- Cross-validation of `mu_hat`, hemispheric lateralization analysis, ILAE-1
  seizure-freedom outcome prediction — ~1 week

### Held in reserve (not in the current paper; may be added later)
- **BrainMoNoCle backend** — email draft is complete at
  `tool_design/email_1_cnnp_gamlss.md`, kept ready. Would upgrade scope
  from 2 platforms to 3 (see §4 abstract V2). Not sent because it adds
  external timeline risk and the paper is defensible without it. Trigger
  to send: opportunity for a follow-up paper, unsolicited response from
  CNNP, or a decision to invest an additional 3–4 weeks for a stronger
  NeuroImage bid.
- **CentileBrain `mean_train` supplementary comparison** — email draft
  at `tool_design/email_2_centilebrain_mean_train.md`, kept ready. Would
  add one supplementary section quantifying how well `mu_hat` recovers
  the true training means. Not sent because the paper is fully
  defensible without it. Trigger to send: reviewer requests, or we
  decide to add depth in a Discussion section.

### Not planned in this manuscript
- Second independent epilepsy cohort — biggest lift, potentially +2–4
  weeks; possibly a follow-up paper
- ComBat-GAM full comparison (versus `mu_hat`) — nice-to-have supplementary
- MELD-Graph head-to-head — likely a separate paper via Veritas

---

## 2. Platform × algorithm matrix — why a literal 3×3 isn't achievable

### 2.1 What a literal 3×3 would mean

A full factorial design would be: 3 platforms (CentileBrain,
BrainMoNoCle, PCN Toolkit) × 3 algorithm classes (fractional polynomial
regression, GAMLSS-LMS distributional modelling, Bayesian regression)
= 9 cells. Each cell would be a pre-trained model consisting of that
specific platform's implementation of that specific algorithm class,
fitted on that platform's specific training cohort.

### 2.2 Why we can only populate 4 of the 9 cells

Normative-modelling platforms are not modular kits. Each platform ships
one or two specific algorithm implementations fitted on one specific
training cohort. What's actually published looks like this:

|  | Fractional polynomial (MFP) | GAMLSS-LMS | Bayesian (HBR / WBLR) |
|---|:---:|:---:|:---:|
| **CentileBrain** (37,407 subjects) | ✅ Published | ✅ Published | ❌ Not published |
| **BrainMoNoCle** (3,276 subjects) | ❌ Not published | ✅ Published (in Shiny app; models blocked on CNNP email) | ❌ Not published |
| **PCN Toolkit** (57,000+ subjects) | ❌ Not published | ❌ Not published | ✅ Published |

Only 4 of the 9 cells have distributed model files. The other 5 do not
exist as public artefacts.

### 2.3 What it would take to fill the missing 5 cells

Every empty cell requires **re-training a normative model** from raw
data:

1. **CentileBrain-Bayesian** — train HBR/WBLR on the CentileBrain 37k
   cohort. Requires access to their pooled raw data (not fully public —
   many contributing sites impose access restrictions).
2. **BrainMoNoCle-MFP** — train MFP on the BrainMoNoCle 3.3k cohort.
   Requires their raw data (not distributed; several sub-cohorts are
   under UK research-only agreements).
3. **BrainMoNoCle-Bayesian** — same access issue.
4. **PCN Toolkit-MFP** — train MFP on the PCN 57k cohort. UKB data is
   accessible under application, but a full re-training on the combined
   cohort is a substantial effort.
5. **PCN Toolkit-GAMLSS** — same access issue.

Each of these missing cells is essentially a methods paper on its own —
Ge et al. (2024) *is* the process of fitting eight algorithm classes to
the CentileBrain 37k cohort and reporting the comparison; that's one
full paper for one row of the matrix.

**Our paper's scope is external validation of what these platforms
actually distribute, not re-implementing them.** The distinction
matters: external validation is a well-understood scientific activity
publishable in a validation-focused venue (Imaging Neuroscience,
NeuroImage). Re-training + comparing algorithms on new cohorts is a
different scientific activity — the CentileBrain 2024 paper is exactly
that, and it took a large multi-site collaboration to execute.

### 2.4 The realistic best case: 4 model instances

Filling the 4 achievable cells gives us this set of model instances,
each of which we can score IDEAS with directly using publicly-
distributed model files:

| # | Model instance | Algorithm class | Training N | Platform group | Status |
|---|---|---|---:|---|:---:|
| 1 | CentileBrain-MFP | Fractional polynomial regression | 37,407 | UBC / Mount Sinai (Ge/Frangou) | ✅ Working |
| 2 | CentileBrain-GAMLSS | LMS distributional modelling (BCCGo / BCPEo / BCTo / NO) | 37,407 | UBC / Mount Sinai (Ge/Frangou) | ✅ Working |
| 3 | BrainMoNoCle-GAMLSS | LMS distributional modelling (GAMLSS) | 3,276 | Newcastle CNNP (Little/Wang) | ❓ Blocked on email |
| 4 | PCN Toolkit-Bayesian | Hierarchical Bayesian / warped Bayesian linear regression | 57,000+ | Donders (Marquand/Rutherford) | ⏳ 3–5 days work |

Four model instances spanning three axes:

- **3 platforms** — three independent research groups, three different
  distribution formats (R Shiny app, R `.rds` files, Python
  `pcntoolkit`).
- **3 algorithm classes** — three mathematically distinct model families:
  frequentist mean regression with fractional-polynomial covariates,
  distributional modelling via LMS families with penalised splines, and
  Bayesian regression with warping and hierarchical priors.
- **3 training cohorts** — 3,276 vs 37,407 vs 57,000+ subjects, from
  distinct site compositions (BrainMoNoCle is UK-heavy, CentileBrain is
  Europe/Australia/North America mix, PCN Toolkit is UK-Biobank-heavy).
  Some overlap is likely — all three groups use UK Biobank and HCP as
  training sources — so "3 independent cohorts" is a slight
  simplification. **We will check overlap explicitly in the Methods
  section and disclose the extent of any shared training subjects.**

### 2.5 Why the 4-cell design is scientifically stronger than it looks

A full 3×3 factorial would in principle give clean separation of platform,
algorithm, and cohort effects — but only if each cell were fitted
identically, which is not the case in the field today. Our 4-cell design
enables three specific comparisons that a naive 3×3 would not
necessarily improve on, because the comparisons already isolate specific
sources of variation:

| Comparison | What varies | What is held constant | What we learn |
|---|---|---|---|
| CentileBrain-MFP vs CentileBrain-GAMLSS | Algorithm class | Platform, training cohort, site-adaptation procedure | Effect of algorithm choice, holding everything else fixed |
| CentileBrain-GAMLSS vs BrainMoNoCle-GAMLSS | Training cohort (37k vs 3.3k), platform, distribution format | Algorithm class (both GAMLSS) | Effect of training cohort + platform, holding algorithm family constant |
| CentileBrain (either) vs PCN Toolkit | Platform, algorithm class, training cohort — all combined | Nothing | Combined cross-platform robustness — the "does normative modelling as a whole generalise?" question |
| All 3 platforms pooled vs any single platform | Platform diversity | Everything else | Whether findings are platform-specific or platform-general |

The **CentileBrain-GAMLSS vs BrainMoNoCle-GAMLSS** comparison is
particularly informative. Both use the same LMS algorithm family; the
only real difference is training-cohort size and composition. If they
give matching results on IDEAS, that's direct evidence that the
CentileBrain team's 37k-subject reference is not necessary for
IDEAS-quality results — a smaller local cohort (3.3k) is enough. If
they disagree, we've identified a genuine training-scale effect.

### 2.6 What we cannot claim from this design (honest limitations)

Being explicit about what the 4-cell design does not permit:

- We cannot say "MFP is universally better/worse than GAMLSS" — MFP
  appears in only one platform, so any performance difference between
  MFP and other algorithms is confounded with platform effects for
  cross-platform comparisons.
- We cannot say "larger training cohorts always give better calibration"
  — we don't have GAMLSS on 57k or MFP on 3.3k, so cohort-size effects
  are only cleanly testable within-algorithm (CentileBrain-GAMLSS 37k vs
  BrainMoNoCle-GAMLSS 3.3k).
- We cannot say "the Bayesian approach is unique to PCN Toolkit" —
  Bayesian regression is available in principle in other libraries; we
  simply have not evaluated it in another platform on this cohort.
- We cannot cleanly separate platform-implementation effects from
  algorithm effects for cross-platform comparisons (the PCN Toolkit
  Bayesian model differs from CentileBrain's MFP on three axes at once).

**But we can say:**

- All findings we test replicate across 3 algorithm classes.
- All findings replicate across 3 published platforms from independent
  research groups.
- Findings replicate across 2 independent GAMLSS implementations trained
  on distinct cohorts (a specific within-algorithm robustness test).
- The joint claim is stronger than any single-platform or single-
  algorithm result — a reviewer arguing "maybe this is a CentileBrain-
  specific artefact" cannot be sustained.

### 2.7 Realistic completion targets — what shapes the paper

Depending on which of the 4 cells we complete, the paper narrative
scales:

- **Baseline (guaranteed with ~3–5 days work)**: Cells 1, 2, 4 →
  2 platforms, 3 algorithm classes, 2 independent training cohorts →
  abstract paragraph V1 in Section 4.
- **Best case (guaranteed if CNNP shares models)**: Cells 1, 2, 3, 4 →
  3 platforms, 3 algorithm classes, 3 training cohorts, 4 model
  instances → abstract paragraph V2 in Section 4.
- **Fallback (if PCN Toolkit integration fails)**: Cells 1, 2 → 1
  platform, 2 algorithms → abstract paragraph V3.

**The 4-cell "3 platforms + 4 model instances + 3 algorithm classes + 3
training cohorts" is the strongest multi-platform triangulation we can
publish** given the current state of what these platforms distribute
and what is scientifically feasible without a re-training effort.

---

## 3. Journal target analysis

### Realistic tier ceilings under each scenario

| Scenario | Realistic ceiling | Comfortable target |
|---|---|---|
| Where we are (1 platform, 2 algorithms, no tool) | HBM / Imaging Neuroscience | HBM / Imaging Neuroscience |
| + PCN Toolkit alone (2 platforms, 3 algorithm classes) | NeuroImage (stretch) | Imaging Neuroscience |
| **✅ LOCKED SCOPE: + PCN Toolkit + tool release (Option A)** | **NeuroImage (moderate)** | **Imaging Neuroscience** |
| Reserved: + BrainMoNoCle (3 platforms + tool) | **NeuroImage (moderate-strong)** | NeuroImage |
| Reserved: + second cohort (3 platforms + tool + 2 cohorts) | **NeuroImage (solid)** | NeuroImage |
| Reserved: + clinical outcome prediction (ILAE-1 AUC > 0.7) | *NeuroImage: Clinical / Lancet Digital Health (stretch)* | NeuroImage |

### Why the ceiling caps at NeuroImage even at 3 platforms

The single-cohort limitation is the binding constraint for Nature-tier
journals. Multi-platform triangulation rules out
platform-specific artefacts, but does not address:
- Site / scanner generalisability (one UK 3T Prisma)
- Population generalisability (predominantly white British)
- Disease-cohort generalisability (one aetiology mix, one centre's
  surgical selection criteria)

To break above NeuroImage:
- **Lancet Digital Health** (IF ~30): needs either a novel clinical claim
  we can actually defend (our current negative Task 7 doesn't provide
  this) or multi-cohort demonstration of clinical utility.
- **Brain** (IF ~10): needs much stronger resection concordance (ρ > 0.3)
  or a mechanistic biological finding.
- **Nature Communications** (IF ~15): requires either a genuinely novel
  methodological advance (our work is validation, not new methods) or a
  breakthrough clinical finding backed by multi-cohort evidence.

### Journal shortlist with reasoning

| Journal | IF | Fit | Why |
|---|---:|:---:|---|
| **NeuroImage** | ~5.7 | Stretch–solid depending on scope | Top general neuroimaging venue; publishes multi-platform validation |
| **Imaging Neuroscience** (MIT) | ~4 | **Comfortable** | Simpson 2025 IDEAS resection paper here; validation-friendly |
| **Human Brain Mapping** | ~4–5 | Comfortable | Yu 2024 BrainAGE paper here; publishes normative-modelling validations |
| **NeuroImage: Clinical** | ~4 | Comfortable if clinical framing tightened | Clinical translation angle |
| **Epilepsia Open** | ~3 | Comfortable | Leverages IDEAS-audience overlap |
| **Lancet Digital Health** | ~30 | Not realistic without expansion | Where CentileBrain published; needs multi-cohort clinical claim |
| **Brain** | ~10 | Not realistic | Needs stronger clinical / mechanistic finding |

---

## 4. Ready-to-use abstract paragraphs

Multiple versions depending on final scope. Pick the one matching what we
actually complete.

### V1 — Baseline (guaranteed): 2 platforms, 3 algorithm classes

> External validation of published normative brain-morphometry models has
> to date been confined to individual platforms. Here we validate **two
> independent normative-modelling platforms — CentileBrain (Ge et al.
> 2024, MFPR and GAMLSS variants trained on 37,407 individuals) and the
> PCN Toolkit lifespan models (Rutherford et al. 2022, hierarchical
> Bayesian regression trained on 57,000+ individuals)** — on 442 focal-
> epilepsy patients and 100 healthy controls from the IDEAS UK cohort
> (Taylor et al. 2025). Applying each platform via its authors'
> recommended site-adaptation procedure, we show that: **(i)** all three
> model instances produce well-calibrated Z-scores on the 100 IDEAS
> healthy controls (per-region SD 1.00–1.09 across 150 Desikan-Killiany +
> Aseg regions); **(ii)** platform-derived Z-scores agree with IDEAS's
> own independent ComBat-harmonised Z-scores at Pearson r ≈ 0.83–0.97
> across virtually every region; **(iii)** contrary to the CentileBrain
> team's original HCP-EP psychosis finding (Z-scores AUC 0.63 vs raw AUC
> 0.49), normative Z-scores under any of the three algorithms give no
> advantage over raw morphometry for classifying focal epilepsy vs
> healthy control (AUC 0.79 vs 0.79); **(iv)** preop Z-scores show a
> weak but statistically-real concordance with the surgically-resected
> region (Spearman ρ ≈ 0.07–0.08, 13× the permutation null), consistent
> across algorithms and with a modest seizure-freedom-outcome gradient.
> Convergence across platforms with different algorithms, training
> cohorts, and site-adaptation implementations demonstrates that these
> findings reflect general properties of the normative-modelling
> paradigm applied to focal epilepsy, not artefacts of any single
> platform's design choices.

### V2 — Best case: 3 platforms, 3 algorithm classes (adds BrainMoNoCle)

Same skeleton as V1 with the additional platform substituted in:

> ... we validate **three independent normative-modelling platforms —
> CentileBrain (Ge et al. 2024, MFPR and GAMLSS variants), BrainMoNoCle
> (Little et al. 2025, GAMLSS on a distinct 3,276-subject reference),
> and the PCN Toolkit lifespan models (Rutherford et al. 2022,
> hierarchical Bayesian regression on 57,000 subjects)** — on 442 focal-
> epilepsy patients ...

with findings (i)–(iv) covering all four model instances instead of
three.

### V3 — Fallback (if PCN Toolkit integration fails or is deferred)

Current state, honestly framed:

> ... we validate the two ships algorithms of the CentileBrain platform
> (MFPR and GAMLSS, trained on 37,407 healthy individuals; Ge et al.
> 2024) on 442 focal-epilepsy patients and 100 healthy controls from the
> IDEAS UK cohort. Findings replicate across both algorithms, showing
> that ... [same four findings, framed as within-platform algorithm
> triangulation] ...

---

## 5. Novelty claims

Ranked from strongest to most modest. Every claim below is defensible on
what we already have or will complete.

### 1. First multi-platform external validation of published normative brain-morphometry models
Every existing external validation we identified (including Ge's own
2026 PNAS ethnoracial paper) uses a single platform. Multi-platform
validation on the same cohort is genuinely new. This is the paper's
central methodological contribution and NeuroImage's likely hook.

### 2. First application of any lifespan normative model to a focal-epilepsy surgical cohort with resection ground truth
The IDEAS cohort was released in 2025; resection percentages were
released alongside (Simpson et al. 2025). No prior work has combined
normative morphometry with the IDEAS resection data at scale (N = 430
surgical cases). Adding ILAE-1 outcome stratification makes this a
novel clinical-imaging finding.

### 3. Scoping the CentileBrain 2024 clinical-utility claim
Ge et al. reported that Z-scores dramatically beat raw morphometry for
HCP-EP psychosis classification (AUC 0.63 vs 0.49). We show that this
advantage does not generalise to focal epilepsy under any of the tested
normative-modelling implementations (AUC ~0.80 across all algorithms).
Substantive negative finding worth publishing, and it's stronger
because we can rule out the "algorithm artefact" objection.

### 4. Documented offline-scoring recipe for the CentileBrain MFP models
The `mu_hat` site-adaptation procedure (per Rutherford 2022) applied
to CentileBrain, plus the `meanarea = (L+R)/2` gotcha, plus the naming-
convention bridge from IDEAS to the CentileBrain templates — none of
this was documented by the CentileBrain team. Any subsequent external
user will benefit from our published recipe. Publishable as a methods
contribution.

### 5. Convergence between the 37k-subject external CentileBrain reference and IDEAS's local 100-subject ComBat approach
The finding that median r ≈ 0.83 (MFP) or 0.96 (GAMLSS) between two
independently-derived Z-score approaches is genuinely new. It says
something quantitative about how similar a large-external-cohort
approach and a small-local-cohort ComBat approach are for producing
per-subject deviations.

### 6. First offline multi-backend normative brain-morphometry report generator (tool release)
`normreport` (working name): a CLI + containerised tool that wraps three
normative-modelling backends (CentileBrain-MFP, CentileBrain-GAMLSS, PCN
Toolkit-Bayesian) in a single pipeline, produces a per-patient PDF
report with cross-backend consensus/disagreement flagging, and is
deployable inside credentialed clinical-research pipelines with an
audit trail. Existing tools (BrainMoNoCle web app, CentileBrain web app,
raw PCN Toolkit library) are all single-backend and mostly web-only.
The tool bridges cortical + subcortical morphometry (BrainMoNoCle is
cortical only) and implements the Rutherford 2022 site-adaptation
procedure per-backend with a disclosed reference cohort. Open-source
release accompanies the manuscript.

---

## 6. Contributions section (as it would appear in the paper)

> **Contributions**
>
> 1. First multi-platform external validation of published normative
>    brain-morphometry models, using two implementations of the
>    CentileBrain platform (MFPR and GAMLSS), the PCN Toolkit lifespan
>    models, and (where available) the BrainMoNoCle platform, on the
>    same clinical cohort.
> 2. First systematic test of normative deviation as a preoperative
>    surgical resection concordance signal in focal epilepsy (N = 430
>    surgical cases), stratified by post-operative ILAE-1 seizure-
>    freedom outcome.
> 3. Empirical demonstration that the CentileBrain team's original
>    clinical-utility claim (normative Z-scores outperform raw
>    morphometry for HCP-EP psychosis classification) does not
>    generalise to focal epilepsy vs. control classification under any
>    of the tested algorithms.
> 4. A documented offline-scoring recipe for the CentileBrain MFP
>    models, including the site-adaptation procedure required by the
>    Rutherford et al. 2022 protocol, the correct handling of
>    hemispheric-mean covariates, and column-naming reconciliation —
>    all issues encountered when applying the publicly-distributed
>    models outside the vendor web app.
> 5. Public release of the pre-computed per-subject Z-scores from all
>    tested algorithms on the IDEAS cohort, enabling future comparisons
>    and follow-up studies without re-running the pipeline.
> 6. Release of `normreport`, an open-source CLI + container tool that
>    wraps all three tested backends (CentileBrain-MFP, CentileBrain-
>    GAMLSS, PCN Toolkit-Bayesian), produces per-patient PDF reports
>    with cross-backend consensus/disagreement flagging, and is
>    deployable inside credentialed clinical-research pipelines with an
>    audit trail. This is the first offline multi-backend normative
>    brain-morphometry report generator; existing tools are single-
>    backend and mostly web-only.

---

## 7. What to do next — prioritised

### Confirmed execution order (locked scope: 2 platforms + tool)

The tool build is on the paper's critical path under Option A. Some
analysis steps (cross-validation, hemispheric lateralisation) can run
in parallel with tool work.

| Step | Effort | Adds to paper |
|---|---|---|
| 1. **PCN Toolkit integration** (analysis) | 3–5 days | Completes the multi-platform scientific triangulation |
| 2. **Tool skeleton** — CLI + backend registry + 3-backend wrappers | 1–2 weeks | Foundation for the tool contribution |
| 3. **PDF report generator** — layout, brain glass-plot, consensus-flag narrative | 1 week | The visible artefact reviewers will see in a paper figure |
| 4. Cross-validation of `mu_hat` (analysis) | 1 h | Removes the "control mean = 0 by construction" tautology |
| 5. Hemispheric lateralisation analysis (analysis) | 1 day | Genuine localisation claim, epilepsy-audience relevance |
| 6. ILAE-1 outcome prediction (analysis) | 3–5 days | Turns Task 8 from concordance into prediction |
| 7. Sample-size sensitivity of `mu_hat` (analysis) | 4 h | Operational recommendation for tool deployment (used in tool defaults) |
| 8. **Tool packaging** — Docker/Singularity, tests, docs, examples | ~1 week | Release-ready deliverable |
| 9. **Tool release engineering** — GitHub repo, versioning, DOI (via Zenodo), citation file | 3 days | Citable tool artefact |
| 10. Draft manuscript | 4–6 weeks | Actual paper (2–3 weeks of overlap with steps 8–9) |

**Total effort: ~4 weeks analysis + tool build. Total to submission:
~10–12 weeks.** The +3–4 weeks over the analysis-only path buys the
tool contribution (Contribution #6) and the NeuroImage-moderate ceiling.

Outreach emails (both drafts held in reserve, not sent — see §1). Send
only if scope shifts.

### Reserved paths (available if scope-change opportunity arises)

- **Send `email_1_cnnp_gamlss.md` to CNNP** → if they share models,
  add BrainMoNoCle backend (~1 week integration), upgrade V1 → V2
  abstract, move NeuroImage from stretch to moderate.
- **Send `email_2_centilebrain_mean_train.md` to Ge/Frangou** → if
  they share training means, add supplementary comparison section
  (~2 days), removes the last methodological caveat.
- **Add a second independent epilepsy cohort** → 2–4 weeks on Slurm,
  moves NeuroImage from stretch to solid; probably better as a
  follow-up paper unless bandwidth allows.

---

## 8. Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| PCN Toolkit's training cohort overlaps substantially with CentileBrain's (both use UK Biobank, HCP, etc.) — "platform independence" claim weakens | Medium — softens the multi-platform narrative | Check overlap in the model documentation before committing; if > 30 % overlap, disclose in Methods and frame as "different algorithm implementations of overlapping training data" |
| BrainMoNoCle team declines to share models | Small — we have V1 fallback | V1 narrative is fine; add one sentence in Discussion about the ask + polite decline (or non-response) |
| Cross-validation of `mu_hat` reveals held-out control SDs substantially > 1.0 | Medium — weakens Task 5 calibration claim | Report honestly; note that this is a real property of the adaptation procedure at N = 100 controls; recommend larger reference cohorts for clinical deployment |
| ILAE-1 outcome prediction achieves near-chance AUC | Small — negative finding is still informative | Report; add to the "normative deviations are weak surgical planners" narrative |
| A NeuroImage reviewer insists on a second cohort as a condition of acceptance | High — could delay by 2–4 weeks or force downgrade to Imaging Neuroscience | Pre-empt with Discussion paragraph on why multi-platform partially substitutes for multi-cohort; be prepared to add cohort in revision |
| A reviewer flags the age-binning imputation as a serious methodological concern | Small — well-defended in `feedback_ideas_age_binned.md` | Cite the CNNP release constraint; include a sensitivity supplement using uniform sampling within bins |
| Tool MVP slips past 4-week estimate, delaying paper submission | Medium — extends submission timeline by whatever the tool slip is | Pre-scope tool features aggressively: MVP = CLI + PDF + 3 backends + Docker only. Defer web UI, Veritas integration, extra visualisations to post-submission releases |
| Tool release attracts scrutiny (bugs, missing edge cases) after publication | Small — normal open-source lifecycle | Version 1.0 must have real tests + explicit "for research use only" disclaimer; issue tracker on GitHub with response SLA |

---

## 9. Alternative paths — for context

Documented here so we know what we're trading off.

### Path 1 — Solid Imaging Neuroscience (2–3 weeks work)
Add cross-validation, sample-size sensitivity, hemispheric analysis, and
pathology stratification. Skip PCN Toolkit. Realistic target: Imaging
Neuroscience or HBM. Higher acceptance probability (~80%+), lower
prestige.

### Path 2 — Stretch for NeuroImage (6–8 weeks work)
Add PCN Toolkit + ILAE outcome + cross-validation + lateralization.
Realistic target: NeuroImage stretch, Imaging Neuroscience solid backup.

### Path 2A — NeuroImage-moderate via tool co-contribution (10–12 weeks work) ← **current plan**
Path 2 + `normreport` tool release as first-class contribution (see §5
Novelty #6, §6 Contribution #6, §7 execution steps 2, 3, 8, 9).
Realistic target: NeuroImage moderate, Imaging Neuroscience solid
backup. The tool is the single strongest lever we control that lifts
NeuroImage odds without external dependencies (BrainMoNoCle) or
massive additional data effort (second cohort).

### Path 3 — Full NeuroImage-tier package (10–12 weeks work)
Everything in Path 2 plus a second cohort. Realistic target: NeuroImage
with real acceptance chance. Real investment.

### Path 4 — Break above NeuroImage (6+ months)
Would need either: multi-cohort + multi-disease validation (NeuroImage:
Clinical / LDH); or a novel clinical breakthrough with strong effect
sizes (Brain / Lancet); or a genuinely new method (Nature Comms). None
are on the current roadmap.

---

## 10. Related design documents in this project

- `differentiation.md` — quantitative contribution / novelty / distance / journal-tier analysis (sibling of this file)
- `validate_narrative.md` — the paper's story arc (Introduction + Discussion drafting scaffold)
- `tool.md` — the tool's story arc (README + tool-paper drafting scaffold)
- `~/Documents/Normative/RESULTS.md` — the results narrative (living)
- `~/Documents/Normative/mu_hat.md` — methodology note on site adaptation
- `~/Documents/Normative/tool_design/ARCHITECTURE.md` — per-patient tool design (`normreport`)
- `~/Documents/Normative/tool_design/email_1_cnnp_gamlss.md` — BrainMoNoCle outreach draft (held in reserve)
- `~/Documents/Normative/tool_design/email_2_centilebrain_mean_train.md` — CentileBrain training-means outreach draft (held in reserve)
