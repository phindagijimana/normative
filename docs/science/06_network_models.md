# Network (connectome) normative models

## From regions to edges

Morphometry charts one **node feature** (e.g. thickness). Connectivity
analyses chart **pairwise relationships**. A normative model can be fit per
edge (or per derived edge feature) on controls, then patients receive
edge-wise deviations (Z), analogous to regional Z (Rutherford et al., 2022
framework still applies).

## Multiscale extreme deviations

A pattern used in large functional-connectivity normative studies is:

1. Score extreme edges ($|Z|$ above a threshold)  
2. Aggregate to **nodes** (e.g. deviation degree: how many extreme edges
   touch a region)  
3. Aggregate to **networks** or spatial parcels  
4. Compare groups with permutation or FDR-aware inference  

Ilioska et al.–style multiscale FC work is a key literature precedent for
that connection → region → network logic. Structural connectomes can use the
same *statistical geometry* once matrices exist.

## Design choices the literature emphasises

- Edge transforms and sparsity / consistency filters  
- Out-of-sample or cross-validated scoring for controls (avoid leakage)  
- Covariates (age, sex, head motion for FC, etc.)  
- Clear definition of networks/parcels  
- Multiple-comparison control across thousands of edges  

## Morphometry vs network normative models

| | Morphometry charts | Network normative models |
|---|---|---|
| Unit | Region measure | Edge / node summary |
| Typical reference | Mega-cohort public models | Often study-specific controls |
| Dominant public engines | CentileBrain, PCN/braincharts, … | More heterogeneous tool stacks |

## Read next

{doc}`07_limits_and_frontier`

## Key literature

- Rutherford et al., *Nature Protocols* 2022 — normative principles for any
  phenotype family.  
- Multiscale FC deviation studies (e.g. Ilioska et al. and related network
  psychiatry imaging papers) — extreme edges, degree, network enrichment.  
- Method papers on connectome reconstruction (tractography / correlation
  pipelines) — cite the pipeline you use; charts assume matrices are given.
