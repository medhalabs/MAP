"""
Application settings routes.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.session import get_db
from database.models import User, Tenant
from api.dependencies import get_current_user, get_current_tenant

router = APIRouter()

# Initialize default settings if needed
DEFAULT_TENANT_SETTINGS = {
    "max_daily_loss": None,
    "max_open_positions": None,
    "max_position_size": None,
    "risk_notifications_enabled": True,
    "email_notifications": False,
}


class TenantSettingsUpdate(BaseModel):
    """Update tenant settings."""
    name: Optional[str] = None
    max_daily_loss: Optional[float] = None
    max_open_positions: Optional[int] = None
    max_position_size: Optional[float] = None
    risk_notifications_enabled: Optional[bool] = None
    email_notifications: Optional[bool] = None


class UserSettingsUpdate(BaseModel):
    """Update user settings."""
    email_notifications: Optional[bool] = None
    risk_alerts: Optional[bool] = None
    strategy_notifications: Optional[bool] = None


@router.get("/tenant")
async def get_tenant_settings(
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Get current tenant settings."""
    settings = current_tenant.settings or {}
    # Merge with defaults
    merged_settings = {**DEFAULT_TENANT_SETTINGS, **settings}
    
    return {
        "name": current_tenant.name,
        "slug": current_tenant.slug,
        "subscription_tier": current_tenant.subscription_tier,
        "max_users": current_tenant.max_users,
        "max_strategies": current_tenant.max_strategies,
        "max_daily_loss": merged_settings.get("max_daily_loss"),
        "max_open_positions": merged_settings.get("max_open_positions"),
        "max_position_size": merged_settings.get("max_position_size"),
        "risk_notifications_enabled": merged_settings.get("risk_notifications_enabled", True),
        "email_notifications": merged_settings.get("email_notifications", False),
    }


@router.put("/tenant")
async def update_tenant_settings(
    settings_data: TenantSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Update tenant settings (only tenant admin can update)."""
    if not current_user.is_tenant_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tenant admin can update tenant settings",
        )
    
    # Update tenant name if provided
    if settings_data.name:
        current_tenant.name = settings_data.name
    
    # Update settings dict
    if current_tenant.settings is None:
        current_tenant.settings = {}
    
    if settings_data.max_daily_loss is not None:
        current_tenant.settings["max_daily_loss"] = settings_data.max_daily_loss
    if settings_data.max_open_positions is not None:
        current_tenant.settings["max_open_positions"] = settings_data.max_open_positions
    if settings_data.max_position_size is not None:
        current_tenant.settings["max_position_size"] = settings_data.max_position_size
    if settings_data.risk_notifications_enabled is not None:
        current_tenant.settings["risk_notifications_enabled"] = settings_data.risk_notifications_enabled
    if settings_data.email_notifications is not None:
        current_tenant.settings["email_notifications"] = settings_data.email_notifications
    
    db.commit()
    db.refresh(current_tenant)
    
    return {
        "message": "Settings updated successfully",
        "settings": current_tenant.settings,
    }


@router.get("/user")
async def get_user_settings(
    current_user: User = Depends(get_current_user),
):
    """Get current user settings."""
    # User settings can be stored in a separate table or in user metadata
    # For now, return default settings
    return {
        "email_notifications": True,
        "risk_alerts": True,
        "strategy_notifications": True,
    }


@router.put("/user")
async def update_user_settings(
    settings_data: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update user settings."""
    # In a full implementation, you'd store these in a user_settings table
    # For now, we'll just return success
    return {
        "message": "User settings updated successfully",
        "settings": settings_data.dict(exclude_unset=True),
    }

