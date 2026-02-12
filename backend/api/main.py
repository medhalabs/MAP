"""
FastAPI main application.

API Layer responsibilities:
- Authentication & authorization
- REST endpoints for strategy lifecycle, orders, trades
- WebSocket endpoints for real-time updates
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes import auth, tenants, strategies, orders, trades, positions, websocket, dashboard, broker_accounts, risk, settings
from database.session import init_db
from utils.logger import configure_logging
# Import strategies module to register all strategies on startup
import strategies as strategies_module  # noqa: F401

# Configure logging
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI app."""
    # Startup
    try:
        init_db()
    except Exception as e:
        # Database not available - log warning but continue
        import logging
        logging.warning(f"Database initialization failed: {e}. Server will continue but database features may not work.")
    yield
    # Shutdown
    pass


app = FastAPI(
    title="MedhaAlgoPilot API",
    description="Production-grade algorithmic trading platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(tenants.router, prefix="/api/tenants", tags=["tenants"])
app.include_router(strategies.router, prefix="/api/strategies", tags=["strategies"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(trades.router, prefix="/api/trades", tags=["trades"])
app.include_router(positions.router, prefix="/api/positions", tags=["positions"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(broker_accounts.router, prefix="/api/broker-accounts", tags=["broker-accounts"])
app.include_router(risk.router, prefix="/api/risk", tags=["risk"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(websocket.router, prefix="/api/ws", tags=["websocket"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "MedhaAlgoPilot API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

