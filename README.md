# MedhaAlgoPilot (MAP)

Production-grade algorithmic trading platform with clean architecture.

## Architecture Overview

### Layers
1. **API Layer**: FastAPI REST + WebSocket endpoints
2. **Trading Engine**: Event-driven strategy execution
3. **Risk Engine**: Stateless rule validation
4. **Broker Integration**: Pluggable broker adapters (Dhan)

### Tech Stack
- **Backend**: Python, FastAPI, PostgreSQL, SQLAlchemy, Celery
- **Frontend**: Next.js (App Router), TypeScript, Tailwind
- **Database**: PostgreSQL
- **Broker**: Dhan API

## Project Structure

```
MAP/
├── backend/           # Python FastAPI backend
├── frontend/          # Next.js frontend
├── shared/            # Shared types/utilities
└── docker-compose.yml # Local development setup
```

## Getting Started

See individual README files in backend/ and frontend/ directories.

