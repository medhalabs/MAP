# Deployment Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- Redis (for Celery)

## Backend Setup

### 1. Install uv Package Manager

```bash
# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

### 2. Install Dependencies

```bash
cd backend

# Install dependencies and create virtual environment
uv sync

# Activate virtual environment (created by uv)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or run commands directly with uv (no activation needed)
uv run uvicorn api.main:app --reload
```

### 2. Database Setup

```bash
# Using Docker Compose
docker-compose up -d postgres

# Or manually create database
createdb map_db
```

### 3. Environment Configuration

Create `.env` file in `backend/`:

```env
DATABASE_URL=postgresql://map_user:map_password@localhost:5432/map_db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DHAN_API_BASE_URL=https://api.dhan.co
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=production
DEBUG=false
```

### 4. Initialize Database

```bash
# Run migrations (if using Alembic)
alembic upgrade head

# Or initialize directly
python -c "from database.session import init_db; init_db()"
```

### 5. Run Backend

```bash
# Development
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Production (with Gunicorn)
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Environment Configuration

Create `.env.local` file in `frontend/`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### 3. Run Frontend

```bash
# Development
npm run dev

# Production build
npm run build
npm start
```

## Docker Deployment

### Backend Dockerfile

```dockerfile
FROM python:3.10-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml .python-version ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Run with uv
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Alternative: Traditional pip-based Dockerfile

If you prefer to use pip in Docker:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM node:18-alpine

WORKDIR /app

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules

CMD ["npm", "start"]
```

## Production Considerations

### Security

1. **Secrets Management**: Use environment variables or secret management service (AWS Secrets Manager, HashiCorp Vault)
2. **HTTPS**: Always use HTTPS in production
3. **CORS**: Configure CORS properly for production domain
4. **Rate Limiting**: Add rate limiting to API endpoints
5. **Input Validation**: All inputs are validated via Pydantic schemas

### Database

1. **Backups**: Set up regular database backups
2. **Connection Pooling**: Already configured in SQLAlchemy
3. **Migrations**: Use Alembic for database migrations
4. **Monitoring**: Set up database monitoring and alerts

### Monitoring

1. **Logging**: Structured logging with structlog
2. **Metrics**: Add Prometheus metrics endpoint
3. **Error Tracking**: Integrate Sentry or similar
4. **Health Checks**: `/health` endpoint available

### Scaling

1. **Horizontal Scaling**: Stateless API can be scaled horizontally
2. **Background Tasks**: Use Celery for async tasks
3. **WebSocket**: Consider using Redis pub/sub for WebSocket scaling
4. **Database**: Use read replicas for read-heavy workloads

## Broker Integration

### Dhan API Setup

1. Register for Dhan API access
2. Get API key and secret
3. Configure in broker_accounts table
4. Test authentication before live trading

### Paper Trading

- Set `trading_mode` to `PAPER` in strategy runs
- Use paper trading API endpoints if available
- Monitor all trades in database

## Risk Management

- Configure risk rules in `risk_engine/rules.py`
- Set appropriate limits per strategy
- Monitor risk events in database
- Set up alerts for risk violations

## Testing

```bash
# Backend tests
pytest

# Frontend tests
npm test
```

## Troubleshooting

### Database Connection Issues

- Check DATABASE_URL in .env
- Verify PostgreSQL is running
- Check network connectivity

### WebSocket Connection Issues

- Verify token is valid
- Check CORS settings
- Verify WebSocket endpoint URL

### Broker API Issues

- Check API credentials
- Verify network connectivity
- Check broker API status

