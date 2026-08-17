#!/usr/bin/env Rscript

options(stringsAsFactors = FALSE, warn = 1)

suppressPackageStartupMessages({
  library(CRABS)
  library(jsonlite)
})

root <- normalizePath(getwd())
out_dir <- file.path(root, "experiments", "crabs_matched", "results")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

mode <- Sys.getenv("CRABS_BENCHMARK_MODE", unset = "full")
if (!mode %in% c("pilot", "full")) stop("CRABS_BENCHMARK_MODE must be pilot or full")

prereg <- fromJSON(file.path(root, "experiments", "crabs_matched", "PREREGISTRATION.json"), simplifyVector = FALSE)
cap <- as.numeric(prereg$scope$turnover_cap_c)
rho <- as.numeric(prereg$scope$sampling_fraction_rho)
cap_tol <- as.numeric(prereg$common_numerical_conventions$cap_acceptance_tolerance)
resid_tol <- as.numeric(prereg$common_numerical_conventions$congruence_residual_tolerance)
width_zero_tol <- as.numeric(prereg$common_numerical_conventions$endpoint_width_zero_tolerance)
accuracy_threshold <- as.numeric(prereg$common_numerical_conventions$endpoint_accuracy_threshold_fraction_of_identified_width)

all_sample_sizes <- unlist(prereg$sample_sizes)
all_seeds <- unlist(prereg$seeds)
proposal_ceiling <- as.integer(prereg$native_sampler_proposal_ceiling_per_replicate)
if (mode == "pilot") {
  sample_sizes <- 100L
  seeds <- all_seeds[1]
  native_ceiling <- min(5000L, proposal_ceiling)
} else {
  sample_sizes <- as.integer(all_sample_sizes)
  seeds <- as.integer(all_seeds)
  native_ceiling <- proposal_ceiling
}
Nmax <- max(sample_sizes)

RNGkind(kind = "Mersenne-Twister", normal.kind = "Inversion", sample.kind = "Rejection")

input <- read.csv(file.path(root, "data", "mammalia_tree1_psr.csv"), check.names = FALSE)
input <- input[input$tau_ma_after_1Ma_trim <= 70 + 1e-12, ]
times <- as.numeric(input$tau_ma_after_1Ma_trim)
lp <- as.numeric(input$lambda_p_per_ma)
actual_age <- as.numeric(input$actual_age_ma)
if (length(times) != 15L || any(abs(times - seq(0, 70, by = 5)) > 1e-12)) {
  stop("Released 0--70 Ma grid does not match preregistration")
}
dt <- times[2] - times[1]
if (any(abs(diff(times) - dt) > 1e-12)) stop("CRABS joint sampler requires equal spacing")
if (rho != 1) stop("This matched run is preregistered for rho=1")

lp_fun <- approxfun(times, lp, method = "linear", rule = 2)
mu_zero_fun <- function(t) rep(0, length(t))
reference_model <- CRABS::create.model(lp_fun, mu_zero_fun, times = times)
pdelta <- as.numeric(reference_model$p.delta(times))
lambda0 <- lp[1]

cumtrap <- function(y, x) {
  out <- numeric(length(y))
  if (length(y) > 1) out[-1] <- cumsum(0.5 * (y[-length(y)] + y[-1]) * diff(x))
  out
}

F <- exp(cumtrap(lp, times))
continuous_lower <- lp * F / (rho + F - 1)
continuous_upper <- lp * F / (rho + (1 - cap) * (F - 1))

solve_next_lambda <- function(lambda_prev, pdelta_i, epsilon, dt) {
  a <- 1 - epsilon
  b <- 1 / dt - pdelta_i
  disc <- b * b + 4 * a * lambda_prev / dt
  if (!is.finite(disc) || disc < 0 || a <= 0) return(NA_real_)
  (-b + sqrt(disc)) / (2 * a)
}

