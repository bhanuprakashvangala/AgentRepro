# Email Automation Script

This project is a Python script that automates sending personalized emails with HTML content and file attachments. 

**Important:** For safety and reproducibility, this script **does not send real emails**. It starts a local SMTP debugging server that intercepts the emails and prints their full content to the console. This allows you to verify the output without any configuration or risk.

## Features

- **Personalization**: Uses HTML templates with placeholders (e.g., `{name}`) to create personalized messages.
- **HTML Content**: Sends emails formatted with HTML for rich content.
- **File Attachments**: Attaches local files to the emails.
- **Retry Logic**: Automatically retries sending an email if a connection failure occurs.
- **Self-Contained**: Requires no external libraries and runs entirely locally.

## Usage

1.  **Set up a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    There are no external dependencies to install. The `requirements.txt` file is empty.

3.  **Run the script:**
    ```bash
    python email_sender.py
    ```

## Expected Output

When you run the script, it will first start the local debugging server. Then, for each recipient, it will prepare and "send" an email. The full content of each email, including headers, HTML body, and the encoded attachment, will be printed to your console. It will look similar to this:

```
--- Starting Local SMTP Debugging Server on port 1025 ---
Emails will be printed to the console, not sent over the internet.

Preparing to send email to: alice@example.com
Attached file: attachment.txt
Successfully sent email to alice@example.com
---------- MESSAGE FOLLOWS ----------
From: automation@example.com
To: alice@example.com
Subject: Your Weekly Report is Ready
...
Content-Type: text/html; charset="us-ascii"
Content-Transfer-Encoding: 7bit

<!DOCTYPE html>
<html>
...
</html>

--==...==--
Content-Type: application/octet-stream
...
Content-Disposition: attachment; filename= attachment.txt

VGhpcyBpcyBhIHNhbXBsZSBhdHRhY2htZW50IGZpbGUuCkl0IGNvbnRhaW5zIHNvbWUgcGxh
aW4gdGV4dCBjb250ZW50IGZvciBkZW1vbnN0cmF0aW9uIHB1cnBvc2VzLgo=

--==...==--
------------ END MESSAGE ------------

(The output for the next recipient follows...)
```
