# How to Run the HITL Service

Complete guide to run the Human-in-the-Loop consultation service.

---

## 🚀 Quick Start (Docker - Recommended)

### Prerequisites
- Docker and Docker Compose installed
- Git

### Steps

```bash
# 1. Navigate to project
cd glitch-forge

# 2. Start all services
docker-compose up -d

# 3. Run database migration
docker exec -it glitch-forge-backend alembic upgrade head

# 4. Create test data
docker exec -it glitch-forge-backend python -m scripts.create_test_data

# 5. Open Swagger UI
open http://localhost:8000/docs

# 6. Open frontend
open http://localhost:3000
```

That's it! The service is running.

---

## 📋 Manual Setup (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Create .env file
cp .env.example .env

# Edit .env with your database credentials
# DATABASE_URL=postgresql://user:password@localhost:5432/hitl_db

# Run migrations
alembic upgrade head

# Create test data
python -m scripts.create_test_data

# Start backend
uvicorn app.main:app --reload
```

Backend running at: http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start frontend
npm run dev
```

Frontend running at: http://localhost:3000

---

## 🧪 Testing the API

### 1. Get Test Credentials

After running `create_test_data.py`, you have:

**Test User:**
- Email: `reviewer@example.com`
- Password: `password123`

**Test API Key:**
- Check the console output when running create_test_data
- It shows the raw API key (save it!)

### 2. Test Authentication (Humans)

#### Register a New User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "securepassword123",
    "name": "New User"
  }'
```

#### Login to Get JWT Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=reviewer@example.com&password=password123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

Save this token! You'll use it in `Authorization: Bearer <token>` headers.

#### Get Current User Info

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <your_jwt_token>"
```

### 3. Test API Keys (Agents)

#### Create an API Key

```bash
curl -X POST http://localhost:8000/api/v1/api-keys \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-agent",
    "description": "My test agent"
  }'
```

Response:
```json
{
  "id": "...",
  "key": "hKj8sH3nX92lP4mN6vB1qW0zR...",  # SAVE THIS!
  "name": "my-agent",
  "created_at": "..."
}
```

**IMPORTANT:** The raw key is shown ONLY ONCE! Save it.

#### List API Keys

```bash
curl http://localhost:8000/api/v1/api-keys \
  -H "Authorization: Bearer <your_jwt_token>"
```

### 4. Test Consultation Requests (Core Workflow)

#### Create a Request (Agent)

```bash
curl -X POST http://localhost:8000/api/v1/requests \
  -H "Authorization: Bearer <api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Review Code Changes",
    "description": "Need approval for database schema changes",
    "context": {
      "code_diff": "ALTER TABLE users ADD COLUMN phone VARCHAR(20);",
      "risk_level": "high"
    },
    "callback_webhook": "https://httpbin.org/post",
    "callback_secret": "my-secret",
    "timeout_minutes": 1440,
    "metadata": {
      "workflow_id": "wf-123",
      "checkpoint_id": "cp-456"
    }
  }'
```

#### List Requests (Human)

```bash
curl http://localhost:8000/api/v1/requests \
  -H "Authorization: Bearer <jwt_token>"
```

#### Get Specific Request (Human)

```bash
curl http://localhost:8000/api/v1/requests/<request_id> \
  -H "Authorization: Bearer <jwt_token>"
```

#### Respond to Request (Human)

```bash
curl -X POST http://localhost:8000/api/v1/requests/<request_id>/respond \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "approve",
    "comment": "Looks good, approved!"
  }'
```

