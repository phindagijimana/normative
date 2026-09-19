# Changelog

## v0.1.0 — 2026-09-19 (initial release)

Ships with the accompanying validation manuscript. Scope:

**Backends**
- `centilebrain_mfp` — wraps the CentileBrain MFP scoring R script
- `centilebrain_gamlss` — wraps the CentileBrain GAMLSS scoring R script
- `pcn_bayesian` — stub; real integration with the Rutherford et al. 2022
  pre-trained lifespan models is a v1.1 roadmap item

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
- Real PCN Toolkit-Bayesian backend
- BrainMoNoCle-GAMLSS backend (contingent on CNNP model access)
- Native FreeSurfer `stats/` directory parsing (currently CSV-only)
- Web UI / Veritas platform endpoint
- Batch mode
