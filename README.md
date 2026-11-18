# Normative modelling toolkit

Score brain morphometry with CentileBrain / PCN Toolkit, generate
single-subject PDF reports (`normreport`), or run structural-connectome
normative analyses. IDEAS is the worked example; the same tools reuse on
your data.

**Docs (canonical):** [`docs/index.md`](docs/index.md)  
Build HTML: `pip install -r docs/requirements.txt && sphinx-build -b html docs docs/_build/html`

[![Docs](https://img.shields.io/badge/docs-Sphinx-blue)](docs/index.md)
[![Source](https://img.shields.io/badge/source-GitHub-black)](https://github.com/phindagijimana/normative)

## Start here

| Step | Link |
|---|---|
| Install | [`docs/installation.md`](docs/installation.md) |
| Tutorials (IDEAS → own data → normreport → connectome) | [`docs/tutorials/`](docs/tutorials/index.md) |
| Methods (short science) | [`docs/methods.md`](docs/methods.md) |
| Input schemas | [`docs/inputs.md`](docs/inputs.md) |

```bash
git clone https://github.com/phindagijimana/normative.git
cd normative
# then follow docs/installation.md and docs/tutorials/
```

## Package folders

| Folder | Role | Local README |
|---|---|---|
| `ideas_data/` | Download / merge IDEAS tables | pointer + IDEAS caveats |
| `score/` | Cohort scorers | pointer + script list |
| `normreport/` | Single-subject CLI / container | pointer + quick demo |
| `connectome_normative/` | Connectome normative CLI | pointer + `--demo` |

Full narrative and tutorials live under `docs/` only (avoids duplicate guides).

## References

Ge et al. 2024 (CentileBrain); Rutherford et al. 2022 (site adaptation / PCN);
Taylor et al. 2025 (IDEAS). See [`docs/references.md`](docs/references.md).
