import uuid

from across_server.db.models import Telescope

from .observatories import sandy_observatory

sandy_telescope = Telescope(
    id=uuid.UUID("760ddaef-a0e2-4110-b402-769376cdb5fb"),
    name="SANDY'S EYE IN THE SKY",
    short_name="SANDY_EYE",
    observatory=sandy_observatory,
)

sandy_smaller_telescope = Telescope(
    id=uuid.UUID("2de2374e-9d4e-4bbc-9b14-fac80068ca55"),
    name="SANDY'S SECOND EYE IN THE SKY",
    short_name="SANDY_2EYE",
    observatory=sandy_observatory,
)

telescopes = [sandy_telescope, sandy_smaller_telescope]
