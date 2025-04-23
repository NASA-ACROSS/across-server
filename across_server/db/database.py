from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import config

engine = create_async_engine(
    config.DB_URI(), connect_args={"ssl": "allow"}, pool_pre_ping=True
)

async_session = async_sessionmaker(
    autocommit=False,
    expire_on_commit=False,
    autoflush=False,
    bind=engine,
)


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
