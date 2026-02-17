from uuid import UUID

from .....core.schemas.base import BaseSchema
from ...observation.schemas import Observation


class ProjectFootprintRead(BaseSchema):
    """
    Represents the query parameters for reading project footprints.
    """

    observation_id: UUID | None = None
    schedule_id: UUID | None = None


class ProjectedObservation(Observation):
    """
    Represents the projected footprint for a given observation, which includes the footprint
    """

    footprint: list[list[tuple[float, float]]]  # this is easy for aladin to plug into
