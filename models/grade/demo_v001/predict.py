import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from schemas.contracts import ModelResult
from models._demo_common import load_active_scenario

def predict(input: dict) -> ModelResult:
    try:
        s = load_active_scenario(input)
        g = s["grade"]
        return ModelResult(
            model_id="grade", model_version="demo_v001", status="DEMO",
            data_source="SYNTHETIC_SCENARIO",
            prediction={"mn_grade_percent": g["mn_grade_percent"],
                        "interval": [g["interval_low"], g["interval_high"]]},
        )
    except Exception as e:
        return ModelResult(model_id="grade", model_version="demo_v001", status="UNAVAILABLE",
                            data_source="SYNTHETIC_SCENARIO", reason=str(e))

if __name__ == "__main__":
    print(predict({}).to_dict())
