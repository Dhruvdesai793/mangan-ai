import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from schemas.contracts import ModelResult
from models._demo_common import load_active_scenario

def predict(input: dict) -> ModelResult:
    try:
        s = load_active_scenario(input)
        p = s["production"]
        return ModelResult(
            model_id="production", model_version="demo_v001", status="DEMO",
            data_source="SYNTHETIC_SCENARIO",
            prediction={"target_tonnes": p["target_tonnes"], "predicted_tonnes": p["predicted_tonnes"]},
            uncertainty=p["shortfall_probability"],
        )
    except Exception as e:
        return ModelResult(model_id="production", model_version="demo_v001", status="UNAVAILABLE",
                            data_source="SYNTHETIC_SCENARIO", reason=str(e))

if __name__ == "__main__":
    print(predict({}).to_dict())
