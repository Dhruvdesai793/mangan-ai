from __future__ import annotations

from datetime import datetime, timezone
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from schemas.contracts import ModelResult
from models._reference_common import find_row, require_site_id, to_float


def predict(input: dict) -> ModelResult:
    try:
        site_id = require_site_id(input.get("site_id"))
        row = find_row("moil_grade_reference.csv", site_id)
        if row is None:
            return ModelResult(
                model_id="grade", model_version="v001", status="UNAVAILABLE",
                data_source="MOIL_VERIFIED_PRODUCT_ASSAYS",
                reason=f"No verified product-grade reference is available for site_id={site_id!r}.",
            )
        interval = [to_float(row.get("mn_grade_min")), to_float(row.get("mn_grade_max"))]
        return ModelResult(
            model_id="grade", model_version="v001", status="LIVE",
            data_source="MOIL_VERIFIED_PRODUCT_ASSAYS",
            prediction={
                "scope": "VERIFIED_PRODUCT_GRADE_REFERENCE_NOT_IN_SITU_SPATIAL_PREDICTION",
                "mine_name": row.get("mine_name"),
                "mn_grade_percent": to_float(row.get("mn_grade_percent")),
                "interval": interval,
                "reference_year": int(row["reference_year"]) if row.get("reference_year") else None,
                "assay_id": row.get("assay_id"),
                "sample_id": row.get("sample_id"),
                "product_id": row.get("product_id"),
                "ore_category": row.get("ore_category"),
                "product_form": row.get("product_form"),
                "primary_use": row.get("primary_use"),
                "chemistry": {
                    "mn_pct": to_float(row.get("mn_grade_percent")),
                    "fe_pct": to_float(row.get("fe_pct")),
                    "sio2_pct": to_float(row.get("sio2_pct")),
                    "p_pct": to_float(row.get("p_pct")),
                    "mno2_pct": to_float(row.get("mno2_pct")),
                    "units": row.get("units"),
                },
                "verification_status": row.get("verification_status"),
            },
            uncertainty=None,
            reason="Reference value only; do not interpret as an in-situ spatial grade prediction.",
            prediction_timestamp=datetime.now(timezone.utc).isoformat(),
        )
    except Exception as exc:
        return ModelResult(
            model_id="grade", model_version="v001", status="UNAVAILABLE",
            data_source="MOIL_VERIFIED_PRODUCT_ASSAYS", reason=str(exc),
        )

if __name__ == "__main__":
    print(predict({"site_id": "MOIL-BAL-001"}).to_dict())
