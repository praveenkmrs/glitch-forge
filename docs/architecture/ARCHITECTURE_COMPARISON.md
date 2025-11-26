# Architecture Comparison: Original vs Event-Driven

## What We Built (v1.0)

**Traditional REST API:**
```
Frontend (React) ←─HTTP─→ Backend (FastAPI) ←─→ Database (PostgreSQL)
                                                   Cache (Redis)
```

**Request Flow:**
1. User opens frontend
2. Frontend calls GET /api/v1/consultations
3. Backend queries database
4. Returns list of consultations
5. User clicks "Respond"
6. Frontend calls POST /api/v1/consultations/{id}/respond
7. Backend updates database
8. Returns success

**Characteristics:**
- ✅ Synchronous
- ✅ Simple request/response
- ✅ Stateless
- ❌ No agent integration
- ❌ No workflow orchestration
- ❌ No pause/resume capability

---

## What You Actually Need (v2.0)

**Event-Driven Architecture with Workflow Orchestration:**
```
┌─────────────────────────────────────────────────────────────────┐
│                         Event Bus                                │
│                    (Redis Streams / Kafka)                       │
└────────┬────────────────────┬───────────────────┬───────────────┘
         │                    │                   │
         ▼                    ▼                   ▼
    ┌─────────┐          ┌─────────┐        ┌──────────┐
    │ Agent 1 │          │ Agent 2 │        │ Agent 3  │
    │  (Code  │          │  (Test) │        │(Deploy)  │
    │ Review) │          │         │        │          │
    └────┬────┘          └────┬────┘        └────┬─────┘
         │                    │                   │
         │ Needs human        │                   │
         │ input              │                   │
         ▼                    │                   │
    ┌────────────────────────────────────────────────┐
    │          HITL Service (REST API)               │
    │  - Receives request                            │
    │  - Stores checkpoint                           │
    │  - Notifies human                              │
    │  - Receives response                           │
    │  - Calls webhook to resume agent               │
    └────────────────┬───────────────────────────────┘
                     │
                     │ Webhook callback
                     ▼
    ┌────────────────────────────────────────┐
    │      Agent Webhook Handler             │
    │  - Loads checkpoint                    │
    │  - Resumes workflow                    │
    │  - Continues from where it left off    │
    └────────────────────────────────────────┘
```

**Request Flow:**
1. Agent publishes event: "code.analysis.needed"
2. CodeReviewAgent subscribes, processes
3. Detects high-risk changes
4. **Saves checkpoint** (workflow state)
5. **Calls HITL API**: POST /api/v1/requests
6. **Agent yields control** (stops processing)
7. HITL service sends notification to human
8. Human reviews via web UI
9. Human submits decision
10. **HITL calls webhook**: POST {agent}/resume
11. **Agent loads checkpoint**
12. **Agent resumes** from exact state
13. Agent publishes next event: "code.approved"
14. Next agent in pipeline takes over

**Characteristics:**
- ✅ Asynchronous
- ✅ Event-driven
- ✅ Workflow orchestration
- ✅ Pause/resume capability
- ✅ Durable state
- ✅ Scalable
- ✅ Resilient

---

## Key Differences

| Aspect | v1.0 (Current) | v2.0 (Needed) |
|--------|----------------|---------------|
| **Communication** | HTTP REST | Events + REST |
| **State** | Stateless | Stateful (checkpoints) |
| **Flow** | Synchronous | Asynchronous |
| **Actors** | Users only | Agents + Users |
| **Workflow** | None | Multi-step orchestration |
| **Pause/Resume** | Not supported | Core feature |
| **Callbacks** | Not needed | Essential (webhooks) |
| **Event Bus** | None | Redis Streams/Kafka |
| **Background Jobs** | None | Needed (timeouts, notifications) |
| **Idempotency** | Nice to have | Critical |

---

## What Stays the Same

✅ **FastAPI** - Perfect for async workflows
✅ **PostgreSQL** - Needed for durable checkpoints
✅ **Redis** - Will use for event bus + cache
✅ **Docker Compose** - Makes it easy to add event bus
✅ **React Frontend** - Humans still need UI to respond
✅ **Type Safety** - More important in distributed systems
✅ **Testing** - Critical for this complexity

---

## What Changes

### 1. Database Schema

**Add:**
- `workflow_checkpoints` table (agent state)
- `webhook_deliveries` table (audit trail)
- `notifications` table (tracking)
- Update `consultation_requests` to include:
  - `workflow_id`
  - `checkpoint_id`
  - `callback_webhook`
  - State machine tracking

### 2. New Components

**HITL Service (extend current):**
- Webhook callback logic
- Background job for timeouts
- Notification sending
- Idempotency checks

**Agent Framework (new):**
- Event bus abstraction
- Base Agent class
- Workflow state manager
- HITL client SDK
- Webhook receiver

### 3. Infrastructure

**Add to docker-compose.yml:**
- Redis Streams (or Kafka)
- Celery worker (background jobs)

### 4. API Changes

**Current API:**
```http
POST /api/v1/consultations
GET /api/v1/consultations
GET /api/v1/consultations/{id}
POST /api/v1/consultations/{id}/respond
```

