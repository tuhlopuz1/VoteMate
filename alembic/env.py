import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import pool

from alembic import context
from backend.models.db_tables import Base

load_dotenv("config/.env")

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
db = os.getenv("POSTGRES_DBNAME")

DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"


def run_migrations_online():
    from sqlalchemy.ext.asyncio import create_async_engine

    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async def do_run_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(
                lambda sync_conn: context.configure(
                    connection=sync_conn,
                    target_metadata=target_metadata,
                    compare_type=True,
                    render_as_batch=True,
                )
            )
            async with context.begin_transaction():
                await context.run_migrations()

    import asyncio

    asyncio.run(do_run_migrations())
