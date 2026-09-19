"""Prevalence / geology-type baseline -- the floor every real model must beat."""
from common import load_verified, prepare_xy
from sklearn.metrics import roc_auc_score
import pandas as pd

def run():
    df = load_verified()
    X, y, groups, _ = prepare_xy(df)
    # geology-type baseline: score = positive rate observed for that geology class
    geo_cols = [c for c in X.columns if c.startswith("geo_")]
    scores = pd.Series(0.0, index=X.index)
    for c in geo_cols:
        mask = X[c] == 1
        rate = y[mask].mean() if mask.sum() else y.mean()
        scores[mask] = rate
    auc = roc_auc_score(y, scores)
    print(f"[baseline] geology-prevalence AUC (in-sample, not spatially validated): {auc:.3f}")
    return {"model": "geology_prevalence_baseline", "auc_in_sample": round(float(auc), 4)}

if __name__ == "__main__":
    run()
