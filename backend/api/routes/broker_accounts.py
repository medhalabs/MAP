"""
Broker account management routes.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import User, BrokerAccount, Strategy
from database.schemas import BrokerAccountCreate, BrokerAccountResponse
from api.dependencies import get_current_user
from broker.factory import create_broker_adapter
from broker.base import BrokerException

router = APIRouter()


@router.get("", response_model=List[BrokerAccountResponse])
async def list_broker_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List broker accounts for current tenant with balances."""
    accounts = db.query(BrokerAccount).filter(
        BrokerAccount.tenant_id == current_user.tenant_id
    ).all()
    
    # Fetch balance for each account
    result = []
    for account in accounts:
        account_dict = {
            "id": account.id,
            "broker_name": account.broker_name,
            "account_id": account.account_id,
            "is_default": account.is_default,
            "user_id": account.user_id,
            "is_active": account.is_active,
            "created_at": account.created_at,
            "available_balance": None,
        }
        
        # Try to fetch balance (don't fail if it doesn't work)
        try:
            access_token = account.access_token or account.api_secret
            if not access_token:
                import logging
                logging.warning(f"No access token for broker account {account.id}")
            else:
                broker = create_broker_adapter(
                    broker_name=account.broker_name,
                    api_key=account.api_key,
                    access_token=access_token,
                    account_id=account.account_id,
                    sandbox=False,
                )
                balance = await broker.get_account_balance()
                await broker.close()
                account_dict["available_balance"] = balance.get("available_balance")
        except Exception as e:
            # Log error for debugging but don't fail the request
            import logging
            logging.warning(f"Failed to fetch balance for broker account {account.id}: {str(e)}")
            # Set to None explicitly so frontend knows it failed
            account_dict["available_balance"] = None
        
        result.append(account_dict)
    
    return result


@router.post("", response_model=BrokerAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_broker_account(
    account_data: BrokerAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new broker account."""
    # For Dhan, api_secret is actually the access_token
    # Map it appropriately
    access_token = account_data.api_secret if account_data.broker_name.lower() == "dhan" else None
    
    # For Dhan v2, account_id and api_key should be the same (client-id)
    # If account_id is not provided, use api_key as account_id
    account_id = account_data.account_id or account_data.api_key
    
    # Test connection before saving (make it optional - don't fail if test fails)
    connection_test_passed = False
    test_error = None
    try:
        broker = create_broker_adapter(
            broker_name=account_data.broker_name,
            api_key=account_data.api_key,  # This is the client-id
            access_token=access_token or account_data.api_secret,
            account_id=account_id,  # Use account_id or fallback to api_key
            sandbox=False,  # Try live first, user can specify sandbox later
        )
        # Test connection by fetching account balance
        await broker.get_account_balance()
        connection_test_passed = True
        await broker.close()
    except BrokerException as e:
        test_error = str(e)
        # Don't fail - allow saving even if connection test fails
        # User can test connection later using the test endpoint
        if 'broker' in locals() and hasattr(broker, 'close'):
            try:
                await broker.close()
            except:
                pass
    except Exception as e:
        test_error = str(e)
        # Don't fail - allow saving even if connection test fails
        if 'broker' in locals() and hasattr(broker, 'close'):
            try:
                await broker.close()
            except:
                pass
    
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
        account_id=account_id,  # Use the processed account_id
        api_key=account_data.api_key,
        api_secret=account_data.api_secret,
        access_token=access_token,  # Store access_token separately for Dhan
        is_default=account_data.is_default,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    
    # Fetch balance if connection test passed
    available_balance = None
    if connection_test_passed:
        try:
            broker = create_broker_adapter(
                broker_name=account_data.broker_name,
                api_key=account_data.api_key,
                access_token=access_token or account_data.api_secret,
                account_id=account_id,
                sandbox=False,
            )
            balance = await broker.get_account_balance()
            await broker.close()
            available_balance = balance.get("available_balance")
        except Exception:
            pass
    
    # Return account with balance
    account_dict = {
        "id": account.id,
        "broker_name": account.broker_name,
        "account_id": account.account_id,
        "is_default": account.is_default,
        "user_id": account.user_id,
        "is_active": account.is_active,
        "created_at": account.created_at,
        "available_balance": available_balance,
    }
    
    return account_dict


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


@router.post("/{account_id}/refresh-balance", status_code=status.HTTP_200_OK)
async def refresh_broker_balance(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Refresh balance for a specific broker account."""
    account = db.query(BrokerAccount).filter(
        BrokerAccount.id == account_id,
        BrokerAccount.tenant_id == current_user.tenant_id,
    ).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker account not found",
        )
    
    try:
        access_token = account.access_token or account.api_secret
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token configured for this account",
            )
        
        broker = create_broker_adapter(
            broker_name=account.broker_name,
            api_key=account.api_key,
            access_token=access_token,
            account_id=account.account_id,
            sandbox=False,
        )
        balance = await broker.get_account_balance()
        await broker.close()
        
        return {
            "status": "success",
            "available_balance": float(balance.get("available_balance", 0)),
            "used_margin": float(balance.get("used_margin", 0)),
            "total_margin": float(balance.get("total_margin", 0)),
            "collateral": float(balance.get("collateral", 0)),
        }
    except BrokerException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch balance: {str(e)}",
        )
    except Exception as e:
        import logging
        logging.error(f"Error refreshing balance for account {account_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh balance: {str(e)}",
        )


