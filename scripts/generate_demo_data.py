"""
Generates ONE coherent fictional-mine scenario so all demo modules tell the
same story instead of independent random numbers, e.g.:
  heavy rainfall -> equipment availability drops -> production drops -> shortfall risk rises.
Writes scenarios/scenario_*.json (consumed by predict.py in every demo model
and, later, by the frontend).
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCENARIOS_DIR = ROOT / "scenarios"

SCENARIOS = {
    "scenario_01_normal.json": {
        "scenario_id": "scenario_01_normal",
        "mine": "Mine A",
        "zone": "Zone C",
        "narrative": "Normal operating conditions.",
        "weather": {"rainfall_mm_forecast": 8, "risk": "LOW"},
        "equipment": {"loader_id": "L4", "availability_pct": 92, "risk": "LOW"},
        "production": {"target_tonnes": 1000, "predicted_tonnes": 970, "shortfall_probability": 0.12},
        "recovery": {"expected_recovery_pct": 78},
        "blast": {"delay_risk": 0.15},
        "grade": {"mn_grade_percent": 40.5, "interval_low": 37.0, "interval_high": 43.5},
    },
    "scenario_02_rainfall.json": {
        "scenario_id": "scenario_02_rainfall",
        "mine": "Mine A",
        "zone": "Zone C",
        "narrative": "Heavy rainfall forecast reduces equipment availability, which cuts production and raises shortfall risk.",
        "weather": {"rainfall_mm_forecast": 65, "risk": "HIGH"},
        "equipment": {"loader_id": "L4", "availability_pct": 58, "risk": "HIGH"},
        "production": {"target_tonnes": 1000, "predicted_tonnes": 860, "shortfall_probability": 0.81},
        "recovery": {"expected_recovery_pct": 74},
        "blast": {"delay_risk": 0.61},
        "grade": {"mn_grade_percent": 38.7, "interval_low": 34.5, "interval_high": 42.3},
    },
    "scenario_03_equipment_failure.json": {
        "scenario_id": "scenario_03_equipment_failure",
        "mine": "Mine A",
        "zone": "Zone C",
        "narrative": "Loader L4 unplanned downtime independent of weather; production and blast schedule both affected.",
        "weather": {"rainfall_mm_forecast": 5, "risk": "LOW"},
        "equipment": {"loader_id": "L4", "availability_pct": 31, "risk": "HIGH"},
        "production": {"target_tonnes": 1000, "predicted_tonnes": 705, "shortfall_probability": 0.90},
        "recovery": {"expected_recovery_pct": 71},
        "blast": {"delay_risk": 0.74},
        "grade": {"mn_grade_percent": 39.9, "interval_low": 36.0, "interval_high": 43.0},
    },
}


def write_scenarios():
    SCENARIOS_DIR.mkdir(parents=True, exist_ok=True)
    for fname, payload in SCENARIOS.items():
        with open(SCENARIOS_DIR / fname, "w") as f:
            json.dump(payload, f, indent=2)
        print("wrote", fname)


ACTIVE_SCENARIO_FILE = ROOT / "scenarios" / "_active_scenario.txt"


def set_active_scenario(name: str = "scenario_02_rainfall.json"):
    with open(ACTIVE_SCENARIO_FILE, "w") as f:
        f.write(name)


if __name__ == "__main__":
    write_scenarios()
    set_active_scenario()
    print("active scenario set ->", ACTIVE_SCENARIO_FILE.read_text())
