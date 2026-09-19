#!/usr/bin/env Rscript
# Apply the CentileBrain pre-trained MFP models to the merged IDEAS table.
#
# Inputs (relative to the repo root, `Documents/Normative/`):
#   - ideas_data/ideas_merged.csv    (per-subject, from load_ideas.py)
#   - centilebrain/models/MFPmodels_<measure>_<sex>.rds
#
# Outputs:
#   - score/ideas_zscores_centilebrain.csv     — long-form Z-scores
#   - score/ideas_zscores_wide.csv             — wide table (one row per subject)
#   - score/scoring_summary.txt                — mean/SD of Z per region per cohort

suppressPackageStartupMessages({
  .libPaths(c("~/R/library", .libPaths()))
  library(mfp)
})

ROOT     <- "/mnt/nfs/home/URMC-SH/pndagiji/Documents/Normative"
IDEAS_CSV<- file.path(ROOT, "ideas_data/ideas_merged.csv")
MODELS   <- file.path(ROOT, "centilebrain/models")
OUT_DIR  <- file.path(ROOT, "score")
dir.create(OUT_DIR, showWarnings = FALSE, recursive = TRUE)

# ---------------------------------------------------------------------------
# Region orderings, taken from the CentileBrain XLSX templates.
# The pre-trained `.rds` file is a positional list where entry i corresponds
# to the i-th regional column in the template.
# ---------------------------------------------------------------------------
DK_ORDER <- c(
  "bankssts", "caudalanteriorcingulate", "caudalmiddlefrontal", "cuneus",
  "entorhinal", "fusiform", "inferiorparietal", "inferiortemporal",
  "isthmuscingulate", "lateraloccipital", "lateralorbitofrontal", "lingual",
  "medialorbitofrontal", "middletemporal", "parahippocampal", "paracentral",
  "parsopercularis", "parsorbitalis", "parstriangularis", "pericalcarine",
  "postcentral", "posteriorcingulate", "precentral", "precuneus",
  "rostralanteriorcingulate", "rostralmiddlefrontal", "superiorfrontal",
  "superiorparietal", "superiortemporal", "supramarginal", "frontalpole",
  "temporalpole", "transversetemporal", "insula"
)

# CentileBrain template order: all 34 L then all 34 R (see template XLSX).
cortical_cols <- function(measure_suffix) {
  # measure_suffix ∈ {"thickness", "area"}: which IDEAS column suffix to use
  c(paste0("lh_", DK_ORDER, "_", measure_suffix),
    paste0("rh_", DK_ORDER, "_", measure_suffix))
}

# Subcortical template order: Lthal, Rthal, Lcaud, Rcaud, Lput, Rput, Lpal,
# Rpal, Lhippo, Rhippo, Lamyg, Ramyg, Laccumb, Raccumb.
ASEG_ORDER <- c(
  "Left-Thalamus", "Right-Thalamus", "Left-Caudate", "Right-Caudate",
  "Left-Putamen", "Right-Putamen", "Left-Pallidum", "Right-Pallidum",
  "Left-Hippocampus", "Right-Hippocampus", "Left-Amygdala", "Right-Amygdala",
  "Left-Accumbens-area", "Right-Accumbens-area"
)

# Load merged IDEAS table.
ideas <- read.csv(IDEAS_CSV, check.names = FALSE, stringsAsFactors = FALSE)
cat(sprintf("Loaded IDEAS: %d rows, %d cols\n", nrow(ideas), ncol(ideas)))

# Ensure sex is uppercase "M"/"F"; drop rows with missing sex or age.
ideas$sex <- toupper(trimws(ideas$sex))
ideas <- ideas[!is.na(ideas$age) & ideas$sex %in% c("M", "F"), ]
cat(sprintf("After sex/age filter: %d rows (F=%d, M=%d)\n",
            nrow(ideas), sum(ideas$sex == "F"), sum(ideas$sex == "M")))

# ---------------------------------------------------------------------------
# Score one (measure × sex) block.
#
# * region_cols : IDEAS column names in the order the model list expects
# * global_col  : IDEAS column name for the global covariate
# * global_term : name of the term the MFP model expects ("ICV",
#                 "meanthickness", or "meanarea")
# * label       : short label for logging + output ("thickness", "area",
#                 "subcortical")
# ---------------------------------------------------------------------------
score_block <- function(sex, measure_label, region_cols, global_col,
                        global_term, rds_path) {
  models <- readRDS(rds_path)
  stopifnot(length(models) == length(region_cols))

  # Rebind term environments so predict.mfp works inside this session.
  for (i in seq_along(models)) {
    attr(models[[i]]$terms, ".Environment") <- globalenv()
    if (!is.null(models[[i]]$fit)) {
      attr(models[[i]]$fit$terms, ".Environment") <- globalenv()
    }
  }

  sub <- ideas[ideas$sex == sex, ]
  cat(sprintf("  [%s / %s] N=%d, %d regions, rds=%s\n",
              sex, measure_label, nrow(sub), length(region_cols),
              basename(rds_path)))

  region_mat <- as.matrix(sub[, region_cols])

  # Build newdata with the exact term names the model expects.
  newdat <- data.frame(age = sub$age)
  newdat[[global_term]] <- sub[[global_col]]

  # Apply the standard PCN Toolkit site-adaptation procedure
  # (Rutherford et al., Nature Protocols 2022): estimate a per-region offset
  # `mu_hat` from the local healthy controls and add it to the model's
  # centered predictions before Z-scoring. See ../mu_hat.md for the full
  # methodology, citations, and sensitivity-test recommendations.
  # Control Z ≈ 0 is a property of the adaptation procedure, so Task 5's
  # SD-based calibration test is the informative one.
  ctl_mask <- sub$cohort == "control"

  results <- vector("list", length(region_cols))
  for (i in seq_along(region_cols)) {
    m <- models[[i]]
    pred <- predict(m, newdata = newdat)
    rmse_m <- sqrt(sum(m$residuals^2) / length(m$residuals))
    obs <- region_mat[, i]

    if (any(ctl_mask)) {
      mu_hat <- mean(obs[ctl_mask] - pred[ctl_mask], na.rm = TRUE)
    } else {
      mu_hat <- 0
    }

    z <- (obs - pred - mu_hat) / rmse_m
    results[[i]] <- data.frame(
      subject_id     = sub$subject_id,
      cohort         = sub$cohort,
      sex            = sub$sex,
      age            = sub$age,
      measure        = measure_label,
      region         = region_cols[i],
      observed       = obs,
      predicted      = pred,
      mu_hat         = mu_hat,
      rmse_m         = rmse_m,
      z              = z
    )
  }
  do.call(rbind, results)
}

