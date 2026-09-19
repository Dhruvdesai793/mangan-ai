# MANGAN-AI — Current Engineering Handoff

This repository is the consolidated model/data + backend checkpoint for integration with the API/frontend architecture.

## Read first

1. `README.md`
2. `docs/UPDATED_GITHUB_ARCHITECTURE_v2.md`
3. `docs/API_FRONTEND_HANDOFF_v2_LIVE_REFERENCE_MODELS.md`
4. `docs/MODEL_DATA_PREPROCESSING_HANDOFF_v3.md`
5. `docs/FILE_INVENTORY.md`

## Core interface

Every registered model exposes:

```python
predict(input: dict) -> ModelResult
```

The registry determines the trusted module, version, status, source and `input_mode`.

## Current status

```text
Prospectivity v001   LIVE ML
Grade v001           LIVE reference
Production v001      LIVE reference
Equipment demo_v001 DEMO
Recovery demo_v001  DEMO
Blast demo_v001     DEMO
Weather demo_v001   DEMO
```

## Backend flow

```text
API request
  ↓
InputBuilder
  ↓
Registry
  ↓
registered predict()
  ↓
ModelResult
  ↓
Decision Engine
  ↓
HTTP response
```

Do not bypass the registry or import models from frontend/API code.

## Data flow

```text
MOIL/public/raw data
  ↓
ingestion
  ↓
preprocessing / geospatial pipeline
  ↓
canonical data or feature vector
  ↓
model
```

The current MOIL Grade and Production implementations are reference lookups, not predictive ML models.
