"""
Writes rows that failed schema_validation to a quarantine file instead of
silently dropping them, with the reason attached, so a bad Team 1/Team 2
delivery is diagnosable rather than mysteriously shrinking the dataset.
"""
import json
import pathlib
from datetime import datetime, timezone

QUARANTINE_DIR = pathlib.Path(__file__).resolve().parents[2] / "data" / "prospectivity" / "raw" / "_quarantine"


def quarantine_rows(bad_rows: list, source_label: str) -> str:
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    out_path = QUARANTINE_DIR / f"quarantine_{source_label}_{ts}.json"
    with open(out_path, "w") as f:
        json.dump({"source": source_label, "quarantined_at": ts, "rows": bad_rows}, f, indent=2)
    return str(out_path)