make_discrete_path <- function(epsilon) {
  if (length(epsilon) == 1L) epsilon <- rep(epsilon, length(times))
  if (length(epsilon) != length(times)) stop("epsilon length mismatch")
  lambda <- numeric(length(times))
  mu <- numeric(length(times))
  lambda[1] <- lambda0
  mu[1] <- epsilon[1] * lambda[1]
  for (i in 2:length(times)) {
    lambda[i] <- solve_next_lambda(lambda[i - 1], pdelta[i], epsilon[i], dt)
    mu[i] <- epsilon[i] * lambda[i]
  }
  list(lambda = lambda, mu = mu, epsilon = epsilon)
}

recurrence_residual <- function(lambda, mu) {
  out <- rep(NA_real_, length(lambda))
  out[-1] <- lambda[-1] - mu[-1] +
    (lambda[-1] - lambda[-length(lambda)]) / (lambda[-1] * dt) - pdelta[-1]
  out
}

discrete_lower_path <- make_discrete_path(0)
discrete_upper_path <- make_discrete_path(cap)
discrete_lower <- discrete_lower_path$lambda
discrete_upper <- discrete_upper_path$lambda
discrete_width <- discrete_upper - discrete_lower
nonzero <- discrete_width > width_zero_tol

exact_df <- data.frame(
  tau_ma = times,
  actual_age_ma = actual_age,
  lambda_p_per_ma = lp,
  F = F,
  CRABS_p_delta = pdelta,
  continuous_affine_lower = continuous_lower,
  continuous_affine_upper = continuous_upper,
  CRABS_discrete_lower = discrete_lower,
  CRABS_discrete_upper = discrete_upper,
  CRABS_discrete_width = discrete_width,
  continuous_minus_discrete_lower = continuous_lower - discrete_lower,
  continuous_minus_discrete_upper = continuous_upper - discrete_upper
)
write.csv(exact_df, file.path(out_dir, "exact_endpoints.csv"), row.names = FALSE)

# Validate that the exact discrete paths can be represented as actual CRABS models.
endpoint_models <- CRABS:::joint.congruent.models(
  reference_model,
  mus = list(
    approxfun(times, discrete_lower_path$mu, rule = 2),
    approxfun(times, discrete_upper_path$mu, rule = 2)
  ),
  lambdas = list(
    approxfun(times, discrete_lower_path$lambda, rule = 2),
    approxfun(times, discrete_upper_path$lambda, rule = 2)
  ),
  keep_ref = FALSE
)
endpoint_model_error <- max(
  abs(endpoint_models[[1]]$lambda(times) - discrete_lower),
  abs(endpoint_models[[2]]$lambda(times) - discrete_upper)
)

sample_cap_aware <- function(n, seed) {
  set.seed(seed)
  lambdas <- matrix(NA_real_, nrow = n, ncol = length(times))
  mus <- matrix(NA_real_, nrow = n, ncol = length(times))
  epsilons <- matrix(runif(n * length(times), min = 0, max = cap), nrow = n)
  lambdas[, 1] <- lambda0
  mus[, 1] <- epsilons[, 1] * lambda0
  for (i in 2:length(times)) {
    a <- 1 - epsilons[, i]
    b <- 1 / dt - pdelta[i]
    lambdas[, i] <- (-b + sqrt(b * b + 4 * a * lambdas[, i - 1] / dt)) / (2 * a)
    mus[, i] <- epsilons[, i] * lambdas[, i]
  }
  list(lambda = lambdas, mu = mus, epsilon = epsilons, attempts = n, accepted = n)
}

