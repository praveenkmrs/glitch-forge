"""
Email provider factory.

Provides a centralized way to get the configured email provider.
"""

import logging
from typing import Optional

from app.core.config import settings
from .base import EmailProvider
from .resend import ResendEmailProvider
from .sendgrid import SendGridEmailProvider

logger = logging.getLogger(__name__)

_provider_instance: Optional[EmailProvider] = None


def get_email_provider() -> Optional[EmailProvider]:
    """
    Get the configured email provider instance.

    Returns:
        EmailProvider instance or None if email is not configured

    Raises:
        ValueError: If provider type is unknown or configuration is invalid
    """
    global _provider_instance

    # Return cached instance if available
    if _provider_instance is not None:
        return _provider_instance

    # Check if email is enabled
    if not settings.EMAIL_ENABLED:
        logger.info("Email notifications are disabled in configuration")
        return None

    provider_type = settings.EMAIL_PROVIDER.lower()

    # Create provider based on configuration
    if provider_type == "resend":
        if not settings.RESEND_API_KEY:
            raise ValueError("RESEND_API_KEY is required when EMAIL_PROVIDER='resend'")
        if not settings.RESEND_FROM_EMAIL:
            raise ValueError("RESEND_FROM_EMAIL is required when EMAIL_PROVIDER='resend'")

        logger.info("Initializing Resend email provider")
        _provider_instance = ResendEmailProvider(
            api_key=settings.RESEND_API_KEY, from_email=settings.RESEND_FROM_EMAIL
        )

    elif provider_type == "sendgrid":
        if not settings.SENDGRID_API_KEY:
            raise ValueError("SENDGRID_API_KEY is required when EMAIL_PROVIDER='sendgrid'")
        if not settings.SENDGRID_FROM_EMAIL:
            raise ValueError("SENDGRID_FROM_EMAIL is required when EMAIL_PROVIDER='sendgrid'")

        logger.info("Initializing SendGrid email provider")
        _provider_instance = SendGridEmailProvider(
            api_key=settings.SENDGRID_API_KEY, from_email=settings.SENDGRID_FROM_EMAIL
        )

    else:
        raise ValueError(
            f"Unknown email provider: {provider_type}. Supported: 'resend', 'sendgrid'"
        )

    logger.info(f"Email provider initialized: {_provider_instance.get_provider_name()}")
    return _provider_instance


async def send_notification_email(to: str | list[str], subject: str, html: str) -> bool:
    """
    Convenience function to send an email using the configured provider.

    Args:
        to: Recipient email address(es)
        subject: Email subject
        html: HTML email content

    Returns:
        True if sent successfully, False otherwise
    """
    from .base import EmailMessage

    provider = get_email_provider()

    if provider is None:
        logger.warning(f"Email notifications disabled, skipping email to {to}")
        return False

    message = EmailMessage(to=to, subject=subject, html=html)

    try:
        return await provider.send_email(message)
    except Exception as e:
        logger.exception(f"Failed to send email: {str(e)}")
        return False
