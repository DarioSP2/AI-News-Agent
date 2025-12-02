import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email(subject: str, html_content: str, recipients: list[str]) -> bool:
    """
    Sends an email using SendGrid.

    Args:
        subject (str): The subject of the email.
        html_content (str): The HTML body of the email.
        recipients (list[str]): A list of email addresses to send to.

    Returns:
        bool: True if sent successfully, False otherwise.
    """
    sender_email = os.getenv("SENDGRID_FROM_EMAIL")
    api_key = os.getenv("SENDGRID_API_KEY")

    if not sender_email:
        logger.error("SENDGRID_FROM_EMAIL is not set in environment variables.")
        return False

    if not api_key:
        logger.error("SENDGRID_API_KEY is not set in environment variables.")
        # For now, return True in development if no key is present to avoid crashing,
        # or we could enforce it. The spec says "The system must...".
        # But we might want to allow running without it in dev.
        # Let's log error and return False.
        return False

    if not recipients:
        logger.warning("No recipients provided for email.")
        return False

    message = Mail(
        from_email=sender_email,
        to_emails=recipients,
        subject=subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        logger.info(f"Email sent! Status Code: {response.status_code}")
        return str(response.status_code).startswith("2")
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False
