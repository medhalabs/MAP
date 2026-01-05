"""
Dashboard data routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, Any

from database.session import get_db
from database.models import User, StrategyRun, Order, Trade, Position, PnlSnapshot, Strategy, StrategyStatus, BrokerAccount
from api.dependencies import get_current_user

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get dashboard statistics."""
    tenant_id = current_user.tenant_id
    
    # Active strategies count
    active_strategies = db.query(StrategyRun).join(Strategy).filter(
        Strategy.tenant_id == tenant_id,
        StrategyRun.status == StrategyStatus.RUNNING
    ).count()
    
    # Total orders today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_orders = db.query(Order).join(BrokerAccount).filter(
        BrokerAccount.tenant_id == tenant_id,
        Order.created_at >= today_start
    ).count()
    
    # Open positions count
    open_positions = db.query(Position).join(BrokerAccount).filter(
        BrokerAccount.tenant_id == tenant_id,
        Position.quantity != 0
    ).count()
    
    # Latest P&L (from latest strategy run snapshot or calculate)
    latest_pnl = db.query(PnlSnapshot).join(StrategyRun).join(Strategy).filter(
        Strategy.tenant_id == tenant_id
    ).order_by(PnlSnapshot.timestamp.desc()).first()
    
    total_pnl = float(latest_pnl.total_pnl) if latest_pnl else 0.0
    
    # Today's P&L
    today_pnl = db.query(func.sum(PnlSnapshot.total_pnl)).join(StrategyRun).join(Strategy).filter(
        Strategy.tenant_id == tenant_id,
        PnlSnapshot.timestamp >= today_start
    ).scalar() or 0
    
    return {
        "active_strategies": active_strategies,
        "today_orders": today_orders,
        "open_positions": open_positions,
        "total_pnl": float(total_pnl),
        "today_pnl": float(today_pnl),
    }


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get recent activity (orders, trades, strategy runs)."""
    tenant_id = current_user.tenant_id
    
    # Recent orders
    recent_orders = db.query(Order).join(BrokerAccount).filter(
        BrokerAccount.tenant_id == tenant_id
    ).order_by(Order.created_at.desc()).limit(limit).all()
    
    # Recent trades
    recent_trades = db.query(Trade).join(StrategyRun).join(Strategy).filter(
        Strategy.tenant_id == tenant_id
    ).order_by(Trade.created_at.desc()).limit(limit).all()
    
    # Recent strategy runs
    recent_runs = db.query(StrategyRun).join(Strategy).filter(
        Strategy.tenant_id == tenant_id
    ).order_by(StrategyRun.created_at.desc()).limit(5).all()
    
    return {
        "orders": [
            {
                "id": o.id,
                "symbol": o.symbol,
                "status": o.status.value,
                "quantity": o.quantity,
                "created_at": o.created_at.isoformat(),
            }
            for o in recent_orders
        ],
        "trades": [
            {
                "id": t.id,
                "symbol": t.symbol,
                "transaction_type": t.transaction_type.value,
                "quantity": t.quantity,
                "is_completed": t.is_completed,
                "created_at": t.created_at.isoformat(),
            }
            for t in recent_trades
        ],
        "strategy_runs": [
            {
                "id": sr.id,
                "strategy_id": sr.strategy_id,
                "status": sr.status.value,
                "trading_mode": sr.trading_mode.value,
                "created_at": sr.created_at.isoformat(),
            }
            for sr in recent_runs
        ],
    }

