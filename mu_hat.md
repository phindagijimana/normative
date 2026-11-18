# `mu_hat`

Per-region site offset for CentileBrain MFP on IDEAS. It is estimated from the 100 local healthy controls (Rutherford et al., *Nature Protocols* 2022).

MFP `predict()` returns a mean-centered value. The training means (`mean_train`) are not in the public model files. Per region and sex, from the same-sex controls:

```
mu_hat = mean(observed − predicted)
Z      = (observed − predicted − mu_hat) / RMSE
```

`RMSE` is the model's own training error. The offset is then applied to every subject in that sex block, patients included. Control mean Z is about 0 because the offset was fit on those controls. Calibration is the SD of control Z, which a constant shift does not change.

Without the offset, control Z in a first pass sat near mean −17 (SD 7.8).

## Other backends

| Backend | Role of the 100 controls | Code |
|---|---|---|
| MFP | `mu_hat` above | `CentileBrain/score_centilebrain.R` |
| GAMLSS | Predicts on the original scale. `z_shift = mean(control z_raw)`, then `Z = z_raw − z_shift` | `CentileBrain/score_centilebrain_gamlss.R` |
| PCN | Adaptation set inside `predict()` | `CentileBrain/score_pcn_toolkit.py` |

Where those adapted scores are used: `compare/controls_use.md`.

## What the offset changes

| Quantity | Changes? |
|---|---|
| SD of control Z | No |
| Mean of control Z | Yes (about 0) |
| Pearson *r* vs IDEAS Z | No |
| Classification AUC | No |
| Resection ρ on \|Z\| | Slightly, for residuals near zero |

## Checks in this bundle

- MFP with `mu_hat = 0`: `hypothesis/README.md`. Patient mean Z is 1.6–4.7 and does not match GAMLSS with its control shift (Pearson *r* = 0.41).
- Held-out controls and how many controls are enough: `compare/extras/MU_HAT_ROBUSTNESS.md`. The offset settles at N ≥ 30.

Rutherford S, Kia SM, Wolfers T, et al. The normative modeling framework for computational psychiatry. *Nature Protocols* 2022;17:1711–1734. doi:10.1038/s41596-022-00696-5.
