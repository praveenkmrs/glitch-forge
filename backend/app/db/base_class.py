"""Base class for SQLAlchemy models.

This module provides the base declarative class that all models inherit from.

Key Concepts:
- Declarative Base: SQLAlchemy pattern for defining models as Python classes
- Mixins: Reusable functionality shared across models
"""

from typing import Any

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from datetime import datetime


class Base(DeclarativeBase):
    """Base class for all database models.

    Provides:
    - Automatic table name generation
    - Common columns (id, created_at, updated_at)
    - Helper methods
    """

    # Generate __tablename__ automatically from class name
    # Example: UserModel -> user_model
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        # Convert CamelCase to snake_case
        import re

        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", cls.__name__)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

    def dict(self) -> dict[str, Any]:
        """Convert model to dictionary.

        Useful for:
        - Debugging
        - Serialization
        - Logging
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps.

    Usage:
        class MyModel(Base, TimestampMixin):
            pass

    This automatically adds:
    - created_at: Set once when record is created
    - updated_at: Updated every time record is modified
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
