"""API v1 router.

Combines all v1 endpoints:
- /auth - Authentication (register, login)
- /requests - Consultation requests
- /api-keys - API key management
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, requests, api_keys

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(requests.router, prefix="/requests", tags=["Consultation Requests"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["API Keys"])
