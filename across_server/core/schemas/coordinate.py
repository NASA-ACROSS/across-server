from typing import Any

from geoalchemy2 import WKBElement, shape
from pydantic import Field
from shapely import Point

from .base import BaseSchema, PrefixMixin


class Coordinate(BaseSchema, PrefixMixin):
    ra: float | None = Field(ge=0.0, le=360.0)
    dec: float | None = Field(ge=-90.0, le=90.0)
    position: WKBElement | None = Field(
        default=None, json_schema_extra={"flatten_only": True}
    )

    def model_post_init(self, __context: Any) -> None:
        """
        Pydantic post-init hook
        Ensure RA and dec are rounded to an appropriate precision
        """
        if self.ra is not None:
            self.ra = round(self.ra, 5)
        if self.dec is not None:
            self.dec = round(self.dec, 5)
        if self.ra is not None and self.dec is not None:
            self.position = self.create_gis_point()

    def create_gis_point(self) -> WKBElement | None:
        """
        returns the GIS Point object
            ra, dec -> "POINT (ra dec)"
        """
        if self.ra is None or self.dec is None:
            return None
        return shape.from_shape(Point(self.ra, self.dec))
