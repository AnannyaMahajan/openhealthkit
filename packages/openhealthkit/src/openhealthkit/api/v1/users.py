from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from openhealthkit.auth import SystemPermission, require_permission
from openhealthkit.database import get_async_db
from openhealthkit.models.user import Role, User
from openhealthkit.schemas.user import RoleRead, UserCreate, UserRead
from openhealthkit.utils.security import hash_password

router = APIRouter(prefix="/users", tags=["Users & Governance"])


@router.get("", response_model=list[UserRead])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission(SystemPermission.USERS_MANAGE)),
):
    stmt = select(User).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    req: UserCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission(SystemPermission.USERS_MANAGE)),
):
    stmt = select(User).where((User.username == req.username) | (User.email == req.email))
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(status_code=400, detail="Username or email already exists")

    user = User(
        username=req.username,
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        organization_id=req.organization_id,
    )

    if req.role_names:
        r_stmt = select(Role).where(Role.name.in_(req.role_names))
        r_res = await db.execute(r_stmt)
        user.roles = r_res.scalars().all()

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/roles", response_model=list[RoleRead])
async def list_roles(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission(SystemPermission.RECORDS_READ)),
):
    stmt = select(Role)
    res = await db.execute(stmt)
    return res.scalars().all()
