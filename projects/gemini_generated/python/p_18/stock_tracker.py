import yfinance as yf
import time
import smtplib
from email.mime.text import MIMEText
from threading import Thread
import asyncore
import smtpd

# --- Configuration ---
# Define stocks to track and their alert thresholds.
# You can add/remove stocks and set 'above' or 'below' price points.
STOCKS_TO_TRACK = {
    "AAPL": {"above": 300.00, "below": 150.00},
    "GOOGL": {"above": 2000.00, "below": 1500.00},
    "TSLA": {"below": 200.00, "above": 1000.00}
}
# Interval in seconds to check prices
CHECK_INTERVAL_SECONDS = 60

# --- Email Simulation Configuration ---
# Emails will be printed to the console, not sent over the internet.
SMTP_HOST = "localhost"
SMTP_PORT = 1025
SENDER_EMAIL = "stock.alerts@example.com"
RECIPIENT_EMAIL = "you@example.com"

# =============================================================================
# --- Local SMTP Server for Reproducible Email Simulation ---
# =============================================================================
class DebuggingServer(smtpd.DebuggingServer):
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        print("\n--- INTERCEPTED EMAIL ALERT ---")
        print(data.decode())
        print("-----------------------------")

def run_debugging_server():
    print(f"Starting local SMTP debugging server on {SMTP_HOST}:{SMTP_PORT}...")
    server = DebuggingServer((SMTP_HOST, SMTP_PORT), None)
    asyncore.loop()

# =============================================================================
# --- Core Application Logic ---
# =============================================================================

def fetch_stock_price(ticker: str) -> float | None:
    """Fetches the current market price for a given stock ticker."""
    try:
        stock = yf.Ticker(ticker)
        # Use 'regularMarketPrice' for a more current price if available
        price = stock.info.get('regularMarketPrice')
        if price is None:
            # Fallback to previous day's close if market is not open
            price = stock.history(period='1d')['Close'].iloc[-1]
        return price
    except Exception as e:
        print(f"Could not fetch price for {ticker}: {e}")
        return None

def send_email_alert(subject: str, body: str):
    """Constructs and sends an email to the local debugging server."""
    try:
        msg = MIMEText(body)
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.send_message(msg)
        print(f"Successfully sent alert: '{subject}'")
    except Exception as e:
        print(f"Failed to send email alert: {e}")

def track_stocks():
    """Main loop to track stocks and check for alert conditions."""
    triggered_alerts = set()
    print("--- Starting Stock Price Tracker ---")

    while True:
        print(f"\n{time.strftime('%Y-%m-%d %H:%M:%S')} - Checking prices...")
        for ticker, thresholds in STOCKS_TO_TRACK.items():
            price = fetch_stock_price(ticker)
            if price is None:
                continue
            
            print(f"  - {ticker}: ${price:.2f}")

            # Check 'above' threshold
            if 'above' in thresholds and price > thresholds['above']:
                alert_key = f"{ticker}-above"
                if alert_key not in triggered_alerts:
                    subject = f"Stock Alert: {ticker} is above ${thresholds['above']:.2f}!"
                    body = f"Alert triggered for {ticker}.\n\nCurrent Price: ${price:.2f}\nThreshold: > ${thresholds['above']:.2f}"
                    send_email_alert(subject, body)
                    triggered_alerts.add(alert_key)

            # Check 'below' threshold
            if 'below' in thresholds and price < thresholds['below']:
                alert_key = f"{ticker}-below"
                if alert_key not in triggered_alerts:
                    subject = f"Stock Alert: {ticker} is below ${thresholds['below']:.2f}!"
                    body = f"Alert triggered for {ticker}.\n\nCurrent Price: ${price:.2f}\nThreshold: < ${thresholds['below']:.2f}"
                    send_email_alert(subject, body)
                    triggered_alerts.add(alert_key)
        
        print(f"Waiting for {CHECK_INTERVAL_SECONDS} seconds...")
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    # Start the local SMTP server in a background thread
    smtp_thread = Thread(target=run_debugging_server, daemon=True)
    smtp_thread.start()
    time.sleep(1) # Give the server a moment to start

    try:
        track_stocks()
    except KeyboardInterrupt:
        print("\n--- Tracker stopped by user. ---")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
