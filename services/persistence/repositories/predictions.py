from __future__ import annotations

from sqlalchemy import select

from services.persistence.models import PredictionRun
from services.persistence.session import Database


class PredictionRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save(self, *, request_id: str, site_id: str | None, scenario_id: str | None, input_snapshot: dict, output_snapshot: dict) -> str:
        row = PredictionRun(
            request_id=request_id, site_id=site_id, scenario_id=scenario_id,
            input_snapshot=input_snapshot, output_snapshot=output_snapshot,
        )
        with self.database.session() as session:
            session.add(row)
            session.flush()
            return row.id

    def for_site(self, site_id: str, limit: int = 20) -> list[dict]:
        with self.database.session() as session:
            rows = session.scalars(
                select(PredictionRun).where(PredictionRun.site_id == site_id)
                .order_by(PredictionRun.created_at.desc()).limit(limit)
            ).all()
            return [{
                "prediction_id": row.id, "request_id": row.request_id, "site_id": row.site_id,
                "scenario_id": row.scenario_id, "output": row.output_snapshot,
                "created_at": row.created_at.isoformat(),
            } for row in rows]
