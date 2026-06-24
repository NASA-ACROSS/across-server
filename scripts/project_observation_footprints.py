import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time

import structlog
from geoalchemy2 import shape
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from across_server.db import config, models
from migrations.util import footprint_util

logger: structlog.stdlib.BoundLogger = structlog.get_logger()

MAX_RECORDS_PER_WRITE = 1000


async def project_observation_footprints() -> None:
    logger.info("Starting project_observation_footprints")
    start_time = time.perf_counter()

    engine = create_async_engine(config.DB_URI)

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # Get all observations for each instrument
        instrument_query = select(models.Instrument)
        result = await session.execute(instrument_query)
        instruments = result.scalars().all()

        records = []

        for index, instrument in enumerate(instruments, start=1):
            logger.info(
                f"({index}/{len(instruments)}) Gathering observations for {instrument.name}"
            )

            # Get observations for this instrument with pointing coordinates
            # and no projected footprints
            obs_query = select(models.Observation).where(
                models.Observation.instrument_id == instrument.id,
                models.Observation.pointing_ra.isnot(None),
                models.Observation.pointing_dec.isnot(None),
                ~models.Observation.footprints.any(),
            )
            obs_result = await session.execute(obs_query)
            observations = obs_result.scalars().all()

            detectors: list[list[dict[str, float]]] = []
            for footprint in instrument.footprints:
                poly = shape.to_shape(footprint.polygon)
                x, y = poly.exterior.coords.xy  # type: ignore
                detectors.append([{"x": x[i], "y": y[i]} for i in range(len(x))])

            logger.info("Projecting footprints for %s observations", len(observations))
            for observation in observations:
                # Project the instrument footprint to the pointing position and save it
                projected_footprints = footprint_util.project_footprint(
                    detectors,
                    observation.pointing_ra,  # type: ignore[arg-type]
                    observation.pointing_dec,  # type: ignore[arg-type]
                    observation.pointing_angle
                    if observation.pointing_angle is not None
                    else 0.0,
                )

                # convert the projected footprint to a list of FootprintPoints
                for projected_footprint in projected_footprints:
                    vertices = [
                        footprint_util.ACROSSFootprintPoint(x=point["x"], y=point["y"])
                        for point in projected_footprint
                    ]

                    wkb_footprint = footprint_util.create_geography(polygon=vertices)

                    # create the footprint model record
                    observation_footprint = models.ObservationFootprint(
                        polygon=wkb_footprint, observation_id=observation.id
                    )
                    records.append(observation_footprint)

        logger.info("Committing to db")
        for i in range(0, len(records), MAX_RECORDS_PER_WRITE):
            chunk = records[i : i + MAX_RECORDS_PER_WRITE]
            session.add_all(chunk)
            await session.commit()

        elapsed_seconds = time.perf_counter() - start_time
        mins, secs = map(int, divmod(elapsed_seconds, 60))

        logger.info(f"Done. Took: {mins} min {secs} sec")

    return None


if __name__ == "__main__":
    asyncio.run(project_observation_footprints())
