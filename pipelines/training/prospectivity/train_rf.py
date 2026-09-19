from common import load_verified, prepare_xy
from sklearn.ensemble import RandomForestClassifier

def build_model():
    return RandomForestClassifier(
        n_estimators=300, max_depth=8, min_samples_leaf=5,
        class_weight="balanced", random_state=42, n_jobs=-1,
    )

if __name__ == "__main__":
    df = load_verified()
    X, y, groups, cols = prepare_xy(df)
    m = build_model().fit(X, y)
    print("[RF] trained on full data (in-sample check only) -- see evaluate_spatial_cv.py for real metric")
