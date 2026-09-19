"""Shared data loading + feature prep for every training script in this folder."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
import pandas as pd
from pipelines.geospatial.feature_engineering import build_feature_matrix, get_final_feature_columns

VERIFIED_PATH = pathlib.Path(__file__).resolve().parents[3] / "data" / "prospectivity" / "verified" / "prospectivity_verified.csv"


def load_verified() -> pd.DataFrame:
    return pd.read_csv(VERIFIED_PATH)


def prepare_xy(df: pd.DataFrame):
    feat_df = build_feature_matrix(df)
    feature_cols = get_final_feature_columns(feat_df)
    X = feat_df[feature_cols].astype(float)
    y = feat_df["label"].astype(int)
    groups = feat_df["spatial_fold_id"]
    return X, y, groups, feature_cols
