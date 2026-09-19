from __future__ import annotations
from sqlalchemy import select
from services.persistence.models import ExplorationTarget
from services.persistence.session import Database


class ExplorationTargetRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, *, name, latitude, longitude, buffer_m, feature_source, features) -> dict:
        row = ExplorationTarget(name=name, latitude=latitude, longitude=longitude, buffer_m=buffer_m, feature_source=feature_source, features=features)
        with self.database.session() as session:
            session.add(row)
            session.flush()
            return {"target_id": row.id, "name": row.name, "latitude": row.latitude, "longitude": row.longitude, "buffer_m": row.buffer_m, "feature_source": row.feature_source, "created_at": row.created_at.isoformat()}

    def list(self, limit: int = 50) -> list[dict]:
        with self.database.session() as session:
            rows = session.scalars(select(ExplorationTarget).order_by(ExplorationTarget.created_at.desc()).limit(limit)).all()
            return [{"target_id": row.id, "name": row.name, "latitude": row.latitude, "longitude": row.longitude, "buffer_m": row.buffer_m, "feature_source": row.feature_source, "created_at": row.created_at.isoformat()} for row in rows]
