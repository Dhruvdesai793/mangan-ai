"""
Route A -- the public-data fallback pipeline.

IMPORTANT (read before touching this file):
This sandbox has no internet/GEE access, so this module does NOT call the real
Google Earth Engine API. It generates a geographically-plausible synthetic
stand-in dataset with the exact same schema Team 1's real Sentinel-2/DEM
extraction would produce (schemas/ingestion_contracts/team1_parquet_schema.json).

This exists so the prospectivity model has a working, non-blocking data path
today. When a machine with GEE credentials + internet is available, replace
the body of `extract_features()` with real ee.Image / ee.FeatureCollection
calls -- the output dataframe must keep the exact same columns, because
everything downstream (feature_engineering.py, training scripts, predict.py)
is written against that schema, not against this function's internals.
"""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

# A rough manganese-belt-like bounding box (illustrative, not a real deposit
# location) so the synthetic points look like a coherent AOI on a map demo.
LAT_RANGE = (21.0, 21.6)
LON_RANGE = (79.5, 80.3)
GEOLOGY_CLASSES = ["gondite", "banded_iron_formation", "laterite", "granite_gneiss", "alluvium"]


def extract_features(n_samples: int = 2000, positive_rate: float = 0.18) -> pd.DataFrame:
    n_pos = int(n_samples * positive_rate)
    n_neg = n_samples - n_pos

    def make_block(n, label):
        lat = RNG.uniform(*LAT_RANGE, n)
        lon = RNG.uniform(*LON_RANGE, n)
        # positives get systematically different (but noisy) geology/spectral signal
        # so the model has a real, learnable-but-imperfect signal to fit.
        geology_bias = RNG.choice(
            GEOLOGY_CLASSES, n,
            p=[0.45, 0.30, 0.10, 0.10, 0.05] if label == 1 else [0.12, 0.18, 0.30, 0.25, 0.15]
        )
        ndvi = RNG.normal(0.35 if label == 0 else 0.22, 0.08, n).clip(-1, 1)
        ndmi = RNG.normal(0.15 if label == 0 else 0.05, 0.07, n).clip(-1, 1)
        elevation = RNG.normal(320 if label == 1 else 280, 60, n)
        slope = RNG.normal(9 if label == 1 else 5, 4, n).clip(0, 90)
        curvature = RNG.normal(0, 0.5, n)
        b2 = RNG.normal(0.08, 0.02, n)
        b3 = RNG.normal(0.10, 0.02, n)
        b4 = RNG.normal(0.12 if label == 1 else 0.10, 0.02, n)
        b8 = RNG.normal(0.25, 0.04, n)
        b11 = RNG.normal(0.30 if label == 1 else 0.22, 0.04, n)
        b12 = RNG.normal(0.22 if label == 1 else 0.16, 0.03, n)
        grid_tile = [f"T{int((la-LAT_RANGE[0])*20):02d}{int((lo-LON_RANGE[0])*20):02d}" for la, lo in zip(lat, lon)]
        return pd.DataFrame({
            "sample_id": [f"S{label}{i:05d}" for i in range(n)],
            "latitude": lat, "longitude": lon,
            "sentinel2_b2": b2, "sentinel2_b3": b3, "sentinel2_b4": b4,
            "sentinel2_b8": b8, "sentinel2_b11": b11, "sentinel2_b12": b12,
            "ndvi": ndvi, "ndmi": ndmi,
            "elevation_m": elevation, "slope_deg": slope, "curvature": curvature,
            "geology_class": geology_bias,
            "label": label,
            "grid_tile_id": grid_tile,
            "acquisition_date": "2026-01-15",
        })

    df = pd.concat([make_block(n_pos, 1), make_block(n_neg, 0)], ignore_index=True)
    return df.sample(frac=1, random_state=42).reset_index(drop=True)


if __name__ == "__main__":
    df = extract_features()
    out = "data/public/synthetic_public_features.csv"
    df.to_csv(out, index=False)
    print(f"wrote {len(df)} rows -> {out}")
