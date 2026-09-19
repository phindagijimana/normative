#!/usr/bin/env Rscript
# Test 1 — Cross-validation of the mu_hat site-adaptation offset.
#
# The current CentileBrain × IDEAS pipeline estimates mu_hat once on all
# 100 healthy controls, then applies it to score every subject. This makes
# Task 5 "control mean Z ≈ 0" tautological. K-fold splitting of the
# controls removes the tautology and produces genuinely held-out control
# Z-scores whose mean and SD are informative diagnostics.
#
# Procedure (mu_hat.md §8 Test 1):
#   * Stratified 5-fold split of the 100 IDEAS controls (sex × age band).
#   * For each fold k: estimate mu_hat per region on 80 training controls
#     (per-sex), apply to the 20 held-out controls.
#   * Aggregate held-out control Z-scores across folds.
#   * Report per-region mean and SD of held-out Z.
#   * Do both under CentileBrain-MFP and CentileBrain-GAMLSS.
#
# References:
#   - Rutherford S, Kia SM, ..., Marquand AF. The normative modeling
#     framework for computational psychiatry. Nature Protocols 17:
#     1711–1734 (2022). — the PCN Toolkit protocol whose adaptation
#     procedure we test here.
#   - Ge R et al. Lancet Digit Health 6(3): e211–e221 (2024). — CentileBrain.

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
K <- 5

# ---- Region orderings (as in score_centilebrain.R) -------------------------
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

# ---- Load and prepare data -------------------------------------------------
ideas <- read.csv(IDEAS_CSV, check.names = FALSE, stringsAsFactors = FALSE)
ideas$sex <- toupper(trimws(ideas$sex))
ideas <- ideas[!is.na(ideas$age) & ideas$sex %in% c("M", "F"), ]
ctl <- ideas[ideas$cohort == "control", ]
cat(sprintf("IDEAS: %d controls (F=%d, M=%d)\n",
            nrow(ctl), sum(ctl$sex == "F"), sum(ctl$sex == "M")))

# ---- Stratified fold assignment --------------------------------------------
# Stratify by sex × age-band (≤30 / 31-50 / >50) to keep each fold balanced.
age_band <- cut(ctl$age, breaks = c(-Inf, 30, 50, Inf),
                labels = c("le30", "b31_50", "gt50"))
strat <- paste(ctl$sex, age_band, sep = ":")

ctl$fold <- NA_integer_
for (s in unique(strat)) {
  ix <- which(strat == s)
  ctl$fold[ix] <- rep_len(1:K, length(ix))[sample(length(ix))]
}
cat("Fold sizes per stratum:\n")
print(table(strat, ctl$fold))

# ---- Rebind term envs (CentileBrain models need this on load) --------------
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

# ---- Score a control fold with MFP (returns held-out Z per region) --------
mfp_zscore_ctl_holdout <- function(sex_lab, measure_label, region_cols,
                                    global_col, global_term, rds_path) {
  models <- readRDS(rds_path)
  models <- lapply(models, rebind_mfp)
  sub_ctl <- ctl[ctl$sex == sex_lab, ]
  newdat  <- data.frame(age = sub_ctl$age)
  newdat[[global_term]] <- sub_ctl[[global_col]]
  region_mat <- as.matrix(sub_ctl[, region_cols])

  # Precompute predictions for all controls in this sex
  preds <- sapply(seq_along(region_cols), function(i)
    predict(models[[i]], newdata = newdat))

  rmse_m <- sapply(models, function(m)
    sqrt(sum(m$residuals^2) / length(m$residuals)))

  # Held-out Z per fold
  z_out <- matrix(NA_real_, nrow = nrow(sub_ctl), ncol = length(region_cols),
                  dimnames = list(NULL, region_cols))
  for (k in 1:K) {
    train_ix <- which(sub_ctl$fold != k)
    test_ix  <- which(sub_ctl$fold == k)
    if (!length(train_ix) || !length(test_ix)) next
    mu_hat_k <- colMeans(region_mat[train_ix, , drop = FALSE] -
                         preds[train_ix, , drop = FALSE], na.rm = TRUE)
    for (i in seq_along(region_cols)) {
      z_out[test_ix, i] <- (region_mat[test_ix, i] - preds[test_ix, i]
                            - mu_hat_k[i]) / rmse_m[i]
    }
  }
  # Emit long-form immediately (avoids rbind column-name mismatch across measures)
  data.frame(
    subject_id = rep(sub_ctl$subject_id, length(region_cols)),
    sex        = rep(sub_ctl$sex, length(region_cols)),
    age        = rep(sub_ctl$age, length(region_cols)),
    measure    = measure_label,
    region     = rep(region_cols, each = nrow(sub_ctl)),
    z          = as.vector(z_out)
  )
}

