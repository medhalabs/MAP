"""
Pydantic schemas for request/response validation.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field

from database.models import (
    TradingMode,
    OrderStatus,
    OrderType,
    ProductType,
    TransactionType,
    StrategyStatus,
    RiskEventType,
)


# ============================================================================
# Tenant Schemas
# ============================================================================

class TenantBase(BaseModel):
    name: str
    slug: str

class TenantCreate(TenantBase):
    domain: Optional[str] = None

class TenantResponse(TenantBase):
    id: int
    domain: Optional[str] = None
    is_active: bool
    subscription_tier: str
    max_users: int
    max_strategies: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    tenant_id: Optional[int] = None  # Optional for registration
    tenant_slug: Optional[str] = None  # Alternative: create/join by slug

class UserResponse(UserBase):
    id: int
    tenant_id: int
    is_active: bool
    is_tenant_admin: bool
    created_at: datetime
    tenant: Optional[TenantResponse] = None

    class Config:
        from_attributes = True


# ============================================================================
# Broker Account Schemas
# ============================================================================

class BrokerAccountBase(BaseModel):
    broker_name: str
    account_id: str
    is_default: bool = False

class BrokerAccountCreate(BrokerAccountBase):
    api_key: str
    api_secret: str

class BrokerAccountResponse(BrokerAccountBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Strategy Schemas
# ============================================================================

class StrategyBase(BaseModel):
    name: str
    description: Optional[str] = None
    config_schema: Optional[Dict[str, Any]] = None

class StrategyCreate(StrategyBase):
    strategy_code: str

class StrategyResponse(StrategyBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Strategy Run Schemas
# ============================================================================

class StrategyRunBase(BaseModel):
    strategy_id: int
    broker_account_id: int
    trading_mode: TradingMode
    config: Dict[str, Any]

class StrategyRunCreate(StrategyRunBase):
    pass

class StrategyRunResponse(StrategyRunBase):
    id: int
    status: StrategyStatus
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Order Schemas
# ============================================================================

class OrderBase(BaseModel):
    symbol: str
    exchange: str
    order_type: OrderType
    product_type: ProductType
    transaction_type: TransactionType
    quantity: int
    price: Optional[Decimal] = None
    trigger_price: Optional[Decimal] = None

class OrderCreate(OrderBase):
    broker_account_id: int
    strategy_run_id: Optional[int] = None
    trade_id: Optional[int] = None

class OrderResponse(OrderBase):
    id: int
    broker_account_id: int
    strategy_run_id: Optional[int] = None
    trade_id: Optional[int] = None
    broker_order_id: Optional[str] = None
    status: OrderStatus
    filled_quantity: int
    average_price: Optional[Decimal] = None
    error_message: Optional[str] = None
    submitted_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Trade Schemas
# ============================================================================

class TradeBase(BaseModel):
    symbol: str
    exchange: str
    transaction_type: TransactionType
    quantity: int
    intended_price: Optional[Decimal] = None
    product_type: ProductType

class TradeCreate(TradeBase):
    strategy_run_id: int

class TradeResponse(TradeBase):
    id: int
    strategy_run_id: int
    is_completed: bool
    total_filled_quantity: int
    average_execution_price: Optional[Decimal] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Position Schemas
# ============================================================================

class PositionResponse(BaseModel):
    id: int
    broker_account_id: int
    strategy_run_id: Optional[int] = None
    symbol: str
    exchange: str
    product_type: ProductType
    quantity: int
    average_price: Decimal
    last_price: Optional[Decimal] = None
    unrealized_pnl: Optional[Decimal] = None
    opened_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# P&L Schemas
# ============================================================================

class PnlSnapshotResponse(BaseModel):
    id: int
    strategy_run_id: int
    timestamp: datetime
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    total_pnl: Decimal
    capital_used: Decimal
    open_positions_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Risk Event Schemas
# ============================================================================

class RiskEventResponse(BaseModel):
    id: int
    strategy_run_id: Optional[int] = None
    broker_account_id: Optional[int] = None
    event_type: RiskEventType
    message: str
    event_metadata: Optional[Dict[str, Any]] = None
    was_blocked: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# WebSocket Event Schemas
# ============================================================================

class WebSocketEvent(BaseModel):
    event_type: str  # order_update, pnl_update, strategy_log, risk_alert
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

