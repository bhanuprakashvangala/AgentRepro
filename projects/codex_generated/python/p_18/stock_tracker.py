#!/usr/bin/env python3
"""Monitor stock prices with yfinance and send email alerts when thresholds are crossed."""

from __future__ import annotations

import argparse
import json
import smtplib
import ssl
import sys
import time
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import yfinance as yf


@dataclass
class AlertThreshold:
    symbol: str
    above: Optional[float]
    below: Optional[float]


@dataclass
class EmailSettings:
    host: str
    port: int
    username: str
    password: str
    sender: str
    recipients: List[str]
    use_tls: bool = True


@dataclass
class Config:
    poll_interval: int
    alerts: List[AlertThreshold]


@dataclass
class AlertState:
    above_triggered: bool = False
    below_triggered: bool = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stock price tracker with alerts")
    parser.add_argument("--config", required=True, help="Path to JSON config with poll_interval and alerts")
    parser.add_argument(
        "--smtp-host",
        help="SMTP host for email notifications (optional if using dry-run)",
    )
    parser.add_argument("--smtp-port", type=int, default=587, help="SMTP port (default: 587)")
    parser.add_argument("--smtp-user", help="SMTP username")
    parser.add_argument("--smtp-password", help="SMTP password")
    parser.add_argument("--sender", help="Sender email address")
    parser.add_argument(
        "--recipients",
        help="Comma-separated list of recipient email addresses",
    )
    parser.add_argument("--no-tls", action="store_true", help="Disable TLS for SMTP connection")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not send emails; log alerts to stdout only",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Fetch prices and evaluate alerts a single time (no polling loop)",
    )
    return parser.parse_args()


def load_config(path: Path) -> Config:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    poll_interval = int(data.get("poll_interval", 60))
    if poll_interval <= 0:
        raise ValueError("poll_interval must be a positive integer")

    alerts_raw = data.get("alerts")
    if not alerts_raw or not isinstance(alerts_raw, list):
        raise ValueError("Config must contain an 'alerts' list")

    alerts: List[AlertThreshold] = []
    for entry in alerts_raw:
        symbol = entry.get("symbol") or entry.get("ticker")
        if not symbol:
            raise ValueError("Each alert must include a 'symbol'")
        above = entry.get("above")
        below = entry.get("below")
        if above is None and below is None:
            raise ValueError(f"Alert for {symbol} must specify 'above' and/or 'below'")
        alerts.append(AlertThreshold(symbol=symbol.upper(), above=above, below=below))

    return Config(poll_interval=poll_interval, alerts=alerts)


def build_email_settings(args: argparse.Namespace) -> Optional[EmailSettings]:
    if args.dry_run:
        return None
    required = [args.smtp_host, args.smtp_user, args.smtp_password, args.sender, args.recipients]
    if any(value is None for value in required):
        raise ValueError(
            "SMTP settings are required unless --dry-run is specified (host, user, password, sender, recipients)"
        )
    recipients = [email.strip() for email in args.recipients.split(",") if email.strip()]
    if not recipients:
        raise ValueError("At least one recipient email address must be provided")
    return EmailSettings(
        host=args.smtp_host,
        port=args.smtp_port,
        username=args.smtp_user,
        password=args.smtp_password,
        sender=args.sender,
        recipients=recipients,
        use_tls=not args.no_tls,
    )


def fetch_latest_price(symbol: str) -> Optional[float]:
    ticker = yf.Ticker(symbol)
    price: Optional[float] = None
    try:
        fast_info = getattr(ticker, "fast_info", None)
        if fast_info is not None:
            price = fast_info.get("last_price") or fast_info.get("lastPrice")
    except Exception:  # pylint: disable=broad-except
        price = None

    if price is None:
        try:
            hist = ticker.history(period="1d", interval="1m")
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])
        except Exception:  # pylint: disable=broad-except
            price = None

    return float(price) if price is not None else None


def send_email(settings: EmailSettings, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = settings.sender
    message["To"] = ", ".join(settings.recipients)
    message["Subject"] = subject
    message.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP(settings.host, settings.port, timeout=30) as server:
        if settings.use_tls:
            server.starttls(context=context)
        if settings.username and settings.password:
            server.login(settings.username, settings.password)
        server.send_message(message)


def evaluate_alert(symbol: str, price: float, threshold: AlertThreshold, state: AlertState) -> List[str]:
    notifications: List[str] = []
    if threshold.above is not None:
        if price >= threshold.above:
            if not state.above_triggered:
                notifications.append(
                    f"{symbol} has crossed above {threshold.above:.2f} (current price: {price:.2f})"
                )
                state.above_triggered = True
        else:
            state.above_triggered = False
    if threshold.below is not None:
        if price <= threshold.below:
            if not state.below_triggered:
                notifications.append(
                    f"{symbol} has fallen below {threshold.below:.2f} (current price: {price:.2f})"
                )
                state.below_triggered = True
        else:
            state.below_triggered = False
    return notifications


def run_tracker(config: Config, email_settings: Optional[EmailSettings], once: bool) -> None:
    states: Dict[str, AlertState] = {alert.symbol: AlertState() for alert in config.alerts}

    def process_cycle() -> None:
        triggered_messages: List[str] = []
        for alert in config.alerts:
            price = fetch_latest_price(alert.symbol)
            if price is None:
                print(f"Warning: unable to fetch price for {alert.symbol}")
                continue
            print(f"{alert.symbol}: {price:.2f}")
            triggered_messages.extend(evaluate_alert(alert.symbol, price, alert, states[alert.symbol]))

        if triggered_messages:
            subject = "Stock Price Alert"
            body = "\n".join(triggered_messages)
            print("Alerts triggered:\n" + body)
            if email_settings:
                try:
                    send_email(email_settings, subject, body)
                    print("Email notification sent.")
                except Exception as exc:  # pylint: disable=broad-except
                    print(f"Error sending email: {exc}", file=sys.stderr)

    process_cycle()
    if once:
        return

    try:
        while True:
            time.sleep(config.poll_interval)
            process_cycle()
    except KeyboardInterrupt:
        print("Stopping tracker.")


def main() -> None:
    args = parse_args()
    try:
        config = load_config(Path(args.config))
        email_settings = build_email_settings(args)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    run_tracker(config, email_settings, once=args.once)


if __name__ == "__main__":
    main()