# ---- Score a control fold with GAMLSS -------------------------------------
gamlss_zscore_ctl_holdout <- function(sex_lab, measure_label, region_cols,
                                       rds_path) {
  models <- readRDS(rds_path)
  models <- lapply(models, rebind_gamlss)
  sub_ctl <- ctl[ctl$sex == sex_lab, ]
  newdat  <- data.frame(age = sub_ctl$age)
  region_mat <- as.matrix(sub_ctl[, region_cols])

  # Raw GAMLSS z per subject per region (before site adaptation)
  z_raw <- matrix(NA_real_, nrow = nrow(sub_ctl), ncol = length(region_cols),
                  dimnames = list(NULL, region_cols))
  for (i in seq_along(region_cols)) {
    m <- models[[i]]
    fam <- m$family[1]
    mu    <- predict(m, newdata = newdat, what = "mu",    type = "response")
    sigma <- predict(m, newdata = newdat, what = "sigma", type = "response")
    nu    <- if (!is.null(m$nu.terms))  predict(m, newdata = newdat, what = "nu",  type = "response") else rep(0, nrow(sub_ctl))
    tau   <- if (!is.null(m$tau.terms)) predict(m, newdata = newdat, what = "tau", type = "response") else rep(NA, nrow(sub_ctl))
    centile <- compute_centile(region_mat[, i], mu, sigma, nu, tau, fam)
    centile <- pmin(pmax(centile, 1e-6), 1 - 1e-6)
    z_raw[, i] <- qnorm(centile)
  }

  # Held-out K-fold adaptation: for GAMLSS the offset is applied on the Z
  # scale (mirrors score_centilebrain_gamlss.R behaviour).
  z_out <- matrix(NA_real_, nrow = nrow(sub_ctl), ncol = length(region_cols),
                  dimnames = list(NULL, region_cols))
  for (k in 1:K) {
    train_ix <- which(sub_ctl$fold != k)
    test_ix  <- which(sub_ctl$fold == k)
    if (!length(train_ix) || !length(test_ix)) next
    shift_k <- colMeans(z_raw[train_ix, , drop = FALSE], na.rm = TRUE)
    for (i in seq_along(region_cols)) {
      z_out[test_ix, i] <- z_raw[test_ix, i] - shift_k[i]
    }
  }
  data.frame(
    subject_id = rep(sub_ctl$subject_id, length(region_cols)),
    sex        = rep(sub_ctl$sex, length(region_cols)),
    age        = rep(sub_ctl$age, length(region_cols)),
    measure    = measure_label,
    region     = rep(region_cols, each = nrow(sub_ctl)),
    z          = as.vector(z_out)
  )
}

# ---- Run all six (measure × sex) blocks × two algorithms -------------------
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

cat("\n[MFP] cross-validating mu_hat ...\n")
mfp_long <- do.call(rbind, lapply(run_mfp, function(x) {
  cat(sprintf("  %s / %s\n", x$sex, x$label))
  mfp_zscore_ctl_holdout(x$sex, x$label, x$cols, x$global_col,
                          x$global_term, x$rds)
}))

cat("\n[GAMLSS] cross-validating mu_hat ...\n")
gamlss_long <- do.call(rbind, lapply(run_gamlss, function(x) {
  cat(sprintf("  %s / %s\n", x$sex, x$label))
  gamlss_zscore_ctl_holdout(x$sex, x$label, x$cols, x$rds)
}))

# ---- Compute per-region mean + SD of held-out Z ----------------------------
per_region_stats <- function(long, algo_label) {
  long <- long[!is.na(long$z), ]
  agg <- aggregate(z ~ measure + region, data = long,
                   FUN = function(x) c(n = length(x),
                                       mean = mean(x), sd = sd(x)))
  out <- data.frame(measure = agg$measure, region = agg$region,
                    n = agg$z[, "n"], mean_z = agg$z[, "mean"],
                    sd_z = agg$z[, "sd"], algorithm = algo_label)
  out[, c("algorithm", "measure", "region", "n", "mean_z", "sd_z")]
}
mfp_stats    <- per_region_stats(mfp_long,    "MFP")
gamlss_stats <- per_region_stats(gamlss_long, "GAMLSS")

results <- rbind(mfp_stats, gamlss_stats)
out_csv <- file.path(OUT_DIR, "mu_hat_cv_results.csv")
write.csv(results, out_csv, row.names = FALSE)
cat(sprintf("\nWrote per-region held-out Z stats: %s (%d rows)\n",
            out_csv, nrow(results)))

# ---- Summary report to stdout ---------------------------------------------
cat("\n=== Held-out control Z-score distributions (aggregated across regions) ===\n")
for (algo in c("MFP", "GAMLSS")) {
  for (m in c("thickness", "area", "subcortical")) {
    sub <- results[results$algorithm == algo & results$measure == m, ]
    cat(sprintf("  %s / %-11s  N regions=%d  median|mean|=%.3f  median SD=%.3f\n",
                algo, m, nrow(sub),
                median(abs(sub$mean_z), na.rm = TRUE),
                median(sub$sd_z, na.rm = TRUE)))
  }
}

cat("\nDone. Cross-validation of mu_hat complete.\n")