**New API:**
```http
# From agents
POST /api/v1/requests
  → workflow_id, checkpoint_id, callback_webhook

GET /api/v1/requests/{id}
  → Include state and webhook status

# From humans (unchanged)
POST /api/v1/requests/{id}/respond

# New: Webhook callback to agent
POST {agent_callback_url}/resume
  → Signed with HMAC
  → Includes workflow_id, checkpoint_id, response
```

---

## Migration Strategy

### Phase 1: Extend Current Backend ✅ (Next)
Keep everything we built, add:
1. Update database schema
2. Add webhook callback logic
3. Add Redis Streams support
4. Implement async request/response pattern

### Phase 2: Build Agent Framework (New Repository)
Separate project for agent SDK:
1. Event bus abstraction
2. Base Agent class
3. State manager
4. HITL client

### Phase 3: Example Agents
Build proof of concept:
1. Simple agent that requests approval
2. Multi-step workflow
3. Test pause/resume

### Phase 4: Production Features
1. Notifications (email, Slack)
2. Timeout monitoring
3. Metrics and monitoring
4. Error handling

---

## Code Reusability

### 100% Reusable ✅
- All FastAPI setup
- Database connection
- Redis connection
- Docker configuration
- Testing infrastructure
- Frontend components (with minor updates)
- Authentication (when we build it)

### Needs Extension 🔧
- Database models (add new tables)
- API endpoints (add webhook support)
- Config (add event bus settings)

### New Components 🆕
- Event bus abstraction
- Agent framework
- Webhook handlers
- Background jobs

---

## Example: Before vs After

### Before (v1.0)
```python
# Simple REST endpoint
@router.post("/consultations")
async def create_consultation(
    consultation: ConsultationCreate,
    db: Session = Depends(get_db)
):
    # Create consultation in database
    db_consultation = models.Consultation(**consultation.dict())
    db.add(db_consultation)
    db.commit()

    # Return immediately
    return db_consultation
```

### After (v2.0)
```python
# Async request with callback
@router.post("/requests")
async def create_request(
    request: HITLRequest,
    db: Session = Depends(get_db),
    background: BackgroundTasks
):
    # Validate callback webhook
    if not request.callback_webhook:
        raise HTTPException(400, "callback_webhook required")

    # Create request in database
    db_request = models.ConsultationRequest(
        workflow_id=request.workflow_id,
        checkpoint_id=request.checkpoint_id,
        context=request.context,
        callback_webhook=request.callback_webhook,
        state="pending",
        timeout_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(db_request)
    db.commit()

    # Send notifications (async background job)
    background.add_task(
        send_notifications,
        request_id=db_request.id,
        routing=request.routing
    )

    # Return immediately (agent can continue other work)
    return db_request

# When human responds
@router.post("/requests/{id}/respond")
async def respond_to_request(
    id: UUID,
    response: ResponseSubmission,
    db: Session = Depends(get_db),
    background: BackgroundTasks
):
    # Update request
    db_request = db.query(models.ConsultationRequest).get(id)
    db_request.response = response.dict()
    db_request.state = "responded"
    db_request.responded_at = datetime.utcnow()
    db.commit()

    # Call agent webhook (async background job)
    background.add_task(
        call_agent_webhook,
        request=db_request
    )

    return db_request

# Background task to call webhook
async def call_agent_webhook(request: models.ConsultationRequest):
    # Build payload
    payload = {
        "event": "request.responded",
        "request_id": str(request.id),
        "metadata": {
            "workflow_id": request.workflow_id,
            "checkpoint_id": request.checkpoint_id
        },
        "response": request.response
    }

    # Sign with HMAC
    signature = create_webhook_signature(payload, request.callback_secret)

    # Call webhook with retry
    async with httpx.AsyncClient() as client:
        for attempt in range(3):
            try:
                response = await client.post(
                    request.callback_webhook,
                    json=payload,
                    headers={
                        "X-Webhook-Signature": signature,
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )
                response.raise_for_status()

                # Log successful delivery
                log_webhook_delivery(request.id, response.status_code, None)
                return

            except Exception as e:
                if attempt == 2:  # Last attempt
                    log_webhook_delivery(request.id, None, str(e))
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

---

## Summary

**Good News:**
- ✅ 80% of what we built is still useful
- ✅ FastAPI is perfect for this architecture
- ✅ We have the foundation (Docker, DB, Redis)
- ✅ Type safety and testing are critical here

**What to Add:**
- Event bus (Redis Streams)
- Webhook support
- Background jobs
- Agent framework (separate project)
- Extended database schema

**Complexity Increase:**
- From: Simple CRUD API
- To: Distributed workflow orchestration
- But: Much more powerful and scalable

**Time Estimate:**
- v1.0 foundation: 1 week (DONE!)
- v2.0 extension: 2-3 weeks
- Agent framework: 1-2 weeks
- Total: 4-6 weeks for MVP

---

## Recommendation

**Keep the v1.0 scaffolding!** It's solid. We'll extend it step-by-step:

1. **Week 1**: Update DB schema, add webhook support
2. **Week 2**: Add event bus, background jobs
3. **Week 3**: Build simple agent framework
4. **Week 4**: Build example agent, test end-to-end
5. **Week 5**: Add notifications, monitoring
6. **Week 6**: Production hardening

Sound good? Where do you want to start?
