"""Idempotently seed canonical MOIL reference data and official lease geometry."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from geoalchemy2.shape import from_shape
from shapely.geometry import shape
from sqlalchemy import select

from services.persistence.models import GradeReference, Mine, MineLease, ProductionReference
from services.persistence.session import Database

DATA = ROOT / "data" / "external"


def rows(filename: str) -> list[dict[str, str]]:
    with (DATA / filename).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def seed(database: Database | None = None) -> dict[str, int]:
    database = database or Database()
    counts = {"mines": 0, "leases": 0, "grades": 0, "production": 0}
    with database.session() as session:
        for record in rows("moil_site_catalog.csv"):
            mine = session.scalar(select(Mine).where(Mine.site_id == record["site_id"]))
            values = {key: record[key] for key in ("mine_name", "state", "district", "mining_method", "operational_status", "source_id")}
            values.update(latitude=float(record["latitude"]), longitude=float(record["longitude"]))
            if mine:
                for key, value in values.items(): setattr(mine, key, value)
            else:
                session.add(Mine(site_id=record["site_id"], **values))
            counts["mines"] += 1
        session.flush()

        geo = json.loads((DATA / "geometries" / "ngdr_moil_major_mining_leases_2022.geojson").read_text())
        for feature in geo.get("features", []):
            props = feature.get("properties") or {}
            mine = session.scalar(select(Mine).where(Mine.site_id == props.get("site_id")))
            if not mine: continue
            source_record_id = str(feature.get("id") or props.get("feature_id"))
            lease = session.scalar(select(MineLease).where(MineLease.source_record_id == source_record_id))
            values = dict(
                mine_id=mine.id, site_id=mine.site_id, source=str(props.get("source_id", "NGDR-ML-2022")),
                verification_status=str(props.get("mapping_status", "VERIFIED")),
                dataset_vintage=str(props.get("source_dataset_vintage", 2022)), properties=props,
                geometry=from_shape(shape(feature["geometry"]), srid=4326),
            )
            if lease:
                for key, value in values.items(): setattr(lease, key, value)
            else:
                session.add(MineLease(source_record_id=source_record_id, **values))
            counts["leases"] += 1

        for record in rows("moil_grade_reference.csv"):
            key = str(record.get("assay_id") or record.get("product_id") or record["site_id"])
            row = session.scalar(select(GradeReference).where(GradeReference.source_record_id == key))
            if row: row.payload = record
            else: session.add(GradeReference(site_id=record["site_id"], source_record_id=key, payload=record))
            counts["grades"] += 1

        for record in rows("moil_production_reference.csv"):
            key = f'{record["site_id"]}:{record["reference_year"]}'
            row = session.scalar(select(ProductionReference).where(ProductionReference.source_record_id == key))
            if row: row.payload = record
            else: session.add(ProductionReference(site_id=record["site_id"], source_record_id=key, reference_year=record["reference_year"], payload=record))
            counts["production"] += 1
    return counts


if __name__ == "__main__":
    print(json.dumps(seed(), indent=2))
