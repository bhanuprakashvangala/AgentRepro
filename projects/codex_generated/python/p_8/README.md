# ARIMA Time Series Forecaster

This script applies an ARIMA model to a time series stored in CSV format. It runs an Augmented Dickey–Fuller (ADF) test, generates forecasts with confidence intervals, and produces a visualization of past observations versus future predictions.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python forecast_arima.py \
  --input data.csv \
  --time-column date \
  --value-column sales \
  --order 1,1,1 \
  --forecast-steps 12 \
  --freq M \
  --output-csv forecast.csv \
  --plot forecast.png \
  --summary summary.json
```

Key options:
- `--order`: ARIMA `(p,d,q)` order (default `1,1,1`).
- `--forecast-steps`: Number of periods to project (default `12`).
- `--freq`: Pandas frequency string (e.g., `D`, `W`, `M`). If omitted, the script attempts to infer frequency.
- `--output-csv`: File storing forecast values and confidence bounds.
- `--plot`: Path for the generated PNG plot.
- `--summary`: JSON file with ADF test statistics and model parameters.

The forecast CSV includes timestamp, point forecast, and lower/upper confidence bounds. The summary JSON records ADF results (test statistic, p-value, critical values) so you can judge stationarity before modeling.
