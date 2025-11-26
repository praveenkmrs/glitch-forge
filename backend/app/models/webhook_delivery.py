"""Webhook Delivery model.

Audit log of all webhook callback attempts.

Why track this?
- Debugging (did the webhook fire?)
- Monitoring (how many failures?)
- Compliance (audit trail)
- Retries (know how many times we tried)
"""

from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin


class WebhookDelivery(Base, TimestampMixin):
    """Webhook delivery attempt log.

    Tracks every attempt to call an agent's webhook with a response.

    Status tracking:
    - status_code = 200-299: Success
    - status_code = 4xx: Client error (agent's fault)
    - status_code = 5xx: Server error (might be transient, retry)
    - status_code = None: Network error (couldn't connect)

    Attributes:
        id: Primary key
        request_id: Which consultation request this relates to
        webhook_url: The URL we called
        payload: The JSON we sent
        status_code: HTTP status code from response (if any)
        response_body: Response from agent (for debugging)
        error: Error message if delivery failed
        retry_count: How many times we've tried this delivery

    Relationships:
        request: The ConsultationRequest this delivery is for

    Example:
        # Log successful delivery
        delivery = WebhookDelivery(
            request_id=request.id,
            webhook_url=request.callback_webhook,
            payload={"event": "request.responded", ...},
            status_code=200,
            response_body='{"status": "received"}',
            retry_count=0
        )

        # Log failed delivery
        delivery = WebhookDelivery(
            request_id=request.id,
            webhook_url=request.callback_webhook,
            payload={...},
            status_code=500,
            error="Internal Server Error",
            retry_count=2
        )
    """

    __tablename__ = "webhook_deliveries"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, nullable=False
    )

    # Foreign Key
    request_id: Mapped[UUID] = mapped_column(
        ForeignKey("consultation_requests.id"), index=True, nullable=False
    )

    # Delivery Details
    webhook_url: Mapped[str] = mapped_column(String(2048), nullable=False)

    payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Response
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Error Tracking
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamps from TimestampMixin:
    # - created_at (when this delivery was attempted)
    # - updated_at

    # Relationships
    request: Mapped["ConsultationRequest"] = relationship(
        "ConsultationRequest", back_populates="webhook_deliveries"
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<WebhookDelivery(id={self.id}, request_id={self.request_id}, status={self.status_code})>"

    @property
    def is_success(self) -> bool:
        """Check if delivery was successful."""
        return self.status_code is not None and 200 <= self.status_code < 300

    @property
    def is_retriable(self) -> bool:
        """Check if this failure is worth retrying.

        Retry on:
        - Network errors (status_code is None)
        - 5xx errors (server errors, might be transient)

        Don't retry on:
        - 4xx errors (client errors, won't fix themselves)
        """
        if self.status_code is None:
            return True  # Network error, retry
        if 500 <= self.status_code < 600:
            return True  # Server error, might be transient
        return False  # 4xx or success, don't retry
