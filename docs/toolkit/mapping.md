# Science concepts → this toolkit

Use this page after {doc}`../science/index`. It only maps ideas to **this**
repo — not general theory.

| Science idea | Where it appears here |
|---|---|
| Individual deviation / Z | Outputs of `score/*.R`, `score_pcn_toolkit.py`, `normreport` |
| CentileBrain MFP / GAMLSS | `score_centilebrain.R`, `score_centilebrain_gamlss.R`; backends in `normreport` |
| PCN hierarchical lifespan models | `score_pcn_toolkit.py`; `pcn_bayesian` in `normreport` |
| Site adaptation (local controls) | `cohort=control` rows; PCN adaptation set; `mu_hat_*.R` checks |
| Multi-model concordance | `normreport` consensus flags; optional `score/compare_*.py` |
| Network edge Z + multiscale summaries | `connectome_normative/multiscale_normative.py` |
| Worked clinical cohort | IDEAS via `ideas_data/` + Tutorial 1 (Taylor et al., 2025) |

## CLI entry points (pointers only)

```bash
Rscript score/score_centilebrain.R --help
python3 score/score_pcn_toolkit.py --help
normreport --help   # after pip install -e normreport/
python3 connectome_normative/multiscale_normative.py --help
```

Full flags: {doc}`../usage/morphometry`, {doc}`../usage/normreport`,
{doc}`../usage/connectome`.  
End-to-end runs: {doc}`../tutorials/index`.
