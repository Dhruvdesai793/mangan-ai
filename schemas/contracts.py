"""
Shared ModelResult contract. Every model's predict.py (LIVE or DEMO) returns
this object. The API/frontend orchestrator only ever depends on this shape --
never on model internals.
"""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Optional
import json

VALID_STATUSES = {"LIVE", "DEMO", "UNAVAILABLE"}


@dataclass
class ModelResult:
    model_id: str
    model_version: str
    status: str
    data_source: str
    prediction: Optional[Any] = None
    uncertainty: Optional[float] = None
    reason: Optional[str] = None
    prediction_timestamp: str = None

    def __post_init__(self):
        if self.status not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}, got {self.status}")
        if self.status == "UNAVAILABLE" and not self.reason:
            raise ValueError("status=UNAVAILABLE requires a non-empty reason")
        if self.prediction_timestamp is None:
            self.prediction_timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
