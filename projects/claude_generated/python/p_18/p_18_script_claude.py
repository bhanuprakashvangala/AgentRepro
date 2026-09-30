import yfinance as yf
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from dotenv import load_dotenv
import schedule
import threading

# Load environment variables
load_dotenv()

class StockTracker:
    def __init__(self):
        self.stocks = {}  # {symbol: {'threshold_high': price, 'threshold_low': price, 'last_price': price}}
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'sender_email': os.getenv('SENDER_EMAIL'),
            'sender_password': os.getenv('SENDER_PASSWORD'),
            'recipient_email': os.getenv('RECIPIENT_EMAIL')
        }
        self.running = False

    def add_stock(self, symbol, threshold_low=None, threshold_high=None):
        """Add a stock to track with optional price thresholds."""
        self.stocks[symbol.upper()] = {
            'threshold_low': threshold_low,
            'threshold_high': threshold_high,
            'last_price': None,
            'alert_sent_high': False,
            'alert_sent_low': False
        }
        print(f"Added {symbol.upper()} to tracking list")

    def get_current_price(self, symbol):
        """Fetch current stock price using yfinance."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d', interval='1m')
            if not data.empty:
                current_price = data['Close'].iloc[-1]
                return round(current_price, 2)
            else:
                print(f"No data available for {symbol}")
                return None
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None

    def send_email_alert(self, subject, body):
        """Send email notification."""
        try:
            if not self.email_config['sender_email'] or not self.email_config['sender_password']:
                print("Email credentials not configured. Alert would be sent:")
                print(f"Subject: {subject}")
                print(f"Body: {body}")
                return

            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['recipient_email']
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            text = msg.as_string()
            server.sendmail(self.email_config['sender_email'],
                          self.email_config['recipient_email'],
                          text)
            server.quit()
            print(f"Email alert sent: {subject}")

        except Exception as e:
            print(f"Error sending email: {e}")

    def check_alerts(self, symbol, current_price):
        """Check if price has crossed thresholds and send alerts."""
        stock_info = self.stocks[symbol]
        threshold_high = stock_info['threshold_high']
        threshold_low = stock_info['threshold_low']

        # Check high threshold
        if threshold_high and current_price >= threshold_high:
            if not stock_info['alert_sent_high']:
                subject = f"🚀 ALERT: {symbol} Price Above Threshold!"
                body = f"""
Stock Alert - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Symbol: {symbol}
Current Price: ${current_price}
Threshold (High): ${threshold_high}

The stock price has risen above your specified threshold.
                """
                self.send_email_alert(subject, body)
                stock_info['alert_sent_high'] = True
                stock_info['alert_sent_low'] = False  # Reset low alert
        elif threshold_high and current_price < threshold_high * 0.99:  # Reset if drops 1% below
            stock_info['alert_sent_high'] = False

        # Check low threshold
        if threshold_low and current_price <= threshold_low:
            if not stock_info['alert_sent_low']:
                subject = f"⚠️ ALERT: {symbol} Price Below Threshold!"
                body = f"""
Stock Alert - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Symbol: {symbol}
Current Price: ${current_price}
Threshold (Low): ${threshold_low}

The stock price has dropped below your specified threshold.
                """
                self.send_email_alert(subject, body)
                stock_info['alert_sent_low'] = True
                stock_info['alert_sent_high'] = False  # Reset high alert
        elif threshold_low and current_price > threshold_low * 1.01:  # Reset if rises 1% above
            stock_info['alert_sent_low'] = False

    def update_prices(self):
        """Fetch current prices for all tracked stocks and check alerts."""
        print(f"\n{'='*60}")
        print(f"Price Update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        for symbol in self.stocks:
            current_price = self.get_current_price(symbol)

            if current_price is not None:
                stock_info = self.stocks[symbol]
                last_price = stock_info['last_price']

                # Calculate change
                if last_price:
                    change = current_price - last_price
                    change_pct = (change / last_price) * 100
                    change_str = f"({change:+.2f}, {change_pct:+.2f}%)"
                else:
                    change_str = "(new)"

                # Display info
                print(f"\n{symbol}: ${current_price} {change_str}")
                if stock_info['threshold_low']:
                    print(f"  Low Threshold: ${stock_info['threshold_low']}")
                if stock_info['threshold_high']:
                    print(f"  High Threshold: ${stock_info['threshold_high']}")

                # Check alerts
                self.check_alerts(symbol, current_price)

                # Update last price
                stock_info['last_price'] = current_price

        print(f"{'='*60}\n")

    def start_tracking(self, interval_seconds=60):
        """Start tracking stocks at specified interval."""
        self.running = True
        print(f"Starting stock tracker (updates every {interval_seconds} seconds)")
        print(f"Tracking {len(self.stocks)} stocks: {', '.join(self.stocks.keys())}")
        print("Press Ctrl+C to stop\n")

        # Initial update
        self.update_prices()

        # Schedule periodic updates
        schedule.every(interval_seconds).seconds.do(self.update_prices)

        try:
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping stock tracker...")
            self.running = False


def main():
    """Example usage of the stock tracker."""
    tracker = StockTracker()

    # Add stocks to track with thresholds
    # Format: add_stock(symbol, threshold_low, threshold_high)

    tracker.add_stock('AAPL', threshold_low=150.00, threshold_high=200.00)
    tracker.add_stock('GOOGL', threshold_low=140.00, threshold_high=180.00)
    tracker.add_stock('MSFT', threshold_low=380.00, threshold_high=450.00)
    tracker.add_stock('TSLA', threshold_low=200.00, threshold_high=300.00)

    # Start tracking (updates every 60 seconds)
    tracker.start_tracking(interval_seconds=60)


if __name__ == "__main__":
    main()
