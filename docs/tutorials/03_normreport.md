# Tutorial 3 — `normreport` (one subject)

**Prereq:** {doc}`../installation` (CentileBrain; PCN optional).

```bash
cd /path/to/normative/normreport && pip install -e .

normreport examples/demo_subject_stats.csv \
  --age 22 --sex M --subject-id demo \
  --backend centilebrain_mfp,centilebrain_gamlss \
  --output /tmp/normreport_out
```

Outputs under `/tmp/normreport_out/demo/`: PDF, Z CSV, provenance JSON.
Add `pcn_bayesian` when PCN models exist.

**Your subject:** same shape as the demo CSV; real `--age`/`--sex`; for a new
scanner pass `--reference local_controls.csv` (≥ ~30/sex).  
Flags/container: {doc}`../usage/normreport`.
