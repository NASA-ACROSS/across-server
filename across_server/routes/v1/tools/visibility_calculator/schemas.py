from datetime import datetime
from uuid import UUID

from across.tools.core.enums import ConstraintType

from .....core.schemas.base import BaseSchema


class ConstrainedDate(BaseSchema):
    """
    Represents a constrained date.
    """

    datetime: datetime
    constraint: ConstraintType
    observatory_id: UUID


class Window(BaseSchema):
    """Visibility Window"""

    begin: ConstrainedDate
    end: ConstrainedDate


class ConstraintReason(BaseSchema):
    """
    Represents the reasons for constraints.
    """

    start_reason: str
    end_reason: str


class VisibilityWindow(BaseSchema):
    """Visibility Window"""

    window: Window
    max_visibility_duration: int
    constraint_reason: ConstraintReason


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
    hi_res: bool
        Whether to use high-resolution visibility calculation (default is True)
    min_visibility_duration: int
        Minimum visibility duration in seconds (default is 0)
    """

    ra: float
    dec: float
    date_range_begin: datetime
    date_range_end: datetime
    hi_res: bool = True
    min_visibility_duration: int = 0


class VisibilityResult(VisibilityRead):
    """
    A Pydantic model class representing the visibility calculation parameters.

    Inherits from VisibilityRead and adds no additional fields.
    This class is used for visibility calculations in the ACROSS SSA system.
    """

    instrument_id: UUID
    visibility_windows: list[VisibilityWindow]


class JointVisibilityRead(VisibilityRead):
    """
    A Pydantic model class representing the query parameters for the Joint
    Visibility GET methods.

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

    instrument_ids: list[UUID]
