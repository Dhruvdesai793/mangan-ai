# MANGAN-AI — API + Frontend Handoff v2 (Reconciled Final)

> This is the current handoff. It preserves the v2 filename for compatibility with prior team links.

## 1. Frontend contract

The frontend talks to FastAPI only. It must not import model modules directly.

### Mine selector

Call:

```http
GET /mines
```

Use `site_id` as the stable state value and `mine_name` as the display label.

### Combined prediction

Call:

```http
POST /predict/all
```

Example:

```json
{
  "scenario_file": "scenario_02_rainfall.json",
  "site_id": "MOIL-BAL-001",
  "prospectivity_features": null
}
```

When a valid prospectivity feature vector is available:

```json
{
  "scenario_file": "scenario_02_rainfall.json",
  "site_id": "MOIL-BAL-001",
  "prospectivity_features": {
    "sentinel2_b2": 0.08,
    "sentinel2_b3": 0.10,
    "sentinel2_b4": 0.13,
    "sentinel2_b8": 0.25,
    "sentinel2_b11": 0.31,
    "sentinel2_b12": 0.23,
    "ndvi": 0.20,
    "ndmi": 0.04,
    "elevation_m": 330,
    "slope_deg": 11,
    "curvature": 0.1,
    "geology_class": "gondite"
  }
}
```

Do not derive prospectivity features from grade/reference values.

## 2. Rendering model cards

Iterate over `response.models` instead of hardcoding the model set.

For each result render at least:

```text
model_id
model_version
status
data_source
prediction
uncertainty
reason
```

### Grade

When:

```text
model_id = grade
status = LIVE
```

Display:

```text
Verified MOIL product-grade reference
```

Use fields inside `prediction` such as:

```text
mn_grade_percent
interval
reference_year
assay_id
sample_id
product_id
chemistry
verification_status
scope
```

Never label this as `Predicted in-situ grade`.

### Production

When:

```text
model_id = production
status = LIVE
```

Display:

```text
Official MOIL FY2012 historical production reference
```

Use:

```text
historical_production_tonnes
reference_year
average_grade_label
reserves_a_tonnes
resources_b_tonnes
a_plus_b_tonnes
scope
```

Never label this as a future production forecast or shortfall probability.

## 3. Lease map

Call:

```http
GET /mines/{site_id}/leases
```

The response is a GeoJSON `FeatureCollection` sourced from the supplied NGDR 2022 lease dataset.

Do not draw a synthetic circle around the site coordinate.

## 4. Exploration map

The existing:

```http
POST /exploration/map
```

remains separately scoped to the current Prospectivity v001 demonstration/fallback dataset. It must retain its disclosure that the current model is not MOIL-trained ground truth.

## 5. Jobs

For longer operations:

```http
POST /jobs
GET /jobs/{job_id}
```

The `predict_all` and `production` job payloads may contain `site_id`.

## 6. Backend assumptions frontend can rely on

- Registry is authoritative.
- Model results are normalized to `ModelResult`.
- Model failures are isolated as `UNAVAILABLE`.
- `request_id` is returned and also exposed in `X-Request-ID`.
- DEMO limitations are included in the response.
- Reference model scope is expressed in `prediction.scope` and `reason`.

## 7. Do not do these in the frontend

- Load model files.
- Recreate model logic.
- Derive grade from satellite values.
- Convert historical production into a forecast.
- Hide `DEMO`/`UNAVAILABLE` statuses.
- Hardcode the list of seven models.
