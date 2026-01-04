# System Architecture

## Overview

MedhaAlgoPilot (MAP) is a production-grade algorithmic trading platform built with clean architecture principles.

## Architecture Layers

### 1. API Layer (`backend/api/`)

**Responsibilities:**
- Authentication & authorization (JWT)
- REST endpoints for CRUD operations
- WebSocket endpoints for real-time updates
- Request validation via Pydantic schemas

**Key Components:**
- `api/main.py` - FastAPI application
- `api/routes/` - Route handlers
- `api/dependencies.py` - Auth dependencies

**Endpoints:**
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/strategies` - List strategies
- `POST /api/strategies` - Create strategy
- `POST /api/strategies/{id}/runs` - Start strategy run
- `GET /api/orders` - List orders
- `GET /api/trades` - List trades
- `GET /api/positions` - List positions
- `WS /api/ws/` - WebSocket for real-time updates

### 2. Trading Engine Layer (`backend/trading_engine/`)

**Responsibilities:**
- Event-driven strategy execution
- Market data subscription
- Strategy state management
- Trade intent to order conversion

**Key Components:**
- `trading_engine/engine.py` - Main trading engine
- Manages strategy lifecycle
- Processes candle close events
- Converts trade intents to orders

**Data Flow:**
1. Strategy run created via API
2. Trading engine starts strategy task
3. Subscribes to market data events
4. Strategy emits trade intents
5. Engine validates risk and creates orders
6. Orders sent to broker adapter

### 3. Risk Engine Layer (`backend/risk_engine/`)

**Responsibilities:**
- Stateless rule evaluation
- Pre-order validation
- Risk event logging

**Key Components:**
- `risk_engine/rules.py` - Risk rules and engine

**Rules:**
- Max daily loss limit
- Max open positions
- Capital allocation limits
- Per-strategy risk caps

**Evaluation:**
- Rules evaluated before every order
- First failing rule stops evaluation
- Risk events logged to database

### 4. Broker Integration Layer (`backend/broker/`)

**Responsibilities:**
- Abstract broker interface
- Dhan adapter implementation
- Order execution
- Position management

**Key Components:**
- `broker/base.py` - Abstract interface
- `broker/dhan_adapter.py` - Dhan implementation
- `broker/factory.py` - Factory for creating adapters

**Interface Methods:**
- `authenticate()` - Broker authentication
- `place_order()` - Place order
- `cancel_order()` - Cancel order
- `get_order_status()` - Get order status
- `fetch_positions()` - Get positions
- `fetch_orders()` - Get orders
- `get_account_balance()` - Get balance

## Database Schema

### Core Tables

1. **users** - User accounts
2. **broker_accounts** - Broker API credentials
3. **strategies** - Strategy definitions
4. **strategy_runs** - Running strategy instances
5. **orders** - Orders sent to broker (immutable audit trail)
6. **trades** - Strategy-level trade intents
7. **positions** - Current positions (updated on fills)
8. **pnl_snapshots** - Time-series P&L data
9. **risk_events** - Immutable risk event log
10. **system_logs** - System-level logs

### Design Principles

- **Normalized Schema**: Proper foreign keys and relationships
- **Immutable Audit Trail**: Orders and risk events are never modified
- **Timezone-Aware**: All timestamps use timezone-aware datetime
- **Single Source of Truth**: PostgreSQL is the authoritative state store

## Strategy Framework

### Strategy Interface

Strategies must:
- Be stateless functions
- Accept market data + config
- Return trade intents (not orders)
- Never talk to broker directly
- Be reusable for backtesting, paper trading, and live trading

### Strategy Lifecycle

1. Strategy class registered in `StrategyRegistry`
2. Strategy run created with config
3. Trading engine instantiates strategy
4. Strategy receives market data events
5. Strategy emits trade intents
6. Trading engine processes intents

### Example Strategy

See `strategies/example_strategy.py` for a simple moving average crossover strategy.

## Data Flow

### Order Execution Flow

```
User starts strategy
    ↓
API creates strategy_run record
    ↓
Trading engine subscribes to market events
    ↓
Strategy emits trade intent
    ↓
Risk engine validates intent
    ↓
Order created in DB (status: PENDING)
    ↓
Broker adapter sends order to Dhan
    ↓
Broker response updates order (status: SUBMITTED)
    ↓
Order status updates (FILLED, etc.)
    ↓
Trade & position updated
    ↓
UI updates via WebSocket
```

## Frontend Architecture

### Pages

- `/` - Landing page
- `/auth/login` - Login
- `/auth/register` - Registration
- `/dashboard` - Main dashboard
- `/dashboard/strategies` - Strategy list
- `/dashboard/strategies/[id]` - Strategy detail
- `/dashboard/orders` - Orders audit
- `/dashboard/positions` - Current positions
- `/dashboard/risk` - Risk monitor

### Components

- Reusable UI components
- WebSocket client hook
- API client with auth
- State management (Zustand)

## Security

### Authentication

- JWT-based authentication
- Token stored in localStorage (frontend)
- Token validated on every request

### Authorization

- User-scoped data access
- Strategy runs belong to users
- Orders filtered by user's broker accounts

### Secrets Management

- API keys encrypted in database (production)
- Environment variables for configuration
- Never commit secrets to git

## Observability

### Logging

- Structured logging with structlog
- JSON format in production
- Console format in development
- Log levels: DEBUG, INFO, WARNING, ERROR

### Monitoring

- Health check endpoint: `/health`
- Database connection monitoring
- WebSocket connection tracking
- Risk event alerts

## Extensibility

### Adding New Brokers

1. Implement `BrokerInterface` in `broker/`
2. Add to `broker/factory.py`
3. No changes needed in trading engine

### Adding New Risk Rules

1. Create rule class extending `RiskRule`
2. Add to `RiskEngine.rules` list
3. Rule automatically evaluated

### Adding New Strategies

1. Create strategy class extending `BaseStrategy`
2. Register in `StrategyRegistry`
3. Available via API

## Non-Functional Requirements

### Idempotency

- Order placement is idempotent
- Strategy runs can be restarted safely

### Graceful Degradation

- Broker failures don't crash trading engine
- WebSocket reconnection logic
- Database connection retry

### Performance

- Async/await for I/O operations
- Database connection pooling
- Background task processing

### Scalability

- Stateless API layer
- Horizontal scaling support
- Database read replicas for reads

