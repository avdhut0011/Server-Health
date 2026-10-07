from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.logging import audit_logger
from app.models.user import User, Role
from app.models.audit import AuditLog
from app.schemas.auth import Token, UserCreate, UserResponse, LoginRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User).where(User.username == form_data.username)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive account")
        
    r_stmt = select(Role).where(Role.id == user.role_id)
    r_res = await db.execute(r_stmt)
    role = r_res.scalar_one_or_none()
    role_name = role.name if role else "VIEWER"
    
    access_token = create_access_token(subject=user.username, role=role_name)
    
    user.last_login = datetime.now(timezone.utc)
    
    audit_entry = AuditLog(
        user_id=user.id,
        username=user.username,
        action="LOGIN",
        resource_type="USER",
        resource_id=user.id
    )
    db.add(audit_entry)
    await db.commit()
    
    audit_logger.info(f"User '{user.username}' logged in successfully.")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": role_name,
            "full_name": user.full_name
        }
    }

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check if user already exists
    stmt = select(User).where((User.username == user_in.username) | (User.email == user_in.email))
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username or Email already exists")
        
    r_stmt = select(Role).where(Role.name == user_in.role_name.upper())
    r_res = await db.execute(r_stmt)
    role = r_res.scalar_one_or_none()
    if not role:
        role = Role(name=user_in.role_name.upper(), description=f"{user_in.role_name.upper()} Role")
        db.add(role)
        await db.flush()
        
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role_id=role.id,
        is_active=user_in.is_active
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        role_id=role.id,
        role_name=role.name,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )
