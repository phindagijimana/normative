# Narrative — `normreport`, the multi-backend normative brain-morphometry report tool

This document is the tool's story arc: the deployment gap it fills,
what it does, how it's used, what design decisions were made and why,
and where it goes after the paper. It serves as the conceptual
backbone for the tool's README, the paper's tool-related manuscript
sections, and the pitch to prospective users at URMC and beyond.

Working name: `normreport` (open to change before v1.0 release —
see `tool_design/ARCHITECTURE.md` §Naming).

---

## 1. The deployment gap

Normative modelling is a mature research paradigm with mature
distributed models — three groups publish pre-trained normative brain-
morphometry models, together covering tens of thousands of healthy
subjects across the human lifespan. The methodological infrastructure
is in place. The scientific validation infrastructure is not.

What exists today, in tool form, is a two-part gap:

**One part is that the vendor tools are web-based single-backend
services.** BrainMoNoCle runs as a Shiny app on shinyapps.io.
CentileBrain runs as a JavaScript SPA at centilebrain.org. Both are
free, both are usable in a browser, both work well for exploratory
research. Neither can be deployed inside a credentialed clinical-
research pipeline that must run offline, log every prediction against
an audit trail, and satisfy institutional data-governance rules that
forbid uploading identifiable imaging data to a public web service.
For anyone applying normative modelling in a US clinical setting — or
any setting with an HIPAA-equivalent regulatory constraint — the
vendor web tools are structurally unavailable.

**The other part is that the toolkit libraries are not packaged for
per-patient reporting.** The PCN Toolkit (`pcntoolkit`) is the
reference Python implementation for normative modelling; Marquand's
group has released pre-trained lifespan models and documented the
site-adaptation protocol thoroughly. But it is a library, not a
product. Applying it to one patient produces a Python object; there
is no per-patient PDF report, no cross-backend comparison, no
consensus flag, no clinical-tone narrative summary of which regions
are outside the expected range. A researcher can build these on top,
and papers demonstrating that pattern exist — but they are
one-offs, not a shared distributable tool.

Between these two categories sits a gap that no distributed tool
fills: **offline, multi-backend, per-patient PDF report generation
with cross-backend consensus flagging, deployable inside a
credentialed clinical-research pipeline.** That is the gap
`normreport` targets.

## 2. What `normreport` is

`normreport` is an open-source command-line tool that, given one
patient's FreeSurfer output directory + age + sex, runs three
normative-modelling backends in parallel and produces a single
per-patient PDF report showing per-region Z-scores from all three
backends, a cross-backend consensus/disagreement flag per region, and
an auto-generated narrative summary of the most-deviant regions.

The three backends bundled in v1.0 are:

1. **CentileBrain-MFP** — multivariate fractional polynomial
   regression on the 37,407-subject ENIGMA Lifespan reference; the
   CentileBrain team's recommended default algorithm.
2. **CentileBrain-GAMLSS** — LMS distributional modelling on the same
   37,407-subject reference; models the full distribution rather than
   just the mean.
3. **PCN Toolkit-Bayesian** — hierarchical Bayesian regression on the
   57,000+ subject PCN Toolkit lifespan reference; algorithmically
   distinct from the CentileBrain algorithms and trained on a largely
   independent cohort.

A fourth backend slot is reserved in the `NormativeBackend` protocol
for BrainMoNoCle-GAMLSS, held pending an outreach response from the
CNNP lab. The design pattern accommodates the fourth backend as a
drop-in without any user-facing changes.

Every report the tool produces embeds a provenance stamp — backend
versions, reference-cohort identifier, script commit SHA, timestamp,
subject ID hash — so any report is traceable back to exactly the
inputs and models that produced it. This matters both for scientific
reproducibility (a paper that cites a `normreport` output can be
traced back to its exact configuration) and for clinical audit (any
report handed to a clinician is a signed artefact, not a snapshot of
volatile web state).

## 3. Who uses it and how

Three user profiles motivate the design.

