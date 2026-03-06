from typing import Annotated, Sequence, Tuple
from uuid import UUID, uuid4

import numpy as np
from fastapi import Depends
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload, selectinload

from across_server.core.enums.instrument_fov import InstrumentFOV

from ....db import models
from ....db.database import get_session
from . import schemas
from .exceptions import (
    DuplicateScheduleException,
    ScheduleInstrumentNotFoundException,
    ScheduleNotFoundException,
)


class ScheduleService:
    """
    -------
    Schedule service for managing astronomical observing Schedules.
    This service handles CRUD operations for Schedule records. This includes retrieval,
    and creation of new Schedule records in the database.

    -------
    Methods:
    -------
    get(schedule_id: UUID) -> models.Schedule
        Retrieve the Schedule record with the given id.
    get_from_checksum(checksum: str) -> models.Schedule | None:
        Retrieve the Schedule record with the given checksum.
    get_many(data: schemas.ScheduleRead) -> Sequence[models.Schedule]
        Retrieves the most recent Schedules for telescopes based on the ScheduleRead filter
        params
    get_history(data: schemas.ScheduleRead) -> Sequence[models.Schedule]
        Retrieves all Schedules based on the ScheduleRead filter params
    create(data: schemas.ScheduleCreate) -> models.Schedule
        Create a new Schedule for a telescope with the ScheduleCreate metadata
    """

    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    async def get(
        self,
        schedule_id: UUID,
        include_observations: bool = False,
        include_observations_footprints: bool = False,
    ) -> models.Schedule:
        """
        Retrieve the Schedule record with the given checksum.

        Parameters
        ----------
        schedule_id : UUID
            the Schedule id
        include_observations: bool, optional
            Whether to include observations in the returned schedule
        include_observations_footprints: bool, optional
            Whether to include observation footprints in the returned schedule if observations are included

        Returns
        -------
        models.Schedule
            The Schedule with the given id

        Raises
        ------
        ScheduleNotFoundException
        """
        query_options = self._get_schedule_query_options(
            include_observations=include_observations,
            include_observations_footprints=include_observations_footprints,
        )

        query = (
            select(models.Schedule)
            .where(models.Schedule.id == schedule_id)
            .options(query_options)  # type: ignore
        )

        result = await self.db.execute(query)
        schedule = result.scalar_one_or_none()

        if schedule is None:
            raise ScheduleNotFoundException(schedule_id)

        return schedule

    async def get_many(
        self, data: schemas.ScheduleRead
    ) -> Sequence[Tuple[models.Schedule, int]]:
        """
        Retrieve a list of the most recent, individual Schedule records for each telescope
        based on the ScheduleRead filter parameters.

        Parameters
        ----------
        data : schemas.ScheduleRead
             class representing Schedule filter parameters

        Returns
        -------
        Sequence[Tuple[models.Schedule, int]]
            The list of Schedules and total number of entries passing the filter
        """
        schedule_filter = self._get_schedule_filter(data=data)

        query_options = self._get_schedule_query_options(
            include_observations=data.include_observations,
            include_observations_footprints=data.include_observations_footprints,
        )

        schedule_query = (
            select(models.Schedule, func.count().over().label("count"))
            .filter(*schedule_filter)
            .distinct(
                models.Schedule.created_on,
                models.Schedule.date_range_begin,
                models.Schedule.date_range_end,
                models.Schedule.status,
                models.Schedule.fidelity,
                models.Schedule.telescope_id,
            )
            .order_by(
                models.Schedule.created_on.desc(),
                models.Schedule.date_range_begin,
                models.Schedule.date_range_end,
                models.Schedule.status,
                models.Schedule.fidelity,
                models.Schedule.telescope_id,
            )
            .group_by(models.Schedule.id)
            .limit(data.page_limit)
            .offset(data.offset)
            .options(query_options)  # type: ignore
        )

        result = await self.db.execute(schedule_query)

        schedules = result.tuples().all()

        return schedules

    async def get_history(
        self, data: schemas.ScheduleRead
    ) -> Sequence[Tuple[models.Schedule, int]]:
        """
        Retrieve a list of Schedule records for each telescope
        based on the ScheduleRead filter parameters.

        Parameters
        ----------
        data : schemas.ScheduleRead
             class representing Schedule filter parameters

        Returns
        -------
        Sequence[Tuple[models.Schedule, int]]
            The list of Schedules and total number of entries passing the filter
        """
        schedule_filter = self._get_schedule_filter(data=data)
        query_options = self._get_schedule_query_options(
            include_observations=data.include_observations,
            include_observations_footprints=data.include_observations_footprints,
        )

        schedule_query = (
            select(models.Schedule, func.count().over().label("count"))
            .filter(*schedule_filter)
            .order_by(models.Schedule.created_on.desc())
            .limit(data.page_limit)
            .offset(data.offset)
            .options(query_options)  # type: ignore
        )

        result = await self.db.execute(schedule_query)

        schedules = result.tuples().all()

        return schedules

    async def create(
        self,
        schedule_create: schemas.ScheduleCreate,
        instruments: list[models.Instrument],
        created_by_id: UUID,
    ) -> UUID:
        """
        Creates a new Schedule record in the database.

        Parameters
        ----------
        schedule_create : schemas.ScheduleCreate
            The Schedule data to be created, following the ScheduleCreate schema format.
        instruments : list[models.Instrument]
            The list of instruments associated with the Schedule.
        created_by_id : UUID
            The ID of the user creating the Schedule.
        Returns
        -------
        models.Schedule
            The created Schedule object with populated Schedule and list of Observation database fields.

        Raises
        ------
        DuplicateScheduleException
            If a Schedule with the same metadata, and observational metadata already exists in the database.
        ScheduleInstrumentNotFoundException
            If an instrument in the Schedule does not belong to the telescope associated with the Schedule.

        Notes
        -----
        The function validates the input data, checks for duplicates based on a checksum created from the
        create schemas performs the database insertion for the schedule and observations in a single commit.
        """
        schedule = schedule_create.to_orm(created_by_id=created_by_id)

        instrument_dict = {instrument.id: instrument for instrument in instruments}

        # schedule validation
        existing = await self._exists([schedule.checksum])

        if len(existing):
            raise DuplicateScheduleException(existing[0].id)

        schedule_instrument_ids = list(
            set(
                [
                    observation.instrument_id
                    for observation in schedule_create.observations
                ]
            )
        )

        for schedule_instrument_id in schedule_instrument_ids:
            if not instrument_dict.get(schedule_instrument_id):
                raise ScheduleInstrumentNotFoundException(
                    instrument_id=schedule_instrument_id,
                    telescope_id=schedule.telescope_id,
                )

        # schedule creation
        schedule.id = uuid4()
        self.db.add(schedule)

        for observation_create in schedule_create.observations:
            instrument = instrument_dict[observation_create.instrument_id]
            fov = InstrumentFOV(instrument.field_of_view)
            observation = observation_create.to_orm(instrument_fov=fov)
            observation.id = uuid4()
            observation.schedule_id = schedule.id
            observation.created_by_id = created_by_id
            self.db.add(observation)
            for footprint_create in observation_create.footprint or []:
                footprint = footprint_create.to_orm()
                footprint.observation_id = observation.id
                self.db.add(footprint)

        await self.db.commit()
        return schedule.id

    async def create_many(
        self,
        schedule_create_many: schemas.ScheduleCreateMany,
        instruments: list[models.Instrument],
        created_by_id: UUID,
    ) -> list[UUID]:
        instrument_dict = {instrument.id: instrument for instrument in instruments}

        # Make list of models.Schedule objects from the data
        schedules = [
            schedule_create.to_orm(created_by_id=created_by_id)
            for schedule_create in schedule_create_many.schedules
        ]

        # Get the subset of schedules that already exist
        existing_schedules = await self._exists(
            [schedule.checksum for schedule in schedules]
        )

        # Get array of schedule_ids for existing schedules to append to and return
        schedule_ids = [schedule.id for schedule in np.asarray(existing_schedules)]

        # Get array of checksums of existing schedules to compare against the schedules being added
        existing_schedules_checksums = [
            schedule.checksum for schedule in existing_schedules
        ]

        # Make filter for existing schedules
        schedule_filter = np.asarray(
            [
                schedule.checksum in existing_schedules_checksums
                for schedule in schedules
            ]
        )

        # For the schedules that don't exist yet, iterate over them,
        # create arrays of schedules and observations to bulk add
        schedules_to_add = []
        observations_to_add = []
        observation_footprints_to_add = []
        for i, schedule in enumerate(
            np.asarray(schedules)[np.logical_not(schedule_filter)]
        ):
            schedule_create = schedule_create_many.schedules[i]
            schedule_instrument_ids = list(
                set(
                    [
                        observation.instrument_id
                        for observation in schedule_create.observations
                    ]
                )
            )

            for schedule_instrument_id in schedule_instrument_ids:
                if not instrument_dict.get(schedule_instrument_id):
                    raise ScheduleInstrumentNotFoundException(
                        instrument_id=schedule_instrument_id,
                        telescope_id=schedule.telescope_id,
                    )

            schedule.id = uuid4()
            schedules_to_add.append(schedule)
            schedule_ids.append(schedule.id)

            for observation_create in schedule_create.observations:
                instrument = instrument_dict[observation_create.instrument_id]
                fov = InstrumentFOV(instrument.field_of_view)
                observation = observation_create.to_orm(instrument_fov=fov)
                observation.id = uuid4()
                observation.schedule_id = schedule.id
                observation.created_by_id = created_by_id
                for footprint_create in observation_create.footprint or []:
                    footprint = footprint_create.to_orm()
                    footprint.observation_id = observation.id
                    observation_footprints_to_add.append(footprint)
                observations_to_add.append(observation)

        self.db.add_all(
            list(
                (
                    *schedules_to_add,
                    *observations_to_add,
                    *observation_footprints_to_add,
                )
            )
        )
        await self.db.commit()
        return schedule_ids

    async def _exists(self, checksums: list[str]) -> Sequence[models.Schedule]:
        """
        Retrieve the Schedule records with the given checksums.

        Parameters
        ----------
        checksum : list[str]
            the Schedule checksum

        Returns
        -------
        Sequence[models.Schedule]
            returns an array of Schedule records

        """
        query = select(models.Schedule).filter(models.Schedule.checksum.in_(checksums))
        result = await self.db.execute(query)
        schedules = result.scalars().all()
        return schedules

    def _get_schedule_filter(self, data: schemas.ScheduleRead) -> list:
        """
        Build the sql alchemy filter list based on ScheduleRead.
        Parses whether or not any of the fields are populated, and constructs a list
        of sqlalchemy filter booleans for a schedule

        Parameters
        ----------
        data : schemas.ScheduleRead
             class representing Schedule filter parameters

        Returns
        -------
        list[sqlalchemy.filters]
            list of schedule filter booleans
        """
        data_filter = []

        if data.date_range_begin:
            data_filter.append(models.Schedule.date_range_end > data.date_range_begin)

        if data.date_range_end:
            data_filter.append(models.Schedule.date_range_begin < data.date_range_end)

        if data.status:
            data_filter.append(models.Schedule.status == data.status)

        if data.external_id:
            data_filter.append(
                func.lower(models.Schedule.external_id).contains(
                    str.lower(data.external_id)
                )
            )

        if data.created_on:
            data_filter.append(
                models.Schedule.created_on >= data.created_on
            )  # this should/could be a date-range parameter

        if data.observatory_ids and len(data.observatory_ids):
            data_filter.append(
                models.Schedule.telescope.has(
                    models.Telescope.observatory_id.in_(data.observatory_ids)
                )
            )

        if data.observatory_names and len(data.observatory_names):
            observatory_name_or_filter = []

            for observatory_name in data.observatory_names:
                observatory_name_or_filter.append(
                    models.Schedule.telescope.has(
                        models.Telescope.observatory.has(
                            func.lower(models.Observatory.name).contains(
                                str.lower(observatory_name)
                            )
                        )
                    )
                )

                observatory_name_or_filter.append(
                    models.Schedule.telescope.has(
                        models.Telescope.observatory.has(
                            func.lower(models.Observatory.short_name).contains(
                                str.lower(observatory_name)
                            )
                        )
                    )
                )

            data_filter.append(or_(*observatory_name_or_filter))

        if data.telescope_ids and len(data.telescope_ids):
            data_filter.append(models.Schedule.telescope_id.in_(data.telescope_ids))

        if data.telescope_names and len(data.telescope_names):
            telescope_name_or_filter = []

            for telescope_name in data.telescope_names:
                telescope_name_or_filter.append(
                    models.Schedule.telescope.has(
                        func.lower(models.Telescope.name).contains(
                            str.lower(telescope_name)
                        )
                    )
                )

                telescope_name_or_filter.append(
                    models.Schedule.telescope.has(
                        func.lower(models.Telescope.short_name).contains(
                            str.lower(telescope_name)
                        )
                    )
                )

            data_filter.append(or_(*telescope_name_or_filter))

        if data.name:
            data_filter.append(
                func.lower(models.Schedule.name).contains(str.lower(data.name))
            )

        if data.fidelity:
            data_filter.append(models.Schedule.fidelity == data.fidelity.value)

        return data_filter

    def _get_schedule_query_options(
        self,
        include_observations: bool | None,
        include_observations_footprints: bool | None = False,
    ) -> list[tuple]:
        if include_observations:
            if include_observations_footprints:
                return selectinload(models.Schedule.observations).selectinload(
                    models.Observation.footprints
                )  # type: ignore
            return selectinload(models.Schedule.observations)  # type: ignore

        return noload(models.Schedule.observations)  # type: ignore
