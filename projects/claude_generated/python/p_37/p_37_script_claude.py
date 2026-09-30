"""
Cryptocurrency Price Tracker with Historical Data
Tracks multiple cryptocurrencies and generates price trend charts
"""

import ccxt
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Optional
import time


class CryptoTracker:
    """Track cryptocurrency prices and historical data"""

    def __init__(self, exchange_name: str = 'binance'):
        """
        Initialize the crypto tracker

        Args:
            exchange_name: Name of the exchange to use (default: binance)
        """
        self.exchange = getattr(ccxt, exchange_name)()
        self.data_file = 'crypto_historical_data.json'
        self.historical_data = self.load_historical_data()

    def load_historical_data(self) -> Dict:
        """Load historical data from file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {}

    def save_historical_data(self):
        """Save historical data to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.historical_data, f, indent=2)

    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for a cryptocurrency

        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')

        Returns:
            Current price or None if failed
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None

    def get_historical_prices(self, symbol: str, timeframe: str = '1d',
                             days: int = 30) -> pd.DataFrame:
        """
        Fetch historical OHLCV data

        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            timeframe: Candlestick timeframe ('1m', '5m', '1h', '1d', etc.)
            days: Number of days of historical data

        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Calculate timestamp for start date
            since = self.exchange.parse8601(
                (datetime.now() - timedelta(days=days)).isoformat()
            )

            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since)

            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            return df
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()

    def track_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Track current prices for multiple cryptocurrencies

        Args:
            symbols: List of trading pair symbols

        Returns:
            Dictionary mapping symbols to current prices
        """
        prices = {}
        timestamp = datetime.now().isoformat()

        for symbol in symbols:
            price = self.get_current_price(symbol)
            if price is not None:
                prices[symbol] = price

                # Store in historical data
                if symbol not in self.historical_data:
                    self.historical_data[symbol] = []

                self.historical_data[symbol].append({
                    'timestamp': timestamp,
                    'price': price
                })

        self.save_historical_data()
        return prices

    def generate_price_chart(self, symbol: str, days: int = 30,
                           save_path: Optional[str] = None):
        """
        Generate price trend chart for a cryptocurrency

        Args:
            symbol: Trading pair symbol
            days: Number of days to chart
            save_path: Path to save chart (if None, displays chart)
        """
        df = self.get_historical_prices(symbol, '1d', days)

        if df.empty:
            print(f"No data available for {symbol}")
            return

        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8),
                                       gridspec_kw={'height_ratios': [3, 1]})

        # Price chart
        ax1.plot(df.index, df['close'], linewidth=2, color='#2962FF')
        ax1.fill_between(df.index, df['close'], alpha=0.3, color='#2962FF')
        ax1.set_title(f'{symbol} Price Trend ({days} Days)',
                     fontsize=16, fontweight='bold')
        ax1.set_ylabel('Price (USDT)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(labelbottom=False)

        # Add min/max annotations
        max_price = df['close'].max()
        min_price = df['close'].min()
        max_date = df['close'].idxmax()
        min_date = df['close'].idxmin()

        ax1.annotate(f'High: ${max_price:,.2f}',
                    xy=(max_date, max_price),
                    xytext=(10, 10), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.5', fc='green', alpha=0.7),
                    fontsize=10, color='white')

        ax1.annotate(f'Low: ${min_price:,.2f}',
                    xy=(min_date, min_price),
                    xytext=(10, -10), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.5', fc='red', alpha=0.7),
                    fontsize=10, color='white')

        # Volume chart
        colors = ['green' if close > open_ else 'red'
                 for close, open_ in zip(df['close'], df['open'])]
        ax2.bar(df.index, df['volume'], color=colors, alpha=0.6)
        ax2.set_ylabel('Volume', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.grid(True, alpha=0.3)

        # Format x-axis
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to {save_path}")
        else:
            plt.show()

    def generate_comparison_chart(self, symbols: List[str], days: int = 30,
                                 save_path: Optional[str] = None):
        """
        Generate comparison chart for multiple cryptocurrencies

        Args:
            symbols: List of trading pair symbols
            days: Number of days to chart
            save_path: Path to save chart (if None, displays chart)
        """
        plt.figure(figsize=(14, 8))

        for symbol in symbols:
            df = self.get_historical_prices(symbol, '1d', days)
            if not df.empty:
                # Normalize prices to show percentage change
                normalized = (df['close'] / df['close'].iloc[0] - 1) * 100
                plt.plot(df.index, normalized, linewidth=2,
                        label=symbol.split('/')[0])

        plt.title(f'Cryptocurrency Price Comparison ({days} Days)',
                 fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Price Change (%)', fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.axhline(y=0, color='black', linestyle='--', linewidth=1)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Comparison chart saved to {save_path}")
        else:
            plt.show()

    def get_price_statistics(self, symbol: str, days: int = 30) -> Dict:
        """
        Calculate price statistics for a cryptocurrency

        Args:
            symbol: Trading pair symbol
            days: Number of days to analyze

        Returns:
            Dictionary with statistics
        """
        df = self.get_historical_prices(symbol, '1d', days)

        if df.empty:
            return {}

        current_price = df['close'].iloc[-1]
        start_price = df['close'].iloc[0]
        price_change = current_price - start_price
        price_change_pct = (price_change / start_price) * 100

        stats = {
            'symbol': symbol,
            'current_price': current_price,
            'start_price': start_price,
            'price_change': price_change,
            'price_change_pct': price_change_pct,
            'high': df['high'].max(),
            'low': df['low'].min(),
            'avg_price': df['close'].mean(),
            'volatility': df['close'].std(),
            'avg_volume': df['volume'].mean(),
            'total_volume': df['volume'].sum()
        }

        return stats

    def print_statistics(self, symbols: List[str], days: int = 30):
        """
        Print price statistics for multiple cryptocurrencies

        Args:
            symbols: List of trading pair symbols
            days: Number of days to analyze
        """
        print(f"\n{'='*80}")
        print(f"CRYPTOCURRENCY STATISTICS ({days} Days)")
        print(f"{'='*80}\n")

        for symbol in symbols:
            stats = self.get_price_statistics(symbol, days)

            if stats:
                print(f"{symbol}")
                print(f"{'-'*80}")
                print(f"Current Price:    ${stats['current_price']:,.2f}")
                print(f"Price Change:     ${stats['price_change']:,.2f} "
                      f"({stats['price_change_pct']:+.2f}%)")
                print(f"High / Low:       ${stats['high']:,.2f} / ${stats['low']:,.2f}")
                print(f"Average Price:    ${stats['avg_price']:,.2f}")
                print(f"Volatility (σ):   ${stats['volatility']:,.2f}")
                print(f"Average Volume:   {stats['avg_volume']:,.0f}")
                print(f"{'-'*80}\n")


def main():
    """Main function demonstrating the crypto tracker"""

    # Initialize tracker
    print("Initializing Cryptocurrency Price Tracker...")
    tracker = CryptoTracker(exchange_name='binance')

    # Define cryptocurrencies to track
    symbols = [
        'BTC/USDT',   # Bitcoin
        'ETH/USDT',   # Ethereum
        'BNB/USDT',   # Binance Coin
        'SOL/USDT',   # Solana
        'XRP/USDT'    # Ripple
    ]

    # Track current prices
    print("\nFetching current prices...")
    current_prices = tracker.track_prices(symbols)

    print("\nCURRENT PRICES:")
    print("-" * 40)
    for symbol, price in current_prices.items():
        print(f"{symbol:15} ${price:,.2f}")

    # Display statistics
    tracker.print_statistics(symbols, days=30)

    # Generate individual price charts
    print("\nGenerating price charts...")
    for symbol in symbols[:2]:  # Generate charts for first 2 cryptos
        crypto_name = symbol.split('/')[0]
        chart_path = f'{crypto_name}_price_chart.png'
        tracker.generate_price_chart(symbol, days=30, save_path=chart_path)

    # Generate comparison chart
    print("\nGenerating comparison chart...")
    tracker.generate_comparison_chart(symbols, days=30,
                                     save_path='crypto_comparison.png')

    print("\n" + "="*80)
    print("Cryptocurrency tracking complete!")
    print("="*80)
    print("\nGenerated files:")
    print("  - crypto_historical_data.json (stored price data)")
    print("  - BTC_price_chart.png (Bitcoin price chart)")
    print("  - ETH_price_chart.png (Ethereum price chart)")
    print("  - crypto_comparison.png (comparison chart)")


if __name__ == "__main__":
    main()
