import smtplib
import time
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# For the local debugging server
import asyncore
import smtpd
from threading import Thread

# --- Configuration ---
SMTP_HOST = "localhost"
SMTP_PORT = 1025
SENDER_EMAIL = "automation@example.com"

class DebuggingServer(smtpd.DebuggingServer):
    """A custom debugging server to close the asyncore loop."""
    def __init__(self, localaddr, remoteaddr):
        smtpd.DebuggingServer.__init__(self, localaddr, remoteaddr)
        self.is_running = True

    def handle_close(self):
        self.close()
        self.is_running = False

def run_debugging_server(server):
    """Runs the asyncore loop for the SMTP server."""
    asyncore.loop()

def send_personalized_email(recipient_email, subject, template_path, personalization_data, attachment_path=None, max_retries=3, retry_delay=5):
    """Constructs and sends a single personalized email with retry logic."""
    print(f"\nPreparing to send email to: {recipient_email}")
    
    # --- Create the email message ---
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # --- Attach HTML Body ---
    try:
        with open(template_path, 'r') as f:
            html_template = f.read()
        html_body = html_template.format(**personalization_data)
        msg.attach(MIMEText(html_body, 'html'))
    except FileNotFoundError:
        print(f"Error: HTML template not found at {template_path}")
        return False
    except KeyError as e:
        print(f"Error: Personalization key {e} not found in data.")
        return False

    # --- Attach File ---
    if attachment_path and os.path.exists(attachment_path):
        try:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(attachment_path)}",
            )
            msg.attach(part)
            print(f"Attached file: {attachment_path}")
        except Exception as e:
            print(f"Error attaching file: {e}")

    # --- Send the email with retry logic ---
    for attempt in range(max_retries):
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.send_message(msg)
            print(f"Successfully sent email to {recipient_email}")
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed for {recipient_email}: {e}")
            if attempt + 1 < max_retries:
                time.sleep(retry_delay)
    
    print(f"Failed to send email to {recipient_email} after {max_retries} attempts.")
    return False

if __name__ == "__main__":
    # --- Start Local SMTP Debugging Server ---
    print("--- Starting Local SMTP Debugging Server on port 1025 ---")
    print("Emails will be printed to the console, not sent over the internet.")
    server = DebuggingServer((SMTP_HOST, SMTP_PORT), None)
    server_thread = Thread(target=run_debugging_server, args=(server,))
    server_thread.start()

    # --- Main Automation Logic ---
    recipients = [
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob", "email": "bob@example.com"}
    ]
    
    for recipient in recipients:
        send_personalized_email(
            recipient_email=recipient['email'],
            subject="Your Weekly Report is Ready",
            template_path="email_template.html",
            personalization_data={"name": recipient['name']},
            attachment_path="attachment.txt"
        )
    
    # --- Shutdown Server ---
    print("\n--- Shutting down local SMTP server. ---")
    server.close()
    # Wait for the server thread to finish
    while server.is_running:
        time.sleep(0.1)
    print("Server shut down.")
