"""Pydantic schemas for WebhookDelivery model.

Mostly used for monitoring/debugging endpoints.
"""

from uuid import UUID
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field


# Base schema
class WebhookDeliveryBase(BaseModel):
    """Shared properties."""

    webhook_url: str
    payload: dict[str, Any]


# Schema for creating a delivery log (internal use)
class WebhookDeliveryCreate(WebhookDeliveryBase):
    """Schema for logging a webhook delivery attempt."""

    request_id: UUID
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0


# Schema for returning delivery data (GET /api/v1/webhook-deliveries/{id})
class WebhookDeliveryResponse(WebhookDeliveryBase):
    """Schema for webhook delivery in API responses.

    Example:
        {
            "id": "...",
            "request_id": "...",
            "webhook_url": "https://agent-system.com/resume",
            "payload": {...},
            "status_code": 200,
            "response_body": "{\"status\": \"received\"}",
            "error": null,
            "retry_count": 0,
            "created_at": "2024-01-15T11:00:00Z"
        }
    """

    id: UUID
    request_id: UUID
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    error: Optional[str] = None
    retry_count: int
    created_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True
