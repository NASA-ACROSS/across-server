from collections.abc import AsyncGenerator
from typing import Tuple

import structlog
from sqlalchemy import Dialect, event, pool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ..core.config import config as core_config
from .config import config

logger: structlog.stdlib.BoundLogger = structlog.get_logger()

engine: AsyncEngine
async_session: async_sessionmaker


# see: https://docs.sqlalchemy.org/en/20/core/events.html#sqlalchemy.events.DialectEvents.do_connect
def refresh_token(
    _dialect: Dialect,
    _conn_rec: pool.ConnectionPoolEntry,
    _cargs: Tuple,
    cparams: dict,
) -> None:
    logger.debug("Refreshing RDS IAM Auth token")
    cparams["password"] = config.get_iam_rds_token()
    logger.debug("Token Refreshed, connecting...")


def init() -> None:
    """
    Initialize database engine and sessionmaker
    """

    global engine
    global async_session

    engine = create_async_engine(
        url=config.DB_URI,
        pool_pre_ping=True,
        connect_args={"ssl": "require" if not core_config.is_local() else False},
    )
    logger.debug("Created async db engine")

    async_session = async_sessionmaker(
        autocommit=False,
        expire_on_commit=False,
        autoflush=False,
        bind=engine,
    )
    logger.debug("Created async db session")

    event.listen(engine.sync_engine, "do_connect", refresh_token)


async def get_session() -> AsyncGenerator[AsyncSession]:
    """
    Dependency to handle session lifecycle per request.
    Any dependency will used the cached result of this function when used with fastapi's `Depends`

    Once all dependencies have finished with their usage of the session, it will close.
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            # This will run after the last usage in downstream
            # dependencies regardless of success or failure.
            await session.close()
