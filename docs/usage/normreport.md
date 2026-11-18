# Single-subject reports (`normreport`)

Given one subject's FreeSurfer stats + age + sex, run one or more backends and
write a PDF report with cross-backend consensus flagging.

**Status:** v0.1.0 — research use only.

## Native install

```bash
cd normreport
pip install -e .
normreport examples/demo_subject_stats.csv \
  --age 22 --sex M --subject-id demo \
  --backend centilebrain_mfp,centilebrain_gamlss,pcn_bayesian \
  --output /tmp/normreport_out
```

Needs CentileBrain models and (for PCN) the braincharts bundle in the parent
repo layout described under {doc}`../installation`.

## Container

```bash
cd normreport
apptainer build --fakeroot normreport.sif Singularity.def
./normreport-container examples/demo_subject_stats.csv \
  --age 22 --sex M --subject-id demo \
  --backend centilebrain_mfp,centilebrain_gamlss,pcn_bayesian \
  --output /tmp/normreport_out
```

## CLI essentials

| Option | Meaning |
|---|---|
| `--age` | Age in years |
| `--sex` | `M` or `F` |
| `--output` | Output directory |
| `--backend` | Comma-separated list or `all` |
| `--reference` | Control cohort CSV (default: bundled IDEAS controls) |

Backends: `centilebrain_mfp`, `centilebrain_gamlss`, `pcn_bayesian`.

## Outputs

Under `<output>/<subject-id>/`:

- `*_report.pdf` — top regions by \|Z\|, consensus flags
- `*_zscores.csv` — long-form Z-scores
- `*_provenance.json` — versions / reference cohort

## Site-matched reference

For a new scanner, pass `--reference` with ≥ ~30 healthy controls per sex,
processed identically to patients. See {doc}`../methods`.
