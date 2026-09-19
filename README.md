# MANGAN-AI

MANGAN-AI is a local-first manganese mining intelligence application. It combines verified MOIL references, NGDR lease geometry, Google Earth Engine site features, registered specialist models, decision support, a FastAPI API, a Streamlit dashboard, and PostgreSQL/PostGIS persistence.

The system is deliberately explicit about evidence quality: `LIVE` means a registered implementation executed, `DEMO` means a scenario simulation, and `UNAVAILABLE` is returned instead of inventing a result. Grade and production outputs are references—not spatial grade or future production forecasts.

## Run the complete local stack

Prerequisites: Docker with Compose, an Earth Engine-enabled Google Cloud project, and Earth Engine OAuth credentials in `~/.config/earthengine`.

```bash
cp .env.example .env
# Set GEE_PROJECT_ID and local database values in .env.
earthengine authenticate
docker compose -f docker-compose.yml -f docker-compose.local.yml up --build -d
```

Open:

- Dashboard: <http://localhost:8501>
- API documentation: <http://localhost:8000/docs>
- Health: <http://localhost:8000/health>

The migration service applies the PostGIS schema and idempotently seeds the MOIL reference data before the API starts. On this workstation PostgreSQL is exposed on port `5433` because port `5432` is already occupied.

Stop the stack without deleting its database volume:

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml down
```

## Verify

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml exec api \
  python -m unittest discover -v

curl -X POST http://localhost:8000/predict/all \
  -H 'Content-Type: application/json' \
  -d '{"site_id":"MOIL-BAL-001","scenario_file":"scenario_01_normal.json"}'

curl -X POST http://localhost:8000/predict/coordinate \
  -H 'Content-Type: application/json' \
  -d '{"latitude":21.855,"longitude":80.231389,"buffer_m":250,"target_name":"Balaghat target"}'
```

With Earth Engine enabled, omitting `prospectivity_features` makes the backend derive the feature vector from the verified lease/site area and cache it in Postgres. The response reports `feature_source` as `GOOGLE_EARTH_ENGINE` on first extraction or `POSTGRES_GEE_FEATURE_CACHE` on reuse. If Earth Engine is unavailable and `GEE_ALLOW_DEMO_FEATURES=true`, the response contains an explicit fallback limitation.

`/predict/coordinate` accepts an arbitrary latitude/longitude and buffered AOI, runs the live Earth Engine feature path, persists the exploration target and prediction audit snapshot, and returns prospectivity plus the applicable scenario models. Mine-specific grade and production references are intentionally unavailable for an arbitrary coordinate.

## Architecture

```text
MOIL references + NGDR geometry + Sentinel-2/SRTM
                         │
                validated providers
                         │
             PostgreSQL/PostGIS cache
                         │
              trusted model registry
                         │
          orchestrator → decision engine
                         │
                    FastAPI
                   /       \
          Streamlit UI    API clients
```

Model modules can only be loaded through `schemas/model_registry.json`; callers cannot supply Python import paths. Database access is behind repositories, external geospatial access is behind a provider interface, and schema changes are Alembic migrations. These boundaries keep the service replaceable and horizontally scalable. The Compose base file uses an ordinary application network and is suitable as the starting point for CI or deployment; `docker-compose.local.yml` contains workstation-only host-network compatibility.

## Model and data status

| Component | Status | Meaning |
|---|---|---|
| Prospectivity v001 | LIVE | Existing trained model; current site features can come from Earth Engine |
| Grade v001 | LIVE | Verified MOIL product-grade reference, not in-situ prediction |
| Production v001 | LIVE | Official historical reference, not a future forecast |
| Equipment, recovery, blast, weather | DEMO | Synthetic operating scenarios with clear disclosure |
| Exploration point layer | DEMO | Existing public/synthetic fallback cache, not MOIL ground truth |

## Configuration

Configuration is read from environment variables and `.env`; see `.env.example`. Never commit `.env` or OAuth credentials. Important settings include `DATABASE_URL`, `GEE_ENABLED`, `GEE_PROJECT_ID`, `GEE_AUTH_METHOD`, `GEE_ALLOW_DEMO_FEATURES`, date bounds, CORS origins, request limits, and optional API-key settings.

For a hosted deployment, store secrets in the platform’s secret manager, run `alembic upgrade head` as a release job, use managed Postgres/PostGIS, mount a service-account credential rather than interactive OAuth, terminate TLS at the ingress, and add institutional identity/RBAC. The application containers run as non-root.

## Repository map

- `apps/frontend/` — Streamlit dashboard using the Forest Canopy theme (FreeSerif headings, FreeSans body)
- `services/api/` — HTTP routes, contracts, request limits, logging
- `services/orchestrator/` — trusted registry dispatch and fault isolation
- `services/providers/` — Earth Engine and MOIL data provider boundaries
- `services/persistence/` — SQLAlchemy models, sessions, repositories
- `db/migrations/` — Alembic/PostGIS migrations
- `models/` — specialist model implementations and adapters
- `tests/` — API, contract, integration, and unit tests
- `docs/IMPLEMENTATION_STATUS.md` — completed scope and remaining production work

The original handoff and architecture documents are preserved under `docs/` as design references. Current runtime behavior is described by this README, the generated OpenAPI document, and `docs/IMPLEMENTATION_STATUS.md`.
