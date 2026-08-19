import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from openhealthkit.database.session import Base
from openhealthkit.utils.time import utc_now


def generate_uuid_str() -> str:
    return str(uuid.uuid4())


class HealthRecord(Base):
    __tablename__ = "health_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid_str)
    patient_identifier: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    age_years: Mapped[int | None] = mapped_column(nullable=True)
    gender: Mapped[str | None] = mapped_column(String(16), nullable=True)
    community_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("communities.id", ondelete="SET NULL"), nullable=True
    )
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    community: Mapped[Optional["Community"]] = relationship(
        "Community", back_populates="health_records"
    )
    observations: Mapped[list["Observation"]] = relationship(
        "Observation", back_populates="health_record", cascade="all, delete-orphan", lazy="selectin"
    )


class Observation(Base):
    __tablename__ = "observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid_str)
    health_record_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("health_records.id", ondelete="CASCADE"), nullable=False, index=True
    )
    observation_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    value_number: Mapped[float | None] = mapped_column(Float, nullable=True)
    value_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    health_record: Mapped[HealthRecord] = relationship(
        "HealthRecord", back_populates="observations"
    )


from openhealthkit.models.organization import Community  # noqa: E402
