import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from schemas.contracts import ModelResult
from models._demo_common import load_active_scenario

def predict(input: dict) -> ModelResult:
    try:
        s = load_active_scenario(input)
        r = s["recovery"]
        return ModelResult(
            model_id="recovery", model_version="demo_v001", status="DEMO",
            data_source="SYNTHETIC_SCENARIO",
            prediction={"expected_recovery_pct": r["expected_recovery_pct"]},
        )
    except Exception as e:
        return ModelResult(model_id="recovery", model_version="demo_v001", status="UNAVAILABLE",
                            data_source="SYNTHETIC_SCENARIO", reason=str(e))

if __name__ == "__main__":
    print(predict({}).to_dict())