sample_native_hsmrf <- function(n, seed, ceiling) {
  set.seed(seed)
  lambdas <- matrix(NA_real_, nrow = n, ncol = length(times))
  mus <- matrix(NA_real_, nrow = n, ncol = length(times))
  accepted <- 0L
  attempts <- 0L
  invalid_nonfinite <- 0L
  invalid_negative <- 0L
  invalid_cap <- 0L
  sampler_errors <- 0L
  sampler <- getFromNamespace("sample.basic.models.joint", "CRABS")
  while (accepted < n && attempts < ceiling) {
    attempts <- attempts + 1L
    mu0 <- runif(1, min = 0, max = cap * lambda0)
    proposal <- try(
      sampler(
        times = times,
        p.delta = reference_model$p.delta,
        lambda0 = lambda0,
        mu0 = mu0,
        MRF.type = "HSMRF",
        beta.param = c(0.3, 0.3),
        mrf.sd.scale = 1.0,
        min.lambda = 0,
        min.mu = 0,
        max.lambda = 2,
        max.mu = 2,
        min.p = 0,
        max.p = 1
      ),
      silent = TRUE
    )
    if (inherits(proposal, "try-error")) {
      sampler_errors <- sampler_errors + 1L
      next
    }
    lam <- as.numeric(proposal$func_lambdas(times))
    mu <- as.numeric(proposal$func_mus(times))
    if (any(!is.finite(lam)) || any(!is.finite(mu)) || any(lam <= 0)) {
      invalid_nonfinite <- invalid_nonfinite + 1L
      next
    }
    if (any(mu < -cap_tol)) {
      invalid_negative <- invalid_negative + 1L
      next
    }
    eps <- mu / lam
    if (any(eps > cap + cap_tol)) {
      invalid_cap <- invalid_cap + 1L
      next
    }
    accepted <- accepted + 1L
    lambdas[accepted, ] <- lam
    mus[accepted, ] <- mu
  }
  if (accepted == 0L) {
    lambdas <- matrix(numeric(0), nrow = 0, ncol = length(times))
    mus <- matrix(numeric(0), nrow = 0, ncol = length(times))
  } else {
    lambdas <- lambdas[seq_len(accepted), , drop = FALSE]
    mus <- mus[seq_len(accepted), , drop = FALSE]
  }
  list(
    lambda = lambdas,
    mu = mus,
    attempts = attempts,
    accepted = accepted,
    rejection_counts = list(
      nonfinite = invalid_nonfinite,
      negative = invalid_negative,
      cap = invalid_cap,
      sampler_error = sampler_errors
    )
  )
}

validate_cap_aware_through_crabs <- function(seed) {
  set.seed(seed)
  generator <- function() {
    eps <- runif(length(times), min = 0, max = cap)
    path <- make_discrete_path(eps)
    list(
      func_lambdas = approxfun(times, path$lambda, rule = 2),
      func_mus = approxfun(times, path$mu, rule = 2)
    )
  }
  models <- CRABS::sample.congruence.class(
    model = reference_model,
    num.samples = 100,
    rate.type = "joint",
    sample.joint.rates = generator
  )
  # sample.congruence.class keeps the reference as the first model.
  sampled <- models[-1]
  max_cap <- max(vapply(sampled, function(m) max(m$mu(times) / m$lambda(times)), numeric(1)))
  max_resid <- max(vapply(sampled, function(m) {
    max(abs(recurrence_residual(m$lambda(times), m$mu(times))[-1]))
  }, numeric(1)))
  list(model_count = length(sampled), max_turnover = max_cap, max_recurrence_residual = max_resid)
}

