from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OrganizationCreate(BaseModel):
    name: str
    code: str
    description: str | None = None


class OrganizationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    code: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class CommunityCreate(BaseModel):
    name: str
    location_name: str | None = None
    organization_id: str | None = None
    attributes_json: str | None = None


class CommunityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    location_name: str | None = None
    organization_id: str | None = None
    attributes_json: str | None = None
    created_at: datetime
    updated_at: datetime
