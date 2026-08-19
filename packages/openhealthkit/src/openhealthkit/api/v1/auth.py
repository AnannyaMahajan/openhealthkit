from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from openhealthkit.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from openhealthkit.database import get_async_db
from openhealthkit.models.user import Role, User
from openhealthkit.schemas.auth import (
    RefreshTokenRequest,
    Token,
    UserLogin,
    UserRegister,
)
from openhealthkit.schemas.user import UserRead
from openhealthkit.utils.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(req: UserRegister, db: AsyncSession = Depends(get_async_db)):
    # Check if username or email exists
    stmt = select(User).where((User.username == req.username) | (User.email == req.email))
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    # Assign default HEALTH_WORKER role
    role_stmt = select(Role).where(Role.name == "HEALTH_WORKER")
    role_res = await db.execute(role_stmt)
    worker_role = role_res.scalars().first()
    if not worker_role:
        worker_role = Role(name="HEALTH_WORKER", description="Community Health Worker")
        db.add(worker_role)
        await db.flush()

    user = User(
        username=req.username,
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        organization_id=req.organization_id,
    )
    user.roles.append(worker_role)

    db.add(user)
    await db.commit()

    stmt_reload = select(User).where(User.id == user.id).options(selectinload(User.roles))
    res_reload = await db.execute(stmt_reload)
    return res_reload.scalars().first()


@router.post("/login", response_model=Token)
async def login_user(req: UserLogin, db: AsyncSession = Depends(get_async_db)):
    stmt = (
        select(User)
        .where((User.username == req.username_or_email) | (User.email == req.username_or_email))
        .options(selectinload(User.roles))
    )
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    roles = [r.name for r in user.roles]
    permissions = []
    for r in user.roles:
        for p in r.permissions:
            permissions.append(p.name)

    access_token = create_access_token(subject=user.id, roles=roles, permissions=permissions)
    refresh_token = create_refresh_token(subject=user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=3600,
    )


@router.post("/refresh", response_model=Token)
async def refresh_access_token(req: RefreshTokenRequest, db: AsyncSession = Depends(get_async_db)):
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    stmt = select(User).where(User.id == user_id, User.is_active == True)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    roles = [r.name for r in user.roles]
    permissions = [p.name for r in user.roles for p in r.permissions]

    new_access_token = create_access_token(subject=user.id, roles=roles, permissions=permissions)
    new_refresh_token = create_refresh_token(subject=user.id)

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=3600,
    )


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
