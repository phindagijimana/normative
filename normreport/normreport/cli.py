"""normreport CLI entry point.

Example:
    normreport <subject_csv> --age 34 --sex F --subject-id anon_042 \\
        --backend all --output ./reports/
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import click
import pandas as pd

from . import __version__
from .backends import REGISTRY, get_backend
from .fs_stats import load_subject, load_reference_cohort
from .report import build_report


DEFAULT_REFERENCE = (Path(__file__).parent / "data" /
                     "ideas_controls_2025.csv")


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(Path(__file__).resolve().parent.parent.parent),
             "rev-parse", "HEAD"], text=True, timeout=5).strip()
    except Exception:
        return "unknown"


@click.command()
@click.argument("subject", type=click.Path(exists=True))
@click.option("--age", type=float, required=True,
              help="Subject age in years")
@click.option("--sex", type=click.Choice(["M", "F"], case_sensitive=False),
              required=True, help="Subject sex")
@click.option("--subject-id", "subject_id", type=str, default=None,
              help="Subject identifier (defaults to file basename)")
@click.option("--backend", "backend_spec", type=str, default="centilebrain_mfp,centilebrain_gamlss",
              help="Comma-separated backend list, or 'all'. "
                   f"Available: {sorted(REGISTRY)}")
@click.option("--reference", "reference_path",
              type=click.Path(exists=True), default=str(DEFAULT_REFERENCE),
              help="Reference cohort CSV (defaults to bundled IDEAS-controls-2025)")
@click.option("--output", "output_dir", type=click.Path(), required=True,
              help="Output directory for the report bundle")
@click.version_option(version=__version__)
def main(subject: str, age: float, sex: str, subject_id: str | None,
         backend_spec: str, reference_path: str, output_dir: str):
    """Generate a per-patient normative brain-morphometry report.

    Wraps CentileBrain-MFP + CentileBrain-GAMLSS + PCN Toolkit-Bayesian
    backends in a single PDF report with cross-backend consensus flag.

    For research use only. See the accompanying paper for validation
    context and mu_hat.md for the site-adaptation methodology.
    """
    subject_path = Path(subject)
    if subject_id is None:
        subject_id = subject_path.stem

    click.echo(f"normreport v{__version__} — subject {subject_id}")

    # Backends
    if backend_spec == "all":
        backend_names = list(REGISTRY.keys())
    else:
        backend_names = [b.strip() for b in backend_spec.split(",") if b.strip()]

    # Load subject + reference
    subj_dict = load_subject(subject_path)
    subj_dict.setdefault("subject_id", subject_id)
    subj_dict["age"] = age
    subj_dict["sex"] = sex.upper()

    reference_id = Path(reference_path).stem
    reference = load_reference_cohort(reference_path)
    click.echo(f"  Reference cohort: {reference_id} (N={len(reference)}, "
               f"F={(reference['sex']=='F').sum()}, "
               f"M={(reference['sex']=='M').sum()})")

    # Score with each backend
    scored: dict = {}
    all_warnings: list = []
    for name in backend_names:
        backend = get_backend(name)
        click.echo(f"  Scoring with {backend.name} ...")
        try:
            result = backend.score(subj_dict, reference)
            scored[backend.name] = result.long_df
            all_warnings.extend(result.warnings)
        except Exception as e:
            click.echo(f"    ERROR: {e}", err=True)
            all_warnings.append(f"{backend.name} failed: {e}")

    if not scored:
        click.echo("No backend produced output — aborting.", err=True)
        sys.exit(1)

    # Emit outputs
    out_dir = Path(output_dir) / subject_id
    out_dir.mkdir(parents=True, exist_ok=True)

    # Long-form Z-scores across all backends
    z_rows = []
    for backend_name, df in scored.items():
        for _, r in df.iterrows():
            z_rows.append({
                "subject_id": subject_id,
                "backend": backend_name,
                "measure": r["measure"],
                "region": r["region"],
                "observed": r.get("observed"),
                "z_adapted": r.get("z_adapted"),
            })
    z_df = pd.DataFrame(z_rows)
    z_csv = out_dir / f"{subject_id}_zscores.csv"
    z_df.to_csv(z_csv, index=False)

    # Provenance
    provenance = {
        "tool": "normreport",
        "tool_version": __version__,
        "git_sha": _git_sha(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subject_id": subject_id,
        "age": age,
        "sex": sex.upper(),
        "backends": list(scored.keys()),
        "reference_cohort": reference_id,
        "reference_size": len(reference),
        "warnings": all_warnings,
    }
    (out_dir / f"{subject_id}_provenance.json").write_text(
        json.dumps(provenance, indent=2)
    )

    # Cleaned raw parse
    (out_dir / f"{subject_id}_raw.json").write_text(
        json.dumps({k: (v if not (isinstance(v, float) and (v != v)) else None)
                    for k, v in subj_dict.items()}, indent=2, default=str)
    )

    # PDF report
    pdf_path = build_report(subject_id, age, sex.upper(), scored,
                            reference_id, out_dir,
                            git_sha=provenance["git_sha"])
    click.echo(f"\nReport bundle at {out_dir}/")
    click.echo(f"  {pdf_path.name} ({pdf_path.stat().st_size / 1024:.1f} KiB)")
    click.echo(f"  {z_csv.name}")
    click.echo(f"  {subject_id}_provenance.json")
    click.echo(f"  {subject_id}_raw.json")

    if all_warnings:
        click.echo("\nWarnings:", err=True)
        for w in all_warnings:
            click.echo(f"  - {w}", err=True)


if __name__ == "__main__":
    main()
