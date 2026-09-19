"""Backend-side DTO helpers that sit above the existing ModelResult contract."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from schemas.contracts import ModelResult, VALID_STATUSES


@dataclass
class PredictionBundle:
    """Collected specialist-model results plus request/scenario metadata."""

    request_id: str
    scenario_id: str
    models: dict[str, ModelResult] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)
    feature_source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "scenario_id": self.scenario_id,
            "models": {model_id: result.to_dict() for model_id, result in self.models.items()},
            "limitations": list(self.limitations),
            "feature_source": self.feature_source,
        }


def validate_model_result(result: Any, expected_model_id: str, expected_version: str) -> ModelResult:
    """Validate a specialist model's returned result against the shared contract."""
    if isinstance(result, ModelResult):
        normalized = result
    elif isinstance(result, dict):
        normalized = ModelResult(**result)
    else:
        raise TypeError(f"model returned unsupported result type: {type(result).__name__}")

    if normalized.model_id != expected_model_id:
        raise ValueError(
            f"model_id mismatch: expected {expected_model_id!r}, got {normalized.model_id!r}"
        )
    if normalized.model_version != expected_version:
        raise ValueError(
            f"model_version mismatch for {expected_model_id!r}: "
            f"expected {expected_version!r}, got {normalized.model_version!r}"
        )
    if normalized.status not in VALID_STATUSES:
        raise ValueError(f"invalid model status: {normalized.status!r}")
    if not normalized.data_source:
        raise ValueError("model result requires a non-empty data_source")
    if normalized.status == "UNAVAILABLE" and not normalized.reason:
        raise ValueError("UNAVAILABLE model result requires a reason")
    return normalized
