# Data

The analysis uses the original **518 annual tourism time-series** CSV recovered from the EM1415 MSc coursework folder (`tourism_data.csv`). The matrix has 43 rows and 518 columns, but individual series contain different numbers of leading missing values and therefore different observed lengths.

The raw course dataset is **not redistributed in this repository** because the recovered folder does not include a clear redistribution/licensing statement. To reproduce the project, place your authorized copy at:

```text
data/tourism_data.csv
```

The audit code then handles missing values series-by-series and reserves the last four observed values of each series for validation.
