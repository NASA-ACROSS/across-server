from pydantic import BaseModel, Field
from typing import Any
from geoalchemy2 import WKBElement, shape
from shapely import Point
from .base import PrefixMixin

class Coordinate(BaseModel, PrefixMixin):
    ra: float | None = Field(ge=0.0, le=360.0)
    dec: float | None = Field(ge=-90.0, le=90.0)

    def model_post_init(self, __context: Any) -> None:
         """
         Pydantic post-init hook
         Ensure RA and dec are rounded to an appropriate precision
         """
         self.ra = round(self.ra, 5)
         self.dec = round(self.dec, 5)

    def create_gis_point(self) -> WKBElement | None:
        """
        returns the GIS Point object
            ra, dec -> "POINT (ra dec)"
        """
        if self.ra is None or self.dec is None:
            return None
        return shape.from_shape(Point(self.ra, self.dec))