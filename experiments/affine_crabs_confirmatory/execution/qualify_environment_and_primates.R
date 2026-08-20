#!/usr/bin/env Rscript

options(stringsAsFactors = FALSE, warn = 1, digits = 17)

suppressPackageStartupMessages({
  library(CRABS)
  library(digest)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 3L) {
  stop("usage: qualify_environment_and_primates.R CRABS_SOURCE_REPO PROJECT_ROOT OUTPUT_DIR")
}

crabs_source <- normalizePath(args[[1]], mustWork = TRUE)
project_root <- normalizePath(args[[2]], mustWork = TRUE)
output_dir <- normalizePath(args[[3]], mustWork = FALSE)
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

expected_commit <- "f2af9b6c8bb93f5512c2882d2e816060c9e07728"
expected_version <- "1.2.0.9001"
expected_input_hash <- "4bb7585641b3788e22e7b0859e967957c200cc497efe94495cbc7206d8a4dfc6"
amendment_path <- file.path(
  project_root, "experiments", "affine_crabs_confirmatory", "AMENDMENT_001_PRE_EXECUTION.json"
)
correction_path <- file.path(
  project_root, "experiments", "affine_crabs_confirmatory", "AMENDMENT_002_COMMIT_CORRECTION.json"
)

sha256_file <- function(path) {
  digest::digest(file = path, algo = "sha256", serialize = FALSE)
}

write_json_atomic <- function(value, path) {
  tmp <- paste0(path, ".tmp")
  jsonlite::write_json(value, tmp, pretty = TRUE, auto_unbox = TRUE, digits = 17, null = "null")
  if (file.exists(path) && sha256_file(path) != sha256_file(tmp)) {
    unlink(tmp)
    stop(sprintf("refusing to overwrite a different qualification artifact: %s", path))
  }
  if (file.exists(path)) unlink(tmp) else if (!file.rename(tmp, path)) stop("atomic JSON rename failed")
}

write_csv_atomic <- function(value, path) {
  tmp <- paste0(path, ".tmp")
  write.csv(value, tmp, row.names = FALSE, quote = TRUE)
  if (file.exists(path) && sha256_file(path) != sha256_file(tmp)) {
    unlink(tmp)
    stop(sprintf("refusing to overwrite a different qualification artifact: %s", path))
  }
  if (file.exists(path)) unlink(tmp) else if (!file.rename(tmp, path)) stop("atomic CSV rename failed")
}

git_value <- function(...) {
  out <- system2("git", c("-C", crabs_source, ...), stdout = TRUE, stderr = TRUE)
  status <- attr(out, "status")
  if (!is.null(status) && status != 0L) stop(paste(out, collapse = "\n"))
  trimws(paste(out, collapse = "\n"))
}

source_commit <- git_value("rev-parse", "HEAD")
source_status <- git_value("status", "--porcelain")
source_input <- file.path(crabs_source, "data", "primates_ebd.rda")
source_input_hash <- sha256_file(source_input)
installed_version <- as.character(packageVersion("CRABS"))

gate_checks <- list(
  crabs_commit_exact = identical(source_commit, expected_commit),
  crabs_source_clean = identical(source_status, ""),
  crabs_version_exact = identical(installed_version, expected_version),
  primates_source_hash_exact = identical(source_input_hash, expected_input_hash),
  amendment_present = file.exists(amendment_path),
  correction_present = file.exists(correction_path)
)
if (!all(unlist(gate_checks, use.names = FALSE))) {
  stop(paste("qualification gate failed:", jsonlite::toJSON(gate_checks, auto_unbox = TRUE)))
}

data_env <- new.env(parent = emptyenv())
data("primates_ebd", package = "CRABS", envir = data_env)
primates <- data_env$primates_ebd
shape_checks <- list(
  rows_exact = nrow(primates) == 100L,
  columns_exact = identical(names(primates), c("lambda", "mu", "time")),
  finite = all(is.finite(as.matrix(primates))),
  time_starts_zero = identical(as.numeric(primates$time[[1]]), 0),
  time_strictly_increasing = all(diff(primates$time) > 0),
  lambda_positive = all(primates$lambda > 0),
  mu_nonnegative = all(primates$mu >= 0)
)
if (!all(unlist(shape_checks, use.names = FALSE))) {
  stop(paste("primates shape gate failed:", jsonlite::toJSON(shape_checks, auto_unbox = TRUE)))
}

times <- as.numeric(primates$time)
lambda <- as.numeric(primates$lambda)
mu <- as.numeric(primates$mu)
lambda_fun <- approxfun(times, lambda, method = "linear", rule = 2)
mu_fun <- approxfun(times, mu, method = "linear", rule = 2)
reference_model <- CRABS::create.model(lambda_fun, mu_fun, times = times)
model_table <- CRABS::model2df(reference_model, gather = FALSE, rho = 1)

native <- data.frame(
  time = times,
  lambda = lambda,
  mu = mu,
  p_delta = as.numeric(reference_model$p.delta(times)),
  lambda_p = as.numeric(model_table[["Pulled speciation"]])
)
derived_checks <- list(
  rows_preserved = nrow(native) == 100L,
  finite = all(is.finite(as.matrix(native))),
  lambda_p_nonnegative = all(native$lambda_p >= 0),
  p_delta_model2df_agreement = max(abs(
    native$p_delta - as.numeric(model_table[["Pulled net-diversification"]])
  )) <= 1e-12 * max(1, max(abs(native$p_delta)))
)
if (!all(unlist(derived_checks, use.names = FALSE))) {
  stop(paste("derived primates gate failed:", jsonlite::toJSON(derived_checks, auto_unbox = TRUE)))
}

native_path <- file.path(output_dir, "crabs_primates_ebd_native.csv")
write_csv_atomic(native, native_path)

grid_receipts <- list()
for (knots in c(25L, 100L, 400L)) {
  grid_time <- seq(min(times), max(times), length.out = knots)
  grid <- data.frame(
    time = grid_time,
    lambda_p = approx(times, native$lambda_p, xout = grid_time, method = "linear", rule = 2)$y,
    p_delta = approx(times, native$p_delta, xout = grid_time, method = "linear", rule = 2)$y
  )
  grid_path <- file.path(output_dir, sprintf("crabs_primates_ebd_%03d.csv", knots))
  write_csv_atomic(grid, grid_path)
  grid_receipts[[as.character(knots)]] <- list(
    path = file.path("execution", "qualification", basename(grid_path)),
    rows = nrow(grid),
    sha256 = sha256_file(grid_path),
    domain = c(min(grid$time), max(grid$time)),
    equally_spaced = max(abs(diff(grid$time) - diff(grid$time)[[1]])) <=
      1e-12 * max(1, abs(diff(grid$time)[[1]]))
  )
}

imports <- unique(c("CRABS", unlist(strsplit(packageDescription("CRABS")$Imports, "[,\\n]"))))
imports <- trimws(sub("\\s*\\(.*$", "", imports))
imports <- imports[nzchar(imports)]
installed <- installed.packages()
missing_imports <- setdiff(imports, rownames(installed))
if (length(missing_imports) > 0L) stop(paste("missing CRABS imports:", paste(missing_imports, collapse = ", ")))
package_lock <- list(
  schema_version = "1.0.0",
  r_version = R.version.string,
  platform = R.version$platform,
  library_paths = .libPaths(),
  packages = unname(lapply(sort(imports), function(package) list(
    package = package,
    version = as.character(packageVersion(package)),
    library = normalizePath(find.package(package))
  )))
)
lock_path <- file.path(output_dir, "R_PACKAGE_LOCK.json")
write_json_atomic(package_lock, lock_path)

session_path <- file.path(output_dir, "R_SESSION_INFO.txt")
session_lines <- capture.output(sessionInfo())
tmp_session <- paste0(session_path, ".tmp")
writeLines(session_lines, tmp_session, useBytes = TRUE)
if (file.exists(session_path) && sha256_file(session_path) != sha256_file(tmp_session)) {
  unlink(tmp_session)
  stop("refusing to overwrite different R_SESSION_INFO.txt")
}
if (file.exists(session_path)) {
  unlink(tmp_session)
} else if (!file.rename(tmp_session, session_path)) {
  stop("atomic session-info rename failed")
}

receipt <- list(
  schema_version = "1.0.0",
  status = "QUALIFIED_ELIGIBLE",
  confirmatory_outcomes_generated = FALSE,
  amendment_sha256 = sha256_file(amendment_path),
  correction_sha256 = sha256_file(correction_path),
  crabs = list(
    source_commit = source_commit,
    source_clean = identical(source_status, ""),
    installed_version = installed_version,
    installed_library = normalizePath(find.package("CRABS")),
    licence = packageDescription("CRABS")$License
  ),
  source = list(
    upstream_object = "CRABS::primates_ebd",
    upstream_path = "data/primates_ebd.rda",
    sha256 = source_input_hash,
    component_licence = "GPL-3",
    attribution_required_for_public_redistribution = TRUE
  ),
  checks = c(gate_checks, shape_checks, derived_checks),
  native_extract = list(
    path = file.path("execution", "qualification", basename(native_path)),
    rows = nrow(native),
    columns = names(native),
    sha256 = sha256_file(native_path),
    time_domain = c(min(times), max(times))
  ),
  resampled_grids = grid_receipts,
  package_lock_sha256 = sha256_file(lock_path),
  session_info_sha256 = sha256_file(session_path),
  public_release_authorized = FALSE
)
receipt_path <- file.path(output_dir, "PRIMATES_QUALIFICATION_RECEIPT.json")
write_json_atomic(receipt, receipt_path)

cat(jsonlite::toJSON(receipt, pretty = TRUE, auto_unbox = TRUE, digits = 17), "\n")
