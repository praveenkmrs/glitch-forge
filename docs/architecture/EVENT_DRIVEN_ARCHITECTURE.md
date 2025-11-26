# Glitch Forge HITL Architecture v2.0
## Event-Driven Workflow Orchestration

Based on the requirements from the HITL protocol discussion, this document outlines the **real architecture** needed for autonomous agents to request human consultation with pause/resume capability.

---

## 🎯 Core Problem

**Autonomous agents** need to:
1. Execute multi-step workflows
2. **Pause** when human input is needed
3. **Save their state** (checkpoints)
4. **Resume** from exact checkpoint when human responds
5. Handle **timeouts** if human doesn't respond
6. Scale to **100s of concurrent workflows**

---

## 🏗️ System Components

### 1. **HITL Service** (This Repository)
**Purpose:** REST API for agents to request human consultation

**Responsibilities:**
- Accept consultation requests from agents
- Store workflow checkpoints
- Send notifications to humans (email, Slack, SMS, web)
- Receive human responses via web UI
- Call webhook to resume agent workflow
- Monitor timeouts
- Track request lifecycle

**Tech Stack:**
- FastAPI (Python 3.11+)
- PostgreSQL (durable storage)
- Redis (caching + pub/sub)
- Celery/BullMQ (background jobs)
- Resend/Twilio (notifications)

---

### 2. **Agent Framework** (Separate - To Be Built)
**Purpose:** SDK for building autonomous agents that can pause/resume

**Responsibilities:**
- Event bus abstraction (Kafka/Redis/RabbitMQ)
- Base Agent class with pause/resume
- Workflow state manager
- HITL client SDK
- Webhook handler for callbacks
- Supervisor pattern for orchestration

**Tech Stack:**
- Python 3.11+ (same as HITL service for consistency)
- aiokafka or aioredis (event bus)
- asyncpg (database)
- FastAPI (webhook receiver)

---

## 🔄 Complete Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    1. Agent Starts Workflow                          │
│                                                                       │
│  Agent: CodeReviewAgent                                               │
│  Event: "code.analysis.needed"                                        │
│  Action: Analyze code for risks                                       │
└───────────────────────────────┬───────────────────────────────────────┘
                                │
                                ▼
                        ┌───────────────┐
                        │ Risk = High?  │
                        └───────┬───────┘
                                │ YES
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                2. Agent Requests Human Input                         │
│                                                                       │
│  1. Generate checkpoint_id                                            │
│  2. Save state to database (workflow_id, checkpoint_id, state_data)   │
│  3. Call HITL Service API:                                            │
│     POST /api/v1/requests                                             │
│     {                                                                 │
│       "workflow_id": "wf-abc123",                                     │
│       "checkpoint_id": "cp-xyz789",                                   │
│       "context": {...code diff, analysis...},                         │
│       "callback_webhook": "https://agent-system/resume"               │
│     }                                                                 │
│  4. Agent yields control (stops processing)                           │
└───────────────────────────────┬───────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                3. HITL Service Processes Request                     │
│                                                                       │
│  1. Store request in database (state = "pending")                     │
│  2. Publish to notification queue                                     │
│  3. Background worker sends notifications:                            │
│     - Email to reviewer@company.com                                   │
│     - Slack message to #review-requests                               │
│     - SMS to on-call human                                            │
│  4. Update state to "notified"                                        │
│  5. Return request_id to agent                                        │
└───────────────────────────────┬───────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                4. Human Reviews (Via Web UI)                         │
│                                                                       │
│  1. Human clicks link in email/Slack                                  │
│  2. Opens HITL web UI showing:                                        │
│     - Code diff                                                       │
│     - Risk analysis                                                   │
│     - Approve/Reject buttons                                          │
│     - Comment field                                                   │
│  3. Human makes decision                                              │
│  4. POST /api/v1/requests/{id}/respond                                │
│     { "decision": "approve", "comment": "LGTM" }                      │
└───────────────────────────────┬───────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                5. HITL Service Calls Webhook                         │
│                                                                       │
│  1. Update request state to "responded"                               │
│  2. Call agent's webhook:                                             │
│     POST https://agent-system/resume                                  │
│     Headers: X-Webhook-Signature (HMAC)                               │
│     Body: {                                                           │
│       "request_id": "req-123",                                        │
│       "metadata": {                                                   │
│         "workflow_id": "wf-abc123",                                   │
│         "checkpoint_id": "cp-xyz789"                                  │
│       },                                                              │
│       "response": {                                                   │
│         "decision": "approve",                                        │
│         "comment": "LGTM",                                            │
│         "responder_id": "user-456"                                    │
│       }                                                               │
│     }                                                                 │
│  3. Update state to "callback_sent"                                   │
└───────────────────────────────┬───────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                6. Agent Resumes from Checkpoint                      │
│                                                                       │
│  1. Webhook handler receives callback                                 │
│  2. Verify HMAC signature                                             │
│  3. Check idempotency (already processed?)                            │
│  4. Load checkpoint from database                                     │
│  5. Merge human response into saved state                             │
│  6. Call agent.resume_from_checkpoint(workflow_id, state)             │
│  7. Agent continues from where it left off                            │
│  8. Delete checkpoint (cleanup)                                       │
│  9. Publish next event: "code.approved"                               │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Database Schema

