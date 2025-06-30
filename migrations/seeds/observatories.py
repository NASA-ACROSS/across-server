import uuid
from datetime import datetime

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
    id=uuid.UUID("c847eaa6-4ce5-45a1-b06a-dd701d4f1a6e"),
    type=space_based,
    name="SANDY'S SPACE STATION",
    short_name="SANDY",
    group=treedome_space_group,
    is_operational=True,
    operational_begin_date=datetime(1999, 5, 2, 0, 30, 0),
    operational_end_date=None,
)

ephemeris_types = [
    ObservatoryEphemerisType(
        id=uuid.UUID("c7e7761d-be73-4fbc-a1d4-f53af899b1d5"),
        observatory_id=sandy_observatory.id,
        ephemeris_type=EphemerisType.TLE.value,
        priority=1,
    ),
    ObservatoryEphemerisType(
        id=uuid.UUID("9da83669-b8ed-4718-9f22-f09d172fd361"),
        observatory_id=sandy_observatory.id,
        ephemeris_type=EphemerisType.JPL.value,
        priority=2,
    ),
]

# Set up Ephemeris Parameter entries for each observatory
tle_parameters: list[TLEParameters] = [
    TLEParameters(
        id=uuid.UUID("6c817107-1aed-42a3-9f0f-90a1e17c395a"),
        observatory_id=sandy_observatory.id,
        norad_id=123456,
        norad_satellite_name="SANDY",
    )
]
jpl_parameters: list[JPLEphemerisParameters] = [
    JPLEphemerisParameters(
        id=uuid.UUID("f475094e-dde5-44ad-83d5-7f4e4bcb0712"),
        observatory_id=sandy_observatory.id,
        naif_id=-123456,
    )
]
spice_kernel_parameters: list[SpiceKernelParameters] = []
earth_location_parameters: list[EarthLocationParameters] = []

observatories = [sandy_observatory]