@router.post("/{account_id}/test", status_code=status.HTTP_200_OK)
async def test_broker_connection(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Test broker account connection."""
    account = db.query(BrokerAccount).filter(
        BrokerAccount.id == account_id,
        BrokerAccount.tenant_id == current_user.tenant_id,
    ).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker account not found",
        )
    
    try:
        # Use access_token if available (for Dhan), otherwise use api_secret
        access_token = account.access_token or account.api_secret
        broker = create_broker_adapter(
            broker_name=account.broker_name,
            api_key=account.api_key,
            access_token=access_token,
            account_id=account.account_id,
            sandbox=False,  # Test with live
        )
        # Test connection by fetching account balance
        balance = await broker.get_account_balance()
        await broker.close()
        return {
            "status": "success",
            "message": "Connection successful",
            "balance": balance,
        }
    except BrokerException as e:
        return {
            "status": "error",
            "message": f"Connection failed: {str(e)}",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection test failed: {str(e)}",
        }


@router.patch("/{account_id}/toggle-active", response_model=BrokerAccountResponse)
async def toggle_broker_account_active(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Toggle broker account active status."""
    account = db.query(BrokerAccount).filter(
        BrokerAccount.id == account_id,
        BrokerAccount.tenant_id == current_user.tenant_id,
    ).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker account not found",
        )
    
    # Toggle active status
    account.is_active = not account.is_active
    db.commit()
    db.refresh(account)
    
    return account


@router.delete("/{account_id}", status_code=status.HTTP_200_OK)
async def delete_broker_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a broker account. Automatically stops all active strategy runs first."""
    from database.models import StrategyRun, StrategyStatus
    from trading_engine.engine import trading_engine
    
    account = db.query(BrokerAccount).filter(
        BrokerAccount.id == account_id,
        BrokerAccount.tenant_id == current_user.tenant_id,
    ).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker account not found",
        )
    
    # Find all active strategy runs using this account
    active_runs = db.query(StrategyRun).join(Strategy).filter(
        StrategyRun.broker_account_id == account_id,
        StrategyRun.status.in_([StrategyStatus.PENDING, StrategyStatus.RUNNING, StrategyStatus.PAUSED]),
        Strategy.tenant_id == current_user.tenant_id,
    ).all()
    
    # Automatically stop all active strategy runs
    if active_runs:
        for strategy_run in active_runs:
            try:
                await trading_engine.stop_strategy(strategy_run.id)
            except Exception as e:
                # Log error but continue with deletion
                import logging
                logging.warning(f"Failed to stop strategy run {strategy_run.id}: {e}")
    
    # Check for Orders and Positions (these have RESTRICT constraint for audit trail)
    from database.models import Order, Position
    
    orders_count = db.query(Order).join(BrokerAccount).filter(
        BrokerAccount.id == account_id,
        BrokerAccount.tenant_id == current_user.tenant_id,
    ).count()
    
    positions_count = db.query(Position).join(BrokerAccount).filter(
        BrokerAccount.id == account_id,
        BrokerAccount.tenant_id == current_user.tenant_id,
    ).count()
    
    if orders_count > 0 or positions_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete broker account: This account has {orders_count} order(s) and {positions_count} position(s) "
                   f"in the audit trail. Broker accounts with trading history cannot be deleted to preserve data integrity. "
                   f"Active strategy runs have been stopped.",
        )
    
    # SQLite doesn't automatically enforce ON DELETE SET NULL, so we need to manually
    # set broker_account_id to NULL for all strategy runs before deleting the account
    all_strategy_runs = db.query(StrategyRun).join(Strategy).filter(
        StrategyRun.broker_account_id == account_id,
        Strategy.tenant_id == current_user.tenant_id,
    ).all()
    
    for strategy_run in all_strategy_runs:
        strategy_run.broker_account_id = None
    
    # Now delete the account
    db.delete(account)
    db.commit()
    
    # Return success message indicating how many runs were stopped
    stopped_count = len(active_runs) if active_runs else 0
    if stopped_count > 0:
        return {
            "message": f"Broker account deleted successfully. {stopped_count} active strategy run(s) were automatically stopped.",
            "stopped_runs": stopped_count,
        }
    
    return {"message": "Broker account deleted successfully."}

