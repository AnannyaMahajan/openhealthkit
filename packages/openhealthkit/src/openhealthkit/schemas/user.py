from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class PermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None
    permissions: list[PermissionRead] = []


class RoleCreate(BaseModel):
    name: str
    description: str | None = None
    permission_ids: list[str] = []


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: EmailStr
    full_name: str | None = None
    is_active: bool
    organization_id: str | None = None
    created_at: datetime
    updated_at: datetime
    roles: list[RoleRead] = []


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None
    organization_id: str | None = None
    role_names: list[str] = ["HEALTH_WORKER"]


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None
    role_names: list[str] | None = None
