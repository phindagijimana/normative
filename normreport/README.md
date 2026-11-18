# normreport

v0.1.0 — research use only.  
**Docs:** [Tutorial 3](../docs/tutorials/03_normreport.md) · [CLI](../docs/usage/normreport.md)

```bash
pip install -e .
normreport examples/demo_subject_stats.csv \
  --age 22 --sex M --subject-id demo \
  --backend centilebrain_mfp,centilebrain_gamlss \
  --output /tmp/normreport_out
```

Needs `../centilebrain/models/`. See also `CHANGELOG.md`, `LICENSE`, `CITATION.cff`.