### HITL Service Database

```sql
-- Consultation requests
CREATE TABLE consultation_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Workflow tracking
    workflow_id VARCHAR(255) NOT NULL,
    checkpoint_id VARCHAR(255) NOT NULL,

    -- Request details
    type VARCHAR(50) NOT NULL DEFAULT 'approval',
    title VARCHAR(255) NOT NULL,
    description TEXT,
    context JSONB NOT NULL,

    -- Routing
    routing JSONB NOT NULL,  -- {channels: [...], recipients: [...]}

    -- Callback
    callback_webhook VARCHAR(2048),
    callback_secret VARCHAR(255),

    -- State machine
    state VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- States: pending → notified → responded → callback_sent → completed

    -- Response
    response JSONB,
    responded_by UUID,

    -- Metadata
    metadata JSONB,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    notified_at TIMESTAMP,
    responded_at TIMESTAMP,
    callback_sent_at TIMESTAMP,
    completed_at TIMESTAMP,
    timeout_at TIMESTAMP,  -- When this request times out

    -- Indexes
    INDEX idx_workflow (workflow_id),
    INDEX idx_state (state),
    INDEX idx_timeout (timeout_at) WHERE state IN ('pending', 'notified'),
    INDEX idx_created (created_at DESC)
);

-- Notification log (audit trail)
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL REFERENCES consultation_requests(id),
    channel VARCHAR(50) NOT NULL,  -- email, slack, sms, web
    recipient VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,  -- sent, failed, delivered, clicked
    provider_id VARCHAR(255),  -- External ID from Resend/Twilio/etc
    error TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    INDEX idx_request (request_id),
    INDEX idx_status (status)
);

-- Webhook delivery log (for debugging)
CREATE TABLE webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL REFERENCES consultation_requests(id),
    webhook_url VARCHAR(2048) NOT NULL,
    payload JSONB NOT NULL,
    status_code INTEGER,
    response_body TEXT,
    error TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    INDEX idx_request (request_id),
    INDEX idx_created (created_at DESC)
);

-- Users (human reviewers)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'reviewer',
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    INDEX idx_email (email)
);
```

### Agent Framework Database

```sql
-- Workflow checkpoints (saved agent state)
CREATE TABLE workflow_checkpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identifiers
    workflow_id VARCHAR(255) NOT NULL,
    checkpoint_id VARCHAR(255) NOT NULL,
    agent_id VARCHAR(255) NOT NULL,

    -- Saved state
    state_data JSONB NOT NULL,
    event_history JSONB,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP,  -- Auto-cleanup old checkpoints

    -- Unique constraint
    UNIQUE(workflow_id, checkpoint_id),

    -- Indexes
    INDEX idx_workflow (workflow_id),
    INDEX idx_agent (agent_id),
    INDEX idx_expires (expires_at) WHERE expires_at IS NOT NULL
);

-- Event log (for debugging and replay)
CREATE TABLE event_log (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID NOT NULL DEFAULT gen_random_uuid(),
    topic VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    workflow_id VARCHAR(255),
    agent_id VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    INDEX idx_topic (topic),
    INDEX idx_workflow (workflow_id),
    INDEX idx_created (created_at DESC)
);
```

