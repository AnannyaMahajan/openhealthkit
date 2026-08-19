from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ObservationCreate(BaseModel):
    health_record_id: str | None = None
    observation_type: str = Field(
        ..., description="E.g. water_quality, fever_count, blood_pressure"
    )
    value_number: float | None = None
    value_text: str | None = None
    unit: str | None = None
    observed_at: datetime | None = None
    metadata_json: str | None = None


class ObservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    health_record_id: str
    observation_type: str
    value_number: float | None = None
    value_text: str | None = None
    unit: str | None = None
    observed_at: datetime
    metadata_json: str | None = None
    created_at: datetime
    updated_at: datetime


class HealthRecordCreate(BaseModel):
    id: str | None = Field(None, description="Optional client-assigned UUID for offline sync")
    patient_identifier: str = Field(..., description="Anonymized/synthetic patient code")
    age_years: int | None = Field(None, ge=0, le=130)
    gender: str | None = None
    community_id: str | None = None
    metadata_json: str | None = None
    observations: list[ObservationCreate] = []


class HealthRecordUpdate(BaseModel):
    patient_identifier: str | None = None
    age_years: int | None = None
    gender: str | None = None
    community_id: str | None = None
    metadata_json: str | None = None


class HealthRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_identifier: str
    age_years: int | None = None
    gender: str | None = None
    community_id: str | None = None
    metadata_json: str | None = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    observations: list[ObservationRead] = []