summarise_prefix <- function(proposal_id, seed, sample_obj, n_requested, elapsed_sec) {
  n_available <- sample_obj$accepted
  n_used <- min(n_requested, n_available)
  if (n_used <= 0) {
    return(list(summary = data.frame(
      proposal = proposal_id, seed = seed, n_requested = n_requested, n_available = n_available,
      attempts = sample_obj$attempts, acceptance_rate = 0, elapsed_sec = elapsed_sec,
      target_lower_gap_fraction = NA_real_, target_upper_gap_fraction = NA_real_,
      max_lower_gap_fraction = NA_real_, max_upper_gap_fraction = NA_real_,
      fraction_knots_within_1pct_both = NA_real_, fraction_knots_within_5pct_both = NA_real_,
      fraction_knots_within_10pct_both = NA_real_, material_miss = TRUE,
      proposal_ceiling_hit = sample_obj$attempts >= native_ceiling
    ), by_age = NULL))
  }
  mat <- sample_obj$lambda[seq_len(n_used), , drop = FALSE]
  cloud_min <- apply(mat, 2, min)
  cloud_max <- apply(mat, 2, max)
  lower_gap <- rep(NA_real_, length(times))
  upper_gap <- rep(NA_real_, length(times))
  lower_gap[nonzero] <- (cloud_min[nonzero] - discrete_lower[nonzero]) / discrete_width[nonzero]
  upper_gap[nonzero] <- (discrete_upper[nonzero] - cloud_max[nonzero]) / discrete_width[nonzero]
  both_1 <- pmax(lower_gap[nonzero], upper_gap[nonzero]) <= 0.01
  both_5 <- pmax(lower_gap[nonzero], upper_gap[nonzero]) <= 0.05
  both_10 <- pmax(lower_gap[nonzero], upper_gap[nonzero]) <= 0.10
  target_i <- length(times)
  material <- n_available < n_requested || any(lower_gap[nonzero] > accuracy_threshold | upper_gap[nonzero] > accuracy_threshold)
  by_age <- data.frame(
    proposal = proposal_id,
    seed = seed,
    n_requested = n_requested,
    n_used = n_used,
    tau_ma = times,
    actual_age_ma = actual_age,
    cloud_min_lambda = cloud_min,
    cloud_max_lambda = cloud_max,
    exact_discrete_lower = discrete_lower,
    exact_discrete_upper = discrete_upper,
    lower_gap_fraction_of_width = lower_gap,
    upper_gap_fraction_of_width = upper_gap
  )
  summary <- data.frame(
    proposal = proposal_id,
    seed = seed,
    n_requested = n_requested,
    n_available = n_available,
    attempts = sample_obj$attempts,
    acceptance_rate = ifelse(sample_obj$attempts > 0, n_available / sample_obj$attempts, NA_real_),
    elapsed_sec = elapsed_sec,
    target_lower_gap_fraction = lower_gap[target_i],
    target_upper_gap_fraction = upper_gap[target_i],
    max_lower_gap_fraction = max(lower_gap[nonzero]),
    max_upper_gap_fraction = max(upper_gap[nonzero]),
    fraction_knots_within_1pct_both = mean(both_1),
    fraction_knots_within_5pct_both = mean(both_5),
    fraction_knots_within_10pct_both = mean(both_10),
    material_miss = material,
    proposal_ceiling_hit = proposal_id == "native_hsmrf_rejection" && sample_obj$attempts >= native_ceiling && n_available < n_requested
  )
  list(summary = summary, by_age = by_age)
}

summary_rows <- list()
by_age_rows <- list()
runtime_rows <- list()
rejection_records <- list()
validation_max_cap_excess <- -Inf
validation_max_residual <- -Inf
row_index <- 1L
age_index <- 1L
runtime_index <- 1L
rejection_index <- 1L

api_validation <- validate_cap_aware_through_crabs(all_seeds[1])

