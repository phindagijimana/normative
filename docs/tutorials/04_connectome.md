# Tutorial 4 — Connectome

No CentileBrain/PCN. Schema: {doc}`../inputs`.

```bash
python3 connectome_normative/multiscale_normative.py --demo --out /tmp/connectome_demo

python3 connectome_normative/multiscale_normative.py \
  --matrices mats/ --labels labels.csv --covariates cov.csv \
  --groups groupA groupB --out results/ --z-thr 2.3 --n-perm 5000
```

Need matrices, labels (`name,hemi,base,sublobe`), covariates
(`subject,group,age,sex,op_side` + `control` group).  
Optional IDEAS outcomes: `ideas_covariates.py` (you still supply matrices).  
Flags: {doc}`../usage/connectome`. Idea: {doc}`../methods`.
