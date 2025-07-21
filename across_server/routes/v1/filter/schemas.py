from __future__ import annotations

import uuid
from datetime import datetime

from ....core.schemas.base import BaseSchema


class FilterBase(BaseSchema):
    """
    A Pydantic model class representing an instrument Filter in the ACROSS SSA system.

    Parameters
    ----------
    id : UUID
        Filter id
    created_on : datetime
        Datetime the Filter record was created
    name : str
        Name of the Filter
    """

    id: uuid.UUID
    created_on: datetime
    name: str
    peak_wavelength: float | None
    min_wavelength: float
    max_wavelength: float
    is_operational: bool
    sensitivity_depth_unit: float | None
    sensitivity_depth: float | None
    sensitivity_time_seconds: float | None
    reference_url: str | None
    instrument_id: uuid.UUID


class Filter(FilterBase):
    """
    A Pydantic model class representing a created Filter

    Notes
    -----
    Inherits from FilterBase
    """


class FilterRead(BaseSchema):
    """
    A Pydantic model class representing the query parameters for the Filters GET methods
    Parameters
    ----------
    name: Optional[str] = None
        Query Param for searching by name or short name
    instrument_id: Optional[UUID] = None
        Query param for searching instrument id
    instrument_name: Optional[str] = None
        Query param for searching instrument name or short name
    covers_wavelength: Optional[float] = None
        Query param for finding a filter that covers a wavelength Angstrom
    """

    name: str | None = None
    instrument_id: uuid.UUID | None = None
    instrument_name: str | None = None
    covers_wavelength: float | None = None
