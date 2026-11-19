"""Initial rule catalogue. Subsequent seeding preserves administrative edits."""
from alembic import op
from sqlalchemy.orm import Session
from app.models import Rule
from app.service import rule_defaults
revision='0002_seed_rules'
down_revision='0001_initial'
branch_labels=None
depends_on=None

def upgrade():
 with Session(op.get_bind()) as db:
  for code,data in rule_defaults().items():
   if not db.get(Rule,code):db.add(Rule(code=code,data=data))
  db.flush()
def downgrade():raise RuntimeError('Forward-only project migration')
