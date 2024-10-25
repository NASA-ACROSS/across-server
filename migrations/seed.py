import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from across_server.db import config, models

from .seeds.users import users
from .seeds.permissions import permissions
from .seeds.roles import roles
from .seeds.group_roles import group_roles
from .seeds.groups import groups
from .seeds.observatories import observatories
from .seeds.telescopes import telescopes
from .seeds.instruments import instruments
from .seeds.footprints import footprints


seed_order = [
    [models.Permission.__tablename__, permissions],
    [models.Role.__tablename__, roles],
    [models.Group.__tablename__, groups],
    [models.GroupRole.__tablename__, group_roles],
    [models.User.__tablename__, users],
    [models.Observatory.__tablename__, observatories],
    [models.Telescope.__tablename__, telescopes],
    [models.Instrument.__tablename__, instruments],
    [models.Footprint.__tablename__, footprints],
]


async def seed():
    engine = create_async_engine(config.DB_URI())

    async_session = async_sessionmaker(engine)

    async with async_session() as session:
        try:
            for [table, records] in seed_order:
                for record in records:
                    session.add(record)

                print(f"seeded {table}")

            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"Rolled back due to an error: {e}")

    await engine.dispose()


asyncio.run(seed())
