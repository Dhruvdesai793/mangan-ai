# MANGAN-AI — API Endpoint Catalog

## Coordinate exploration (phase 1)

`POST /predict/coordinate` accepts `latitude`, `longitude`, optional `buffer_m`, `target_name`, and `scenario_file`. It extracts a buffered Earth Engine AOI, runs the applicable spatial/scenario models, stores the exploration target and prediction audit snapshot, and returns `feature_source`. Grade and production remain unavailable for arbitrary coordinates because they are mine-specific reference models.

`GET /exploration/targets` returns the persisted coordinate target list.

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
