"""Deterministic decision thresholds for the prototype decision engine."""
from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionRules:
    production_shortfall_pct: float = 0.10
    production_shortfall_probability: float = 0.70
    equipment_failure_risk: float = 0.70
    equipment_availability_pct: float = 70.0
    weather_rainfall_mm: float = 50.0
    blast_delay_risk: float = 0.60
    recovery_pct: float = 75.0
    high_risk_driver_count: int = 2


DEFAULT_RULES = DecisionRules()
