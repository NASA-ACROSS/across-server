from __future__ import annotations

from geoalchemy2 import WKTElement, shape
from shapely import Polygon

from ....core.schemas.base import BaseSchema
from ....db.models import Footprint as FootprintModel


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

    def polygon_to_wkt(self) -> WKTElement:
        """
        Method that converts the polygon of this footprint to a WKT Element

        Returns
        -------
            WKTElement: WKT representation of the polygon
        """
        points = [(point.x, point.y) for point in self.polygon]

        shapely_polygon = Polygon(points)

        wkt_polygon = WKTElement(
            shapely_polygon.wkt,
            srid=4326,  # Specify the appropriate SRID
        )
        return wkt_polygon


class Footprint(FootprintBase):
    """
    A Pydantic model class representing a created Footprint

    Notes
    -----
    Inherits from FootprintBase

    Methods
    -------
    from_orm(obj: FootprintModel) -> Footprint
        Static method that instantiates this class from a footprint database record
    """

    @classmethod
    def from_orm(cls, obj: FootprintModel) -> Footprint:
        """
        Method that converts a models.Footprint record to a schemas.Footprint

        Parameters
        ----------
        obj: FootprintModel
            the models.Footprint record

        Returns
        -------
            schemas.Footprint
        """

        poly = shape.to_shape(obj.polygon)
        x, y = poly.exterior.coords.xy  # type: ignore
        polygon = [Point(x=x[i], y=y[i]) for i in range(len(x))]

        return cls(polygon=polygon)
