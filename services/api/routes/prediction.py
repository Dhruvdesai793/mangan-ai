from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from services.api.dependencies import get_decision_engine, get_orchestrator, get_prediction_repository
from services.api.schemas.requests import PredictAllRequest, ProspectivityRequest
from services.api.schemas.responses import ModelResultResponse, PredictAllResponse
from services.api.security import rate_limit_prediction
from services.decision_engine.engine import DecisionEngine
from services.orchestrator.orchestrator import PredictionOrchestrator
from services.persistence.repositories import PredictionRepository

router = APIRouter()


@router.post("/predict/prospectivity", response_model=ModelResultResponse, dependencies=[Depends(rate_limit_prediction)])
def predict_prospectivity(
    payload: ProspectivityRequest,
    request: Request,
    orchestrator: PredictionOrchestrator = Depends(get_orchestrator),
) -> dict:
    try:
        result = orchestrator.predict_one(
            "prospectivity",
            scenario_file=orchestrator.input_builder.resolve_scenario_filename(None),
            scenario=orchestrator.input_builder.load_scenario(None),
            features=payload.features.supplied(),
            site_id=None,
            meta=orchestrator.registry.get_model("prospectivity"),
        )
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    request.state.model_results = [result]
    return result.to_dict()


@router.post("/predict/all", response_model=PredictAllResponse, dependencies=[Depends(rate_limit_prediction)])
def predict_all(
    payload: PredictAllRequest,
    request: Request,
    orchestrator: PredictionOrchestrator = Depends(get_orchestrator),
    decision_engine: DecisionEngine = Depends(get_decision_engine),
    prediction_repository: PredictionRepository | None = Depends(get_prediction_repository),
) -> dict:
    request_id = request.state.request_id
    try:
        bundle = orchestrator.predict_all(payload, request_id=request_id)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    request.state.model_results = list(bundle.models.values())
    decision = decision_engine.evaluate(bundle.models)
    response = {
        "request_id": bundle.request_id,
        "scenario_id": bundle.scenario_id,
        "feature_source": bundle.feature_source,
        "models": {model_id: result.to_dict() for model_id, result in bundle.models.items()},
        "decision": decision,
        "limitations": list(dict.fromkeys(bundle.limitations + decision["limitations"])),
    }
    if prediction_repository:
        try:
            prediction_repository.save(
                request_id=bundle.request_id, site_id=payload.site_id, scenario_id=bundle.scenario_id,
                input_snapshot=payload.model_dump(mode="json"), output_snapshot=response,
            )
        except Exception:
            response["limitations"].append("Prediction completed, but persistence was unavailable.")
    return response
