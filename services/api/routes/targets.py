from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from services.api.dependencies import get_decision_engine, get_gee_provider, get_orchestrator, get_prediction_repository, get_target_repository
from services.api.schemas.requests import CoordinatePredictionRequest
from services.api.schemas.responses import CoordinatePredictionResponse
from services.decision_engine.engine import DecisionEngine
from services.orchestrator.orchestrator import PredictionOrchestrator
from services.persistence.repositories import ExplorationTargetRepository
from services.persistence.repositories import PredictionRepository
from services.providers.gee import GeeProvider

router = APIRouter()


@router.get("/exploration/targets")
def list_targets(repository: ExplorationTargetRepository | None = Depends(get_target_repository)) -> dict:
    return {"targets": repository.list() if repository else [], "persistence": "postgresql" if repository else "unavailable"}

@router.get("/exploration/targets/{target_id}")
def get_target(target_id: str, repository: ExplorationTargetRepository | None = Depends(get_target_repository)) -> dict:
    if not repository:
        raise HTTPException(status_code=503, detail="target persistence unavailable")
    target = repository.get(target_id)
    if not target:
        raise HTTPException(status_code=404, detail="target not found")
    return target


@router.post("/predict/coordinate", response_model=CoordinatePredictionResponse)
def predict_coordinate(payload: CoordinatePredictionRequest, request: Request, gee: GeeProvider = Depends(get_gee_provider), orchestrator: PredictionOrchestrator = Depends(get_orchestrator), decision_engine: DecisionEngine = Depends(get_decision_engine), repository: ExplorationTargetRepository | None = Depends(get_target_repository), prediction_repository: PredictionRepository | None = Depends(get_prediction_repository)) -> dict:
    try:
        vector = gee.extract_point(payload.latitude, payload.longitude, payload.buffer_m)
        request_model = type("CoordinateRequest", (), {"scenario_file": payload.scenario_file, "prospectivity_features": type("FeatureInput", (), {"supplied": lambda self: vector.features})(), "site_id": None})()
        bundle = orchestrator.predict_all(request_model, request_id=request.state.request_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"coordinate feature extraction failed: {type(exc).__name__}: {exc}") from exc
    decision = decision_engine.evaluate(bundle.models)
    response = {"request_id": bundle.request_id, "scenario_id": bundle.scenario_id, "feature_source": vector.data_source, "target": {"latitude": payload.latitude, "longitude": payload.longitude, "buffer_m": payload.buffer_m, "feature_source": vector.data_source}, "models": {key: value.to_dict() for key, value in bundle.models.items()}, "decision": decision, "limitations": list(dict.fromkeys(bundle.limitations + decision["limitations"]))}
    target = repository.create(name=payload.target_name, latitude=payload.latitude, longitude=payload.longitude, buffer_m=payload.buffer_m, feature_source=vector.data_source, features=vector.features, model_results=response["models"], decision=decision, scenario_id=bundle.scenario_id) if repository else {"latitude": payload.latitude, "longitude": payload.longitude, "buffer_m": payload.buffer_m, "feature_source": vector.data_source}
    response["target"] = target
    request.state.model_results = list(bundle.models.values())
    if prediction_repository:
        prediction_repository.save(request_id=bundle.request_id, site_id=None, scenario_id=bundle.scenario_id, input_snapshot=payload.model_dump(mode="json"), output_snapshot=response)
    return response
