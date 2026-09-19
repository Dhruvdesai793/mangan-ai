"""Persist coordinate model evidence alongside exploration targets."""
from alembic import op

revision = "0003_target_model_evidence"
down_revision = "0002_exploration_targets"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("ALTER TABLE exploration_targets ADD COLUMN IF NOT EXISTS model_results JSONB NOT NULL DEFAULT '{}'::jsonb")
    op.execute("ALTER TABLE exploration_targets ADD COLUMN IF NOT EXISTS decision JSONB NOT NULL DEFAULT '{}'::jsonb")
    op.execute("ALTER TABLE exploration_targets ADD COLUMN IF NOT EXISTS scenario_id VARCHAR(120)")

def downgrade() -> None:
    op.execute("ALTER TABLE exploration_targets DROP COLUMN IF EXISTS scenario_id")
    op.execute("ALTER TABLE exploration_targets DROP COLUMN IF EXISTS decision")
    op.execute("ALTER TABLE exploration_targets DROP COLUMN IF EXISTS model_results")
