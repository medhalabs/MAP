"""
Tenant/Organization management routes.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import User, Tenant
from database.schemas import TenantResponse, TenantCreate
from api.dependencies import get_current_user, get_current_tenant

router = APIRouter()


@router.get("/current", response_model=TenantResponse)
async def get_current_tenant_info(
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Get current user's tenant information."""
    return current_tenant


@router.get("/users", response_model=List[dict])
async def list_tenant_users(
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all users in current tenant (admin only)."""
    if not current_user.is_tenant_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tenant admins can view users",
        )
    
    users = db.query(User).filter(User.tenant_id == current_tenant.id).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "username": u.username,
            "is_active": u.is_active,
            "is_tenant_admin": u.is_tenant_admin,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]

