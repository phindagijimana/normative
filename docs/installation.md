# Installation

- **OS:** Linux recommended (RHEL 9 tested); macOS usually fine for scoring  
- **Python** ≥ 3.9 (3.11+ for `normreport` / recent `pcntoolkit`)  
- **R** ≥ 4.0 for CentileBrain scorers  

```bash
git clone https://github.com/phindagijimana/normative.git
cd normative
pip install -r requirements.txt
playwright install firefox          # IDEAS downloaders only
pip install "pcntoolkit>=0.28"      # optional PCN scoring
cd normreport && pip install -e .   # optional single-subject CLI
```

```r
install.packages(c("mfp", "gamlss", "gamlss.dist"),
                 repos = "https://cloud.r-project.org")
```

**CentileBrain** (not bundled) — clone at repo root:

```bash
git clone --depth 1 https://github.com/CentileBrain/centilebrain.git
# need: centilebrain/models/MFPmodels_{thickness,surfacearea,subcorticalvolume}_{male,female}.rds
# GAMLSS also needs GAMLSSmodels_*.rds
```

**PCN** — [braincharts](https://github.com/predictive-clinical-neuroscience/braincharts) under
`pcn_models/braincharts/` with
`models/lifespan_DK_ct/lifespan_DK_46K_59sites/` plus that checkout’s `docs/` and `scripts/`.

```bash
python3 -c "import pandas, numpy, scipy; print('python OK')"
Rscript -e 'library(mfp); library(gamlss); cat("R OK\n")'
test -f centilebrain/models/MFPmodels_thickness_male.rds && echo CentileBrain OK
```

Next: {doc}`tutorials/index`.
