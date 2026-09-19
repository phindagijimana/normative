"""normreport — multi-backend normative brain-morphometry report generator.

Wraps CentileBrain-MFP, CentileBrain-GAMLSS, and PCN Toolkit-Bayesian
normative-modelling backends in a single per-patient PDF report with
cross-backend consensus/disagreement flagging. Deployable inside
credentialed clinical-research pipelines (Singularity container ships
with the repository).

The scientific validation this tool operationalises is described in the
accompanying paper (see repository root: README.md, RESULTS.md, and
paper_planning/).
"""
__version__ = "0.1.0"
