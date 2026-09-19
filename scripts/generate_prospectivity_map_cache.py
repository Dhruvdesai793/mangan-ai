"""Generate a repository-local cached prospectivity map from the frozen v001 model.

This is an offline/demo acceleration step. It does not change the model artifact or
its predict() contract. Regenerate it when the verified fallback dataset/model version
changes.
"""
from __future__ import annotations

import json
import pathlib
import pickle

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models" / "prospectivity" / "v001"
DATASET = ROOT / "data" / "prospectivity" / "verified" / "prospectivity_verified.csv"
OUT = ROOT / "services" / "orchestrator" / "cache" / "prospectivity_map_demo_v001.json"

with (MODEL_DIR / "model.pkl").open("rb") as handle:
    model = pickle.load(handle)
with (MODEL_DIR / "feature_schema.json").open("r", encoding="utf-8") as handle:
    feature_cols = json.load(handle)["feature_columns_in_order"]

df = pd.read_csv(DATASET)
X = pd.DataFrame(index=df.index)
X["sentinel2_b2"] = df["sentinel2_b2"]
X["sentinel2_b3"] = df["sentinel2_b3"]
X["sentinel2_b4"] = df["sentinel2_b4"]
X["sentinel2_b8"] = df["sentinel2_b8"]
X["sentinel2_b11"] = df["sentinel2_b11"]
X["sentinel2_b12"] = df["sentinel2_b12"]
X["ndvi"] = df["ndvi"]
X["ndmi"] = df["ndmi"]
X["elevation_m"] = df["elevation_m"]
X["slope_deg"] = df["slope_deg"]
X["curvature"] = df["curvature"]
X["b11_b12_ratio"] = df["sentinel2_b11"] / df["sentinel2_b12"].replace(0, 1e-6)
X["ferrous_index"] = (df["sentinel2_b11"] - df["sentinel2_b8"]) / (
    (df["sentinel2_b11"] + df["sentinel2_b8"]).replace(0, 1e-6)
)
for col in feature_cols:
    if col.startswith("geo_"):
        geology = col.removeprefix("geo_")
        X[col] = (df["geology_class"] == geology).astype(float)
X = X.reindex(columns=feature_cols, fill_value=0.0)

probas = model.predict_proba(X)[:, 1]
tree_probas = np.column_stack([tree.predict_proba(X.to_numpy())[:, 1] for tree in model.estimators_])
uncertainty = tree_probas.std(axis=1)

points = []
for lat, lon, score, unc in zip(df["latitude"], df["longitude"], probas, uncertainty):
    points.append({
        "latitude": float(lat),
        "longitude": float(lon),
        "prospectivity": round(float(score), 6),
        "uncertainty": round(float(unc), 6),
        "status": "LIVE",
    })

payload = {
    "model_id": "prospectivity",
    "model_version": "v001",
    "data_source": "PUBLIC_DATA_SYNTHETIC_FALLBACK",
    "point_count": len(points),
    "points": points,
}
OUT.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
print(f"wrote {OUT} with {len(points)} points")
