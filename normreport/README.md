# normreport

Single-subject multi-backend normative morphometry reports (PDF + Z-scores).

**Status:** v0.1.0 — research use only.  
**Docs:** [Tutorial 3](../docs/tutorials/03_normreport.md) ·
[CLI reference](../docs/usage/normreport.md) ·
[Install](../docs/installation.md)

## Quick demo

```bash
cd normreport
pip install -e .
normreport examples/demo_subject_stats.csv \
  --age 22 --sex M --subject-id demo \
  --backend centilebrain_mfp,centilebrain_gamlss \
  --output /tmp/normreport_out
```

Needs CentileBrain models in the parent repo (`../centilebrain/models/`).
Add `pcn_bayesian` when PCN models are installed. For a new site, pass
`--reference` with local controls.

## Container

```bash
apptainer build --fakeroot normreport.sif Singularity.def
./normreport-container --help
```

See the docs pages above for backends, outputs, and site-matched references.
Also: `CHANGELOG.md`, `LICENSE`, `CITATION.cff`.
