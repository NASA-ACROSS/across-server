import uuid

from across_server.core.enums import EphemerisType, ObservatoryType
from across_server.db.models import (
    EarthLocationParameters,
    JPLEphemerisParameters,
    Observatory,
    ObservatoryEphemerisType,
    SpiceKernelParameters,
    TLEParameters,
)

from .groups import treedome_space_group

space_based: str = ObservatoryType.SPACE_BASED.value
ground_based: str = ObservatoryType.GROUND_BASED.value

sandy_observatory = Observatory(
    id=uuid.uuid4(),
    type=space_based,
    name="SANDY'S SPACE STATION",
    short_name="SANDY",
    group=treedome_space_group,
    ephemeris_types=[
        ObservatoryEphemerisType(ephemeris_type=EphemerisType.TLE, priority=1),
        ObservatoryEphemerisType(ephemeris_type=EphemerisType.JPL, priority=2),
    ],
)

# Set up Ephemeris Parameter entries for each observatory
tle_parameters: list[TLEParameters] = [
    TLEParameters(
        id=uuid.uuid4(),
        observatory_id=sandy_observatory.id,
        norad_id=123456,
        norad_satellite_name="SANDY",
    )
]
jpl_parameters: list[JPLEphemerisParameters] = [
    JPLEphemerisParameters(
        id=uuid.uuid4(),
        observatory_id=sandy_observatory.id,
        naif_id=-123456,
    )
]
spice_kernel_parameters: list[SpiceKernelParameters] = []
earth_location_parameters: list[EarthLocationParameters] = []

observatories = [sandy_observatory]
