import smtplib
import time
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Dict, Optional
from string import Template
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailAutomation:
    """Email automation with HTML templates, attachments, and retry logic."""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
        max_retries: int = 3,
        retry_delay: int = 5
    ):
        """
        Initialize email automation.

        Args:
            smtp_server: SMTP server address (e.g., 'smtp.gmail.com')
            smtp_port: SMTP port (587 for TLS, 465 for SSL)
            sender_email: Sender's email address
            sender_password: Sender's email password or app password
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def load_html_template(self, template_path: str) -> Template:
        """Load HTML template from file."""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            return Template(template_content)
        except FileNotFoundError:
            logger.error(f"Template file not found: {template_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading template: {e}")
            raise

    def create_email(
        self,
        recipient_email: str,
        subject: str,
        html_body: str,
        plain_text_body: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> MIMEMultipart:
        """
        Create email message with HTML body and attachments.

        Args:
            recipient_email: Recipient's email address
            subject: Email subject
            html_body: HTML content of the email
            plain_text_body: Plain text alternative (optional)
            attachments: List of file paths to attach

        Returns:
            MIMEMultipart message object
        """
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Add plain text version (fallback)
        if plain_text_body:
            plain_part = MIMEText(plain_text_body, 'plain')
            msg.attach(plain_part)

        # Add HTML version
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)

        # Add attachments if provided
        if attachments:
            for file_path in attachments:
                self._attach_file(msg, file_path)

        return msg

    def _attach_file(self, msg: MIMEMultipart, file_path: str):
        """Attach a file to the email message."""
        try:
            file_path_obj = Path(file_path)

            if not file_path_obj.exists():
                logger.warning(f"Attachment not found: {file_path}")
                return

            # Read file in binary mode
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())

            # Encode file in base64
            encoders.encode_base64(part)

            # Add header with filename
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {file_path_obj.name}'
            )

            msg.attach(part)
            logger.info(f"Attached file: {file_path_obj.name}")

        except Exception as e:
            logger.error(f"Error attaching file {file_path}: {e}")
            raise

    def send_email(
        self,
        recipient_email: str,
        subject: str,
        html_body: str,
        plain_text_body: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Send email with retry logic.

        Returns:
            True if email sent successfully, False otherwise
        """
        msg = self.create_email(
            recipient_email,
            subject,
            html_body,
            plain_text_body,
            attachments
        )

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Attempt {attempt}/{self.max_retries} - Sending email to {recipient_email}")

                # Connect to SMTP server
                if self.smtp_port == 465:
                    # SSL connection
                    server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
                else:
                    # TLS connection
                    server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                    server.starttls()

                # Login
                server.login(self.sender_email, self.sender_password)

                # Send email
                server.send_message(msg)
                server.quit()

                logger.info(f"Email sent successfully to {recipient_email}")
                return True

            except smtplib.SMTPAuthenticationError:
                logger.error("SMTP Authentication failed. Check credentials.")
                return False

            except smtplib.SMTPException as e:
                logger.error(f"SMTP error on attempt {attempt}: {e}")
                if attempt < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to send email to {recipient_email} after {self.max_retries} attempts")
                    return False

            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt}: {e}")
                if attempt < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to send email to {recipient_email} after {self.max_retries} attempts")
                    return False

        return False

    def send_bulk_emails(
        self,
        recipients_data: List[Dict],
        template_path: str,
        subject_template: str,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """
        Send personalized emails to multiple recipients.

        Args:
            recipients_data: List of dicts with recipient info and template variables
                Example: [
                    {
                        'email': 'user@example.com',
                        'name': 'John Doe',
                        'company': 'ABC Corp',
                        ...
                    }
                ]
            template_path: Path to HTML template file
            subject_template: Subject line with variables (e.g., "Hello $name")
            attachments: List of file paths to attach to all emails

        Returns:
            Dictionary with success/failure counts
        """
        html_template = self.load_html_template(template_path)
        subject_tmpl = Template(subject_template)

        results = {'success': 0, 'failed': 0}

        for recipient_data in recipients_data:
            try:
                # Personalize subject and body
                subject = subject_tmpl.safe_substitute(**recipient_data)
                html_body = html_template.safe_substitute(**recipient_data)

                # Send email
                success = self.send_email(
                    recipient_email=recipient_data['email'],
                    subject=subject,
                    html_body=html_body,
                    attachments=attachments
                )

                if success:
                    results['success'] += 1
                else:
                    results['failed'] += 1

                # Small delay to avoid overwhelming the server
                time.sleep(1)

            except KeyError as e:
                logger.error(f"Missing required field in recipient data: {e}")
                results['failed'] += 1
            except Exception as e:
                logger.error(f"Error processing recipient {recipient_data.get('email', 'unknown')}: {e}")
                results['failed'] += 1

        logger.info(f"Bulk email complete - Success: {results['success']}, Failed: {results['failed']}")
        return results


def main():
    """Example usage of the EmailAutomation class."""

    # Configuration (use environment variables or config file in production)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "your-email@gmail.com"
    SENDER_PASSWORD = "your-app-password"  # Use app-specific password for Gmail

    # Initialize email automation
    email_bot = EmailAutomation(
        smtp_server=SMTP_SERVER,
        smtp_port=SMTP_PORT,
        sender_email=SENDER_EMAIL,
        sender_password=SENDER_PASSWORD,
        max_retries=3,
        retry_delay=5
    )

    # Example 1: Send single email with attachment
    print("=== Example 1: Single Email ===")
    success = email_bot.send_email(
        recipient_email="recipient@example.com",
        subject="Test Email with Attachment",
        html_body="""
        <html>
            <body>
                <h2>Hello!</h2>
                <p>This is a <strong>test email</strong> with HTML formatting.</p>
                <ul>
                    <li>Feature 1</li>
                    <li>Feature 2</li>
                    <li>Feature 3</li>
                </ul>
            </body>
        </html>
        """,
        plain_text_body="Hello! This is a test email.",
        attachments=["document.pdf", "image.jpg"]  # Add your file paths
    )
    print(f"Single email sent: {success}\n")

    # Example 2: Bulk personalized emails
    print("=== Example 2: Bulk Personalized Emails ===")

    # Sample recipients data
    recipients = [
        {
            'email': 'john@example.com',
            'name': 'John Doe',
            'company': 'ABC Corp',
            'product': 'Premium Plan'
        },
        {
            'email': 'jane@example.com',
            'name': 'Jane Smith',
            'company': 'XYZ Inc',
            'product': 'Basic Plan'
        }
    ]

    # Create template file (or use existing one)
    template_content = """
    <html>
        <body>
            <h2>Hello $name!</h2>
            <p>Thank you for your interest in our services at <strong>$company</strong>.</p>
            <p>We're excited to offer you our <em>$product</em>.</p>
            <p>Best regards,<br>The Team</p>
        </body>
    </html>
    """

    with open('email_template.html', 'w', encoding='utf-8') as f:
        f.write(template_content)

    # Send bulk emails
    results = email_bot.send_bulk_emails(
        recipients_data=recipients,
        template_path='email_template.html',
        subject_template='Hello $name - Special Offer for $company',
        attachments=['brochure.pdf']  # Optional attachments
    )

    print(f"Bulk email results: {results}")


if __name__ == "__main__":
    main()
