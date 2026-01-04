"""
Position management routes.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import User, Position
from database.schemas import PositionResponse
from api.dependencies import get_current_user, get_current_tenant

router = APIRouter()


@router.get("", response_model=List[PositionResponse])
async def list_positions(
    strategy_run_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List positions for current tenant."""
    query = db.query(Position).filter(
        Position.broker_account.has(tenant_id=current_user.tenant_id),
        Position.quantity != 0,  # Only non-zero positions
    )
    
    if strategy_run_id:
        query = query.filter(Position.strategy_run_id == strategy_run_id)
    
    positions = query.all()
    return positions


@router.get("/{position_id}", response_model=PositionResponse)
async def get_position(
    position_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get position by ID."""
    position = db.query(Position).filter(
        Position.id == position_id,
        Position.broker_account.has(tenant_id=current_user.tenant_id),
    ).first()
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found",
        )
    return position