for (seed in seeds) {
  t0 <- proc.time()[["elapsed"]]
  cap_obj <- sample_cap_aware(Nmax, seed)
  cap_elapsed <- proc.time()[["elapsed"]] - t0
  eps_cap <- cap_obj$mu / cap_obj$lambda
  validation_max_cap_excess <- max(validation_max_cap_excess, max(eps_cap - cap))
  cap_residuals <- matrix(NA_real_, nrow = cap_obj$accepted, ncol = length(times) - 1)
  for (i in 2:length(times)) {
    cap_residuals[, i - 1] <- cap_obj$lambda[, i] - cap_obj$mu[, i] +
      (cap_obj$lambda[, i] - cap_obj$lambda[, i - 1]) / (cap_obj$lambda[, i] * dt) - pdelta[i]
  }
  validation_max_residual <- max(validation_max_residual, max(abs(cap_residuals)))
  runtime_rows[[runtime_index]] <- data.frame(
    proposal = "cap_aware_uniform", seed = seed, accepted = cap_obj$accepted,
    attempts = cap_obj$attempts, elapsed_sec = cap_elapsed,
    seconds_per_accepted = cap_elapsed / cap_obj$accepted
  )
  runtime_index <- runtime_index + 1L
  for (n in sample_sizes) {
    s <- summarise_prefix("cap_aware_uniform", seed, cap_obj, n, cap_elapsed)
    summary_rows[[row_index]] <- s$summary; row_index <- row_index + 1L
    by_age_rows[[age_index]] <- s$by_age; age_index <- age_index + 1L
  }

  t0 <- proc.time()[["elapsed"]]
  native_obj <- sample_native_hsmrf(Nmax, seed + 1000000L, native_ceiling)
  native_elapsed <- proc.time()[["elapsed"]] - t0
  if (native_obj$accepted > 0) {
    eps_native <- native_obj$mu / native_obj$lambda
    validation_max_cap_excess <- max(validation_max_cap_excess, max(eps_native - cap))
    native_residuals <- matrix(NA_real_, nrow = native_obj$accepted, ncol = length(times) - 1)
    for (i in 2:length(times)) {
      native_residuals[, i - 1] <- native_obj$lambda[, i] - native_obj$mu[, i] +
        (native_obj$lambda[, i] - native_obj$lambda[, i - 1]) / (native_obj$lambda[, i] * dt) - pdelta[i]
    }
    validation_max_residual <- max(validation_max_residual, max(abs(native_residuals)))
  }
  runtime_rows[[runtime_index]] <- data.frame(
    proposal = "native_hsmrf_rejection", seed = seed, accepted = native_obj$accepted,
    attempts = native_obj$attempts, elapsed_sec = native_elapsed,
    seconds_per_accepted = ifelse(native_obj$accepted > 0, native_elapsed / native_obj$accepted, NA_real_)
  )
  runtime_index <- runtime_index + 1L
  rejection_records[[rejection_index]] <- data.frame(
    seed = seed,
    attempts = native_obj$attempts,
    accepted = native_obj$accepted,
    rejected_nonfinite = native_obj$rejection_counts$nonfinite,
    rejected_negative = native_obj$rejection_counts$negative,
    rejected_cap = native_obj$rejection_counts$cap,
    sampler_errors = native_obj$rejection_counts$sampler_error
  )
  rejection_index <- rejection_index + 1L
  for (n in sample_sizes) {
    s <- summarise_prefix("native_hsmrf_rejection", seed, native_obj, n, native_elapsed)
    summary_rows[[row_index]] <- s$summary; row_index <- row_index + 1L
    if (!is.null(s$by_age)) { by_age_rows[[age_index]] <- s$by_age; age_index <- age_index + 1L }
  }

  # Keep target-age values for diagnosis without retaining full trajectories.
  target_values <- data.frame(
    proposal = c(rep("cap_aware_uniform", cap_obj$accepted), rep("native_hsmrf_rejection", native_obj$accepted)),
    seed = seed,
    draw = c(seq_len(cap_obj$accepted), seq_len(native_obj$accepted)),
    lambda_at_tau70 = c(cap_obj$lambda[, ncol(cap_obj$lambda)], if (native_obj$accepted > 0) native_obj$lambda[, ncol(native_obj$lambda)] else numeric(0))
  )
  target_path <- file.path(out_dir, sprintf("target_age_samples_seed_%d.csv.gz", seed))
  con <- gzfile(target_path, open = "wt")
  write.csv(target_values, con, row.names = FALSE)
  close(con)
}

