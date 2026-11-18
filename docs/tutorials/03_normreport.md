# Tutorial 3 — One subject with `normreport`

**Goal.** Produce a multi-backend PDF report from one FreeSurfer stats table.

**Prereqs.** {doc}`../installation` (CentileBrain; PCN optional). Parent repo
layout so models resolve next to `normreport/`.

## 1. Install the CLI

```bash
cd /path/to/normative/normreport
pip install -e .
```

## 2. Run the bundled demo

```bash
normreport examples/demo_subject_stats.csv \
  --age 22 --sex M --subject-id demo \
  --backend centilebrain_mfp,centilebrain_gamlss \
  --output /tmp/normreport_out
```

Add `pcn_bayesian` to `--backend` once PCN models are installed.

## 3. Inspect outputs

Under `/tmp/normreport_out/demo/`:

- `demo_report.pdf` — top regions by \|Z\|, consensus flags  
- `demo_zscores.csv` — long-form Z-scores  
- `demo_provenance.json` — backend / reference metadata  

## 4. Reuse on your subject

1. Export FreeSurfer stats into a CSV shaped like
   `examples/demo_subject_stats.csv`.
2. Pass real `--age` / `--sex` / `--subject-id`.
3. For a new scanner, pass a site-matched control table:

```bash
normreport /path/to/subject_stats.csv \
  --age 41 --sex F --subject-id sub-041 \
  --reference /path/to/local_controls.csv \
  --backend centilebrain_mfp,centilebrain_gamlss,pcn_bayesian \
  --output /path/to/out
```

Controls: ≥ ~30 per sex, same FreeSurfer pipeline as the patient
({doc}`../methods`).

## Container option

See {doc}`../usage/normreport` for Apptainer / Singularity build and the
`normreport-container` wrapper.
