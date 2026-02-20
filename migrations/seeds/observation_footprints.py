import uuid

from across.tools import Coordinate
from across.tools import Polygon as ToolsPolygon
from across.tools.footprint import Footprint as ToolsFootprint
from geoalchemy2 import WKTElement, shape
from shapely.geometry import Polygon

from across_server.db.models import Footprint, ObservationFootprint

from .footprints import simple_xray_footprint
from .observations import sandy_observation


def tools_footprint_to_wkt_polygon(detector: ToolsPolygon) -> WKTElement:
    # Assuming the footprint has only one detector for simplicity
    coordinates = [(coord.ra, coord.dec) for coord in detector.coordinates]
    shapely_polygon = Polygon(coordinates)

    wkt_polygon = WKTElement(
        shapely_polygon.wkt,
        srid=4326,  # Specify the appropriate SRID
    )
    return wkt_polygon


def footprint_to_tools_footprint(footprints: list[Footprint]) -> ToolsFootprint:
    detectors = []
    for obj in footprints:
        poly = shape.to_shape(obj.polygon)
        x, y = poly.exterior.coords.xy  # type: ignore
        coordinates = [Coordinate(ra=x[i], dec=y[i]) for i in range(len(x))]
        detectors.append(ToolsPolygon(coordinates=coordinates))
    return ToolsFootprint(detectors=detectors)


projected_footprint = footprint_to_tools_footprint([simple_xray_footprint]).project(
    coordinate=Coordinate(
        ra=sandy_observation.pointing_ra or 0.0,
        dec=sandy_observation.pointing_dec or 0.0,
    ),
    roll_angle=0.0,
)

observation_footprints: list[ObservationFootprint] = []

for detector in projected_footprint.detectors:
    observation_footprints.append(
        ObservationFootprint(
            id=uuid.uuid4(),
            observation_id=sandy_observation.id,
            polygon=tools_footprint_to_wkt_polygon(detector),
        )
    )
