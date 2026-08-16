# Corrected R implementation of the EM1415 Tourism Forecasting project
#
# Important audit correction: columns contain leading NA values and therefore
# have different observed lengths. Each series is split independently so that
# the last four observed values form the validation sample.

mape <- function(actual, forecast) {
  keep <- is.finite(actual) & is.finite(forecast) & actual != 0
  if (!any(keep)) return(NA_real_)
  mean(abs((actual[keep] - forecast[keep]) / actual[keep])) * 100
}

mase <- function(actual, forecast, training) {
  scale <- mean(abs(diff(training)), na.rm = TRUE)
  if (!is.finite(scale) || scale <= 0) return(NA_real_)
  mean(abs(actual - forecast), na.rm = TRUE) / scale
}

split_observed_series <- function(x, h = 4) {
  y <- as.numeric(na.omit(x))
  if (length(y) <= h) stop("Series is too short for the requested validation horizon")
  list(
    train = y[1:(length(y) - h)],
    validation = y[(length(y) - h + 1):length(y)]
  )
}

forecast_one_series <- function(x) {
  parts <- split_observed_series(x, h = 4)
  train <- parts$train
  validation <- parts$validation
  h <- 1:4

  naive <- rep(tail(train, 1), 4)
  growth_naive <- tail(train, 1) * (1.055 ^ h)

  time <- seq_along(train)
  fit <- lm(train ~ time)
  linear_trend <- predict(
    fit,
    newdata = data.frame(time = (length(train) + 1):(length(train) + 4))
  )

  train_actual <- train[-1]
  train_naive <- train[-length(train)]

  data.frame(
    method = c("naive", "growth_naive", "linear_trend"),
    training_mape = c(mape(train_actual, train_naive), NA, NA),
    training_mase = c(mase(train_actual, train_naive, train), NA, NA),
    validation_mape = c(
      mape(validation, naive),
      mape(validation, growth_naive),
      mape(validation, linear_trend)
    ),
    validation_mase = c(
      mase(validation, naive, train),
      mase(validation, growth_naive, train),
      mase(validation, linear_trend, train)
    )
  )
}

# Usage:
# tourism_data <- read.csv("data/tourism_data.csv", check.names = FALSE)
# all_results <- lapply(tourism_data, forecast_one_series)
# results <- do.call(rbind, all_results)
# aggregate(cbind(validation_mape, validation_mase) ~ method,
#           data = results, FUN = mean, na.rm = TRUE)
