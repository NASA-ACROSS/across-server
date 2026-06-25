import os
import sys
from concurrent.futures import ThreadPoolExecutor
from itertools import batched

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time

import structlog
from geoalchemy2 import shape
from sqlalchemy import select

from across_server.db import database, models
from migrations.util import footprint_util

logger: structlog.stdlib.BoundLogger = structlog.get_logger()

MAX_RECORDS_PER_WRITE = 1000
MAX_PROJECTION_WORKERS = max(1, os.cpu_count() or 1)
PROJECTION_BATCH_SIZE = 256


def _project_observation_footprint(
    observation_id: int,
    pointing_ra: float,
    pointing_dec: float,
    pointing_angle: float,
    detectors: list[list[dict[str, float]]],
) -> tuple[int, list]:
    projected_footprints = footprint_util.project_footprint(
        detectors,
        pointing_ra,
        pointing_dec,
        pointing_angle,
    )

    geometries = []
    for projected_footprint in projected_footprints:
        vertices = [
            footprint_util.ACROSSFootprintPoint(x=point["x"], y=point["y"])
            for point in projected_footprint
        ]
        geometries.append(footprint_util.create_geography(polygon=vertices))

    return observation_id, geometries


async def project_footprints(observations, detectors):
    if not observations:
        return []

    loop = asyncio.get_running_loop()
    max_workers = min(MAX_PROJECTION_WORKERS, len(observations))
    footprints = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for observation_batch in batched(observations, PROJECTION_BATCH_SIZE):
            batch_results = await asyncio.gather(
                *[
                    loop.run_in_executor(
                        executor,
                        _project_observation_footprint,
                        observation.id,
                        observation.pointing_ra,
                        observation.pointing_dec,
                        observation.pointing_angle
                        if observation.pointing_angle is not None
                        else 0.0,
                        detectors,
                    )
                    for observation in observation_batch
                ]
            )
            footprints.extend(batch_results)

    return footprints


async def project_observation_footprints() -> None:
    start_time = time.perf_counter()

    database.init()

    async with database.async_session() as session:
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
            footprints = await project_footprints(observations, detectors)

            for observation_id, geometries in footprints:
                for wkb_footprint in geometries:
                    records.append(
                        models.ObservationFootprint(
                            polygon=wkb_footprint,
                            observation_id=observation_id,
                        )
                    )

        chunks = batched(records, MAX_RECORDS_PER_WRITE)

        logger.info("Committing to db")
        for _, chunk in enumerate(chunks):
            session.add_all(chunk)
            await session.commit()

    elapsed_seconds = time.perf_counter() - start_time
    mins, secs = map(int, divmod(elapsed_seconds, 60))
    logger.info(f"Done. took: {mins} min {secs} sec")


if __name__ == "__main__":
    asyncio.run(project_observation_footprints())
