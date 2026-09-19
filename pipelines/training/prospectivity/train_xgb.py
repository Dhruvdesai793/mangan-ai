"""
XGBoost path. This sandbox has no internet access to install xgboost, so this
script degrades to sklearn's GradientBoostingClassifier (same gradient-boosted
tree family) and clearly labels itself as a substitute. On a machine with
`pip install xgboost` available, swap build_model() back to xgboost.XGBClassifier
with equivalent hyperparameters -- evaluate_spatial_cv.py doesn't care which
implementation it's given.
"""
from common import load_verified, prepare_xy

try:
    import xgboost as xgb
    def build_model():
        return xgb.XGBClassifier(
            n_estimators=300, max_depth=4, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, eval_metric="logloss", random_state=42,
        )
    IMPL = "xgboost.XGBClassifier"
except ImportError:
    from sklearn.ensemble import GradientBoostingClassifier
    def build_model():
        return GradientBoostingClassifier(n_estimators=300, max_depth=3, learning_rate=0.05, random_state=42)
    IMPL = "sklearn.GradientBoostingClassifier (xgboost unavailable offline -- swap back when online)"

if __name__ == "__main__":
    print(f"[GBT] implementation in use: {IMPL}")
    df = load_verified()
    X, y, groups, cols = prepare_xy(df)
    m = build_model().fit(X, y)
    print("[GBT] trained on full data (in-sample check only) -- see evaluate_spatial_cv.py for real metric")
