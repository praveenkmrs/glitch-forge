"""Consultation Request model.

Represents a request from an external agent for human consultation.

Lifecycle:
1. Agent creates request → state = "pending"
2. Human responds → state = "responded"
3. Webhook called successfully → state = "callback_sent"
4. Workflow complete → state = "completed"

If webhook fails after retries → state = "callback_failed"
If request times out → state = "timeout"
"""

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin


class ConsultationRequest(Base, TimestampMixin):
    """Consultation request from an agent.

    State Machine:
        pending → responded → callback_sent → completed
                            ↓
                        callback_failed
        pending → timeout (if no response within SLA)

    Attributes:
        id: Primary key
        title: Short description (shown in UI list)
        description: Longer description (optional)
        context: JSON blob with all context from agent (flexible schema)

        callback_webhook: URL to call when human responds
        callback_secret: Shared secret for HMAC signature

        state: Current state in lifecycle

        response: JSON blob with human's response
        responded_by: User ID who responded (foreign key)
        responded_at: When response was submitted

        callback_sent_at: When webhook was successfully called
        timeout_at: When this request times out (if not responded)

        metadata: Extra data from agent (workflow_id, checkpoint_id, etc.)

    Relationships:
        responder: The User who responded to this request
        webhook_deliveries: Audit log of webhook attempts

    Example:
        # Agent creates request
        request = ConsultationRequest(
            title="Review High-Risk Code Changes",
            description="Complaint #42 requires DB schema changes",
            context={
                "code_diff": "...",
                "risk_level": "high",
                "affected_files": ["users.py"]
            },
            callback_webhook="https://agent-system.com/resume",
            callback_secret="shared-secret",
            metadata={
                "workflow_id": "wf-abc123",
                "checkpoint_id": "cp-xyz789",
                "agent_id": "code-review-agent"
            }
        )
    """

    __tablename__ = "consultation_requests"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, nullable=False
    )

    # Request Details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Context from agent (flexible JSON)
    # Could contain: code_diff, risk_assessment, metrics, etc.
    context: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Callback Configuration
    callback_webhook: Mapped[Optional[str]] = mapped_column(
        String(2048), nullable=True
    )
    callback_secret: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    # State Machine
    state: Mapped[str] = mapped_column(
        String(50), default="pending", index=True, nullable=False
    )
    # States: pending, responded, callback_sent, completed, callback_failed, timeout

    # Response
    response: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    responded_by: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    responded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Callback Tracking
    callback_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Timeout
    timeout_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    # Metadata (workflow_id, checkpoint_id, agent_id, etc.)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps from TimestampMixin:
    # - created_at (indexed automatically for listing queries)
    # - updated_at

    # Relationships
    responder: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[responded_by]
    )

    webhook_deliveries: Mapped[list["WebhookDelivery"]] = relationship(
        "WebhookDelivery", back_populates="request"
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<ConsultationRequest(id={self.id}, title={self.title}, state={self.state})>"