**The research validator.** A neuroimaging researcher wants to
reproduce a paper's normative-modelling analysis on their own cohort,
or compare Z-scores across platforms without hand-rolling three
separate scoring pipelines. They run `normreport --patient <fs_dir>
--age <y> --sex <MF> --backend all --output out/` and get a PDF
report per patient plus a machine-readable CSV of per-region Z-scores
from each backend. Batch mode (planned for v1.1) processes a folder
of patients in one call.

**The clinical-research site deploying normative modelling.** A
researcher at an institution like URMC wants to make normative
Z-scores available as one input into their epilepsy surgical
planning workflow, or as a supplementary read for a research-only
imaging protocol. They need the tool to run on their local Slurm
cluster or workstation without any external network calls, to produce
reports that fit into an institutional audit system, and to accept a
local reference cohort so that Z-scores are computed against
scanner-matched healthy controls. `normreport` supplies all three,
with the local reference specified by `--reference /path/to/local/`
and the Rutherford 2022 site-adaptation procedure applied
automatically per-backend.

**The multi-platform robustness auditor.** A clinician or researcher
looking at one patient's Z-score wants to know whether the "abnormal"
flag would replicate under a different modelling choice. The tool's
consensus/disagreement panel — "all three backends flag this region
as |Z| > 2" versus "one backend flags this region but the others do
not" — provides that check natively. This is a genuinely new signal
that neither BrainMoNoCle nor CentileBrain nor PCN Toolkit alone can
offer, because none of them run the alternatives.

The typical use pattern for all three profiles is: preprocess the
patient's T1w through FreeSurfer (existing pipeline at URMC), point
`normreport` at the resulting stats directory, receive a PDF report
in under a minute per patient.

## 4. Design decisions worth naming

Three decisions that shape how the tool behaves and that a user or
reviewer should understand.

**Reference cohort defaults to IDEAS-controls-2025.** The tool ships
with 100 UK Newcastle 3T Siemens Prisma healthy controls (from the
IDEAS release) as the built-in reference cohort. Every report's footer
discloses that this is the reference used, and every report advises
the user to supply a local reference cohort (`--reference`) for
clinical deployment at their own site. Users who cannot supply a
local reference (small clinics, retrospective analyses of historical
data) still get valid Z-scores computed against the IDEAS reference,
with the appropriate disclosure that these are "relative to a UK
Newcastle 3T reference" rather than site-calibrated. Users who can
supply a local reference (≥ 30 healthy controls scanned on the same
scanner and processed through the same FreeSurfer pipeline) get
proper site-adapted Z-scores that behave correctly in a clinical
setting. The default-plus-override pattern lets the tool work
immediately for research but transitions cleanly to clinical
deployment.

**Site adaptation is not optional.** Every backend applies the
Rutherford 2022 site-adaptation offset (`mu_hat`) as a mandatory
step. This is not a knob users can turn off, because doing so
produces Z-scores that are silently mis-calibrated for any site
different from the platform's original training cohort. The
adaptation adds a single per-region additive offset estimated from
the reference cohort — mathematically the same operation every
comparable normative-modelling platform requires at a new site. The
methodology is documented in the project's `mu_hat.md` and cited in
every generated report.

**Consensus flagging is a first-class output.** The report highlights
regions where all backends agree (high-confidence flag) separately
from regions where backends disagree (interpret-with-caution flag).
The rationale is that a Z-score that only one platform flags is
harder to trust than a Z-score three independent platforms flag —
and that this cross-backend information is exactly what
single-platform tools cannot provide by construction. The consensus
rule is transparent: "all three backends |Z| > threshold" for the
high-confidence flag, threshold configurable via a CLI flag with 2.0
as the default. This lets users tune the sensitivity/specificity
trade-off for their setting.

## 5. What v1.0 ships (the paper-release version)

The v1.0 release accompanying the manuscript is deliberately narrow.
Every feature has to justify its presence by supporting the paper's
tool-contribution claim; anything else is deferred.

**In scope for v1.0:**

