# MANGAN-AI Backend + Model Completion Report — Reconciled Package

## Scope

This package consolidates the original model/data backend checkpoint with the later MOIL reference integration and the expanded API/frontend repository architecture.

## Implemented

- Shared `ModelResult` contract.
- Trusted registry-driven model discovery and importing.
- Registry `input_mode`: `feature_vector`, `site_reference`, `scenario`.
- Fault-isolated orchestrator.
- Explicit preprocessing validation layer.
- Prospectivity v001 frozen ML integration.
- Grade v001 verified MOIL product-grade reference.
- Production v001 verified FY2012 historical MOIL reference.
- Four DEMO operational modules retained.
- MOIL site catalog provider.
- NGDR lease geometry provider.
- FastAPI mine and lease routes.
- Existing health, prediction, exploration, production and jobs routes retained.
- Request IDs, CORS restriction, body-size guard, rate limiting and safe scenario resolution.
- API/frontend documentation and model/data handoff.
- Tests for API, orchestration, model contracts and canonical MOIL preprocessing validation.

## Current status

```text
7 registered models
3 LIVE
4 DEMO
```

`UNAVAILABLE` is still a valid runtime state for missing request inputs or model failures.

## Verification performed

```text
python -m unittest discover -v
→ 21 tests passed

python -m py_compile ...
→ passed

python scripts/register_models.py
→ registry regenerated successfully

pipelines/preprocessing/moil_reference.py
→ canonical site/grade/production datasets validate successfully
```

Target API responses were additionally exercised through FastAPI `TestClient` for:

- `/health`
- `/predict/prospectivity`
- `/predict/all`
- `/exploration/map`
- `/production`
- `/mines`
- `/mines/{site_id}/leases`
- `/jobs`

## Scientific scope disclosure

The package does **not** claim that all three LIVE components are trained predictive ML models.

- Prospectivity v001 is the current LIVE ML model and retains its existing public/synthetic fallback provenance.
- Grade v001 is a LIVE verified reference lookup for product-grade data.
- Production v001 is a LIVE historical reference lookup for FY2012 data.

Future predictive Grade/Production versions must use new model versions after the required labels, preprocessing and validation are available.
