from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from services.api.dependencies import get_registry
from services.orchestrator.registry import ModelRegistry

router = APIRouter()


@router.get("/models")
def list_models(registry: ModelRegistry = Depends(get_registry)) -> dict:
    return {"summary": registry.summary(), "models": registry.get_active_models()}


@router.get("/models/{model_id}")
def get_model(model_id: str, registry: ModelRegistry = Depends(get_registry)) -> dict:
    model = registry.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="model not found")
    return {"model_id": model_id, **model}
