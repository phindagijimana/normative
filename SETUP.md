# Setup

Everything a fresh workstation needs to reproduce the four validation tasks.

## System

- **OS:** Linux (tested on RHEL 9)
- **Disk footprint:** ~1.5 GB total
  - IDEAS tabular data: ~4 MB
  - CentileBrain models repo: ~960 MB (upstream clone)
  - Playwright Firefox cache: ~330 MB
  - Analysis outputs: ~15 MB

## Runtime

- **R** ≥ 4.0 (tested on 4.6.1). Install `mfp`:
  ```r
  install.packages("mfp", lib = "~/R/library",
                   repos = "https://cloud.r-project.org")
  ```
- **Python** ≥ 3.9 with:
  ```
  pandas numpy scipy scikit-learn openpyxl pdfplumber playwright
  ```
- **Playwright Firefox** (for the Figshare AWS-WAF-gated share pages):
  ```bash
  pip install playwright
  playwright install firefox    # downloads ~100 MB browser cache
  ```

## CentileBrain repo

**Clone separately** — the upstream CentileBrain repo (~960 MB) is not
bundled here (it's a full mirror of another public repository and does
not belong in this codebase). Fetch it into the project root once:

```bash
cd ~/Documents/Normative
git clone --depth 1 https://github.com/CentileBrain/centilebrain.git
```

The repo contains the pre-trained `.rds` MFP model files, GAMLSS
alternates, templates, and demo data.

The scoring script (`score/score_centilebrain.R`) expects the models at
`centilebrain/models/MFPmodels_<measure>_<sex>.rds`. If you relocate the
folder, edit the `MODELS` path at the top of that file.

**Only the 6 MFP model files are strictly needed for our pipeline** —
`centilebrain/models/MFPmodels_{thickness,surfacearea,subcorticalvolume}_{male,female}.rds`
(~40 MB total). The remaining ~920 MB is the upstream GAMLSS alternates,
brainAGE models, demos, and instructions — kept intact for reproducibility
and to match what centilebrain.org publishes.

**Pinning:** we validated against the CentileBrain repo state as of
2026-09-18. If the upstream repo changes model layout, the region-order
tables at the top of `score_centilebrain.R` may need updating.

## Firewall / network

- **Figshare** downloads go via `figshare.com` (AWS WAF challenge — requires
  Playwright, plain `curl` returns HTTP 202) and
  `ndownloader.figshare.com` (plain HTTPS after we've resolved the file
  IDs). Both must be reachable.
- **CRAN mirror** for the R `mfp` package install.
- **GitHub** for the CentileBrain clone.

## Environment sanity check

Once installed, this one-liner should print `mfp loaded OK`:

```bash
Rscript -e '.libPaths(c("~/R/library", .libPaths())); library(mfp); cat("mfp loaded OK\n")'
```

And this should print `playwright OK` + `firefox` binary path:

```bash
python3 -c "from playwright.sync_api import sync_playwright; \
  p = sync_playwright().start(); print('playwright OK'); \
  print(p.firefox.executable_path); p.stop()"
```

## Not required (but useful)

- **FreeSurfer** — not needed. The IDEAS Figshare release ships FreeSurfer
  stats already extracted; we don't re-run recon-all.
- **ComBat-GAM / neuroHarmonize** — not needed for single-site IDEAS.
  Required only if extending to multi-site cohorts.

## Data provenance

All IDEAS Figshare files are re-fetched by
`ideas_data/fetch_figshare.py` and `ideas_data/fetch_resection.py`. File IDs
and byte counts are recorded in `ideas_data/manifest.json` at download
time.
