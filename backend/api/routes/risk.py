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
    query = db.query(RiskEvent).filter(
        RiskEvent.tenant_id == current_user.tenant_id
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
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Total risk events today
    today_events = db.query(func.count(RiskEvent.id)).filter(
        RiskEvent.tenant_id == current_user.tenant_id,
        RiskEvent.created_at >= today_start
    ).scalar() or 0
    
    # Events by severity
    from database.models import RiskSeverity
    critical_count = db.query(func.count(RiskEvent.id)).filter(
        RiskEvent.tenant_id == current_user.tenant_id,
        RiskEvent.severity == RiskSeverity.CRITICAL,
        RiskEvent.created_at >= today_start
    ).scalar() or 0
    
    warning_count = db.query(func.count(RiskEvent.id)).filter(
        RiskEvent.tenant_id == current_user.tenant_id,
        RiskEvent.severity == RiskSeverity.WARNING,
        RiskEvent.created_at >= today_start
    ).scalar() or 0
    
    return {
        "today_events": today_events,
        "critical_count": critical_count,
        "warning_count": warning_count,
    }