replicate_summary <- do.call(rbind, summary_rows)
endpoint_by_age <- do.call(rbind, by_age_rows)
runtime_summary <- do.call(rbind, runtime_rows)
rejections <- do.call(rbind, rejection_records)
write.csv(replicate_summary, file.path(out_dir, "replicate_summary.csv"), row.names = FALSE)
write.csv(endpoint_by_age, file.path(out_dir, "endpoint_by_age.csv"), row.names = FALSE)
write.csv(runtime_summary, file.path(out_dir, "runtime_summary.csv"), row.names = FALSE)
write.csv(rejections, file.path(out_dir, "native_rejections.csv"), row.names = FALSE)

# Exact method timing, including continuous and CRABS-discrete endpoints.
exact_elapsed <- system.time({
  for (k in seq_len(1000)) {
    Fx <- exp(cumtrap(lp, times))
    lo <- lp * Fx / (rho + Fx - 1)
    hi <- lp * Fx / (rho + (1 - cap) * (Fx - 1))
    dlo <- make_discrete_path(0)$lambda
    dhi <- make_discrete_path(cap)$lambda
  }
})[["elapsed"]]
exact_runtime <- data.frame(
  repetitions = 1000L,
  total_elapsed_sec = exact_elapsed,
  seconds_per_full_endpoint_pair = exact_elapsed / 1000
)
write.csv(exact_runtime, file.path(out_dir, "exact_runtime.csv"), row.names = FALSE)

primary <- replicate_summary[replicate_summary$n_requested == max(all_sample_sizes), ]
if (mode == "pilot") primary <- replicate_summary[replicate_summary$n_requested == max(sample_sizes), ]
material_counts <- aggregate(material_miss ~ proposal, primary, function(x) sum(x, na.rm = TRUE))
native_runtime <- runtime_summary[runtime_summary$proposal == "native_hsmrf_rejection", ]
native_any_incomplete <- any(native_runtime$accepted < Nmax)
native_median_acceptance <- median(native_runtime$accepted / pmax(native_runtime$attempts, 1))
native_practical_failure <- native_any_incomplete || native_median_acceptance < 0.02
cap_material <- material_counts$material_miss[material_counts$proposal == "cap_aware_uniform"]
native_material <- material_counts$material_miss[material_counts$proposal == "native_hsmrf_rejection"]
if (length(cap_material) == 0) cap_material <- NA_integer_
if (length(native_material) == 0) native_material <- NA_integer_
material_endpoint_miss <- (!is.na(cap_material) && cap_material >= ceiling(length(seeds) / 2)) ||
  (!is.na(native_material) && native_material >= ceiling(length(seeds) / 2))
recommend_affine <- material_endpoint_miss || native_practical_failure

validation <- list(
  mode = mode,
  endpoint_CRABS_object_max_abs_error = endpoint_model_error,
  cap_aware_CRABS_API_validation = api_validation,
  maximum_turnover_cap_excess_across_accepted_histories = validation_max_cap_excess,
  maximum_CRABS_recurrence_residual_across_accepted_histories = validation_max_residual,
  exact_lower_endpoint_recurrence_residual = max(abs(recurrence_residual(discrete_lower_path$lambda, discrete_lower_path$mu)[-1])),
  exact_upper_endpoint_recurrence_residual = max(abs(recurrence_residual(discrete_upper_path$lambda, discrete_upper_path$mu)[-1])),
  continuous_vs_discrete_max_abs_lower = max(abs(continuous_lower - discrete_lower)),
  continuous_vs_discrete_max_abs_upper = max(abs(continuous_upper - discrete_upper)),
  cap_tolerance = cap_tol,
  recurrence_tolerance = resid_tol,
  checks_pass = endpoint_model_error <= resid_tol &&
    api_validation$max_turnover <= cap + cap_tol &&
    api_validation$max_recurrence_residual <= resid_tol &&
    validation_max_cap_excess <= cap_tol &&
    validation_max_residual <= resid_tol
)
write_json(validation, file.path(out_dir, "validation_checks.json"), pretty = TRUE, auto_unbox = TRUE, digits = 16)

