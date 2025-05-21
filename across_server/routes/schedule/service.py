from typing import Annotated, Sequence
from uuid import UUID, uuid4

from fastapi import Depends
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from across_server.core.enums.instrument_fov import InstrumentFOV

from ...db import models
from ...db.database import get_session
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

    async def get(self, schedule_id: UUID) -> models.Schedule:
        """
        Retrieve the Schedule record with the given checksum.

        Parameters
        ----------
        schedule_id : UUID
            the Schedule id

        Returns
        -------
        models.Schedule
            The Schedule with the given id

        Raises
        ------
        ScheduleNotFoundException
        """
        query = select(models.Schedule).where(models.Schedule.id == schedule_id)

        result = await self.db.execute(query)
        schedule = result.scalar_one_or_none()

        if schedule is None:
            raise ScheduleNotFoundException(schedule_id)

        return schedule

    async def _exists(self, checksum: str) -> models.Schedule | None:
        """
        Retrieve the Schedule record with the given checksum.

        Parameters
        ----------
        checksum : str
            the Schedule checksum

        Returns
        -------
        models.Schedule | None
            returns a Schedule record

        """
        query = select(models.Schedule).filter(models.Schedule.checksum == checksum)
        result = await self.db.execute(query)
        schedule = result.scalar_one_or_none()
        return schedule

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
            date_range_begin_or = [
                models.Schedule.date_range_begin >= data.date_range_begin,
                models.Schedule.date_range_end > data.date_range_begin,
            ]
            data_filter.append(or_(*date_range_begin_or))

        if data.date_range_end:
            date_range_end_or = [
                models.Schedule.date_range_end <= data.date_range_end,
                models.Schedule.date_range_begin < data.date_range_end,
            ]
            data_filter.append(or_(*date_range_end_or))

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

    async def get_many(self, data: schemas.ScheduleRead) -> Sequence[models.Schedule]:
        """
        Retrieve a list of the most recent, individual Schedule records for each telescope
        based on the ScheduleRead filter parameters.

        Parameters
        ----------
        data : schemas.ScheduleRead
             class representing Schedule filter parameters

        Returns
        -------
        Sequence[models.Schedule]
            The list of Schedules
        """
        schedule_filter = self._get_schedule_filter(data=data)

        schedule_query = (
            select(models.Schedule)
            .filter(*schedule_filter)
            .distinct(
                models.Schedule.date_range_begin,
                models.Schedule.date_range_end,
                models.Schedule.status,
                models.Schedule.fidelity,
            )
            .order_by(
                models.Schedule.date_range_begin,
                models.Schedule.date_range_end,
                models.Schedule.status,
                models.Schedule.fidelity,
                models.Schedule.created_on.desc(),
                models.Schedule.telescope_id,
            )
        )

        result = await self.db.execute(schedule_query)

        schedules = result.scalars().all()

        return schedules

    async def get_history(
        self, data: schemas.ScheduleRead
    ) -> Sequence[models.Schedule]:
        """
        Retrieve a list of Schedule records for each telescope
        based on the ScheduleRead filter parameters.

        Parameters
        ----------
        data : schemas.ScheduleRead
             class representing Schedule filter parameters

        Returns
        -------
        Sequence[models.Schedule]
            The list of Schedules
        """
        schedule_filter = self._get_schedule_filter(data=data)

        schedule_query = (
            select(models.Schedule)
            .filter(*schedule_filter)
            .order_by(models.Schedule.created_on.desc())
        )

        result = await self.db.execute(schedule_query)

        schedules = result.scalars().all()

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
        existing = await self._exists(schedule.checksum)

        if existing:
            raise DuplicateScheduleException(existing.id)

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
            observation.schedule_id = schedule.id
            observation.created_by_id = created_by_id
            self.db.add(observation)

        await self.db.commit()
        return schedule.id
