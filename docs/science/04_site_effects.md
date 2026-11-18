# Site effects and adaptation

## The transfer problem

A model trained on tens of thousands of scans can still mis-centre on a
**new scanner, coil, or FreeSurfer version**. Healthy people at the new site
then show systematically non-zero Z — a calibration failure, not “shared
pathology” (Rutherford et al., 2022).

## What the protocol literature recommends

Rutherford et al. (*Nature Protocols* 2022) describe using **local healthy
controls**, processed like the target patients, to adapt predictions or
offsets before interpreting clinical cases. Exact machinery depends on the
model family (empirical mean offset vs model-native adaptation APIs).

Practical themes across papers:

- Match acquisition and preprocessing between adaptation controls and cases  
- Prefer adequate control $N$ (often tens per sex as a rule of thumb in
  applied work; sensitivity analyses appear in protocol-oriented studies)  
- Recheck that adapted controls land near mean 0, SD 1  

## Adaptation is not the same as…

| Approach | Goal |
|---|---|
| Site adaptation of a normative model | Centre a published chart on a new site |
| ComBat / neuroHarmonize | Harmonise features across sites (different estimator) |
| Full retraining | Learn new $\hat{\mu}$, $\hat{\sigma}$ from scratch |

Choose based on data scale and whether a trusted public model already covers
your phenotype (Ge et al., 2024; Rutherford et al., 2022).

## Read next

{doc}`05_interpretation` — reading deviation maps without overclaiming.

## Key literature

- Rutherford et al., *Nature Protocols* 2022 — canonical adaptation workflow.  
- Bayer et al. / related transfer papers cited therein — site bias in
  normative models.  
- Ge et al., 2024 — applying CentileBrain outside the training distribution.
