import uuid

from across_server.core.enums import InstrumentFOV, InstrumentType, instrument_type
from across_server.db.models import Instrument

from .telescopes import sandy_smaller_telescope, sandy_telescope

# NUM_INSTRUMENTS_MIN = 1
# NUM_INSTRUMENTS_MAX = 10

# instruments = []

# for instrument in InstrumentType:
#     Instrument(
#         id=uuid.UUID("a4cf7691-8d3c-4fea-899c-9bcc33d23a5e"),
#         name="SANDY'S_{instrument}",
#         short_name="S_{instrument}",
#         telescope=sandy_telescope,
#         type=instrument,
#         field_of_view=InstrumentFOV.POLYGON.value,
#         is_operational=True,
#     )

sandy_instrument_calorimeter = Instrument(
    id=uuid.UUID("a4cf7691-8d3c-4fea-899c-9bcc33d23a5e"),
    name="SANDY'S X-RAY",
    short_name="SANDY_XRAY",
    telescope=sandy_telescope,
    type=InstrumentType.CALORIMETER.value,
    field_of_view=InstrumentFOV.POLYGON.value,
    is_operational=True,
)

sandy_all_sky_instrument = Instrument(
    id=uuid.UUID("f3a2b0c1-4d5e-4f6a-8b7c-8d9e0f1a2b3c"),
    name="SANDY'S ALL-SKY",
    short_name="SANDALLSKY",
    telescope=sandy_telescope,
    type=InstrumentType.PHOTOMETRIC.value,
    field_of_view=InstrumentFOV.ALL_SKY.value,
    is_operational=True,
)

sandy_optical_instrument = Instrument(
    id=uuid.UUID("c31dc89c-d2f0-4335-9d6f-e42e7a7d86af"),
    name="SANDY'S OPTICAL",
    short_name="SANDOPT",
    telescope=sandy_smaller_telescope,
    type=InstrumentType.PHOTOMETRIC.value,
    field_of_view=InstrumentFOV.POLYGON.value,
    is_operational=True,
)

instruments = [
    sandy_instrument_calorimeter,
    sandy_all_sky_instrument,
    sandy_optical_instrument,
]
