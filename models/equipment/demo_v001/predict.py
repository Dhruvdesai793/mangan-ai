import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from schemas.contracts import ModelResult
from models._demo_common import load_active_scenario

def predict(input: dict) -> ModelResult:
    try:
        s = load_active_scenario(input)
        e = s["equipment"]
        risk_score = {"LOW": 0.15, "MEDIUM": 0.45, "HIGH": 0.75}.get(e["risk"], 0.5)
        return ModelResult(
            model_id="equipment", model_version="demo_v001", status="DEMO",
            data_source="SYNTHETIC_SCENARIO",
            prediction={"equipment_id": e["loader_id"], "availability_pct": e["availability_pct"], "failure_risk": risk_score},
        )
    except Exception as ex:
        return ModelResult(model_id="equipment", model_version="demo_v001", status="UNAVAILABLE",
                            data_source="SYNTHETIC_SCENARIO", reason=str(ex))

if __name__ == "__main__":
    print(predict({}).to_dict())
