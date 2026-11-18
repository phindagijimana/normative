# Multiscale normative modelling of structural connectivity after epilepsy surgery

Adapts Ilioska et al. 2026 (*Nature Mental Health*, [doi:10.1038/s44220-026-00656-y](https://doi.org/10.1038/s44220-026-00656-y); summary in `../papers/Ilioska2026_Multiscale_FC_Autism_summary.md`) to diffusion MRI (DWI) structural connectomes in the IDEAS cohort. It compares two groups of surgical patients: those **not seizure-free at 1 year** and those with **durable seizure freedom**.

Code: `multiscale_normative.py` (this folder).

## Aim

Test whether the pre-operative structural connectivity of patients who are not seizure-free one year after surgery deviates from normative expectations differently from patients with durable seizure freedom. The comparison is made at three spatial scales:

| Scale | Unit | Measure per patient | Analogue in Ilioska et al. |
|---|---|---|---|
| Connections | Each matrix element (edge) | Extreme deviation yes/no | Connections |
| Nodes | Each atlas region | Deviation degree = number of extreme edges attached to the node | Regions |
| Sublobes | Each pair of lateralised sublobes (ipsilateral or contralateral to surgery) | % of the patient's extreme edges falling within or between the pair | Canonical networks |

A normative model of node strength is run alongside as the conventional comparator. The convergence analysis is meant to show what node strength misses.

## Groups and outcome definition

Groups are defined from the IDEAS yearly ILAE outcome columns (`ILAE_Year1`–`ILAE_Year5` in `Metadata_Release_Anon.csv`). `ideas_covariates.py` builds the table.

| Group | Definition | N (minimum follow-up 3 years) |
|---|---|---|
| `notSF1` | ILAE > 1 at year 1 | 182 |
| `durable` | ILAE 1 at every recorded year, with ≥ 3 years of follow-up | 138 |
| `relapse` (optional, `--keep-relapse`) | ILAE 1 at year 1, ILAE > 1 later | 70 |
| `control` | IDEAS healthy controls | 100 |

- **Follow-up sensitivity:** with a 2-year minimum, `durable` has 163 patients; with a 5-year minimum, 99. Seizure-free patients with shorter follow-up than the minimum are excluded.
- **Scale:** ILAE 1 means completely seizure-free with no auras; ILAE 2 (auras only) counts as not seizure-free. A sensitivity analysis treating ILAE 1–2 as seizure-free is worth reporting.
- **Covariates:** age is the midpoint of the 5-year IDEAS age-at-scan bin (`load_ideas.bin_to_midpoint`). Surgery type (316 of 443 are temporal lobectomies) and pathology are carried in the table for stratification, e.g. a temporal-only sensitivity analysis.
- **Reference (normative) cohort:** the 100 IDEAS controls, if they have connectomes from the same pipeline. See the reference cohort section below.

## Inputs

1. **Pre-operative connectomes.** One N × N weighted, undirected matrix per subject, built with the same pipeline, parcellation and edge weighting for patients and controls. Post-operative matrices would show the resected nodes as artificial deviations.
2. **Atlas label table** (`labels.csv`, row order = matrix order):

   | Column | Meaning |
   |---|---|
   | `name` | region name |
   | `hemi` | `L`, `R` or `M` (midline, e.g. brainstem) |
   | `base` | homolog key, identical for the left and right copy of a region (e.g. `hippocampus`) |
   | `sublobe` | hemisphere-free sublobe name (e.g. `temporal_mesial`) |

3. **Covariate table** (`covariates.csv`):

   | Column | Meaning |
   |---|---|
   | `subject` | matches the matrix filename stem |
   | `group` | `control`, or a patient group label (e.g. `notSF1`, `durable`) |
   | `age` | age at scan. IDEAS ages are 5-year bins; use bin midpoints and document the rule for open-ended bins. |
   | `sex` | `M` / `F` |
   | `op_side` | `L` / `R` (patients only) |
   | `site` | optional. Every patient site must also appear among the controls. |
   | other | optional covariates passed with `--extra-covariates` (e.g. intracranial volume, DWI quality metrics) |

## Analysis steps

1. **Edge filtering (consistency thresholding).** Keep edges that are non-zero in at least 90% of controls (`--min-frac`). The filter is mirror-symmetric: an edge is kept only if its contralateral mirror also passes. This keeps the edge set identical after left/right re-indexing. Sparse tractography edges are zero-inflated and can't be modelled with a Gaussian model.
2. **Transform.** Apply `log1p` to the edge weights, which suits streamline counts and densities. Use `--transform none` for FA- or MD-weighted matrices.
3. **Normative model.** For every edge, fit a closed-form linear model on controls only, with covariates age, age², sex, optional site indicators and extra covariates. The deviation is z = (observed − predicted) / predictive SD, where the predictive SD includes the leverage term.
   - Patients are scored by the model fit to all controls.
   - Controls are scored by 10-fold cross-validation, so each control is scored by a model that never saw their data. This matches the paper.
   - The model is linear rather than a Gaussian process because the adult age range is narrow and the reference cohort is small. A Gaussian process from PCNtoolkit can be swapped in if the age range is wide.
4. **Lateralisation.** Models are fit in native left/right space. After scoring, each patient's nodes are relabelled `ipsi_*` or `contra_*` according to the side of surgery, and midline nodes become `mid_*`. Controls have no surgical side, so they get pseudo-sides at the same left/right ratio as the patients. That only affects the optional patient-vs-control tests.
5. **Extreme deviations.** |z| > 2.3 (p ≈ 0.01), with positive and negative deviations analysed separately. Sensitivity analyses use thresholds of 1.96 and 2.6 (`--z-thr`).
6. **Overlap at three scales.**
   - **Connections:** % of each group with an extreme deviation at each edge.
   - **Nodes:** for thresholds τ = 1…20 (`--deg-thr`), the % of the group with deviation degree ≥ τ. Summarised as the area under the curve (AUC) over τ, so no single threshold has to be chosen.
   - **Sublobes:** the same AUC summary over τ = 1…10% (`--net-thr`), applied to the % of each patient's extreme edges within or between each pair of lateralised sublobes. With many sublobes, check the distribution of these percentages and widen τ if needed.
7. **Inference.**
   - Two-sided permutation test of the group difference (notSF1 − durable) with 10,000 label permutations. Benjamini–Hochberg FDR is applied within each scale and sign.
   - The effect size is the relative difference (AUC_A − AUC_B) / AUC_B.
   - `--vs-controls` adds each patient group vs controls.
   - Use at least 10,000 permutations. The smallest possible p is 1/(n_perm + 1), and the FDR correction needs that resolution.
8. **Global checks.**
   - Total deviation burden per patient (Mann–Whitney test).
   - Fraction of deviations that are positive (Welch t-test), i.e. whether either group leans toward reduced or increased connectivity overall.
9. **Comparator.** Node-strength z-scores from the same normative model, compared between groups with the same permutation test.
10. **Optional secondary analysis.** Cross-validated classification of notSF1 vs durable from deviation features at each scale (logistic regression or a linear support vector machine, nested cross-validation). Report balanced accuracy and AUC against a permutation null. The paper's support vector regression applies to continuous outcomes only.

## Outputs (`--out DIR`)

| File | Content |
|---|---|
| `qc.json` | Sample sizes, edges kept, normative-model calibration (CV z mean/SD of controls, observed vs expected extreme fraction) |
| `deviations.npz` | Lateralised edge z-scores and node-strength z-scores per subject, for figures and classifiers |
| `<A>_vs_<B>_{connections,nodes,sublobes}_{pos,neg}.csv` | Per-feature group values, difference, relative difference, permutation p, BH q |
| `<A>_vs_<B>_node_strength_z.csv` | Node-strength comparator |
| `summary.csv` | One row per comparison: burden tests, maximum connection overlap, number of significant features per scale |

**Check calibration before interpreting results.** In `qc.json`, the CV z-scores of controls should have mean ≈ 0 and SD ≈ 1. The fraction of extreme edges in controls should be close to the Gaussian expectation (2.1% at |z| > 2.3). A large excess means the transform or model is mis-specified for those edges.

## Usage

```bash
# synthetic end-to-end check (~3 s): heterogeneous edges, convergent sublobe effect
python3 multiscale_normative.py --demo --out demo_out

# IDEAS covariates (controls + notSF1 + durable); matrices named sub-<ID>.csv
python3 ideas_covariates.py --min-followup 3 --out covariates_ideas.csv

# real data
python3 multiscale_normative.py \
  --matrices connectomes/ --labels labels.csv --covariates covariates_ideas.csv \
  --groups notSF1 durable --out results/ --vs-controls
```

Requirements: Python ≥ 3.9, numpy, pandas, scipy.

**Demo result (validation of the pipeline).** In the synthetic data, each patient in group A loses a random 3 of the 16 edges between the ipsilateral mesial and lateral temporal sublobes. The pipeline recovers the paper's signature:
- **Connections:** no edge survives FDR correction; maximum overlap is 30%.
- **Nodes:** 2 ipsilateral temporal nodes are significant (q = 0.026).
- **Sublobes:** the planted ipsilateral mesial ↔ lateral temporal pair is significant (q = 0.012; relative difference ≈ +19×).
- **Node strength:** nothing survives correction (best q = 0.24).

## Reference cohort: the main blocker

The normative model is only valid if controls and patients share scanner, protocol and processing.

- **IDEAS.** Patients are from IDEAS, so the 100 IDEAS controls (same centre) are the natural reference. However, the public OpenNeuro release (ds005602) contains only T1w and FLAIR scans for controls and patients; there is no DWI. Connectome matrices therefore come from a non-public source, and the key question is whether the **controls have matrices from the same source and pipeline**.
  1. If yes, use the IDEAS controls directly. Add a scanner/protocol covariate if IDEAS acquisitions changed over time.
  2. If not, ask the IDEAS / CNNP team (Newcastle) whether control DWI exists and can be processed identically.
  3. As a last resort, use public DWI cohorts (e.g. HCP Young Adult, HCP-Aging, Cam-CAN) reprocessed through the same connectome pipeline, with harmonisation.
- **Confounding.** If all controls come from one scanner and all patients from another, site is completely confounded with patient status. Neither ComBat nor a site covariate can separate them, and every edge will look deviant. In that case:
  - The primary notSF1-vs-durable contrast is still interpretable, because both groups are scored against the same reference and share the site offset.
  - Patient-vs-control results are not.
  - Report this explicitly.
- **Minimum size.** Roughly ≥ 50 controls for a linear model with 4–5 covariates. Fewer controls make the predictive SDs, and therefore the z-scores, noisy.

## Known limitations and decisions to record

- The thresholds (|z|, τ ranges, edge consistency) are partly arbitrary. Report the sensitivity analyses.
- Group sizes from IDEAS (182 vs 138) are reasonable, but connection-level tests across all edges remain conservative after FDR correction. Weak connection-level results alongside region and network convergence are part of the scientific point.
- Lateralisation assumes left/right homologs exist for every non-midline region in the atlas.
- Resected tissue overlapping a node does not affect pre-operative matrices, but tractography through lesions such as hippocampal sclerosis or FCD can produce real deviations. Record the pathology for each patient and consider it as a covariate or for stratification.
- Pseudo-sides for controls make patient-vs-control lateralised results depend on the random seed. Report results across several seeds, or symmetrise the analysis.
