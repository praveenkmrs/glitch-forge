"""Security utilities for authentication and authorization.

Provides:
1. Password hashing/verification (bcrypt)
2. JWT token creation/validation
3. API key hashing/verification
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Example:
        hashed = hash_password("MySecurePassword123")
        # Returns: $2b$12$... (60 chars)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Example:
        is_valid = verify_password("MySecurePassword123", hashed)
        # Returns: True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.

    Args:
        data: Payload to encode in the token (user_id, email, etc.)
        expires_delta: How long until token expires

    Returns:
        Encoded JWT token string

    Example:
        token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=timedelta(minutes=30)
        )
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict[str, Any]]:
    """Verify and decode a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload if valid, None if invalid

    Example:
        payload = verify_token(token)
        if payload:
            user_id = payload.get("sub")
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_api_key() -> str:
    """Generate a secure random API key.

    Returns:
        URL-safe random string (~43 characters)

    Example:
        key = generate_api_key()
        # Returns: "hKj8sH3nX92lP4mN6vB1qW0zR5tY7u..."
        # SHOW THIS TO USER ONCE!
    """
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage.

    Args:
        api_key: Raw API key string

    Returns:
        SHA256 hex digest (64 characters)

    Example:
        key_hash = hash_api_key(raw_key)
        # Store key_hash in database
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, key_hash: str) -> bool:
    """Verify an API key against its hash.

    Args:
        api_key: Raw API key from request
        key_hash: Stored hash from database

    Returns:
        True if key matches hash

    Example:
        is_valid = verify_api_key(incoming_key, stored_hash)
    """
    return hash_api_key(api_key) == key_hash


def create_webhook_signature(payload: dict[str, Any], secret: str) -> str:
    """Create HMAC signature for webhook payload.

    Args:
        payload: JSON payload to sign
        secret: Shared secret with agent

    Returns:
        Signature string in format "sha256=<hex>"

    Example:
        signature = create_webhook_signature(payload, secret)
        # Returns: "sha256=abcdef123456..."
        # Include in X-Webhook-Signature header
    """
    import json
    import hmac

    payload_bytes = json.dumps(payload, separators=(',', ':')).encode()
    signature = hmac.new(
        secret.encode(),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()

    return f"sha256={signature}"


def verify_webhook_signature(payload: dict[str, Any], signature: str, secret: str) -> bool:
    """Verify webhook signature.

    Args:
        payload: JSON payload
        signature: Signature from X-Webhook-Signature header
        secret: Shared secret

    Returns:
        True if signature is valid

    Example:
        is_valid = verify_webhook_signature(payload, request_signature, secret)
    """
    import hmac

    expected_signature = create_webhook_signature(payload, secret)
    return hmac.compare_digest(signature, expected_signature)
