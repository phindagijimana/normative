"""Normative-modelling backend registry + wrappers.

Each backend implements the `NormativeBackend` protocol:
    name: str
    reference_cohort_id: str
    def score(subject: dict, reference: pd.DataFrame) -> pd.DataFrame
        columns: region, observed, predicted, z_raw, z_adapted

MVP ships three backends:
1. CentileBrain-MFP        — subprocess-wraps score/score_centilebrain.R
2. CentileBrain-GAMLSS     — subprocess-wraps score/score_centilebrain_gamlss.R
3. PCN Toolkit-Bayesian    — STUB (see paper_planning/PAPER_PLAN.md §1 —
                              deep PCN Toolkit integration deferred; stub
                              returns NaN scores with a clear log message)

Site adaptation (mu_hat) follows Rutherford et al., Nature Protocols
2022 — the field-standard procedure. See ../mu_hat.md for full
methodology + citations.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # normative/


@dataclass
class ScoringResult:
    backend_name: str
    reference_cohort_id: str
    long_df: pd.DataFrame  # cols: region, measure, observed, z_raw, z_adapted
    warnings: list


class NormativeBackend:
    """Base class / registry entry."""

    name: str = "base"
    reference_cohort_id: str = "ideas-controls-2025"

    def score(self, subject: dict, reference: pd.DataFrame) -> ScoringResult:
        raise NotImplementedError


# --------------------------------------------------------------------------
# CentileBrain wrappers — call the R scripts as subprocess
# --------------------------------------------------------------------------

def _write_temp_csv(rows: list, path: Path):
    pd.DataFrame(rows).to_csv(path, index=False)


def _run_r_scoring_script(script_name: str, subject_row: dict,
                          reference: pd.DataFrame,
                          tmpdir: Path) -> pd.DataFrame:
    """Merge subject + reference into a single ideas_merged-shaped CSV,
    invoke the R scoring script against it via Rscript, return the long-
    form Z-score CSV the script produces."""
    subj_df = pd.DataFrame([subject_row])
    subj_df["cohort"] = "patient"
    # If subject lacks subject_id, assign one for consistency
    if "subject_id" not in subj_df:
        subj_df["subject_id"] = 999999
    ref_df = reference.copy()
    ref_df["cohort"] = "control"
    merged = pd.concat([subj_df, ref_df], ignore_index=True)

    merged_path = tmpdir / "ideas_merged.csv"
    merged.to_csv(merged_path, index=False)

    # The shipped R scripts read a fixed path. For MVP we monkeypatch by
    # setting IDEAS_CSV via env var isn't wired; instead run a small
    # wrapper R script that sources ours with a substituted path.
    r_script_src = REPO_ROOT / "score" / script_name
    if not r_script_src.exists():
        raise FileNotFoundError(f"R scoring script not found: {r_script_src}")
    r_wrap = tmpdir / f"wrap_{script_name}"
    contents = r_script_src.read_text()
    # Redirect the hard-coded ROOT + IDEAS_CSV + OUT_DIR to our tmpdir
    contents = contents.replace(
        'ROOT     <- "/mnt/nfs/home/URMC-SH/pndagiji/Documents/Normative"',
        f'ROOT     <- "{REPO_ROOT}"'
    ).replace(
        'ROOT      <- "/mnt/nfs/home/URMC-SH/pndagiji/Documents/Normative"',
        f'ROOT      <- "{REPO_ROOT}"'
    ).replace(
        'IDEAS_CSV<- file.path(ROOT, "ideas_data/ideas_merged.csv")',
        f'IDEAS_CSV<- "{merged_path}"'
    ).replace(
        'IDEAS_CSV <- file.path(ROOT, "ideas_data/ideas_merged.csv")',
        f'IDEAS_CSV <- "{merged_path}"'
    ).replace(
        'OUT_DIR  <- file.path(ROOT, "score")',
        f'OUT_DIR  <- "{tmpdir}"'
    ).replace(
        'OUT_DIR   <- file.path(ROOT, "score")',
        f'OUT_DIR   <- "{tmpdir}"'
    )
    r_wrap.write_text(contents)

    result = subprocess.run(
        ["Rscript", str(r_wrap)], capture_output=True, text=True, timeout=600
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"R scoring script failed:\nSTDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    # Locate the long-form Z-scores CSV produced
    for candidate in ("ideas_zscores_centilebrain.csv",
                      "ideas_zscores_centilebrain_gamlss.csv"):
        p = tmpdir / candidate
        if p.exists():
            return pd.read_csv(p)
    raise RuntimeError(f"No expected output CSV in {tmpdir}")


class CentileBrainMFP(NormativeBackend):
    name = "centilebrain-mfp-v1.0"
    reference_cohort_id = "ideas-controls-2025"

    def score(self, subject: dict, reference: pd.DataFrame) -> ScoringResult:
        with tempfile.TemporaryDirectory() as td:
            full = _run_r_scoring_script(
                "score_centilebrain.R", subject, reference, Path(td)
            )
        subj_id = subject.get("subject_id", 999999)
        subj_rows = full[full["subject_id"] == subj_id][
            ["measure", "region", "observed", "predicted", "rmse_m", "z"]
        ].copy()
        subj_rows.rename(columns={"z": "z_adapted"}, inplace=True)
        return ScoringResult(
            backend_name=self.name,
            reference_cohort_id=self.reference_cohort_id,
            long_df=subj_rows,
            warnings=[],
        )


class CentileBrainGAMLSS(NormativeBackend):
    name = "centilebrain-gamlss-v1.0"
    reference_cohort_id = "ideas-controls-2025"

    def score(self, subject: dict, reference: pd.DataFrame) -> ScoringResult:
        with tempfile.TemporaryDirectory() as td:
            full = _run_r_scoring_script(
                "score_centilebrain_gamlss.R", subject, reference, Path(td)
            )
        subj_id = subject.get("subject_id", 999999)
        subj_rows = full[full["subject_id"] == subj_id][
            ["measure", "region", "observed", "z"]
        ].copy()
        subj_rows.rename(columns={"z": "z_adapted"}, inplace=True)
        return ScoringResult(
            backend_name=self.name,
            reference_cohort_id=self.reference_cohort_id,
            long_df=subj_rows,
            warnings=[],
        )


# --------------------------------------------------------------------------
# PCN Toolkit backend — STUB
# --------------------------------------------------------------------------

class PCNBayesianStub(NormativeBackend):
    """v0.1.x stub retained for testing.

    Real PCN-Bayesian scoring is now implemented in the accompanying
    ``score/score_pcn_toolkit.py`` script and produces the file
    ``score/ideas_zscores_pcn.csv`` (cortical thickness, 68 regions,
    Rutherford et al. 2022 lifespan_DK_46K_59sites model with the
    PCN Toolkit's built-in site-adaptation using IDEAS controls). See
    the manuscript §Methods for details. Wrapping the real scoring
    behind the ``NormativeBackend`` interface for on-demand per-patient
    invocation from the CLI is a v0.2.0 task; the current release ships
    this stub so that ``--backend all`` runs without errors and clearly
    reports PCN's status."""

    name = "pcn-bayesian-stub-v0.1"
    reference_cohort_id = "ideas-controls-2025"

    def score(self, subject: dict, reference: pd.DataFrame) -> ScoringResult:
        # Emit NaN Z-scores with the expected schema. The consumer can
        # detect NaN and gracefully drop from consensus flagging.
        # Region list matches the CentileBrain schema (150 regions).
        DK = ["bankssts","caudalanteriorcingulate","caudalmiddlefrontal","cuneus",
              "entorhinal","fusiform","inferiorparietal","inferiortemporal",
              "isthmuscingulate","lateraloccipital","lateralorbitofrontal","lingual",
              "medialorbitofrontal","middletemporal","parahippocampal","paracentral",
              "parsopercularis","parsorbitalis","parstriangularis","pericalcarine",
              "postcentral","posteriorcingulate","precentral","precuneus",
              "rostralanteriorcingulate","rostralmiddlefrontal","superiorfrontal",
              "superiorparietal","superiortemporal","supramarginal","frontalpole",
              "temporalpole","transversetemporal","insula"]
        ASEG = ["Left-Thalamus","Right-Thalamus","Left-Caudate","Right-Caudate",
                "Left-Putamen","Right-Putamen","Left-Pallidum","Right-Pallidum",
                "Left-Hippocampus","Right-Hippocampus","Left-Amygdala","Right-Amygdala",
                "Left-Accumbens-area","Right-Accumbens-area"]
        rows = []
        for hemi in ("lh", "rh"):
            for r in DK:
                rows.append({"measure": "thickness",
                              "region": f"{hemi}_{r}_thickness",
                              "observed": subject.get(f"{hemi}_{r}_thickness", np.nan),
                              "z_adapted": np.nan})
                rows.append({"measure": "area",
                              "region": f"{hemi}_{r}_area",
                              "observed": subject.get(f"{hemi}_{r}_area", np.nan),
                              "z_adapted": np.nan})
        for r in ASEG:
            rows.append({"measure": "subcortical",
                          "region": r,
                          "observed": subject.get(r, np.nan),
                          "z_adapted": np.nan})
        return ScoringResult(
            backend_name=self.name,
            reference_cohort_id=self.reference_cohort_id,
            long_df=pd.DataFrame(rows),
            warnings=[
                "PCN Toolkit backend is a v1.0 stub. Real integration with "
                "Rutherford et al. 2022 pre-trained lifespan models is on the "
                "post-publication v1.1 roadmap."
            ],
        )


REGISTRY = {
    "centilebrain_mfp":    CentileBrainMFP,
    "centilebrain_gamlss": CentileBrainGAMLSS,
    "pcn_bayesian":        PCNBayesianStub,
}


def get_backend(name: str) -> NormativeBackend:
    if name not in REGISTRY:
        raise ValueError(f"Unknown backend: {name}. Available: {sorted(REGISTRY)}")
    return REGISTRY[name]()
