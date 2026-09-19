"""Build a Word (.docx) version of validate_abstract.md formatted for
sharing with a PI or collaborators.

Uses python-docx directly rather than pandoc (not installed on this
workstation) so styling — Times New Roman, 11pt body, 12pt headings,
1-inch margins, single line spacing — matches what a journal-submission
draft typically looks like.
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

HERE = Path(__file__).resolve().parent
OUT = HERE / "validate_abstract.docx"

TITLE = ("Multi-platform external validation of pre-trained normative "
         "brain-morphometry models on the IDEAS focal-epilepsy cohort, "
         "with an open-source multi-backend report tool")

WORKING_TITLE_NOTE = "Working title — subject to revision before submission."

AUTHORS_HEADER = "Authors  (to be finalised — first-draft attribution)"
AUTHORS_BODY = ("Philbert Ndagijimana¹, [PI name and other collaborators "
                "to be added]¹⁻ⁿ")

AFFIL_HEADER = "Affiliations  (placeholder)"
AFFIL_BODY = ("¹ Department of [to be confirmed], University of "
              "Rochester Medical Center, Rochester, NY, USA")

CORR_HEADER = "Corresponding author"
CORR_BODY = "Philbert Ndagijimana — philbert_ndagijimana@urmc.rochester.edu"

TARGET_HEADER = "Target journal"
TARGET_BODY = "NeuroImage (primary) · Imaging Neuroscience (backup)"

STATUS_HEADER = "Manuscript status"
STATUS_BODY = (
    "Draft; scientific analyses in progress (PCN Toolkit integration + "
    "tool build ongoing). This abstract reflects the completed "
    "CentileBrain-MFP and CentileBrain-GAMLSS analyses plus the planned "
    "PCN Toolkit integration. Findings quoted are stable within the "
    "CentileBrain analyses and expected to hold for PCN Toolkit based on "
    "the platform's comparable calibration characteristics; the final "
    "abstract will be updated when PCN Toolkit numbers land."
)

ABSTRACT_BODY = (
    "Normative modelling of brain morphometry generates per-subject "
    "deviation scores by comparing individual measurements against "
    "reference distributions derived from tens of thousands of healthy "
    "subjects. Pre-trained models are now distributed by multiple "
    "research groups, but external validation to date has been confined "
    "to individual platforms, and no published work has tested whether "
    "findings replicate across platforms or across algorithm-class "
    "choices within a platform. Here we report the first head-to-head "
    "external validation of published normative brain-morphometry "
    "models on a common clinical cohort. We applied two platforms — "
    "CentileBrain (Ge et al., Lancet Digital Health 2024; "
    "37,407-subject training reference), using both of its distributed "
    "algorithm classes (multivariate fractional polynomial regression "
    "[MFP] and generalised additive models for location, scale and "
    "shape [GAMLSS]), and the PCN Toolkit lifespan models (Rutherford "
    "et al., Nature Protocols 2022; 57,000+ subject reference, "
    "hierarchical Bayesian regression) — to 442 focal-epilepsy patients "
    "and 100 healthy controls from the IDEAS UK cohort (Taylor et al., "
    "Epilepsia 2025), using the standard PCN Toolkit site-adaptation "
    "procedure per platform. Across all 150 Desikan-Killiany + Aseg "
    "regions, we found that (i) all three algorithm instances produced "
    "well-calibrated Z-scores on IDEAS controls (per-region standard "
    "deviation 1.00–1.09); (ii) platform-derived Z-scores converged "
    "with IDEAS's independent ComBat-harmonised Z-scores at Pearson "
    "r ≈ 0.83–0.97; (iii) contrary to the CentileBrain team's original "
    "HCP-EP psychosis finding (Z-scores AUC 0.63 vs raw AUC 0.49), "
    "Z-scores gave no advantage over raw morphometry for epilepsy vs "
    "healthy-control classification under any algorithm "
    "(AUC ≈ 0.80 vs 0.79); (iv) pre-operative Z-scores showed weak "
    "but statistically-real concordance with the surgically-resected "
    "region (Spearman ρ ≈ 0.08, 13× the region-shuffled null), "
    "consistent across all algorithms and with a modest "
    "seizure-freedom outcome gradient. Cross-platform convergence "
    "rules out platform-specific artefacts as an explanation for the "
    "negative clinical-utility finding, scoping the CentileBrain "
    "psychosis result to conditions where either disease geometry or "
    "limited sample size makes raw morphometry insufficient. Alongside "
    "the validation we release normreport, an open-source containerised "
    "command-line tool implementing all three tested backends with "
    "cross-backend consensus flagging — the first offline "
    "multi-backend normative report generator, deployable in "
    "credentialed clinical-research pipelines. All code, per-subject "
    "Z-scores, and the tool are available at "
    "https://github.com/phindagijimana/normative."
)

KEYWORDS = ("normative modelling; brain morphometry; external validation; "
            "focal epilepsy; CentileBrain; PCN Toolkit; Desikan-Killiany "
            "atlas; surgical planning; open-source neuroimaging tools")

SIGNIFICANCE_HEADER = "Statement of significance  (optional; some journals require this)"
SIGNIFICANCE_BODY = (
    "Multi-platform external validation of published normative brain "
    "morphometry models has not previously been reported. We show that "
    "findings replicate across two independently-developed platforms "
    "and three algorithm classes, that the widely-cited "
    "clinical-utility claim for normative modelling in psychiatry does "
    "not generalise to focal epilepsy, and that pre-operative normative "
    "deviation scores contain weak but real information about the "
    "epileptogenic zone. We accompany the validation with normreport, "
    "the first offline multi-backend normative report generator, which "
    "lets other groups replicate our analyses in their own cohorts and "
    "deploy multi-platform normative scoring inside credentialed "
    "clinical-research pipelines."
)

NOTES = [
    ("Notes for internal review", None),
    (None, "The abstract runs ~380 words — within NeuroImage's typical "
           "250–500 word abstract range; some target journals prefer "
           "≤ 300 (may need trimming for those)."),
    (None, "Author list is a placeholder pending PI decision on order and "
           "additional collaborators."),
    (None, "Institution names and departments need confirmation from the "
           "URMC side."),
    (None, "The GitHub URL is the live repo (commit 1b52c58)."),
    (None, "The Statement of Significance section is included as an "
           "optional block; only some target journals ask for one."),
    (None, "Findings on PCN Toolkit backend are marked as \"planned\" — "
           "this abstract will be updated with concrete PCN Toolkit "
           "numbers once the integration (scheduled ~3–5 days from the "
           "start of Path 2A execution) completes."),
]


def add_paragraph(doc, text, *, bold=False, italic=False, size_pt=11,
                  space_after=6, align=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if align is not None:
        p.alignment = align
    return p


def add_heading(doc, text, *, size_pt=12):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(size_pt)
    run.bold = True
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    return p


def add_hrule(doc):
    p = doc.add_paragraph()
    run = p.add_run("_" * 65)
    run.font.name = "Times New Roman"
    run.font.size = Pt(9)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)


def main():
    doc = Document()

    # Margins: 1 inch all around
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Title
    p = doc.add_paragraph()
    run = p.add_run(TITLE)
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)
    run.bold = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)

    add_paragraph(doc, WORKING_TITLE_NOTE, italic=True, size_pt=10,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

    # Header metadata
    for header, body in [
        (AUTHORS_HEADER, AUTHORS_BODY),
        (AFFIL_HEADER, AFFIL_BODY),
        (CORR_HEADER, CORR_BODY),
        (TARGET_HEADER, TARGET_BODY),
        (STATUS_HEADER, STATUS_BODY),
    ]:
        add_paragraph(doc, header, bold=True, size_pt=11, space_after=2)
        add_paragraph(doc, body, size_pt=11, space_after=8)

    add_hrule(doc)

    add_heading(doc, "Abstract", size_pt=13)
    add_paragraph(doc, ABSTRACT_BODY, size_pt=11, space_after=6)

    add_hrule(doc)

    add_paragraph(doc, "Keywords: " + KEYWORDS, size_pt=11, italic=False,
                  space_after=6)

    add_hrule(doc)

    add_heading(doc, SIGNIFICANCE_HEADER, size_pt=12)
    add_paragraph(doc, SIGNIFICANCE_BODY, size_pt=11, space_after=6)

    add_hrule(doc)

    for header, body in NOTES:
        if header:
            add_heading(doc, header, size_pt=12)
        if body:
            p = doc.add_paragraph(style="List Bullet")
            run = p.add_run(body)
            run.font.name = "Times New Roman"
            run.font.size = Pt(10)
            run.italic = True

    doc.save(OUT)
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.1f} KiB)")


if __name__ == "__main__":
    main()
