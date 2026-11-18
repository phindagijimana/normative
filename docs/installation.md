# Installation

## System

- Linux recommended (tested on RHEL 9); macOS usually works for scoring
- Python ≥ 3.9 (3.11+ preferred for `normreport` + recent `pcntoolkit`)
- R ≥ 4.0 for CentileBrain scorers

## Python packages

From the repository root:

```bash
git clone https://github.com/phindagijimana/normative.git
cd normative
pip install -r requirements.txt
playwright install firefox   # only for IDEAS Figshare downloaders
```

Optional PCN cohort scoring:

```bash
pip install "pcntoolkit>=0.28"
```

Single-subject tool:

```bash
cd normreport && pip install -e .
```

## R packages

```r
install.packages(c("mfp", "gamlss", "gamlss.dist"),
                 repos = "https://cloud.r-project.org")
```

## CentileBrain models

Not shipped in this repo (~960 MB upstream). Clone beside the project root:

```bash
git clone --depth 1 https://github.com/CentileBrain/centilebrain.git
```

Required for MFP scoring:

```text
centilebrain/models/MFPmodels_{thickness,surfacearea,subcorticalvolume}_{male,female}.rds
```

GAMLSS scoring also needs `centilebrain/models/GAMLSSmodels_*.rds`.

## PCN Toolkit models

Place the public [braincharts](https://github.com/predictive-clinical-neuroscience/braincharts)
checkout under `pcn_models/braincharts/` and extract the lifespan DK
cortical-thickness bundle so this exists:

```text
pcn_models/braincharts/models/lifespan_DK_ct/lifespan_DK_46K_59sites/
```

Also keep the `docs/` phenotype lists and `scripts/` folder from that
checkout (used by `score/score_pcn_toolkit.py`).

## Sanity checks

```bash
python3 -c "import pandas, numpy, scipy; print('python OK')"
Rscript -e 'library(mfp); library(gamlss); cat("R OK\n")'
test -f centilebrain/models/MFPmodels_thickness_male.rds && echo CentileBrain OK
test -d pcn_models/braincharts/models/lifespan_DK_ct/lifespan_DK_46K_59sites && echo PCN OK
```

## Not required

- FreeSurfer re-run (IDEAS ships extracted stats; `normreport` accepts a stats CSV)
- ComBat / neuroHarmonize for single-site scoring with local controls

## Next

Go to {doc}`tutorials/index` (IDEAS → own cohort → normreport → connectome).
