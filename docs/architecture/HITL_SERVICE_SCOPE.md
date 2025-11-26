# HITL Service - Simplified Scope

## What We're Building

**A REST API + Web UI for human consultation requests.**

Agents (external systems) call our API to request human input. Humans review via web UI and respond. We callback the agent with the response.

---

## System Boundary

### ✅ In Scope (What We Build)

1. **REST API**
   - POST /api/v1/requests - Agents create consultation requests
   - GET /api/v1/requests - List requests (for humans)
   - GET /api/v1/requests/{id} - Get request details
   - POST /api/v1/requests/{id}/respond - Humans submit responses

2. **Web UI** (React Frontend)
   - Login page
   - Dashboard showing pending requests
   - Request detail view (show context, code diffs, etc.)
   - Response form (approve/reject + comments)
   - Request history

3. **Database**
   - Store consultation requests
   - Store human responses
   - Track state (pending → responded → callback_sent)

4. **Webhook Callbacks**
   - When human responds, call agent's callback URL
   - Include HMAC signature for security
   - Retry on failure

5. **Authentication**
   - JWT auth for human users
   - API key auth for agents

6. **Optional:**
   - Email notifications when new request arrives
   - Slack notifications

### ❌ Out of Scope (Not Our Problem)

- ❌ Agent framework
- ❌ Event bus (Kafka/Redis Streams)
- ❌ Workflow orchestration
- ❌ Agent code
- ❌ Checkpoint management (agents handle this)
- ❌ Complex state machines

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     External Agent System                    │
│  (Not our code - agent handles its own state management)     │
└────────────────┬─────────────────────────────┬──────────────┘
                 │                             │
                 │ 1. Create Request           │ 4. Webhook Callback
                 │ POST /api/v1/requests       │ POST {callback_url}/resume
                 │                             │
                 ▼                             │
┌────────────────────────────────────────────────────────────────┐
│                     HITL Service (Our Code)                     │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Backend API (FastAPI)                                     │ │
│  │  - Receive requests from agents                            │ │
│  │  - Store in database                                       │ │
│  │  - Serve data to frontend                                  │ │
│  │  - Receive responses from humans                           │ │
│  │  - Call agent webhooks                                     │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Database (PostgreSQL)                                     │ │
│  │  - consultation_requests                                   │ │
│  │  - users (human reviewers)                                 │ │
│  │  - webhook_deliveries (audit log)                          │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              ▲                                  │
│                              │                                  │
│                    2. Fetch Requests                            │
│                    3. Submit Response                           │
│                              │                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Frontend (React)                                          │ │
│  │  - Login                                                   │ │
│  │  - View pending requests                                   │ │
│  │  - Submit approve/reject + comments                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Request Lifecycle

```
1. Agent → HITL API
   POST /api/v1/requests
   {
     "title": "Review Code Changes",
     "context": {...},
     "callback_webhook": "https://agent/resume"
   }

   → State: "pending"

2. HITL stores in database
   → Optional: Send email/Slack notification to human

3. Human logs in to web UI
   → Sees pending request
   → Reviews context
   → Submits decision:
     POST /api/v1/requests/{id}/respond
     { "decision": "approve", "comment": "LGTM" }

   → State: "responded"

4. HITL calls agent webhook
   POST https://agent/resume
   X-Webhook-Signature: sha256=...
   {
     "request_id": "...",
     "response": {
       "decision": "approve",
       "comment": "LGTM"
     }
   }

   → State: "callback_sent"

5. Done!
```

---

## Database Schema (Simplified)

```sql
-- Human users (reviewers)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Consultation requests
CREATE TABLE consultation_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Request details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    context JSONB NOT NULL,  -- Flexible - agents send whatever they need

    -- Callback
    callback_webhook VARCHAR(2048),  -- Where to send response
    callback_secret VARCHAR(255),    -- For HMAC signature

    -- State
    state VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- States: pending → responded → callback_sent

    -- Response
    response JSONB,
    responded_by UUID REFERENCES users(id),
    responded_at TIMESTAMP,

    -- Metadata
    metadata JSONB,  -- Extra data from agent

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    callback_sent_at TIMESTAMP,

    INDEX idx_state (state),
    INDEX idx_created (created_at DESC)
);

-- Webhook delivery log (for debugging)
CREATE TABLE webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID REFERENCES consultation_requests(id),
    webhook_url VARCHAR(2048) NOT NULL,
    payload JSONB NOT NULL,
    status_code INTEGER,
    response_body TEXT,
    error TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- API keys for agents
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),  -- e.g., "code-review-agent"
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Specification

### 1. Create Request (Agent → HITL)

```http
POST /api/v1/requests
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "title": "Review High-Risk Code Changes",
  "description": "Complaint #42 requires database schema changes",
  "context": {
    "code_diff": "...",
    "risk_level": "high",
    "affected_files": ["users.py", "schema.sql"]
  },
  "callback_webhook": "https://agent-system.com/resume",
  "callback_secret": "shared-secret-for-hmac",
  "metadata": {
    "agent_id": "code-review-agent",
    "workflow_id": "wf-abc123",
    "checkpoint_id": "cp-xyz789"
  }
}

