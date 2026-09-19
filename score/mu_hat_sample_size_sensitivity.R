#!/usr/bin/env Rscript
# Test 2 — Sample-size sensitivity of the mu_hat site-adaptation offset.
#
# Question: at what reference-cohort size does mu_hat stabilise? This
# feeds directly into tool deployment guidance — the ≥ 30-control
# recommendation from Rutherford et al. 2022 and Little et al. 2025
# should be verifiable on IDEAS.
#
# Procedure (mu_hat.md §8 Test 2):
#   * Subsample controls at N ∈ {10, 20, 30, 50, 75, 100}
#   * At each N, draw B = 100 random sex-stratified subsamples
#   * Per subsample, per (region × sex): compute mu_hat = mean(obs − pred)
#   * Report per-region SD of mu_hat across subsamples at each N
#   * Do for both MFP and GAMLSS
#
# References:
#   - Rutherford et al. Nature Protocols 2022
#   - Little et al. Imaging Neuroscience 2025

suppressPackageStartupMessages({
  .libPaths(c("~/R/library", .libPaths()))
  library(mfp)
  library(gamlss)
})

ROOT      <- "/mnt/nfs/home/URMC-SH/pndagiji/Documents/Normative"
IDEAS_CSV <- file.path(ROOT, "ideas_data/ideas_merged.csv")
MODELS    <- file.path(ROOT, "centilebrain/models")
OUT_DIR   <- file.path(ROOT, "score")

set.seed(20260919)
Ns <- c(10, 20, 30, 50, 75, 100)
B  <- 100

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
cortical_cols <- function(suffix) {
  c(paste0("lh_", DK_ORDER, "_", suffix),
    paste0("rh_", DK_ORDER, "_", suffix))
}
ASEG_ORDER <- c(
  "Left-Thalamus", "Right-Thalamus", "Left-Caudate", "Right-Caudate",
  "Left-Putamen", "Right-Putamen", "Left-Pallidum", "Right-Pallidum",
  "Left-Hippocampus", "Right-Hippocampus", "Left-Amygdala", "Right-Amygdala",
  "Left-Accumbens-area", "Right-Accumbens-area"
)

ideas <- read.csv(IDEAS_CSV, check.names = FALSE, stringsAsFactors = FALSE)
ideas$sex <- toupper(trimws(ideas$sex))
ideas <- ideas[!is.na(ideas$age) & ideas$sex %in% c("M", "F"), ]
ctl <- ideas[ideas$cohort == "control", ]
cat(sprintf("IDEAS: %d controls (F=%d, M=%d)\n",
            nrow(ctl), sum(ctl$sex == "F"), sum(ctl$sex == "M")))

rebind_mfp <- function(mod) {
  attr(mod$terms, ".Environment") <- globalenv()
  if (!is.null(mod$fit)) attr(mod$fit$terms, ".Environment") <- globalenv()
  mod
}
rebind_gamlss <- function(mod) {
  attr(mod$mu.terms, ".Environment") <- globalenv()
  if (!is.null(mod$sigma.terms)) attr(mod$sigma.terms, ".Environment") <- globalenv()
  if (!is.null(mod$nu.terms))    attr(mod$nu.terms, ".Environment")    <- globalenv()
  if (!is.null(mod$tau.terms))   attr(mod$tau.terms, ".Environment")   <- globalenv()
  mod
}
compute_centile <- function(y, mu, sigma, nu, tau, family) {
  if      (family == "NO")    pNO(y, mu = mu, sigma = sigma)
  else if (family == "BCCGo") pBCCGo(y, mu = mu, sigma = sigma, nu = nu)
  else if (family == "BCPEo") pBCPEo(y, mu = mu, sigma = sigma, nu = nu, tau = tau)
  else if (family == "BCTo")  pBCTo(y, mu = mu, sigma = sigma, nu = nu, tau = tau)
  else stop("Unsupported family: ", family)
}

# ---- Precompute per-control predictions per block --------------------------
# For efficiency: score all controls ONCE with each model, then subsample
# from the residual matrix rather than re-scoring per subsample.

