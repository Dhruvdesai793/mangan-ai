"""Shared helper every DEMO model's predict.py uses to load the active scenario."""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCENARIOS_DIR = ROOT / "scenarios"


def load_active_scenario(input: dict = None) -> dict:
    """input can override which scenario file to use via input['scenario_id'];
    otherwise reads scenarios/_active_scenario.txt."""
    if input and input.get("scenario_file"):
        fname = input["scenario_file"]
    else:
        active_file = SCENARIOS_DIR / "_active_scenario.txt"
        fname = active_file.read_text().strip() if active_file.exists() else "scenario_01_normal.json"
    path = SCENARIOS_DIR / fname
    with open(path) as f:
        return json.load(f)
