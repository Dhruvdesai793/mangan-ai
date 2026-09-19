"""Stable application-layer facade over the trusted model registry."""
from __future__ import annotations

from typing import Any
from schemas.contracts import ModelResult
from services.orchestrator.registry import ModelRegistry
from services.orchestrator.contracts import validate_model_result

class ModelService:
    def __init__(self, registry: ModelRegistry) -> None:
        self.registry = registry

    def predict(self, model_id: str, payload: dict[str, Any]) -> ModelResult:
        meta = self.registry.get_model(model_id)
        if meta is None:
            return ModelResult(model_id=model_id, model_version="unknown", status="UNAVAILABLE", data_source="MODEL_SERVICE", reason="model is not registered")
        try:
            fn = self.registry.import_predict(model_id, meta)
            return validate_model_result(fn(payload), model_id, meta["version"])
        except Exception as exc:
            return ModelResult(model_id=model_id, model_version=meta["version"], status="UNAVAILABLE", data_source=meta.get("source") or "MODEL_SERVICE", reason=f"model execution failed: {type(exc).__name__}: {exc}")
