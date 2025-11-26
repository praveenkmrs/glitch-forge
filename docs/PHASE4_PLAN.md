# Phase 4 Plan: Production Readiness & Enhancements

## Overview

Phase 4 focuses on making the HITL service production-ready with key enhancements for usability and reliability.

---

## 1. Frontend Enhancements

### 1.1 Navigation Header with Logout ⏳

**Goal:** Add persistent navigation with user menu and logout functionality

**Implementation:**
```typescript
// frontend/src/components/Navigation.tsx
- Header component with logo and user menu
- Logout button that clears token and redirects to login
- Current user display (name, email)
- Active page indicator
- Mobile-responsive hamburger menu
```

**Files to Create/Modify:**
- `frontend/src/components/Navigation.tsx` (new)
- `frontend/src/App.tsx` (add Navigation to layout)
- `frontend/src/context/AuthContext.tsx` (ensure logout clears state)

**Acceptance Criteria:**
- [ ] Navigation header appears on all protected pages
- [ ] Logout button clears localStorage token
- [ ] Logout redirects to /login
- [ ] User info displayed in header
- [ ] Mobile-responsive design

---

### 1.2 Polling for Real-Time Updates ⏳

**Goal:** Implement differential polling to refresh dashboard without full page reload

**Approach:**
1. **Polling Strategy:**
   - Poll every 10 seconds when on dashboard
   - Stop polling when navigating away
   - Use `If-Modified-Since` or timestamp-based differential queries

2. **Differential Polling:**
   ```typescript
   // Only fetch requests updated after last poll
   GET /api/v1/requests?updated_after=2024-01-01T12:00:00Z
   ```

3. **Implementation:**
   ```typescript
   // Custom hook: usePolling
   - Interval-based polling (10s default)
   - Cleanup on unmount
   - Pause when tab not visible (Page Visibility API)
   - Show "New requests available" banner when updates detected
   ```

**Files to Create/Modify:**
- `frontend/src/hooks/usePolling.ts` (new)
- `frontend/src/pages/Dashboard.tsx` (integrate polling)
- `backend/app/api/v1/endpoints/requests.py` (add updated_after filter)

**Acceptance Criteria:**
- [ ] Dashboard polls every 10 seconds
- [ ] Polling stops when navigating away
- [ ] Only fetches changed requests (differential)
- [ ] Shows update notification when new data arrives
- [ ] Pauses polling when tab inactive

---

## 2. Backend Enhancements

### 2.1 Abstract Email Notification System ⏳

**Goal:** Create pluggable email notification system with Resend as default provider

**Architecture:**

```python
# Abstract base class
class EmailProvider(ABC):
    @abstractmethod
    async def send_email(self, to: str, subject: str, html: str) -> bool:
        pass

# Resend implementation
class ResendEmailProvider(EmailProvider):
    async def send_email(self, to: str, subject: str, html: str) -> bool:
        # Resend API call
        pass

# SendGrid implementation (alternative)
class SendGridEmailProvider(EmailProvider):
    async def send_email(self, to: str, subject: str, html: str) -> bool:
        # SendGrid API call
        pass

# Factory pattern for provider selection
def get_email_provider() -> EmailProvider:
    provider_type = settings.EMAIL_PROVIDER  # "resend" or "sendgrid"
    if provider_type == "resend":
        return ResendEmailProvider(api_key=settings.RESEND_API_KEY)
    elif provider_type == "sendgrid":
        return SendGridEmailProvider(api_key=settings.SENDGRID_API_KEY)
    else:
        raise ValueError(f"Unknown email provider: {provider_type}")
```

**Email Templates:**
1. **New Request Notification** - Sent to all active reviewers when request created
2. **Request Responded** - Confirmation to reviewer after submitting response
3. **Request Timeout** - Alert when request times out without response

**Files to Create:**
- `backend/app/services/email/base.py` (abstract base)
- `backend/app/services/email/resend.py` (Resend implementation)
- `backend/app/services/email/sendgrid.py` (SendGrid implementation)
- `backend/app/services/email/factory.py` (provider factory)
- `backend/app/services/email/templates.py` (email templates)
- `backend/app/core/config.py` (add email settings)

**Environment Variables:**
```bash
EMAIL_PROVIDER=resend  # or "sendgrid"
RESEND_API_KEY=re_xxxxx
RESEND_FROM_EMAIL=noreply@yourdomain.com
SENDGRID_API_KEY=SG.xxxxx
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
```

