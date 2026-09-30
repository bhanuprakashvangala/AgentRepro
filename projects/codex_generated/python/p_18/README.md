# Stock Price Tracker

Fetches live quotes via `yfinance`, monitors threshold breaches, and sends email alerts.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Create a JSON config (e.g., `config.json`):

```json
{
  "poll_interval": 120,
  "alerts": [
    { "symbol": "AAPL", "above": 190.0 },
    { "symbol": "MSFT", "below": 300.0 },
    { "symbol": "TSLA", "above": 260.0, "below": 210.0 }
  ]
}
```

- `poll_interval` — seconds between checks (default 60 if omitted).
- Each alert entry requires `symbol` and optional `above`/`below` thresholds.

## Run the tracker

Dry-run (no email) to verify alerts:

```bash
python stock_tracker.py --config config.json --dry-run --once
```

Continuous monitoring with email notifications:

```bash
python stock_tracker.py \
  --config config.json \
  --smtp-host smtp.example.com \
  --smtp-port 587 \
  --smtp-user user@example.com \
  --smtp-password "app-password" \
  --sender alerts@example.com \
  --recipients you@example.com,team@example.com
```

### Flags
- `--dry-run`: Log alerts without sending email.
- `--once`: Run a single poll instead of looping.
- `--no-tls`: Disable SMTP TLS (enabled by default).

Alerts fire once when a threshold is breached and reset after the price returns past the threshold in the opposite direction. Email notifications list all triggers detected within the latest poll cycle.

> **Note:** Provide email credentials securely (e.g., environment variables) and use app passwords where available. API rate limits may affect how frequently you can poll tickers; adjust `poll_interval` accordingly.
