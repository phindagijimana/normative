# Connectome normative modelling

Morphometry asks “is this **region** atypical?” Connectome normative
modelling asks “is this **connection** (and patterns of connections)
atypical?”

## Intermediate idea

1. Build a normative model **per edge** on healthy controls (covariates:
   age, sex, …).  
2. Score patients with out-of-sample Z; score controls with cross-validation
   so they are not fit in-sample.  
3. Mark **extreme** edges (\|Z\| above a threshold, often 2.3).  
4. Summarise extremes at multiple scales:
   - **Connections** — which edges differ between groups  
   - **Nodes** — deviation degree (how many extreme edges touch a region)  
   - **Networks / sublobes** — spatial aggregates (here: ipsi/contra to
     surgery via `op_side`)

This multiscale extreme-deviation logic follows the spirit of large FC
normative studies (e.g. Ilioska et al.–style connection / region / network
summaries). This repo implements it for **structural** connectomes you
supply.

## How this differs from CentileBrain / PCN

| | Morphometry backends | Connectome scripts |
|---|---|---|
| Reference | Published mega-cohort models | **Your** controls |
| Unit | Region morphometry | Matrix edge (+ strength comparator) |
| Adaptation | Site offset / PCN adapt | Built into fitting on local controls |
| Code | `score/`, `normreport` | `connectome_normative/` |

## Node strength comparator

Along with edge-wise models, the toolkit fits a **node-strength** normative
model (conventional summary of how strongly a region connects overall). Use
it as a simpler comparator to multiscale edge deviations.

## Group contrasts

Typical use: compare two patient groups (e.g. outcome strata) with
permutation tests on burdens and spatial overlap of extremes. Optional:
each group vs controls (`--vs-controls`).

Tutorial: {doc}`../tutorials/04_connectome`. Schema: {doc}`../inputs`.

## Read next

{doc}`07_advanced` — limits, transfer, and what “advanced” still cannot do.

## Literature

- Ilioska I, et al. (and related) multiscale FC deviation frameworks —
  connection / region / network extreme deviations.  
- Rutherford et al., *Nature Protocols* 2022 — normative modelling principles
  still apply (fit on controls, score deviations, careful inference).  
- For structural connectome construction itself, cite your tractography /
  pipeline papers separately (this toolkit assumes matrices already exist).
