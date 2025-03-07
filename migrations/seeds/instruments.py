import uuid

from across_server.db.models import Instrument

from .telescopes import sandy_smaller_telescope, sandy_telescope

sandy_instrument = Instrument(
    id=uuid.UUID("511d9ab3-6d0a-4471-bb41-937dd608c6f4"),
    name="SANDY'S X-RAY",
    short_name="SANDY_XRAY",
    telescope=sandy_telescope,
)

sandy_instrument = Instrument(
    id=uuid.UUID("c31dc89c-d2f0-4335-9d6f-e42e7a7d86af"),
    name="SANDY'S OPTICAL",
    short_name="SANDOPT",
    telescope=sandy_smaller_telescope,
)

instruments = [sandy_instrument]
