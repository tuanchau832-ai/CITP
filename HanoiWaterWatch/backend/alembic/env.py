import os
from alembic import context
from sqlalchemy import create_engine
from app.models import Base
config=context.config
url=os.getenv('DATABASE_URL',config.get_main_option('sqlalchemy.url')).replace('sqlite+aiosqlite:','sqlite:').replace('postgresql+asyncpg:','postgresql+psycopg:')
if url.startswith('postgresql://'):url=url.replace('postgresql://','postgresql+psycopg://',1)
if context.is_offline_mode():
 context.configure(url=url,target_metadata=Base.metadata,literal_binds=True)
 with context.begin_transaction():context.run_migrations()
else:
 engine=create_engine(url)
 with engine.connect() as connection:
  context.configure(connection=connection,target_metadata=Base.metadata,render_as_batch=engine.dialect.name=='sqlite')
  with context.begin_transaction():context.run_migrations()
