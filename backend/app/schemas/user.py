"""Pydantic schemas for User model.

Schemas define:
1. What data the API accepts (request validation)
2. What data the API returns (response serialization)
3. Validation rules (email format, password strength, etc.)

Why separate from SQLAlchemy models?
- Models = database structure
- Schemas = API contracts
- They can evolve independently!
"""

from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# Base schema (common fields)
class UserBase(BaseModel):
    """Shared properties across User schemas."""

    email: EmailStr
    name: Optional[str] = None
    role: str = "reviewer"


# Schema for creating a user (POST /users)
class UserCreate(UserBase):
    """Schema for user registration.

    Requires:
    - email (validated format)
    - password (plain text - will be hashed before storing)
    - name (optional)
    - role (defaults to "reviewer")

    Example:
        {
            "email": "reviewer@company.com",
            "password": "SecurePassword123!",
            "name": "Jane Doe"
        }
    """

    password: str = Field(
        ..., min_length=8, description="Password (min 8 characters)"
    )


# Schema for updating a user (PATCH /users/{id})
class UserUpdate(BaseModel):
    """Schema for updating user (all fields optional).

    Example:
        {
            "name": "Jane Smith",
            "role": "admin"
        }
    """

    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


# Schema for returning user data (GET /users, GET /users/{id})
class UserResponse(UserBase):
    """Schema for user in API responses.

    Note: We don't include hashed_password!
    Never expose password hashes in API responses.

    Example:
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "reviewer@company.com",
            "name": "Jane Doe",
            "role": "reviewer",
            "is_active": true,
            "created_at": "2024-01-15T10:30:00Z"
        }
    """

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True  # Allow creating from ORM models
        # Before Pydantic v2 this was: orm_mode = True


# Schema for user in JWT token payload
class UserInToken(BaseModel):
    """Minimal user data stored in JWT token.

    Keep JWT tokens small!
    """

    id: UUID
    email: str
    role: str
