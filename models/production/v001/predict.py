from __future__ import annotations

from datetime import datetime, timezone
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from schemas.contracts import ModelResult
from models._reference_common import find_row, require_site_id


def predict(input: dict) -> ModelResult:
    try:
        site_id = require_site_id(input.get("site_id"))
        row = find_row("moil_production_reference.csv", site_id)
        if row is None:
            return ModelResult(
                model_id="production", model_version="v001", status="UNAVAILABLE",
                data_source="MOIL_HISTORICAL_2012",
                reason=f"No verified historical production reference is available for site_id={site_id!r}.",
            )
        return ModelResult(
            model_id="production", model_version="v001", status="LIVE",
            data_source="MOIL_HISTORICAL_2012",
            prediction={
                "scope": "OFFICIAL_HISTORICAL_REFERENCE_NOT_FUTURE_FORECAST",
                "mine_name": row.get("mine_name"),
                "historical_production_tonnes": float(row["historical_production_tonnes"]),
                "reference_year": int(row["reference_year"]),
                "average_grade_label": row.get("average_grade_label"),
                "reserves_a_tonnes": float(row["reserves_a_tonnes"]),
                "resources_b_tonnes": float(row["resources_b_tonnes"]),
                "a_plus_b_tonnes": float(row["a_plus_b_tonnes"]),
                "interpretation_status": row.get("interpretation_status"),
            },
            uncertainty=None,
            reason="Historical context only; this v001 is not a future production or shortfall forecast.",
            prediction_timestamp=datetime.now(timezone.utc).isoformat(),
        )
    except Exception as exc:
        return ModelResult(
            model_id="production", model_version="v001", status="UNAVAILABLE",
            data_source="MOIL_HISTORICAL_2012", reason=str(exc),
        )

if __name__ == "__main__":
    print(predict({"site_id": "MOIL-BAL-001"}).to_dict())
