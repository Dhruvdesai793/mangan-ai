"""SQLAlchemy models. Alembic remains the schema source of truth."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


JSON_TYPE = JSON().with_variant(JSONB, "postgresql")


class Base(DeclarativeBase):
    pass


class Mine(Base):
    __tablename__ = "mines"
    id: Mapped[int] = mapped_column(primary_key=True)
    site_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    mine_name: Mapped[str] = mapped_column(String(160))
    state: Mapped[str] = mapped_column(String(80))
    district: Mapped[str] = mapped_column(String(80))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    mining_method: Mapped[str] = mapped_column(String(80))
    operational_status: Mapped[str] = mapped_column(String(80))
    source_id: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    leases: Mapped[list["MineLease"]] = relationship(back_populates="mine", cascade="all, delete-orphan")


class MineLease(Base):
    __tablename__ = "mine_leases"
    __table_args__ = (UniqueConstraint("source_record_id", name="uq_mine_leases_source_record"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    mine_id: Mapped[int] = mapped_column(ForeignKey("mines.id", ondelete="CASCADE"), index=True)
    site_id: Mapped[str] = mapped_column(String(32), index=True)
    source: Mapped[str] = mapped_column(String(120))
    source_record_id: Mapped[str] = mapped_column(String(160))
    verification_status: Mapped[str] = mapped_column(String(80))
    dataset_vintage: Mapped[str] = mapped_column(String(40))
    properties: Mapped[dict] = mapped_column(JSON_TYPE, default=dict)
    geometry: Mapped[object] = mapped_column(Geometry("MULTIPOLYGON", srid=4326, spatial_index=True))
    mine: Mapped[Mine] = relationship(back_populates="leases")


class GradeReference(Base):
    __tablename__ = "grade_references"
    id: Mapped[int] = mapped_column(primary_key=True)
    site_id: Mapped[str] = mapped_column(String(32), index=True)
    source_record_id: Mapped[str] = mapped_column(String(160), unique=True)
    payload: Mapped[dict] = mapped_column(JSON_TYPE)


class ProductionReference(Base):
    __tablename__ = "production_references"
    id: Mapped[int] = mapped_column(primary_key=True)
    site_id: Mapped[str] = mapped_column(String(32), index=True)
    source_record_id: Mapped[str] = mapped_column(String(160), unique=True)
    reference_year: Mapped[str] = mapped_column(String(24), index=True)
    payload: Mapped[dict] = mapped_column(JSON_TYPE)


class SatelliteFeature(Base):
    __tablename__ = "satellite_features"
    __table_args__ = (UniqueConstraint("cache_key", name="uq_satellite_features_cache_key"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    cache_key: Mapped[str] = mapped_column(String(256))
    site_id: Mapped[str] = mapped_column(String(32), index=True)
    date_start: Mapped[str] = mapped_column(String(10))
    date_end: Mapped[str] = mapped_column(String(10))
    pipeline_version: Mapped[str] = mapped_column(String(32))
    data_source: Mapped[str] = mapped_column(String(160))
    features: Mapped[dict] = mapped_column(JSON_TYPE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class ExplorationTarget(Base):
    __tablename__ = "exploration_targets"
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: f"target_{uuid.uuid4().hex[:20]}")
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    buffer_m: Mapped[int] = mapped_column(Integer, default=250)
    feature_source: Mapped[str] = mapped_column(String(160))
    features: Mapped[dict] = mapped_column(JSON_TYPE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class PredictionRun(Base):
    __tablename__ = "prediction_runs"
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: f"pred_{uuid.uuid4().hex}")
    request_id: Mapped[str] = mapped_column(String(64), index=True)
    site_id: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    scenario_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    input_snapshot: Mapped[dict] = mapped_column(JSON_TYPE)
    output_snapshot: Mapped[dict] = mapped_column(JSON_TYPE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    job_type: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(24), index=True)
    payload: Mapped[dict] = mapped_column(JSON_TYPE, default=dict)
    result: Mapped[dict | None] = mapped_column(JSON_TYPE, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


Index("ix_prediction_request_created", PredictionRun.request_id, PredictionRun.created_at)
