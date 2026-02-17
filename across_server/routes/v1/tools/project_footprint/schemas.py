from ...observation.schemas import Observation


class ProjectedObservation(Observation):
    """
    Represents the projected footprint for a given observation, which includes the footprint
    """

    footprint: list[list[tuple[float, float]]]  # this is easy for aladin to plug into
