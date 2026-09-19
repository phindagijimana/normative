# Changelog

## v0.1.0 — 2026-09-19 (initial release)

Ships with the accompanying validation manuscript. Scope:

**Backends**
- `centilebrain_mfp` — wraps the CentileBrain MFP scoring R script
- `centilebrain_gamlss` — wraps the CentileBrain GAMLSS scoring R script
- `pcn_bayesian` — real per-subject scoring against the Rutherford et
  al. 2022 lifespan_DK_46K_59sites hierarchical Bayesian regression
  models (cortical thickness, 68 Desikan–Killiany regions), with the
  PCN Toolkit's built-in site-adaptation using the reference cohort
- `pcn_bayesian_stub` — NaN-returning stub kept for tests when the
  pcn_models/braincharts bundle is not present locally

**Features**
- Per-patient PDF report with cross-backend consensus/disagreement flagging
- CLI: `normreport <subject_csv> --age <y> --sex <MF> --output <dir>`
- Bundled IDEAS-controls-2025 reference cohort (100 UK controls)
- `--reference /path/` for local reference-cohort override
- Site adaptation follows the PCN Toolkit protocol (Rutherford 2022)
- Provenance stamp on every report (git SHA, backend versions, timestamp)
- Singularity container definition (`Singularity.def`)
- "For research use only" disclaimer on every report

**Deferred to v1.1+**
- URMC-scanner-specific reference cohort (post-publication URMC deployment)
- BrainMoNoCle-GAMLSS backend (contingent on CNNP model access)
- PCN Toolkit backends for surface area and subcortical volume
  (currently only cortical thickness is bundled in the distributed
  Desikan–Killiany lifespan model set)
- Native FreeSurfer `stats/` directory parsing (currently CSV-only)
- Web UI / Veritas platform endpoint
- Batch mode
