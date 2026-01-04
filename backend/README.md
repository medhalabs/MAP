# Backend - MedhaAlgoPilot

## Architecture Layers

### 1. API Layer (`api/`)
- REST endpoints for strategy lifecycle, orders, trades
- WebSocket endpoints for real-time updates
- Authentication & authorization

### 2. Trading Engine (`trading_engine/`)
- Event-driven strategy execution
- Market data subscription
- Strategy state management

### 3. Risk Engine (`risk_engine/`)
- Stateless rule evaluation
- Pre-order validation
- Risk event logging

### 4. Broker Integration (`broker/`)
- Abstract broker interface
- Dhan adapter implementation
- Order execution & position management

## Database Schema

See `database/models.py` for ORM models.

## Running

### Prerequisites

Install `uv` package manager:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup

```bash
# Install dependencies using uv
uv sync

# Activate virtual environment (created by uv)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run migrations
alembic upgrade head

# Start server
uvicorn api.main:app --reload
```

### Alternative: Run without activating venv

```bash
# Run commands directly with uv
uv run uvicorn api.main:app --reload
uv run alembic upgrade head
```

