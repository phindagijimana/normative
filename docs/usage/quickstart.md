# Quickstart

## IDEAS morphometry (worked example)

```bash
# dependencies + model clones — see Installation
pip install -r requirements.txt

cd ideas_data
python3 fetch_figshare.py
python3 fetch_resection.py    # optional; resection analyses only
python3 load_ideas.py         # → ideas_merged.csv
cd ..

Rscript score/score_centilebrain.R
Rscript score/score_centilebrain_gamlss.R
python3 score/score_pcn_toolkit.py
```

Outputs land in `score/` as long-form Z-score CSVs.

## Your own morphometry cohort

1. Build a CSV matching {doc}`../inputs` (`subject_id`, `cohort`, `sex`,
   `age`, DK region columns; controls must be `cohort=control`).
2. Score:

```bash
Rscript score/score_centilebrain.R --input cohort.csv --out-dir out/
Rscript score/score_centilebrain_gamlss.R --input cohort.csv --out-dir out/
python3 score/score_pcn_toolkit.py --input cohort.csv --out-dir out/
```

## One FreeSurfer subject

```bash
cd normreport
pip install -e .
normreport examples/demo_subject_stats.csv \
  --age 22 --sex M --subject-id demo \
  --backend centilebrain_mfp,centilebrain_gamlss,pcn_bayesian \
  --output /tmp/normreport_out
```

See {doc}`normreport`.

## Connectome smoke test

```bash
python3 connectome_normative/multiscale_normative.py --demo --out /tmp/connectome_demo
```

See {doc}`connectome`.
