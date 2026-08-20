# Emit a schema-bound CRABS/affine request without silently converting p.delta
# to pulled speciation. This adapter is scoped to the frozen confirmatory bridge:
# rho=1, reference lambda=lambda_p, and reference mu=0.

canonical_vector_json <- function(values) {
  # jsonlite digits=15 matches the shortest decimal values transmitted by the
  # adapter and re-serialized by Python's canonical JSON encoder.
  paste0(jsonlite::toJSON(as.numeric(values), auto_unbox = FALSE, digits = 15, pretty = FALSE), "\n")
}

vector_sha256 <- function(values) {
  digest::digest(canonical_vector_json(values), algo = "sha256", serialize = FALSE)
}

require_condition <- function(condition, message) {
  if (!isTRUE(condition)) stop(message, call. = FALSE)
}

crabs_affine_contract <- function(
  model,
  lambda_p,
  sampling_ledger,
  rho = 1,
  crabs_version = "1.2.0.9001",
  crabs_commit = "f2af9b6c8bb93f5512c2882d2e816060c9e07728"
) {
  require_condition(inherits(model, "CRABS"), "model must inherit from CRABS")
  times <- as.numeric(model$times)
  lambda_p <- as.numeric(lambda_p)
  require_condition(length(times) >= 2L, "CRABS time grid must contain at least two knots")
  require_condition(length(lambda_p) == length(times), "lambda_p length must match model times")
  require_condition(all(is.finite(times)) && all(is.finite(lambda_p)), "time and lambda_p must be finite")
  require_condition(all(diff(times) > 0), "time grid must be strictly increasing")
  tolerance <- 64 * .Machine$double.eps * max(1, max(abs(diff(times))))
  require_condition(max(diff(times)) - min(diff(times)) <= tolerance, "CRABS confirmatory grid must be equally spaced")
  require_condition(all(lambda_p >= 0), "lambda_p must be non-negative")
  require_condition(is.finite(rho) && rho == 1, "frozen CRABS matching requires rho=1")
  require_condition(is.function(model$lambda) && is.function(model$mu) && is.function(model$p.delta), "CRABS model lacks required rate functions")

  reference_lambda <- as.numeric(model$lambda(times))
  reference_mu <- as.numeric(model$mu(times))
  pdelta <- as.numeric(model$p.delta(times))
  require_condition(length(reference_lambda) == length(times), "reference lambda length mismatch")
  require_condition(length(reference_mu) == length(times), "reference mu length mismatch")
  require_condition(length(pdelta) == length(times), "p.delta length mismatch")
  require_condition(all(is.finite(reference_lambda)) && all(is.finite(reference_mu)) && all(is.finite(pdelta)), "CRABS rates must be finite")
  bridge_error <- max(abs(reference_lambda - lambda_p))
  bridge_scale <- max(1, abs(reference_lambda), abs(lambda_p))
  require_condition(bridge_error <= 5e-12 * bridge_scale, "reference lambda does not equal supplied lambda_p")
  require_condition(all(reference_mu == 0), "reference mu must be exactly zero for the frozen bridge")

  required_counts <- c("requested_samples", "returned_models", "attempts", "accepted", "rejected")
  require_condition(all(required_counts %in% names(sampling_ledger)), "sampling ledger is incomplete")
  counts <- lapply(sampling_ledger[required_counts], as.integer)
  require_condition(all(vapply(counts, function(x) length(x) == 1L && !is.na(x) && x >= 0L, logical(1))), "sampling counts must be non-negative integers")
  require_condition(counts$returned_models == counts$requested_samples + 1L, "retained-reference count mismatch")
  require_condition(counts$attempts == counts$accepted + counts$rejected, "proposal accounting mismatch")
  require_condition(counts$accepted == counts$requested_samples, "accepted/requested mismatch")

  list(
    schema_version = "1.0.0",
    mode = "verify_both",
    time_grid = times,
    equal_grid_declared = TRUE,
    interpolation = "piecewise_linear",
    units = list(time = "myr", rate = "per_myr"),
    rho = 1,
    pulled_speciation = list(values = lambda_p, sha256 = vector_sha256(lambda_p)),
    pulled_net_diversification = list(values = pdelta, sha256 = vector_sha256(pdelta)),
    reference_model = list(lambda = reference_lambda, mu = reference_mu),
    crabs = list(version = crabs_version, commit = crabs_commit),
    sampling_ledger = counts
  )
}

write_crabs_affine_contract <- function(record, path) {
  jsonlite::write_json(record, path, auto_unbox = TRUE, digits = 15, pretty = TRUE)
  invisible(path)
}

if (sys.nframe() == 0L) {
  if (!requireNamespace("jsonlite", quietly = TRUE) || !requireNamespace("digest", quietly = TRUE)) {
    stop("jsonlite and digest are required", call. = FALSE)
  }
  args <- commandArgs(trailingOnly = TRUE)
  require_condition(length(args) == 1L, "usage: Rscript adoption/crabs_affine_contract.R output.json")
  times <- c(0, 1, 2)
  lp <- c(0.2, 0.2, 0.2)
  fixture <- list(
    times = times,
    lambda = function(t) rep(0.2, length(t)),
    mu = function(t) rep(0, length(t)),
    p.delta = function(t) rep(0.2, length(t))
  )
  class(fixture) <- "CRABS"
  ledger <- list(requested_samples = 100, returned_models = 101, attempts = 125, accepted = 100, rejected = 25)
  record <- crabs_affine_contract(fixture, lp, ledger)
  write_crabs_affine_contract(record, args[[1L]])
  cat(sprintf("Wrote validated CRABS/affine contract fixture to %s\n", args[[1L]]))
}
