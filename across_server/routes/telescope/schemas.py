from __future__ import annotations

import uuid
from datetime import datetime

from ...core.schemas.base import BaseSchema, IDNameSchema
from ...db.models import Telescope as TelescopeModel


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
    observatory: IDNameSchema | None = None
    instruments: list[IDNameSchema] | None = None


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

    @staticmethod
    def from_orm(telescope: TelescopeModel) -> Telescope:
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
        return Telescope(
            id=telescope.id,
            name=telescope.name,
            short_name=telescope.short_name,
            observatory=IDNameSchema(
                id=telescope.observatory.id, name=telescope.observatory.name
            ),
            instruments=[
                IDNameSchema(id=instrument.id, name=instrument.name)
                for instrument in telescope.instruments
            ],
            created_on=telescope.created_on,
        )


class TelescopeRead(BaseSchema):
    """
    A Pydantic model class representing the query parameters for the Telescope GET methods
    Parameters
    ----------
    name: Optional[str] = None
        Query param for evaluating Telescope.name.contains(value)
    instrument_id: Optional[UUID] = None
        Query param for evaluating Telescope.instruments.any(id==value)
    instrument_name: Optional[str] = None
        Query param for evaluating Telescope.instruments.any((name or shortname).contains(value))
    created_on: Optional[datetime] = None
        Query param for evaluating Telescope.created_on > value
    """

    name: str | None = None
    instrument_id: uuid.UUID | None = None
    instrument_name: str | None = None
    created_on: datetime | None = None
