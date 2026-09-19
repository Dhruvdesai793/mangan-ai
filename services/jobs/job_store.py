"""Small in-process job store used until a persistent worker queue is introduced."""
from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Callable

from services.persistence.repositories import DatabaseJobRepository


class JobStore:
    STATUSES = {"QUEUED", "RUNNING", "COMPLETED", "FAILED"}

    def __init__(self, repository: DatabaseJobRepository | None = None) -> None:
        self._lock = threading.Lock()
        self._jobs: dict[str, dict[str, Any]] = {}
        self.repository = repository

    def create(self, job_type: str, payload: dict | None = None) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        job = {
            "job_id": job_id,
            "job_type": job_type,
            "status": "QUEUED",
            "created_at": now,
            "updated_at": now,
            "result": None,
            "error": None,
        }
        if self.repository:
            try:
                return self.repository.create(job_id, job_type, payload or {})
            except Exception:
                pass
        with self._lock:
            self._jobs[job_id] = job
        return dict(job)

    def get(self, job_id: str) -> dict[str, Any] | None:
        if self.repository:
            try:
                row = self.repository.get(job_id)
                if row:
                    return row
            except Exception:
                pass
        with self._lock:
            job = self._jobs.get(job_id)
            return dict(job) if job else None

    def run(self, job_id: str, handler: Callable[[], Any]) -> None:
        self._set(job_id, status="RUNNING", error=None)
        try:
            result = handler()
        except Exception as exc:
            self._set(job_id, status="FAILED", error=f"{type(exc).__name__}: {exc}")
            return
        self._set(job_id, status="COMPLETED", result=result, error=None)

    def _set(self, job_id: str, **updates: Any) -> None:
        if self.repository:
            try:
                self.repository.update(job_id, **updates)
                return
            except Exception:
                pass
        with self._lock:
            if job_id not in self._jobs:
                return
            self._jobs[job_id].update(updates)
            self._jobs[job_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
