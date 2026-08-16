# Tourism Demand Forecasting — 518 Annual Time Series

An audited reconstruction of my MSc **Predictive Business and Finance (EM1415)** coursework on annual tourism-demand forecasting.

---

## Key results

Across **518 heterogeneous annual tourism series**, the **5.5% growth-adjusted naive forecast** achieved the lowest average validation error among the three benchmark rules:

- **5.5% growth-adjusted naive:** 20.52% MAPE
- **Flat naive:** 20.87% MAPE
- **Linear trend:** 29.98% MAPE

![Validation MAPE by forecasting method](figures/model_comparison.svg)

Forecast accuracy also deteriorates substantially with the prediction horizon. For the flat naive forecast, MAPE rises from **12.75% at one year** to **28.66% at four years**.

![Forecast error by horizon](figures/horizon_error.svg)

**Interpretation.** A more flexible extrapolation rule is not automatically better. In this reconstruction, a modest fixed-growth adjustment slightly improves scale-free forecast accuracy, while the fitted linear trend performs substantially worse on average. In-sample MAPE and validation MAPE correlate only **0.427**, reinforcing the importance of genuine out-of-sample evaluation.

---

## Research question

How well do simple forecasting rules generalize across a large collection of heterogeneous annual tourism-demand series, and how does forecast error evolve as the prediction horizon increases?

The recovered coursework dataset contains **518 annual time series** stored in a 43-row matrix. The series have different numbers of observed values because of leading missing observations: observed lengths range from **7 to 43 years**, with a mean of **20.47 years**.

A key audit finding was therefore that a single global 39-row training / 4-row validation split was inappropriate. The reconstruction instead reserves the **last four observed values of each individual series** for validation.

---

## Data audit

| Feature | Value |
|---|---:|
| Number of annual series | **518** |
| Matrix rows | **43** |
| Missing cells | **11,668** |
| Shortest observed series | **7 years** |
| Longest observed series | **43 years** |
| Mean observed length | **20.47 years** |
| Validation horizon | **4 years per series** |

Because the series differ strongly in level and scale, raw MAE and RMSE are not ideal as the primary metrics for averaging performance across all 518 series. The main comparison therefore emphasizes **MAPE** and **MASE**.

---

# Mathematical forecasting framework

For each annual series:

- `y_t` denotes the observed value in year `t`;
- `T` is the final year in the training sample;
- `h` is the forecast horizon;
- `H = 4` is the validation horizon;
- the forecast for year `T + h` is denoted by the fitted value shown in the equations below.

The equations are displayed as vector graphics so that mathematical notation renders consistently on GitHub.

## 1. Mean Absolute Percentage Error (MAPE)

<p align="center">
  <img src="figures/mape_formula.svg" width="760" alt="MAPE formula">
</p>

MAPE measures the average absolute percentage forecast error over the four validation horizons. It is scale-free and easy to interpret as a percentage, although it can become unstable when observed values are close to zero.

## 2. Mean Absolute Scaled Error (MASE)

MASE first scales forecast errors by the average one-step naive error observed in the training sample.

<p align="center">
  <img src="figures/mase_scale_formula.svg" width="700" alt="MASE scaling term">
</p>

The scaled forecast-error measure is then:

<p align="center">
  <img src="figures/mase_formula.svg" width="760" alt="MASE formula">
</p>

A MASE below 1 means that forecast errors are, on average, smaller than the in-sample one-step naive benchmark scale. A value above 1 means that the forecast errors are larger relative to that benchmark.

---

# Forecasting models

## Model 1 — Flat naive forecast

The flat naive forecast uses the **last observed training value for every future horizon**.

<p align="center">
  <img src="figures/naive_forecast_formula.svg" width="720" alt="Flat naive forecast formula">
</p>

This is the simplest benchmark and imposes no trend.

## Model 2 — 5.5% growth-adjusted naive forecast

The second rule starts from the final observed training value and compounds it by **5.5% per year**.

<p align="center">
  <img src="figures/growth_forecast_formula.svg" width="760" alt="Growth-adjusted naive forecast formula">
</p>

The exponent is the forecast horizon `h`. This matters: using `h − 1` would imply **no growth at the one-year-ahead forecast**, which was one of the issues identified in the original coursework workflow.

## Model 3 — Linear-trend forecast

For each series separately, the training observations are represented by a linear time-trend model:

<p align="center">
  <img src="figures/trend_model_formula.svg" width="700" alt="Linear trend model formula">
</p>

Here:

- `α` is the intercept;
- `β` is the estimated annual trend;
- `ε_t` is the model disturbance.

After estimating the intercept and slope by ordinary least squares, the future forecast is obtained by evaluating the fitted line at the future time point `T + h`:

<p align="center">
  <img src="figures/trend_forecast_formula.svg" width="700" alt="Linear trend forecast formula">
</p>

This model allows every series to have its own estimated trend, but linear extrapolation can be fragile when a series is short, volatile, or affected by structural change.

---

# Validation results

## Overall model comparison

| Forecasting method | Validation MAPE | Validation MASE |
|---|---:|---:|
| Flat naive | **20.87%** | **3.37** |
| **5.5% growth-adjusted naive** | **20.52%** | **2.87** |
| Linear trend | **29.98%** | **3.74** |

