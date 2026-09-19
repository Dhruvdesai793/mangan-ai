# MANGAN-AI — MOIL Live Model Integration v2 (Reconciled Final)

## Result

The MOIL package is integrated without changing the shared `ModelResult` contract or the registry-driven orchestration boundary.

Current intended runtime inventory:

```text
3 LIVE
4 DEMO
0 UNAVAILABLE when the complete package and required request inputs are available
```

A missing `site_id` or missing prospectivity feature vector can still make an individual model `UNAVAILABLE`; this is intentional.

## 1. Grade v001 — LIVE reference

Path:

```text
models/grade/v001/
```

Runtime input:

```json
{"site_id": "MOIL-BAL-001"}
```

Canonical source:

```text
data/external/moil_grade_reference.csv
```

Source provenance:

```text
MOIL_v12.xlsx
USER_SOURCE_Assays
USER_SOURCE_Ore Products
```

The result exposes product-grade Mn %, interval, assay/product IDs and supplied chemistry.

**Scope:** verified product-grade reference. It is not a trained spatial in-situ grade regression model.

## 2. Production v001 — LIVE reference

Path:

```text
models/production/v001/
```

Runtime input:

```json
{"site_id": "MOIL-BAL-001"}
```

Canonical source:

```text
data/external/moil_production_reference.csv
```

Source provenance:

```text
MOIL_v12.xlsx
HISTORICAL_MOIL_2012
```

The result exposes FY2012 production and historical grade/reserve/resource context.

**Scope:** official historical reference. It is not a future production or shortfall forecast.

## 3. Prospectivity v001 — unchanged

`models/prospectivity/v001/` remains the existing LIVE ML model. The current training source remains `PUBLIC_DATA_SYNTHETIC_FALLBACK`.

The MOIL package is not silently injected into this model because the supplied data do not establish the validated spatial feature/label retraining path required for a defensible update.

## 4. DEMO modules retained

```text
models/equipment/demo_v001/
models/recovery/demo_v001/
models/blast/demo_v001/
models/weather/demo_v001/
```

They remain synthetic workflow simulations and retain `status=DEMO`.

## 5. Preprocessing path

```text
MOIL_v12.xlsx
       ↓
source-tab extraction
       ↓
identity/site normalization
       ↓
canonical CSV exports
       ↓
pipelines/preprocessing/moil_reference.py validation
       ↓
services/providers/moil_reference.py
       ↓
site-reference model predict()
```

The lease geometry follows the same provenance principle:

```text
NGDR 2022 GeoJSON
       ↓
verified canonical mapping
       ↓
GET /mines/{site_id}/leases
```

## 6. Future scientific promotion path

Only promote to true predictive ML after the corresponding data requirements are met.

### Grade

```text
models/grade/v002/
```

Requires geolocated in-situ assay labels, features available at prediction time, leakage control and spatial validation.

### Production

```text
models/production/v002/
```

Requires chronological production history, a fixed forecast origin/horizon, cutoff-safe operational/material inputs, weather-forecast parity and time-based evaluation.

### Equipment / Recovery / Blast

Create new validated model versions only after the required future-window event/history or process datasets and evaluation targets are available.
