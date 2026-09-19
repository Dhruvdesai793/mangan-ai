# Implementation status

Updated 2026-09-20.

## Completed and verified

- FastAPI endpoints for health, models, mines, verified leases, predictions, exploration, production, jobs, and prediction history.
- Registry-only model loading, typed request/response contracts, fault isolation, structured request IDs/logging, request-size bounds, CORS, and prediction rate limiting.
- Live Prospectivity v001 execution with site-driven Sentinel-2 and SRTM feature extraction through Google Earth Engine.
- Database-backed Earth Engine feature cache with explicit `feature_source` provenance.
- Verified MOIL product-grade and official historical-production reference adapters.
- PostgreSQL 17/PostGIS persistence, Alembic migration, idempotent seed, repository boundaries, prediction audit snapshots, and persisted job state.
- Streamlit dashboard with verified lease map, model evidence, decision support, provenance, history, and explicit LIVE/DEMO disclosures.
- Forest Canopy design: `#2d4a2b`, `#7d8471`, `#a4ac86`, `#faf9f6`; FreeSerif Bold headings and FreeSans body text.
- Non-root Docker image, dependency-ordered Compose stack, health checks, and separate workstation compatibility override.
- Automated contract, API, integration, and preprocessing tests.

Local verification used the configured Earth Engine project. A site prediction for `MOIL-BAL-001` completed successfully and stored a `GOOGLE_EARTH_ENGINE` cache record. The local PostgreSQL port is `5433` because the host already uses `5432`.

## Scientific scope

The prospectivity model executes live, but its training data remains the existing public/synthetic fallback dataset and must not be represented as MOIL exploration ground truth. Grade is a verified product reference rather than an in-situ spatial estimator. Production is historical context rather than a forward forecast. Equipment, recovery, blast, and weather remain disclosed demonstrations.

## Before institutional production

Application wiring is deployment-ready, but production authorization still requires an organization-selected identity provider and role policy. A hosted environment should also use a managed PostGIS database, a workload/service identity for Earth Engine, a secret manager, TLS ingress, centralized rate limiting, audit retention, observability, backup/restore drills, vulnerability scanning, and load/capacity tests. Advancing DEMO modules to LIVE requires real governed training data, validation, model cards, and domain-owner approval.
