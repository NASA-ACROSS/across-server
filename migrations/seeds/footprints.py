import uuid

from geoalchemy2 import WKTElement
from shapely.geometry import Polygon

from across_server.db.models import Footprint

from .instruments import sandy_instrument_calorimeter, sandy_optical_instrument


# Function to create a WKT polygon from a Shapely Polygon
def create_polygon(vertices: list[tuple]) -> WKTElement:
    # Create a Shapely Polygon
    shapely_polygon = Polygon(vertices)

    # Convert to WKT
    wkt_polygon = WKTElement(
        shapely_polygon.wkt,
        srid=4326,  # Specify the appropriate SRID
    )
    return wkt_polygon


vertices = [(0.5, 0.5), (0.5, -0.5), (-0.5, -0.5), (-0.5, 0.5), (0.5, 0.5)]

simple_optical_footprint = Footprint(
    id=uuid.UUID("e0214a61-7c90-497e-aa69-e1cf58e8c81d"),
    instrument=sandy_optical_instrument,
    polygon=create_polygon(vertices),
)
simple_xray_footprint = Footprint(
    id=uuid.UUID("843a2d54-a503-4c4a-acb8-f03fae3cf2f0"),
    instrument=sandy_instrument_calorimeter,
    polygon=create_polygon(vertices),
)

footprints = [simple_optical_footprint, simple_xray_footprint]