# ---------------------------------------------------------------------------
# Run the six (measure × sex) blocks and concatenate the long-form output.
# ---------------------------------------------------------------------------
run <- list(
  list(sex = "F", label = "thickness",
       cols = cortical_cols("thickness"), global_col = "mean_thickness",
       global_term = "meanthickness",
       rds = file.path(MODELS, "MFPmodels_thickness_female.rds")),
  list(sex = "M", label = "thickness",
       cols = cortical_cols("thickness"), global_col = "mean_thickness",
       global_term = "meanthickness",
       rds = file.path(MODELS, "MFPmodels_thickness_male.rds")),
  list(sex = "F", label = "area",
       cols = cortical_cols("area"),
       global_col = "mean_surface_area", global_term = "meanarea",
       rds = file.path(MODELS, "MFPmodels_surfacearea_female.rds")),
  list(sex = "M", label = "area",
       cols = cortical_cols("area"),
       global_col = "mean_surface_area", global_term = "meanarea",
       rds = file.path(MODELS, "MFPmodels_surfacearea_male.rds")),
  list(sex = "F", label = "subcortical",
       cols = ASEG_ORDER, global_col = "eTIV", global_term = "ICV",
       rds = file.path(MODELS, "MFPmodels_subcorticalvolume_female.rds")),
  list(sex = "M", label = "subcortical",
       cols = ASEG_ORDER, global_col = "eTIV", global_term = "ICV",
       rds = file.path(MODELS, "MFPmodels_subcorticalvolume_male.rds"))
)

cat("\nScoring...\n")
all_scores <- do.call(rbind, lapply(run, function(x)
  score_block(x$sex, x$label, x$cols, x$global_col, x$global_term, x$rds)))

# ---------------------------------------------------------------------------
# Save outputs.
# ---------------------------------------------------------------------------
long_path <- file.path(OUT_DIR, "ideas_zscores_centilebrain.csv")
write.csv(all_scores, long_path, row.names = FALSE)
cat(sprintf("\nWrote long-form Z-scores: %s (%d rows)\n",
            long_path, nrow(all_scores)))

# Wide table: one row per subject, one column per (measure_region).
wide <- reshape(
  all_scores[, c("subject_id", "cohort", "sex", "age", "measure", "region", "z")],
  timevar = "region", idvar = c("subject_id", "cohort", "sex", "age", "measure"),
  direction = "wide"
)
wide_path <- file.path(OUT_DIR, "ideas_zscores_wide.csv")
write.csv(wide, wide_path, row.names = FALSE)
cat(sprintf("Wrote wide Z-scores: %s (%d rows x %d cols)\n",
            wide_path, nrow(wide), ncol(wide)))

# Distributional summary: mean and SD of Z per (measure, region, cohort).
by <- split(all_scores, list(all_scores$measure, all_scores$region,
                             all_scores$cohort), drop = TRUE)
summary_df <- do.call(rbind, lapply(by, function(g) {
  data.frame(
    measure = g$measure[1], region = g$region[1], cohort = g$cohort[1],
    n = nrow(g),
    mean_z = mean(g$z, na.rm = TRUE), sd_z = sd(g$z, na.rm = TRUE)
  )
}))
summary_path <- file.path(OUT_DIR, "scoring_summary.txt")
write.csv(summary_df, summary_path, row.names = FALSE)
cat(sprintf("Wrote per-region summary: %s\n", summary_path))

# One-line-per-cohort quick look
cat("\n=== Overall Z-score distribution ===\n")
for (co in unique(all_scores$cohort)) {
  z <- all_scores$z[all_scores$cohort == co]
  cat(sprintf("  cohort=%s  n=%d  mean=%.3f  sd=%.3f  |mean|>0.5 frac=%.1f%%\n",
              co, length(z), mean(z, na.rm = TRUE), sd(z, na.rm = TRUE),
              100 * mean(abs(z) > 0.5, na.rm = TRUE)))
}
