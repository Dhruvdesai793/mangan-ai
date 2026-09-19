from __future__ import annotations

from services.persistence.models import Job
from services.persistence.session import Database


class DatabaseJobRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    @staticmethod
    def _dict(row: Job) -> dict:
        return {
            "job_id": row.id, "job_type": row.job_type, "status": row.status,
            "created_at": row.created_at.isoformat(), "updated_at": row.updated_at.isoformat(),
            "result": row.result, "error": row.error,
        }

    def create(self, job_id: str, job_type: str, payload: dict) -> dict:
        row = Job(id=job_id, job_type=job_type, status="QUEUED", payload=payload)
        with self.database.session() as session:
            session.add(row)
            session.flush()
            return self._dict(row)

    def get(self, job_id: str) -> dict | None:
        with self.database.session() as session:
            row = session.get(Job, job_id)
            return self._dict(row) if row else None

    def update(self, job_id: str, **updates) -> None:
        with self.database.session() as session:
            row = session.get(Job, job_id)
            if row:
                for key, value in updates.items():
                    setattr(row, key, value)
