# Draft — Outreach email to CNNP Lab (BrainMoNoCle team)

> **Status: HELD IN RESERVE (not sent).**
> The confirmed paper scope is 2 platforms (CentileBrain + PCN Toolkit),
> so BrainMoNoCle integration is not required for the current
> manuscript. This email is kept ready to send if (a) we decide later
> to expand scope to 3 platforms, (b) an opportunity for a follow-up
> paper arises, or (c) the CNNP team reaches out independently. Revise
> the opening paragraph before sending to reflect what has been
> completed at that point in time.

**To:**  bethany.little@newcastle.ac.uk, yujiang.wang@newcastle.ac.uk
**Cc:**  peter.taylor@newcastle.ac.uk
**Subject:**  Request for BrainMoNoCle GAMLSS model objects for multi-platform normative-modelling comparison

---

Dear Dr Little and Dr Wang,

I hope this finds you well. I am Philbert Ndagijimana, a clinical
informatics researcher at the University of Rochester Medical Center
(URMC). I am writing to ask whether you would be willing to share the
fitted GAMLSS model objects that underlie the Brain MoNoCle platform
([Little et al., *Imaging Neuroscience* 2025](https://pubmed.ncbi.nlm.nih.gov/40800979/)).

**What we are building.** We have completed an external validation of
the CentileBrain MFPR models (Ge et al., *Lancet Digit Health* 2024) on
the IDEAS cohort you released — 442 focal-epilepsy patients + 100 healthy
controls. Alongside the validation we are prototyping a per-patient
report-generation tool for research and (eventually) clinical use, built
around the FreeSurfer processing pipeline that is already standard on the
IDEAS release.

**Why we would like BrainMoNoCle's fitted models.** A single-backend
tool would be redundant with what Brain MoNoCle already provides through
your Shiny web app. However, we believe a genuinely useful contribution
would be a **multi-backend report** that runs both platforms on the same
patient and reports where they agree and disagree — a form of
robustness / sensitivity analysis for normative-model-based clinical
inference. To do this offline (and inside a credentialed clinical-
research pipeline that cannot upload identifiable data to a public web
app), we would need programmatic access to BrainMoNoCle's fitted
GAMLSS objects.

**Specifically we are asking for:**

1. The fitted GAMLSS model objects (e.g., `.rds` or `.RData`) for the
   FreeSurfer cortical thickness, cortical volume, and pial surface area
   models across the Desikan-Killiany parcellation, at the granularity
   your app exposes (region-level, hemisphere-level).
2. Any per-region training-set summary statistics your scoring pipeline
   depends on (means, SDs, distribution-shape parameters) — everything
   needed to compute centiles offline without calling the Shiny app.
3. Guidance on the correct way to apply the models to a new site without
   uploading data to your Shiny endpoint — including how the ≥ 30 local
   healthy controls requirement should be operationalised in code.

**What we would commit to in return:**

* All resulting code will cite the Little et al. 2025 paper and clearly
  attribute the GAMLSS models to your group.
* The multi-backend report tool will be open-source (likely MIT or
  Apache-2.0) on GitHub, with a design that keeps your models as an
  optional backend (so you can control any redistribution constraints).
* We will share preprints and the tool prior to any submission for your
  review, and would welcome your team as co-authors or advisors on any
  publication that uses your models directly.
* If you would prefer to keep the models private, we understand
  completely — we can note the limitation in our writeup and use only
  CentileBrain as the backend, or offer users a "point at your own
  BrainMoNoCle server" configuration option.

Happy to jump on a short call to discuss what would work for your group.
And regardless of the answer on model sharing, thank you for building
BrainMoNoCle and for releasing the IDEAS data — both have already been
enormously useful to our work.

Best regards,

Philbert Ndagijimana
Clinical Informatics Researcher, URMC
philbert_ndagijimana@urmc.rochester.edu

---

## Notes for you before sending

- **Names / titles**: I've addressed Dr Little (first author) and
  Dr Wang (senior author), cc'd Peter Taylor because he leads IDEAS
  and is the natural bridge. Adjust honorifics as you know them.
- **The Newcastle addresses above are inferred** from the CNNP lab
  page; verify before sending. If they're wrong, the CNNP lab site has
  a contact form.
- **The "co-authors or advisors" offer is a soft signal**, not a
  commitment — it makes it easier for them to say yes because they
  know they'll be credited. You can dial that up or down.
- **Timing**: two weeks is a reasonable response window; if no reply,
  a gentle follow-up is fine. If they decline or don't reply, the
  tool still works with CentileBrain as the only backend and the
  multi-backend framing becomes a "future work" note.
- **What NOT to promise**: don't offer to give them IDEAS-processed
  outputs unless you're sure that fits their data-sharing terms —
  IDEAS is their data to begin with.
