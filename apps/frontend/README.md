# Frontend integration boundary

The frontend talks to FastAPI over HTTP. Do not import modules from `models/` or `services/orchestrator/` directly.

Recommended first state:

```text
selected_site_id
selected_scenario
optional prospectivity_features
```

Then call:

```http
GET /mines
POST /predict/all
GET /mines/{site_id}/leases
```

Render model cards dynamically from `response.models` and preserve `status`, `data_source`, `reason` and `prediction.scope` disclosures.
