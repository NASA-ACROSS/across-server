from __future__ import annotations

from typing import Any

from geoalchemy2 import WKBElement, shape
from pydantic import field_validator

from ...core.schemas.base import BaseSchema


class Point(BaseSchema):
    """
    A Pydantic model class representing a 2D Point.

    Parameters
    ----------
    x: float
    y: float
    """

    x: float
    y: float


class FootprintBase(BaseSchema):
    """
    A Pydantic model class representing a Footprint in the ACROSS SSA system.

    Parameters
    ----------
    polygon: list[Point]
    """

    polygon: list[Point]


class Footprint(FootprintBase):
    """
    A Pydantic model class representing a created Footprint

    Notes
    -----
    Inherits from FootprintBase
    """

    @field_validator("polygon", mode="before")
    @classmethod
    def validate_polygon(cls, value: Any) -> list[Point]:
        """
        Validate the polygon field to ensure it is a list of Point objects. If
        it is a WKBElement, convert it to a list of Point objects.
        """
        if isinstance(value, WKBElement):
            # Convert WKBElement to a list of Point objects
            polygon = shape.to_shape(value)
            return [Point(x=point[0], y=point[1]) for point in polygon.exterior.coords]
        return value
