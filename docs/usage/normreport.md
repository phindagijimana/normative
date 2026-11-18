# `normreport` CLI reference

How-to: {doc}`../tutorials/03_normreport`. Research use only (v0.1.0).

| Option | Meaning |
|---|---|
| `--age` | Years |
| `--sex` | `M` / `F` |
| `--output` | Output directory |
| `--subject-id` | ID (default: CSV stem) |
| `--backend` | `centilebrain_mfp`, `centilebrain_gamlss`, `pcn_bayesian`, or `all` |
| `--reference` | Control CSV (default: bundled IDEAS controls) |

**Outputs** (`<output>/<id>/`): `*_report.pdf`, `*_zscores.csv`, `*_provenance.json`.

**Container:** `apptainer build --fakeroot normreport.sif Singularity.def` then `./normreport-container …`.
