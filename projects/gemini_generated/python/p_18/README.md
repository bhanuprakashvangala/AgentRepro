# Stock Price Tracker with Email Alerts

This project is a Python script that tracks the prices of specified stocks and sends alerts when they cross predefined thresholds.

**Important:** For safety and reproducibility, this script **does not send real emails**. It starts a local SMTP debugging server that intercepts any triggered email alerts and prints their full content to the console. This allows you to see the notification system work without needing to configure any email accounts or credentials.

## Features

- **Live Price Tracking**: Uses the `yfinance` library to fetch near real-time stock prices without needing an API key.
- **Configurable Alerts**: Easily define multiple stocks to track and set 'above' or 'below' price thresholds for each.
- **Simulated Email Notifications**: When an alert is triggered, a fully-formatted email is generated and sent to a local debugging server, which prints the email to your console.
- **Persistent Alerts**: An alert for a specific stock and threshold will only be sent once per session to avoid spam.

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

3.  **(Optional) Configure Stocks and Alerts:**
    Open `stock_tracker.py` and modify the `STOCKS_TO_TRACK` dictionary to your liking. You can change the tickers and the price thresholds.
    ```python
    STOCKS_TO_TRACK = {
        "AAPL": {"above": 300.00, "below": 150.00},
        "GOOGL": {"above": 2000.00, "below": 1500.00},
        # Add your favorite stocks here
    }
    ```

4.  **Run the script:**
    ```bash
    python stock_tracker.py
    ```

The script will now run continuously, checking prices at the interval defined in the configuration. To stop the tracker, press `Ctrl+C`.

## Expected Output

The console will show periodic price updates. If a stock price crosses a threshold you have set, you will see an intercepted email alert printed directly to your console, similar to this:

```
2023-10-27 14:30:00 - Checking prices...
  - AAPL: $170.50
  - GOOGL: $1450.10
  - TSLA: $210.00
Waiting for 60 seconds...

--- INTERCEPTED EMAIL ALERT ---
From: stock.alerts@example.com
To: you@example.com
Subject: Stock Alert: GOOGL is below $1500.00!

Alert triggered for GOOGL.

Current Price: $1450.10
Threshold: < $1500.00
-----------------------------
```
