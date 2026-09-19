# `paper_planning/` — manuscript scaffolding and decision documents

Eight files that together form the paper's connective tissue. Read them
in the order below to trace how the manuscript came together.

## Reading order

### 1. Start here — `PAPER_PLAN.md`

The living scope, execution order, journal targets, risks, and reserved
paths. Read this first to understand *what* the paper claims, *what*
scope is locked, and *what* remains conditional. Ten sections, roughly
15 pages.

### 2. Narrative — `validate_narrative.md`

The story arc for the science. Eight sections trace: the field's
promise → the gap in external validation → the IDEAS opportunity →
what we did → what we found → what it means → limitations → future
work. Written as continuous prose ready to adapt into Introduction and
Discussion. Roughly 7 pages.

### 3. Tool narrative — `tool.md`

The story arc for the `normreport` tool contribution. Seven sections
trace: the deployment gap between web apps and libraries → what the
tool is → who uses it → design decisions → v1.0 MVP scope → position vs
existing tools → roadmap. Roughly 5 pages.

### 4. Differentiation — `differentiation.md`

Quantitative analysis of contribution, novelty, and journal tier. Applies
a scoring rubric to our work and to five comparable published papers so
comparisons are honest rather than self-serving. Contains the ready-to-
adapt Introduction positioning arguments and Discussion novelty
defence. Roughly 5 pages.

### 5. Manuscript draft — `validate_manuscript.md`

The actual first-pass manuscript. ~3,900 words main text plus abstract
and references. Written in the style of *Brain Communications* (the
author's prior venue). Sections: Abstract, Introduction, Methods,
Results, Discussion, Data availability, Code availability, Author
contributions, Acknowledgements, Funding, Competing interests,
References. All placeholders clearly marked for finalisation.

### 6. Abstract for sharing — `validate_abstract.md` + `validate_abstract.docx`

The abstract extracted as a standalone document formatted for sharing
with the PI or collaborators. Same abstract as in the manuscript, plus
title/authors/keywords/statement-of-significance blocks. The `.docx`
version is generated deterministically by `_build_abstract_docx.py`;
edit the Python script and re-run to keep both formats in sync.

### 7. Build script — `_build_abstract_docx.py`

Generates the `.docx` from the abstract Markdown using `python-docx`.
Not a manuscript artefact per se — a small utility.

## Cross-references

- Scientific results the manuscript claims: `../RESULTS.md` (living)
  and per-task summary files in `../score/`.
- Site-adaptation methodology: `../mu_hat.md`.
- Source-paper (Ge et al. 2024) summary: `../normative.md`.
- Tool design that the manuscript's tool contribution operationalises:
  `../tool_design/ARCHITECTURE.md`.
- Outreach emails currently held in reserve (see `PAPER_PLAN.md` §1):
  `../tool_design/email_1_cnnp_gamlss.md`,
  `../tool_design/email_2_centilebrain_mean_train.md`.

## Suggested workflow

1. Skim `PAPER_PLAN.md` to understand scope + journal target.
2. Read `validate_narrative.md` for the scientific story.
3. Read `tool.md` for the tool contribution's framing.
4. Consult `differentiation.md` when writing Introduction (positioning
   vs prior work) or Discussion (novelty defence) sections.
5. Draft or revise `validate_manuscript.md` using the above as scaffold.
6. Export the abstract to `.docx` via `_build_abstract_docx.py` when
   sending to collaborators.

## Naming convention

- `PAPER_PLAN.md` (all-caps) — living plan document
- `validate_*.md` — validation-paper artefacts
- `tool.md` — tool contribution artefact
- `differentiation.md` — quantitative rubric analysis
- `_build_*.py` — utility scripts (underscore prefix signals "not a
  content artefact")
