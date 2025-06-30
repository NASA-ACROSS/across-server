from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import model_validator

from ....core.enums import ObservatoryType
from ....core.enums.ephemeris_type import EphemerisType
from ....core.schemas.base import BaseSchema, IDNameSchema
from ....core.schemas.date_range import DateRange


class TLEParameters(BaseSchema):
    norad_id: int
    norad_satellite_name: str


class JPLParameters(BaseSchema):
    naif_id: int


class SPICEParameters(BaseSchema):
    naif_id: int
    spice_kernel_url: str


class GroundParameters(BaseSchema):
    longitude: float
    latitude: float
    height: float


class ObservatoryEphemerisType(BaseSchema):
    ephemeris_type: EphemerisType
    priority: int
    parameters: TLEParameters | JPLParameters | SPICEParameters | GroundParameters


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
    ephemeris_types: list[ObservatoryEphemerisType]
        List of ephemeris types for the observatory
    """

    id: uuid.UUID
    created_on: datetime
    name: str
    short_name: str
    type: ObservatoryType
    telescopes: list[IDNameSchema] | None = None
    ephemeris_types: list[ObservatoryEphemerisType] | None = None
    operational: DateRange

    @model_validator(mode="before")
    def validate_operational_date(cls, values: Any) -> dict:
        """
        Validates the operational_date field to ensure it is not None.
        If it is None, it sets it to an empty DateRange.
        """
        if not isinstance(values, dict):
            values = values.__dict__

        # Fetch operational begin and end dates, if they don't exist, set defaults
        begin = values.get("operational_begin_date", "1900-01-01T00:00:00")
        end = values.get("operational_end_date", None) or "2099-12-31T23:59:59"
        operational_date = DateRange(begin=begin, end=end)
        values["operational"] = operational_date.model_dump()
        values.pop("operational_begin_date", None)
        values.pop("operational_end_date", None)

        return values


class Observatory(ObservatoryBase):
    """
    A Pydantic model class representing a created observatory

    Notes
    -----
    Inherits from ObservatoryBase
    """


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
    ephemeris_type: Optional[list[EphemerisType]] = None
        Query param to search by ephemeris types
    """

    name: str | None = None
    type: ObservatoryType | None = None
    telescope_name: str | None = None
    telescope_id: uuid.UUID | None = None
    ephemeris_type: list[EphemerisType] | None = None
    created_on: datetime | None = None
