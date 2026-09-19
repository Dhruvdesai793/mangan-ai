"""Pydantic HTTP request contracts."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProspectivityFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sentinel2_b2: float | None = Field(default=None, ge=0, le=1)
    sentinel2_b3: float | None = Field(default=None, ge=0, le=1)
    sentinel2_b4: float | None = Field(default=None, ge=0, le=1)
    sentinel2_b8: float | None = Field(default=None, ge=0, le=1)
    sentinel2_b11: float | None = Field(default=None, ge=0, le=1)
    sentinel2_b12: float | None = Field(default=None, ge=0, le=1)
    ndvi: float | None = Field(default=None, ge=-1, le=1)
    ndmi: float | None = Field(default=None, ge=-1, le=1)
    elevation_m: float | None = Field(default=None, ge=-1000, le=10000)
    slope_deg: float | None = Field(default=None, ge=0, le=90)
    curvature: float | None = Field(default=None, ge=-1000, le=1000)
    geology_class: str | None = Field(default=None, min_length=1, max_length=80)

    @field_validator("geology_class")
    @classmethod
    def validate_geology_class(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("geology_class must not be blank")
        return cleaned

    def supplied(self) -> dict:
        return self.model_dump(exclude_none=True)


class PredictAllRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_file: str | None = Field(default=None, max_length=120)
    prospectivity_features: ProspectivityFeatures | None = None
    site_id: str | None = Field(default=None, pattern=r"^MOIL-[A-Z]{3}-\d{3}$")


class ProspectivityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    features: ProspectivityFeatures


class ProductionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_file: str | None = Field(default=None, max_length=120)
    site_id: str | None = Field(default=None, pattern=r"^MOIL-[A-Z]{3}-\d{3}$")


class ExplorationMapRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int = Field(default=2000, ge=1, le=2000)
    min_score: float | None = Field(default=None, ge=0, le=1)


class JobRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_type: Literal["exploration_map", "predict_all", "production"]
    payload: dict = Field(default_factory=dict)

    @field_validator("payload")
    @classmethod
    def validate_payload_size(cls, value: dict) -> dict:
        if len(value) > 25:
            raise ValueError("payload may contain at most 25 top-level fields")
        return value
