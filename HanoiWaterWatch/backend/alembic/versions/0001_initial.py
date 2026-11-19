"""Initial durable platform schema, including episode and idempotency constraints."""
from alembic import op
from app.models import Base
revision='0001_initial'
down_revision=None
branch_labels=None
depends_on=None

def upgrade():Base.metadata.create_all(bind=op.get_bind())
def downgrade():raise RuntimeError('Forward-only project migration')