protocol_realised <- list(
  execution_mode = mode,
  executed_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
  release_tag = prereg$release_target$tag,
  CRABS_commit = prereg$comparator$commit,
  CRABS_version = as.character(packageVersion("CRABS")),
  R_version = R.version.string,
  platform = R.version$platform,
  grid = times,
  sample_sizes = sample_sizes,
  seeds = seeds,
  turnover_cap = cap,
  rho = rho,
  native_proposal_ceiling = native_ceiling,
  deviations_from_preregistration = if (mode == "pilot") "Pilot reduced to one seed and N=100; no primary decision." else "none"
)
write_json(protocol_realised, file.path(out_dir, "protocol_realised.json"), pretty = TRUE, auto_unbox = TRUE, digits = 16)

verdict <- list(
  execution_mode = mode,
  primary_sample_size = if (mode == "pilot") max(sample_sizes) else max(all_sample_sizes),
  replicate_count = length(seeds),
  material_miss_replicates = setNames(as.list(material_counts$material_miss), material_counts$proposal),
  native_any_incomplete = native_any_incomplete,
  native_median_acceptance_rate = native_median_acceptance,
  native_practical_failure = native_practical_failure,
  material_endpoint_miss = material_endpoint_miss,
  recommend_affine_for_endpoint_certification = if (mode == "full") recommend_affine else NA,
  scope = "CRABS remains an exploration tool; this verdict concerns sharp endpoint certification under the matched cap."
)
write_json(verdict, file.path(out_dir, "verdict.json"), pretty = TRUE, auto_unbox = TRUE, digits = 16)

# Base-R figures use a non-standard, print-safe palette.
col_cap <- "#168C8C"
col_native <- "#B23A6F"
col_exact <- "#6750A4"
col_lower <- "#C58B1B"

png(file.path(out_dir, "figure_endpoint_recovery_tau70.png"), width = 1500, height = 900, res = 160)
plot(NA, xlim = range(sample_sizes), ylim = c(0, 1), log = "x",
     xlab = "Accepted histories", ylab = "Endpoint deficit / identified width",
     main = "Matched CRABS endpoint recovery at 70 Ma")
for (proposal in unique(replicate_summary$proposal)) {
  dat <- replicate_summary[replicate_summary$proposal == proposal, ]
  agg <- aggregate(cbind(target_lower_gap_fraction, target_upper_gap_fraction) ~ n_requested, dat, median, na.rm = TRUE)
  colour <- if (proposal == "cap_aware_uniform") col_cap else col_native
  lines(agg$n_requested, agg$target_upper_gap_fraction, type = "b", pch = 19, lwd = 2, col = colour)
  lines(agg$n_requested, agg$target_lower_gap_fraction, type = "b", pch = 1, lwd = 2, col = colour, lty = 2)
}
abline(h = accuracy_threshold, lty = 3, lwd = 2, col = col_exact)
legend("topright", legend = c("Cap-aware upper", "Cap-aware lower", "Native HSMRF upper", "Native HSMRF lower", "5% threshold"),
       col = c(col_cap, col_cap, col_native, col_native, col_exact),
       lty = c(1, 2, 1, 2, 3), pch = c(19, 1, 19, 1, NA), bty = "n")
dev.off()

png(file.path(out_dir, "figure_exact_and_cloud_envelopes.png"), width = 1500, height = 900, res = 160)
plot(times, discrete_upper, type = "l", lwd = 3, col = col_exact,
     ylim = range(c(discrete_lower, discrete_upper, continuous_upper), finite = TRUE),
     xlab = "Age after 1 Ma trim (Ma)", ylab = "Speciation rate (lineages/Ma)",
     main = sprintf("Exact endpoints and median N=%d CRABS cloud", max(sample_sizes)))