---

## 🔌 API Specification

### HITL Service REST API

#### Create Consultation Request
```http
POST /api/v1/requests
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "workflow_id": "wf-abc123",
  "checkpoint_id": "cp-xyz789",
  "type": "approval",  // approval, decision, clarification
  "title": "Review High-Risk Code Changes",
  "description": "Complaint #42 requires database schema changes",
  "context": {
    "code_diff": "...",
    "risk_assessment": {...},
    "affected_systems": ["payments", "user-auth"]
  },
  "routing": {
    "channels": ["email", "slack"],
    "recipients": [
      {"email": "senior-engineer@company.com"},
      {"slack_user_id": "U123456"}
    ]
  },
  "callback_webhook": "https://agent-system.company.com/resume",
  "timeout_minutes": 1440,  // 24 hours
  "metadata": {
    "agent_id": "code-review-agent",
    "priority": "high"
  }
}

Response 201:
{
  "id": "req-uuid",
  "workflow_id": "wf-abc123",
  "state": "pending",
  "created_at": "2024-01-15T10:30:00Z",
  "timeout_at": "2024-01-16T10:30:00Z"
}
```

#### Submit Response (Human Reviewer)
```http
POST /api/v1/requests/{id}/respond
Authorization: Bearer {user_token}
Content-Type: application/json

{
  "decision": "approve",  // approve, reject, request_changes
  "comment": "Looks good, but add error handling for edge case X",
  "attachments": []
}

Response 200:
{
  "id": "req-uuid",
  "state": "responded",
  "response": {
    "decision": "approve",
    "comment": "...",
    "responder_id": "user-uuid",
    "responded_at": "2024-01-15T11:00:00Z"
  }
}
```

#### Get Request Status
```http
GET /api/v1/requests/{id}
Authorization: Bearer {api_key}

Response 200:
{
  "id": "req-uuid",
  "workflow_id": "wf-abc123",
  "state": "responded",
  "context": {...},
  "response": {...},
  "created_at": "...",
  "responded_at": "..."
}
```

### Agent Webhook Endpoint (Callback)

```http
POST /resume
X-Webhook-Signature: sha256=...
Content-Type: application/json

{
  "event": "request.responded",
  "request_id": "req-uuid",
  "metadata": {
    "workflow_id": "wf-abc123",
    "checkpoint_id": "cp-xyz789",
    "agent_id": "code-review-agent"
  },
  "response": {
    "decision": "approve",
    "comment": "LGTM",
    "responder_id": "user-uuid"
  }
}

Response 200:
{
  "status": "resumed",
  "workflow_id": "wf-abc123"
}
```

---

## 🔐 Security

### 1. **API Key Authentication (Agent → HITL)**
```python
# Agent calls HITL service
headers = {
    "Authorization": f"Bearer {HITL_API_KEY}"
}
```

### 2. **Webhook Signature Verification (HITL → Agent)**
```python
# HITL service signs webhook
signature = hmac.new(
    webhook_secret.encode(),
    json.dumps(payload).encode(),
    hashlib.sha256
).hexdigest()

headers = {
    "X-Webhook-Signature": f"sha256={signature}"
}

# Agent verifies signature
def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

### 3. **JWT for Human Users**
```python
# Human logs in to web UI
# Gets JWT token
# Includes in requests to submit responses
```

---

## ⚡ Event Bus (Agent Framework)

### Event Topics

```python
# Workflow events
"workflow.started"          # Supervisor starts new workflow
"workflow.completed"        # All steps done
"workflow.failed"           # Unrecoverable error

# Analysis events
"code.analysis.needed"      # Trigger code review
"code.approved"             # Code approved (human or auto)
"code.rejected"             # Code rejected

# HITL events
"human.input.requested"     # Agent paused, waiting for human
"human.input.received"      # Human responded
"human.input.timeout"       # No response within SLA

