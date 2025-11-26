"""
Resend email provider implementation.

Resend is a modern email API focused on developer experience and transactional emails.
API Docs: https://resend.com/docs/send-with-python
"""

import httpx
from typing import Optional
import logging

from .base import EmailProvider, EmailMessage

logger = logging.getLogger(__name__)


class ResendEmailProvider(EmailProvider):
    """Email provider using Resend API."""

    def __init__(self, api_key: str, from_email: str):
        """
        Initialize Resend provider.

        Args:
            api_key: Resend API key (starts with 're_')
            from_email: Default sender email address
        """
        self.api_key = api_key
        self.from_email = from_email
        self.api_url = "https://api.resend.com/emails"

    async def send_email(self, message: EmailMessage) -> bool:
        """
        Send email via Resend API.

        Example payload:
        {
            "from": "noreply@yourdomain.com",
            "to": ["user@example.com"],
            "subject": "New Consultation Request",
            "html": "<p>Hello!</p>"
        }
        """
        try:
            # Prepare recipients list
            recipients = message.to if isinstance(message.to, list) else [message.to]

            # Build payload
            payload = {
                "from": message.from_email or self.from_email,
                "to": recipients,
                "subject": message.subject,
                "html": message.html,
            }

            if message.reply_to:
                payload["reply_to"] = message.reply_to

            # Send request to Resend API
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

                if response.status_code == 200:
                    logger.info(
                        f"Email sent successfully via Resend to {recipients}",
                        extra={"email_id": response.json().get("id")},
                    )
                    return True
                else:
                    logger.error(
                        f"Resend API error: {response.status_code} - {response.text}",
                        extra={"to": recipients, "subject": message.subject},
                    )
                    return False

        except Exception as e:
            logger.exception(
                f"Failed to send email via Resend: {str(e)}",
                extra={"to": message.to, "subject": message.subject},
            )
            return False

    def get_provider_name(self) -> str:
        return "resend"
