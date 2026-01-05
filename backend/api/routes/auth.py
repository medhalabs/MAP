"""
Authentication routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import User
from database.schemas import UserResponse, UserCreate
from api.dependencies import get_current_user, create_access_token

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """Register a new user."""
    from passlib.context import CryptContext
    from datetime import datetime
    from database.models import Tenant
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Check if user wants to join existing tenant or create new one
    tenant = None
    if user_data.tenant_id:
        tenant = db.query(Tenant).filter(Tenant.id == user_data.tenant_id).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found",
            )
    elif user_data.tenant_slug:
        tenant = db.query(Tenant).filter(Tenant.slug == user_data.tenant_slug).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found",
            )
    
    # If no tenant specified, create a new one
    if not tenant:
        from database.models import Tenant
        import re
        
        # Generate slug from username
        base_slug = re.sub(r'[^a-z0-9]+', '-', user_data.username.lower()).strip('-')
        slug = base_slug
        counter = 1
        
        # Ensure unique slug
        while db.query(Tenant).filter(Tenant.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        tenant = Tenant(
            name=user_data.username,
            slug=slug,
            is_active=True,
            subscription_tier="free",
            max_users=10,
            max_strategies=5,
        )
        db.add(tenant)
        db.flush()  # Get tenant ID without committing
        
        # First user becomes admin
        is_tenant_admin = True
    else:
        is_tenant_admin = False
    
    # Check if email/username already exists in this tenant
    existing_user = db.query(User).filter(
        User.email == user_data.email,
        User.tenant_id == tenant.id,
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered in this organization",
        )
    
    existing_username = db.query(User).filter(
        User.username == user_data.username,
        User.tenant_id == tenant.id,
    ).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken in this organization",
        )
    
    # Create user
    hashed_password = pwd_context.hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        tenant_id=tenant.id,
        is_active=True,
        is_tenant_admin=is_tenant_admin,
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
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
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
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active,
        },
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user information."""
    return current_user
