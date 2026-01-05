"""
Order management routes.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import User, Order, OrderStatus, BrokerAccount
from database.schemas import OrderResponse
from api.dependencies import get_current_user, get_current_tenant

router = APIRouter()


@router.get("", response_model=List[OrderResponse])
async def list_orders(
    strategy_run_id: Optional[int] = Query(None),
    status: Optional[OrderStatus] = Query(None),
    symbol: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List orders for current tenant."""
    query = db.query(Order).join(BrokerAccount).filter(
        BrokerAccount.tenant_id == current_user.tenant_id
    )
    
    if strategy_run_id:
        query = query.filter(Order.strategy_run_id == strategy_run_id)
    if status:
        query = query.filter(Order.status == status)
    if symbol:
        query = query.filter(Order.symbol == symbol)
    
    orders = query.order_by(Order.created_at.desc()).limit(100).all()
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get order by ID."""
    order = db.query(Order).join(BrokerAccount).filter(
        Order.id == order_id,
        BrokerAccount.tenant_id == current_user.tenant_id,
    ).first()
    if not order:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return order
    """Get order by ID."""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.broker_account.has(tenant_id=current_user.tenant_id),
    ).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return order

