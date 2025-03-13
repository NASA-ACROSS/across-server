from __future__ import annotations

import uuid
from datetime import datetime

from ...core.schemas.base import BaseSchema, IDNameSchema
from ...db.models import Instrument as InstrumentModel
from ..footprint.schemas import Footprint, Point


class InstrumentBase(BaseSchema):
    """
    A Pydantic model class representing an Instrument in the ACROSS SSA system.

    Parameters
    ----------
    id : UUID
        Instrument id
    created_on : datetime
        Datetime the Instrument record was created
    name : str
        Name of the Instrument
    short_name : str
        Short Name of the Instrument
    telescope: IDNameSchema
        the Telescope record the instrument belongs to in id,name format
    footprints: list[list[Point]]
        List of imaging footprints belonging to instrument
    """

    id: uuid.UUID
    created_on: datetime
    name: str
    short_name: str
    telescope: IDNameSchema | None = None
    footprints: list[list[Point]] | None = None


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
        footprints = [
            Footprint.from_orm(footprint) for footprint in instrument.footprints
        ]

        return Instrument(
            id=instrument.id,
            name=instrument.name,
            short_name=instrument.short_name,
            telescope=IDNameSchema(
                id=instrument.telescope.id, name=instrument.telescope.name
            ),
            footprints=[footprint.polygon for footprint in footprints],
            created_on=instrument.created_on,
        )


class InstrumentRead(BaseSchema):
    """
    A Pydantic model class representing the query parameters for the Instrument GET methods
    Parameters
    ----------
    name: Optional[str] = None
        Query Param for searching by name or short name
    telescope_id: Optional[UUID] = None
        Query param for searching telescope id
    telescope_name: Optional[str] = None
        Query param for searching telescope name or short name
    created_on: Optional[datetime] = None
        Query param to search by created date after value
    """

    name: str | None = None
    telescope_id: uuid.UUID | None = None
    telescope_name: str | None = None
    created_on: datetime | None = None
