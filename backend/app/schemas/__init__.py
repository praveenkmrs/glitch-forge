"""Pydantic schemas package.

All API request/response schemas are defined here.
"""

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserInToken,
)
from app.schemas.consultation_request import (
    ConsultationRequestBase,
    ConsultationRequestCreate,
    ConsultationRequestUpdate,
    ConsultationRequestResponse,
    ConsultationRequestList,
    HumanResponse,
)
from app.schemas.webhook_delivery import (
    WebhookDeliveryBase,
    WebhookDeliveryCreate,
    WebhookDeliveryResponse,
)
from app.schemas.api_key import (
    APIKeyBase,
    APIKeyCreate,
    APIKeyCreated,
    APIKeyResponse,
    APIKeyUpdate,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInToken",
    # ConsultationRequest schemas
    "ConsultationRequestBase",
    "ConsultationRequestCreate",
    "ConsultationRequestUpdate",
    "ConsultationRequestResponse",
    "ConsultationRequestList",
    "HumanResponse",
    # WebhookDelivery schemas
    "WebhookDeliveryBase",
    "WebhookDeliveryCreate",
    "WebhookDeliveryResponse",
    # APIKey schemas
    "APIKeyBase",
    "APIKeyCreate",
    "APIKeyCreated",
    "APIKeyResponse",
    "APIKeyUpdate",
]
