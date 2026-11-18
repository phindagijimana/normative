# Advanced topics and limits

## Transfer vs retraining

| Strategy | When | In this toolkit |
|---|---|---|
| **Apply + adapt** | Published morphometry models, new scanner | Default CentileBrain / PCN path |
| **Fit locally** | Connectomes; or morphometry if you train your own | Connectome scripts |
| **Full retrain** | New phenotype, age range, or inadequate published coverage | Out of scope here |

Advanced users still usually **adapt** rather than retrain 30k–50k models
unless they have the data and compute (Rutherford et al. 2022; Ge et al. 2024).

## Hierarchical / multi-site models

PCN-style Bayesian models treat site as part of a hierarchy. That helps
generalisation across the **training** sites. A brand-new site is still a
transfer problem — hence adaptation sets.

## Uncertainty and multiple testing

- Thousands of edges ⇒ extreme counts need permutation / FDR-style control
  (connectome scripts expose `--n-perm`).  
- Dozens of regions ⇒ still correct for multiplicity in cohort studies.  
- Single-patient maps are descriptive; cohort claims need statistics.

## Failure modes experts watch for

1. **Wrong FreeSurfer / column schema** → silent mis-scoring.  
2. **Too few / poorly matched controls** → bad `mu_hat`.  
3. **Age bins (IDEAS)** → extra noise in \(\hat{\mu}(x)\).  
4. **Backend disagreement** → investigate before claiming a focal finding.  
5. **Leakage** — fitting connectome models on subjects later tested without
   CV.  
6. **Over-thresholding** — \|Z\|>2.3 on noisy edges floods “extremes.”

## What this documentation intentionally skips

Manuscript-level IDEAS results, unpublished analyses, and outreach notes stay
off the public docs. The science guide teaches **concepts + literature**;
tutorials teach **how to run the code**.

## Suggested reading order (advanced)

1. Rutherford et al., *Nature Protocols* 2022 (end-to-end practice).  
2. Ge et al., *Lancet Digital Health* 2024 (CentileBrain).  
3. Rutherford et al., *eLife* 2022 (PCN / braincharts).  
4. Marquand et al., *Mol Psychiatry* 2019 (conceptual framing).  
5. Your connectome pipeline papers + multiscale deviation papers (e.g.
   Ilioska-style FC work) if you use `connectome_normative/`.  
6. Taylor et al., *Epilepsia* 2025 if you reuse IDEAS.

## Back to practice

{doc}`../tutorials/index` · {doc}`../references`
