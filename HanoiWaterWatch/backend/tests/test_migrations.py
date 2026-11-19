import os
from pathlib import Path
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine,inspect,select,func
from app.models import Base,Rule
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql

def test_empty_database_migrations(tmp_path,monkeypatch):
    url='sqlite:///'+str(tmp_path/'migrations.db');monkeypatch.setenv('DATABASE_URL',url)
    config=Config(str(Path(__file__).resolve().parents[1]/'alembic.ini'));command.upgrade(config,'head')
    engine=create_engine(url)
    assert set(Base.metadata.tables).issubset(set(inspect(engine).get_table_names()))
    with Session(engine) as db:assert db.scalar(select(func.count()).select_from(Rule))==6
    engine.dispose()

def test_postgres_ddl_uses_timezone_and_jsonb():
    ddl=str(CreateTable(Base.metadata.tables['measurements']).compile(dialect=postgresql.dialect()))
    assert 'TIMESTAMP WITH TIME ZONE' in ddl and 'simulated_wokwi' in ddl
    assert 'JSONB' in str(CreateTable(Base.metadata.tables['stations']).compile(dialect=postgresql.dialect()))
