from __future__ import annotations

import uuid
from datetime import datetime

from ...core.enums import ObservatoryType
from ...core.enums.ephemeris_type import EphemerisType
from ...core.schemas.base import BaseSchema, IDNameSchema
from ...db.models import Observatory as ObservatoryModel


class ObservatoryEphemerisType(BaseSchema):
    """
    A Pydantic model class representing an Observatory Ephemeris Type in the ACROSS SSA system.

    Parameters
    ----------
    id : UUID
        Observatory Ephemeris Type id
    name : str
        Name of the observatory ephemeris type
    """

    ephemeris_type: EphemerisType
    priority: int


class ObservatoryEphemerisParameters(BaseSchema):
    """
    A Pydantic model class representing an Observatory Ephemeris Parameter in the ACROSS SSA system.

    Parameters
    ----------
    id : UUID
        Observatory Ephemeris Parameter id
    name : str
        Name of the observatory ephemeris parameter
    """

    norad_id: int | None = None
    norad_satellite_name: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    height: float | None = None
    naif_id: int | None = None
    spice_kernel_url: str | None = None


class ObservatoryBase(BaseSchema):
    """
    A Pydantic model class representing an Observatory in the ACROSS SSA system.

    Parameters
    ----------
    id : UUID
        Observatory id
    created_on : datetime
        Datetime the observatory record was created
    name : str
        Name of the observatory
    short_name : str
        Short Name of the observatory
    type: ObservatoryType
        Type of observatory
    telescopes: list[IDNameSchema]
        List of telescopes belonging to observatory in id,name format
    """

    id: uuid.UUID
    created_on: datetime
    name: str
    short_name: str
    type: ObservatoryType
    telescopes: list[IDNameSchema] | None = None
    ephemeris_types: list[ObservatoryEphemerisType] | None = None
    ephemeris_parameters: ObservatoryEphemerisParameters | None = None


class Observatory(ObservatoryBase):
    """
    A Pydantic model class representing a created observatory

    Notes
    -----
    Inherits from ObservatoryBase

    Methods
    -------
    from_orm(observatory: ObservatoryModel) -> Observatory
        Static method that instantiates this class from a observatory database record
    """

    @staticmethod
    def from_orm(observatory: ObservatoryModel) -> Observatory:
        """
        Method that converts a models.Observatory record to a schemas.Observatory
        Parameters
        ----------
        observatory: ObservatoryModel
            the models.Observatory record
        Returns
        -------
            schemas.Observatory
        """
        return Observatory(
            id=observatory.id,
            name=observatory.name,
            short_name=observatory.short_name,
            type=observatory.observatory_type,
            telescopes=[
                IDNameSchema(id=telescope.id, name=telescope.name)
                for telescope in observatory.telescopes
            ],
            ephemeris_types=[
                ObservatoryEphemerisType.model_validate(etype)
                for etype in observatory.ephemeris_types
            ],
            ephemeris_parameters=ObservatoryEphemerisParameters.model_validate(
                observatory.ephemeris_parameters
            )
            if observatory.ephemeris_parameters
            else None,
            created_on=observatory.created_on,
        )


class ObservatoryRead(BaseSchema):
    """
    A Pydantic model class representing the query parameters for the Observatory GET methods
    Parameters
    ----------
    name: Optional[str] = None
        Query param to search by name or short name
    telescope_name: Optional[str] = None
        Query param to search by telescopes names or short names
    telescope_id: Optional[UUID] = None
        Query param to search by telescopes id
    type: Optional[ObservatoryType] = None
        Query param to search by type
    created_on: Optional[datetime] = None
        Query param to search by created date after value
    """

    name: str | None = None
    type: ObservatoryType | None = None
    telescope_name: str | None = None
    telescope_id: uuid.UUID | None = None
    created_on: datetime | None = None
