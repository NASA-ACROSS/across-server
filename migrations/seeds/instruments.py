import uuid

from across.tools.core.enums import ConstraintType
from across.tools.visibility.constraints import (
    EarthLimbConstraint,
    MoonAngleConstraint,
    SunAngleConstraint,
)

from across_server.core.enums import InstrumentFOV, InstrumentType, visibility_type
from across_server.db.models import Constraint, Instrument

from .telescopes import sandy_smaller_telescope, sandy_telescope

sun45constraint = Constraint(
    id=uuid.UUID("d530a37d-0fc1-4ea3-8bae-1ab4940308b5"),
    constraint_type=ConstraintType.SUN,
    constraint_parameters=SunAngleConstraint(min_angle=45).model_dump(),
)
earth10constraint = Constraint(
    id=uuid.UUID("65b93846-df6e-4d64-8150-917d4782cfa0"),
    constraint_type=ConstraintType.EARTH,
    constraint_parameters=EarthLimbConstraint(min_angle=10).model_dump(),
)
moon20constraint = Constraint(
    id=uuid.UUID("3390c3f9-62ea-4ee1-a94e-cc5178a7a383"),
    constraint_type=ConstraintType.MOON,
    constraint_parameters=MoonAngleConstraint(min_angle=20).model_dump(),
)
earth0constraint = Constraint(
    id=uuid.UUID("5a2bcefc-f08e-4d4f-a2a9-1dd526638884"),
    constraint_type=ConstraintType.EARTH,
    constraint_parameters=EarthLimbConstraint(min_angle=0).model_dump(),
)
earth20constraint = Constraint(
    id=uuid.UUID("70d3f9cb-2550-4064-9808-36a75f9cae87"),
    constraint_type=ConstraintType.EARTH,
    constraint_parameters=EarthLimbConstraint(min_angle=20).model_dump(),
)

sandy_instrument_calorimeter = Instrument(
    id=uuid.UUID("a4cf7691-8d3c-4fea-899c-9bcc33d23a5e"),
    name="SANDY'S X-RAY",
    short_name="SANDY_XRAY",
    telescope=sandy_telescope,
    type=InstrumentType.CALORIMETER.value,
    field_of_view=InstrumentFOV.POLYGON.value,
    is_operational=True,
    visibility_type=visibility_type.VisibilityType.EPHEMERIS,
    constraints=[
        sun45constraint,
        moon20constraint,
        earth10constraint,
    ],
)

sandy_all_sky_instrument = Instrument(
    id=uuid.UUID("f3a2b0c1-4d5e-4f6a-8b7c-8d9e0f1a2b3c"),
    name="SANDY'S ALL-SKY",
    short_name="SANDALLSKY",
    telescope=sandy_telescope,
    type=InstrumentType.PHOTOMETRIC.value,
    field_of_view=InstrumentFOV.ALL_SKY.value,
    is_operational=True,
    visibility_type=visibility_type.VisibilityType.EPHEMERIS,
    constraints=[earth0constraint],
)

sandy_optical_instrument = Instrument(
    id=uuid.UUID("c31dc89c-d2f0-4335-9d6f-e42e7a7d86af"),
    name="SANDY'S OPTICAL",
    short_name="SANDOPT",
    telescope=sandy_smaller_telescope,
    type=InstrumentType.PHOTOMETRIC.value,
    field_of_view=InstrumentFOV.POLYGON.value,
    is_operational=True,
    visibility_type=visibility_type.VisibilityType.EPHEMERIS,
    constraints=[sun45constraint, moon20constraint, earth20constraint],
)

instruments = [
    sandy_instrument_calorimeter,
    sandy_all_sky_instrument,
    sandy_optical_instrument,
]
