from fastapi import APIRouter, Depends

from services.api.dependencies import database_available, get_registry
from config import get_settings
from services.api.schemas.responses import HealthResponse
from services.orchestrator.registry import ModelRegistry

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(registry: ModelRegistry = Depends(get_registry)) -> dict:
    return {
        "status": "ok",
        "service": "mangan-ai-api",
        "registry": registry.summary(),
        "database": "connected" if database_available() else "fallback",
        "gee": "enabled" if get_settings().gee_enabled else "disabled",
    }
