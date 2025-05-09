import uuid

from across_server.core.enums import InstrumentType
from across_server.db.models import Instrument

from .telescopes import sandy_smaller_telescope, sandy_telescope

sandy_instrument_calorimeter = Instrument(
    id=uuid.UUID("a4cf7691-8d3c-4fea-899c-9bcc33d23a5e"),
    name="SANDY'S X-RAY",
    short_name="SANDY_XRAY",
    telescope=sandy_telescope,
    type=InstrumentType.CALORIMETER.value,
    is_operational=True,
)

sandy_instrument_photometric = Instrument(
    id=uuid.UUID("27493a8d-38e2-45cf-ac1e-1fa3bb0ffca3"),
    name="SANDY'S OPTICAL",
    short_name="SANDOPT",
    telescope=sandy_smaller_telescope,
    type=InstrumentType.PHOTOMETRIC.value,
    is_operational=True,
)

instruments = [sandy_instrument_calorimeter, sandy_instrument_photometric]
