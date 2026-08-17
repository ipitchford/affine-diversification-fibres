#!/usr/bin/env Rscript

options(stringsAsFactors = FALSE, warn = 1)
suppressPackageStartupMessages({
  library(CRABS)
  library(jsonlite)
})

root <- normalizePath(getwd())
out_dir <- file.path(root, "exploratory", "results")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

input <- read.csv(file.path(root, "data", "mammalia_tree1_psr.csv"), check.names = FALSE)
input <- input[input$tau_ma_after_1Ma_trim <= 70 + 1e-12, ]
base_times <- as.numeric(input$tau_ma_after_1Ma_trim)
base_lp <- as.numeric(input$lambda_p_per_ma)
lp_fun <- approxfun(base_times, base_lp, method = "linear", rule = 2)
mu_zero_fun <- function(t) rep(0, length(t))
cap <- 0.5
rho <- 1.0
steps <- c(5, 2.5, 1, 0.5, 0.25, 0.1, 0.05)

cumtrap <- function(y, x) {
  out <- numeric(length(y))
  if (length(y) > 1) out[-1] <- cumsum(0.5 * (y[-length(y)] + y[-1]) * diff(x))
  out
}

solve_path <- function(times, pdelta, lambda0, epsilon) {
  dt <- times[2] - times[1]
  lambda <- numeric(length(times))
  lambda[1] <- lambda0
  for (i in 2:length(times)) {
    a <- 1 - epsilon
    b <- 1 / dt - pdelta[i]
    lambda[i] <- (-b + sqrt(b * b + 4 * a * lambda[i - 1] / dt)) / (2 * a)
  }
  lambda
}

rows <- list()
for (j in seq_along(steps)) {
  step <- steps[j]
  times <- seq(0, 70, by = step)
  lp <- lp_fun(times)
  model <- CRABS::create.model(lp_fun, mu_zero_fun, times = times)
  pdelta <- as.numeric(model$p.delta(times))
  lower_discrete <- solve_path(times, pdelta, lp[1], 0)
  upper_discrete <- solve_path(times, pdelta, lp[1], cap)
  F <- exp(cumtrap(lp, times))
  lower_continuous <- lp * F / (rho + F - 1)
  upper_continuous <- lp * F / (rho + (1 - cap) * (F - 1))
  rows[[j]] <- data.frame(
    grid_step_ma = step,
    knot_count = length(times),
    max_abs_lower_error = max(abs(lower_discrete - lower_continuous)),
    max_abs_upper_error = max(abs(upper_discrete - upper_continuous)),
    tau70_discrete_lower = tail(lower_discrete, 1),
    tau70_discrete_upper = tail(upper_discrete, 1),
    tau70_continuous_lower = tail(lower_continuous, 1),
    tau70_continuous_upper = tail(upper_continuous, 1),
    tau70_lower_error = tail(lower_discrete - lower_continuous, 1),
    tau70_upper_error = tail(upper_discrete - upper_continuous, 1)
  )
}

results <- do.call(rbind, rows)
write.csv(results, file.path(out_dir, "crabs_grid_sensitivity.csv"), row.names = FALSE)

validation <- list(
  status = "exploratory_post_preregistration",
  primary_decision_unchanged = TRUE,
  signal = "released Mammalia pulled-speciation curve, piecewise linear, 0--70 Ma",
  turnover_cap = cap,
  CRABS_version = as.character(packageVersion("CRABS")),
  CRABS_commit = "f2af9b6c8bb93f5512c2882d2e816060c9e07728",
  R_version = R.version.string,
  coarse_grid_upper_error_matches_primary = abs(results$max_abs_upper_error[results$grid_step_ma == 5] - 0.09853170579826911) < 1e-10,
  note = "This check isolates finite-difference convergence. It is not part of the preregistered sampling decision and does not tune either proposal."
)
write_json(validation, file.path(out_dir, "crabs_grid_sensitivity.json"), pretty = TRUE, auto_unbox = TRUE, digits = 16)
capture.output(sessionInfo(), file = file.path(out_dir, "sessionInfo_grid_sensitivity.txt"))

cat(toJSON(list(validation = validation, results = results), pretty = TRUE, auto_unbox = TRUE, digits = 16), "\n")