* CLI (`normreport <patient_dir> --age <y> --sex <MF>`) producing a
  per-region Z-score table + a PDF report from all three bundled
  backends
* IDEAS-controls-2025 as the shipped default reference cohort
* `--reference` flag accepting a local cohort of FreeSurfer stats
* Docker / Singularity container definition files (built and
  published by the user; not required for functional use)
* Unit tests + one golden-file integration test using a demo subject
* Documentation: README, quickstart, one worked example, methods
  attribution to the three platform papers plus Rutherford 2022
* Zenodo DOI for citation in the manuscript
* Explicit "for research use only" disclaimer on every report footer

**Deferred to v1.1+ (post-publication):**

* URMC-scanner-specific `mu_hat` adaptation, done at URMC via
  retrospective control harvest — the first real clinical deployment
* Web UI / Veritas endpoint integration
* Additional report formats (HTML dashboard, JSON API)
* BrainMoNoCle backend if CNNP shares models
* Interactive visualisations (age-trajectory plots, brain glass-plot)
* Batch mode for research-cohort processing
* Additional metric types (cortical folding, sulcal depth) as
  backends add them

The narrow v1.0 scope is not a limitation of ambition — it is a
release-engineering discipline. Every feature that ships in v1.0
must be tested, documented, and stable enough to survive the
attention that comes with a NeuroImage publication. Every feature
that ships later is scoped, prioritised, and released on its own
merits.

## 6. How it fits with existing tools

`normreport` does not compete with BrainMoNoCle, CentileBrain, or PCN
Toolkit — it composes them.

For a researcher choosing between the vendor web apps and
`normreport`, the trade-off is clear: use the web app for a single
quick exploratory analysis when data governance permits uploading
outputs; use `normreport` when either (a) data cannot leave the
institutional perimeter, or (b) cross-backend consensus is
scientifically or clinically desired.

For a researcher choosing between PCN Toolkit and `normreport`, the
trade-off is different: use PCN Toolkit directly if you are doing
methods research on the Bayesian normative-modelling algorithm
itself; use `normreport` if you want a per-patient report that
includes the PCN Toolkit outputs alongside two others.

For a research group considering their tool release strategy,
`normreport` demonstrates a pattern: wrap multiple upstream backends,
add the reporting layer none of them provide individually, distribute
as an offline containerised CLI, cite the upstream tools as
first-class dependencies rather than replacing them. This composition
pattern is generalisable to other neuroimaging tool categories where
the upstream landscape is fragmented.

## 7. Roadmap after the paper

The v1.0 release is the beginning, not the end.

**v1.1 — URMC clinical-research deployment.** Add URMC-scanner-
specific `mu_hat` adaptation using retrospective healthy controls
harvested from URMC's existing IRB-approved neuroimaging datasets.
Ship a URMC-local reference cohort as a second bundled option. This
is the first genuine clinical-research deployment of the tool and
the natural next milestone.

**v1.2 — Veritas platform integration.** Add a thin authenticated
endpoint that wraps the containerised CLI as a service inside the
Veritas clinical-AI biomarker validation platform (currently under
development at URMC). Enables audit-tracked per-patient scoring as
part of the Veritas workflow — see the `project-veritas-atlas`
memory for the full Veritas context.

**v1.3 — Fourth backend if available.** Integrate BrainMoNoCle-GAMLSS
as the fourth backend if the CNNP lab shares their fitted models;
otherwise this slot remains reserved. Upgrading to a four-backend
consensus reduces false positives further and closes the platform-
diversity claim.

**v2.0 — Batch, longitudinal, and non-morphometry extensions.** Batch
processing for research-cohort applications. Longitudinal Z-score
tracking (change in deviation over time). Non-morphometric extensions
if the upstream platforms release them (diffusion, functional,
molecular).

Everything past v1.0 is speculative until it ships. The v1.0
release, however, is fully-scoped, on the manuscript's critical path,
and coherent with the paper's four scientific findings — and that is
what makes it a first-class contribution to the paper rather than a
supplementary code release.
