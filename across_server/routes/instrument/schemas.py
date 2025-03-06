from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from ...core.schemas.base import BaseSchema
from ...db.models import Instrument as InstrumentModel
from ..footprint.schemas import Footprint


class InstrumentBase(BaseSchema):
    """
    A Pydantic model class representing an Instrument in the ACROSS SSA system.

    Parameters
    ----------
    id : UUID
        Instrument id
    created_on : datetime
        Datetime the Instrument was created in our database
    name : str
        Name of the Instrument
    short_name : str
        Short Name of the Instrument
    footprints: list[Footprint]
        List of imaging footprint belonging to instrument
    """

    id: uuid.UUID
    created_on: datetime
    name: str
    short_name: str
    footprints: list[Footprint]


class Instrument(InstrumentBase):
    """
    A Pydantic model class representing a created Instrument

    Notes
    -----
    Inherits from InstrumentBase

    Methods
    -------
    from_orm(instrument: InstrumentModel) -> Instrument
        Static method that instantiates this class from a Instrument database record
    """

    @staticmethod
    def from_orm(instrument: InstrumentModel) -> Instrument:
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
        return Instrument(
            id=instrument.id,
            name=instrument.name,
            short_name=instrument.short_name,
            footprints=[
                Footprint.from_orm(footprint) for footprint in instrument.footprints
            ],
            created_on=instrument.created_on,
        )


class InstrumentRead(BaseSchema):
    """
    A Pydantic model class representing the query parameters for the Instrument GET methods
    Parameters
    ----------
    name: Optional[str] = None
        Query Param for evaluating Instrument.name.contains(value)
    short_name: Optional[str] = None
        Query Param for evaluating Instrument.short_name.contains(value)
    created_on: Optional[datetime] = None
        Query Param for evaluating Instrument.created_on > value
    """

    name: Optional[str] = None
    short_name: Optional[str] = None
    created_on: Optional[datetime] = None
