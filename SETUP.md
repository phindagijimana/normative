# Setup

What a fresh workstation needs to run the morphometry scorers, IDEAS
downloaders, connectome scripts, and (optionally) `normreport`.

Full documentation (Sphinx / Read the Docs): see [`docs/installation.md`](docs/installation.md)
and [`docs/index.md`](docs/index.md).

## System

- **OS:** Linux (tested on RHEL 9); macOS usually works for scoring if
  models are present
- **Disk (approximate):**
  - This repo + IDEAS tables: tens of MB
  - CentileBrain clone: ~960 MB (or ~40 MB if you keep only the six MFP `.rds` files)
  - PCN Toolkit braincharts + extracted lifespan DK models: on the order of GB
  - Playwright Firefox (IDEAS Figshare only): ~100–330 MB

## Python

Python ≥ 3.9. From the repository root:

```bash
pip install -r requirements.txt
playwright install firefox   # only needed for ideas_data/fetch_*.py
```

For PCN cohort scoring also install:

```bash
pip install "pcntoolkit>=0.28"
```

(`normreport` pins its own deps via `normreport/pyproject.toml`; prefer
Python 3.11+ there so `pcntoolkit>=1.0` installs cleanly.)

## R

R ≥ 4.0. Install:

```r
install.packages(c("mfp", "gamlss", "gamlss.dist"),
                 repos = "https://cloud.r-project.org")
```

If you keep packages under `~/R/library`, the scoring scripts already
prepend that path.

Sanity check:

```bash
Rscript -e 'library(mfp); library(gamlss); cat("R packages OK\n")'
```

## CentileBrain models

Not bundled. Clone next to this repo’s root (directory name must be
`centilebrain/`):

```bash
cd /path/to/normative   # repository root
git clone --depth 1 https://github.com/CentileBrain/centilebrain.git
```

Expected paths:

- MFP: `centilebrain/models/MFPmodels_{thickness,surfacearea,subcorticalvolume}_{male,female}.rds`
- GAMLSS: `centilebrain/models/GAMLSSmodels_*.rds`

Only the six MFP files are required for `score_centilebrain.R` (~40 MB).
GAMLSS scoring needs the GAMLSS `.rds` files as well.

Override with `--models /other/path` on the R scorers if needed.

**Pinning:** validated against the CentileBrain repo layout as of
2026-09-18. If upstream renames templates, update the region-order
tables at the top of `score/score_centilebrain.R`.

## PCN Toolkit models

Not bundled. Place the public braincharts checkout under
`pcn_models/braincharts/` and extract the lifespan DK cortical-thickness
bundle so this path exists:

```text
pcn_models/braincharts/models/lifespan_DK_ct/lifespan_DK_46K_59sites/
```

Also required alongside that checkout:

```text
pcn_models/braincharts/docs/phenotypes_ct_dk_lh.txt
pcn_models/braincharts/docs/phenotypes_ct_dk_rh.txt
pcn_models/braincharts/docs/phenotypes_sc.txt
pcn_models/braincharts/docs/site_ids_ct_dk_59sites.txt
pcn_models/braincharts/scripts/   # nm_utils used by score_pcn_toolkit.py
```

Upstream starting point:
https://github.com/predictive-clinical-neuroscience/braincharts

Then:

```bash
python3 score/score_pcn_toolkit.py --help
```

## Firewall / network

- **Figshare** (`figshare.com`, `ndownloader.figshare.com`) — IDEAS download
  (Playwright required; plain `curl` often gets HTTP 202 from the WAF)
- **CRAN** — R packages
- **GitHub / PyPI** — CentileBrain clone, Python packages, braincharts

## Not required for morphometry scoring

- FreeSurfer — IDEAS ships extracted stats; `normreport` can also ingest a
  pre-exported stats CSV
- ComBat / neuroHarmonize — not needed for single-site scoring with
  control-based site adaptation

## Environment sanity checks

```bash
python3 -c "import pandas, numpy, scipy, sklearn; print('python OK')"
python3 -c "from playwright.sync_api import sync_playwright; \
  p = sync_playwright().start(); print(p.firefox.executable_path); p.stop()"
Rscript -e 'library(mfp); cat("mfp OK\n")'
test -f centilebrain/models/MFPmodels_thickness_male.rds && echo "CentileBrain OK"
test -d pcn_models/braincharts/models/lifespan_DK_ct/lifespan_DK_46K_59sites && echo "PCN OK"
```

## Data provenance (IDEAS)

`ideas_data/fetch_figshare.py` and `fetch_resection.py` re-download public
tables; file IDs and sizes are recorded in `ideas_data/manifest.json`.
