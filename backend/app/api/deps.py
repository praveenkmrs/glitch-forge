"""API dependencies for FastAPI routes.

Provides reusable dependencies for:
- Database sessions
- User authentication (JWT)
- API key authentication (for agents)
"""

from typing import Generator, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import verify_token, hash_api_key
from app.db.session import SessionLocal
from app.models import User, APIKey

# Security scheme for Swagger UI
security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """Get database session.

    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token.

    Usage:
        @app.get("/me")
        def read_current_user(user: User = Depends(get_current_user)):
            return {"email": user.email}

    Raises:
        HTTPException 401: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise credentials_exception

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_uuid).first()
    if user is None or not user.is_active:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (additional check).

    Usage:
        @app.get("/admin")
        def admin_only(user: User = Depends(get_current_active_user)):
            if user.role != "admin":
                raise HTTPException(403)
            return {"message": "Admin access"}
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def verify_api_key_dependency(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> APIKey:
    """Verify API key from Authorization header.

    Usage:
        @app.post("/api/v1/requests")
        def create_request(
            api_key: APIKey = Depends(verify_api_key_dependency),
            db: Session = Depends(get_db)
        ):
            # api_key.name shows which agent made the request
            return {"message": f"Request from {api_key.name}"}

    Expects header:
        Authorization: Bearer <api_key>

    Raises:
        HTTPException 401: If API key is invalid or inactive
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract key from "Bearer <key>"
    try:
        scheme, key = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use: Bearer <api_key>",
        )

    # Hash the provided key and look up in database
    key_hash = hash_api_key(key)
    api_key = db.query(APIKey).filter(
        APIKey.key_hash == key_hash,
        APIKey.is_active == True
    ).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
        )

    return api_key
