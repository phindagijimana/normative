# Draft — Outreach email to CentileBrain team (supplementary comparison request)

> **Status: HELD IN RESERVE (not sent).**
> The paper is fully defensible without `mean_train` — the `mu_hat`
> site-adaptation procedure (Rutherford et al., *Nature Protocols*
> 2022; see `mu_hat.md`) is the field standard and does not require
> CentileBrain's training-set means. This email remains ready to send
> as a strengthening step if we decide to add a supplementary comparison
> section, or if a reviewer requests one. Revise the opening paragraph
> before sending to reflect what has been completed at that point.

**To:**  ruiyang.ge@ubc.ca, sophia.frangou@gmail.com
**Subject:**  CentileBrain MFP models — request for per-region training means as a supplementary comparison in an external-validation study

---

Dear Dr Ge and Prof Frangou,

I hope this finds you well. I am Philbert Ndagijimana, a clinical
informatics researcher at the University of Rochester Medical Center
(URMC). I am writing regarding a supplementary analysis in an external
validation of the CentileBrain MFP models we are preparing for
publication. First, thank you for making the models and platform freely
available — the pre-trained `.rds` objects on your GitHub repository
have been directly useful.

**What we did.** We validated the CentileBrain MFP models on the IDEAS
focal-epilepsy cohort (Taylor et al., *Epilepsia* 2025; 442 patients +
100 controls). We ran the scoring locally in R rather than through the
web app, because our institutional data-governance rules do not permit
uploading identifiable neuroimaging outputs to a public web service.
Because the per-region training means used to un-center MFP predictions
are not distributed with the public `.rds` files, we applied the
standard site-adaptation procedure from the PCN Toolkit normative-
modeling framework ([Rutherford et al., *Nature Protocols* 2022](https://link.springer.com/protocol/10.1007/978-1-0716-4260-3_14)):
we estimated a per-region offset from the 100 IDEAS healthy controls to
align the CentileBrain reference to the IDEAS scanning-site
distribution. This is the same adaptation procedure required by
BrainMoNoCle and other comparable platforms when applied to a new site.
The pipeline works cleanly — control Z-score standard deviations are
1.02 (thickness), 1.09 (subcortical), and 1.25 (surface area) across
the 150 Desikan-Killiany + Aseg regions, and our Z-scores correlate at
median r ≈ 0.83 with IDEAS's own ComBat-harmonised Z-scores.

**What we would like to add.** To strengthen a supplementary
methodological analysis, we would like to compare our empirical
per-region offsets against the actual training-set means that
CentileBrain fit against. Concretely, this would let us:

* Quantify how faithfully the site-adaptation procedure recovers the
  true un-centering constants — a genuine methodological contribution
  useful to any future external validator.
* Present two versions of Task 5 (control calibration): one with the
  site-adapted offsets, one with the true training means, side by side.
* Confirm that our qualitative findings (thickness calibrates best,
  surface area shows ~25 % over-dispersion, classification AUC 0.80 for
  epilepsy vs. control) are robust to the choice of un-centering
  reference.

**What we are asking for**, if you are willing to share:

1. The 300 per-region training means used to un-center MFP predictions
   — 68 cortical thickness + 68 cortical surface area + 14 subcortical
   volume regions × 2 sexes, in whatever format is easiest (a small
   CSV or `.rds`).
2. Optionally, any per-region training standard deviations if these
   differ from the model residuals' RMSE.

We understand entirely if these values were intentionally kept
server-side — the web app is the intended user interface and it
harmonises via ComBat-GAM which is the fuller pipeline. Our request is
purely to enable a stronger supplementary comparison in the validation
paper, not a claim that the models cannot be used offline.

**What we would commit to in return:**

* The paper will properly cite Ge et al. 2024 (as it already does) and
  the 2022 PCN Toolkit protocol for the adaptation procedure. Any use
  of your training means would be attributed explicitly.
* We are happy to share preprints with you before submission and would
  welcome your comments; if the exchange shapes the methods, we would
  offer co-authorship as appropriate.
* If it would be useful to the broader community, we could contribute
  a small pull request to the CentileBrain GitHub repository adding the
  per-region training means plus documentation of the offline scoring
  recipe (with your review).

Thank you again for building CentileBrain — external-validation studies
like ours would not be possible without the pre-trained models being
publicly available.

Best regards,

Philbert Ndagijimana
Clinical Informatics Researcher, URMC
philbert_ndagijimana@urmc.rochester.edu

---

## Notes for you before sending

- **Addressees**: Dr Ge (first author) and Prof Frangou (senior author).
  Both are listed as the contact addresses in the CentileBrain
  instructions PDF and on the `/model2` page.
- **Framing change from the earlier draft**: this version does not
  imply we are stuck without the training means. It presents our work
  as a completed validation using the standard PCN Toolkit adaptation
  procedure, and requests the training means as an *enhancement* for a
  supplementary comparison. This is both more accurate and gives them
  a face-saving reason to help (contribute to a stronger paper) rather
  than treating the request as a bug report.
- **The "small pull request" offer** is a genuine olive branch — no
  cost to us, low-effort way for them to say yes.
- **What NOT to promise**: don't offer to share IDEAS-derived Z-scores
  or raw data — the IDEAS release is CNNP's to distribute.
- **Timing**: reasonable to wait 2–3 weeks; a gentle follow-up if no
  reply. The validation paper is fully defensible without this
  supplementary comparison, so there is no schedule risk in waiting.
