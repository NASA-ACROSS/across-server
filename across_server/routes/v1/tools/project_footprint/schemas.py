from uuid import UUID

from across_server.core.schemas.base import BaseSchema


class ProjectFootprintRead(BaseSchema):
    """
    Represents the query parameters for reading project footprints.
    """

    observation_id: UUID | None = None
    schedule_id: UUID | None = None


class ProjectedFootprint(BaseSchema):
    """
    Represents the projected footprint for a given observation, which includes the footprint
    """

    footprint: list[list[tuple[float, float]]]  # this is easy for aladin to plug into
    observation_id: UUID