**Acceptance Criteria:**
- [ ] Abstract EmailProvider interface defined
- [ ] Resend provider implemented and working
- [ ] SendGrid provider implemented (fallback)
- [ ] Provider switchable via environment variable
- [ ] Email sent when new request created
- [ ] Email templates are HTML-formatted and mobile-friendly
- [ ] Error handling for failed email sends

---

### 2.2 Timeout Monitoring Background Job ⏳

**Goal:** Background worker that monitors request timeouts and triggers callbacks

**Implementation:**

```python
# backend/app/workers/timeout_monitor.py
import asyncio
from datetime import datetime, timedelta

async def timeout_monitor_worker():
    """
    Background job that runs every 60 seconds to check for timed-out requests.
    """
    while True:
        try:
            db = SessionLocal()

            # Find requests that:
            # 1. State = "pending" or "responded"
            # 2. Created + timeout_minutes < now
            # 3. State != "timeout"

            cutoff_time = datetime.utcnow()
            timed_out_requests = db.query(ConsultationRequest).filter(
                ConsultationRequest.state.in_(["pending", "responded"]),
                ConsultationRequest.created_at +
                    func.make_interval(mins=ConsultationRequest.timeout_minutes) < cutoff_time
            ).all()

            for request in timed_out_requests:
                # Update state to "timeout"
                request.state = "timeout"

                # Call timeout webhook if configured
                if request.callback_webhook:
                    await call_timeout_webhook(request)

                # Send email notification
                await send_timeout_notification(request)

            db.commit()

        except Exception as e:
            logger.error(f"Timeout monitor error: {e}")
        finally:
            db.close()

        # Wait 60 seconds before next check
        await asyncio.sleep(60)
```

**Integration:**
```python
# backend/app/main.py
@app.on_event("startup")
async def startup_event():
    # Start timeout monitor in background
    asyncio.create_task(timeout_monitor_worker())
```

**Files to Create/Modify:**
- `backend/app/workers/__init__.py` (new)
- `backend/app/workers/timeout_monitor.py` (new)
- `backend/app/main.py` (start worker on startup)
- `backend/app/api/v1/endpoints/requests.py` (add timeout webhook logic)

**Acceptance Criteria:**
- [ ] Worker runs in background on app startup
- [ ] Checks for timeouts every 60 seconds
- [ ] Updates request state to "timeout"
- [ ] Calls timeout webhook with appropriate payload
- [ ] Sends timeout notification email
- [ ] Handles errors gracefully without crashing
- [ ] Logs all timeout events

---

## 3. Production Readiness

### 3.1 End-to-End Tests ⏳

**Goal:** Playwright tests for critical user flows

**Test Scenarios:**
1. **Authentication Flow**
   - Register new user
   - Login with credentials
   - Access protected page
   - Logout

2. **Request Review Flow**
   - Login as reviewer
   - View dashboard
   - Filter by state
   - Open request detail
   - Submit response (approve)
   - Verify webhook called

3. **API Key Management Flow**
   - Login as admin
   - Create API key
   - Verify raw key shown
   - List keys
   - Revoke key

**Files to Create:**
- `frontend/tests/e2e/auth.spec.ts` (new)
- `frontend/tests/e2e/request-flow.spec.ts` (new)
- `frontend/tests/e2e/admin.spec.ts` (new)
- `frontend/playwright.config.ts` (new)

**Setup:**
```bash
npm install -D @playwright/test
npx playwright install
```

**Acceptance Criteria:**
- [ ] All 3 test suites pass
- [ ] Tests run in CI/CD pipeline
- [ ] Tests use test database (not production)
- [ ] Tests clean up after themselves

---

### 3.2 Security Audit & Hardening ⏳

**Checklist:**

1. **Authentication Security**
   - [ ] JWT secret is strong (32+ chars)
   - [ ] Token expiration configured (30 min default)
   - [ ] Password hashing uses bcrypt with proper rounds
   - [ ] API keys hashed with SHA256
   - [ ] No credentials in logs

2. **Input Validation**
   - [ ] All endpoints use Pydantic validation
   - [ ] SQL injection prevention (using ORM)
   - [ ] XSS prevention in frontend
   - [ ] CSRF protection for state-changing operations

3. **CORS Configuration**
   - [ ] Only allow specific origins in production
   - [ ] No wildcard (*) in production CORS

