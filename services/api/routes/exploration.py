from fastapi import APIRouter, Depends

from services.api.dependencies import get_exploration_map_service
from services.api.schemas.requests import ExplorationMapRequest
from services.api.schemas.responses import ExplorationMapResponse
from services.api.security import rate_limit_prediction
from services.orchestrator.exploration import ExplorationMapService

router = APIRouter()


@router.post("/exploration/map", response_model=ExplorationMapResponse, dependencies=[Depends(rate_limit_prediction)])
def exploration_map(
    payload: ExplorationMapRequest,
    service: ExplorationMapService = Depends(get_exploration_map_service),
) -> dict:
    points = service.get_points(limit=payload.limit, min_score=payload.min_score)
    metadata = service.metadata()
    return {
        **metadata,
        "point_count": len(points),
        "points": points,
    }
