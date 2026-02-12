"""
Risk monitoring routes.
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import User, RiskEvent
from database.schemas import RiskEventResponse
from api.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=List[RiskEventResponse])
async def list_risk_events(
    limit: int = Query(100, le=1000),
    severity: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List risk events for current tenant."""
    from database.models import Strategy, StrategyRun
    
    # RiskEvent doesn't have tenant_id, filter via strategy_run -> strategy -> tenant_id
    query = db.query(RiskEvent).join(
        StrategyRun, RiskEvent.strategy_run_id == StrategyRun.id, isouter=True
    ).join(
        Strategy, StrategyRun.strategy_id == Strategy.id, isouter=True
    ).filter(
        Strategy.tenant_id == current_user.tenant_id
    )
    
    if severity:
        query = query.filter(RiskEvent.severity == severity)
    
    events = query.order_by(RiskEvent.created_at.desc()).limit(limit).all()
    return events


@router.get("/stats")
async def get_risk_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get risk statistics."""
    from sqlalchemy import func
    from datetime import datetime, timedelta
    from database.models import Strategy, StrategyRun, RiskSeverity
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Total risk events today (filtered by tenant via strategy_run -> strategy)
    today_events = db.query(func.count(RiskEvent.id)).join(
        StrategyRun, RiskEvent.strategy_run_id == StrategyRun.id, isouter=True
    ).join(
        Strategy, StrategyRun.strategy_id == Strategy.id, isouter=True
    ).filter(
        Strategy.tenant_id == current_user.tenant_id,
        RiskEvent.created_at >= today_start
    ).scalar() or 0
    
    # Events by severity
    critical_count = db.query(func.count(RiskEvent.id)).join(
        StrategyRun, RiskEvent.strategy_run_id == StrategyRun.id, isouter=True
    ).join(
        Strategy, StrategyRun.strategy_id == Strategy.id, isouter=True
    ).filter(
        Strategy.tenant_id == current_user.tenant_id,
        RiskEvent.severity == RiskSeverity.CRITICAL,
        RiskEvent.created_at >= today_start
    ).scalar() or 0
    
    warning_count = db.query(func.count(RiskEvent.id)).join(
        StrategyRun, RiskEvent.strategy_run_id == StrategyRun.id, isouter=True
    ).join(
        Strategy, StrategyRun.strategy_id == Strategy.id, isouter=True
    ).filter(
        Strategy.tenant_id == current_user.tenant_id,
        RiskEvent.severity == RiskSeverity.WARNING,
        RiskEvent.created_at >= today_start
    ).scalar() or 0
    
    return {
        "today_events": today_events,
        "critical_count": critical_count,
        "warning_count": warning_count,
    }

