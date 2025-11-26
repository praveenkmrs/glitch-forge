"""Pydantic schemas for ConsultationRequest model.

These schemas define the API contract between agents and the HITL service.
"""

from uuid import UUID
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field, HttpUrl


# Base schema
class ConsultationRequestBase(BaseModel):
    """Shared properties."""

    title: str = Field(..., max_length=255, description="Short title for the request")
    description: Optional[str] = Field(None, description="Longer description (optional)")
    context: dict[str, Any] = Field(
        ..., description="Flexible JSON context from agent"
    )
    metadata: Optional[dict[str, Any]] = Field(
        None, description="Additional metadata (workflow_id, etc.)"
    )


# Schema for creating a request (POST /api/v1/requests)
class ConsultationRequestCreate(ConsultationRequestBase):
    """Schema for agents creating consultation requests.

    Example:
        {
            "title": "Review High-Risk Code Changes",
            "description": "Complaint #42 requires database schema changes",
            "context": {
                "code_diff": "...",
                "risk_level": "high",
                "affected_files": ["users.py", "schema.sql"]
            },
            "callback_webhook": "https://agent-system.com/resume",
            "callback_secret": "shared-secret-for-hmac",
            "timeout_minutes": 1440,
            "metadata": {
                "workflow_id": "wf-abc123",
                "checkpoint_id": "cp-xyz789",
                "agent_id": "code-review-agent"
            }
        }
    """

    callback_webhook: Optional[HttpUrl] = Field(
        None, description="Webhook URL to call when human responds"
    )
    callback_secret: Optional[str] = Field(
        None,
        max_length=255,
        description="Secret for HMAC signature (recommended)",
    )
    timeout_minutes: Optional[int] = Field(
        1440,  # 24 hours default
        ge=1,
        le=10080,  # Max 1 week
        description="How long to wait for response (minutes)",
    )


# Schema for updating a request (PATCH /api/v1/requests/{id})
class ConsultationRequestUpdate(BaseModel):
    """Schema for updating a request (all fields optional)."""

    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    state: Optional[str] = Field(
        None, pattern="^(pending|responded|callback_sent|completed|callback_failed|timeout)$"
    )


# Schema for human response (POST /api/v1/requests/{id}/respond)
class HumanResponse(BaseModel):
    """Schema for human submitting a response.

    Example:
        {
            "decision": "approve",
            "comment": "Looks good, but add error handling for edge case X"
        }
    """

    decision: str = Field(
        ...,
        pattern="^(approve|reject|request_changes)$",
        description="Human's decision",
    )
    comment: Optional[str] = Field(None, description="Optional comment/feedback")


# Schema for returning request data (GET /api/v1/requests, GET /api/v1/requests/{id})
class ConsultationRequestResponse(ConsultationRequestBase):
    """Schema for consultation request in API responses.

    Example:
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Review High-Risk Code Changes",
            "description": "...",
            "context": {...},
            "state": "pending",
            "response": null,
            "responded_by": null,
            "responded_at": null,
            "created_at": "2024-01-15T10:30:00Z",
            "timeout_at": "2024-01-16T10:30:00Z",
            "metadata": {...}
        }
    """

    id: UUID
    state: str
    response: Optional[dict[str, Any]] = None
    responded_by: Optional[UUID] = None
    responded_at: Optional[datetime] = None
    callback_sent_at: Optional[datetime] = None
    timeout_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True  # Allow creating from ORM models


# Schema for list responses (GET /api/v1/requests)
class ConsultationRequestList(BaseModel):
    """Schema for paginated list of requests.

    Example:
        {
            "items": [...],
            "total": 42,
            "limit": 20,
            "offset": 0
        }
    """

    items: list[ConsultationRequestResponse]
    total: int
    limit: int
    offset: int
