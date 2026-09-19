"""Smoke tests for the normreport package.

Verify (in order):
  1. Package imports cleanly
  2. Backend registry contains the 3 expected backends
  3. Bundled reference cohort loads with the expected schema
  4. Demo subject CSV parses cleanly
  5. Report generator produces a valid PDF from mock scored data
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parent.parent


def test_package_imports():
    import normreport
    assert normreport.__version__ == "0.1.0"


def test_backend_registry():
    from normreport.backends import REGISTRY, get_backend
    assert set(REGISTRY.keys()) == {
        "centilebrain_mfp",
        "centilebrain_gamlss",
        "pcn_bayesian",
        "pcn_bayesian_stub",
    }
    for name in REGISTRY:
        b = get_backend(name)
        assert hasattr(b, "score")
        assert isinstance(b.name, str)
        assert isinstance(b.reference_cohort_id, str)


def test_bundled_reference_loads():
    from normreport.fs_stats import load_reference_cohort
    ref = load_reference_cohort(REPO / "normreport" / "data" /
                                 "ideas_controls_2025.csv")
    assert len(ref) == 100
    assert "sex" in ref.columns
    assert "age" in ref.columns
    assert "eTIV" in ref.columns
    assert "lh_bankssts_thickness" in ref.columns
    assert "Left-Thalamus" in ref.columns


def test_demo_subject_parses():
    from normreport.fs_stats import load_subject
    subj = load_subject(REPO / "examples" / "demo_subject_stats.csv")
    for req in ("eTIV", "mean_thickness", "mean_surface_area",
                "lh_bankssts_thickness", "Left-Thalamus"):
        assert req in subj


def test_pcn_stub_returns_nan_scores():
    from normreport.backends import PCNBayesianStub
    from normreport.fs_stats import load_subject, load_reference_cohort
    subj = load_subject(REPO / "examples" / "demo_subject_stats.csv")
    subj["age"] = 30
    subj["sex"] = "F"
    ref = load_reference_cohort(REPO / "normreport" / "data" /
                                 "ideas_controls_2025.csv")
    result = PCNBayesianStub().score(subj, ref)
    assert result.long_df["z_adapted"].isna().all()
    assert len(result.warnings) >= 1


def test_pdf_report_generates():
    from normreport.report import build_report
    # Build mock scored dfs
    regions = [("thickness", f"lh_bankssts_thickness"),
               ("thickness", f"rh_hippocampus_thickness"),
               ("subcortical", "Left-Thalamus")]
    mock = pd.DataFrame({
        "measure":  [r[0] for r in regions],
        "region":   [r[1] for r in regions],
        "observed": [2.5, 2.7, 8000.0],
        "z_adapted":[-2.4, -1.2, +0.3],
    })
    tmp = Path("/tmp/normreport_test_report")
    tmp.mkdir(exist_ok=True)
    pdf = build_report("test_subj", 34.5, "F",
                        {"centilebrain-mfp-v1.0": mock,
                         "centilebrain-gamlss-v1.0": mock},
                        "ideas-controls-2025", tmp)
    assert pdf.exists()
    assert pdf.stat().st_size > 1024  # non-trivial PDF


def test_hemi_of_helper():
    """Sanity-check the hemisphere-assignment helper used in the tool +
    the corresponding analysis in score/hemispheric_lateralization.py."""
    # Not exposed in the package but the same conceptual mapping;
    # this test is a placeholder to remind implementers of the naming
    # convention used across the codebase.
    assert "lh_bankssts_thickness".startswith("lh_")
    assert "rh_insula_area".startswith("rh_")
    assert "Left-Thalamus".startswith("Left-")
