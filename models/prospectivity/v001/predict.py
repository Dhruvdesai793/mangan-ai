"""
Prospectivity model prediction interface -- the ONLY function anything
outside this folder should call.

    from models.prospectivity.v001.predict import predict
    result = predict({"sentinel2_b2": 0.08, ..., "geology_class": "gondite"})
    result.to_dict()

Never import model.pkl directly from elsewhere -- go through this function so
a future v002 (trained on real Team 2 data) is a drop-in swap.
"""
import pickle
import pathlib
import json
import sys

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parents[2]))  # repo root, for schemas.contracts
from schemas.contracts import ModelResult

_MODEL = None
_FEATURE_COLS = None


def _load():
    global _MODEL, _FEATURE_COLS
    if _MODEL is None:
        with open(_HERE / "model.pkl", "rb") as f:
            _MODEL = pickle.load(f)
        with open(_HERE / "feature_schema.json") as f:
            _FEATURE_COLS = json.load(f)["feature_columns_in_order"]
    return _MODEL, _FEATURE_COLS


def _vectorize(input: dict, feature_cols: list) -> list:
    row = {}
    row["b11_b12_ratio"] = input["sentinel2_b11"] / (input["sentinel2_b12"] or 1e-6)
    row["ferrous_index"] = (input["sentinel2_b11"] - input["sentinel2_b8"]) / (
        (input["sentinel2_b11"] + input["sentinel2_b8"]) or 1e-6)
    for k in ["sentinel2_b2", "sentinel2_b3", "sentinel2_b4", "sentinel2_b8", "sentinel2_b11",
              "sentinel2_b12", "ndvi", "ndmi", "elevation_m", "slope_deg", "curvature"]:
        row[k] = input[k]
    geo_col = f"geo_{input['geology_class']}"
    for c in feature_cols:
        if c.startswith("geo_"):
            row.setdefault(c, 0)
    row[geo_col] = 1 if geo_col in feature_cols else row.get(geo_col, 0)
    return [row.get(c, 0) for c in feature_cols]


REQUIRED_FIELDS = ["sentinel2_b2", "sentinel2_b3", "sentinel2_b4", "sentinel2_b8", "sentinel2_b11",
                    "sentinel2_b12", "ndvi", "ndmi", "elevation_m", "slope_deg", "curvature", "geology_class"]


def predict(input: dict) -> ModelResult:
    missing = [f for f in REQUIRED_FIELDS if f not in input]
    if missing:
        return ModelResult(
            model_id="prospectivity", model_version="v001", status="UNAVAILABLE",
            data_source="PUBLIC_DATA_SYNTHETIC_FALLBACK",
            reason=f"missing required input fields: {missing}",
        )
    try:
        import pandas as pd
        model, feature_cols = _load()
        x = pd.DataFrame([_vectorize(input, feature_cols)], columns=feature_cols)
        proba = float(model.predict_proba(x)[0][1])
        # crude per-tree spread across the forest as an uncertainty proxy
        tree_probas = [t.predict_proba(x.values)[0][1] for t in model.estimators_]
        uncertainty = float(pd_std(tree_probas))
        return ModelResult(
            model_id="prospectivity", model_version="v001", status="LIVE",
            data_source="PUBLIC_DATA_SYNTHETIC_FALLBACK",
            prediction=round(proba, 4), uncertainty=round(uncertainty, 4),
        )
    except Exception as e:
        return ModelResult(
            model_id="prospectivity", model_version="v001", status="UNAVAILABLE",
            data_source="PUBLIC_DATA_SYNTHETIC_FALLBACK", reason=str(e),
        )


def pd_std(values):
    n = len(values)
    if n < 2:
        return 0.0
    mean = sum(values) / n
    return (sum((v - mean) ** 2 for v in values) / n) ** 0.5


if __name__ == "__main__":
    sample = {"sentinel2_b2": 0.08, "sentinel2_b3": 0.10, "sentinel2_b4": 0.13,
              "sentinel2_b8": 0.25, "sentinel2_b11": 0.31, "sentinel2_b12": 0.23,
              "ndvi": 0.20, "ndmi": 0.04, "elevation_m": 330, "slope_deg": 11,
              "curvature": 0.1, "geology_class": "gondite"}
    print(predict(sample).to_dict())
