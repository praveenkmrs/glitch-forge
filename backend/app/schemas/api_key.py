"""Pydantic schemas for APIKey model.

Security note: Never expose the actual API key in responses!
The raw key is shown ONLY when first created.
"""

from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Base schema
class APIKeyBase(BaseModel):
    """Shared properties."""

    name: str = Field(..., max_length=255, description="Human-readable name")
    description: Optional[str] = Field(None, max_length=512)


# Schema for creating an API key (POST /api/v1/api-keys)
class APIKeyCreate(APIKeyBase):
    """Schema for creating a new API key.

    Example:
        {
            "name": "code-review-agent",
            "description": "Agent that reviews code changes"
        }
    """

    pass


# Schema for the response when creating (shows raw key ONCE)
class APIKeyCreated(APIKeyBase):
    """Schema returned ONLY when creating a key.

    Contains the raw key - must be saved by the agent!

    Example:
        {
            "id": "...",
            "name": "code-review-agent",
            "description": "...",
            "key": "hKj8sH3nX92lP4mN6vB1qW0zR...",  # RAW KEY (shown once!)
            "created_at": "2024-01-15T10:30:00Z"
        }
    """

    id: UUID
    key: str = Field(..., description="RAW API KEY - SAVE THIS! It won't be shown again")
    created_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# Schema for returning existing API keys (GET /api/v1/api-keys, GET /api/v1/api-keys/{id})
class APIKeyResponse(APIKeyBase):
    """Schema for API key in responses (no raw key!).

    Example:
        {
            "id": "...",
            "name": "code-review-agent",
            "description": "...",
            "is_active": true,
            "created_at": "2024-01-15T10:30:00Z"
        }

    Note: The raw key is NOT included (security)
    """

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# Schema for updating an API key (PATCH /api/v1/api-keys/{id})
class APIKeyUpdate(BaseModel):
    """Schema for updating an API key (all fields optional).

    Typically used for:
    - Updating name/description
    - Revoking (is_active = False)

    Example:
        {
            "is_active": false  # Revoke the key
        }
    """

    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=512)
    is_active: Optional[bool] = None
