"""
Authentication routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import timedelta

from database.session import get_db
from database.models import User, Tenant
from database.schemas import UserCreate, UserResponse, TenantCreate, TenantResponse
from api.dependencies import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with tenant."""
    # Determine tenant
    tenant_id = user_data.tenant_id
    
    if user_data.tenant_slug:
        # Join existing tenant by slug
        tenant = db.query(Tenant).filter(Tenant.slug == user_data.tenant_slug).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found",
            )
        if not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant is inactive",
            )
        tenant_id = tenant.id
    elif not tenant_id:
        # Create new tenant (first user becomes admin)
        tenant = Tenant(
            name=f"{user_data.username}'s Organization",
            slug=user_data.username.lower().replace(" ", "-"),
            subscription_tier="free",
        )
        db.add(tenant)
        db.flush()
        tenant_id = tenant.id
    
    # Check if user exists within tenant
    existing_user = db.query(User).filter(
        User.tenant_id == tenant_id,
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered in this organization",
        )
    
    # Create user (first user in tenant becomes admin)
    is_first_user = db.query(User).filter(User.tenant_id == tenant_id).count() == 0
    
    user = User(
        tenant_id=tenant_id,
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        is_tenant_admin=is_first_user,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login and get access token."""
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user),
    }

