from __future__ import annotations

import uuid
from datetime import datetime

from ...core.enums import ScheduleFidelity, ScheduleStatus
from ...core.schemas import DateRange
from ...core.schemas.base import BaseSchema
from ...db.models import Schedule as ScheduleModel
from ..observation.schemas import Observation, ObservationCreate


class ScheduleBase(BaseSchema):
    """
    A Pydantic model class representing the base astronomical observing schedule for a telescope.

    Parameters
    ----------
    telescope_id : UUID
        Record identifier for the schedules telescope
    name : str
        Name of the schedule
    date_range : DateRange
        Date range of the schedule. Must be a DateRange Object that has a
        begin (datetime) and end (datetime)
    status : ScheduleStatus
        Status of the schedule. Must be enum<planned, scheduled, performed>
    external_id : Optional[str]
        Optional external identifier for the schedule used by the submitting observatory.
    fidelity : Optional[ScheduleFidelity]
        Optional fidelity for the schedule. Must be enum<high, low>

    """

    telescope_id: uuid.UUID
    name: str
    date_range: DateRange
    status: ScheduleStatus
    external_id: str | None = None
    fidelity: ScheduleFidelity | None = None


class Schedule(ScheduleBase):
    """
    A Pydantic model class representing a created observing schedule for a telescope.

    Parameters
    ----------
    id : UUID
        Schedule id
    observations : list[schemas.Observation]
        A list of observations for the schedule
    created_on : datetime
        Datetime the schedule was created
    created_by_id : UUID
        AuthUser id
    checksum : str
        Unique string representation of the schedule and observations

    Notes
    -----
    Inherits from ScheduleBase

    Methods
    -------
    create_checksum(schedule: ScheduleModel) -> str
        Static method that creates the checksum from the schedule metadata and observation list metadata
    from_orm(schedule: ScheduleModel) -> Schedule
        Static method that instantiates this class from a schedule database record
    """

    id: uuid.UUID
    observations: list[Observation] | None
    created_on: datetime
    created_by_id: uuid.UUID | None
    checksum: str | None = ""

    @staticmethod
    def from_orm(schedule: ScheduleModel) -> Schedule:
        """
        Method that converts a models.Schedule record to a schemas.Schedule

        Parameters
        ----------
        schedule: ScheduleModel
            the models.Schedule record

        Returns
        -------
            schemas.Schedule
        """
        return Schedule(
            id=schedule.id,
            telescope_id=schedule.telescope_id,
            date_range=DateRange(
                begin=schedule.date_range_begin, end=schedule.date_range_end
            ),
            status=ScheduleStatus(schedule.status),
            name=schedule.name,
            external_id=schedule.external_id,
            fidelity=ScheduleFidelity(schedule.fidelity),
            created_on=schedule.created_on,
            created_by_id=schedule.created_by_id,
            observations=[
                Observation.from_orm(observation)
                for observation in schedule.observations
            ],
            checksum=schedule.checksum,
        )


class ScheduleCreate(ScheduleBase):
    """
    A Pydantic model class representing the a schedule to be created in the database

    Parameters
    ----------
    observations : list[schemas.Observation]
        A list of observations for the schedule

    Notes
    ---------
    Inherits from ScheduleBase

    Methods
    to_orm(self, created_by_id: UUID) -> ScheduleModel
        Method that creates the ORM record for a schedule to be serialized into the database.
        This method does not instantiate the list of observations, the observation schema requires
        a schedule ID so it is instantiated after the model id is flushed within the service.
    """

    observations: list[ObservationCreate]

    def to_orm(self, created_by_id: uuid.UUID) -> ScheduleModel:
        return ScheduleModel(
            telescope_id=self.telescope_id,
            name=self.name,
            status=self.status.value,
            date_range_begin=self.date_range.begin,
            date_range_end=self.date_range.end,
            external_id=self.external_id,
            fidelity=self.fidelity.value
            if self.fidelity
            else ScheduleFidelity.HIGH.value,
            created_by_id=created_by_id,
            checksum=self.generate_checksum(),
        )


class ScheduleRead(BaseSchema):
    """
    A Pydantic model class representing the query parameters for the schedule GET methods

    Parameters
    ----------
    date_range_begin: Optional[datetime] = None
        Query Param for evaluating Schedule.date_range_begin >= value
    date_range_end: Optional[datetime] = None
        Query Param for evaluating Schedule.date_range_end <= value
    status: Optional[ScheduleStatus] = None
        Query Param for evaluating Schedule.status == value
    external_id: Optional[str] = None
        Query Param for evaluating Schedule.external_id.contains(value)
    fidelity: Optional[ScheduleFidelity] = None
        Query Param for evaluating Schedule.fidelity == value
    created_on: Optional[datetime] = None
        Query Param for evaluating Schedule.created_on > value
    observatory_ids: Optional[list[uuid.UUID]] = []
        Query Param for evaluating Schedule.Telescope.Observatory.id in value
    observatory_names: Optional[list[str]] = []
        Query Param for evaluating Schedule.Telescope.Observatory.name in value
    observatory_short_names: Optional[list[str]] = []
        Query Param for evaluating Schedule.Telescope.Observatory.short_name in value
    telescope_ids: Optional[list[uuid.UUID]] = []
        Query Param for evaluating Schedule.Telescope.id in value
    telescope_names: Optional[list[str]] = []
        Query Param for evaluating Schedule.Telescope.name in value
    telescope_short_names: Optional[list[str]] = []
        Query Param for evaluating Schedule.Telescope.short_name in value
    name: Optional[str] = None
        Query Param for evaluating Schedule.name.contains(value)

    """

    date_range_begin: datetime | None = None
    date_range_end: datetime | None = None
    status: ScheduleStatus | None = None
    external_id: str | None = None
    fidelity: ScheduleFidelity | None = None
    created_on: datetime | None = None
    observatory_ids: list[uuid.UUID] | None = []
    observatory_names: list[str] | None = []
    telescope_ids: list[uuid.UUID] | None = []
    telescope_names: list[str] | None = []
    name: str | None = None
