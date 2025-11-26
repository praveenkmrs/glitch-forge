# Getting Started with Glitch Forge

This guide will walk you through setting up the HITL application for development.

## Prerequisites

- **Docker** and **Docker Compose** (recommended)
- OR:
  - **Python 3.11+** for backend
  - **Node.js 20+** for frontend
  - **PostgreSQL 16+**
  - **Redis 7+**

## Quick Start with Docker (Recommended)

### 1. Clone and Navigate

```bash
cd glitch-forge
```

### 2. Create Environment Files

Backend:
```bash
cd backend
cp .env.example .env
# Edit .env if needed (defaults work for Docker)
cd ..
```

Frontend:
```bash
cd frontend
cp .env.example .env
# Edit .env if needed (defaults work for Docker)
cd ..
```

### 3. Start Everything

```bash
docker-compose up
```

This will start:
- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **Backend API** on port 8000
- **Frontend** on port 3000

### 4. Verify Setup

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Manual Setup (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Setup environment
cp .env.example .env

# Edit .env to point to your local PostgreSQL and Redis
# DATABASE_URL=postgresql://user:password@localhost:5432/hitl_db
# REDIS_URL=redis://localhost:6379/0

# Run migrations (when we add them)
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env

# Start development server
npm run dev
```

## Development Workflow

### Making Changes

1. **Backend changes**: Auto-reload enabled (uvicorn --reload)
2. **Frontend changes**: Hot Module Replacement (HMR) enabled

### Running Tests

Backend:
```bash
cd backend
pytest
pytest --cov=app  # With coverage
```

Frontend:
```bash
cd frontend
npm test
npm run test:coverage
```

### Code Quality

Backend:
```bash
cd backend
black .           # Format
ruff check .      # Lint
mypy app/         # Type check
```

Frontend:
```bash
cd frontend
npm run format    # Format
npm run lint      # Lint
npm run type-check  # Type check
```

## Project Structure Overview

```
glitch-forge/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/          # HTTP routes
│   │   ├── core/         # Config, security
│   │   ├── models/       # Database models
│   │   ├── schemas/      # API schemas
│   │   ├── services/     # Business logic
│   │   └── tests/        # Tests
│   └── Dockerfile
│
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── pages/       # Pages
│   │   ├── hooks/       # Custom hooks
│   │   ├── services/    # API client
│   │   └── tests/       # Tests
│   └── Dockerfile
│
├── docker-compose.yml    # Dev environment
└── docs/                 # Documentation
```

## Next Steps

Now that your environment is set up, you can:

1. **Design the database schema** for HITL entities
2. **Implement authentication** with JWT
3. **Build API endpoints** for agent consultations
4. **Create UI components** for the frontend
5. **Add real-time features** with WebSockets (optional)

## Troubleshooting

### Docker Issues

**Containers won't start:**
```bash
docker-compose down -v  # Remove volumes
docker-compose up --build  # Rebuild
```

**Port already in use:**
```bash
# Change ports in docker-compose.yml
# Or stop conflicting services
```

### Backend Issues

**Import errors:**
```bash
# Ensure you're in virtual environment
which python  # Should point to venv
pip install -r requirements-dev.txt
```

**Database connection failed:**
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Check firewall settings

### Frontend Issues

**Module not found:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Port 3000 in use:**
```bash
# Change port in package.json
"dev": "vite --port 3001"
```

## Getting Help

- Check the README files in `backend/` and `frontend/`
- Review code comments (extensively documented)
- Check GitHub issues
- Review logs: `docker-compose logs -f [service]`

## Development Tips

1. **Use the API docs**: http://localhost:8000/docs
2. **Hot reload**: Changes reflect automatically
3. **Test as you go**: Write tests alongside features
4. **Mobile-first**: Always check mobile view
5. **Type safety**: Let TypeScript catch bugs early

Happy coding! 🚀
