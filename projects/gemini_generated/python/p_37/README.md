# Cryptocurrency Price Tracker

This is a command-line tool that fetches current and historical cryptocurrency prices from a public exchange API and generates price trend charts.

## Features

- **No API Key Required**: Uses the `ccxt` library to access the public, unauthenticated endpoints of the Binance exchange.
- **Live & Historical Data**: Fetches both the current ticker price and historical OHLCV (Open, High, Low, Close, Volume) data.
- **Data Export**: Saves the fetched historical data for each cryptocurrency pair into a well-formatted `.csv` file.
- **Chart Generation**: Creates a `.png` line chart visualizing the closing price trend from the historical data for each pair.
- **Customizable**: You can specify which cryptocurrency pairs and what historical timeframe to analyze via command-line arguments.

## Usage

1.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Tracker:**

    **To run with default settings (BTC/USDT and ETH/USDT for the last 90 days):**
    ```bash
    python crypto_tracker.py
    ```

    **To track different cryptocurrencies and a different timeframe:**
    Use the `--pairs` (or `-p`) and `--timeframe` (or `-t`) flags.
    ```bash
    # Get daily data for Solana and Cardano
    python crypto_tracker.py --pairs SOL/USDT ADA/USDT

    # Get 4-hour data for Dogecoin
    python crypto_tracker.py -p DOGE/USDT -t 4h
    ```

## Output

For each cryptocurrency pair you track, the script will generate two files in the same directory:

1.  `[PAIR]_historical_data.csv`: A CSV file containing the OHLCV data.
    - e.g., `BTC-USDT_historical_data.csv`
2.  `[PAIR]_price_chart.png`: A PNG image of the price trend chart.
    - e.g., `BTC-USDT_price_chart.png`

The script will also print the current price and status updates to your console.