mfp_precomputed <- function(sex_lab, region_cols, global_col, global_term, rds_path) {
  models <- readRDS(rds_path); models <- lapply(models, rebind_mfp)
  sub <- ctl[ctl$sex == sex_lab, ]
  nd <- data.frame(age = sub$age); nd[[global_term]] <- sub[[global_col]]
  preds <- sapply(seq_along(region_cols), function(i)
    predict(models[[i]], newdata = nd))
  obs <- as.matrix(sub[, region_cols])
  list(residuals = obs - preds, subject_id = sub$subject_id)
}

gamlss_precomputed_zraw <- function(sex_lab, region_cols, rds_path) {
  models <- readRDS(rds_path); models <- lapply(models, rebind_gamlss)
  sub <- ctl[ctl$sex == sex_lab, ]
  nd <- data.frame(age = sub$age)
  z_raw <- matrix(NA_real_, nrow = nrow(sub), ncol = length(region_cols),
                  dimnames = list(NULL, region_cols))
  for (i in seq_along(region_cols)) {
    m <- models[[i]]; fam <- m$family[1]
    mu    <- predict(m, newdata = nd, what = "mu",    type = "response")
    sigma <- predict(m, newdata = nd, what = "sigma", type = "response")
    nu    <- if (!is.null(m$nu.terms))  predict(m, newdata = nd, what = "nu",  type = "response") else rep(0, nrow(sub))
    tau   <- if (!is.null(m$tau.terms)) predict(m, newdata = nd, what = "tau", type = "response") else rep(NA, nrow(sub))
    obs <- sub[[region_cols[i]]]
    centile <- compute_centile(obs, mu, sigma, nu, tau, fam)
    centile <- pmin(pmax(centile, 1e-6), 1 - 1e-6)
    z_raw[, i] <- qnorm(centile)
  }
  list(z_raw = z_raw, subject_id = sub$subject_id)
}

# ---- Bootstrap-style SD of mu_hat estimate per N --------------------------
mu_hat_sd_across_subsamples <- function(estimator_matrix, N, B_reps) {
  # estimator_matrix[i, j] is the per-subject-per-region quantity whose
  # column-mean is mu_hat. Return per-column SD of column-means across
  # B_reps random subsamples of N rows.
  n_ctl <- nrow(estimator_matrix)
  if (N > n_ctl) return(rep(NA_real_, ncol(estimator_matrix)))
  vals <- matrix(NA_real_, nrow = B_reps, ncol = ncol(estimator_matrix))
  for (b in seq_len(B_reps)) {
    ix <- sample.int(n_ctl, N)
    vals[b, ] <- colMeans(estimator_matrix[ix, , drop = FALSE], na.rm = TRUE)
  }
  apply(vals, 2, sd, na.rm = TRUE)
}

# ---- Run all 6 blocks per algorithm ---------------------------------------
run_mfp <- list(
  list(sex = "F", label = "thickness", cols = cortical_cols("thickness"),
       global_col = "mean_thickness", global_term = "meanthickness",
       rds = file.path(MODELS, "MFPmodels_thickness_female.rds")),
  list(sex = "M", label = "thickness", cols = cortical_cols("thickness"),
       global_col = "mean_thickness", global_term = "meanthickness",
       rds = file.path(MODELS, "MFPmodels_thickness_male.rds")),
  list(sex = "F", label = "area", cols = cortical_cols("area"),
       global_col = "mean_surface_area", global_term = "meanarea",
       rds = file.path(MODELS, "MFPmodels_surfacearea_female.rds")),
  list(sex = "M", label = "area", cols = cortical_cols("area"),
       global_col = "mean_surface_area", global_term = "meanarea",
       rds = file.path(MODELS, "MFPmodels_surfacearea_male.rds")),
  list(sex = "F", label = "subcortical", cols = ASEG_ORDER,
       global_col = "eTIV", global_term = "ICV",
       rds = file.path(MODELS, "MFPmodels_subcorticalvolume_female.rds")),
  list(sex = "M", label = "subcortical", cols = ASEG_ORDER,
       global_col = "eTIV", global_term = "ICV",
       rds = file.path(MODELS, "MFPmodels_subcorticalvolume_male.rds"))
)
run_gamlss <- list(
  list(sex = "F", label = "thickness",   cols = cortical_cols("thickness"),
       rds = file.path(MODELS, "GAMLSSmodels_thickness_female.rds")),
  list(sex = "M", label = "thickness",   cols = cortical_cols("thickness"),
       rds = file.path(MODELS, "GAMLSSmodels_thickness_male.rds")),
  list(sex = "F", label = "area",        cols = cortical_cols("area"),
       rds = file.path(MODELS, "GAMLSSmodels_surfacearea_female.rds")),
  list(sex = "M", label = "area",        cols = cortical_cols("area"),
       rds = file.path(MODELS, "GAMLSSmodels_surfacearea_male.rds")),
  list(sex = "F", label = "subcortical", cols = ASEG_ORDER,
       rds = file.path(MODELS, "GAMLSSmodels_subcorticalvolume_female.rds")),
  list(sex = "M", label = "subcortical", cols = ASEG_ORDER,
       rds = file.path(MODELS, "GAMLSSmodels_subcorticalvolume_male.rds"))
)

