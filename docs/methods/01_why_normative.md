# Why normative modelling?

## The problem beginners hit first

Brain measures (cortical thickness, volume, connectivity) vary with **age**,
**sex**, and other factors. A raw number — “this hippocampus is 3200 mm³” —
is hard to interpret without a reference for *who that person is*.

Clinical cohorts make this worse: patients are compared to each other, or to
a small local control group, so you cannot tell **disease-related deviation**
from **normal demographic variation** or **scanner effects**.

## The growth-chart idea

Normative modelling borrows the logic of pediatric growth charts:

1. Build a model of the **healthy** population: expected value (and often
   variance) of a measure given covariates \(x\) (age, sex, …).
2. Place a new person on that chart as a **deviation** from expectation.
3. Interpret large deviations as *unusual relative to the reference*, not as
   a diagnosis by themselves.

In neuroimaging this is often called **normative modelling** or
**brain charts** (Marquand et al., 2016/2019; Rutherford et al., 2022).

## What this toolkit does with that idea

| Path | What is “normal”? | What you get |
|---|---|---|
| Morphometry (`score/`, `normreport`) | Large published models (CentileBrain, PCN) | Regional Z-scores (+ PDF report) |
| Connectome (`connectome_normative/`) | **Your** healthy controls’ edges | Edge/node/sublobe deviations + group tests |

Morphometry: we **apply** published models.  
Connectomes: we **fit** a normative model on your controls.

## Why not only “patient vs control t-tests”?

Group tests answer “do means differ?” Normative scores answer “**where does
this individual sit** on a population chart?” That individual map is what
surgical planning, case review, and multi-site transfer usually need
(Rutherford et al., *Nature Protocols* 2022).

## Read next

{doc}`02_z_scores` — the Z-score definition everyone uses in this repo.

## Literature

- Marquand AF, et al. Conceptualizing mental disorders as deviations from
  normative functioning. *Mol Psychiatry* 2019.  
- Rutherford S, et al. The normative modeling framework for computational
  psychiatry. *Nature Protocols* 2022.  
- Bethlehem RAI, et al. Brain charts for the human lifespan. *Nature* 2022
  (related “brain chart” framing; not wrapped here).