4. **Rate Limiting**
   - [ ] Add rate limiting to login endpoint
   - [ ] Add rate limiting to request creation

5. **HTTPS**
   - [ ] Force HTTPS in production
   - [ ] HSTS headers configured

6. **Dependency Security**
   - [ ] Run `npm audit` and fix vulnerabilities
   - [ ] Run `pip-audit` and fix vulnerabilities

**Files to Modify:**
- `backend/app/core/config.py` (production settings)
- `backend/app/main.py` (add security middleware)
- `docker-compose.prod.yml` (HTTPS configuration)

---

### 3.3 Performance Optimization ⏳

**Tasks:**

1. **Database Optimization**
   - [ ] Add indexes for frequently queried columns
   - [ ] Optimize N+1 queries (use joinedload)
   - [ ] Add connection pooling settings

2. **API Response Time**
   - [ ] Add caching for user lookups
   - [ ] Optimize request list endpoint (pagination working)
   - [ ] Add response compression (gzip)

3. **Frontend Optimization**
   - [ ] Code splitting (React.lazy)
   - [ ] Optimize bundle size
   - [ ] Add loading skeletons
   - [ ] Lazy load JSON context viewer

4. **Monitoring**
   - [ ] Add request timing logs
   - [ ] Track webhook success rate
   - [ ] Monitor database query times

**Files to Modify:**
- `backend/app/db/session.py` (connection pooling)
- `backend/app/api/v1/endpoints/requests.py` (query optimization)
- `frontend/src/App.tsx` (code splitting)

---

### 3.4 CI/CD Pipeline ⏳

**Goal:** Automated testing and deployment

**GitHub Actions Workflow:**

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app tests/
      - name: Run linters
        run: |
          cd backend
          ruff check app/
          black --check app/
          mypy app/

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run tests
        run: |
          cd frontend
          npm run test
      - name: Run linters
        run: |
          cd frontend
          npm run lint
      - name: Type check
        run: |
          cd frontend
          npm run type-check

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    steps:
      - uses: actions/checkout@v3
      - name: Start services
        run: docker-compose up -d
      - name: Run migrations
        run: docker exec glitch-forge-backend alembic upgrade head
      - name: Run E2E tests
        run: |
          cd frontend
          npm ci
          npx playwright test
```

**Files to Create:**
- `.github/workflows/ci.yml` (new)
- `.github/workflows/deploy.yml` (new, for production deployment)

**Acceptance Criteria:**
- [ ] CI runs on every PR
- [ ] All tests must pass before merge
- [ ] Linters enforce code quality
- [ ] Deployment to staging on merge to develop
- [ ] Manual approval for production deployment

---

## Implementation Order

**Week 1: Core Enhancements**
1. ✅ Navigation header with logout (2 hours)
2. ✅ Polling for dashboard updates (3 hours)
3. ✅ Abstract email notification system (4 hours)
4. ✅ Timeout monitoring worker (3 hours)

**Week 2: Production Readiness**
5. ✅ E2E tests (4 hours)
6. ✅ Security audit (3 hours)
7. ✅ Performance optimization (3 hours)
8. ✅ CI/CD pipeline (2 hours)

---

## Success Metrics

**Phase 4 Complete When:**
- [ ] Users can logout via UI button
- [ ] Dashboard auto-updates via polling
- [ ] Email notifications sent for new requests
- [ ] Timed-out requests automatically handled
- [ ] E2E tests pass consistently
- [ ] Security audit findings resolved
- [ ] Page load time < 2 seconds
- [ ] CI/CD pipeline operational

---

## Out of Scope (Deferred)

- ❌ Request creation form in UI (use REST client instead)
- ❌ Slack integration
- ❌ WebSocket real-time updates (using polling instead)
- ❌ Multi-factor authentication
- ❌ Advanced analytics dashboard

---

## Questions to Resolve

1. **Email Provider:** Resend or SendGrid as default?
   - Decision: Start with Resend (simpler API, better for transactional emails)

2. **Polling Interval:** 10 seconds or 30 seconds?
   - Decision: 10 seconds for better UX, with pause when tab inactive

3. **Timeout Action:** What should happen when request times out?
   - Decision: Update state to "timeout", call webhook, send email

4. **E2E Test Environment:** Separate test database or mock APIs?
   - Decision: Use Docker test environment with isolated test database

---

**Ready to begin Phase 4 implementation!** 🚀
