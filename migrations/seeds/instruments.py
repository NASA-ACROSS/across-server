import uuid

from across_server.db.models import Instrument

from .telescopes import sandy_telescope

sandy_instrument = Instrument(
    id=uuid.uuid4(),
    name="SANDY'S X-RAY",
    short_name="SANDY_XRAY",
    telescope=sandy_telescope,
)

instruments = [sandy_instrument]
