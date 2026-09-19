"""Pydantic HTTP response contracts."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ModelResultResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_id: str
    model_version: str
    status: Literal["LIVE", "DEMO", "UNAVAILABLE"]
    prediction: Any | None = None
    uncertainty: float | None = None
    data_source: str
    prediction_timestamp: str
    reason: str | None = None


class DecisionAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str
    reason: str
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    requires_human_approval: bool = True


class DecisionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_level: Literal["HIGH", "MEDIUM", "LOW"]
    primary_drivers: list[str] = Field(default_factory=list)
    secondary_drivers: list[str] = Field(default_factory=list)
    recommended_actions: list[DecisionAction] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)


class PredictAllResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    scenario_id: str
    feature_source: str | None = None
    models: dict[str, ModelResultResponse]
    decision: DecisionResponse
    limitations: list[str] = Field(default_factory=list)


class CoordinatePredictionResponse(PredictAllResponse):
    target: dict[str, Any]


class MineResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    site_id: str
    mine_name: str
    state: str
    district: str
    latitude: float
    longitude: float
    mining_method: str
    operational_status: str
    source_id: str


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]
    service: str
    registry: dict[str, int]
    database: Literal["connected", "fallback"]
    gee: Literal["enabled", "disabled"]


class MapPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    latitude: float
    longitude: float
    prospectivity: float
    uncertainty: float | None = None
    status: Literal["LIVE", "DEMO", "UNAVAILABLE"]


class ExplorationMapResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data_source: str
    model_version: str
    point_count: int
    points: list[MapPoint]


class ProductionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    scenario_id: str
    data_source: str
    production: ModelResultResponse
    equipment: ModelResultResponse
    weather: ModelResultResponse
    recovery: ModelResultResponse
    blast: ModelResultResponse
    grade: ModelResultResponse
    decision: DecisionResponse
    limitations: list[str] = Field(default_factory=list)


class JobAcceptedResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: str
    status: Literal["QUEUED", "RUNNING", "COMPLETED", "FAILED"]


class JobResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: str
    job_type: str
    status: Literal["QUEUED", "RUNNING", "COMPLETED", "FAILED"]
    created_at: str
    updated_at: str
    result: Any | None = None
    error: str | None = None