# Deployment events
"deployment.started"
"deployment.completed"
"deployment.failed"
```

### Event Schema
```python
{
    "event_id": "evt-uuid",
    "event_type": "code.approved",
    "workflow_id": "wf-abc123",
    "timestamp": "2024-01-15T10:30:00Z",
    "data": {
        "complaint_id": "42",
        "approved_by": "user-uuid",
        "code_changes": {...}
    },
    "metadata": {
        "agent_id": "code-review-agent",
        "correlation_id": "corr-xyz"
    }
}
```

---

## 🎯 Implementation Strategy

### Phase 1: Core HITL Service (2 weeks)
- [x] Project scaffolding (DONE!)
- [ ] Update database schema (checkpoints, requests, webhooks)
- [ ] Implement request creation endpoint
- [ ] Implement response submission endpoint
- [ ] Add webhook callback logic
- [ ] Basic web UI for human reviewers

### Phase 2: Event Infrastructure (1 week)
- [ ] Add Redis Streams to Docker Compose
- [ ] Event bus abstraction layer
- [ ] Event publishing/subscribing
- [ ] Event log persistence

### Phase 3: Agent Framework (2 weeks)
- [ ] Base Agent class
- [ ] Workflow state manager
- [ ] HITL client SDK
- [ ] Webhook handler
- [ ] Example agent (CodeReviewAgent)

### Phase 4: Production Features (2 weeks)
- [ ] Notification channels (email, Slack)
- [ ] Timeout monitoring
- [ ] Dead letter queue
- [ ] Idempotency
- [ ] Retry logic
- [ ] Metrics and monitoring

### Phase 5: Supervisor Pattern (1 week)
- [ ] Supervisor agent
- [ ] Workflow orchestration
- [ ] Complex multi-step workflows

---

## 🤔 Key Decisions Needed

### 1. **Event Bus Choice**

**Option A: Redis Streams** (Recommended to start)
- ✅ Already have Redis
- ✅ Simpler to operate
- ✅ Good enough for moderate scale (1000s msgs/sec)
- ✅ Pub/Sub + persistence
- ❌ Not as battle-tested as Kafka

**Option B: Kafka**
- ✅ Industry standard
- ✅ Proven at massive scale
- ✅ Rich ecosystem
- ❌ More complex to operate
- ❌ Heavier resource usage

**Recommendation:** Start with Redis Streams, migrate to Kafka if you hit scale limits.

### 2. **Background Jobs**

**Option A: Celery**
- ✅ Python standard
- ✅ Mature, battle-tested
- ✅ Great monitoring tools
- ❌ Can be complex to configure

**Option B: BullMQ** (Node.js)
- ✅ Modern, simpler
- ✅ Built on Redis
- ❌ Would need Node.js in stack

**Option C: Custom async tasks**
- ✅ No extra dependency
- ✅ Simple for basic needs
- ❌ Reinventing the wheel

**Recommendation:** Celery for production, or custom async for MVP.

### 3. **Deployment Model**

Keep agent framework and HITL service separate:
- Different scaling needs
- Different deployment cycles
- Clear boundaries

---

## 📚 Learning Path

For you to build this, learn in order:

1. **Async Python** (asyncio, async/await)
2. **Event-driven patterns** (pub/sub, event sourcing)
3. **State machines** (request lifecycle)
4. **Webhooks** (callbacks, signatures, retries)
5. **Idempotency** (handling duplicate events)
6. **Distributed tracing** (correlation IDs, observability)

---

## ✅ What's Already Done

From your scaffolding:
- ✅ FastAPI backend (perfect!)
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ Docker Compose
- ✅ Testing infrastructure
- ✅ Type safety
- ✅ React frontend

**All of this is useful!** We just need to:
- Extend the database schema
- Add event bus
- Add webhook support
- Build agent framework

---

## 🚀 Next Steps

Want me to:
1. **Update the database schema** with checkpoint and webhook tables?
2. **Add Redis Streams** to docker-compose and create event bus abstraction?
3. **Build the consultation request API** with async callback support?
4. **Create a simple example agent** that pauses and resumes?

Which would you like to tackle first?
