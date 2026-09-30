# Email Automation Script

This script sends personalized HTML emails with optional attachments using `smtplib` and Python's `email` package. It reads recipients from a CSV, merges template variables, and includes retry logic for transient failures.

## Prerequisites

- SMTP server credentials that allow TLS connections.
- A CSV file with headers `email`, `name`, and any other fields referenced in your template.
- An HTML template file using `${variable}` placeholders.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # (empty because only stdlib is used)
```

## Usage

```bash
python send_emails.py \
  --smtp-host smtp.example.com \
  --smtp-port 587 \
  --smtp-user your_username \
  --smtp-password your_password \
  --sender you@example.com \
  --subject "Hello" \
  --recipients recipients.csv \
  --template template.html \
  --attachments path/to/file1.pdf,path/to/file2.png
```

Optional flags:
- `--max-retries`: Retry attempts per recipient (default `3`).
- `--delay`: Sleep seconds between retries (default `5`).
- `--limit-pages`: None (not applicable).

The script prints a log line for each recipient indicating success or failure. Errors are written to stderr.
