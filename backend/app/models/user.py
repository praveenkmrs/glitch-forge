"""User model for human reviewers.

Represents people who log in to review and respond to consultation requests.

Security best practices:
- Never store plain text passwords (use hashed_password)
- Use bcrypt for hashing (via passlib)
- Add is_active flag for soft deletes
- Add role for future RBAC (Role-Based Access Control)
"""

from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User model for human reviewers.

    Attributes:
        id: Primary key (UUID for security - no enumeration attacks)
        email: Unique email address (used for login)
        name: Display name
        hashed_password: Bcrypt hashed password (NEVER store plain text!)
        is_active: Soft delete flag (instead of actually deleting users)
        role: User role (reviewer, admin, etc.) for future RBAC

    Relationships:
        consultation_requests: Requests this user has responded to

    Example:
        # Create a new user
        user = User(
            email="reviewer@company.com",
            name="Jane Doe",
            hashed_password=hash_password("secret"),  # Use passlib
            role="reviewer"
        )
        db.add(user)
        db.commit()
    """

    __tablename__ = "users"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, nullable=False
    )

    # Authentication
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Authorization
    role: Mapped[str] = mapped_column(
        String(50), default="reviewer", nullable=False
    )

    # Soft Delete
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps come from TimestampMixin:
    # - created_at
    # - updated_at

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
