#!/usr/bin/env Rscript

options(stringsAsFactors = FALSE, warn = 1, digits = 17)

suppressPackageStartupMessages({
  library(CRABS)
  library(digest)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 4L) {
  stop("usage: run_stochastic_cell.R PROJECT_ROOT CELL_ID RESULT_DIR SAMPLE_DIR")
}

root <- normalizePath(args[[1]], mustWork = TRUE)
cell_id <- args[[2]]
result_dir <- normalizePath(args[[3]], mustWork = FALSE)
sample_dir <- normalizePath(args[[4]], mustWork = FALSE)
dir.create(result_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(sample_dir, recursive = TRUE, showWarnings = FALSE)
protocol_dir <- file.path(root, "experiments", "affine_crabs_confirmatory")
result_path <- file.path(result_dir, paste0(cell_id, ".json"))
sample_path <- file.path(sample_dir, paste0(cell_id, "_decision_values.csv"))

sha256_file <- function(path) digest::digest(file = path, algo = "sha256", serialize = FALSE)

git_value <- function(...) {
  out <- system2("git", c("-C", root, ...), stdout = TRUE, stderr = TRUE)
  status <- attr(out, "status")
  if (!is.null(status) && status != 0L) stop(paste(out, collapse = "\n"))
  trimws(paste(out, collapse = "\n"))
}

manifest_lines <- readLines(file.path(protocol_dir, "CELL_MANIFEST.jsonl"), warn = FALSE)
matching <- manifest_lines[grepl(paste0('"cell_id":"', cell_id, '"'), manifest_lines, fixed = TRUE)]
if (length(matching) != 1L) stop("cell id is not uniquely registered")
cell <- jsonlite::fromJSON(matching[[1]], simplifyVector = FALSE)
if (!identical(cell$layer, "stochastic")) stop("cell is not stochastic")

execution_commit <- git_value("rev-parse", "HEAD")
bindings <- list(
  protocol_sha256 = sha256_file(file.path(protocol_dir, "PREREGISTRATION.json")),
  cell_manifest_sha256 = sha256_file(file.path(protocol_dir, "CELL_MANIFEST.jsonl")),
  amendment_001_sha256 = sha256_file(file.path(protocol_dir, "AMENDMENT_001_PRE_EXECUTION.json")),
  amendment_002_sha256 = sha256_file(file.path(protocol_dir, "AMENDMENT_002_COMMIT_CORRECTION.json")),
  amendment_003_sha256 = sha256_file(file.path(protocol_dir, "AMENDMENT_003_STOCHASTIC_METRICS.json")),
  amendment_004_sha256 = sha256_file(file.path(protocol_dir, "AMENDMENT_004_NONTERMINATION_REPAIR.json")),
  primates_qualification_receipt_sha256 = sha256_file(file.path(
    protocol_dir, "execution", "qualification", "PRIMATES_QUALIFICATION_RECEIPT.json"
  )),
  deterministic_execution_receipt_sha256 = sha256_file(file.path(
    protocol_dir, "execution", "DETERMINISTIC_EXECUTION_RECEIPT.json"
  )),
  stochastic_stage1_incident_sha256 = sha256_file(file.path(
    protocol_dir, "execution", "STOCHASTIC_STAGE1_INCIDENT.json"
  )),
  execution_commit = execution_commit
)

if (file.exists(result_path)) {
  existing <- jsonlite::fromJSON(result_path, simplifyVector = FALSE)
  if (!identical(existing$cell$cell_id, cell_id) ||
      !identical(existing$bindings$execution_commit, execution_commit)) {
    stop("existing stochastic result has different bindings")
  }
  cat(jsonlite::toJSON(list(cell_id = cell_id, status = existing$status, existing = TRUE), auto_unbox = TRUE), "\n")
  quit(save = "no", status = 0L)
}

load_signal <- function(signal_id, knots) {
  if (identical(signal_id, "crabs_primates_ebd")) {
    path <- file.path(protocol_dir, "execution", "qualification", sprintf("crabs_primates_ebd_%03d.csv", knots))
    receipt <- jsonlite::fromJSON(file.path(
      protocol_dir, "execution", "qualification", "PRIMATES_QUALIFICATION_RECEIPT.json"
    ), simplifyVector = FALSE)
    expected <- receipt$resampled_grids[[as.character(knots)]]$sha256
    if (!identical(receipt$status, "QUALIFIED_ELIGIBLE") || !identical(sha256_file(path), expected)) {
      stop("primates signal is not qualified")
    }
    data <- read.csv(path, check.names = FALSE)
    return(list(time = as.numeric(data$time), lambda_p = as.numeric(data$lambda_p), sha256 = expected))
  }
  frozen <- jsonlite::fromJSON(file.path(protocol_dir, "synthetic_signals.json"), simplifyVector = FALSE)
  for (signal in frozen$signals) {
    if (!identical(signal$id, signal_id)) next
    for (grid in signal$grids) {
      if (as.integer(grid$knots) == knots) {
        return(list(time = as.numeric(unlist(grid$tau)), lambda_p = as.numeric(unlist(grid$lambda_p)), sha256 = grid$sha256))
      }
    }
  }
  stop("registered signal/grid not found")
}

input <- load_signal(cell$signal_id, as.integer(cell$grid_knots))
times <- input$time
lambda_p <- input$lambda_p
nt <- length(times)
dt <- times[[2]] - times[[1]]
if (max(abs(diff(times) - dt)) > 1e-12 * max(1, abs(dt))) stop("CRABS stochastic cell grid is not equal")
if (any(!is.finite(lambda_p)) || any(lambda_p < 0)) stop("invalid pulled-speciation input")

lambda_fun <- approxfun(times, lambda_p, method = "linear", rule = 2)
mu_zero <- function(t) rep(0, length(t))
reference_model <- CRABS::create.model(lambda_fun, mu_zero, times = times)
pdelta <- as.numeric(reference_model$p.delta(times))
lambda0 <- lambda_p[[1]]
if (!is.finite(lambda0) || lambda0 <= 0 || lambda0 > 2) stop("lambda0 lies outside frozen CRABS bounds")

cumtrap <- function(y, x) {
  out <- numeric(length(y))
  if (length(y) > 1L) out[-1] <- cumsum(0.5 * (y[-length(y)] + y[-1]) * diff(x))
  out
}

solve_next <- function(lambda_previous, pdelta_i, epsilon, delta) {
  a <- 1 - epsilon
  b <- 1 / delta - pdelta_i
  discriminant <- b * b + 4 * a * lambda_previous / delta
  answer <- (-b + sqrt(pmax(discriminant, 0))) / (2 * a)
  answer[!is.finite(discriminant) | discriminant < 0 | a <= 0 | !is.finite(answer) | answer <= 0] <- NA_real_
  answer
}

make_discrete_path <- function(epsilon) {
  if (length(epsilon) == 1L) epsilon <- rep(epsilon, nt)
  lambda <- numeric(nt)
  mu <- numeric(nt)
  lambda[[1]] <- lambda0
  mu[[1]] <- epsilon[[1]] * lambda0
  if (nt > 1L) {
    for (index in 2:nt) {
      lambda[[index]] <- solve_next(lambda[[index - 1]], pdelta[[index]], epsilon[[index]], dt)
      mu[[index]] <- epsilon[[index]] * lambda[[index]]
    }
  }
  list(lambda = lambda, mu = mu, epsilon = epsilon)
}

recurrence_residual <- function(lambda, mu) {
  if (is.null(dim(lambda))) {
    residual <- lambda[-1] - mu[-1] +
      (lambda[-1] - lambda[-length(lambda)]) / (lambda[-1] * dt) - pdelta[-1]
    return(max(abs(residual)))
  }
  residual_max <- 0
  for (index in 2:nt) {
    residual <- lambda[, index] - mu[, index] +
      (lambda[, index] - lambda[, index - 1]) / (lambda[, index] * dt) - pdelta[[index]]
    residual_max <- max(residual_max, abs(residual), na.rm = TRUE)
  }
  residual_max
}

decision_indices <- as.integer(floor(c(0.25, 0.5, 0.75, 1.0) * (nt - 1) + 0.5) + 1L)
if (length(unique(decision_indices)) != 4L) stop("decision-age indices are not distinct")
prefixes <- as.integer(unlist(cell$accepted_cloud_prefixes))
target <- max(prefixes)
attempt_ceiling <- if (is.null(cell$proposal_ceiling)) 2000000L else as.integer(cell$proposal_ceiling)

cap <- if (is.null(cell$turnover_cap)) NA_real_ else as.numeric(cell$turnover_cap)
minimum_path <- make_discrete_path(0)
exact <- NULL
if (identical(cell$task, "cap_matched")) {
  lower_path <- minimum_path
  upper_path <- make_discrete_path(cap)
  F <- exp(cumtrap(lambda_p, times))
  continuous_lower <- lambda_p * F / F
  continuous_upper <- lambda_p * F / (1 + (1 - cap) * (F - 1))
  exact <- list(
    continuous_lower = continuous_lower,
    continuous_upper = continuous_upper,
    discrete_lower = lower_path$lambda,
    discrete_upper = upper_path$lambda,
    discrete_lower_residual = recurrence_residual(lower_path$lambda, lower_path$mu),
    discrete_upper_residual = recurrence_residual(upper_path$lambda, upper_path$mu),
    continuous_discrete_max_abs_lower = max(abs(continuous_lower - lower_path$lambda)),
    continuous_discrete_max_abs_upper = max(abs(continuous_upper - upper_path$lambda))
  )
}

RNGkind(kind = "Mersenne-Twister", normal.kind = "Inversion", sample.kind = "Rejection")
set.seed(as.integer(cell$seed))
started <- proc.time()[["elapsed"]]

uses_crabs_internal_sampler <- cell$explorer %in% c("crabs_hsmrf", "crabs_gmrf", "crabs_rejection")
violating_indices <- which(minimum_path$lambda > 2 + 1e-12)
structural_censor <- NULL
if (uses_crabs_internal_sampler && length(violating_indices) > 0L) {
  first_violation <- violating_indices[[1]]
  stage1_incident <- jsonlite::fromJSON(file.path(
    protocol_dir, "execution", "STOCHASTIC_STAGE1_INCIDENT.json"
  ), simplifyVector = FALSE)
  structural_censor <- list(
    type = "minimum_required_lambda_exceeds_frozen_CRABS_max",
    first_violating_index = first_violation,
    time = times[[first_violation]],
    required_minimum_lambda = minimum_path$lambda[[first_violation]],
    frozen_max_lambda = 2.0,
    excess = minimum_path$lambda[[first_violation]] - 2.0,
    maximum_required_lambda = max(minimum_path$lambda),
    crabs_source_sha256 = stage1_incident$proof$crabs_source_sha256,
    stage1_incident_sha256 = bindings$stochastic_stage1_incident_sha256
  )
}

sample_crabs <- function(mrf_type, reject_cap = NULL) {
  sampler <- getFromNamespace("sample.basic.models.joint", "CRABS")
  lambdas <- matrix(NA_real_, nrow = target, ncol = nt)
  mus <- matrix(NA_real_, nrow = target, ncol = nt)
  accepted <- 0L
  attempts <- 0L
  rejected <- list(nonfinite = 0L, nonpositive_lambda = 0L, negative_mu = 0L, cap = 0L, sampler_error = 0L)
  while (accepted < target && attempts < attempt_ceiling) {
    attempts <- attempts + 1L
    mu_max <- if (is.null(reject_cap)) lambda0 else reject_cap * lambda0
    mu0 <- runif(1L, min = 0, max = mu_max)
    proposal <- try(suppressWarnings(sampler(
      times = times,
      p.delta = reference_model$p.delta,
      lambda0 = lambda0,
      mu0 = mu0,
      MRF.type = mrf_type,
      beta.param = c(0.3, 0.3),
      mrf.sd.scale = 1.0,
      min.lambda = 0,
      min.mu = 0,
      max.lambda = 2,
      max.mu = 2,
      min.p = 0,
      max.p = 1
    )), silent = TRUE)
    if (inherits(proposal, "try-error")) {
      rejected$sampler_error <- rejected$sampler_error + 1L
      next
    }
    lambda <- as.numeric(proposal$func_lambdas(times))
    mu <- as.numeric(proposal$func_mus(times))
    if (any(!is.finite(lambda)) || any(!is.finite(mu))) {
      rejected$nonfinite <- rejected$nonfinite + 1L
      next
    }
    if (any(lambda <= 0)) {
      rejected$nonpositive_lambda <- rejected$nonpositive_lambda + 1L
      next
    }
    if (any(mu < -1e-12)) {
      rejected$negative_mu <- rejected$negative_mu + 1L
      next
    }
    if (!is.null(reject_cap) && any(mu / lambda > reject_cap + 1e-12)) {
      rejected$cap <- rejected$cap + 1L
      next
    }
    accepted <- accepted + 1L
    lambdas[accepted, ] <- lambda
    mus[accepted, ] <- mu
  }
  if (accepted == 0L) {
    lambdas <- matrix(numeric(0), nrow = 0L, ncol = nt)
    mus <- matrix(numeric(0), nrow = 0L, ncol = nt)
  } else {
    lambdas <- lambdas[seq_len(accepted), , drop = FALSE]
    mus <- mus[seq_len(accepted), , drop = FALSE]
  }
  list(lambda = lambdas, mu = mus, accepted = accepted, attempts = attempts, rejected = rejected)
}

sample_cap_aware <- function() {
  lambdas <- matrix(NA_real_, nrow = target, ncol = nt)
  mus <- matrix(NA_real_, nrow = target, ncol = nt)
  accepted <- 0L
  attempts <- 0L
  invalid <- 0L
  while (accepted < target && attempts < attempt_ceiling) {
    batch_size <- min(target - accepted, attempt_ceiling - attempts, 10000L)
    epsilon <- matrix(runif(batch_size * nt, min = 0, max = cap), nrow = batch_size, ncol = nt)
    lambda <- matrix(NA_real_, nrow = batch_size, ncol = nt)
    lambda[, 1] <- lambda0
    for (index in 2:nt) {
      lambda[, index] <- solve_next(lambda[, index - 1], pdelta[[index]], epsilon[, index], dt)
    }
    mu <- epsilon * lambda
    valid <- apply(is.finite(lambda) & lambda > 0 & is.finite(mu) & mu >= -1e-12, 1L, all)
    attempts <- attempts + batch_size
    invalid <- invalid + sum(!valid)
    keep <- which(valid)
    if (length(keep) > 0L) {
      number <- min(length(keep), target - accepted)
      destinations <- accepted + seq_len(number)
      lambdas[destinations, ] <- lambda[keep[seq_len(number)], , drop = FALSE]
      mus[destinations, ] <- mu[keep[seq_len(number)], , drop = FALSE]
      accepted <- accepted + number
    }
  }
  if (accepted == 0L) {
    lambdas <- matrix(numeric(0), nrow = 0L, ncol = nt)
    mus <- matrix(numeric(0), nrow = 0L, ncol = nt)
  } else {
    lambdas <- lambdas[seq_len(accepted), , drop = FALSE]
    mus <- mus[seq_len(accepted), , drop = FALSE]
  }
  list(
    lambda = lambdas, mu = mus, accepted = accepted, attempts = attempts,
    rejected = list(invalid_recurrence = invalid)
  )
}

if (!is.null(structural_censor)) {
  samples <- list(
    lambda = matrix(numeric(0), nrow = 0L, ncol = nt),
    mu = matrix(numeric(0), nrow = 0L, ncol = nt),
    accepted = 0L,
    attempts = 0L,
    rejected = list(structural_nontermination = 1L)
  )
} else if (identical(cell$explorer, "crabs_hsmrf")) {
  samples <- sample_crabs("HSMRF")
} else if (identical(cell$explorer, "crabs_gmrf")) {
  samples <- sample_crabs("GMRF")
} else if (identical(cell$explorer, "crabs_rejection")) {
  samples <- sample_crabs("HSMRF", cap)
} else if (identical(cell$explorer, "cap_aware_uniform")) {
  samples <- sample_cap_aware()
} else if (identical(cell$explorer, "boundary_constructor")) {
  samples <- list(
    lambda = rbind(exact$discrete_lower, exact$discrete_upper),
    mu = rbind(make_discrete_path(0)$mu, make_discrete_path(cap)$mu),
    accepted = 2L,
    attempts = 2L,
    rejected = list()
  )
} else {
  stop("unknown registered explorer")
}

elapsed <- proc.time()[["elapsed"]] - started
accepted <- samples$accepted
recurrence_max <- if (accepted > 0L) recurrence_residual(samples$lambda, samples$mu) else NA_real_
cap_excess <- if (identical(cell$task, "cap_matched") && accepted > 0L) {
  max(samples$mu / samples$lambda - cap)
} else {
  NA_real_
}

prefix_summaries <- list()
largest_prefix <- NA_integer_
if (!identical(cell$explorer, "boundary_constructor")) {
  attained <- prefixes[prefixes <= accepted]
  if (length(attained) > 0L) largest_prefix <- max(attained)
  for (prefix in attained) {
    lambda <- samples$lambda[seq_len(prefix), , drop = FALSE]
    cloud_min <- apply(lambda, 2L, min)
    cloud_max <- apply(lambda, 2L, max)
    summary <- list(prefix = prefix, cloud_min = cloud_min, cloud_max = cloud_max)
    if (!is.null(exact)) {
      width <- exact$discrete_upper - exact$discrete_lower
      nonzero <- width > 1e-12 * pmax(1, abs(exact$discrete_lower), abs(exact$discrete_upper))
      indices <- decision_indices[nonzero[decision_indices]]
      lower_deficit <- pmax(0, cloud_min[indices] - exact$discrete_lower[indices]) / width[indices]
      upper_deficit <- pmax(0, exact$discrete_upper[indices] - cloud_max[indices]) / width[indices]
      summary$normalized_deficit <- max(c(lower_deficit, upper_deficit))
      summary$decision_lower_deficits <- lower_deficit
      summary$decision_upper_deficits <- upper_deficit
    }
    prefix_summaries[[as.character(prefix)]] <- summary
  }
}

queries <- list()
query_changed <- 0L
false_certificates <- 0L
if (identical(cell$explorer, "crabs_rejection") && is.finite(largest_prefix)) {
  lambda <- samples$lambda[seq_len(largest_prefix), , drop = FALSE]
  cloud_min <- apply(lambda, 2L, min)
  cloud_max <- apply(lambda, 2L, max)
  signal_median <- median(lambda_p)
  multipliers <- c(0.5, 1.0, 2.0, 4.0)
  query_index <- 1L
  for (age_index in decision_indices) {
    for (multiplier in multipliers) {
      threshold <- multiplier * signal_median
      cloud_status <- if (cloud_max[[age_index]] < threshold) "BELOW" else if (cloud_min[[age_index]] > threshold) "ABOVE" else "UNRESOLVED"
      certificate_status <- if (exact$continuous_upper[[age_index]] < threshold) "BELOW" else if (exact$continuous_lower[[age_index]] > threshold) "ABOVE" else "UNRESOLVED"
      discrete_status <- if (exact$discrete_upper[[age_index]] < threshold) "BELOW" else if (exact$discrete_lower[[age_index]] > threshold) "ABOVE" else "UNRESOLVED"
      changed <- !identical(cloud_status, certificate_status)
      false_certificate <- (identical(certificate_status, "BELOW") && exact$continuous_upper[[age_index]] >= threshold) ||
        (identical(certificate_status, "ABOVE") && exact$continuous_lower[[age_index]] <= threshold)
      query_changed <- query_changed + as.integer(changed)
      false_certificates <- false_certificates + as.integer(false_certificate)
      queries[[query_index]] <- list(
        age_index = age_index,
        time = times[[age_index]],
        threshold_multiplier = multiplier,
        threshold = threshold,
        finite_cloud_status = cloud_status,
        continuous_certificate_status = certificate_status,
        discrete_endpoint_status = discrete_status,
        changed = changed,
        false_certificate = false_certificate
      )
      query_index <- query_index + 1L
    }
  }
}

sidecar <- NULL
if (!identical(cell$explorer, "boundary_constructor")) {
  values <- data.frame(draw = if (accepted > 0L) seq_len(accepted) else integer(0))
  for (offset in seq_along(decision_indices)) {
    values[[paste0("lambda_at_index_", decision_indices[[offset]])]] <-
      if (accepted > 0L) samples$lambda[, decision_indices[[offset]]] else numeric(0)
  }
  temporary <- paste0(sample_path, ".tmp")
  write.csv(values, temporary, row.names = FALSE, quote = TRUE)
  if (file.exists(sample_path) && sha256_file(sample_path) != sha256_file(temporary)) {
    unlink(temporary)
    stop("refusing to overwrite different stochastic sample sidecar")
  }
  if (file.exists(sample_path)) {
    unlink(temporary)
  } else if (!file.rename(temporary, sample_path)) {
    stop("atomic stochastic sample rename failed")
  }
  sidecar <- list(
    path = file.path("execution", "results", basename(sample_dir), basename(sample_path)),
    rows = nrow(values),
    sha256 = sha256_file(sample_path),
    decision_indices = decision_indices,
    decision_times = times[decision_indices]
  )
}

censored_below_first <- !identical(cell$explorer, "boundary_constructor") && accepted < min(prefixes)
h2_event <- NULL
if (identical(cell$explorer, "crabs_rejection")) {
  if (censored_below_first) {
    h2_event <- TRUE
  } else {
    h2_event <- prefix_summaries[[as.character(largest_prefix)]]$normalized_deficit > 0.05
  }
}

h3_pass <- NULL
if (identical(cell$explorer, "boundary_constructor")) {
  width <- exact$discrete_upper - exact$discrete_lower
  nonzero <- width > 1e-12 * pmax(1, abs(exact$discrete_lower), abs(exact$discrete_upper))
  indices <- decision_indices[nonzero[decision_indices]]
  lower_deficit <- pmax(0, samples$lambda[1L, indices] - exact$discrete_lower[indices]) / width[indices]
  upper_deficit <- pmax(0, exact$discrete_upper[indices] - samples$lambda[2L, indices]) / width[indices]
  h3_pass <- max(c(lower_deficit, upper_deficit), 0) <= 1e-10 &&
    recurrence_max <= 1e-10 * max(1, max(abs(pdelta)))
}

integrity_pass <- accepted >= 0L && accepted <= target && samples$attempts <= attempt_ceiling &&
  (is.na(recurrence_max) || recurrence_max <= 1e-10 * max(1, max(abs(pdelta)))) &&
  (is.na(cap_excess) || cap_excess <= 1e-12) &&
  (is.null(h3_pass) || h3_pass) &&
  (is.null(structural_censor) || structural_censor$required_minimum_lambda > structural_censor$frozen_max_lambda + 1e-12)

result <- list(
  schema_version = "1.0.0",
  status = if (!integrity_pass) "FAIL" else if (!is.null(structural_censor)) "CENSORED_STRUCTURAL_NONTERMINATION" else "PASS",
  layer = "stochastic",
  cell = cell,
  bindings = bindings,
  input = list(
    signal_grid_sha256 = input$sha256,
    time = times,
    lambda_p = lambda_p,
    p_delta = pdelta
  ),
  exact_endpoints = exact,
  sampling = list(
    requested = if (identical(cell$explorer, "boundary_constructor")) 2L else target,
    accepted = accepted,
    attempts = samples$attempts,
    rejected = samples$rejected,
    acceptance_rate = if (samples$attempts > 0L) accepted / samples$attempts else NA_real_,
    proposal_ceiling_hit = samples$attempts >= attempt_ceiling && accepted < target,
    elapsed_seconds = elapsed,
    post_cell_rng_sha256 = digest::digest(.Random.seed, algo = "sha256"),
    maximum_recurrence_residual = recurrence_max,
    maximum_turnover_cap_excess = cap_excess,
    attained_prefixes = prefixes[prefixes <= accepted],
    largest_attained_prefix = largest_prefix,
    censored_below_first_prefix = censored_below_first,
    prefix_summaries = prefix_summaries,
    decision_value_sidecar = sidecar
  ),
  structural_censor = structural_censor,
  confirmatory_metrics = list(
    H2_deficit_event = h2_event,
    H3_boundary_pass = h3_pass,
    H4_queries = queries,
    H4_changed_query_count = query_changed,
    H4_false_certificate_count = false_certificates
  ),
  integrity_pass = integrity_pass,
  public_release_authorized = FALSE
)

temporary_result <- paste0(result_path, ".tmp")
jsonlite::write_json(result, temporary_result, pretty = FALSE, auto_unbox = TRUE, digits = 17, null = "null", na = "string")
cat("\n", file = temporary_result, append = TRUE)
if (file.exists(result_path)) {
  unlink(temporary_result)
  stop("stochastic result appeared concurrently")
}
if (!file.rename(temporary_result, result_path)) stop("atomic stochastic result rename failed")

cat(jsonlite::toJSON(list(
  cell_id = cell_id,
  status = result$status,
  explorer = cell$explorer,
  accepted = accepted,
  attempts = samples$attempts,
  existing = FALSE
), auto_unbox = TRUE), "\n")