lines(times, discrete_lower, lwd = 3, col = col_lower)
lines(times, continuous_upper, lwd = 2, lty = 3, col = col_exact)
for (proposal in unique(endpoint_by_age$proposal)) {
  dat <- endpoint_by_age[endpoint_by_age$proposal == proposal & endpoint_by_age$n_requested == max(sample_sizes), ]
  if (nrow(dat) > 0) {
    upper_med <- aggregate(cloud_max_lambda ~ tau_ma, dat, median, na.rm = TRUE)
    lower_med <- aggregate(cloud_min_lambda ~ tau_ma, dat, median, na.rm = TRUE)
    colour <- if (proposal == "cap_aware_uniform") col_cap else col_native
    lines(upper_med$tau_ma, upper_med$cloud_max_lambda, lwd = 2, col = colour)
    lines(lower_med$tau_ma, lower_med$cloud_min_lambda, lwd = 2, lty = 2, col = colour)
  }
}
legend("topleft", legend = c("CRABS-discrete exact upper", "CRABS-discrete exact lower", "Continuous affine upper", "Cap-aware cloud", "Native HSMRF cloud"),
       col = c(col_exact, col_lower, col_exact, col_cap, col_native),
       lty = c(1, 1, 3, 1, 1), lwd = c(3, 3, 2, 2, 2), bty = "n")
dev.off()

capture.output(sessionInfo(), file = file.path(out_dir, "sessionInfo.txt"))

# Human-readable report assembled from the preregistered metrics.
report <- c(
  "# Matched CRABS comparison",
  "",
  sprintf("**Execution mode:** %s", mode),
  sprintf("**Signal:** released Mammalia pulled-speciation curve, tau 0--70 Ma, 5 Ma knots"),
  sprintf("**Restriction:** 0 <= mu/lambda <= %.3f; rho=%.1f; no fossil constraints", cap, rho),
  sprintf("**Comparator:** CRABS %s at commit %s", as.character(packageVersion("CRABS")), prereg$comparator$commit),
  "",
  "## Validation",
  "",
  sprintf("- Maximum accepted cap excess: %.3e", validation_max_cap_excess),
  sprintf("- Maximum CRABS recurrence residual: %.3e", validation_max_residual),
  sprintf("- Continuous/discrete upper-endpoint maximum absolute difference: %.6g", validation$continuous_vs_discrete_max_abs_upper),
  sprintf("- Validation checks passed: %s", validation$checks_pass),
  "",
  "## Preregistered decision inputs",
  "",
  sprintf("- Material-miss replicates, cap-aware proposal: %s", cap_material),
  sprintf("- Material-miss replicates, native HSMRF proposal: %s", native_material),
  sprintf("- Native median acceptance rate: %.6f", native_median_acceptance),
  sprintf("- Native sampler incomplete in any replicate: %s", native_any_incomplete),
  sprintf("- Material endpoint miss rule triggered: %s", material_endpoint_miss),
  sprintf("- Native practicality rule triggered: %s", native_practical_failure),
  "",
  "## Verdict",
  "",
  if (mode == "pilot") {
    "Pilot only. The preregistered primary decision is withheld until the full run."
  } else if (recommend_affine) {
    "The preregistered adoption rule recommends the affine routine for endpoint certification. CRABS remains suitable for stochastic exploration, but the matched finite cloud either materially misses an endpoint or fails the native practicality threshold."
  } else {
    "At the preregistered scale, CRABS empirically approximates the matched endpoints within the tolerance rule. It still supplies no endpoint certificate; the affine routine remains the certification layer."
  },
  "",
  "## Scope",
  "",
  "This is a deterministic comparison conditional on one fixed pulled signal. It is not a confidence-coverage study, fossil validation, or general ranking of diversification software."
)
writeLines(report, file.path(out_dir, "matched_comparison_report.md"))

cat(toJSON(list(mode = mode, validation = validation, verdict = verdict), pretty = TRUE, auto_unbox = TRUE, digits = 16), "\n")
