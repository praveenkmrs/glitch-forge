"""Consultation request endpoints.

Core API for the HITL service:
- Agents create requests
- Humans list and view requests
- Humans submit responses
- System calls webhooks
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, verify_api_key_dependency
from app.models import ConsultationRequest, User, APIKey, WebhookDelivery
from app.schemas import (
    ConsultationRequestCreate,
    ConsultationRequestResponse,
    ConsultationRequestList,
    HumanResponse,
)
from app.core.security import create_webhook_signature

router = APIRouter()


@router.post("/", response_model=ConsultationRequestResponse, status_code=201)
async def create_request(
    request_data: ConsultationRequestCreate,
    background_tasks: BackgroundTasks,
    api_key: APIKey = Depends(verify_api_key_dependency),
    db: Session = Depends(get_db),
):
    """Create a consultation request (agents only).

    Requires API key authentication.

    Example request:
        POST /api/v1/requests
        Authorization: Bearer <api_key>

        {
            "title": "Review High-Risk Code Changes",
            "description": "Complaint #42 requires DB changes",
            "context": {
                "code_diff": "...",
                "risk_level": "high"
            },
            "callback_webhook": "https://agent-system.com/resume",
            "callback_secret": "shared-secret",
            "timeout_minutes": 1440,
            "metadata": {
                "workflow_id": "wf-123",
                "checkpoint_id": "cp-456"
            }
        }
    """
    # Calculate timeout
    timeout_at = None
    if request_data.timeout_minutes:
        timeout_at = datetime.utcnow() + timedelta(minutes=request_data.timeout_minutes)

    # Create request
    db_request = ConsultationRequest(
        title=request_data.title,
        description=request_data.description,
        context=request_data.context,
        callback_webhook=str(request_data.callback_webhook) if request_data.callback_webhook else None,
        callback_secret=request_data.callback_secret,
        state="pending",
        timeout_at=timeout_at,
        metadata=request_data.metadata or {},
    )

    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    # TODO: Send notification to humans (email, Slack, etc.)
    # background_tasks.add_task(send_notification, db_request.id)

    return db_request


@router.get("/", response_model=ConsultationRequestList)
async def list_requests(
    state: Optional[str] = Query(None, description="Filter by state (pending, responded, etc.)"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List consultation requests (humans only).

    Requires JWT authentication.

    Example:
        GET /api/v1/requests?state=pending&limit=20&offset=0
        Authorization: Bearer <jwt_token>
    """
    query = db.query(ConsultationRequest)

    # Filter by state if provided
    if state:
        query = query.filter(ConsultationRequest.state == state)

    # Get total count
    total = query.count()

    # Get paginated results
    requests = query.order_by(ConsultationRequest.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "items": requests,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{request_id}", response_model=ConsultationRequestResponse)
async def get_request(
    request_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific consultation request (humans only).

    Example:
        GET /api/v1/requests/550e8400-e29b-41d4-a716-446655440000
        Authorization: Bearer <jwt_token>
    """
    request = db.query(ConsultationRequest).filter(ConsultationRequest.id == request_id).first()

    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    return request


@router.post("/{request_id}/respond", response_model=ConsultationRequestResponse)
async def respond_to_request(
    request_id: UUID,
    response: HumanResponse,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit a response to a consultation request (humans only).

    Example:
        POST /api/v1/requests/550e8400.../respond
        Authorization: Bearer <jwt_token>

        {
            "decision": "approve",
            "comment": "Looks good!"
        }

    Side effects:
    - Updates request state to "responded"
    - Calls webhook asynchronously
    """
    request = db.query(ConsultationRequest).filter(ConsultationRequest.id == request_id).first()

    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.state != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Request is already {request.state}, cannot respond"
        )

    # Update request with response
    request.response = {
        "decision": response.decision,
        "comment": response.comment,
        "responder_id": str(current_user.id),
        "responded_at": datetime.utcnow().isoformat(),
    }
    request.responded_by = current_user.id
    request.responded_at = datetime.utcnow()
    request.state = "responded"

    db.commit()
    db.refresh(request)

    # Call webhook in background
    if request.callback_webhook:
        background_tasks.add_task(call_agent_webhook, request.id, db)

    return request


async def call_agent_webhook(request_id: UUID, db: Session):
    """Background task to call agent's webhook.

    Retries up to 3 times with exponential backoff.
    """
    import httpx
    import asyncio

    request = db.query(ConsultationRequest).filter(ConsultationRequest.id == request_id).first()
    if not request or not request.callback_webhook:
        return

    # Build payload
    payload = {
        "event": "request.responded",
        "request_id": str(request.id),
        "metadata": request.metadata or {},
        "response": request.response,
    }

    # Create signature if secret provided
    headers = {"Content-Type": "application/json"}
    if request.callback_secret:
        signature = create_webhook_signature(payload, request.callback_secret)
        headers["X-Webhook-Signature"] = signature

    # Retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    request.callback_webhook,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()

                # Log successful delivery
                delivery = WebhookDelivery(
                    request_id=request.id,
                    webhook_url=request.callback_webhook,
                    payload=payload,
                    status_code=response.status_code,
                    response_body=response.text[:1000],  # Limit size
                    retry_count=attempt,
                )
                db.add(delivery)

                # Update request state
                request.state = "callback_sent"
                request.callback_sent_at = datetime.utcnow()
                db.commit()

                return  # Success!

        except Exception as e:
            error_msg = str(e)

            # Log failed delivery
            delivery = WebhookDelivery(
                request_id=request.id,
                webhook_url=request.callback_webhook,
                payload=payload,
                status_code=None,
                error=error_msg[:1000],
                retry_count=attempt,
            )
            db.add(delivery)
            db.commit()

            if attempt < max_retries - 1:
                # Exponential backoff: 2s, 4s, 8s
                await asyncio.sleep(2 ** attempt)
            else:
                # Final failure
                request.state = "callback_failed"
                db.commit()
