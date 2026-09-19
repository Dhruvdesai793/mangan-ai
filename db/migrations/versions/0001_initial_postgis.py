"""Initial PostGIS persistence schema."""
from alembic import op

revision = "0001_initial_postgis"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("""
    CREATE TABLE IF NOT EXISTS mines (
      id BIGSERIAL PRIMARY KEY, site_id VARCHAR(32) NOT NULL UNIQUE,
      mine_name VARCHAR(160) NOT NULL, state VARCHAR(80) NOT NULL, district VARCHAR(80) NOT NULL,
      latitude DOUBLE PRECISION NOT NULL, longitude DOUBLE PRECISION NOT NULL,
      mining_method VARCHAR(80) NOT NULL, operational_status VARCHAR(80) NOT NULL,
      source_id VARCHAR(120) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS ix_mines_site_id ON mines(site_id);
    CREATE TABLE IF NOT EXISTS mine_leases (
      id BIGSERIAL PRIMARY KEY, mine_id BIGINT NOT NULL REFERENCES mines(id) ON DELETE CASCADE,
      site_id VARCHAR(32) NOT NULL, source VARCHAR(120) NOT NULL,
      source_record_id VARCHAR(160) NOT NULL UNIQUE, verification_status VARCHAR(80) NOT NULL,
      dataset_vintage VARCHAR(40) NOT NULL, properties JSONB NOT NULL DEFAULT '{}'::jsonb,
      geometry geometry(MULTIPOLYGON, 4326) NOT NULL
    );
    CREATE INDEX IF NOT EXISTS ix_mine_leases_site_id ON mine_leases(site_id);
    CREATE INDEX IF NOT EXISTS ix_mine_leases_geometry ON mine_leases USING GIST(geometry);
    CREATE TABLE IF NOT EXISTS grade_references (
      id BIGSERIAL PRIMARY KEY, site_id VARCHAR(32) NOT NULL,
      source_record_id VARCHAR(160) NOT NULL UNIQUE, payload JSONB NOT NULL
    );
    CREATE INDEX IF NOT EXISTS ix_grade_references_site_id ON grade_references(site_id);
    CREATE TABLE IF NOT EXISTS production_references (
      id BIGSERIAL PRIMARY KEY, site_id VARCHAR(32) NOT NULL,
      source_record_id VARCHAR(160) NOT NULL UNIQUE, reference_year VARCHAR(24) NOT NULL, payload JSONB NOT NULL
    );
    CREATE INDEX IF NOT EXISTS ix_production_references_site_id ON production_references(site_id);
    CREATE INDEX IF NOT EXISTS ix_production_references_year ON production_references(reference_year);
    CREATE TABLE IF NOT EXISTS satellite_features (
      id BIGSERIAL PRIMARY KEY, cache_key VARCHAR(256) NOT NULL UNIQUE, site_id VARCHAR(32) NOT NULL,
      date_start VARCHAR(10) NOT NULL, date_end VARCHAR(10) NOT NULL, pipeline_version VARCHAR(32) NOT NULL,
      data_source VARCHAR(160) NOT NULL, features JSONB NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS ix_satellite_features_site_id ON satellite_features(site_id);
    CREATE INDEX IF NOT EXISTS ix_satellite_features_created_at ON satellite_features(created_at);
    CREATE TABLE IF NOT EXISTS prediction_runs (
      id VARCHAR(40) PRIMARY KEY, request_id VARCHAR(64) NOT NULL, site_id VARCHAR(32), scenario_id VARCHAR(120),
      input_snapshot JSONB NOT NULL, output_snapshot JSONB NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS ix_prediction_runs_request_id ON prediction_runs(request_id);
    CREATE INDEX IF NOT EXISTS ix_prediction_runs_site_id ON prediction_runs(site_id);
    CREATE INDEX IF NOT EXISTS ix_prediction_runs_created_at ON prediction_runs(created_at);
    CREATE TABLE IF NOT EXISTS jobs (
      id VARCHAR(40) PRIMARY KEY, job_type VARCHAR(64) NOT NULL, status VARCHAR(24) NOT NULL,
      payload JSONB NOT NULL DEFAULT '{}'::jsonb, result JSONB, error TEXT,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS ix_jobs_status ON jobs(status);
    CREATE INDEX IF NOT EXISTS ix_jobs_job_type ON jobs(job_type);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS jobs, prediction_runs, satellite_features, production_references, grade_references, mine_leases, mines CASCADE")
