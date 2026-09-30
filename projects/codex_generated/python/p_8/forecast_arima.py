#!/usr/bin/env python3
"""Time series forecasting with ARIMA, including ADF test and visualization."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ARIMA forecasting with stationarity diagnostics")
    parser.add_argument("--input", required=True, help="Path to CSV file containing the time series")
    parser.add_argument("--time-column", required=True, help="Column containing datetime values")
    parser.add_argument("--value-column", required=True, help="Column containing numeric values")
    parser.add_argument(
        "--order",
        default="1,1,1",
        help="ARIMA order as comma-separated p,d,q (default: 1,1,1)",
    )
    parser.add_argument(
        "--forecast-steps",
        type=int,
        default=12,
        help="Number of periods to forecast (default: 12)",
    )
    parser.add_argument(
        "--freq",
        default=None,
        help="Optional pandas frequency string (e.g., 'M', 'D'). If omitted, inferred where possible.",
    )
    parser.add_argument(
        "--output-csv",
        default="forecast.csv",
        help="Destination CSV file for forecast and confidence intervals",
    )
    parser.add_argument(
        "--plot",
        default="forecast.png",
        help="Output path for the forecast plot",
    )
    parser.add_argument(
        "--summary",
        default="summary.json",
        help="Path to write JSON summary including ADF statistics",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Encoding of the input CSV (default: utf-8)",
    )
    return parser.parse_args()


def parse_order(order_str: str) -> Tuple[int, int, int]:
    try:
        parts = [int(part.strip()) for part in order_str.split(",")]
        if len(parts) != 3:
            raise ValueError
        return tuple(parts)  # type: ignore[return-value]
    except ValueError as exc:
        raise ValueError("--order must be in the format p,d,q with integers") from exc


def load_series(path: Path, time_col: str, value_col: str, freq: str | None, encoding: str) -> pd.Series:
    if not path.exists():
        raise FileNotFoundError(f"Input CSV not found: {path}")

    df = pd.read_csv(path, encoding=encoding)
    if time_col not in df.columns or value_col not in df.columns:
        raise KeyError(f"Input columns not found. Available columns: {list(df.columns)}")

    series = df[[time_col, value_col]].dropna(subset=[time_col, value_col]).copy()
    if series.empty:
        raise ValueError("No data available after dropping missing time/value rows")

    series[time_col] = pd.to_datetime(series[time_col], errors="coerce")
    series = series.dropna(subset=[time_col])
    series = series.sort_values(time_col)
    ts = series.set_index(time_col)[value_col].astype(float)

    if freq is not None:
        ts = ts.asfreq(freq)
    else:
        inferred = pd.infer_freq(ts.index)
        if inferred is not None:
            ts = ts.asfreq(inferred)

    ts = ts.interpolate(method="time")
    ts = ts.bfill().ffill()

    return ts


def perform_adf_test(series: pd.Series) -> Dict[str, float | Dict[str, float]]:
    result = adfuller(series.dropna())
    test_stat, p_value, used_lag, n_obs, critical_values, icbest = result
    adf_summary: Dict[str, float | Dict[str, float]] = {
        "test_statistic": float(test_stat),
        "p_value": float(p_value),
        "used_lags": float(used_lag),
        "n_obs": float(n_obs),
        "icbest": float(icbest),
        "critical_values": {key: float(value) for key, value in critical_values.items()},
    }
    return adf_summary


def fit_arima(series: pd.Series, order: Tuple[int, int, int]) -> ARIMA:
    model = ARIMA(series, order=order)
    return model.fit()


def forecast(model_fit, steps: int) -> Tuple[pd.Series, pd.DataFrame]:
    forecast_res = model_fit.get_forecast(steps=steps)
    mean = forecast_res.predicted_mean
    conf_int = forecast_res.conf_int()
    return mean, conf_int


def save_forecast(mean: pd.Series, conf_int: pd.DataFrame, output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(
        {
            "forecast": mean,
            "lower": conf_int.iloc[:, 0],
            "upper": conf_int.iloc[:, 1],
        }
    )
    df.index.name = "timestamp"
    df.to_csv(output_csv)


def plot_forecast(series: pd.Series, mean: pd.Series, conf_int: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 5))
    plt.plot(series.index, series.values, label="Observed", color="tab:blue")
    plt.plot(mean.index, mean.values, label="Forecast", color="tab:orange")
    plt.fill_between(
        mean.index,
        conf_int.iloc[:, 0],
        conf_int.iloc[:, 1],
        color="tab:orange",
        alpha=0.2,
        label="Confidence Interval",
    )
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.title("ARIMA Forecast")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def write_summary(summary_path: Path, adf_summary: Dict[str, float | Dict[str, float]], order: Tuple[int, int, int]) -> None:
    summary_data = {
        "adf_test": adf_summary,
        "model_order": {"p": order[0], "d": order[1], "q": order[2]},
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary_data, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()

    try:
        order = parse_order(args.order)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        series = load_series(Path(args.input), args.time_column, args.value_column, args.freq, args.encoding)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Failed to load series: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        adf_summary = perform_adf_test(series)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Failed to run ADF test: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        model_fit = fit_arima(series, order)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Failed to fit ARIMA model: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        mean, conf_int = forecast(model_fit, max(1, args.forecast_steps))
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Failed to generate forecast: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        save_forecast(mean, conf_int, Path(args.output_csv))
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Failed to save forecast CSV: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        plot_forecast(series, mean, conf_int, Path(args.plot))
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Failed to save forecast plot: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        write_summary(Path(args.summary), adf_summary, order)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Failed to write summary: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Forecasting complete.")
    print(f"ADF p-value: {adf_summary['p_value']:.4f}")
    print(f"Forecast saved to: {args.output_csv}")
    print(f"Plot saved to: {args.plot}")
    print(f"Summary saved to: {args.summary}")


if __name__ == "__main__":
    main()
