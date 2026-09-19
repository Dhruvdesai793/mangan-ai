"""
Freezes the selected model (Random Forest -- comparable spatial-CV AUC to LR/GBT,
plus usable feature importances for the exploration map) as models/prospectivity/v001.
Run evaluate_spatial_cv.py first; this script re-reads its output for metrics.json
so the frozen metrics are never hand-typed.
"""
import json, pickle, pathlib
from datetime import datetime, timezone
from common import load_verified, prepare_xy
from train_rf import build_model

OUT_DIR = pathlib.Path(__file__).resolve().parents[3] / "models" / "prospectivity" / "v001"

def run():
    df = load_verified()
    X, y, groups, feature_cols = prepare_xy(df)

    model = build_model()
    model.fit(X, y)

    with open(OUT_DIR / "model.pkl", "wb") as f:
        pickle.dump(model, f)

    with open(OUT_DIR / "feature_schema.json", "w") as f:
        json.dump({"feature_columns_in_order": feature_cols, "n_features": len(feature_cols)}, f, indent=2)

    with open(OUT_DIR / "_cv_results_full.json") as f:
        cv_results = json.load(f)

    metrics = {
        "selected_model": "random_forest",
        "selection_reason": "Comparable spatial-CV AUC to logistic regression and gradient-boosted trees, with usable feature importances for the exploration map.",
        "spatial_cv_auc_mean": cv_results["random_forest"]["auc_mean"],
        "spatial_cv_auc_std": cv_results["random_forest"]["auc_std"],
        "spatial_cv_average_precision": cv_results["random_forest"]["ap_mean"],
        "n_spatial_folds": cv_results["random_forest"]["n_folds_used"],
        "baseline_auc_in_sample": cv_results["baseline_geology_prevalence"]["auc_in_sample"],
        "ablation_no_spectral_bands_auc": cv_results["ablation_random_forest_no_spectral_bands"]["auc_mean"],
        "all_candidates_compared": cv_results,
        "validation_method": "GroupKFold(n_splits=5) grouped by spatial_fold_id (tile-grouped) -- not a random row split",
        "important_note": "These metrics are computed on a SYNTHETIC public-fallback dataset (Route A). They demonstrate the training/validation pipeline works end to end and are NOT a claim of real-world or MOIL manganese-prospectivity accuracy. Retrain on Team 2's verified real dataset (Route B) before quoting any metric to a stakeholder as a real-world result.",
    }
    with open(OUT_DIR / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    training_metadata = {
        "model_id": "prospectivity",
        "model_version": "v001",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "algorithm": "RandomForestClassifier",
        "hyperparameters": model.get_params(),
        "training_data_route": "Route A -- public-data fallback (SYNTHETIC, see gee_extraction.py header)",
        "training_data_path": "data/prospectivity/verified/prospectivity_verified.csv",
        "n_training_samples": len(X),
        "n_positive": int(y.sum()),
        "n_negative": int((y == 0).sum()),
        "geographic_scope": "illustrative AOI, lat 21.0-21.6 / lon 79.5-80.3 (NOT a real deposit location)",
        "feature_schema_version": 1,
        "status": "LIVE",
        "status_meaning": "The training + validation PIPELINE is real and working end-to-end. The MODEL's accuracy claim is scoped to synthetic data until Route B (Team 1 -> Team 2 real data) replaces Route A -- see README.md.",
    }
    with open(OUT_DIR / "training_metadata.json", "w") as f:
        json.dump(training_metadata, f, indent=2, default=str)

    print("Frozen model.pkl, feature_schema.json, metrics.json, training_metadata.json ->", OUT_DIR)

if __name__ == "__main__":
    run()