results <- list()

cat("\n[MFP] precomputing per-control residuals ...\n")
for (blk in run_mfp) {
  cat(sprintf("  %s / %s\n", blk$sex, blk$label))
  pc <- mfp_precomputed(blk$sex, blk$cols, blk$global_col,
                         blk$global_term, blk$rds)
  # For each N, compute SD of mu_hat estimate across B subsamples.
  # Sample size N applies WITHIN this sex (approximation: assume the
  # cohort splits ~evenly across sexes).
  n_avail <- nrow(pc$residuals)
  for (N in Ns) {
    n_per_sex <- min(N, n_avail)  # cap at what's available
    sds <- mu_hat_sd_across_subsamples(pc$residuals, n_per_sex, B)
    results[[length(results) + 1]] <- data.frame(
      algorithm = "MFP", sex = blk$sex, measure = blk$label,
      region = blk$cols, N_total = N, N_per_sex = n_per_sex,
      mu_hat_sd = sds
    )
  }
}

cat("\n[GAMLSS] precomputing per-control z_raw ...\n")
for (blk in run_gamlss) {
  cat(sprintf("  %s / %s\n", blk$sex, blk$label))
  pc <- gamlss_precomputed_zraw(blk$sex, blk$cols, blk$rds)
  # For GAMLSS the "mu_hat"-analogue is the per-region mean of z_raw on
  # controls (subtracted at scoring time as the site-adaptation offset).
  n_avail <- nrow(pc$z_raw)
  for (N in Ns) {
    n_per_sex <- min(N, n_avail)
    sds <- mu_hat_sd_across_subsamples(pc$z_raw, n_per_sex, B)
    results[[length(results) + 1]] <- data.frame(
      algorithm = "GAMLSS", sex = blk$sex, measure = blk$label,
      region = blk$cols, N_total = N, N_per_sex = n_per_sex,
      mu_hat_sd = sds
    )
  }
}

all_results <- do.call(rbind, results)
out_csv <- file.path(OUT_DIR, "mu_hat_sample_size_variance.csv")
write.csv(all_results, out_csv, row.names = FALSE)
cat(sprintf("\nWrote per-region mu_hat SDs at each N: %s (%d rows)\n",
            out_csv, nrow(all_results)))

# ---- Summary: median mu_hat SD across regions at each N -------------------
cat("\n=== Median mu_hat SD across regions, per algorithm × measure × N ===\n")
cat(sprintf("%-8s %-11s %-6s %-8s\n", "algo", "measure", "N", "median_SD"))
for (algo in c("MFP", "GAMLSS")) {
  for (m in c("thickness", "area", "subcortical")) {
    for (N in Ns) {
      sub <- all_results[all_results$algorithm == algo &
                         all_results$measure == m &
                         all_results$N_total == N, ]
      cat(sprintf("%-8s %-11s %-6d %.4f\n",
                  algo, m, N, median(sub$mu_hat_sd, na.rm = TRUE)))
    }
  }
}

cat("\nDone. Sample-size sensitivity of mu_hat complete.\n")
