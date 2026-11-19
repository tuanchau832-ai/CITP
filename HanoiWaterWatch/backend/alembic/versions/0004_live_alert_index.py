"""Allow an unresolved historical episode beside a live condition."""

from alembic import op
from sqlalchemy import text

revision = '0004'
down_revision = '0003_historical_rules'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index('uq_active_sensor_alert', table_name='alerts')
    predicate = text('cleared_at IS NULL AND sensor IS NOT NULL AND detected_late IS FALSE')
    op.create_index('uq_active_sensor_alert', 'alerts', ['sensor', 'rule_code'], unique=True,
                    sqlite_where=predicate, postgresql_where=predicate)


def downgrade():
    raise RuntimeError('Forward-only project migration')
