import uuid

from across_server.core.enums import EphemerisType, ObservatoryType
from across_server.db.models import (
    Observatory,
    ObservatoryEphemerisParameters,
    ObservatoryEphemerisType,
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
        ObservatoryEphemerisType(ephemeris_type=EphemerisType.TLE, priority=1)
    ],
    ephemeris_parameters=ObservatoryEphemerisParameters(
        norad_satellite_name="SANDY",
        norad_id=12345,
    ),
)

observatories = [sandy_observatory]
