from geoalchemy2 import WKBElement, shape
from pydantic import BaseModel
from shapely import Polygon


class ACROSSFootprintPoint(BaseModel):
    x: float  # ra
    y: float  # dec


# this is sort of duplicated in seeds/footprints.py, the one in the seed should be replaced with this.
def create_geography(polygon: list[ACROSSFootprintPoint]) -> WKBElement:
    return shape.from_shape(Polygon([[point.x, point.y] for point in polygon]))
