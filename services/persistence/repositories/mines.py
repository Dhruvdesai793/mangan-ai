from __future__ import annotations

import json

from geoalchemy2.functions import ST_AsGeoJSON
from sqlalchemy import select

from services.persistence.models import Mine, MineLease
from services.persistence.session import Database


class MineRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    @staticmethod
    def _mine(row: Mine) -> dict:
        return {key: getattr(row, key) for key in (
            "site_id", "mine_name", "state", "district", "latitude", "longitude",
            "mining_method", "operational_status", "source_id",
        )}

    def list(self) -> list[dict]:
        with self.database.session() as session:
            rows = session.scalars(select(Mine).order_by(Mine.mine_name)).all()
            return [self._mine(row) for row in rows]

    def get(self, site_id: str) -> dict | None:
        with self.database.session() as session:
            row = session.scalar(select(Mine).where(Mine.site_id == site_id))
            return self._mine(row) if row else None

    def leases(self, site_id: str) -> dict:
        with self.database.session() as session:
            rows = session.execute(
                select(MineLease, ST_AsGeoJSON(MineLease.geometry)).where(MineLease.site_id == site_id)
            ).all()
        features = [
            {
                "type": "Feature",
                "geometry": json.loads(geometry_json),
                "properties": {**(lease.properties or {}), "site_id": lease.site_id},
            }
            for lease, geometry_json in rows
        ]
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {"source": "NGDR-ML-2022", "site_id": site_id, "official_source": True, "dataset_vintage": 2022},
        }
