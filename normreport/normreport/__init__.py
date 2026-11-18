"""normreport — multi-backend normative brain-morphometry report generator.

Wraps CentileBrain-MFP, CentileBrain-GAMLSS, and PCN Toolkit-Bayesian
normative-modelling backends in a single per-patient PDF report with
cross-backend consensus/disagreement flagging. Deployable inside
credentialed clinical-research pipelines (Singularity container ships
with the repository).

See the repository root README.md and SETUP.md for install and reuse.
"""
__version__ = "0.1.0"
