# Persistence

SQLAlchemy models and repositories isolate storage from API and model code. PostgreSQL/PostGIS stores mines, verified lease geometries, reference grades and production, cached satellite features, prediction audit snapshots, and asynchronous job state.

Alembic owns schema evolution under `db/migrations`. Apply migrations with `alembic upgrade head`; seed reference data with `python scripts/seed_reference_data.py`. Both operations are performed automatically by the Compose `migrate` service and the seed operation is idempotent.

If the database is optional and unavailable, read paths fall back to the checked-in validated reference artifacts. Prediction persistence and cache writes fail closed without preventing a model response. Set `MANGAN_DATABASE_REQUIRED=true` in deployments where a missing database must stop startup.
