from __future__ import annotations

import uuid
from datetime import datetime

from ....core.enums.schedule_status import ScheduleStatus
from ....core.schemas.base import BaseSchema, IDNameSchema
from ....db.models import Instrument as InstrumentModel
from ....db.models import Telescope as TelescopeModel
from ..filter.schemas import Filter
from ..footprint.schemas import Footprint
from ..instrument.schemas import InstrumentBase


class TelescopeBase(BaseSchema):
    """
    A Pydantic model class representing a Telescope in the ACROSS SSA system.

    Parameters
    ----------
    id : UUID
        Telescope id
    created_on : datetime
        Datetime the Telescope record was created
    name : str
        Name of the Telescope
    short_name : str
        Short Name of the Telescope
    instruments: list[IDNameSchema]
        List of Instruments belonging to Telescope in id,name format
    """

    id: uuid.UUID
    created_on: datetime
    name: str
    short_name: str
    schedule_cadences: list[ScheduleCadence] | None = None
    observatory: IDNameSchema | None = None
    instruments: list[TelescopeInstrument] | None = None


class Telescope(TelescopeBase):
    """
    A Pydantic model class representing a created telescope

    Notes
    -----
    Inherits from TelescopeBase

    Methods
    -------
    from_orm(telescope: TelescopeModel) -> Telescope
        Static method that instantiates this class from a telescope database record
    """

    @classmethod
    def from_orm(
        cls,
        obj: TelescopeModel,
        include_footprints: bool = True,
        include_filters: bool = True,
    ) -> Telescope:
        """
        Method that converts a models.Telescope record to a schemas.Telescope
        Parameters
        ----------
        Telescope: TelescopeModel
            the models.Telescope record
        Returns
        -------
            schemas.Telescope
        """
        return cls(
            id=obj.id,
            name=obj.name,
            short_name=obj.short_name,
            observatory=IDNameSchema(
                id=obj.observatory.id,
                name=obj.observatory.name,
                short_name=obj.observatory.short_name,
            ),
            instruments=[
                TelescopeInstrument.from_orm(
                    instrument, include_footprints, include_filters
                )
                for instrument in obj.instruments
            ],
            schedule_cadences=[
                ScheduleCadence.model_validate(schedule_cadence)
                for schedule_cadence in obj.schedule_cadences
            ],
            created_on=obj.created_on,
        )


class TelescopeRead(BaseSchema):
    """
    A Pydantic model class representing the query parameters for the Telescope GET methods
    Parameters
    ----------
    name: Optional[str] = None
        Query param to search by name or short name
    instrument_id: Optional[UUID] = None
        Query param to search by instruments id
    instrument_name: Optional[str] = None
        Query param to search by instruments name or short name
    created_on: Optional[datetime] = None
        Query param to search by created date after value
    """

    name: str | None = None
    instrument_id: uuid.UUID | None = None
    instrument_name: str | None = None
    created_on: datetime | None = None
    include_filters: bool = False
    include_footprints: bool = False


class TelescopeInstrument(InstrumentBase):
    """
    A Pydantic model class representing a created Instrument for the Telescope Endpoint

    Notes
    -----
    Inherits from InstrumentBase

    Methods
    -------
    from_orm(instrument: InstrumentModel, include_footprints: bool, include_filters: bool) -> Instrument
        Static method that instantiates this class from a Instrument database record
    """

    @classmethod
    def from_orm(
        cls,
        obj: InstrumentModel,
        include_footprints: bool = True,
        include_filters: bool = True,
    ) -> TelescopeInstrument:
        """
        Method that converts a models.Instrument record to a schemas.Instrument
        Parameters
        ----------
        Telescope: TelescopeModel
            the models.Telescope record
        Returns
        -------
            schemas.Telescope
        """
        footprints = [Footprint.from_orm(footprint) for footprint in obj.footprints]
        filters = [Filter.model_validate(filter) for filter in obj.filters]

        return cls(
            id=obj.id,
            name=obj.name,
            short_name=obj.short_name,
            telescope=IDNameSchema(
                id=obj.telescope.id,
                name=obj.telescope.name,
                short_name=obj.telescope.short_name,
            ),
            footprints=[footprint.polygon for footprint in footprints]
            if include_footprints
            else [],
            filters=filters if include_filters else [],
            created_on=obj.created_on,
        )


class ScheduleCadence(BaseSchema):
    id: uuid.UUID
    telescope_id: uuid.UUID
    cron: str | None
    schedule_status: ScheduleStatus
