import asyncio
from logging.config import fileConfig
from typing import Any

import structlog
from alembic import context
from geoalchemy2 import alembic_helpers
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.schema import CreateSchema

from across_server.core import config as core_config
from across_server.db import config, models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
ctx_config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if ctx_config.config_file_name is not None:
    fileConfig(ctx_config.config_file_name)

logger = structlog.getLogger()

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = models.Base.metadata


def include_name(name: Any, type_: Any | None, parent_names: Any) -> bool:
    """Used to only autogenerate migrations ACROSS models

    See: [Alembic Docs](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#omitting-schema-names-from-the-autogenerate-process)
    """
    if type_ == "schema":
        # this **will** include the default schema
        return name in [config.ACROSS_DB_NAME]
    else:
        return True


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
logger.info(f"Running migration for '{core_config.APP_ENV.value}' environment.")
DATABASE_URL = config.DB_URI()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        render_item=alembic_helpers.render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=target_metadata.schema,
        include_name=include_name,
        include_schemas=True,
        render_item=alembic_helpers.render_item,
    )

    with context.begin_transaction():
        if target_metadata.schema:
            # This is only relevant for local development...the schema must be
            # created separately outside of the actual migration because the
            # migration context will not have the schema created yet.
            context.execute(CreateSchema(target_metadata.schema, if_not_exists=True))
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """

    engine = create_async_engine(
        url=DATABASE_URL,
        pool_pre_ping=True,
        connect_args={"ssl": "require" if not core_config.is_local() else "allow"},
    )

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