The growth-adjusted naive rule performs best on average under both MAPE and MASE in this reconstruction.

The difference between the two naive-style methods is modest, but the linear-trend forecast performs substantially worse. This illustrates an important forecasting principle: additional model flexibility does not necessarily improve out-of-sample accuracy.

---

## Flat-naive performance by horizon

| Forecast horizon | MAPE | MASE |
|---:|---:|---:|
| 1 year | **12.75%** | **1.59** |
| 2 years | **19.60%** | **3.05** |
| 3 years | **22.46%** | **3.89** |
| 4 years | **28.66%** | **4.94** |

The deterioration with horizon is pronounced. A constant-last-value forecast becomes increasingly inaccurate when it is extended several years into time series that often exhibit trend or structural movement.

---

## Training versus validation performance

For the one-step training benchmark, each observation from the second training year onward is forecast using the immediately preceding observation. This is a genuine one-step-ahead naive forecast, rather than comparing repeated copies of the final training value with themselves.

The resulting average metrics across the 518 series are:

| Metric | Mean across series |
|---|---:|
| Training MAPE | **15.87%** |
| Training MASE | **1.00** |
| Validation MAPE | **20.87%** |
| Validation MASE | **3.37** |

Training MASE equals 1 by construction for this one-step naive benchmark.

The original coursework workflow incorrectly produced zero training MAPE because it compared repeated copies of the final training observation with themselves instead of constructing genuine one-step-ahead in-sample forecasts.

The correlation between training MAPE and validation MAPE across the 518 series is only **0.427**. In-sample forecastability therefore provides only a partial indication of out-of-sample performance.

---

# Methodological audit

The portfolio reconstruction corrected several issues in the original coursework workflow.

## 1. Series-specific train/validation splitting

The 518 columns do not have a common observed starting year. Each series is therefore cleaned separately before its final four observed values are reserved for validation.

## 2. Correct naive training errors

Training errors are constructed from genuine one-step forecasts rather than repeated values of the last training observation.

## 3. Correct growth exponent

The 5.5% growth-adjusted forecast compounds the final training value once for a one-year-ahead forecast, twice for a two-year-ahead forecast, and so on. The horizon exponent is therefore `h`, not `h − 1`.

## 4. Scale-free evaluation

MAPE and MASE are emphasized because the tourism-demand series differ greatly in magnitude.

## 5. Out-of-sample comparison

The model comparison is based on the held-out final four observations of each series rather than in-sample fit.

---

# Further forecasting considerations

## Polynomial-order selection

Selecting first- through fifth-order polynomial trends using the same validation set would introduce selection overfitting. A stronger design would use rolling-origin time-series cross-validation inside the training period and reserve a final untouched test horizon.

## Exponential-smoothing alternatives

Depending on the series structure, reasonable extensions include:

- simple exponential smoothing for approximately level series;
- Holt's linear trend method;
- damped-trend Holt models;
- ETS specifications selected by information criteria.

The data used here are annual, so seasonal Holt-Winters components are not relevant to these 518 annual series themselves.

## Forecast combinations

Instead of manually selecting combination weights, ensemble weights could be estimated using rolling-origin validation, constrained least squares, inverse-error weighting, or stacking. A convex combination would restrict the model weights to be **non-negative and to sum to one**, which preserves a clear interpretation of the combined forecast.

---

# Interpretation boundary

This project evaluates **forecasting performance**, not causal effects.

The results show how three simple forecasting rules perform on the recovered annual tourism dataset under a corrected validation design. They should not be interpreted as structural estimates of the effect of economic conditions, policy, or other determinants on tourism demand.

The reported numerical results were recomputed from the original coursework data. They are **portfolio reconstruction results**, not claims that the corrected outputs appeared in the original submitted assignment.

---

# Repository structure

```text
├── README.md
├── R/
│   └── tourism_forecasting.R
├── analysis/
│   └── validate_forecasts.py
├── data/
│   └── README.md
├── docs/
│   └── coursework_audit.md
├── figures/
│   ├── model_comparison.svg
│   ├── horizon_error.svg
│   ├── mape_formula.svg
│   ├── mase_scale_formula.svg
│   ├── mase_formula.svg
│   ├── naive_forecast_formula.svg
│   ├── growth_forecast_formula.svg
│   ├── trend_model_formula.svg
│   └── trend_forecast_formula.svg
├── results/
│   ├── model_comparison.csv
│   ├── horizon_metrics.csv
│   ├── naive_train_validation_summary.csv
│   └── first5_linear_trend_forecasts.csv
└── requirements.txt
```

---

# Reproduce the audit

Place the recovered course file at:

```text
data/tourism_data.csv
```

Install the Python dependencies and run:

```bash
pip install -r requirements.txt
python analysis/validate_forecasts.py --data data/tourism_data.csv
```

An R implementation following the same series-specific split is provided in `R/tourism_forecasting.R`.

---

## Author

**Maha Gasim**  
MSc Data Analytics for Business and Society  
Ca' Foscari University of Venice
