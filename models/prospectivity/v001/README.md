# Prospectivity Model -- v001

**Status: LIVE** (pipeline is real; accuracy claim is scoped to synthetic data -- read "What LIVE means" below)

## What it does
Given spatial/spectral/geological features for a location, returns a manganese
prospectivity score in [0,1] and a rough uncertainty estimate.

## Algorithm
Random Forest (300 trees, max_depth=8, class_weight=balanced), chosen over
logistic regression and gradient-boosted trees for comparable spatial-CV AUC
plus usable feature importances. See `metrics.json` -> `all_candidates_compared`
for the full comparison.

## Validation method
`GroupKFold(n_splits=5)` grouped by spatial tile (`spatial_fold_id`), **not** a
random row split. An ablation run (dropping all Sentinel-2 spectral bands) is
included in `metrics.json` to show how much the spectral features actually
contribute versus geology/terrain alone.

## What "LIVE" means here (read this before quoting a number to anyone)
The training + validation **pipeline** is real, working, and spatially honest.
The **training data** is currently the public-data fallback path
(`pipelines/geospatial/gee_extraction.py`), which — because this build
environment has no internet/GEE access — is a synthetic, geographically
plausible stand-in dataset, not real Sentinel-2/DEM extraction and not real
MOIL or ground-truth occurrence data.

**Do not present `metrics.json`'s AUC as a real-world prospectivity accuracy
claim.** Present it as: "our training and spatial-validation pipeline is
built and working; here is the metric it produces on the current data source;
retraining on Team 1/Team 2's real data is a drop-in swap, not a rebuild."

## How this gets upgraded to real data (Route A -> Route B)
1. Team 1 delivers a Parquet matching `schemas/ingestion_contracts/team1_parquet_schema.json`.
2. Team 2 verifies it -> matches `schemas/ingestion_contracts/team2_verified_schema.json`
   -> lands in `data/prospectivity/verified/`.
3. Re-run `pipelines/training/prospectivity/evaluate_spatial_cv.py` then `freeze_model.py`
   pointed at the real file.
4. Save as `models/prospectivity/v002/`, update `schemas/model_registry.json` to point at it.
   Do not overwrite v001 -- keep it archived for comparison.

## Interface
```python
from models.prospectivity.v001.predict import predict
result = predict({...})   # see config.yaml for required fields
```
Returns a `schemas.contracts.ModelResult`. Never import `model.pkl` directly.
