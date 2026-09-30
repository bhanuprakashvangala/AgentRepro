#!/usr/bin/env python3
"""Send personalized emails with HTML templates and attachments."""

from __future__ import annotations

import argparse
import csv
import mimetypes
import os
import smtplib
import sys
import time
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path
from string import Template
from typing import Dict, Iterable, List, Optional

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5


@dataclass
class Recipient:
    email: str
    name: str
    variables: Dict[str, str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send personalized HTML emails with attachments")
    parser.add_argument("--smtp-host", required=True, help="SMTP server hostname")
    parser.add_argument("--smtp-port", type=int, default=587, help="SMTP server port (default: 587)")
    parser.add_argument("--smtp-user", required=True, help="SMTP username")
    parser.add_argument("--smtp-password", required=True, help="SMTP password")
    parser.add_argument("--sender", required=True, help="Sender email address")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--recipients", required=True, help="CSV file listing recipients")
    parser.add_argument("--template", required=True, help="Path to HTML template file")
    parser.add_argument(
        "--attachments",
        default=None,
        help="Comma-separated list of file paths to attach",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=MAX_RETRIES,
        help="Retry attempts for failed sends (default: 3)",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=RETRY_DELAY_SECONDS,
        help="Delay in seconds between retries (default: 5)",
    )
    return parser.parse_args()


def read_recipients(csv_path: Path) -> List[Recipient]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Recipients file not found: {csv_path}")

    recipients: List[Recipient] = []
    with csv_path.open("r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        required_fields = {"email", "name"}
        missing_fields = required_fields - set(reader.fieldnames or [])
        if missing_fields:
            raise ValueError(f"Recipients CSV missing required columns: {missing_fields}")

        for row in reader:
            email = (row.get("email") or "").strip()
            name = (row.get("name") or "").strip()
            if not email:
                continue
            variables = {k: (v or "") for k, v in row.items() if k not in required_fields}
            recipients.append(Recipient(email=email, name=name, variables=variables))

    return recipients


def load_template(template_path: Path) -> Template:
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    content = template_path.read_text(encoding="utf-8")
    return Template(content)


def build_message(
    sender: str,
    recipient: Recipient,
    subject: str,
    template: Template,
    attachments: Iterable[Path],
) -> EmailMessage:
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient.email
    message["Subject"] = subject

    substitutions = {"name": recipient.name, **recipient.variables}
    html_content = template.safe_substitute(substitutions)

    message.set_content("This email requires an HTML-compatible client.")
    message.add_alternative(html_content, subtype="html")

    for attachment in attachments:
        if not attachment.exists():
            raise FileNotFoundError(f"Attachment not found: {attachment}")
        mime_type, _ = mimetypes.guess_type(attachment.name)
        maintype, subtype = (mime_type or "application/octet-stream").split("/", 1)
        message.add_attachment(
            attachment.read_bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=attachment.name,
        )

    return message


def send_email(
    message: EmailMessage,
    host: str,
    port: int,
    username: str,
    password: str,
    max_retries: int,
    delay: int,
) -> None:
    attempts = max(1, max_retries)
    for attempt in range(1, attempts + 1):
        try:
            with smtplib.SMTP(host, port, timeout=30) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(message)
            return
        except Exception as exc:
            if attempt == attempts:
                raise RuntimeError(
                    f"Failed to send email to {message['To']} after {attempts} attempt(s)"
                ) from exc
            time.sleep(delay)


def parse_attachments(attachment_str: Optional[str]) -> List[Path]:
    if not attachment_str:
        return []
    paths = [Path(path.strip()) for path in attachment_str.split(",") if path.strip()]
    return paths


def main() -> None:
    args = parse_args()

    recipients = read_recipients(Path(args.recipients))
    template = load_template(Path(args.template))
    attachments = parse_attachments(args.attachments)

    for recipient in recipients:
        message = build_message(args.sender, recipient, args.subject, template, attachments)
        try:
            send_email(
                message,
                args.smtp_host,
                args.smtp_port,
                args.smtp_user,
                args.smtp_password,
                args.max_retries,
                args.delay,
            )
            print(f"Sent email to {recipient.email}")
        except Exception as exc:
            print(f"ERROR sending to {recipient.email}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
