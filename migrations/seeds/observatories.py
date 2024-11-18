import uuid
from across_server.db.models import Observatory
from across_server.routes.observatory.enums import OBSERVATORY_TYPE
from .groups import treedome_space_group

space_based: OBSERVATORY_TYPE = "SPACE_BASED"
ground_based: OBSERVATORY_TYPE = "GROUND_BASED"

sandy_observatory = Observatory(
    id=uuid.uuid4(),
    observatory_type=space_based,
    name="SANDY'S SPACE STATION",
    short_name="SANDY",
    group=treedome_space_group,
)

observatories = [sandy_observatory]
