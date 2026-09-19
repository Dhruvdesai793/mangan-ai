from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from services.api.dependencies import get_moil_provider, get_prediction_repository
from services.persistence.repositories import PredictionRepository
from services.api.schemas.responses import MineResponse
from services.providers.moil_reference import MoilReferenceProvider

router = APIRouter()

@router.get("/mines", response_model=list[MineResponse])
def list_mines(provider: MoilReferenceProvider = Depends(get_moil_provider)) -> list[dict]:
    return provider.list_mines()

@router.get("/mines/{site_id}", response_model=MineResponse)
def get_mine(site_id: str, provider: MoilReferenceProvider = Depends(get_moil_provider)) -> dict:
    mine = provider.get_mine(site_id)
    if mine is None:
        raise HTTPException(status_code=404, detail="unknown site_id")
    return mine

@router.get("/mines/{site_id}/leases")
def get_leases(site_id: str, provider: MoilReferenceProvider = Depends(get_moil_provider)) -> dict:
    mine = provider.get_mine(site_id)
    if mine is None:
        raise HTTPException(status_code=404, detail="unknown site_id")
    result = provider.leases_for_site(site_id)
    if not result["features"]:
        raise HTTPException(status_code=404, detail="no verified lease geometry is mapped to site_id")
    return result

@router.get("/mines/{site_id}/predictions")
def prediction_history(
    site_id: str,
    limit: int = 20,
    provider: MoilReferenceProvider = Depends(get_moil_provider),
    repository: PredictionRepository | None = Depends(get_prediction_repository),
) -> dict:
    if provider.get_mine(site_id) is None:
        raise HTTPException(status_code=404, detail="unknown site_id")
    if repository is None:
        return {"site_id": site_id, "predictions": [], "persistence": "unavailable"}
    return {"site_id": site_id, "predictions": repository.for_site(site_id, max(1, min(limit, 100))), "persistence": "postgresql"}
