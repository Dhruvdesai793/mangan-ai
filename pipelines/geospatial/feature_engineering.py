"""
Turns raw Team1-schema features into the model-ready matrix. Same function
runs on Route A (public fallback) and Route B (Team 2 verified) output,
since both are guaranteed to share schemas/ingestion_contracts/team1_parquet_schema.json.
"""
import pandas as pd

NUMERIC_FEATURES = [
    "sentinel2_b2", "sentinel2_b3", "sentinel2_b4", "sentinel2_b8", "sentinel2_b11", "sentinel2_b12",
    "ndvi", "ndmi", "elevation_m", "slope_deg", "curvature",
]
CATEGORICAL_FEATURES = ["geology_class"]


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    # a couple of derived spectral ratios -- common, cheap, genuinely useful
    out["b11_b12_ratio"] = out["sentinel2_b11"] / out["sentinel2_b12"].replace(0, 1e-6)
    out["ferrous_index"] = (out["sentinel2_b11"] - out["sentinel2_b8"]) / (out["sentinel2_b11"] + out["sentinel2_b8"] + 1e-6)
    out = pd.get_dummies(out, columns=CATEGORICAL_FEATURES, prefix="geo")
    return out


def get_final_feature_columns(feature_df: pd.DataFrame) -> list:
    exclude = {"sample_id", "latitude", "longitude", "label", "grid_tile_id", "acquisition_date",
               "duplicate_check_passed", "leakage_check_passed", "coordinate_valid",
               "spatial_fold_id", "verification_report_id", "verified_timestamp"}
    return [c for c in feature_df.columns if c not in exclude]
