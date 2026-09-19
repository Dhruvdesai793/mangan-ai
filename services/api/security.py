"""Prototype security controls: request IDs, structured logging, CORS helpers, and rate limiting."""
from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Callable

from fastapi import HTTPException, Request


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extras = getattr(record, "structured", None)
        if isinstance(extras, dict):
            payload.update(extras)
        return json.dumps(payload, separators=(",", ":"))


logger = logging.getLogger("mangan_ai.api")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False


@dataclass(frozen=True)
class RateLimitSettings:
    requests: int = 120
    window_seconds: int = 60


def load_rate_limit_settings() -> RateLimitSettings:
    try:
        requests = max(1, int(os.getenv("MANGAN_RATE_LIMIT_REQUESTS", "120")))
    except ValueError:
        requests = 120
    try:
        window = max(1, int(os.getenv("MANGAN_RATE_LIMIT_WINDOW_SECONDS", "60")))
    except ValueError:
        window = 60
    return RateLimitSettings(requests=requests, window_seconds=window)


class InProcessRateLimiter:
    def __init__(self, settings: RateLimitSettings | None = None) -> None:
        self.settings = settings or load_rate_limit_settings()
        self._lock = threading.Lock()
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def check(self, request: Request) -> None:
        if os.getenv("MANGAN_ENV", "development").lower() == "test":
            return
        key = request.client.host if request.client else "unknown"
        now = time.monotonic()
        cutoff = now - self.settings.window_seconds
        with self._lock:
            events = self._events[key]
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= self.settings.requests:
                raise HTTPException(status_code=429, detail="rate limit exceeded")
            events.append(now)


rate_limiter = InProcessRateLimiter()


def new_request_id(value: str | None) -> str:
    if value and 8 <= len(value) <= 100 and all(c.isalnum() or c in "-_." for c in value):
        return value
    return f"req_{uuid.uuid4().hex[:16]}"


def log_request(request: Request, request_id: str, status_code: int, elapsed_ms: float, model_id: str | None = None,
                model_version: str | None = None, status: str | None = None, error: str | None = None) -> None:
    logger.info(
        "request_complete",
        extra={
            "structured": {
                "request_id": request_id,
                "endpoint": request.url.path,
                "timestamp": time.time(),
                "model_id": model_id,
                "model_version": model_version,
                "status": status,
                "processing_time_ms": round(elapsed_ms, 3),
                "error": error,
            }
        },
    )


def rate_limit_prediction(request: Request) -> None:
    rate_limiter.check(request)
