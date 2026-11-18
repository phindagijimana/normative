# Interpreting results (safely)

## Checklist before believing a patient map

1. **Controls look calibrated** — mean Z ≈ 0, SD ≈ 1 after adaptation.  
2. **Covariates are correct** — age units, sex coding, scan age (not surgery age).  
3. **Regions/names match** the model templates ({doc}`../inputs`).  
4. **Extremes are not over-interpreted** — thresholds are conventions.  
5. **Multi-backend agreement** — prefer features extreme in MFP *and* GAMLSS
   *and/or* PCN (`normreport` consensus flags).

## Common displays

| Display | Use |
|---|---|
| Long-form Z CSV | Downstream stats, plotting |
| Top-\|Z\| tables / PDF | Case review (`normreport`) |
| Control summary SD / mean | QC of adaptation |
| Cross-backend correlation | Algorithm agreement, not truth |

## Clinical / research caution

This software is **research use only** (see repository `LICENSE`). Normative
Z-scores are decision-*support* features, not FDA/CE-cleared diagnostics.

Epilepsy worked example (IDEAS): scores can be related to laterality,
resection overlap, or outcome in research analyses — always with appropriate
statistics and clinical ground truth (Taylor et al. 2025).

## IDEAS-specific caveat

Public IDEAS ages are **binned**. This toolkit maps bins to midpoints. That
is an approximation; state it if you publish IDEAS-based results.

## Read next

{doc}`06_connectome` — normative modelling when the data are networks.  
Or jump to tutorials: {doc}`../tutorials/index`.

## Literature

- Rutherford et al., *Nature Protocols* 2022 — interpretation & reporting.  
- Taylor et al., *Epilepsia* 2025 — IDEAS.  
- Ge et al., *Lancet Digital Health* 2024 — morphometry centiles/Z in practice.
