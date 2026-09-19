"""Shared helpers for MOIL reference models.

These are deterministic verified-reference lookups, not trained ML models.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data" / "external"

def load_rows(filename: str) -> list[dict[str, str]]:
    path = DATA_ROOT / filename
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))

def find_row(filename: str, site_id: str) -> dict[str, str] | None:
    for row in load_rows(filename):
        if row.get("site_id") == site_id:
            return row
    return None

def require_site_id(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("site_id is required")
    return value.strip()

def to_float(value: str | None) -> float | None:
    if value in (None, "", "—", "-"):
        return None
    try:
        return float(value)
    except ValueError:
        return None
