"""Audit and complete the EM1415 Tourism Forecasting coursework.

The source CSV stores 518 annual series in columns with leading missing values,
so each series is split independently: its final four *observed* values form the
validation period.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def observed_split(series: pd.Series, validation_years: int = 4):
    y = pd.to_numeric(series, errors="coerce").dropna().to_numpy(dtype=float)
    if len(y) <= validation_years:
        raise ValueError("A series must have more observations than the validation horizon.")
    return y[:-validation_years], y[-validation_years:]


def mape(actual, forecast) -> float:
    actual = np.asarray(actual, dtype=float)
    forecast = np.asarray(forecast, dtype=float)
    mask = np.isfinite(actual) & np.isfinite(forecast) & (actual != 0)
    if not mask.any():
        return np.nan
    return float(np.mean(np.abs((actual[mask] - forecast[mask]) / actual[mask])) * 100)


def mase(actual, forecast, training) -> float:
    actual = np.asarray(actual, dtype=float)
    forecast = np.asarray(forecast, dtype=float)
    training = np.asarray(training, dtype=float)
    scale = np.mean(np.abs(np.diff(training)))
    if not np.isfinite(scale) or scale <= 0:
        return np.nan
    return float(np.mean(np.abs(actual - forecast)) / scale)


def forecasts(training: np.ndarray) -> dict[str, np.ndarray]:
    horizon = np.arange(1, 5)
    naive = np.repeat(training[-1], 4)
    growth = training[-1] * (1.055 ** horizon)

    time = np.arange(1, len(training) + 1)
    slope, intercept = np.polyfit(time, training, 1)
    linear = intercept + slope * np.arange(len(training) + 1, len(training) + 5)

    return {
        "naive": naive,
        "growth_naive": growth,
        "linear_trend": linear,
    }


def run(data_path: str | Path):
    data = pd.read_csv(data_path)
    method_rows = []
    horizon_rows = []
    first_five = []

    for position, column in enumerate(data.columns):
        train, validation = observed_split(data[column])

        # Genuine one-step in-sample naive forecast.
        train_actual = train[1:]
        train_naive = train[:-1]
        train_mape = mape(train_actual, train_naive)
        train_mase = mase(train_actual, train_naive, train)

        candidate_forecasts = forecasts(train)
        for method, prediction in candidate_forecasts.items():
            method_rows.append(
                {
                    "series": column,
                    "method": method,
                    "training_mape": train_mape if method == "naive" else np.nan,
                    "training_mase": train_mase if method == "naive" else np.nan,
                    "validation_mape": mape(validation, prediction),
                    "validation_mase": mase(validation, prediction, train),
                    "validation_mae": float(np.mean(np.abs(validation - prediction))),
                    "validation_rmse": float(
                        np.sqrt(np.mean((validation - prediction) ** 2))
                    ),
                }
            )

        naive = candidate_forecasts["naive"]
        scale = np.mean(np.abs(np.diff(train)))
        for h in range(4):
            horizon_rows.append(
                {
                    "series": column,
                    "horizon": h + 1,
                    "mape": mape([validation[h]], [naive[h]]),
                    "mase": float(abs(validation[h] - naive[h]) / scale)
                    if scale > 0
                    else np.nan,
                }
            )

        if position < 5:
            linear = candidate_forecasts["linear_trend"]
            for h in range(4):
                first_five.append(
                    {
                        "series": column,
                        "horizon": h + 1,
                        "actual": validation[h],
                        "forecast": linear[h],
                        "error_actual_minus_forecast": validation[h] - linear[h],
                    }
                )

    methods = pd.DataFrame(method_rows)
    horizons = pd.DataFrame(horizon_rows)
    first_five = pd.DataFrame(first_five)

    model_summary = (
        methods.groupby("method", sort=False)
        .agg(
            validation_mape=("validation_mape", "mean"),
            validation_mase=("validation_mase", "mean"),
            validation_mae=("validation_mae", "mean"),
            validation_rmse=("validation_rmse", "mean"),
        )
        .reset_index()
    )

    naive = methods.loc[methods["method"] == "naive"]
    train_validation = pd.DataFrame(
        [
            {
                "training_mape_mean": naive["training_mape"].mean(),
                "training_mase_mean": naive["training_mase"].mean(),
                "validation_mape_mean": naive["validation_mape"].mean(),
                "validation_mase_mean": naive["validation_mase"].mean(),
                "train_validation_mape_correlation": naive[
                    ["training_mape", "validation_mape"]
                ].corr().iloc[0, 1],
            }
        ]
    )

    horizon_summary = (
        horizons.groupby("horizon")
        .agg(mape=("mape", "mean"), mase=("mase", "mean"))
        .reset_index()
    )

    audit = {
        "n_series": data.shape[1],
        "matrix_rows": data.shape[0],
        "missing_cells": int(data.isna().sum().sum()),
        "minimum_observed_length": int(data.notna().sum().min()),
        "maximum_observed_length": int(data.notna().sum().max()),
        "mean_observed_length": float(data.notna().sum().mean()),
    }

    return audit, model_summary, train_validation, horizon_summary, first_five


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/tourism_data.csv")
    parser.add_argument("--output-dir", default="results/generated")
    args = parser.parse_args()

    audit, models, train_validation, horizons, first_five = run(args.data)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    models.to_csv(output / "model_comparison.csv", index=False)
    train_validation.to_csv(output / "naive_train_validation_summary.csv", index=False)
    horizons.to_csv(output / "horizon_metrics.csv", index=False)
    first_five.to_csv(output / "first5_linear_trend_forecasts.csv", index=False)

    print(audit)
    print(models.to_string(index=False))
    print(train_validation.to_string(index=False))
    print(horizons.to_string(index=False))


if __name__ == "__main__":
    main()
