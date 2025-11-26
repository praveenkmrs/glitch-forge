# Glitch Forge Backend

FastAPI-based backend for the HITL application.

## 🏗️ Architecture

This backend follows **Clean Architecture** principles:

```
app/
├── main.py              # Application entry point
├── core/                # Core functionality (config, security, logging)
├── api/                 # HTTP layer
│   └── v1/             # API versioning
│       └── endpoints/  # Route handlers
├── models/             # Database models (SQLAlchemy)
├── schemas/            # API contracts (Pydantic)
├── services/           # Business logic (domain layer)
├── db/                 # Database utilities
└── tests/              # Test suite
```

## 🎯 Design Decisions

### 1. **Separation of Concerns**
- **Models** (database) ≠ **Schemas** (API)
- Models can change without breaking API contracts
- API can evolve without changing database

### 2. **Dependency Injection**
- FastAPI's dependency system for clean code
- Easy to test (mock dependencies)
- Reusable components

### 3. **Type Safety**
- Pydantic for runtime validation
- mypy for static type checking
- Catch errors before production

### 4. **Testing from Start**
- pytest for testing
- TestClient for API tests
- Coverage tracking

## 🚀 Quick Start

### Local Development (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Set up environment
cp .env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### With Docker

```bash
# From project root
docker-compose up backend
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_main.py -v
```

## 📝 Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type check
mypy app/
```

## 🔒 Security Best Practices

1. **Never commit secrets** - Use `.env` files
2. **Use environment variables** - For all configuration
3. **Validate input** - Pydantic schemas validate everything
4. **Hash passwords** - Using bcrypt via passlib
5. **JWT tokens** - With expiration and refresh
6. **CORS configuration** - Explicit allowed origins
7. **Rate limiting** - TODO: Add later
8. **SQL injection prevention** - SQLAlchemy ORM handles this

## 📚 Key Libraries

| Library | Purpose | Why This One? |
|---------|---------|---------------|
| FastAPI | Web framework | Modern, fast, automatic docs |
| SQLAlchemy | ORM | Industry standard, powerful |
| Alembic | Migrations | Works with SQLAlchemy |
| Pydantic | Validation | Built into FastAPI, type-safe |
| python-jose | JWT | Well-maintained, secure |
| passlib | Password hashing | Best practices built-in |
| pytest | Testing | Most popular, great plugins |

## 🔄 Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## 📖 API Documentation

When running in development:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🐛 Debugging

```bash
# Run with debug logging
DEBUG=true uvicorn app.main:app --reload --log-level debug

# Use ipdb for debugging (install via requirements-dev.txt)
# Add to code: import ipdb; ipdb.set_trace()
```
