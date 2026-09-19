#!/usr/bin/env Rscript
# Score IDEAS with the CentileBrain GAMLSS models (alternative to MFP scoring).
#
# Unlike the MFP models, GAMLSS models are:
#   - Age-only (no ICV/global covariate)
#   - Predict on the ORIGINAL scale (no un-centering needed — no mean_train issue)
#   - Return full distribution parameters (mu, sigma, nu, [tau])
#   - Use LMS-family distributions: BCCGo for thickness+subcortical, BCPEo for area
#
# Z-scores are computed via CDF-inverse-normal:
#   centile = pBCCGo(y, mu, sigma, nu)   (or pBCPEo(...) for area with 4 params)
#   Z       = qnorm(centile)
#
# We optionally add PCN Toolkit site adaptation on top (mu_hat, per mu_hat.md).
# This lets us compare raw GAMLSS Z-scores to site-adapted GAMLSS Z-scores.

suppressPackageStartupMessages({
  .libPaths(c("~/R/library", .libPaths()))
  library(gamlss)
  library(gamlss.dist)
})

ROOT      <- "/mnt/nfs/home/URMC-SH/pndagiji/Documents/Normative"
IDEAS_CSV <- file.path(ROOT, "ideas_data/ideas_merged.csv")
MODELS    <- file.path(ROOT, "centilebrain/models")
OUT_DIR   <- file.path(ROOT, "score")

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
cat(sprintf("IDEAS: %d rows, %d F, %d M\n", nrow(ideas),
            sum(ideas$sex == "F"), sum(ideas$sex == "M")))

# ---- CDF helper: dispatch to the right p*() function per family -----------
# CentileBrain's GAMLSS models select the best-fit LMS-family distribution
# per region during training, so we handle four families:
#   NO    — Normal (mu, sigma)
#   BCCGo — Box-Cox-Cole-Green original (mu, sigma, nu)
#   BCPEo — Box-Cox Power Exponential original (mu, sigma, nu, tau)
#   BCTo  — Box-Cox t original (mu, sigma, nu, tau)
compute_centile <- function(y, mu, sigma, nu, tau, family) {
  if (family == "NO") {
    pNO(y, mu = mu, sigma = sigma)
  } else if (family == "BCCGo") {
    pBCCGo(y, mu = mu, sigma = sigma, nu = nu)
  } else if (family == "BCPEo") {
    pBCPEo(y, mu = mu, sigma = sigma, nu = nu, tau = tau)
  } else if (family == "BCTo") {
    pBCTo(y, mu = mu, sigma = sigma, nu = nu, tau = tau)
  } else {
    stop("Unsupported GAMLSS family: ", family)
  }
}

# ---- Score one (measure x sex) block --------------------------------------
score_block <- function(sex, measure_label, region_cols, rds_path) {
  models <- readRDS(rds_path)
  stopifnot(length(models) == length(region_cols))

  # Rebind term environments for predict()
  for (i in seq_along(models)) {
    m <- models[[i]]
    attr(m$mu.terms, ".Environment") <- globalenv()
    if (!is.null(m$sigma.terms)) attr(m$sigma.terms, ".Environment") <- globalenv()
    if (!is.null(m$nu.terms))    attr(m$nu.terms, ".Environment")    <- globalenv()
    if (!is.null(m$tau.terms))   attr(m$tau.terms, ".Environment")   <- globalenv()
    models[[i]] <- m
  }

  sub <- ideas[ideas$sex == sex, ]
  ctl_mask <- sub$cohort == "control"
  cat(sprintf("  [%s / %s] N=%d, %d regions, rds=%s\n",
              sex, measure_label, nrow(sub), length(region_cols),
              basename(rds_path)))

  results <- vector("list", length(region_cols))
  for (i in seq_along(region_cols)) {
    m <- models[[i]]
    fam <- m$family[1]  # e.g. "BCCGo"
    nd <- data.frame(age = sub$age)

    mu    <- predict(m, newdata = nd, what = "mu", type = "response")
    sigma <- predict(m, newdata = nd, what = "sigma", type = "response")
    nu    <- if (!is.null(m$nu.terms))  predict(m, newdata = nd, what = "nu", type = "response")  else rep(0, nrow(sub))
    tau   <- if (!is.null(m$tau.terms)) predict(m, newdata = nd, what = "tau", type = "response") else rep(NA, nrow(sub))

    obs <- sub[[region_cols[i]]]

    # Raw GAMLSS Z-score (CDF-inverse-normal)
    centile <- compute_centile(obs, mu, sigma, nu, tau, fam)
    # Guard against 0/1 which would give -Inf/+Inf under qnorm
    centile <- pmin(pmax(centile, 1e-6), 1 - 1e-6)
    z_raw <- qnorm(centile)

    # Optional PCN Toolkit site adaptation on the Z-score scale
    # (subtract the mean of control z-scores per region — the analogue of
    #  mu_hat but in Z-space)
    z_shift <- if (any(ctl_mask)) mean(z_raw[ctl_mask], na.rm = TRUE) else 0
    z_adapted <- z_raw - z_shift

    results[[i]] <- data.frame(
      subject_id = sub$subject_id, cohort = sub$cohort, sex = sub$sex,
      age = sub$age, measure = measure_label, region = region_cols[i],
      observed = obs, mu = mu, sigma = sigma, nu = nu, tau = tau,
      centile = centile, z_raw = z_raw,
      z_shift = z_shift, z = z_adapted
    )
  }
  do.call(rbind, results)
}

run <- list(
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

cat("\nScoring with GAMLSS ...\n")
all_scores <- do.call(rbind, lapply(run, function(x)
  score_block(x$sex, x$label, x$cols, x$rds)))

out_long <- file.path(OUT_DIR, "ideas_zscores_centilebrain_gamlss.csv")
write.csv(all_scores, out_long, row.names = FALSE)
cat(sprintf("\nWrote long-form GAMLSS Z-scores: %s (%d rows)\n",
            out_long, nrow(all_scores)))

cat("\n=== Z-score distribution (RAW, before site adaptation) ===\n")
for (co in unique(all_scores$cohort)) {
  z <- all_scores$z_raw[all_scores$cohort == co]
  cat(sprintf("  cohort=%s  n=%d  mean=%.3f  sd=%.3f\n",
              co, length(z), mean(z, na.rm = TRUE), sd(z, na.rm = TRUE)))
}

cat("\n=== Z-score distribution (SITE-ADAPTED per PCN Toolkit) ===\n")
for (co in unique(all_scores$cohort)) {
  z <- all_scores$z[all_scores$cohort == co]
  cat(sprintf("  cohort=%s  n=%d  mean=%.3f  sd=%.3f\n",
              co, length(z), mean(z, na.rm = TRUE), sd(z, na.rm = TRUE)))
}
