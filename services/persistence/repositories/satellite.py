from __future__ import annotations

from sqlalchemy import select

from services.persistence.models import SatelliteFeature
from services.persistence.session import Database


class SatelliteFeatureRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def get(self, cache_key: str) -> dict | None:
        with self.database.session() as session:
            row = session.scalar(select(SatelliteFeature).where(SatelliteFeature.cache_key == cache_key))
            return dict(row.features) if row else None

    def put(self, *, cache_key: str, site_id: str, date_start: str, date_end: str, pipeline_version: str, data_source: str, features: dict) -> None:
        with self.database.session() as session:
            row = session.scalar(select(SatelliteFeature).where(SatelliteFeature.cache_key == cache_key))
            if row:
                row.features = features
                row.data_source = data_source
            else:
                session.add(SatelliteFeature(
                    cache_key=cache_key, site_id=site_id, date_start=date_start, date_end=date_end,
                    pipeline_version=pipeline_version, data_source=data_source, features=features,
                ))
