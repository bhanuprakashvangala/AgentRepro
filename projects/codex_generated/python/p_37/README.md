# Cryptocurrency Price Tracker

Fetches historical OHLCV data for multiple trading pairs via CCXT and generates CSV files plus price trend charts.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage
```bash
python price_tracker.py \
  --exchange binance \
  --symbols BTC/USDT ETH/USDT \
  --timeframe 1h \
  --limit 500 \
  --output-dir data
```

Options:
- `--exchange`: CCXT exchange id (default `binance`).
- `--symbols`: One or more trading pairs supported by the exchange.
- `--timeframe`: Candle timeframe (e.g., `1m`, `15m`, `1h`, `1d`).
- `--limit`: Number of candles to fetch (default `200`).
- `--since`: Optional ISO8601 start date (e.g., `2023-01-01T00:00:00Z`).
- `--output-dir`: Directory to store CSVs and charts.
- `--device`: Not applicable (CPU) but you can adjust usage as needed.

Each symbol produces:
- `<symbol>_<timeframe>.csv` – Historical OHLCV with timestamps.
- `<symbol>_<timeframe>.png` – Closing price trend chart.

> **Note:** Public market data requires no authentication on many exchanges, but you may hit rate limits. For high volume usage consider API keys and CCXT rate limit guidance.
