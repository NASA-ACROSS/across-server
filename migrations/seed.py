import asyncio
from sqlite3 import IntegrityError
from typing import Sequence, Type

from asyncpg import UniqueViolationError
import structlog
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from across_server.db import config, models

from .seeds.footprints import footprints
from .seeds.group_roles import group_roles
from .seeds.groups import groups
from .seeds.instruments import instruments
from .seeds.observations import observations
from .seeds.observatories import (
    earth_location_parameters,
    ephemeris_types,
    jpl_parameters,
    observatories,
    spice_kernel_parameters,
    tle_parameters,
)
from .seeds.roles import roles
from .seeds.schedules import schedules
from .seeds.telescopes import telescopes
from .seeds.tles import tles
from .seeds.users import users

logger: structlog.stdlib.BoundLogger = structlog.get_logger()

seed_order: list[tuple[Type[DeclarativeBase], Sequence[DeclarativeBase]]] = [
    (models.Role, roles),
    (models.Group, groups),
    (models.GroupRole, group_roles),
    (models.User, users),
    (models.Observatory, observatories),
    (models.ObservatoryEphemerisType, ephemeris_types),
    (models.Telescope, telescopes),
    (models.Instrument, instruments),
    (models.Footprint, footprints),
    (models.Schedule, schedules),
    (models.Observation, observations),
    #(models.TLE, tles),
    #(models.TLEParameters, tle_parameters),
    #(models.JPLEphemerisParameters, jpl_parameters),
    #(models.SpiceKernelParameters, spice_kernel_parameters),
    #(models.EarthLocationParameters, earth_location_parameters),
]


async def seed() -> None:
    engine = create_async_engine(config.DB_URI())

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        try:
            for [model, records] in seed_order:
                session.add_all(records)

                logger.info(f"Seeded {model.__tablename__} in txn.")

            await session.commit()
            logger.info("Seeding commit successful.")
        except Exception as err:
            if "already exists" in err.__str__():
                pass
            else:
                logger.error("Seeding failed, rolling back.", err=err)
                await session.rollback()

    await engine.dispose()


asyncio.run(seed())
