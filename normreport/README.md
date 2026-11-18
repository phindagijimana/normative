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

Full narrative: see `../paper_planning/tool.md` in the parent repository.

## Backends shipped

1. **CentileBrain-MFP** — multivariate fractional polynomial regression;
   37,407-subject training reference (Ge et al., *Lancet Digital Health*
   2024).
2. **CentileBrain-GAMLSS** — LMS distributional modelling; same 37k
   reference.
3. **PCN Toolkit-Bayesian** — hierarchical Bayesian regression against
   the pre-trained lifespan_DK_46K_59sites model bundle (Rutherford et
   al., *Nature Protocols* 2022; *eLife* 2022), covering the 68
   Desikan–Killiany cortical thickness regions. Site adaptation uses
   the PCN Toolkit's built-in mechanism with the reference cohort as
   the adaptation set.

## Two deployment modes

Pick whichever fits your workstation or clinical-research pipeline —
both share the same CLI arguments, output layout, and scientific
behaviour.

### 1. Native (Python + R on the host)

```bash
cd normreport
pip install --user -e .            # requires Python ≥ 3.9 and R ≥ 4.0
normreport examples/demo_subject_stats.csv \
    --age 22 --sex M --subject-id demo \
    --backend centilebrain_mfp,centilebrain_gamlss,pcn_bayesian \
    --output /tmp/normreport_out
```

Runtime dependencies: Python ≥ 3.9 (3.11+ recommended so that
`pcntoolkit>=1.0` installs cleanly), R ≥ 4.0 with the `mfp` and
`gamlss` packages, plus a local checkout of
[phindagijimana/normative](https://github.com/phindagijimana/normative)
where `centilebrain/models/` and `score/score_centilebrain*.R` exist.

### 2. Containerised (Apptainer / Singularity)

For clinical-research pipelines that require a fixed environment or
whose hosts don't have R + Python + pcntoolkit installed:

```bash
# a. build the image (once, ~10 min, ~700 MB or ~3.5 GB depending on
#    the pcntoolkit line — see Singularity.def and CHANGELOG.md)
cd normreport
APPTAINER_TMPDIR=$HOME/apptainer_tmp \
PROOT_TMP_DIR=$HOME/apptainer_tmp \
  apptainer build --fakeroot normreport.sif Singularity.def

# b. run via the packaged wrapper (auto-binds the parent repo at /work
#    and translates host paths for you)
./normreport-container examples/demo_subject_stats.csv \
    --age 22 --sex M --subject-id demo \
    --backend centilebrain_mfp,centilebrain_gamlss,pcn_bayesian \
    --output /tmp/normreport_out
```

The `normreport-container` shell wrapper resolves the `.sif`, sets the
required bind-mount, and forwards every other argument to the
containerised CLI unchanged. Override any assumption with the
environment variables listed in the wrapper's `--help` (`NORMREPORT_SIF`,
`NORMREPORT_REPO_ROOT`, `NORMREPORT_RUNTIME`).

### Which mode should I use?

| | Native | Container |
|---|---|---|
| **Fastest to set up** | ✓ (pip install) | (~10 min container build first) |
| **Reproducible across machines** | Same-versioned deps required | ✓ (SIF is byte-identical) |
| **Air-gapped clinical hosts** | Needs R + Python + pcntoolkit installed | ✓ (single SIF file, no runtime pip installs) |
| **Fits inside HPC / Slurm queues** | Needs module load + pip venv | ✓ (Apptainer is the standard) |
| **Uses host FreeSurfer subject directories directly** | ✓ (no bind-mount needed) | Needs `--bind /path:/work` (the wrapper handles this) |

**Recommended:** native for development and single-machine use;
container for URMC / Newcastle / any HPC or clinical-research
deployment where reproducibility across hosts matters more than
setup speed.

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

## Singularity container (advanced)

The `Singularity.def` ships in this directory. Both rootless
(`apptainer build --fakeroot`) and sudo-based (`sudo singularity
build`) build paths are supported. See the *Two deployment modes*
section above for the rootless recipe recommended for most users.

If you prefer to call the container directly (bypassing the
`normreport-container` wrapper), remember to bind-mount the parent
`Normative` repo at `/work` and set `NORMREPORT_REPO_ROOT=/work`
inside the container:

```bash
apptainer run --bind $(pwd)/..:/work normreport.sif \
    /work/normreport/examples/demo_subject_stats.csv \
    --age 22 --sex M --output /tmp/normreport_out
```

The bundled `%environment` block in `Singularity.def` sets
`NORMREPORT_REPO_ROOT=/work` automatically, so the tool can locate
the R scoring scripts and the CentileBrain + PCN Toolkit model
bundles on the bind-mount without extra flags.

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
