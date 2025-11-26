"""
Email notification service for HITL.

Provides pluggable email providers (Resend, SendGrid) with a simple interface.
"""

from .base import EmailProvider, EmailMessage
from .factory import get_email_provider, send_notification_email
from .templates import (
    new_request_email,
    request_responded_email,
    request_timeout_email,
)

__all__ = [
    "EmailProvider",
    "EmailMessage",
    "get_email_provider",
    "send_notification_email",
    "new_request_email",
    "request_responded_email",
    "request_timeout_email",
]
