from common import load_verified, prepare_xy
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

def build_model():
    return Pipeline([
        ("scale", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])

if __name__ == "__main__":
    df = load_verified()
    X, y, groups, cols = prepare_xy(df)
    m = build_model().fit(X, y)
    print("[LR] trained on full data (in-sample check only) -- see evaluate_spatial_cv.py for real metric")
