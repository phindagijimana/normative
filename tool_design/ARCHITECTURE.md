# Per-patient normative brain report — tool architecture

**Working name:** `normreport` (placeholder; see naming discussion at the end).

**One-line pitch.** A CLI + containerised tool that, given one patient's
FreeSurfer stats + age/sex, applies three normative-modelling backends
(CentileBrain-MFP, CentileBrain-GAMLSS, PCN Toolkit-Bayesian) and returns
a per-region Z-score profile + a PDF report showing consensus and
disagreement across backends.

**Scope decision (locked with the paper scope, Option A):** the tool is
**a first-class contribution of the accompanying manuscript** — not a
supplementary code release. See `paper_planning/PAPER_PLAN.md` §5
Novelty #6 and §6 Contribution #6 for the paper-side framing.

The initial release ships **three backends**, mirroring the paper's
2-platform / 3-algorithm scope:

1. `centilebrain_mfp` — wraps `score/score_centilebrain.R`
2. `centilebrain_gamlss` — wraps `score/score_centilebrain_gamlss.R`
3. `pcn_bayesian` — wraps PCN Toolkit's hierarchical Bayesian scoring
   (integration pending)

A **BrainMoNoCle backend slot** is reserved in the design but not
implemented — the `NormativeBackend` protocol accommodates it as a
drop-in fourth backend if the CNNP lab later shares their fitted models
(email draft held in reserve at `email_1_cnnp_gamlss.md`).

## MVP scope for paper submission

Because the tool is on the paper's critical path, the MVP is defined
by what must ship at manuscript submission (not the full vision below).
MVP scope (Version 1.0 for the paper):

* **CLI** (`normreport <patient_dir> --age <y> --sex <MF> -o <outdir>`)
  producing per-region Z-scores from all 3 backends
* **PDF report** — 1–2 pages, per-region table sorted by |Z|,
  consensus/disagreement flag, provenance footer
* **Docker or Singularity container** with all dependencies pinned
* **Reference-cohort handling** — ships IDEAS-controls-2025 as the
  default (documented as UK Newcastle 3T; the same reference used in the
  accompanying paper); accepts a `--reference` flag to point at any
  local cohort. URMC-scanner-specific `mu_hat` adaptation is a
  post-publication v1.1 task, done at URMC as part of the Veritas
  rollout — NOT part of the v1.0 release accompanying the manuscript.
* **GitHub repository** with tests (~10 unit tests + 1 golden-file
  integration test), documentation, and one worked example on a demo
  subject
* **Zenodo DOI** for citation in the manuscript
* **Explicit "for research use only" disclaimer** on every report

Deferred to post-submission releases (Version 1.1+):

* **URMC-scanner-specific `mu_hat` adaptation** — using URMC healthy
  controls acquired via retrospective harvest or prospective IRB, per
  Rutherford 2022 site-adaptation protocol. First real clinical
  deployment step for the tool.
* Web UI / Veritas endpoint integration
* Additional report formats (HTML dashboard, JSON API)
* BrainMoNoCle backend
* Additional visualisations (age-trajectory plots per region, brain
  glass-plot in interactive form)
* Batch mode for research-cohort processing

Rationale for aggressive MVP scoping: tool MVP slip risks delaying the
paper. Version 1.0 must be the smallest coherent release that supports
the paper's contribution claim; everything else is a follow-up.

---

## Design goals

1. **Multi-backend by construction.** Backends are pluggable; the CLI
   picks one or more via a flag. Ships with 3 backends:
   CentileBrain-MFP, CentileBrain-GAMLSS, PCN Toolkit-Bayesian.
   Fourth-backend slot reserved for BrainMoNoCle-GAMLSS.
2. **Deterministic, auditable.** Every report embeds: backend + version,
   reference cohort used, script SHA, timestamp, subject ID hash. Same
   input → identical output.
3. **Runs offline.** No calls to shinyapps.io or centilebrain.org at
   inference time. All models loaded from disk.
4. **Clinical form factor.** CLI first, Docker/Singularity second, thin
   Veritas endpoint third — so the tool can be dropped into a
   credentialed clinical pipeline with an audit trail.
5. **One command per patient.** No manual data munging between steps.

---

## Module layout

