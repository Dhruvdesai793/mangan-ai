"""
This is the file that produces the number you're allowed to say out loud.
Uses GroupKFold on spatial_fold_id (tile-grouped) -- NOT a random row split --
so nearby, spatially-correlated samples never appear on both sides of a fold.
Also runs a simple feature-ablation check.
"""
import json
import numpy as np
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score, average_precision_score

from common import load_verified, prepare_xy
import train_baseline
from train_lr import build_model as build_lr
from train_rf import build_model as build_rf
from train_xgb import build_model as build_gbt, IMPL as GBT_IMPL


def spatial_cv_score(build_fn, X, y, groups, n_splits=5):
    gkf = GroupKFold(n_splits=n_splits)
    aucs, aps = [], []
    for train_idx, test_idx in gkf.split(X, y, groups):
        if y.iloc[train_idx].nunique() < 2:
            continue
        model = build_fn()
        model.fit(X.iloc[train_idx], y.iloc[train_idx])
        proba = model.predict_proba(X.iloc[test_idx])[:, 1]
        aucs.append(roc_auc_score(y.iloc[test_idx], proba))
        aps.append(average_precision_score(y.iloc[test_idx], proba))
    return {"auc_mean": float(np.mean(aucs)), "auc_std": float(np.std(aucs)),
            "ap_mean": float(np.mean(aps)), "n_folds_used": len(aucs)}


def ablation(build_fn, X, y, groups, drop_cols):
    kept = [c for c in X.columns if c not in drop_cols]
    return spatial_cv_score(build_fn, X[kept], y, groups)


def run():
    df = load_verified()
    X, y, groups, feature_cols = prepare_xy(df)

    results = {}
    results["baseline_geology_prevalence"] = train_baseline.run()
    results["logistic_regression"] = spatial_cv_score(build_lr, X, y, groups)
    results["random_forest"] = spatial_cv_score(build_rf, X, y, groups)
    results["gradient_boosted_trees"] = {**spatial_cv_score(build_gbt, X, y, groups), "implementation": GBT_IMPL}

    # ablation: how much do the satellite spectral bands actually matter?
    spectral_cols = [c for c in X.columns if c.startswith("sentinel2_")]
    results["ablation_random_forest_no_spectral_bands"] = ablation(build_rf, X, y, groups, spectral_cols)

    print(json.dumps(results, indent=2))
    with open("../../../models/prospectivity/v001/_cv_results_full.json", "w") as f:
        json.dump(results, f, indent=2)
    return results, feature_cols


if __name__ == "__main__":
    run()
