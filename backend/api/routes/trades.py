"""
Trade management routes.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import User, Trade, StrategyRun, Strategy
from database.schemas import TradeResponse
from api.dependencies import get_current_user, get_current_tenant

router = APIRouter()


@router.get("", response_model=List[TradeResponse])
async def list_trades(
    strategy_run_id: Optional[int] = Query(None),
    symbol: Optional[str] = Query(None),
    is_completed: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List trades for current tenant."""
    query = db.query(Trade).join(StrategyRun).join(Strategy).filter(
        Strategy.tenant_id == current_user.tenant_id
    )
    
    if strategy_run_id:
        query = query.filter(Trade.strategy_run_id == strategy_run_id)
    if symbol:
        query = query.filter(Trade.symbol == symbol)
    if is_completed is not None:
        query = query.filter(Trade.is_completed == is_completed)
    
    trades = query.order_by(Trade.created_at.desc()).limit(100).all()
    return trades


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get trade by ID."""
    trade = db.query(Trade).join(StrategyRun).join(Strategy).filter(
        Trade.id == trade_id,
        Strategy.tenant_id == current_user.tenant_id,
    ).first()
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found",
        )
    return trade
    """Get trade by ID."""
    trade = db.query(Trade).filter(
        Trade.id == trade_id,
        Trade.strategy_run.has(strategy__tenant_id=current_user.tenant_id),
    ).first()
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found",
        )
    return trade