```
normreport/
├── normreport/
│   ├── __init__.py
│   ├── cli.py              # entry point: `normreport <patient_dir>`
│   ├── fs_stats.py         # parse FreeSurfer aparc/aseg stats → dict
│   ├── reference.py        # load / cache reference cohorts + mu_hat
│   ├── backends/
│   │   ├── __init__.py            # BackendProtocol + registry
│   │   ├── centilebrain_mfp.py    # wraps score/score_centilebrain.R
│   │   ├── centilebrain_gamlss.py # wraps score/score_centilebrain_gamlss.R
│   │   ├── pcn_bayesian.py        # wraps PCN Toolkit Bayesian scoring
│   │   ├── brainmonocle.py        # (reserved slot; not implemented)
│   │   └── null.py                # trivial baseline (raw Z from cohort)
│   ├── zscore.py           # normalisation + centile math
│   ├── report/
│   │   ├── __init__.py
│   │   ├── layout.py       # A4 page composition
│   │   ├── plots.py        # trajectory + brain glass plot
│   │   ├── narrative.py    # auto text (top-K deviations)
│   │   └── pdf.py          # reportlab / weasyprint renderer
│   └── audit.py            # provenance stamp
├── data/
│   ├── centilebrain_models/     # symlink to ../centilebrain/models/
│   ├── reference_cohorts/
│   │   ├── ideas_controls_2025.parquet   # bundled default (100 subj)
│   │   └── README.md                     # sourcing + provenance
│   └── brain_geometry/          # DK + Aseg surface glyphs for plots
├── tests/
│   ├── test_fs_stats.py
│   ├── test_zscore.py
│   ├── test_backends.py
│   └── golden/                   # frozen expected outputs for CI
│       └── subject_demo_*.json
├── pyproject.toml
├── Dockerfile
├── Singularity.def
└── README.md
```

---

## Backend interface

Every backend implements a small protocol so the CLI can loop over them:

```python
class NormativeBackend(Protocol):
    name: str                 # "centilebrain-mfp-v1.0"
    reference_cohort_id: str  # "ideas-controls-2025"
    regions: list[str]        # canonical DK+Aseg names it covers

    def score(self, subject: SubjectData) -> pd.DataFrame:
        """Return per-region {region, observed, predicted, rmse, z, centile}."""
```

`SubjectData` is a small dataclass carrying age, sex, per-region measurements
in canonical names, and a subject_id hash. Backends are responsible for
their own model loading, offset estimation, and Z-score formula.

CLI:

```bash
normreport /path/to/subject_freesurfer_stats/ \
    --age 34 \
    --sex F \
    --subject-id anon_042 \
    --backend centilebrain,brainmonocle \
    --reference ideas-controls-2025 \
    --output ./reports/anon_042/
```

Outputs:

```
reports/anon_042/
├── anon_042_report.pdf              # A4, 1–2 pages
├── anon_042_zscores.csv             # long-form: backend × region × z
├── anon_042_provenance.json         # backend versions, model hashes, git SHA
└── anon_042_raw.json                # cleaned FreeSurfer parse for debugging
```

---

## Report layout — 1 to 2 A4 pages

Page 1 (always):
```
┌──────────────────────────────────────────────────────────────┐
│  Normative Brain Report — Subject anon_042                   │
│  Age 34.0  •  Sex F  •  Scanned <date>  •  Report 2026-09-18 │
│  Backends: centilebrain-mfp-v1.0, brainmonocle-gamlss-v?     │
│  Reference: ideas-controls-2025 (100 UK, Newcastle 3T)       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Regional Z-scores (sorted by |Z|, top 20 shown)             │
│  ┌──────────────────────────────┬────────┬────────┬────────┐ │
│  │ Region                       │  CB    │  BMC   │ Centile │ │
│  ├──────────────────────────────┼────────┼────────┼────────┤ │
│  │ Left-Hippocampus             │ -2.41  │ -2.28  │  1st   │ │  ← red
│  │ Right-Amygdala               │ -2.12  │ -1.98  │  2nd   │ │  ← red
│  │ lh_entorhinal_thickness      │ -1.87  │ -1.63  │  3rd   │ │  ← yellow
│  │ ...                          │  ...   │  ...   │  ...   │ │
│  └──────────────────────────────┴────────┴────────┴────────┘ │
│                                                              │
│  Glass-brain overlay (DK+Aseg, Z heat-map, lateral + medial) │
│                                                              │
│  Interpretation:                                             │
│  Regions with |Z| > 2 (outside the 95% expected range):      │
│  Left-Hippocampus, Right-Amygdala. Both backends agree on    │
│  direction and magnitude within 0.2 SD.                      │
│                                                              │
│  Backend disagreement > 0.5 SD:                              │
│  rh_transversetemporal_thickness (CB -1.4, BMC +0.1) —       │
│  interpret with caution.                                     │
└──────────────────────────────────────────────────────────────┘
```

Page 2 (optional — `--full` flag):
- Age-trajectory plot for the top-5 deviant regions (backend curve +
  patient's point + 95% CI ribbon).
- Full 150-region table.
- Method summary + citations for each backend used.

---

## Reference-cohort strategy

Three tiers, controlled by `--reference`:

1. **`ideas-controls-2025`** (bundled default) — 100 UK controls we already
   have processed. Ships in `data/reference_cohorts/`. Zero setup.
2. **`--reference /path/to/local/controls/`** — user provides a folder of
   ≥ 20 healthy subjects (FreeSurfer stats + a metadata CSV). Tool
   estimates `mu_hat` from these on first use and caches it. Recommended
   for clinical deployments.
3. **`--reference centilebrain-native`** — reserved for the case where
   the CentileBrain team's actual training means become available (would
   enable scoring without a local reference cohort, at the cost of losing
   the site-adaptation step recommended by Rutherford 2022).

