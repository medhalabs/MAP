"""
Strategy management routes.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import User, Strategy, StrategyRun, StrategyStatus, BrokerAccount
from database.schemas import (
    StrategyCreate,
    StrategyResponse,
    StrategyRunCreate,
    StrategyRunResponse,
)
from api.dependencies import get_current_user, get_current_tenant
from trading_engine.engine import trading_engine

router = APIRouter()


@router.get("", response_model=List[StrategyResponse])
async def list_strategies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant = Depends(get_current_tenant),
):
    """List all strategies for current tenant."""
    strategies = db.query(Strategy).filter(
        Strategy.tenant_id == current_user.tenant_id
    ).all()
    return strategies


@router.post("", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    strategy_data: StrategyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant = Depends(get_current_tenant),
):
    """Create a new strategy."""
    strategy = Strategy(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        name=strategy_data.name,
        description=strategy_data.description,
        strategy_code=strategy_data.strategy_code,
        config_schema=strategy_data.config_schema,
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return strategy


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant = Depends(get_current_tenant),
):
    """Get strategy by ID."""
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.tenant_id == current_user.tenant_id,
    ).first()
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )
    return strategy


@router.post("/{strategy_id}/runs", response_model=StrategyRunResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy_run(
    strategy_id: int,
    run_data: StrategyRunCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create and start a strategy run."""
    # Verify strategy belongs to tenant
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.tenant_id == current_user.tenant_id,
    ).first()
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )
    
    # Verify broker account belongs to tenant
    broker_account = db.query(BrokerAccount).filter(
        BrokerAccount.id == run_data.broker_account_id,
        BrokerAccount.tenant_id == current_user.tenant_id,
    ).first()
    if not broker_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker account not found",
        )
    
    # Create strategy run
    strategy_run = StrategyRun(
        strategy_id=strategy_id,
        broker_account_id=run_data.broker_account_id,
        trading_mode=run_data.trading_mode,
        config=run_data.config,
        status=StrategyStatus.PENDING,
    )
    db.add(strategy_run)
    db.commit()
    db.refresh(strategy_run)
    
    # Start strategy in trading engine
    await trading_engine.start_strategy(strategy_run.id)
    
    return strategy_run


@router.get("/runs/{run_id}", response_model=StrategyRunResponse)
async def get_strategy_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get strategy run by ID."""
    strategy_run = db.query(StrategyRun).filter(
        StrategyRun.id == run_id,
        StrategyRun.strategy.has(tenant_id=current_user.tenant_id),
    ).first()
    if not strategy_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy run not found",
        )
    return strategy_run


@router.post("/runs/{run_id}/stop")
async def stop_strategy_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stop a running strategy."""
    strategy_run = db.query(StrategyRun).filter(
        StrategyRun.id == run_id,
        StrategyRun.strategy.has(tenant_id=current_user.tenant_id),
    ).first()
    if not strategy_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy run not found",
        )
    
    await trading_engine.stop_strategy(run_id)
    
    return {"message": "Strategy stopped"}


@router.get("/runs", response_model=List[StrategyRunResponse])
async def list_strategy_runs(
    strategy_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List strategy runs for current tenant."""
    query = db.query(StrategyRun).filter(
        StrategyRun.strategy.has(tenant_id=current_user.tenant_id)
    )
    
    if strategy_id:
        query = query.filter(StrategyRun.strategy_id == strategy_id)
    
    runs = query.order_by(StrategyRun.created_at.desc()).all()
    return runs

