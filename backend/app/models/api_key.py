"""API Key model for agent authentication.

Agents use API keys to authenticate when creating consultation requests.

Security best practices:
- Store only hashed keys (like passwords)
- Generate keys with high entropy (use secrets module)
- Allow key rotation (multiple keys per agent)
- Support key revocation (is_active flag)
"""

from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin


class APIKey(Base, TimestampMixin):
    """API Key for agent authentication.

    Security model:
    1. Generate random key with secrets.token_urlsafe(32)
    2. Show key to user ONCE (they must save it)
    3. Store only SHA256 hash in database
    4. On auth: hash incoming key, compare with stored hash

    This means:
    - If database is compromised, keys can't be recovered
    - Lost keys can't be recovered (must rotate)
    - Same security model as passwords

    Attributes:
        id: Primary key
        key_hash: SHA256 hash of the API key
        name: Human-readable name (e.g., "code-review-agent")
        description: Optional description
        is_active: Soft delete / revocation flag

    Example:
        # Generate new API key
        import secrets
        import hashlib

        # Generate random key (show this to user ONCE)
        raw_key = secrets.token_urlsafe(32)  # ~43 chars
        print(f"API Key (save this!): {raw_key}")

        # Hash for storage
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        # Save to database
        api_key = APIKey(
            key_hash=key_hash,
            name="code-review-agent",
            description="Agent that reviews code changes"
        )

        # Later, to verify:
        incoming_hash = hashlib.sha256(incoming_key.encode()).hexdigest()
        db_key = db.query(APIKey).filter(
            APIKey.key_hash == incoming_hash,
            APIKey.is_active == True
        ).first()

        if db_key:
            # Valid key
            pass
    """

    __tablename__ = "api_keys"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, nullable=False
    )

    # Key (hashed with SHA256)
    key_hash: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )

    # Identification
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Revocation
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps from TimestampMixin:
    # - created_at (when key was created)
    # - updated_at (when key was last modified, e.g., revoked)

    def __repr__(self) -> str:
        """String representation for debugging."""
        # Never log the actual key!
        return f"<APIKey(id={self.id}, name={self.name}, is_active={self.is_active})>"
