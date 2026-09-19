# MANGAN-AI — Updated GitHub Architecture v2 (Reconciled Final)

> This file keeps the v2 filename so existing team links remain valid. It is the current architecture after reconciling the API/frontend team's expected repository structure with the model/data and backend work.

## 1. System boundary

```text
RAW / EXTERNAL SOURCES
        ↓
INGESTION + VALIDATION
        ↓
PREPROCESSING / GEOSPATIAL FEATURE BUILDING
        ↓
CANONICAL MODEL INPUT
        ↓
TRUSTED MODEL REGISTRY
        ↓
registered_model.predict(input)
        ↓
ModelResult
        ↓
ORCHESTRATOR
        ↓
DECISION ENGINE
        ↓
FASTAPI
        ↓
FRONTEND
```

The application layer must not load `model.pkl` directly and must not accept arbitrary Python module paths from HTTP.

## 2. Current model inventory

| Model | Version | Status | Type | Input mode | Current meaning |
|---|---|---|---|---|---|
| Prospectivity | v001 | LIVE | ML | `feature_vector` | Existing public/synthetic-fallback ML model |
| Grade | v001 | LIVE | REFERENCE | `site_reference` | Verified MOIL product-grade reference; not spatial in-situ prediction |
| Production | v001 | LIVE | REFERENCE | `site_reference` | FY2012 MOIL historical reference; not future forecast |
| Equipment | demo_v001 | DEMO | SIMULATION | `scenario` | Synthetic operational scenario |
| Recovery | demo_v001 | DEMO | SIMULATION | `scenario` | Synthetic operational scenario |
| Blast | demo_v001 | DEMO | SIMULATION | `scenario` | Synthetic operational scenario |
| Weather | demo_v001 | DEMO | SIMULATION | `scenario` | Synthetic scenario input; real forecast-provider integration is future work |

Runtime registry target: **7 total / 3 LIVE / 4 DEMO / 0 UNAVAILABLE** when the full package is present.

## 3. Canonical repository

```text
mangan-ai/
├── apps/
│   └── frontend/
│       ├── app.py
│       ├── pages/
│       ├── components/
│       ├── assets/
│       └── .streamlit/
│
├── services/
│   ├── api/
│   │   ├── main.py
│   │   ├── dependencies.py
│   │   ├── middleware/
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   ├── prediction.py
│   │   │   ├── exploration.py
│   │   │   ├── production.py
│   │   │   ├── jobs.py
│   │   │   └── mines.py
│   │   └── schemas/
│   │       ├── requests.py
│   │       └── responses.py
│   ├── auth/
│   ├── model_service/
│   │   └── service.py
│   ├── orchestrator/
│   │   ├── registry.py
│   │   ├── contracts.py
│   │   ├── input_builder.py
│   │   ├── orchestrator.py
│   │   └── exploration.py
│   ├── decision_engine/
│   ├── optimization/
│   ├── persistence/
│   ├── providers/
│   │   └── moil_reference.py
│   └── jobs/
│
├── models/
│   ├── _reference_common.py
│   ├── prospectivity/v001/
│   ├── grade/v001/
│   ├── grade/demo_v001/
│   ├── production/v001/
│   ├── production/demo_v001/
│   ├── equipment/demo_v001/
│   ├── recovery/demo_v001/
│   ├── blast/demo_v001/
│   └── weather/demo_v001/
│
├── pipelines/
│   ├── ingestion/
│   ├── preprocessing/
│   │   └── moil_reference.py
│   ├── geospatial/
│   └── training/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── verified/
│   ├── features/
│   ├── public/
│   ├── prospectivity/{raw,processed,verified}/
│   ├── synthetic/
│   └── external/
│       ├── MOIL_v12.xlsx
│       ├── moil_site_catalog.csv
│       ├── moil_grade_reference.csv
│       ├── moil_production_reference.csv
│       ├── moil_reference_manifest.json
│       └── geometries/
│           └── ngdr_moil_major_mining_leases_2022.geojson
│
├── schemas/
│   ├── prediction_contract.json
│   ├── model_registry.json
│   └── ingestion_contracts/
│
├── scenarios/
├── configs/
├── scripts/
├── tests/{unit,contract,api,integration,frontend,security,performance,model_contract}/
├── db/migrations/
├── docs/
├── pyproject.toml
├── requirements.txt
├── .env.example
├── SECURITY.md
└── README.md
```

Empty application folders are intentionally retained as integration boundaries for the API/frontend, auth, persistence and optimization work owned by other team members.

## 4. Data/model contract

Every registered specialist implementation exposes:

```python
predict(input: dict) -> ModelResult
```

The shared response remains:

```json
{
  "model_id": "string",
  "model_version": "string",
  "status": "LIVE | DEMO | UNAVAILABLE",
  "prediction": "any | null",
  "uncertainty": "number | null",
  "data_source": "string",
  "prediction_timestamp": "ISO-8601 string",
  "reason": "string | null"
}
```

`schemas/model_registry.json` is generated from each selected model's `config.yaml` by `scripts/register_models.py`.

## 5. Input modes

The registry now declares an `input_mode` for every model:

```text
feature_vector  → prospectivity_features
site_reference  → site_id
scenario        → approved scenario JSON
```

The API does not branch on individual model names. `InputBuilder` reads the registry metadata and builds the model-specific input.

## 6. Preprocessing boundary

Preprocessing is explicitly separated from inference.

```text
MOIL_v12.xlsx / NGDR
        ↓
extraction + identity normalization
        ↓
canonical CSV / GeoJSON
        ↓
validation / provenance checks
        ↓
reference provider or feature pipeline
        ↓
model input
```

The runtime API uses canonical CSVs/GeoJSON. The source workbook is retained for provenance, but the API is not responsible for spreadsheet parsing.

For Prospectivity, the existing geospatial/training pipeline remains responsible for feature construction; the API only accepts the frozen feature contract.

## 7. API/frontend boundary

```text
Streamlit / frontend
        ↓ HTTP
services/api/routes/*
        ↓
services/orchestrator
        ↓
services/model_service / trusted registry
        ↓
models/*/predict.py
```

Frontend code must not import specialist model modules directly.

## 8. MOIL reference data

Grade and Production v001 are intentionally reference implementations:

- Grade uses verified product-grade assay/product information. The source does not establish geolocated in-situ labels suitable for the spatial regression task defined by the audit.
- Production uses the supplied FY2012 mine-level history. It is not a chronological forecast dataset.

Future predictive versions should be new model versions (`grade/v002`, `production/v002`) after the required data and leakage-safe validation are available.

## 9. Lease geometry

`GET /mines/{site_id}/leases` serves the repository-supplied NGDR 2022 GeoJSON feature set mapped to the selected canonical mine.

The frontend must render the returned geometry rather than drawing a synthetic circle around the mine coordinate.

## 10. Non-negotiable rules

1. API/frontend never load `model.pkl` directly.
2. HTTP never supplies arbitrary Python import/module paths.
3. Registry, not the frontend, is the source of truth for available models.
4. DEMO output is never relabeled as LIVE/validated ML.
5. Reference-grade and historical-production values are never described as spatial grade predictions or future forecasts.
6. One failed model becomes `UNAVAILABLE`; it does not abort `/predict/all`.
7. Long-running work uses `/jobs` rather than blocking the UI.
