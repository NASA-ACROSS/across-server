from datetime import datetime
from typing import Any
from uuid import UUID

from across.tools.core.enums import ConstraintType
from pydantic import Field, model_validator

from .....core.schemas.base import BaseSchema


def convert_astropy_time_to_datetime(time_obj: Any) -> datetime:
    """
    Convert an astropy.time.Time object to a datetime.datetime object.

    Parameters
    ----------
    time_obj : Any
        An astropy.time.Time object or datetime object

    Returns
    -------
    datetime
        A datetime.datetime object
    """
    # Check if the object is already a datetime
    if isinstance(time_obj, datetime):
        return time_obj

    # Check if it's an astropy Time object by checking for the datetime attribute
    if hasattr(time_obj, "datetime"):
        return time_obj.datetime

    # If it's neither, try to convert it to datetime
    return datetime.fromisoformat(str(time_obj))


class ConstrainedDate(BaseSchema):
    """
    Represents a constrained date.
    """

    datetime: datetime
    constraint: ConstraintType
    observatory_id: UUID

    @model_validator(mode="before")
    @classmethod
    def convert_astropy_times(cls, data: Any) -> Any:
        """Convert astropy.time.Time objects to datetime.datetime objects."""
        if isinstance(data, dict) and "datetime" in data:
            data["datetime"] = convert_astropy_time_to_datetime(data["datetime"])
        return data


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
    """Represents a Visibility Window with max visibility duration and
    information about the start and end constraints reason."""

    window: Window
    max_visibility_duration: int
    constraint_reason: ConstraintReason


class VisibilityReadParams(BaseSchema):
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

    ra: float = Field(ge=0.0, le=360.0)
    dec: float = Field(ge=-90.0, le=90.0)
    date_range_begin: datetime
    date_range_end: datetime
    hi_res: bool = True
    min_visibility_duration: int = 0


class VisibilityResult(BaseSchema):
    """
    A Pydantic model class representing the visibility calculation parameters.

    This class is used for visibility calculations in the ACROSS SSA system.
    """

    instrument_id: UUID
    visibility_windows: list[VisibilityWindow]


class JointVisibilityReadParams(VisibilityReadParams):
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


class JointVisibilityResult(BaseSchema):
    """
    A Pydantic model class representing the joint visibility calculation
    parameters.

    This class is used for joint visibility calculations in the ACROSS SSA
    system.

    Parameters
    ----------
    instrument_ids: list[UUID]
        List of instrument IDs to check visibility against
    visibility_windows: list[VisibilityWindow]
        List of joint visibility windows for all the instruments
    observatory_visibility_windows: dict[UUID, list[VisibilityWindow]]
        Dictionary mapping instrument IDs to their respective visibility windows
    """

    instrument_ids: list[UUID]
    visibility_windows: list[VisibilityWindow]
    observatory_visibility_windows: dict[UUID, list[VisibilityWindow]]
