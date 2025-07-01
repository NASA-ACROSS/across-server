from datetime import datetime
from uuid import UUID

from across_server.core.schemas.base import BaseSchema


class VisibilityRead(BaseSchema):
    """
    A Pydantic model class representing the query parameters for the Visibility
    GET methods.

    Parameters
    ----------
    ra: float
        Right Ascension in degrees
    dec: float
        Declination in degrees
    date_range_begin: datetime
        Start of the date range for visibility calculation
    date_range_end: datetime
        End of the date range for visibility calculation
    instrument_ids: list[UUID]
        List of instrument IDs to check visibility against
    hi_res: bool
        Whether to use high-resolution visibility calculation (default is True)
    min_visibility_duration: int
        Minimum visibility duration in seconds (default is 0)
    """

    ra: float
    dec: float
    date_range_begin: datetime
    date_range_end: datetime
    instrument_ids: list[UUID]
    hi_res: bool = True
    min_visibility_duration: int = 0
