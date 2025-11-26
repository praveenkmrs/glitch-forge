# Glitch Forge - Human-in-the-Loop (HITL) Application

A production-ready, cloud-agnostic Human-in-the-Loop application for agent consultation and oversight.

## 🏗️ Architecture

- **Backend**: FastAPI (Python 3.11+), SQLAlchemy, PostgreSQL
- **Frontend**: React 18, TypeScript, TailwindCSS, Vite
- **Authentication**: JWT-based (OAuth2 ready)
- **Deployment**: Docker containers (cloud-agnostic)
- **Database**: PostgreSQL (works anywhere)

## 🚀 Quick Start

```bash
# Start development environment
docker-compose up

# Backend API: http://localhost:8000
# Frontend App: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

## 📁 Project Structure

```
glitch-forge/
├── backend/          # FastAPI application
├── frontend/         # React + TypeScript application
├── docker/           # Docker configurations
├── docs/             # Documentation
└── docker-compose.yml
```

## 🛠️ Development Setup

Detailed setup instructions coming soon...

## 📚 Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [API Documentation](docs/api/README.md)
- [Development Guide](docs/development.md)

## 🧪 Testing

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test
```

## 🚢 Deployment

This application is containerized and can be deployed to:
- AWS (ECS, EKS, App Runner)
- GCP (Cloud Run, GKE)
- Azure (Container Apps, AKS)
- On-premise Kubernetes
- Any Docker-compatible platform
