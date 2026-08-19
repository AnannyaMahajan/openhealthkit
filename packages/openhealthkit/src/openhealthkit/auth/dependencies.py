from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from openhealthkit.auth.jwt import decode_token
from openhealthkit.auth.rbac import SystemPermission, SystemRole
from openhealthkit.database import get_async_db
from openhealthkit.models.user import User

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> User | None:
    if not credentials or not credentials.credentials:
        return None

    token = credentials.credentials
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    stmt = (
        select(User)
        .where(User.id == user_id, User.is_active == True)
        .options(selectinload(User.roles))
    )
    result = await db.execute(stmt)
    user = result.scalars().first()
    return user


async def get_current_user(
    user: User | None = Depends(get_current_user_optional),
) -> User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_permission(required_permission: SystemPermission | str) -> Callable:
    perm_str = (
        required_permission.value
        if isinstance(required_permission, SystemPermission)
        else required_permission
    )

    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_permissions: set[str] = set()
        for role in current_user.roles:
            # Check direct permissions attached to role
            for p in role.permissions:
                user_permissions.add(p.name)
            # Check default RBAC map
            from openhealthkit.auth.rbac import ROLE_PERMISSIONS_MAP, SystemRole

            try:
                sys_role = SystemRole(role.name)
                if sys_role in ROLE_PERMISSIONS_MAP:
                    for perm_enum in ROLE_PERMISSIONS_MAP[sys_role]:
                        user_permissions.add(perm_enum.value)
            except ValueError:
                pass


        if perm_str not in user_permissions and "ADMIN" not in [r.name for r in current_user.roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{perm_str}' required for this resource",
            )
        return current_user

    return permission_checker


def require_role(required_role: SystemRole | str) -> Callable:
    role_str = required_role.value if isinstance(required_role, SystemRole) else required_role

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_names = [r.name for r in current_user.roles]
        if role_str not in user_role_names and "ADMIN" not in user_role_names:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role_str}' required for this resource",
            )
        return current_user

    return role_checker
