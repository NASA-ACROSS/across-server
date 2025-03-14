from geoalchemy2 import WKTElement
from shapely.geometry import Polygon

from across_server.db.models import Footprint

from .instruments import sandy_instrument


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

simple_footprint = Footprint(
    instrument=sandy_instrument, polygon=create_polygon(vertices)
)

footprints = [simple_footprint]
