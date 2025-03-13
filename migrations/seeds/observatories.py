import uuid

from across_server.core.enums import ObservatoryType
from across_server.db.models import Observatory

from .groups import treedome_space_group

space_based: str = ObservatoryType.SPACE_BASED.value
ground_based: str = ObservatoryType.GROUND_BASED.value

sandy_observatory = Observatory(
    id=uuid.uuid4(),
    observatory_type=space_based,
    name="SANDY'S SPACE STATION",
    short_name="SANDY",
    group=treedome_space_group,
)

observatories = [sandy_observatory]
