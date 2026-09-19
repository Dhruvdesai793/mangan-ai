# MANGAN-AI — API Endpoint Catalog

## Health

```http
GET /health
```

Returns service status plus registry counts.

## Specialist prospectivity

```http
POST /predict/prospectivity
```

Accepts the validated feature vector and invokes the registered Prospectivity model.

## Combined orchestration

```http
POST /predict/all
```

Request fields:

```text
scenario_file?: string
site_id?: string
prospectivity_features?: object
```

The orchestrator resolves the input mode for every registered model.

## Exploration map

```http
POST /exploration/map
```

Returns the current prospectivity demonstration/fallback map cache.

## Production intelligence bundle

```http
POST /production
```

Supports `site_id`. The response is multi-source: historical MOIL reference + scenario simulations + decision-engine output.

## Mine catalog

```http
GET /mines
```

Returns the canonical mine selector data.

## Lease geometry

```http
GET /mines/{site_id}/leases
```

Returns a GeoJSON `FeatureCollection` from the supplied NGDR 2022 lease dataset.

## Long-running jobs

```http
POST /jobs
GET /jobs/{job_id}
```

Supported job types remain `exploration_map`, `predict_all` and `production`.
