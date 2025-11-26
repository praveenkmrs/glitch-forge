"""API key management endpoints.

Allows admins to:
- Create API keys for agents
- List API keys
- Revoke API keys
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.security import generate_api_key, hash_api_key
from app.models import User, APIKey
from app.schemas import APIKeyCreate, APIKeyCreated, APIKeyResponse, APIKeyUpdate

router = APIRouter()


@router.post("/", response_model=APIKeyCreated, status_code=201)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new API key.

    Requires admin role (you can adjust this).

    Example:
        POST /api/v1/api-keys
        Authorization: Bearer <jwt_token>

        {
            "name": "code-review-agent",
            "description": "Agent that reviews code changes"
        }

    Returns:
        {
            "id": "...",
            "key": "hKj8sH3nX...",  # RAW KEY - SHOWN ONCE!
            "name": "code-review-agent",
            "created_at": "..."
        }
    """
    # Optional: Check if user is admin
    # if current_user.role != "admin":
    #     raise HTTPException(status_code=403, detail="Admin access required")

    # Generate raw key
    raw_key = generate_api_key()

    # Hash for storage
    key_hash = hash_api_key(raw_key)

    # Create API key
    db_key = APIKey(
        key_hash=key_hash,
        name=key_data.name,
        description=key_data.description,
    )

    db.add(db_key)
    db.commit()
    db.refresh(db_key)

    # Return raw key ONCE
    return {
        "id": db_key.id,
        "key": raw_key,  # IMPORTANT: This is the only time the raw key is shown!
        "name": db_key.name,
        "description": db_key.description,
        "created_at": db_key.created_at,
    }


@router.get("/", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all API keys (without raw keys).

    Example:
        GET /api/v1/api-keys
        Authorization: Bearer <jwt_token>
    """
    keys = db.query(APIKey).order_by(APIKey.created_at.desc()).all()
    return keys


@router.get("/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific API key.

    Example:
        GET /api/v1/api-keys/550e8400-...
        Authorization: Bearer <jwt_token>
    """
    key = db.query(APIKey).filter(APIKey.id == key_id).first()

    if not key:
        raise HTTPException(status_code=404, detail="API key not found")

    return key


@router.patch("/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    key_id: UUID,
    key_data: APIKeyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an API key (typically to revoke).

    Example:
        PATCH /api/v1/api-keys/550e8400-...
        Authorization: Bearer <jwt_token>

        {
            "is_active": false  # Revoke the key
        }
    """
    key = db.query(APIKey).filter(APIKey.id == key_id).first()

    if not key:
        raise HTTPException(status_code=404, detail="API key not found")

    # Update fields
    if key_data.name is not None:
        key.name = key_data.name
    if key_data.description is not None:
        key.description = key_data.description
    if key_data.is_active is not None:
        key.is_active = key_data.is_active

    db.commit()
    db.refresh(key)

    return key
