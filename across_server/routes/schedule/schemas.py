from __future__ import annotations

import uuid
from datetime import datetime

from ...core.enums import ScheduleFidelity, ScheduleStatus
from ...core.schemas import DateRange, PaginationParams
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
    checksum: str = ""

    @classmethod
    def from_orm(cls, obj: ScheduleModel) -> Schedule:
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
        return cls(
            id=obj.id,
            telescope_id=obj.telescope_id,
            date_range=DateRange(begin=obj.date_range_begin, end=obj.date_range_end),
            status=ScheduleStatus(obj.status),
            name=obj.name,
            external_id=obj.external_id,
            fidelity=ScheduleFidelity(obj.fidelity),
            created_on=obj.created_on,
            created_by_id=obj.created_by_id,
            observations=[
                Observation.from_orm(observation) for observation in obj.observations
            ],
            checksum=obj.checksum,
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


class ScheduleRead(PaginationParams):
    """
    A Pydantic model class representing the query parameters for the schedule GET methods

    Parameters
    ----------
    date_range_begin: datetime, optional
        Query Param for evaluating Schedule.date_range_begin >= value
    date_range_end: datetime, optional
        Query Param for evaluating Schedule.date_range_end <= value
    status: ScheduleStatus, optional
        Query Param for evaluating Schedule.status == value
    external_id: str, optional
        Query Param for evaluating Schedule.external_id.contains(value)
    fidelity: ScheduleFidelity, optional
        Query Param for evaluating Schedule.fidelity == value
    created_on: datetime, optional
        Query Param for evaluating Schedule.created_on > value
    observatory_ids: list[uuid.UUID], default = []
        Query Param for evaluating Schedule.Telescope.Observatory.id in value
    observatory_names: list[str], default = []
        Query Param for evaluating Schedule.Telescope.Observatory.name in value
    observatory_short_names: list[str], optional
        Query Param for evaluating Schedule.Telescope.Observatory.short_name in value
    telescope_ids: list[uuid.UUID], optional
        Query Param for evaluating Schedule.Telescope.id in value
    telescope_names: list[str], optional
        Query Param for evaluating Schedule.Telescope.name in value
    telescope_short_names: list[str], optional
        Query Param for evaluating Schedule.Telescope.short_name in value
    name: str, optional
        Query Param for evaluating Schedule.name.contains(value)

    """

    date_range_begin: datetime | None = None
    date_range_end: datetime | None = None
    status: ScheduleStatus | None = None
    external_id: str | None = None
    fidelity: ScheduleFidelity | None = None
    created_on: datetime | None = None
    observatory_ids: list[uuid.UUID] = []
    observatory_names: list[str] = []
    telescope_ids: list[uuid.UUID] = []
    telescope_names: list[str] = []
    name: str | None = None


class SchedulePaginate(BaseSchema):
    """
    A Pydantic model class representing a returned, paginated list of Schedules

    Parameters
    ----------
    number: int
        the number of entries returned by the query
    page: int
        the page number
    page_limit: int
        the maximum number of entries per page
    schedules: list[Schedule]
        the queried Schedule objects
    """

    number: int | None
    page: int | None
    page_limit: int | None
    schedules: list[Schedule]
