#!/usr/bin/env python3
"""Cryptocurrency price tracker with historical data download and chart generation."""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path
from typing import List, Optional

import ccxt
import matplotlib.pyplot as plt
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch and chart historical cryptocurrency prices")
    parser.add_argument(
        "--exchange",
        default="binance",
        help="Exchange id supported by ccxt (default: binance)",
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        required=True,
        help="Trading pairs e.g. BTC/USDT ETH/USDT",
    )
    parser.add_argument(
        "--timeframe",
        default="1h",
        help="OHLCV timeframe (default: 1h)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=200,
        help="Number of candles to fetch (default: 200)",
    )
    parser.add_argument(
        "--since",
        help="Start time ISO 8601 (optional, overrides limit start)",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to save CSVs and charts",
    )
    return parser.parse_args()


def create_exchange(exchange_id: str) -> ccxt.Exchange:
    try:
        exchange_class = getattr(ccxt, exchange_id)
    except AttributeError as exc:
        raise ValueError(f"Unsupported exchange: {exchange_id}") from exc
    exchange = exchange_class({"enableRateLimit": True})
    exchange.load_markets()
    return exchange


def parse_since(since: Optional[str], exchange: ccxt.Exchange, timeframe: str) -> Optional[int]:
    if not since:
        return None
    try:
        timestamp = exchange.parse8601(since)
    except Exception as exc:  # pylint: disable=broad-except
        raise ValueError(f"Invalid since timestamp: {since}") from exc
    if timestamp is None:
        raise ValueError(f"Unable to parse since timestamp: {since}")
    return timestamp


def fetch_ohlcv(exchange: ccxt.Exchange, symbol: str, timeframe: str, limit: int, since: Optional[int]) -> pd.DataFrame:
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit, since=since)
    except Exception as exc:  # pylint: disable=broad-except
        raise RuntimeError(f"Failed to fetch data for {symbol}: {exc}") from exc

    if not ohlcv:
        raise RuntimeError(f"No OHLCV data returned for {symbol}")

    columns = ["timestamp", "open", "high", "low", "close", "volume"]
    df = pd.DataFrame(ohlcv, columns=columns)
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.tz_convert(None)
    return df


def save_csv(df: pd.DataFrame, output_path: Path) -> None:
    df.to_csv(output_path, index=False)
    print(f"Saved CSV: {output_path}")


def plot_trend(df: pd.DataFrame, symbol: str, output_path: Path) -> None:
    plt.figure(figsize=(10, 5))
    plt.plot(df["datetime"], df["close"], label="Close")
    plt.title(f"Price Trend for {symbol}")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved chart: {output_path}")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    exchange = create_exchange(args.exchange)
    since_ts = parse_since(args.since, exchange, args.timeframe)

    for symbol in args.symbols:
        if symbol not in exchange.symbols:
            print(f"Warning: {symbol} not found on {args.exchange}. Skipping.")
            continue
        try:
            df = fetch_ohlcv(exchange, symbol, args.timeframe, args.limit, since_ts)
        except RuntimeError as exc:
            print(exc, file=sys.stderr)
            continue

        csv_path = output_dir / f"{symbol.replace('/', '_')}_{args.timeframe}.csv"
        save_csv(df, csv_path)

        chart_path = output_dir / f"{symbol.replace('/', '_')}_{args.timeframe}.png"
        plot_trend(df, symbol, chart_path)

    print("Processing complete.")


if __name__ == "__main__":
    main()
