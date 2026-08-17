# Exact conditional pointwise speciation bounds for a pulled-speciation signal.
# Scope: piecewise-linear lambda_p on a strictly increasing time grid,
# 0 < rho <= 1, and 0 <= turnover_cap <= 1.
# Units are inherited from the input: if time is Ma and lambda_p is lineages/Ma,
# the returned rates are lineages/Ma.


affine_speciation_bounds <- function(time, lambda_p, rho = 1, turnover_cap = 0.5) {
  time <- as.numeric(time)
  lambda_p <- as.numeric(lambda_p)

  if (length(time) != length(lambda_p) || length(time) < 2L) {
    stop("time and lambda_p must have the same length >= 2")
  }
  if (any(!is.finite(time)) || any(!is.finite(lambda_p))) {
    stop("time and lambda_p must be finite")
  }
  if (any(diff(time) <= 0)) stop("time must be strictly increasing")
  if (any(lambda_p <= 0)) stop("lambda_p must be strictly positive")
  if (!is.finite(rho) || rho <= 0 || rho > 1) stop("rho must lie in (0, 1]")
  if (!is.finite(turnover_cap) || turnover_cap < 0 || turnover_cap > 1) {
    stop("this adapter is scoped to turnover_cap in [0, 1]")
  }

  dt <- diff(time)
  integral <- c(0, cumsum(0.5 * (lambda_p[-length(lambda_p)] + lambda_p[-1L]) * dt))
  F <- exp(integral)

  lower_denom <- rho + F - 1
  upper_denom <- rho + (1 - turnover_cap) * (F - 1)

  out <- data.frame(
    time = time,
    lambda_p = lambda_p,
    pulled_scale_F = F,
    lambda_lower = lambda_p * F / lower_denom,
    lambda_upper = lambda_p * F / upper_denom,
    rho = rho,
    turnover_cap = turnover_cap,
    check.names = FALSE
  )

  if (any(!is.finite(out$lambda_lower)) || any(!is.finite(out$lambda_upper))) {
    stop("non-finite bound generated; inspect signal scale and inputs")
  }
  if (any(out$lambda_lower > out$lambda_upper + 1e-13)) {
    stop("internal ordering check failed")
  }
  out
}


# Command-line use:
#   Rscript affine_bounds_adapter.R input.csv output.csv [rho] [turnover_cap]
# The input must contain columns named `time` and `lambda_p`.
# With no arguments, the script runs the released Mammalia replay check.
if (sys.nframe() == 0L) {
  args <- commandArgs(trailingOnly = TRUE)

  if (length(args) == 0L) {
    mammalia_time <- seq(0, 70, by = 5)
    mammalia_lambda_p <- c(
      0.213458252223705, 0.16805839744963, 0.136208371201428,
      0.110503855522888, 0.08836274336085501, 0.06930816385153329,
      0.0540393543691787, 0.0554138491764691, 0.034830604992764,
      0.0640666088715508, 0.0446952562044947, 0.0184350320496953,
      0.0693268651425006, 0.0748328802215691, 0.0778740782069533
    )
    replay <- affine_speciation_bounds(
      mammalia_time,
      mammalia_lambda_p,
      rho = 1,
      turnover_cap = 0.5
    )
    stopifnot(
      abs(tail(replay$lambda_lower, 1) - 0.0778740782069533) < 1e-12,
      abs(tail(replay$lambda_upper, 1) - 0.155212330887834) < 1e-12
    )
    cat("Mammalia replay passed. Endpoint at tau=70 Ma:\n")
    print(tail(replay, 1), row.names = FALSE)
  } else {
    if (length(args) < 2L || length(args) > 4L) {
      stop("usage: Rscript affine_bounds_adapter.R input.csv output.csv [rho] [turnover_cap]")
    }
    input_path <- args[[1L]]
    output_path <- args[[2L]]
    rho <- if (length(args) >= 3L) as.numeric(args[[3L]]) else 1
    turnover_cap <- if (length(args) >= 4L) as.numeric(args[[4L]]) else 0.5

    input <- read.csv(input_path, check.names = FALSE)
    required <- c("time", "lambda_p")
    if (!all(required %in% names(input))) {
      stop("input CSV must contain columns: time, lambda_p")
    }
    bounds <- affine_speciation_bounds(input$time, input$lambda_p, rho, turnover_cap)
    write.csv(bounds, output_path, row.names = FALSE)
    cat(sprintf("Wrote %d endpoint rows to %s\n", nrow(bounds), output_path))
  }
}
