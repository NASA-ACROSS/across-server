import uuid

from ...core.exceptions import NotFoundException


class ObservationNotFoundException(NotFoundException):
    def __init__(self, observation_id: uuid.UUID):
        super().__init__(entity_name="Observation", entity_id=observation_id)
