# Limits and open problems

## What normative modelling does well

- Places individuals on a demographic-aware reference  
- Separates “unusual for age/sex” from raw morphometry  
- Supports multi-site science when adaptation is done carefully  

(Rutherford et al., 2022; Marquand et al., 2019; Ge et al., 2024.)

## Known hard problems

| Issue | Why it matters |
|---|---|
| **Reference definition** | “Healthy” cohorts differ by age, ancestry, comorbidities, geography |
| **Site / pipeline shift** | Undoes calibration if ignored |
| **Model mismatch** | Wrong likelihood or covariates → distorted tails |
| **Multiplicity** | Thousands of edges/regions inflate false extremes |
| **Clinical validity** | Extremes ≠ diagnosis; need outcome-linked evidence |
| **Missing modalities** | Public morphometry engines ≠ automatic connectome engines |

## Frontier directions (reading pointers)

- Richer uncertainty (predictive intervals, conformal methods)  
- Fairness / representation across demographics  
- Multimodal normative models  
- Longitudinal charts (change vs cross-section)  
- Tighter integration with clinical decision studies  

See discussions and citations in Rutherford et al. (2022), Bethlehem et al.
(2022), and Ge et al. (2024).

## Bridging back to software

Understanding these limits is what makes a **toolkit** safe to use. For how
*this* repository maps onto the science (without mixing CLI into the theory
pages), continue to {doc}`../toolkit/index`.

## Key literature

- Rutherford et al., *Nature Protocols* 2022.  
- Bethlehem et al., *Nature* 2022.  
- Ge et al., *Lancet Digital Health* 2024.  
- Marquand et al., *Mol Psychiatry* 2019.
