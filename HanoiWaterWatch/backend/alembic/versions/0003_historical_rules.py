"""Persist isolated historical rule counters on existing development databases."""
from alembic import op
from sqlalchemy import inspect,Column
from app.models import J
revision='0003_historical_rules'
down_revision='0002_seed_rules'
branch_labels=None
depends_on=None

def upgrade():
 if 'historical_rule_state' not in {c['name'] for c in inspect(op.get_bind()).get_columns('sensor_state')}:
  op.add_column('sensor_state',Column('historical_rule_state',J,nullable=True))
def downgrade():raise RuntimeError('Forward-only project migration')
