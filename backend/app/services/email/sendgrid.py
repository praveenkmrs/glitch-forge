"""
SendGrid email provider implementation.

SendGrid is a widely-used email delivery platform with robust features.
API Docs: https://docs.sendgrid.com/api-reference/mail-send/mail-send
"""

import httpx
from typing import Optional
import logging

from .base import EmailProvider, EmailMessage

logger = logging.getLogger(__name__)


class SendGridEmailProvider(EmailProvider):
    """Email provider using SendGrid API."""

    def __init__(self, api_key: str, from_email: str):
        """
        Initialize SendGrid provider.

        Args:
            api_key: SendGrid API key (starts with 'SG.')
            from_email: Default sender email address
        """
        self.api_key = api_key
        self.from_email = from_email
        self.api_url = "https://api.sendgrid.com/v3/mail/send"

    async def send_email(self, message: EmailMessage) -> bool:
        """
        Send email via SendGrid API.

        Example payload:
        {
            "personalizations": [
                {
                    "to": [{"email": "user@example.com"}]
                }
            ],
            "from": {"email": "noreply@yourdomain.com"},
            "subject": "New Consultation Request",
            "content": [
                {
                    "type": "text/html",
                    "value": "<p>Hello!</p>"
                }
            ]
        }
        """
        try:
            # Prepare recipients list
            recipients = message.to if isinstance(message.to, list) else [message.to]
            to_list = [{"email": email} for email in recipients]

            # Build payload (SendGrid format)
            payload = {
                "personalizations": [{"to": to_list}],
                "from": {"email": message.from_email or self.from_email},
                "subject": message.subject,
                "content": [{"type": "text/html", "value": message.html}],
            }

            if message.reply_to:
                payload["reply_to"] = {"email": message.reply_to}

            # Send request to SendGrid API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=10.0,
                )

                if response.status_code == 202:  # SendGrid returns 202 Accepted
                    logger.info(
                        f"Email sent successfully via SendGrid to {recipients}",
                        extra={"message_id": response.headers.get("X-Message-Id")},
                    )
                    return True
                else:
                    logger.error(
                        f"SendGrid API error: {response.status_code} - {response.text}",
                        extra={"to": recipients, "subject": message.subject},
                    )
                    return False

        except Exception as e:
            logger.exception(
                f"Failed to send email via SendGrid: {str(e)}",
                extra={"to": message.to, "subject": message.subject},
            )
            return False

    def get_provider_name(self) -> str:
        return "sendgrid"
