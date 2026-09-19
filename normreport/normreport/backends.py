"""Normative-modelling backend registry + wrappers.

Each backend implements the `NormativeBackend` protocol:
    name: str
    reference_cohort_id: str
    def score(subject: dict, reference: pd.DataFrame) -> ScoringResult

Three backends ship:
1. CentileBrain-MFP        — subprocess-wraps score/score_centilebrain.R
2. CentileBrain-GAMLSS     — subprocess-wraps score/score_centilebrain_gamlss.R
3. PCN Toolkit-Bayesian    — real per-subject scoring against the
                              lifespan_DK_46K_59sites hierarchical Bayesian
                              regression models (Rutherford et al. 2022);
                              cortical thickness only.
                              A NaN-returning stub is kept for tests when
                              the model bundle is not present locally
                              (PCNBayesianStub).

Site adaptation (mu_hat) follows Rutherford et al., Nature Protocols
2022 — the field-standard procedure. See ../mu_hat.md for full
methodology + citations.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
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
    """NaN-returning stub kept for tests when the pcn_models/braincharts
    bundle is not present locally. The real PCNBayesian backend above
    calls the pre-trained models directly; this stub is only used when
    the user explicitly requests ``pcn_bayesian_stub`` from the CLI."""

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


# --------------------------------------------------------------------------
# PCN Toolkit — real per-subject scoring
# --------------------------------------------------------------------------


def _ideas_to_pcn_cortical(ideas_col: str) -> Optional[str]:
    """lh_bankssts_thickness -> L_bankssts; rh_insula_thickness -> R_insula."""
    for h_ideas, h_pcn in (("lh_", "L_"), ("rh_", "R_")):
        if ideas_col.startswith(h_ideas) and ideas_col.endswith("_thickness"):
            return h_pcn + ideas_col[len(h_ideas):-len("_thickness")]
    return None


def _load_lines(path: Path) -> list:
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


class PCNBayesian(NormativeBackend):
    """PCN Toolkit lifespan_DK_46K_59sites hierarchical Bayesian regression
    (Rutherford et al., Nature Protocols 2022 / eLife 2022).

    Cortical thickness only — the distributed Desikan–Killiany lifespan
    bundle covers ~68 cortical thickness IDPs. Surface area and
    subcortical volumes need the CentileBrain backends.

    Site adaptation is via the PCN Toolkit's built-in mechanism: the
    reference cohort supplies adaptation data, and each patient is
    scored against the adapted model.
    """

    name = "pcn-bayesian-v1.0"
    reference_cohort_id = "ideas-controls-2025"

    # Model files live under REPO_ROOT/pcn_models/braincharts by default;
    # can be overridden for testing.
    def __init__(self, model_root: Optional[Path] = None):
        self.model_root = Path(model_root) if model_root else (
            REPO_ROOT / "pcn_models" / "braincharts"
        )

    def score(self, subject: dict, reference: pd.DataFrame) -> ScoringResult:
        model_dir = (self.model_root / "models" / "lifespan_DK_ct"
                     / "lifespan_DK_46K_59sites")
        docs_dir = self.model_root / "docs"

        if not model_dir.exists() or not docs_dir.exists():
            return ScoringResult(
                backend_name=self.name,
                reference_cohort_id=self.reference_cohort_id,
                long_df=pd.DataFrame(columns=[
                    "measure", "region", "observed", "z_adapted"]),
                warnings=[
                    f"PCN Toolkit lifespan_DK_46K_59sites bundle not found at "
                    f"{model_dir}. See SETUP.md for setup. Backend returned "
                    f"no scores; consensus flagging will proceed with the "
                    f"remaining backends only."
                ],
            )

        # Late imports so callers that never ask for this backend don't
        # pay the pcntoolkit startup cost.
        import warnings
        warnings.filterwarnings("ignore")
        scripts_dir = str(self.model_root / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from pcntoolkit.normative import predict          # noqa: E402
        from pcntoolkit.util.utils import create_design_matrix  # noqa: E402

        # Region + site metadata
        pcn_names = set(
            _load_lines(docs_dir / "phenotypes_ct_dk_lh.txt")
            + _load_lines(docs_dir / "phenotypes_ct_dk_rh.txt")
        )
        site_ids_tr = _load_lines(docs_dir / "site_ids_ct_dk_59sites.txt")

        # Adaptation frame — reference cohort (controls).
        ref = reference.copy()
        ref["sex"] = ref["sex"].astype(str).str.upper().str.strip()
        ref = ref[ref["sex"].isin(["M", "F"])]
        ref = ref[ref["age"].notna()].reset_index(drop=True)
        ref["sex_bin"] = (ref["sex"] == "M").astype(int)
        ref["site"] = "SUBJECT_SITE"
        ref["sitenum"] = len(site_ids_tr)

        # Test frame — single subject.
        subj_row = dict(subject)
        subj_row["sex_bin"] = (
            1 if str(subj_row.get("sex", "")).upper().strip() == "M" else 0
        )
        subj_row["site"] = "SUBJECT_SITE"
        subj_row["sitenum"] = len(site_ids_tr)
        subj_row["age"] = float(subj_row["age"])
        te = pd.DataFrame([subj_row])

        # Which IDPs can we score? Need (a) the column in subject + reference,
        # (b) a PCN-named model directory in the bundle.
        idps = []
        for c in te.columns:
            pcn_name = _ideas_to_pcn_cortical(c) if isinstance(c, str) else None
            if pcn_name is None or pcn_name not in pcn_names:
                continue
            if c not in ref.columns:
                continue
            if not (model_dir / pcn_name / "Models").exists():
                continue
            idps.append((c, pcn_name))

        if not idps:
            return ScoringResult(
                backend_name=self.name,
                reference_cohort_id=self.reference_cohort_id,
                long_df=pd.DataFrame(columns=[
                    "measure", "region", "observed", "z_adapted"]),
                warnings=[
                    "PCN Toolkit backend: no cortical-thickness IDPs matched "
                    "between subject, reference, and the pre-trained bundle."
                ],
            )

        # pcntoolkit's file-based predict() expects the test cov file to
        # parse back as a 2D array. np.savetxt / np.loadtxt of a single-
        # row matrix silently collapses to 1D. Pad the test frame with a
        # duplicate row so N=2, and pick off row 0 from the Z output.
        te = pd.concat([te, te], ignore_index=True)

        # Build once — design matrices are IDP-agnostic.
        cov_te = create_design_matrix(
            te[["age", "sex_bin"]].rename(columns={"sex_bin": "sex"}),
            site_ids=te["site"], all_sites=site_ids_tr,
            basis="bspline", xmin=-5, xmax=110,
        )
        cov_ad = create_design_matrix(
            ref[["age", "sex_bin"]].rename(columns={"sex_bin": "sex"}),
            site_ids=ref["site"], all_sites=site_ids_tr,
            basis="bspline", xmin=-5, xmax=110,
        )

        results = []
        warnings_out = []
        cwd = os.getcwd()
        with tempfile.TemporaryDirectory(prefix="pcn_cli_") as td:
            td = Path(td)
            cov_te_f = td / "cov_te.txt"; np.savetxt(cov_te_f, cov_te)
            cov_ad_f = td / "cov_ad.txt"; np.savetxt(cov_ad_f, cov_ad)
            snum_te_f = td / "sitenum_te.txt"
            np.savetxt(snum_te_f, te["sitenum"].to_numpy(dtype=int))
            snum_ad_f = td / "sitenum_ad.txt"
            np.savetxt(snum_ad_f, ref["sitenum"].to_numpy(dtype=int))

            fail = 0
            for ideas_name, pcn_name in idps:
                resp_te = td / f"resp_te_{pcn_name}.txt"
                resp_ad = td / f"resp_ad_{pcn_name}.txt"
                np.savetxt(resp_te, te[ideas_name].to_numpy())
                np.savetxt(resp_ad, ref[ideas_name].to_numpy())

                idp_workdir = td / pcn_name
                idp_workdir.mkdir(exist_ok=True)
                os.chdir(idp_workdir)
                try:
                    yhat, s2, Z = predict(
                        str(cov_te_f), alg="blr", respfile=str(resp_te),
                        model_path=str(model_dir / pcn_name / "Models"),
                        adaptrespfile=str(resp_ad),
                        adaptcovfile=str(cov_ad_f),
                        adaptvargroupfile=str(snum_ad_f),
                        testvargroupfile=str(snum_te_f),
                    )
                except Exception as exc:      # noqa: BLE001
                    fail += 1
                    if fail <= 3:
                        warnings_out.append(
                            f"PCN Toolkit: {pcn_name} failed — {exc}"
                        )
                    continue
                finally:
                    os.chdir(cwd)

                # Z is (2,) from the padded test frame; take row 0.
                z_arr = np.asarray(Z).ravel()
                results.append({
                    "measure": "thickness",
                    "region": ideas_name,
                    "observed": float(te[ideas_name].iloc[0]),
                    "z_adapted": float(z_arr[0]),
                })

        if fail > 3:
            warnings_out.append(
                f"PCN Toolkit: {fail - 3} further IDP failures suppressed."
            )
        return ScoringResult(
            backend_name=self.name,
            reference_cohort_id=self.reference_cohort_id,
            long_df=pd.DataFrame(results),
            warnings=warnings_out,
        )


REGISTRY = {
    "centilebrain_mfp":    CentileBrainMFP,
    "centilebrain_gamlss": CentileBrainGAMLSS,
    "pcn_bayesian":        PCNBayesian,
    "pcn_bayesian_stub":   PCNBayesianStub,
}


def get_backend(name: str) -> NormativeBackend:
    if name not in REGISTRY:
        raise ValueError(f"Unknown backend: {name}. Available: {sorted(REGISTRY)}")
    return REGISTRY[name]()
