"""PDF report generator.

Produces a single-page A4 per-patient report combining Z-scores from all
requested backends, sorted by |Z|, with cross-backend consensus flag and
"For research use only" disclaimer.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)


def _consensus_flag(row) -> str:
    """Given per-backend Z columns, return CONSENSUS / DIVERGENT / SINGLE."""
    vals = [row[c] for c in row.index if c.startswith("z_")
            and pd.notna(row[c])]
    if len(vals) == 0:
        return "no data"
    n_extreme = sum(abs(v) > 2 for v in vals)
    if n_extreme == 0:
        return "within-normal"
    if n_extreme == len(vals):
        return "CONSENSUS ABNORMAL"
    return "divergent"


def _colour_for_z(z: float):
    if pd.isna(z):
        return colors.lightgrey
    a = abs(z)
    if a > 2:
        return colors.pink
    if a > 1:
        return colors.HexColor("#FFF2B2")
    return colors.HexColor("#DFF5D4")


def build_report(subject_id: str, age: float, sex: str,
                 scored_dfs: dict, reference_id: str,
                 output_dir: Path, git_sha: str = "unknown") -> Path:
    """Compose a PDF report from a dict of {backend_name: long_df}.

    Returns the path to the generated PDF.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"{subject_id}_report.pdf"

    # Merge all backends' Z-scores into a wide table for the report
    wide = None
    for backend_name, df in scored_dfs.items():
        z_col = f"z_{backend_name}"
        piece = df[["measure", "region", "observed", "z_adapted"]].copy()
        piece = piece.rename(columns={"z_adapted": z_col})
        if wide is None:
            wide = piece
        else:
            wide = wide.merge(piece[["measure", "region", z_col]],
                              on=["measure", "region"], how="outer")

    if wide is None or len(wide) == 0:
        raise ValueError("No backend outputs to render.")

    wide["max_abs_z"] = wide[[c for c in wide.columns
                              if c.startswith("z_")]].abs().max(axis=1)
    wide["consensus"] = wide.apply(_consensus_flag, axis=1)
    wide = wide.sort_values("max_abs_z", ascending=False)

    # ---- Build PDF ---------------------------------------------------
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4,
                            topMargin=1.5*cm, bottomMargin=1.5*cm,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            title=f"Normative brain report — {subject_id}")
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        "header", parent=styles["Heading1"], fontSize=13, leading=15,
        spaceAfter=2, alignment=1
    )
    meta_style = ParagraphStyle(
        "meta", parent=styles["Normal"], fontSize=9, leading=11,
        spaceAfter=4
    )
    small_style = ParagraphStyle(
        "small", parent=styles["Normal"], fontSize=7, leading=9,
        textColor=colors.grey
    )
    body_style = ParagraphStyle(
        "body", parent=styles["Normal"], fontSize=9, leading=11,
        spaceAfter=6
    )

    story = []
    story.append(Paragraph("Normative Brain Morphometry Report", header_style))
    story.append(Paragraph(
        f"Subject <b>{subject_id}</b> &nbsp;|&nbsp; age {age:.1f} y "
        f"&nbsp;|&nbsp; sex {sex} &nbsp;|&nbsp; report generated "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        meta_style))
    backends_str = ", ".join(scored_dfs.keys())
    story.append(Paragraph(
        f"Backends: <b>{backends_str}</b> &nbsp;|&nbsp; "
        f"Reference cohort: <b>{reference_id}</b> &nbsp;|&nbsp; "
        f"Repo SHA: {git_sha[:8]}",
        meta_style))
    story.append(Spacer(1, 0.3*cm))

    # Table: top-20 regions by |Z|
    top = wide.head(20)
    z_cols = [c for c in top.columns if c.startswith("z_")]
    header = ["Region", "Measure", "Obs"] + [c.replace("z_", "") for c in z_cols] + ["Flag"]
    rows = [header]
    for _, r in top.iterrows():
        row = [
            r["region"], r["measure"],
            f"{r['observed']:.2f}" if pd.notna(r["observed"]) else "—",
        ]
        for zc in z_cols:
            row.append(f"{r[zc]:+.2f}" if pd.notna(r[zc]) else "—")
        row.append(r["consensus"])
        rows.append(row)

    tbl = Table(rows, colWidths=[4.8*cm, 1.8*cm, 1.3*cm] +
                                [1.6*cm]*len(z_cols) + [2.5*cm])
    ts = TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#333333")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("ALIGN", (2, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ])
    # Colour the max-|Z| cell per row
    for i in range(1, len(rows)):
        max_z_this = top.iloc[i - 1]["max_abs_z"]
        colour = colors.pink if max_z_this > 2 else (
            colors.HexColor("#FFF2B2") if max_z_this > 1
            else colors.HexColor("#DFF5D4"))
        ts.add("BACKGROUND", (-1, i), (-1, i), colour)
    tbl.setStyle(ts)
    story.append(tbl)
    story.append(Spacer(1, 0.4*cm))

    # Interpretation paragraph
    n_consensus = (wide["consensus"] == "CONSENSUS ABNORMAL").sum()
    n_divergent = (wide["consensus"] == "divergent").sum()
    interp = (
        f"<b>Interpretation.</b> Of {len(wide)} regions scored, "
        f"<font color='red'><b>{n_consensus}</b></font> are flagged "
        f"as abnormal by every backend used (|Z| > 2 in all); "
        f"<b>{n_divergent}</b> are flagged by at least one backend but "
        f"not others (interpret with caution — model disagreement suggests "
        f"a region where scoring is sensitive to algorithmic choice). "
        f"The remaining {len(wide) - n_consensus - n_divergent} regions are "
        f"within the expected range."
    )
    story.append(Paragraph(interp, body_style))
    story.append(Spacer(1, 0.3*cm))

    # Footer / caveats
    footer = (
        "<b>For research use only.</b> This report is generated by "
        f"<font face='Courier'>normreport v0.1.0</font> and reflects normative "
        "deviation scores computed against the reference cohort noted above. "
        "Site adaptation follows the standard PCN Toolkit protocol "
        "(Rutherford et al., <i>Nature Protocols</i> 2022). The bundled "
        "reference cohort is IDEAS-controls-2025 (100 UK controls scanned "
        "on Newcastle 3T Siemens Prisma); for clinical deployment, use a "
        "site-matched reference cohort with ≥ 30 subjects per sex "
        "(see the accompanying paper's mu_hat.md for methodology). "
        "Backend citations: CentileBrain — Ge et al., <i>Lancet Digital "
        "Health</i> 2024; PCN Toolkit — Rutherford et al., <i>Nature "
        "Protocols</i> 2022; BrainMoNoCle (optional) — Little et al., "
        "<i>Imaging Neuroscience</i> 2025."
    )
    story.append(Paragraph(footer, small_style))

    doc.build(story)
    return pdf_path