Response 201:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Review High-Risk Code Changes",
  "state": "pending",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 2. List Requests (Human → HITL)

```http
GET /api/v1/requests?state=pending&limit=20&offset=0
Authorization: Bearer {jwt_token}

Response 200:
{
  "items": [
    {
      "id": "...",
      "title": "Review High-Risk Code Changes",
      "description": "...",
      "state": "pending",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

### 3. Get Request Details (Human → HITL)

```http
GET /api/v1/requests/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer {jwt_token}

Response 200:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Review High-Risk Code Changes",
  "description": "Complaint #42 requires database schema changes",
  "context": {
    "code_diff": "...",
    "risk_level": "high",
    "affected_files": ["users.py", "schema.sql"]
  },
  "state": "pending",
  "created_at": "2024-01-15T10:30:00Z",
  "response": null,
  "responded_at": null
}
```

### 4. Submit Response (Human → HITL)

```http
POST /api/v1/requests/550e8400-e29b-41d4-a716-446655440000/respond
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "decision": "approve",  // approve | reject | request_changes
  "comment": "Looks good, but add error handling for X"
}

Response 200:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "state": "responded",
  "response": {
    "decision": "approve",
    "comment": "Looks good, but add error handling for X",
    "responded_by": "user-uuid",
    "responded_at": "2024-01-15T11:00:00Z"
  }
}

Side Effect:
- Asynchronously calls callback_webhook with response
- Updates state to "callback_sent" after success
```

### 5. Webhook Callback (HITL → Agent)

```http
POST https://agent-system.com/resume
X-Webhook-Signature: sha256=abcdef123456...
Content-Type: application/json

{
  "event": "request.responded",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "metadata": {
    "agent_id": "code-review-agent",
    "workflow_id": "wf-abc123",
    "checkpoint_id": "cp-xyz789"
  },
  "response": {
    "decision": "approve",
    "comment": "Looks good, but add error handling for X",
    "responded_by": "user-uuid",
    "responded_at": "2024-01-15T11:00:00Z"
  }
}

Agent Expected Response:
200 OK
{ "status": "received" }

Signature Calculation:
signature = HMAC-SHA256(callback_secret, request_body)
X-Webhook-Signature = "sha256=" + hex(signature)
```

---

## Frontend Pages

### 1. Login Page
- Email + password
- Returns JWT token
- Store in localStorage

### 2. Dashboard
- List of pending requests (table or cards)
- Columns: Title, Created, State
- Click to view details

### 3. Request Detail Page
- Show full context (formatted nicely)
- Code diff viewer (if present)
- Response form:
  - Radio buttons: Approve / Reject / Request Changes
  - Text area for comments
  - Submit button

### 4. History Page (Optional)
- Show all requests (pending + responded)
- Filter by state

---

## Implementation Plan

### Phase 1: Database & Models (1-2 days)
- [ ] Create Alembic migration for tables
- [ ] Create SQLAlchemy models
- [ ] Create Pydantic schemas

### Phase 2: Backend API (2-3 days)
- [ ] POST /api/v1/requests (create)
- [ ] GET /api/v1/requests (list with pagination)
- [ ] GET /api/v1/requests/{id} (get details)
- [ ] POST /api/v1/requests/{id}/respond
- [ ] Webhook callback logic with HMAC
- [ ] API key authentication
- [ ] JWT authentication

### Phase 3: Frontend (3-4 days)
- [ ] Login page
- [ ] Dashboard (request list)
- [ ] Request detail page
- [ ] Response form
- [ ] API client (axios/fetch)
- [ ] Auth state management (Zustand)

### Phase 4: Testing (1-2 days)
- [ ] Backend unit tests
- [ ] API integration tests
- [ ] Frontend component tests
- [ ] Manual end-to-end test with mock agent

### Phase 5: Polish (1-2 days)
- [ ] Error handling
- [ ] Loading states
- [ ] Validation
- [ ] Documentation
- [ ] Docker production builds

**Total: ~2 weeks for MVP**

---

## What We Already Have

✅ FastAPI backend setup
✅ PostgreSQL database
✅ React frontend setup
✅ Docker Compose
✅ Type safety
✅ Testing infrastructure

**We just need to:**
1. Define the database schema
2. Build the API endpoints
3. Build the frontend UI
4. Add webhook logic

---

## Next Steps

**Want me to:**
1. **Create the database models** (SQLAlchemy + Alembic migration)?
2. **Build the API endpoints** (start with POST /api/v1/requests)?
3. **Design the frontend UI** (mockup first)?

Which would you like to tackle first?
