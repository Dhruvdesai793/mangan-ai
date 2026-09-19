"""MOIL reference-data provider used by API routes.

It serves only repository-owned canonical data and NGDR lease geometry.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from services.persistence.repositories.mines import MineRepository

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "external"

class MoilReferenceProvider:
    def __init__(self, data_dir: Path | None = None, repository: MineRepository | None = None) -> None:
        self.data_dir = data_dir or DATA
        self.repository = repository

    def _read(self, filename: str) -> list[dict[str, str]]:
        with (self.data_dir / filename).open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def list_mines(self) -> list[dict[str, Any]]:
        if self.repository:
            try:
                rows = self.repository.list()
                if rows:
                    return rows
            except Exception:
                pass
        return [
            {
                "site_id": r["site_id"], "mine_name": r["mine_name"],
                "state": r["state"], "district": r["district"],
                "latitude": float(r["latitude"]), "longitude": float(r["longitude"]),
                "mining_method": r["mining_method"], "operational_status": r["operational_status"],
                "source_id": r["source_id"],
            }
            for r in self._read("moil_site_catalog.csv")
        ]

    def get_mine(self, site_id: str) -> dict[str, Any] | None:
        if self.repository:
            try:
                mine = self.repository.get(site_id)
                if mine:
                    return mine
            except Exception:
                pass
        return next((m for m in self.list_mines() if m["site_id"] == site_id), None)

    def leases_for_site(self, site_id: str) -> dict[str, Any]:
        if self.repository:
            try:
                result = self.repository.leases(site_id)
                if result["features"]:
                    return result
            except Exception:
                pass
        path = self.data_dir / "geometries" / "ngdr_moil_major_mining_leases_2022.geojson"
        with path.open("r", encoding="utf-8") as handle:
            obj = json.load(handle)
        features = [f for f in obj.get("features", []) if (f.get("properties") or {}).get("site_id") == site_id]
        return {"type": "FeatureCollection", "features": features, "metadata": {"source": "NGDR-ML-2022", "site_id": site_id, "official_source": True, "dataset_vintage": 2022}}
