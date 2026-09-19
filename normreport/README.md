# normreport

Multi-backend normative brain-morphometry report generator. Given one
patient's FreeSurfer output + age + sex, runs multiple published
normative-modelling backends and produces a single per-patient PDF
report with cross-backend consensus/disagreement flagging.

**Status:** v0.1.0 — initial release accompanying the validation
manuscript. For research use only.

Repository: <https://github.com/phindagijimana/normative>

## Why this tool exists

Existing normative-modelling platforms distribute their pre-trained
models via web apps (BrainMoNoCle, CentileBrain) or as research
libraries (PCN Toolkit). None of them is a per-patient PDF report
generator, and none of them runs multiple backends side-by-side.
For a clinical-research pipeline that must run offline, produce
audited reports, and provide a robustness check by comparing multiple
normative-modelling approaches, this tool fills the gap.

Full tool design: see `../tool_design/ARCHITECTURE.md`.

## Backends shipped

1. **CentileBrain-MFP** — multivariate fractional polynomial regression;
   37,407-subject training reference (Ge et al., *Lancet Digital Health*
   2024).
2. **CentileBrain-GAMLSS** — LMS distributional modelling; same 37k
   reference.
3. **PCN Toolkit-Bayesian** — STUB in v0.1.0. Real integration with the
   Rutherford et al. 2022 pre-trained lifespan models is on the v1.1
   roadmap.

## Install (workstation)

```bash
cd normreport
pip install --user -e .
```

Runtime dependencies: Python ≥ 3.9, R ≥ 4.0 with the `mfp` and `gamlss`
packages installed. The R scripts and CentileBrain `.rds` model files
must be reachable at the standard relative paths from the parent
repository — the tool assumes a checkout of
[phindagijimana/normative](https://github.com/phindagijimana/normative)
where `centilebrain/models/` and `score/score_centilebrain*.R` exist.

## Quick start

```bash
# Score a demo subject
normreport examples/demo_subject_stats.csv \
    --age 22 --sex M --subject-id demo \
    --backend centilebrain_mfp,centilebrain_gamlss \
    --output /tmp/normreport_out
```

Output at `/tmp/normreport_out/demo/`:

* `demo_report.pdf` — 1-page A4 report, top-20 regions by |Z|, consensus
  flag per region
* `demo_zscores.csv` — long-form Z-scores (all backends × all regions)
* `demo_provenance.json` — git SHA, backend versions, timestamp,
  reference cohort ID
* `demo_raw.json` — cleaned FreeSurfer parse

## CLI reference

```
normreport SUBJECT_CSV [OPTIONS]

Required options:
  --age FLOAT         Subject age in years
  --sex [M|F]         Subject sex
  --output DIR        Output directory

Optional:
  --subject-id STR    Subject identifier (default: CSV filename stem)
  --backend STR       Comma-separated backend list or 'all'
                      Default: centilebrain_mfp,centilebrain_gamlss
                      Available: centilebrain_mfp, centilebrain_gamlss,
                                 pcn_bayesian
  --reference PATH    Reference cohort CSV
                      Default: bundled IDEAS-controls-2025 (100 UK controls)
  --version           Show tool version
```

## Reference cohort

The tool ships with **IDEAS-controls-2025** (100 healthy UK controls
scanned on a Newcastle 3T Siemens Prisma) as the default. Every
generated report discloses which reference was used.

For clinical deployment at a different site, supply your own reference
with `--reference /path/to/local_controls.csv`. The reference should be
≥ 30 healthy subjects per sex scanned on the same scanner and
FreeSurfer-processed identically to the patients you will score.
Site adaptation follows the PCN Toolkit protocol (Rutherford et al.,
*Nature Protocols* 2022) — see `../mu_hat.md` in the parent repository
for the methodology note and the sample-size sensitivity results.

## Singularity container

For deployment inside a credentialed clinical-research pipeline:

```bash
sudo singularity build normreport.sif Singularity.def
singularity run normreport.sif examples/demo_subject_stats.csv \
    --age 22 --sex M --output /tmp/normreport_out
```

## Tests

```bash
pip install --user -e '.[dev]'
pytest tests/
```

## License

MIT. See `LICENSE`. For research use only; not evaluated by any
regulatory body for clinical use.

## Citation

If you use this tool please cite:

* This tool: see `CITATION.cff` (Zenodo DOI will be added at v1.0
  release).
* CentileBrain: Ge R et al. *Lancet Digital Health* 2024.
* PCN Toolkit protocol / site adaptation: Rutherford S et al.
  *Nature Protocols* 2022.
* IDEAS reference cohort: Taylor P et al. *Epilepsia* 2025.

## Roadmap

See `CHANGELOG.md` for v0.1.0 scope and deferred v1.1+ items.