Cache is keyed by `(backend_version, cohort_id, region_set)` so a given
reference is computed once per unique combination.

---

## Positioning vs. existing tools

| Capability | BrainMoNoCle | CentileBrain | `normreport` (this) |
|---|:---:|:---:|:---:|
| Backends | GAMLSS only | MFPR/GAMLSS/LMS | **Multiple, pluggable** |
| Cortical thickness/area/volume | ✓ | ✓ (thick + area) | ✓ (via backends) |
| **Subcortical volume** | ✗ | ✓ | ✓ |
| **Runs offline** | ✗ (Shiny) | Partial | **✓** |
| **PDF / HTML report** | ✓ HTML | ✗ | **✓ PDF** |
| **Backend-disagreement flag** | — | — | **✓** |
| **Resection concordance panel** | ✗ | ✗ | **✓ (planned)** |
| **Audit trail / clinical governance** | — | — | **✓ (planned)** |
| Source available | ✗ | Partial | ✓ (open) |

Three real differentiators, in order of importance:
1. **Multi-backend + agreement/disagreement flag** — the scientific novelty.
2. **Offline + audited** — the practical differentiator for clinical use.
3. **Resection concordance panel** — the epilepsy-specific extension that
   leverages our Task 8 work and the IDEAS resection release.

---

## Phasing

| Phase | Effort | Deliverable |
|---|---|---|
| **P1 — CentileBrain-only MVP** | ~1 week | Working `normreport` CLI, PDF report, tests, golden files. Uses IDEAS-controls-bundled reference. |
| **P2 — Containerise** | ~2 days | Dockerfile + Singularity def, runs on URMC Slurm without local Python setup. |
| **P3 — BrainMoNoCle backend** | ~1 week | Contingent on CNNP model access. Second `NormativeBackend` implementation. Backend-disagreement flag activated. |
| **P4 — Resection concordance panel** | ~3 days | Adds page 3 of the report showing patient's |Z| ranking vs. any prior resection region (uses IDEAS `table_resected.csv` as an atlas prior). |
| **P5 — Veritas endpoint** | ~1 week | Wraps the containerised CLI as a POST endpoint in the Veritas platform, tied to auth + audit log. |

Total to a publishable, deployable tool: **~4–6 weeks** of focused work.

---

## Naming

Working name `normreport` is generic. Better options to consider:
- **`brainzscore`** — descriptive, unlikely to conflict.
- **`morphogauge`** — evocative, memorable.
- **`ncr` / `NCR`** = Normative Comparison Report — abbreviates well.
- **`Deviant`** — provocative; not recommended.
- **Keep it descriptive**: `centilebrain-cli` if we stay single-backend.

Recommend picking after the first CentileBrain-only MVP is working — the
name matters more once we have something people would type.

---

## Risks and open questions

1. **BrainMoNoCle model access** — if CNNP declines, the multi-backend
   framing collapses to "CentileBrain wrapper," which is a weaker
   contribution. Fallback: publish the resection-concordance panel + the
   audited-offline form factor as the differentiators, and note
   BrainMoNoCle integration as future work.
2. **Site-adaptation offset (`mu_hat`) is required per site** — this is
   the standard PCN Toolkit procedure (Rutherford et al., Nature Protocols
   2022), not a workaround. The tool needs a local healthy-control
   reference cohort at every deployment site to estimate the offset,
   consistent with what BrainMoNoCle and other comparable platforms
   require. Report footer must disclose which reference cohort was used
   (see `../mu_hat.md`). Not a blocker; it is the accepted deployment
   pattern.
3. **FreeSurfer version mismatch** — if a user's input was processed with
   a very different FS version than the reference cohort, Z-scores may
   drift. Mitigation: report footer shows both FS versions; a
   `--warn-fs-mismatch` flag defaults ON.
4. **Small reference cohorts** — with < 20 controls, `mu_hat` estimation
   is noisy. Mitigation: emit a warning and refuse to proceed at N < 10.
5. **Clinical framing vs. research framing** — a "clinical report" tone
   carries regulatory expectations we may not want to invite. First
   version should say "for research use only" on every page.
6. **Positioning against a live tool** — BrainMoNoCle is published in
   *Imaging Neuroscience*; picking a fight is a bad idea. Framing should
   be complementary ("multi-backend meta-tool that includes BrainMoNoCle
   as one option") not competitive ("better than BrainMoNoCle").
