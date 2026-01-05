"""
Broker account management routes.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import User, BrokerAccount
from database.schemas import BrokerAccountCreate, BrokerAccountResponse
from api.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=List[BrokerAccountResponse])
async def list_broker_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List broker accounts for current tenant."""
    accounts = db.query(BrokerAccount).filter(
        BrokerAccount.tenant_id == current_user.tenant_id
    ).all()
    return accounts


@router.post("", response_model=BrokerAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_broker_account(
    account_data: BrokerAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new broker account."""
    # Check if default account exists and update if needed
    if account_data.is_default:
        existing_default = db.query(BrokerAccount).filter(
            BrokerAccount.tenant_id == current_user.tenant_id,
            BrokerAccount.is_default == True
        ).first()
        if existing_default:
            existing_default.is_default = False
    
    account = BrokerAccount(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        broker_name=account_data.broker_name,
        account_id=account_data.account_id,
        api_key=account_data.api_key,
        api_secret=account_data.api_secret,
        is_default=account_data.is_default,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("/{account_id}", response_model=BrokerAccountResponse)
async def get_broker_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get broker account by ID."""
    account = db.query(BrokerAccount).filter(
        BrokerAccount.id == account_id,
        BrokerAccount.tenant_id == current_user.tenant_id,
    ).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker account not found",
        )
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_broker_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a broker account."""
    account = db.query(BrokerAccount).filter(
        BrokerAccount.id == account_id,
        BrokerAccount.tenant_id == current_user.tenant_id,
    ).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker account not found",
        )
    db.delete(account)
    db.commit()
    return None

