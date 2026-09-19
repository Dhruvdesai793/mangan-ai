# MANGAN-AI — API + Frontend Engineer Guide (Current)

The API/frontend application is an outer layer around the model/data contract. The model/data boundary must remain stable.

## Stable backend contract

```python
registered_model.predict(input_dict) -> ModelResult
```

The API must never load `model.pkl` directly and must never accept arbitrary module/model paths from HTTP.

## Current model input modes

The registry declares one of:

```text
feature_vector
site_reference
scenario
```

`services/orchestrator/input_builder.py` maps requests to those modes.

## Current API endpoints

```text
GET  /health
GET  /mines
GET  /mines/{site_id}/leases
POST /predict/prospectivity
POST /predict/all
POST /exploration/map
POST /production
POST /jobs
GET  /jobs/{job_id}
```

## Frontend responsibilities

- Call the API over HTTP.
- Keep selected `site_id` in frontend state.
- Render model cards dynamically from `response.models`.
- Preserve `status`, `data_source`, `reason` and `prediction.scope`.
- Render NGDR lease GeoJSON from the lease endpoint.

## Frontend must not

- import model modules directly;
- recreate model calculations;
- convert historical references into forecasts;
- relabel DEMO/UNAVAILABLE results as LIVE;
- hardcode the available model list.

See `docs/API_FRONTEND_HANDOFF_v2_LIVE_REFERENCE_MODELS.md` for the complete field-level handoff.
