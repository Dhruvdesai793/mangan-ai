"""Persist arbitrary coordinate exploration targets."""
from alembic import op

revision = "0002_exploration_targets"
down_revision = "0001_initial_postgis"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE IF NOT EXISTS exploration_targets (
      id VARCHAR(40) PRIMARY KEY,
      name VARCHAR(120), latitude DOUBLE PRECISION NOT NULL, longitude DOUBLE PRECISION NOT NULL,
      buffer_m INTEGER NOT NULL DEFAULT 250, feature_source VARCHAR(160) NOT NULL,
      features JSONB NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS ix_exploration_targets_created_at ON exploration_targets(created_at);
    CREATE INDEX IF NOT EXISTS ix_exploration_targets_coordinates ON exploration_targets(latitude, longitude);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS exploration_targets")
