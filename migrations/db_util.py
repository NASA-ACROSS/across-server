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


def arcsec_to_deg(arcsec: float) -> float:
    """Convert arcsecond to degrees."""
    return arcsec / 3600.0


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


def parallelogram_footprint(
    length_deg: float, width_deg: float, length_rotation: float, width_rotation: float
) -> list[list[dict]]:
    """
    Create a parallelogram footprint with a given length and width (in degrees),
    and rotation angles of the length and width (in degrees).
    IMPORTANT: Because of how coordinate systems for detectors are typically defined,
    both the rotation angles are defined with respect to the y-axis
    (absent any roll angle, this axis points straight North).
    Therefore the rotation matrix looks slightly different than how it's usually defined.
    For more information, see the explanation at the bottom of this page:
    https://www.stsci.edu/hst/instrumentation/focus-and-pointing/fov-geometry
    """
    half_length = length_deg / 2.0
    half_width = width_deg / 2.0

    length_rotation = np.deg2rad(length_rotation)
    width_rotation = np.deg2rad(width_rotation)

    unrotated_coords = np.asarray(
        [
            [-half_length, -half_width],
            [half_length, -half_width],
            [half_length, half_width],
            [-half_length, half_width],
            [-half_length, -half_width],
        ]
    )

    rotation_matrix = np.asarray(
        [
            [np.sin(length_rotation), np.sin(width_rotation)],
            [np.cos(length_rotation), np.cos(width_rotation)],
        ]
    )

    rotated_coords = unrotated_coords @ rotation_matrix

    return [[{"x": coord[0], "y": coord[1]} for coord in rotated_coords.astype(object)]]
