from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request

from services.api.dependencies import (
    get_decision_engine,
    get_exploration_map_service,
    get_job_store,
    get_orchestrator,
)
from services.jobs.job_store import JobStore
from services.api.schemas.requests import ExplorationMapRequest, JobRequest, PredictAllRequest, ProductionRequest
from services.api.schemas.responses import JobAcceptedResponse, JobResponse
from services.decision_engine.engine import DecisionEngine
from services.orchestrator.exploration import ExplorationMapService
from services.orchestrator.orchestrator import PredictionOrchestrator

router = APIRouter()


@router.post("/jobs", response_model=JobAcceptedResponse, status_code=202)
def create_job(
    payload: JobRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    orchestrator: PredictionOrchestrator = Depends(get_orchestrator),
    decision_engine: DecisionEngine = Depends(get_decision_engine),
    exploration_service: ExplorationMapService = Depends(get_exploration_map_service),
    job_store: JobStore = Depends(get_job_store),
) -> dict:
    job = job_store.create(payload.job_type, payload.payload)

    def handler():
        if payload.job_type == "exploration_map":
            req = ExplorationMapRequest.model_validate(payload.payload)
            points = exploration_service.get_points(req.limit, req.min_score)
            return {
                **exploration_service.metadata(),
                "point_count": len(points),
                "points": points,
            }

        if payload.job_type == "predict_all":
            req = PredictAllRequest.model_validate(payload.payload)
            bundle = orchestrator.predict_all(req, request_id=request.state.request_id)
            decision = decision_engine.evaluate(bundle.models)
            return {
                "request_id": bundle.request_id,
                "scenario_id": bundle.scenario_id,
                "models": {mid: result.to_dict() for mid, result in bundle.models.items()},
                "decision": decision,
                "limitations": list(dict.fromkeys(bundle.limitations + decision["limitations"])),
            }

        req = ProductionRequest.model_validate(payload.payload)
        combined = PredictAllRequest(scenario_file=req.scenario_file, site_id=req.site_id)
        bundle = orchestrator.predict_all(combined, request_id=request.state.request_id)
        decision = decision_engine.evaluate(bundle.models)
        return {
            "request_id": bundle.request_id,
            "scenario_id": bundle.scenario_id,
            "decision": decision,
            "models": {mid: result.to_dict() for mid, result in bundle.models.items()},
        }

    background_tasks.add_task(job_store.run, job["job_id"], handler)
    return {"job_id": job["job_id"], "status": job["status"]}


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str, job_store: JobStore = Depends(get_job_store)) -> dict:
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job
