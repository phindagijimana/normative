# Introduction: what is normative modelling?

## A simple analogy

Pediatricians plot a child’s height on a **growth chart**: given age and sex,
they see whether the child is typical or extreme *for that reference
population*. Normative modelling applies the same idea to brain measures.

Instead of asking only “do patients differ from controls on average?”
(case–control), we ask “**where does this individual sit** on a chart of
expected brain biology?” (Marquand et al., 2016, 2019).

## Formal idea

Learn, from a large **healthy** (or reference) sample, a predictive mapping

$$
y \mid x \sim f(\hat{\mu}(x),\ \hat{\sigma}(x),\ \ldots)
$$

where $y$ is a brain feature and $x$ are covariates (age, sex, …). A new
person receives a **deviation score** (often a Z or a centile) relative to
that mapping. Large deviations mean *atypical versus the chart*, not a
clinical diagnosis by themselves (Rutherford et al., 2022).

## Why the field moved this way

| Classical case–control | Normative / charting |
|---|---|
| Group mean differences | Individualised position on a reference |
| Hard to use for single-subject decisions | Natural language for case review & mapping |
| Collapses heterogeneity | Preserves person-specific deviation patterns |

Psychiatric and neurological cohorts are heterogeneous; normative scores are
one principled way to quantify that heterogeneity (Marquand et al., 2019;
Rutherford et al., 2022).

## What gets modelled?

Historically and today:

- **Morphometry** — thickness, area, volume (e.g. CentileBrain, braincharts /
  PCN lifespan models)  
- **Function & connectivity** — edge-wise or network models of FC/SC
  deviations ({doc}`06_network_models`)  
- Other derived phenotypes (cognition, multimodal features) in the wider
  literature  

## Separating science from software

The papers above define the **science**. Separate software projects
*implement* pieces of it (CentileBrain web/models, PCN Toolkit, Brain MoNoCle,
etc.). The next pages stay with science and literature; how **this**
repository implements a slice of the field is documented under
{doc}`../toolkit/index`.

## Read next

{doc}`02_z_scores_and_centiles`

## Key literature

- Marquand AF, Rezek I, Buitelaar J, Beckmann CF. Understanding heterogeneity
  in clinical cohorts using normative models… *Biol Psychiatry* 2016.  
- Marquand AF, et al. Conceptualizing mental disorders as deviations from
  normative functioning. *Mol Psychiatry* 2019.  
- Rutherford S, et al. The normative modeling framework for computational
  psychiatry. *Nature Protocols* 2022.
