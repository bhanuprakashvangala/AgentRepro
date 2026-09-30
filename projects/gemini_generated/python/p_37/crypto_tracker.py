import ccxt
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
from datetime import datetime

# --- Main Functions ---
def fetch_crypto_data(exchange, pairs, timeframe, limit):
    """Fetches current and historical data for a list of crypto pairs."""
    print(f"Fetching data from {exchange.name}...")
    results = {}
    for pair in pairs:
        try:
            print(f"  - Fetching {pair}...")
            # Fetch current price (ticker)
            ticker = exchange.fetch_ticker(pair)
            
            # Fetch historical data (OHLCV)
            ohlcv = exchange.fetch_ohlcv(pair, timeframe=timeframe, limit=limit)
            
            results[pair] = {
                'ticker': ticker,
                'ohlcv': ohlcv
            }
        except ccxt.NetworkError as e:
            print(f"[ERROR] Network error while fetching {pair}: {e}")
        except ccxt.ExchangeError as e:
            print(f"[ERROR] Exchange error for {pair} (it may not be supported): {e}")
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred for {pair}: {e}")
    return results

def process_and_save_data(pair, ohlcv_data):
    """Converts OHLCV data to a pandas DataFrame and saves it to a CSV file."""
    if not ohlcv_data:
        print(f"No historical data to process for {pair}.")
        return None

    # Convert to DataFrame
    df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Save to CSV
    filename = f"{pair.replace('/', '-')}_historical_data.csv"
    df.to_csv(filename, index=False)
    print(f" -> Historical data saved to: {filename}")
    return df

def generate_price_chart(pair, df):
    """Generates and saves a price trend chart from a DataFrame."""
    if df is None or df.empty:
        print(f"No data to generate chart for {pair}.")
        return

    plt.figure(figsize=(12, 6))
    plt.plot(df['timestamp'], df['close'], label='Close Price')
    plt.title(f'{pair} Price Trend')
    plt.xlabel('Date')
    plt.ylabel('Price (in USDT)')
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    filename = f"{pair.replace('/', '-')}_price_chart.png"
    plt.savefig(filename)
    print(f" -> Price chart saved to: {filename}")
    plt.close() # Close the plot to free up memory

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Track cryptocurrency prices and historical data.")
    parser.add_argument("-p", "--pairs", nargs='+', default=['BTC/USDT', 'ETH/USDT'], help='Crypto pairs to track (e.g., BTC/USDT SOL/USDT).')
    parser.add_argument("-t", "--timeframe", default='1d', help='Timeframe for historical data (e.g., 1h, 1d, 1w, 1M).')
    parser.add_argument("-l", "--limit", type=int, default=90, help='Number of historical data points to fetch (default: 90).')
    args = parser.parse_args()

    # Initialize the exchange (Binance does not require API keys for public data)
    exchange = ccxt.binance()

    # Fetch data
    crypto_data = fetch_crypto_data(exchange, args.pairs, args.timeframe, args.limit)

    # Process each pair
    print("\n--- Processing Results ---")
    for pair, data in crypto_data.items():
        print(f"\n--- {pair} ---")
        # Print current price
        current_price = data['ticker']['last']
        print(f"Current Price: ${current_price:.2f}")

        # Process historical data and generate chart
        df_history = process_and_save_data(pair, data['ohlcv'])
        generate_price_chart(pair, df_history)
    
    print("\n--- Process Complete ---")
