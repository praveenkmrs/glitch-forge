"""
Abstract base class for email providers.

This allows swapping email providers (Resend, SendGrid, etc.) without changing application code.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class EmailMessage:
    """Email message data structure."""

    to: str | List[str]
    subject: str
    html: str
    from_email: Optional[str] = None
    reply_to: Optional[str] = None


class EmailProvider(ABC):
    """Abstract base class for email providers."""

    @abstractmethod
    async def send_email(self, message: EmailMessage) -> bool:
        """
        Send an email.

        Args:
            message: EmailMessage object with email details

        Returns:
            True if email sent successfully, False otherwise

        Raises:
            Exception: If email sending fails critically
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider name (e.g., 'resend', 'sendgrid')."""
        pass
