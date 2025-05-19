import uuid

from ...core.exceptions import InvalidEntityException, NotFoundException


class ObservationNotFoundException(NotFoundException):
    def __init__(self, observation_id: uuid.UUID):
        super().__init__(entity_name="Observation", entity_id=observation_id)


class InvalidObservationReadParametersException(InvalidEntityException):
    def __init__(self, message: str):
        super().__init__(entity_name="ObservationRead", message=message)
