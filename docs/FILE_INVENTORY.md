# MANGAN-AI — Backend + Model File Inventory

## Specialist models

```text
models/prospectivity/v001/       LIVE ML
models/grade/v001/              LIVE MOIL reference
models/production/v001/         LIVE MOIL historical reference
models/equipment/demo_v001/     DEMO
models/recovery/demo_v001/      DEMO
models/blast/demo_v001/         DEMO
models/weather/demo_v001/       DEMO
```

## Core backend

```text
services/api/
services/model_service/
services/orchestrator/
services/decision_engine/
services/providers/
services/jobs/
```

## Data/preprocessing

```text
pipelines/ingestion/
pipelines/preprocessing/
pipelines/geospatial/
pipelines/training/
data/external/
data/prospectivity/
```

## Contracts

```text
schemas/prediction_contract.json
schemas/model_registry.json
schemas/contracts.py
```

## Tests

```text
tests/model_contract/
tests/unit/
tests/api/
tests/integration/
```

## Team integration docs

```text
docs/UPDATED_GITHUB_ARCHITECTURE_v2.md
docs/API_FRONTEND_HANDOFF_v2_LIVE_REFERENCE_MODELS.md
docs/MOIL_LIVE_MODEL_INTEGRATION_v2.md
docs/MODEL_DATA_PREPROCESSING_HANDOFF_v3.md
docs/MODEL_LIVE_STATUS_v2.md
docs/API_ENDPOINT_CATALOG_v2.md
docs/CHANGELOG_V2_TO_V2_RECONCILED.md
```