**What happens:**
1. Request state changes to "responded"
2. Response is saved with your user ID and timestamp
3. Webhook is called asynchronously (to agent's callback_webhook)
4. Request state updates to "callback_sent"

---

## 🔍 Using Swagger UI

The easiest way to test the API is through Swagger UI:

1. Open http://localhost:8000/docs
2. Click **Authorize** button (top right)
3. For `/auth` endpoints: No auth needed for register/login
4. For `/requests` (human): Use JWT token
   - Get token from `/auth/login`
   - Click "Authorize", paste token, click "Authorize"
5. For `/requests` (agent): Use API key
   - Get key from `/api-keys` or test data
   - Click "Authorize", paste key, click "Authorize"
6. Try endpoints by clicking "Try it out"

---

## 📊 Database Access

### View Tables

```bash
# Connect to PostgreSQL
docker exec -it glitch-forge-db psql -U hitl_user -d hitl_db

# List tables
\dt

# View users
SELECT * FROM users;

# View consultation requests
SELECT id, title, state, created_at FROM consultation_requests;

# View webhook deliveries
SELECT * FROM webhook_deliveries;

# Exit
\q
```

---

## 🐛 Troubleshooting

### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'jose'`

**Fix:**
```bash
cd backend
pip install -r requirements.txt
```

### Database connection error

**Error:** `could not connect to server`

**Fix:**
```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart PostgreSQL
docker-compose restart postgres

# Check DATABASE_URL in .env
```

### Migration errors

**Error:** `Target database is not up to date`

**Fix:**
```bash
cd backend
alembic upgrade head
```

### API returns 401 Unauthorized

**Fix:**
- Check your token/API key is correct
- Check token hasn't expired (default: 30 minutes)
- Re-login to get a fresh token

### Webhook not being called

**Check:**
1. Is `callback_webhook` a valid URL?
2. Is `callback_secret` provided (optional but recommended)?
3. Check `webhook_deliveries` table for errors:
   ```sql
   SELECT * FROM webhook_deliveries ORDER BY created_at DESC LIMIT 5;
   ```

---

## 📖 API Endpoints Reference

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/register` | Register new user | None |
| POST | `/api/v1/auth/login` | Login (get JWT) | None |
| GET | `/api/v1/auth/me` | Get current user | JWT |

### Consultation Requests

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/requests` | Create request | API Key |
| GET | `/api/v1/requests` | List requests | JWT |
| GET | `/api/v1/requests/{id}` | Get request | JWT |
| POST | `/api/v1/requests/{id}/respond` | Respond | JWT |

### API Keys

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/api-keys` | Create key | JWT |
| GET | `/api/v1/api-keys` | List keys | JWT |
| GET | `/api/v1/api-keys/{id}` | Get key | JWT |
| PATCH | `/api/v1/api-keys/{id}` | Update/revoke | JWT |

---

## 🔄 Complete Workflow Example

### Scenario: Agent requests human approval for code changes

**Step 1: Agent creates request**

```bash
curl -X POST http://localhost:8000/api/v1/requests \
  -H "Authorization: Bearer <api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Deploy to Production",
    "context": {"commit": "abc123"},
    "callback_webhook": "https://agent-system.com/resume"
  }'
```

Response: `201 Created` with `request_id`

**Step 2: Human lists pending requests**

```bash
curl http://localhost:8000/api/v1/requests?state=pending \
  -H "Authorization: Bearer <jwt_token>"
```

**Step 3: Human reviews request details**

```bash
curl http://localhost:8000/api/v1/requests/<request_id> \
  -H "Authorization: Bearer <jwt_token>"
```

**Step 4: Human approves**

```bash
curl -X POST http://localhost:8000/api/v1/requests/<request_id>/respond \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "approve",
    "comment": "Looks good!"
  }'
```

**Step 5: HITL service calls webhook**

Automatically calls `https://agent-system.com/resume` with:
```json
{
  "event": "request.responded",
  "request_id": "...",
  "response": {
    "decision": "approve",
    "comment": "Looks good!",
    "responder_id": "...",
    "responded_at": "..."
  },
  "metadata": {...}
}
```

**Step 6: Agent resumes workflow**

Agent receives callback, loads checkpoint, continues execution.

---

## 🚢 Production Deployment

### Environment Variables

Required in production:

```bash
# Security (CRITICAL!)
SECRET_KEY=<strong-random-secret>  # Use: openssl rand -hex 32

# Database
DATABASE_URL=postgresql://user:password@host:5432/db

# Redis
REDIS_URL=redis://host:6379/0

# Environment
ENVIRONMENT=production
DEBUG=false

# CORS
CORS_ORIGINS=["https://yourdomain.com"]
```

### Docker Production Build

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Run in production mode
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📚 Next Steps

1. **Add Email Notifications**
   - Notify humans when new requests arrive
   - Use Resend, SendGrid, or AWS SES

2. **Add Slack Integration**
   - Post to Slack channel when requests are created
   - Allow responding via Slack

3. **Add Timeout Monitoring**
   - Background job to check for expired requests
   - Automatic timeout callbacks

4. **Add Metrics**
   - Request count, response time
   - Webhook success rate
   - Integrate Prometheus/Grafana

5. **Build Frontend UI**
   - React dashboard for humans
   - Real-time updates with WebSocket

---

## 🆘 Getting Help

- **Backend API docs**: http://localhost:8000/docs
- **Check logs**: `docker-compose logs -f backend`
- **Database issues**: Check `docker-compose logs postgres`
- **Frontend issues**: Check browser console

---

**Happy testing! 🎉**
