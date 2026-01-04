"""
PostgreSQL ORM Models for MedhaAlgoPilot.

Design principles:
- Normalized schema
- Immutable audit trail
- Timezone-aware timestamps
- Single source of truth
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    JSON,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class TradingMode(str, Enum):
    """Trading mode enum."""
    PAPER = "paper"
    LIVE = "live"


class OrderStatus(str, Enum):
    """Order status enum."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class OrderType(str, Enum):
    """Order type enum."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SL = "SL"
    SL_M = "SL-M"


class ProductType(str, Enum):
    """Product type enum."""
    INTRADAY = "INTRADAY"
    MARGIN = "MARGIN"
    CASH = "CASH"
    CO = "CO"
    BO = "BO"


class TransactionType(str, Enum):
    """Transaction type enum."""
    BUY = "BUY"
    SELL = "SELL"


class StrategyStatus(str, Enum):
    """Strategy run status enum."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class RiskEventType(str, Enum):
    """Risk event type enum."""
    MAX_DAILY_LOSS = "max_daily_loss"
    MAX_OPEN_POSITIONS = "max_open_positions"
    CAPITAL_LIMIT = "capital_limit"
    PER_STRATEGY_LIMIT = "per_strategy_limit"
    POSITION_SIZE_LIMIT = "position_size_limit"


# ============================================================================
# Core Tables
# ============================================================================


class Tenant(Base):
    """Tenant/Organization for multi-tenancy."""
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)  # URL-friendly identifier
    domain = Column(String(255), nullable=True, unique=True, index=True)  # Optional custom domain
    is_active = Column(Boolean, default=True, nullable=False)
    subscription_tier = Column(String(50), default="free", nullable=False)  # free, pro, enterprise
    max_users = Column(Integer, default=5, nullable=False)
    max_strategies = Column(Integer, default=10, nullable=False)
    settings = Column(JSON, nullable=True)  # Tenant-specific settings
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    broker_accounts = relationship("BrokerAccount", back_populates="tenant", cascade="all, delete-orphan")
    strategies = relationship("Strategy", back_populates="tenant", cascade="all, delete-orphan")


