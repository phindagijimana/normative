# Normative modelling toolkit

CentileBrain / PCN morphometry scoring, `normreport` PDFs, and connectome
normative analyses. IDEAS worked example; reusable on your data.

**License:** MIT (research use only) — see [`LICENSE`](LICENSE)  
**Docs:** [`docs/`](docs/index.md) — install → [tutorials](docs/tutorials/index.md) → methods/reference  
**Cite:** [`CITATION.cff`](CITATION.cff)

```bash
git clone https://github.com/phindagijimana/normative.git && cd normative
# docs/installation.md then docs/tutorials/
sphinx-build -b html docs docs/_build/html   # optional local docs site
```

| Folder | Role |
|---|---|
| `ideas_data/` | IDEAS download / merge |
| `score/` | Cohort scorers (outputs regenerable, not shipped) |
| `normreport/` | Single-subject CLI + container |
| `connectome_normative/` | Connectome CLI |

Package READMEs are pointers only.
