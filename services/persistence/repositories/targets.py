from __future__ import annotations
from sqlalchemy import select
from services.persistence.models import ExplorationTarget
from services.persistence.session import Database


class ExplorationTargetRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, *, name, latitude, longitude, buffer_m, feature_source, features, model_results=None, decision=None, scenario_id=None) -> dict:
        row = ExplorationTarget(name=name, latitude=latitude, longitude=longitude, buffer_m=buffer_m, feature_source=feature_source, features=features, model_results=model_results or {}, decision=decision or {}, scenario_id=scenario_id)
        with self.database.session() as session:
            session.add(row)
            session.flush()
            return self._summary(row)

    @staticmethod
    def _summary(row):
        return {"target_id": row.id, "name": row.name or f"Coordinate {row.latitude:.5f}, {row.longitude:.5f}", "latitude": row.latitude, "longitude": row.longitude, "buffer_m": row.buffer_m, "feature_source": row.feature_source, "scenario_id": row.scenario_id, "created_at": row.created_at.isoformat()}

    def list(self, limit: int = 50) -> list[dict]:
        with self.database.session() as session:
            rows = session.scalars(select(ExplorationTarget).order_by(ExplorationTarget.created_at.desc()).limit(limit)).all()
            return [self._summary(row) for row in rows]

    def get(self, target_id: str) -> dict | None:
        with self.database.session() as session:
            row = session.get(ExplorationTarget, target_id)
            if not row:
                return None
            return {**self._summary(row), "features": row.features, "models": row.model_results or {}, "decision": row.decision or {}}
