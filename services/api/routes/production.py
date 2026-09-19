from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from services.api.dependencies import get_decision_engine, get_orchestrator
from services.api.schemas.requests import PredictAllRequest, ProductionRequest
from services.api.schemas.responses import ProductionResponse
from services.api.security import rate_limit_prediction
from services.decision_engine.engine import DecisionEngine
from services.orchestrator.orchestrator import PredictionOrchestrator

router = APIRouter()


@router.post("/production", response_model=ProductionResponse, dependencies=[Depends(rate_limit_prediction)])
def production(
    payload: ProductionRequest,
    request: Request,
    orchestrator: PredictionOrchestrator = Depends(get_orchestrator),
    decision_engine: DecisionEngine = Depends(get_decision_engine),
) -> dict:
    combined = PredictAllRequest(scenario_file=payload.scenario_file, site_id=payload.site_id)
    try:
        bundle = orchestrator.predict_all(combined, request_id=request.state.request_id)
        request.state.model_results = list(bundle.models.values())
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    decision = decision_engine.evaluate(bundle.models)
    models = bundle.models
    return {
        "request_id": bundle.request_id,
        "scenario_id": bundle.scenario_id,
        "data_source": "MIXED_SOURCE",
        "production": models["production"].to_dict(),
        "equipment": models["equipment"].to_dict(),
        "weather": models["weather"].to_dict(),
        "recovery": models["recovery"].to_dict(),
        "blast": models["blast"].to_dict(),
        "grade": models["grade"].to_dict(),
        "decision": decision,
        "limitations": list(dict.fromkeys(bundle.limitations + decision["limitations"])),
    }
