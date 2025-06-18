import numpy as np
from geoalchemy2 import WKBElement, shape
from pydantic import BaseModel
from shapely import Polygon


class ACROSSFootprintPoint(BaseModel):
    x: float  # ra
    y: float  # dec


# this is sort of duplicated in seeds/footprints.py, the one in the seed should be replaced with this.
def create_geography(polygon: list[ACROSSFootprintPoint]) -> WKBElement:
    return shape.from_shape(Polygon([[point.x, point.y] for point in polygon]))


def arcmin_to_deg(arcmin: float) -> float:
    """Convert arcminute to degrees."""
    return arcmin / 60.0


def circular_footprint(radius_deg: float) -> list[list[dict]]:
    """Create a circular footprint with the given radius in degrees."""
    thetas = np.linspace(0, -2 * np.pi, 200)
    ras = radius_deg * np.cos(thetas)
    decs = radius_deg * np.sin(thetas)
    return [[{"x": ras[i], "y": decs[i]} for i in range(len((ras)))]]


def square_footprint(length_deg: float) -> list[list[dict]]:
    """Create a square footprint with the given length in degrees."""
    half_length = length_deg / 2.0
    return [
        [
            {"x": -half_length, "y": -half_length},
            {"x": half_length, "y": -half_length},
            {"x": half_length, "y": half_length},
            {"x": -half_length, "y": half_length},
            {"x": -half_length, "y": -half_length},
        ]
    ]
