# Coursework audit

The original RMarkdown is titled **Predictive Business and Finance [EM1415] — Project: The Forecasting Tourism 2010 Competition**.

## What was already present

The submission contained code to import the 518-series CSV, visualize the columns, create a nominal four-row validation sample, generate naive forecasts, and discuss some methodological questions. Several Question 8 prompts were answered in prose.

## What required correction or completion

### Series-specific validation split

The original code uses rows 1–39 for training and rows 40–43 for validation for every column. This assumes that every series has 43 observed years. The CSV instead contains leading missing values and observed lengths from 7 to 43 years.

The reconstruction removes leading missing values separately for each series and reserves its final four observed values for validation.

### Training MAPE

The submitted code defines the training actual values as four copies of the final training observation and compares them to four copies of the same value. This mechanically gives zero error.

The corrected training naive forecast is the standard one-step rule:

`forecast[t] = actual[t-1]`.

Across the 518 series the mean training MAPE is **15.873984%**.

### MASE

Question 6 was unanswered. The reconstruction computes MASE using the mean absolute one-step naive error in the training sample as the scaling denominator. Mean validation MASE for the naive forecast is **3.370211**.

### Scatter-plot interpretation

Question 7 was unanswered. The reconstructed series-level results show a training/validation MAPE correlation of **0.427076**: higher in-sample error tends to predict higher validation error, but the relationship is only moderate. Validation errors are also substantially more dispersed and increase with forecast horizon.

### Growth-adjusted naive formula

The submitted response wrote `F[t+k] = F[t] * 1.055^(k-1)`. Baker and Howard's competition-method description uses the last observation multiplied by **1.055^h**. The corrected rule therefore applies 5.5% growth already at horizon one.

### Rationale for growth adjustment

The original response included an unrelated statement about adding a constant to MAPE. The relevant rationale is that a positive drift incorporates empirical/domain knowledge about long-run growth in tourism demand into a simple naive forecast.

### Linear regression forecasts

Question 8(d) was unanswered. The reconstruction fits `tourism demand ~ time` separately to each training series and forecasts the four held-out observations. Exact forecasts for the first five series are committed in `results/first5_linear_trend_forecasts.csv`.

## Interpretive boundary

The corrected numerical values are recomputed portfolio results. They should not be described as results contained in the submitted assignment. This distinction is intentional so that the GitHub project remains auditable and interview-defensible.
