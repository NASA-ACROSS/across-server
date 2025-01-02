import uuid

from across_server.db.models import Telescope

from .observatories import sandy_observatory

sandy_telescope = Telescope(
    id=uuid.uuid4(),
    name="SANDY'S EYE IN THE SKY",
    short_name="SANDY_EYE",
    observatory=sandy_observatory,
)

telescopes = [sandy_telescope]
