"""Validation utilities for the canonical MOIL reference datasets.

The supplied XLSX is retained as provenance/source material. Runtime model code uses
canonical CSV exports so the API does not depend on spreadsheet tooling.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "external"

EXPECTED_MINE_IDS = {
    "MOIL-BAL-001", "MOIL-UKW-001", "MOIL-TIR-001", "MOIL-SIT-001",
    "MOIL-CHI-001", "MOIL-DON-001", "MOIL-KAN-001", "MOIL-MAN-001",
    "MOIL-GUM-001", "MOIL-BEL-001",
}

def _read(name: str) -> list[dict[str, str]]:
    with (DATA / name).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))

def validate() -> dict[str, object]:
    site_rows = _read("moil_site_catalog.csv")
    grade_rows = _read("moil_grade_reference.csv")
    production_rows = _read("moil_production_reference.csv")
    site_ids = {r["site_id"] for r in site_rows}
    grade_ids = {r["site_id"] for r in grade_rows}
    production_ids = {r["site_id"] for r in production_rows}
    errors: list[str] = []
    if site_ids != EXPECTED_MINE_IDS:
        errors.append(f"site catalog mismatch: {sorted(site_ids ^ EXPECTED_MINE_IDS)}")
    if grade_ids != EXPECTED_MINE_IDS:
        errors.append(f"grade reference mismatch: {sorted(grade_ids ^ EXPECTED_MINE_IDS)}")
    if production_ids != EXPECTED_MINE_IDS:
        errors.append(f"production reference mismatch: {sorted(production_ids ^ EXPECTED_MINE_IDS)}")
    for row in grade_rows:
        if row.get("verification_status", "").startswith("verified") is False:
            errors.append(f"unverified grade row: {row.get('site_id')}")
    return {
        "valid": not errors,
        "errors": errors,
        "site_rows": len(site_rows),
        "grade_rows": len(grade_rows),
        "production_rows": len(production_rows),
    }

if __name__ == "__main__":
    import json
    print(json.dumps(validate(), indent=2))
