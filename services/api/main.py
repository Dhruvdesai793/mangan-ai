"""FastAPI application entry point for the MANGAN-AI backend prototype."""
from __future__ import annotations

import os
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from services.api.routes import exploration, health, jobs, mines, models, prediction, production, targets
from services.api.security import log_request, new_request_id


def _allowed_origins() -> list[str]:
    raw = os.getenv("MANGAN_ALLOWED_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501")
    origins = [item.strip() for item in raw.split(",") if item.strip()]
    return origins or ["http://localhost:8501"]


def _max_body_bytes() -> int:
    try:
        return max(1024, int(os.getenv("MANGAN_MAX_REQUEST_BODY_BYTES", str(1024 * 1024))))
    except ValueError:
        return 1024 * 1024


def create_app() -> FastAPI:
    app = FastAPI(
        title="MANGAN-AI API",
        version="0.3.0",
        description="Registry-driven mining intelligence API for MANGAN-AI.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Request-ID"],
    )

    @app.middleware("http")
    async def request_boundary(request: Request, call_next):
        request_id = new_request_id(request.headers.get("X-Request-ID"))
        request.state.request_id = request_id
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > _max_body_bytes():
                    return JSONResponse(
                        status_code=413,
                        content={"detail": "request body exceeds configured size limit", "request_id": request_id},
                        headers={"X-Request-ID": request_id},
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "invalid Content-Length header", "request_id": request_id},
                    headers={"X-Request-ID": request_id},
                )

        started = time.perf_counter()
        status_code = 500
        error = None
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            elapsed = (time.perf_counter() - started) * 1000
            model_results = getattr(request.state, "model_results", None) or []
            model_id = ",".join(item.model_id for item in model_results) if model_results else None
            model_version = ",".join(item.model_version for item in model_results) if model_results else None
            model_status = ",".join(item.status for item in model_results) if model_results else None
            log_request(
                request, request_id, status_code, elapsed,
                model_id=model_id, model_version=model_version, status=model_status, error=error,
            )

    @app.middleware("http")
    async def attach_request_id(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    app.include_router(health.router)
    app.include_router(prediction.router)
    app.include_router(exploration.router)
    app.include_router(production.router)
    app.include_router(mines.router)
    app.include_router(models.router)
    app.include_router(jobs.router)
    app.include_router(targets.router)
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "services.api.main:app",
        host=os.getenv("MANGAN_HOST", "0.0.0.0"),
        port=int(os.getenv("MANGAN_PORT", "8000")),
        reload=False,
    )
