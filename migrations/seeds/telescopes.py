import uuid

from across_server.db.models import Telescope

from .observatories import sandy_observatory

sandy_telescope = Telescope(
    id=uuid.UUID("87e15f42-72c0-4973-a1f6-c23807cf90c5"),
    name="SANDY'S EYE IN THE SKY",
    short_name="SANDY_EYE",
    observatory=sandy_observatory,
    is_operational=True,
)

sandy_smaller_telescope = Telescope(
    id=uuid.UUID("ca8d3753-438f-4f5d-a77d-107fb10df228"),
    name="SANDY'S SECOND EYE IN THE SKY",
    short_name="SANDY_2EYE",
    observatory=sandy_observatory,
    is_operational=True,
)

telescopes = [sandy_telescope, sandy_smaller_telescope]