class User(Base):
    """User account."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    username = Column(String(100), nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_tenant_admin = Column(Boolean, default=False, nullable=False)  # Admin within tenant
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    broker_accounts = relationship("BrokerAccount", back_populates="user", cascade="all, delete-orphan")
    strategies = relationship("Strategy", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_user_tenant_email", "tenant_id", "email", unique=True),
        Index("idx_user_tenant_username", "tenant_id", "username", unique=True),
    )


class BrokerAccount(Base):
    """Broker account linked to a user."""
    __tablename__ = "broker_accounts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    broker_name = Column(String(50), nullable=False)  # e.g., "dhan"
    account_id = Column(String(100), nullable=False)  # Broker's account identifier
    api_key = Column(String(255), nullable=False)  # Encrypted in production
    api_secret = Column(String(255), nullable=False)  # Encrypted in production
    access_token = Column(Text, nullable=True)  # Temporary token, encrypted
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="broker_accounts")
    user = relationship("User", back_populates="broker_accounts")
    strategy_runs = relationship("StrategyRun", back_populates="broker_account")
    orders = relationship("Order", back_populates="broker_account")

    __table_args__ = (
        Index("idx_broker_account_tenant_user", "tenant_id", "user_id", "is_default"),
    )


class Strategy(Base):
    """Strategy definition (template)."""
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    strategy_code = Column(Text, nullable=False)  # Python code or reference
    config_schema = Column(JSON, nullable=True)  # JSON schema for strategy config
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="strategies")
    user = relationship("User", back_populates="strategies")
    strategy_runs = relationship("StrategyRun", back_populates="strategy")

    __table_args__ = (
        Index("idx_strategy_tenant", "tenant_id", "is_active"),
    )


class StrategyRun(Base):
    """A running instance of a strategy."""
    __tablename__ = "strategy_runs"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False, index=True)
    broker_account_id = Column(Integer, ForeignKey("broker_accounts.id", ondelete="RESTRICT"), nullable=False, index=True)
    trading_mode = Column(SQLEnum(TradingMode), nullable=False, default=TradingMode.PAPER)
    status = Column(SQLEnum(StrategyStatus), nullable=False, default=StrategyStatus.PENDING, index=True)
    config = Column(JSON, nullable=False)  # Strategy-specific configuration
    started_at = Column(DateTime(timezone=True), nullable=True)
    stopped_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    strategy = relationship("Strategy", back_populates="strategy_runs")
    broker_account = relationship("BrokerAccount", back_populates="strategy_runs")
    trades = relationship("Trade", back_populates="strategy_run")
    pnl_snapshots = relationship("PnlSnapshot", back_populates="strategy_run")
    risk_events = relationship("RiskEvent", back_populates="strategy_run")

    __table_args__ = (
        Index("idx_strategy_run_status", "status", "trading_mode"),
    )


class Order(Base):
    """Order sent to broker (immutable audit trail)."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    broker_account_id = Column(Integer, ForeignKey("broker_accounts.id", ondelete="RESTRICT"), nullable=False, index=True)
    strategy_run_id = Column(Integer, ForeignKey("strategy_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    trade_id = Column(Integer, ForeignKey("trades.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Broker-specific identifiers
    broker_order_id = Column(String(100), nullable=True, unique=True, index=True)  # Dhan order ID
    dhan_order_id = Column(String(100), nullable=True, unique=True, index=True)  # Alias for clarity
    
    # Order details
    symbol = Column(String(50), nullable=False, index=True)
    exchange = Column(String(20), nullable=False)  # NSE, BSE, etc.
    order_type = Column(SQLEnum(OrderType), nullable=False)
    product_type = Column(SQLEnum(ProductType), nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=True)  # For LIMIT orders
    trigger_price = Column(Numeric(10, 2), nullable=True)  # For SL orders
    status = Column(SQLEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING, index=True)
    
    # Execution details
    filled_quantity = Column(Integer, default=0, nullable=False)
    average_price = Column(Numeric(10, 2), nullable=True)
    
    # Metadata
    broker_response = Column(JSON, nullable=True)  # Raw broker response
    error_message = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    filled_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    broker_account = relationship("BrokerAccount", back_populates="orders")
    trade = relationship("Trade", back_populates="orders")

    __table_args__ = (
        Index("idx_order_status_symbol", "status", "symbol"),
        Index("idx_order_strategy_run", "strategy_run_id", "created_at"),
    )


class Trade(Base):
    """Strategy-level trade intent (one trade may map to multiple orders)."""
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    strategy_run_id = Column(Integer, ForeignKey("strategy_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    exchange = Column(String(20), nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    quantity = Column(Integer, nullable=False)
    intended_price = Column(Numeric(10, 2), nullable=True)  # Strategy's intended price
    product_type = Column(SQLEnum(ProductType), nullable=False)
    
    # Execution status
    is_completed = Column(Boolean, default=False, nullable=False, index=True)
    total_filled_quantity = Column(Integer, default=0, nullable=False)
    average_execution_price = Column(Numeric(10, 2), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    strategy_run = relationship("StrategyRun", back_populates="trades")
    orders = relationship("Order", back_populates="trade")

    __table_args__ = (
        Index("idx_trade_strategy_symbol", "strategy_run_id", "symbol", "is_completed"),
    )


class Position(Base):
    """Current position snapshot (updated on order fill)."""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    broker_account_id = Column(Integer, ForeignKey("broker_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    strategy_run_id = Column(Integer, ForeignKey("strategy_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    exchange = Column(String(20), nullable=False)
    product_type = Column(SQLEnum(ProductType), nullable=False)
    
    # Position details
    quantity = Column(Integer, nullable=False)  # Positive for long, negative for short
    average_price = Column(Numeric(10, 2), nullable=False)
    last_price = Column(Numeric(10, 2), nullable=True)  # Last traded price
    unrealized_pnl = Column(Numeric(12, 2), nullable=True)
    
    # Timestamps
    opened_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    broker_account = relationship("BrokerAccount")

    __table_args__ = (
        Index("idx_position_account_symbol", "broker_account_id", "symbol", "product_type", unique=True),
        Index("idx_position_strategy", "strategy_run_id", "symbol"),
    )


class PnlSnapshot(Base):
    """Time-series P&L snapshots for strategies."""
    __tablename__ = "pnl_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    strategy_run_id = Column(Integer, ForeignKey("strategy_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # P&L metrics
    realized_pnl = Column(Numeric(12, 2), default=0, nullable=False)
    unrealized_pnl = Column(Numeric(12, 2), default=0, nullable=False)
    total_pnl = Column(Numeric(12, 2), nullable=False)
    capital_used = Column(Numeric(12, 2), nullable=False)
    open_positions_count = Column(Integer, default=0, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    strategy_run = relationship("StrategyRun", back_populates="pnl_snapshots")

    __table_args__ = (
        Index("idx_pnl_strategy_timestamp", "strategy_run_id", "timestamp"),
    )


class RiskEvent(Base):
    """Immutable risk event log."""
    __tablename__ = "risk_events"

    id = Column(Integer, primary_key=True, index=True)
    strategy_run_id = Column(Integer, ForeignKey("strategy_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    broker_account_id = Column(Integer, ForeignKey("broker_accounts.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(SQLEnum(RiskEventType), nullable=False, index=True)
    
    # Event details
    message = Column(Text, nullable=False)
    event_metadata = Column(JSON, nullable=True)  # Additional context
    was_blocked = Column(Boolean, nullable=False)  # Whether the action was blocked
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    strategy_run = relationship("StrategyRun", back_populates="risk_events")

    __table_args__ = (
        Index("idx_risk_event_type_time", "event_type", "created_at"),
    )


class SystemLog(Base):
    """System-level logs for audit and debugging."""
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR
    component = Column(String(50), nullable=False, index=True)  # trading_engine, risk_engine, broker, etc.
    message = Column(Text, nullable=False)
    log_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (
        Index("idx_system_log_component_time", "component", "created_at"),
    )

